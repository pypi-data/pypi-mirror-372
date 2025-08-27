# -*- coding: utf-8 -*-
import os
import subprocess
import sys


ROOT_DIR = os.path.join(os.path.dirname(__file__), "bin")

def _program(name, args):
    return subprocess.call([os.path.join(ROOT_DIR, name)] + args, close_fds=False)


def edgembar():
    suffix = '.exe' if os.name == 'nt' else ''
    raise SystemExit(_program('edgembar' + suffix, sys.argv[1:]))


def edgembar_omp():
    suffix = '.exe' if os.name == 'nt' else ''
    raise SystemExit(_program('edgembar_omp' + suffix, sys.argv[1:]))


def edgembar_WriteGraphHtml():
    raise SystemExit(_program('edgembar-WriteGraphHtml.py', sys.argv[1:]))


def edgembar_amber2dats():
    raise SystemExit(_program('edgembar-amber2dats.py', sys.argv[1:]))

def edgembar_bookend2dats():
    raise SystemExit(_program('edgembar-bookend2dats.py', sys.argv[1:]))

def edgembar_calcamberboresch():
    raise SystemExit(_program('edgembar-calcamberboresch.py', sys.argv[1:]))
