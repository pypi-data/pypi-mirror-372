#!/usr/bin/env python

from collections import OrderedDict

import time
import logging

from igniter import logger as _logger


class Logger(logging.Logger):
    def __init__(self, name: str = None, cache_size: int = 1000):
        super(Logger, self).__init__(name)
    
        self.max_cache_size = cache_size
        self.last_logged_time = OrderedDict()

    def _log_interval(self, func, message, interval, *args, **kwargs):
        current_time = time.time()
        message_key = (self.name, message)

        if len(self.last_logged_time) >= self.max_cache_size:
            self.last_logged_time.popitem(last=False)

        if message_key not in self.last_logged_time or (current_time - self.last_logged_time[message_key]) > interval:
            self.last_logged_time[message_key] = current_time
            func(message, *args, **kwargs)

    def warn_throttle(self, message, interval, *args, **kwargs):
        self._log_interval(self.warning, message, interval, *args, **kwargs)

    def info_throttle(self, message, interval, *args, **kwargs):
        self._log_interval(self.info, message, interval, *args, **kwargs)


logger = Logger()
logger.addHandler(_logger.console_handler)
logger.setLevel(_logger.level)
