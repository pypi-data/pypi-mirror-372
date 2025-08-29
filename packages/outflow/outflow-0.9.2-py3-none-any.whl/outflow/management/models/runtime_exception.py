# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from outflow.core.db import Model

# from outflow.management.models.task import Task
from outflow.management.models.block import Block


class RuntimeException(Model):
    """
    This table provides the history of the runtime exceptions that
    occurred in the pipeline.
    """

    __tablename__ = "outflow_runtime_exception"

    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey(Block.id))
    exception_type = Column(String(64), nullable=False)
    exception_msg = Column(Text, nullable=False)
    traceback = Column(Text, nullable=False)
    block = relationship("Block")
    time = Column(DateTime, nullable=False)
