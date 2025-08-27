#!/usr/bin/env python

import os
import click

import time
import numpy as np
from tqdm import tqdm
import torch
import cv2 as cv
import matplotlib.pyplot as plt

from vision_engine.models.build_tracker import build_tracker


def get_track_region(frame: np.ndarray) -> np.ndarray:
    from vision_engine.utils.bbox_draw import RectangleDrawer

    rect = RectangleDrawer().run(frame)
    return rect


def show_mask(mask, ax, random_color=False, borders = True):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask = mask.astype(np.uint8)
    mask_image =  mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    if borders:
        contours, _ = cv.findContours(mask,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE) 
        contours = [cv.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
        mask_image = cv.drawContours(mask_image, contours, -1, (1, 1, 1, 0.5), thickness=2) 
    ax.imshow(mask_image)

def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(
        pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25
    )
    ax.scatter(
        neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25
    )


def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))    


def show_masks(image, masks, scores, point_coords=None, box_coords=None, input_labels=None, borders=True):
    for i, (mask, score) in enumerate(zip(masks, scores)):
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        show_mask(mask, plt.gca(), borders=borders)
        if point_coords is not None:
            assert input_labels is not None
            show_points(point_coords, input_labels, plt.gca())
        if box_coords is not None:
            show_box(box_coords, plt.gca())
        if len(scores) > 1:
            plt.title(f"Mask {i+1}, Score: {score:.3f}", fontsize=18)
        plt.axis('off')
        plt.show()


def run_image(predictor, im_path, **kwargs):
    assert os.path.isfile(im_path), f'Invalid filename {im_path}'

    image = cv.imread(im_path)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    bbox = get_track_region(image)
    
    with torch.inference_mode(), torch.autocast('cuda', dtype=torch.bfloat16):
        predictor.set_image(image)

        center = bbox[:2] + (np.diff(bbox.reshape(2, -1), axis=0) / 2)
        masks, scores, _ = predictor.predict(point_coords=center, point_labels=[1], box=bbox)

    show_masks(image, masks, scores, box_coords=bbox)


def overlay_results(image, result, show_mask: bool = True):
    assert isinstance(result, dict), f'Expects dict but got {type(result)}'
    if 'bboxes' in result:
        for i, bbox in enumerate(result['bboxes']):
            x1, y1, x2, y2 = bbox.cpu().int().numpy() if isinstance(bbox, torch.Tensor) else bbox
            cv.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)

    if show_mask and 'masks' in result:
        masks = result['masks'][0].cpu().numpy().astype(np.uint8)  # currently only one image
        masks *= 255 if masks.max() != 255 else 1
        all_mask = cv.cvtColor(masks, cv.COLOR_GRAY2RGB)
        image = cv.addWeighted(image, 1, all_mask, 0.5, 0)
    return image


def run_video(predictor, media, scale: float = 1.0, start_frame: int = 0) -> None:
    video_cap = cv.VideoCapture(media)
    wname = 'video'
    cv.namedWindow(wname)

    ic = 0
    while video_cap.isOpened():
        ret, frame = video_cap.read()

        if scale < 1.0:
            frame = cv.resize(frame, dsize=None, fx=scale, fy=scale)

        im_hw = frame.shape[:2]
        ic = ic + 1

        if ic < start_frame:
            print(f"skip: {ic} {start_frame}")
            continue

        annotation = None
        if not predictor.has_initialized:
            all_mask = np.zeros((*im_hw, 1), dtype=np.uint8)
            bbox = get_track_region(frame.copy())

            annotation = {'bbox': bbox}
        
        start = time.perf_counter()
        results = predictor(frame, annotation)
        print(">>> Perf Count", time.perf_counter() - start)

        results = predictor.bboxes_from_masks(results)
        im_viz = overlay_results(frame, results)
        
        cv.imshow(wname, im_viz)

        os.makedirs('./results', exist_ok=True)
        cv.imwrite(f'./results/img_{str(ic).zfill(4)}.jpg', im_viz)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break


@click.command()
@click.argument('media', type=str)
@click.option('--model', type=str, default='tiny')
@click.option('--predictor', type=str, default='camera')
@click.option('--scale', type=float, default=1.0)
@click.option('--start_frame', type=int, default=0)
def main(media, model: str, predictor: str, scale: float, start_frame: int) -> None:
    if not (media.isdigit() or os.path.isfile(media)):
        raise TypeError(f'{media}')

    proc_func = run_video
    if media.lower().endswith(('jpg', 'png')):
        predictor = 'image' if predictor == 'auto' else predictor
        proc_func = run_image

    predictor = build_tracker(model, predictor, image_size=512)
    proc_func(predictor, media, scale=scale, start_frame=start_frame)


if __name__ == '__main__':
    main()
