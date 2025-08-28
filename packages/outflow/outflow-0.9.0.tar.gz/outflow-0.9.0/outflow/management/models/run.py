# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from outflow.core.db import Model
from outflow.management.models.configuration import Configuration
from outflow.management.models.mixins import Executable


class Run(Model, Executable):
    """
    Stores a run
    """

    __tablename__ = "outflow_run"
    id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, ForeignKey(Configuration.id), nullable=False)
    configuration = relationship("Configuration", back_populates="runs")
    command_name = Column(String, nullable=True)
