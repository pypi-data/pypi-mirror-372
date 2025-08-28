# -*- coding: utf-8 -*-
from .command import Command


class RootCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, invokable=False, **kwargs)
