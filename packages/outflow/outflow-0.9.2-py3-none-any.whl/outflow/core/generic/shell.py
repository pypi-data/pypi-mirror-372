# -*- coding: utf-8 -*-
import pathlib
import sys


def source(script: pathlib.Path, encoding=sys.getdefaultencoding()):
    """
    Generate env vars from a sourced script

    http://pythonwise.blogspot.fr/2010/04/sourcing-shell-script.html (Miki Tebeka)
    http://stackoverflow.com/questions/3503719/#comment28061110_3505826 (ahal)
    https://stackoverflow.com/questions/20669558/how-to-make-subprocess-called-with-call-popen-inherit-environment-variables
    """
    import subprocess

    proc = subprocess.Popen(
        ["bash", "-c", f"set -a && source {script.resolve().as_posix()} && env -0"],
        stdout=subprocess.PIPE,
        shell=False,
    )
    output, err = proc.communicate()
    output = output.decode(encoding)
    env = dict((line.split("=", 1) for line in output.split("\x00") if line))
    return env
