#!/usr/bin/env python

from typing import Dict, Any
import os
import os.path as osp

from dataclasses import dataclass

import numpy as np
import cv2 as cv
import torch

from igniter.registry import model_registry
from igniter.logger import logger
from vision_engine.engine import TrackerABC


CONFIG_DIR = osp.join(osp.dirname(osp.abspath(__file__)), 'configs/sam2.1/sam2.1_hiera_%s.yaml')

_BASE_URL = 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_%s.pt'
SAM2_MODELS = {
    'tiny': {'config': CONFIG_DIR % 't', 'url': _BASE_URL % 'tiny'},
    'small': {'config': CONFIG_DIR % 's', 'url': _BASE_URL % 'small'},
    'large': {'config': CONFIG_DIR % 'l', 'url': _BASE_URL % 'large'},
    'base': {'config': CONFIG_DIR % 'b+', 'url': _BASE_URL % 'base_plus'},
}


class SamTracker(TrackerABC):
    def __call__(self, image: np.ndarray, annotation: Dict[str, Any] = None) -> Dict[str, torch.Tensor]:
        if not self.has_initialized:
            self.initialize(image, annotation)
            
        with torch.inference_mode(), torch.autocast(self.device.type, dtype=torch.bfloat16):
            out_obj_ids, out_mask_logits = self.model.track(image)

        out_mask_logits = out_mask_logits.sigmoid()
        self.is_tracking = True
        return {'mask_logits': out_mask_logits}

    def update(self, image: np.ndarray, annotation: Dict[str, Any]):
        logger.warning('Tracker update is not yet implemented!')

    def initialize(self, image, annotation: Dict[str, Any]):
        assert 'bbox' in annotation, 'bbox is required'
        self.model.load_first_frame(image)
        self.add_prompt(**annotation)
        super(SamTracker, self).initialize()

    def add_prompt(self, bbox: np.ndarray, mask: np.ndarray = None):
        ann_frame_idx = 0
        ann_obj_id = 1
        _, out_obj_ids, out_mask_logits = self.model.add_new_prompt(
            frame_idx=ann_frame_idx, obj_id=ann_obj_id, bbox=bbox
        )

    def bboxes_from_masks(self, results: Dict[str, torch.Tensor], thresh: float = 0.5) -> Dict[str, torch.Tensor]:
        out_mask_logits = results['mask_logits']

        # curently only one bbox
        _, _, ys, xs = torch.where(out_mask_logits > thresh)

        if len(ys) < 2 or len(xs) <  2:
            self.is_tracking = False            
            logger.warning('Tracking target is lost')
            return results

        xmin, ymin = xs.min(), ys.min()
        xmax, ymax = xs.max(), ys.max()

        all_masks = out_mask_logits > thresh
        all_masks = all_masks.any(dim=1)

        results['bboxes'] = [torch.Tensor([xmin, ymin, xmax, ymax])]
        results['masks'] = all_masks
        return results

    def reset(self) -> None:
        self.model.reset_state()
        self.has_initialized = False
        self.is_tracking = False

    @property
    def device(self) -> torch.device:
        return self.model.device


@model_registry('sam_tracker')
def build_tracker(model: str, predictor: str = 'camera', checkpoint: str = None, **kwargs):
    torch.autocast(device_type='cuda', dtype=torch.bfloat16).__enter__()

    assert model in SAM2_MODELS, f'{model} unknown, available: {SAM2_MODELS.keys()}'
    checkpoint = checkpoint or get_checkpoint(SAM2_MODELS[model]['url'])
    predictor = load_predictor(SAM2_MODELS[model]['config'], checkpoint, predictor.lower(), **kwargs)

    return SamTracker(predictor)


def load_predictor(config: str, checkpoint: str, predictor: str, **kwargs):
    if torch.cuda.get_device_properties(0).major >= 8:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    config = osp.relpath(config, osp.dirname(osp.abspath(__file__)))
    if predictor in ['camera', 'cam', 'rt']:
        from vision_engine.models.build_sam2 import build_sam2_camera_predictor
    
        predictor = build_sam2_camera_predictor(config, checkpoint, **kwargs)
    elif predictor == 'image':
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        predictor = SAM2ImagePredictor(build_sam2(config, checkpoint), **kwargs)
    else:
        raise TypeError(f'Unknown predictor {predictor}')
    return predictor


def get_checkpoint(url: str) -> str:
    import requests
    from tqdm import tqdm

    filename = osp.join(os.environ['HOME'], '.cache/torch/hub/checkpoints/', osp.basename(url))
    os.makedirs(osp.dirname(filename), exist_ok=True)
    if not osp.isfile(filename):
        logger.info(f'Downloading SAM2 weights from {url}')    
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        with open(filename, 'wb') as file:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar.update(len(chunk))
    logger.info(f'SAM2 Checkpoint: {filename}')
    return filename
