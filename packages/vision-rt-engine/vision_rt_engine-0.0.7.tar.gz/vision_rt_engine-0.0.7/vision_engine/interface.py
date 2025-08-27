#!/usr/bin/env python

from typing import Callable
# from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, InitVar, field

from functools import partial
import requests

import io
import base64
import numpy as np
from PIL import Image


def pil_img_to_byte(image: Image.Image, format: str = 'JPEG') -> str:
    ibuffer = io.BytesIO()
    image.save(ibuffer, format=format)
    ibuffer.seek(0)
    return ibuffer


def img_to_byte(image: np.ndarray) -> str:
    return image.tobytes()


@dataclass(slots=True)
class Interface(object):
    endpoint: InitVar[str]
    _post: Callable = field(init=False, repr=False)

    def __post_init__(self, endpoint):
        self._post = partial(requests.post, endpoint)

    def __call__(self, image, prompts: str, temperature: float = None):
        files = {'image': ('image.jpg', image, 'image/jpeg')}
        data = {'text': prompts}

        if temperature is not None and 0 <= temperature <= 1:
            assert isinstance(temperature, float)
            data['temperature'] = temperature

        return self._post(files=files, data=data)

    @property
    def addr(self) -> str:
        return self._post.args[0]


inf = Interface('http://127.0.0.1:8080/chat', )
import IPython; IPython.embed()
