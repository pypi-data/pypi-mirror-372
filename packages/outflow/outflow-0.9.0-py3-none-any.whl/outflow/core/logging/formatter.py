# -*- coding: utf-8 -*-
import logging


class OutflowFormatter(logging.Formatter):
    base_format = "[%(name)s] %(message)s"
    remote_format = "(%(ip)s) [%(name)s]  %(message)s"

    def __init__(self):
        super().__init__(fmt=self.base_format)

    def format(self, record):
        ip = getattr(record, "ip", None)
        pid = getattr(record, "pid", None)

        if ip and pid:
            self._style._fmt = self.remote_format
        else:
            self._style._fmt = self.base_format

        text = super().format(record)

        return text


class OutflowFileFormatter(OutflowFormatter):
    base_format = "%(asctime)s - %(levelname)s - [%(name)s] %(message)s"
    remote_format = "%(asctime)s - %(levelname)s - (%(ip)s) [%(name)s]  %(message)s"
