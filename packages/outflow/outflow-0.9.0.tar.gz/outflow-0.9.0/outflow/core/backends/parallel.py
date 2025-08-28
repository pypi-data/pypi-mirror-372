# -*- coding: utf-8 -*-
from outflow.core.backends.default import Backend as DefaultBackend


class Backend(DefaultBackend):
    def __init__(self):
        super().__init__()

        self.name = "parallel"
