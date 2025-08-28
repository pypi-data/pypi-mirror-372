# -*- coding: utf-8 -*-
from outflow.core.db.skip_if_untracked import skip_if_untracked
import datetime
from enum import Enum as py_Enum

from outflow.core.pipeline import context
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as sa_Enum
from sqlalchemy import String


class StateEnum(py_Enum):
    pending = 1
    running = 2
    failed = 3
    success = 4
    skipped = 5


class Executable:
    """
    Executable mixin

    Has all the columns needed to record something executable (run and task for now)
    """

    uuid = Column(String(36), nullable=False, unique=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    state = Column(sa_Enum(StateEnum), nullable=False, default="pending")
    hostname = Column(String(256), nullable=True)

    @skip_if_untracked
    def start(self):
        session = context.session
        self.state = "running"
        self.start_time = datetime.datetime.now()
        session.commit()

    @skip_if_untracked
    def fail(self):
        session = context.session
        self.state = "failed"
        self.end_time = datetime.datetime.now()
        session.commit()

    @skip_if_untracked
    def skip(self):
        session = context.session
        self.state = "skipped"
        self.end_time = datetime.datetime.now()
        session.commit()

    @skip_if_untracked
    def success(self):
        session = context.session
        self.state = "success"
        self.end_time = datetime.datetime.now()
        session.commit()
