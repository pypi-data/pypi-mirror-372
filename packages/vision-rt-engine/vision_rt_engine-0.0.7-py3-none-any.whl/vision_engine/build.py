#!/usr/bin/env python

from typing import Any, Dict, Callable
from omegaconf import DictConfig
from igniter.registry import model_registry, engine_registry
from igniter.logger import logger

import torch.nn as nn
from vision_engine.engine import RTBaseEngine


def get_key(dt: Dict[str, Any]) -> str:
    return next(iter(dt.keys()))


def make_it(dt: Dict[str, Any], registry: Dict[str, Callable] = model_registry) -> Callable:
    name = get_key(dt)
    logger.info(f'>>> Building model {name}')    
    kwargs = dt[name] or {}
    return registry[name](**kwargs)


class WrappedModel(nn.Module):
    def __init__(self, tracker, detector: Any = None):
        super(WrappedModel, self).__init__()
        self.tracker = tracker
        if detector is not None:
            self.detector = detector

    def forward(self, image):
        raise NotImplementedError()


class VisionEngine(RTBaseEngine):
    def post_detection(self, inputs: Dict[str, Any], results: Any):
        results.filter('__background__')
        target_name = inputs.get('target_name', None)

        if target_name:
            indices = [i for i, name in enumerate(results.labels) if name == target_name]
            results._filter_by_indices(results, indices)

            if len(results.scores) > 0:
                index = results.scores.argmax()
                results._filter_by_indices(results, [index])

        return results
        
    
@model_registry('rt_tracking')
def build(tracker: DictConfig, detector: DictConfig = None, rpn: DictConfig = None) -> WrappedModel:
    from hydra.core.global_hydra import GlobalHydra

    rpn = make_it(rpn) if rpn is not None else None
    tracker = make_it(tracker)

    if GlobalHydra().is_initialized():
        GlobalHydra().clear()

    detector = make_it(detector) if detector is not None else None
    model = WrappedModel(detector=detector, tracker=tracker)

    logger.info('>>> Tracking model is ready')
    return model


@engine_registry
def rt_vision_engine(cfg: DictConfig, model: nn.Module, transforms: DictConfig=None) -> RTBaseEngine:
    engine = VisionEngine(model.detector, model.tracker)
    return engine


class VisionEngine2(VisionEngine):
    def _detect(self):
        # from hydra.core.global_hydra import GlobalHydra

        # if GlobalHydra().is_initialized():
        #     GlobalHydra().clear()

        self._detector = make_it(self.offline_detector)
        super(VisionEngine2, self)._detect()
        logger.info('Offline Detector is ready!')

    def _track(self):
        self._tracker = make_it(self.online_tracker)
        # self._tracker.cuda()
        # self._online_cache = {'bboxes': [[500, 200, 700, 300]]}
        super(VisionEngine2, self)._track()
        logger.info('Online Tracker is ready')


@model_registry('rt_tracking2')
def build(detector: DictConfig, tracker: DictConfig, rpn: DictConfig = None) -> WrappedModel:
    # tracker = make_it(tracker)
    model = WrappedModel(detector=detector, tracker=tracker)
    return model


@engine_registry
def rt_vision_engine2(cfg, model, transforms=None) -> RTBaseEngine:
    engine = VisionEngine2(model.detector, model.tracker)
    return engine
