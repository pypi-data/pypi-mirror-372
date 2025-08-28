# -*- coding: utf-8 -*-
from .database import Databases  # noqa: F401 E402
from .declarative_base_model import BaseModel, make_declarative_base  # noqa: E402

Model = make_declarative_base(BaseModel)
