#!/usr/bin/env python

from igniter.builder import build_engine
from igniter.main import get_full_config
from vision_engine import main

import torch.multiprocessing as mp

import time
import cv2 as cv

import click

from vision_engine.tracking import overlay_results


@click.command()
@click.argument('media')
@click.option('--target', default='leaf_petiteoseille')
@click.option('--cfg', default='./configs/tracking.yaml')
def main(media, target, cfg):
    # if mp.get_start_method(allow_none=True) != 'spawn':
    #     mp.set_start_method('spawn', force=True)

    cfg = get_full_config(cfg)
    engine = build_engine(cfg)
    # engine = VisionEngine2(cfg.models.rt_tracking2.detector, cfg.models.rt_tracking2.tracker)

    cv.namedWindow('viz', cv.WINDOW_NORMAL)

    video_cap = cv.VideoCapture(media)
    while video_cap.isOpened():
        # image = cv.imread('/root/krishneel/Pictures/Screenshots/boston.png')
        _, image = video_cap.read()
        engine(image, target_name=target)
        results = engine._results_queue.get()
    
        if results is None:
            print('>>>> Empty')
            continue

        im_viz = overlay_results(image, results)
        cv.imshow('viz', im_viz)
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break


if __name__ == '__main__':
    main()
