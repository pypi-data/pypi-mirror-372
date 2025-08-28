# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from outflow.core.db import Model


class Configuration(Model):
    """
    Stores a run configuration
    """

    __tablename__ = "outflow_configuration"

    id = Column(Integer, primary_key=True)
    config = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=False)
    # TODO add cli args
    hash = Column(String(64), nullable=False, unique=True)
    runs = relationship("Run", back_populates="configuration")
