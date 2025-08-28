# -*- coding: utf-8 -*-
import sys

from .logger import OutflowLogger
from .rotating_file_handler import RotatingFileHandlerPerUser
from .formatter import OutflowFormatter, OutflowFileFormatter
from .socket_receiver import SocketReceiver
from .stream_handler import StreamHandler

set_plugins_loggers_config = None

# removes import warning
LogRecordSocketReceiver = None

# create a outflowLogger
outflow_logger = OutflowLogger()

# store the path of the __init__.py file in the OutflowLogger instance
outflow_logger.__file__ = __file__

# Map the submodules to the OutflowLogger instance properties to allow imports
outflow_logger.RotatingFileHandlerPerUser = RotatingFileHandlerPerUser
outflow_logger.OutflowFormatter = OutflowFormatter
outflow_logger.OutflowFileFormatter = OutflowFileFormatter
outflow_logger.LogRecordSocketReceiver = SocketReceiver
outflow_logger.LogRecordStreamHandler = StreamHandler

# replace the outflow.core.logging module by outflow logger instance
# this allows to import the 'logger' property of 'OutflowLogger' as a module
sys.modules[__name__] = outflow_logger
