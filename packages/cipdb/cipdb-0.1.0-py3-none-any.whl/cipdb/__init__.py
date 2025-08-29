#!/usr/bin/env python3
"""
cipdb - Conditional iPDB

A simple conditional debugging wrapper for iPDB.
Debug specific breakpoints by ID matching.
"""

import os
import sys
from typing import Union, Optional, Callable

from ._core import set_trace, post_mortem, disable, enable

__all__ = ["set_trace", "post_mortem", "disable", "enable"]
