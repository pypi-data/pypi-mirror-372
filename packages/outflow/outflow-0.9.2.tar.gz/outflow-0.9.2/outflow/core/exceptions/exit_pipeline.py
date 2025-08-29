# -*- coding: utf-8 -*-
from outflow.core.logging import logger


class ExitPipeline(Exception):
    pass


def exit_pipeline():
    logger.debug("Manually exiting pipeline")
    raise ExitPipeline()
