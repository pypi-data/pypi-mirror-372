#!/usr/bin/env python

from igniter.main import get_full_config
from igniter.builder import build_engine
from igniter.registry import model_registry
from igniter.logger import logger


@model_registry('svc_detector')
def build_detector(config: str):
    try:
        from detection.few_shot import main
        import sys
    except ImportError:
        logger.error('Install detection library\npip install -e detection[fsl]')
        sys.exit(1)

    cfg = get_full_config(config)
    return build_engine(cfg)


@model_registry('fast_sam')
def build_rpn():
    from fsl.models.fast_sam_utils import build_fast_sam_mask_generator

    return build_fast_sam_mask_generator()
