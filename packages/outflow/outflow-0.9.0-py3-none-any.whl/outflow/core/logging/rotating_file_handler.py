#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.handlers
import os
import os.path as osp

try:
    import pwd
except ImportError:
    import getpass

    pwd = None

__all__ = ["RotatingFileHandlerPerUser"]


def current_user():
    if pwd:
        return pwd.getpwuid(os.getuid()).pw_name
    else:
        return getpass.getuser()


class RotatingFileHandlerPerUser(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, *args, **kwargs):
        # modify the name of the file by adding the user name in prefix
        # first get the dirname and the basename
        dirname, basename = osp.dirname(filename), osp.basename(filename)

        # add the user name to the filename, the name of the user is retrieved
        # for various environment variables in all OS, so it is easy to change
        # the user running based on this. This is not a secure way of doing
        # this but in this case it is not critical,
        new_filename = osp.join(dirname, "_".join([current_user(), basename]))

        # init as usual but with new name
        super(RotatingFileHandlerPerUser, self).__init__(new_filename, *args, **kwargs)
