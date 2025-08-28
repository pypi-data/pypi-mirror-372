# -*- coding: utf-8 -*-
from outflow.core.db import Model
from outflow.management.models.mixins import Executable
from outflow.management.models.run import Run
from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from enum import Enum as py_Enum
from sqlalchemy import Enum as sa_Enum


class BlockTypeEnum(py_Enum):
    task = 1
    workflow = 2


class Block(Model, Executable):
    """
    Table for runnable block
    """

    __tablename__ = "outflow_block"

    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(sa_Enum(BlockTypeEnum), nullable=False, default="pending")
    plugin = Column(String(256))
    name = Column(String(256), nullable=False)

    run_id = Column(Integer, ForeignKey(Run.id), nullable=False)
    run = relationship("Run")

    input_targets = Column(JSON, nullable=False, server_default="{}")
    output_targets = Column(JSON, nullable=False, server_default="{}")
    input_values = Column(JSON, nullable=True, server_default="{}")

    upstream_blocks = relationship(
        "Block",
        secondary="outflow_edge",
        primaryjoin="Block.id == Edge.downstream_block_id",
        secondaryjoin="Block.id == Edge.upstream_block_id",
        backref="downstream_blocks",
    )

    parent_id = Column(Integer, ForeignKey("outflow_block.id"))
    parent = relationship("Block", backref="children", remote_side=[id])


class Edge(Model):
    """
    Stores relations between Blocks
    """

    __tablename__ = "outflow_edge"

    upstream_block_id = Column(Integer, ForeignKey(Block.id), primary_key=True)
    downstream_block_id = Column(Integer, ForeignKey(Block.id), primary_key=True)
