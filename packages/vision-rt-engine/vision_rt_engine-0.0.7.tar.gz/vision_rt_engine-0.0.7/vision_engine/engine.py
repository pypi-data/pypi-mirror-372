#!/usr/bin/env python

import sys
from typing import Any, Callable, Type, Union, Optional, Dict
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field, InitVar

from collections import deque
# from threading import Event
import torch.multiprocessing as mp # import Process, Queue

import numpy as np
import torch
import torch.nn as nn

# from igniter.logger import logger
from vision_engine.utils.logger import logger

Module = Type[nn.Module]
Tensor = Type[torch.Tensor]


# @dataclass(slots=True)
class TrackerABC(metaclass=ABCMeta):
    model: Module
    has_initialized: Optional[bool] = field(default=False, init=False)
    is_tracking: bool = field(default=False, init=False)

    @abstractmethod
    def __call__(self, image: Tensor):
        if not self.has_initialized:
            self.initialize(image)

    def initialize(self, *args, **kwargs):
        self.has_initialized = True
        self.is_tracking = True

    def reset(self) -> None:
        raise NotImplementedError('Not implemented')

    def update(self, image: Tensor) -> None:
        raise NotImplementedError('Not implemented')


# @dataclass(slots=True)
class BaseEngine(metaclass=ABCMeta):
    offline_detector: InitVar[Union[Module, Callable]]
    online_tracker: InitVar[TrackerABC]
    region_proposal_net: InitVar[Module] = None

    _detector: Union[Module, Callable] = field(init=False, repr=False)
    _tracker: TrackerABC = field(init=False, repr=False)
    _rpn: Module = field(default=None, init=False, repr=False)

    def __post_init__(self, *args):
        for arg, name in zip(args, ['_detector', '_tracker']):
            # assert callable(arg), f'{name[1:]} must be callable'
            setattr(self, name, arg)

        self.instantiate()

    def instantiate(self):
        pass

    @abstractmethod
    def __call__(self, image: Tensor):
        raise NotImplementedError('Not Implemented')

    @property
    def region_proposal_net(self) -> Module:
        return self._rpn

    @property
    def offline_detector(self) -> Union[Module, Callable]:
        return self._detector

    @property
    def online_tracker(self) -> TrackerABC:
        return self._tracker


Queue = mp.Queue


# @dataclass(slots=True)
class RTBaseEngine(BaseEngine):
    _detect_input_queue: Queue = field(default_factory=Queue, init=False, repr=False)
    _track_input_queue: Queue = field(default_factory=Queue, init=False, repr=False)    
    
    _results_queue: Queue = field(default_factory=Queue, init=False, repr=False)
    # _stop_event: Event = field(default_factory=Event, init=False, repr=False)
    # _online_cache: Queue = field(default_factory=Queue, init=False, repr=False)
    _online_cache: Queue = field(init=False, repr=False)    
    _tracker_thread: mp.Process = field(init=False, repr=False)
    _detector_thread: mp.Process = field(init=False, repr=False)

    def instantiate(self):
        self._online_cache = Queue(maxsize=2)
        self.start()

    def start(self) -> None:
        self._detector_thread = mp.Process(target=self._detect)
        self._tracker_thread = mp.Process(target=self._track)
        self._detector_thread.start()        
        self._tracker_thread.start()

    def stop(self) -> None:
        # self._stop_event.set()
        self._online_cache.put(None)
        self._detect_input_queue.put(None)
        self._track_input_queue.put(None)
        for name in ['_tracker_thread', '_detector_thread']:
            thread = getattr(self, name, None)
            if thread is not None:
                thread.join()

    def __call__(self, image: Tensor, target_name: str = None) -> None:
        # self._track_input_queue.put(image)
        # self._detect_input_queue.put({'image': image, 'target_name': target_name})
        self.clear_and_put(self._track_input_queue, image)
        self.clear_and_put(self._detect_input_queue, {'image': image, 'target_name': target_name})

        logger.info(f">>> __call__ {[image.shape, self._detect_input_queue.qsize(), self._track_input_queue.qsize()]}")

        # self._track(image)

    def update(self, image, results) -> None:
        # logger.info(f"Updating cache: {image.shape}, {results}")        

        # self.online_tracker.update(image, results)
        self._online_cache.put(results)

    def _detect(self) -> None:
        while True:  # not self.stop_event.is_set():
            # logger.error(f"[DETECT] Queue {self._detect_input_queue.qsize()}")

            if self._detect_input_queue.empty():
                logger.info_throttle(f"[DETECT] Queue is empty ... {self._detect_input_queue.qsize()}", 5)
                continue

            in_dict = self._detect_input_queue.get()
            image = in_dict['image']

            logger.info(f">>> _detect  {image.shape}, {self._detect_input_queue.qsize()}")
  
            results = self.detect(image)
            results = self.post_detection(in_dict, results)

            logger.warning(f'>>> {results.labels}')
            # import cv2 as cv
            # x1, y1, x2, y2 = results.bboxes.int().numpy()
            # cv.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            # cv.imwrite('/root/krishneel/Desktop/detect.jpg', image)

            if len(results.labels) > 0:
                self.update(image, results)

            logger.info('-' * 40)
            # import time; time.sleep(2)

    def _track(self, image = None) -> None:
        while True:
            if self._track_input_queue.empty():
                logger.info_throttle(f"[TRACK] Queue is empty {self._track_input_queue.qsize()}", 5)
                continue

            if self.cache.empty() and not self.online_tracker.has_initialized:
                logger.warn_throttle(f"[TRACK] No Init {self._track_input_queue.qsize()} {self.cache.qsize()}", 2)
                continue

            annotation = None
            if not self.online_tracker.has_initialized:
                cache = self.cache.get(block=False)
                annotation = {'bbox': getattr(cache,'bboxes').int().numpy()}

            image = self._track_input_queue.get()

            # logger.info(f'Has init {self.online_tracker.has_initialized}')
            logger.info(f">>> _track {[image.shape, self._track_input_queue.qsize()]}")

            import time
            st = time.perf_counter()
            results = self.track(image, annotation)
            self._results_queue.put(results)

            logger.info(f'# time {time.perf_counter() - st}')
            # logger.info(f'Tracking result {results}')

    @torch.inference_mode()
    def detect(self, image: Tensor) -> Any:
        proposals = self.proposals(image)
        results = self.offline_detector(image, proposals)
        return results

    @torch.inference_mode()    
    def track(self, image: Tensor, annotation: Dict[str, Any] = None) -> Any:
        results = self.online_tracker(image, annotation)
        return self.online_tracker.bboxes_from_masks(results)

    @torch.inference_mode()    
    def proposals(self, image: Tensor) -> Any:
        return self.region_proposal_net(image) if self.region_proposal_net is not None else None

    def post_detection(self, inputs: Dict[str, Any], results: Any):
        return results

    @property
    def cache(self):
        return self._online_cache

    @staticmethod
    def clear_and_put(queue: Queue, item: Any) -> None:
        while not queue.empty():
            try:
                queue.get_nowait()
            except Exception as e:
                logger.error(f'Error while clearing queue: {e}')
                break
        queue.put(item)


# @dataclass(slots=True)
class VisionEngine(RTBaseEngine):
    def to(self, *args, **kwargs):
        pass


if sys.version_info >= (3, 10):
    TrackerABC = dataclass(slots=True)(TrackerABC)
    BaseEngine = dataclass(slots=True)(BaseEngine)
    RTBaseEngine = dataclass(slots=True)(RTBaseEngine)
    VisionEngine = dataclass(slots=True)(VisionEngine)
else:
    TrackerABC = dataclass(TrackerABC)
    BaseEngine = dataclass(BaseEngine)
    RTBaseEngine = dataclass(RTBaseEngine)
    VisionEngine = dataclass(VisionEngine)


### CALLBACKS

class SamTracker(TrackerABC):
    def __call__(self, x):
        logger.info(f'[Track] {x}')
        time.sleep(0.1)
        return x

    def update(self, image, result):
        logger.warning('Tracker Updated')

def detect(x, y):
    logger.info(f'[Detect] {[x.shape, y]}')
    # time.sleep(2)    
    return y

def rpn(x):
    from datetime import datetime
    x = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logger.info(f'[RPN] {x}')
    return x


if __name__ == '__main__':
    import time

    track = SamTracker(1)
    try:
        b = VisionEngine(detect, track, None)
        i = 0
        while i < 50:
            inp = torch.randn((3, 224, 224))
            b(inp)
            i += 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    b.stop()
