#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An equivalent of `sphinx-build -b html . build`
Used for simple debugger execution for doc build.
"""

from sphinx.cmd.build import build_main
build_main(["-b", "html", ".", "_build"])
