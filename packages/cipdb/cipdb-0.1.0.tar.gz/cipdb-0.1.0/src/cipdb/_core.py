#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-29 04:13:14 (ywatanabe)"
# File: /home/ywatanabe/proj/cipdb/src/cipdb/_cipdb.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./cipdb/src/cipdb/_cipdb.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
cipdb - Conditional iPDB

A simple conditional debugging wrapper for iPDB.
Debug specific breakpoints by ID matching.
"""

import sys
from typing import Callable, Optional, Union


class _ConditionChecker:
    """Internal condition evaluation logic."""

    def __init__(self):
        self.enabled = True  # Global enable/disable switch

    def check(
        self,
        condition: Union[bool, str, Callable] = True,
        id: Optional[str] = None,
    ) -> bool:
        """
        Evaluate condition with ID matching support.

        Priority order (ALL must pass to trigger debugging):
        1. Global enable/disable switch (cipdb.enable/disable)
        2. CIPDB environment override (CIPDB=false disables all)  
        3. ID matching (if id provided):
           - Production mode: If CIPDB_ID or CIPDB_IDS is set → must match
           - Development mode: If neither is set → all ID breakpoints work
        4. Condition evaluation (boolean/callable/string must be truthy)

        Logic: Global AND Environment AND ID AND Condition = Debug
        """
        # Global switch
        if not self.enabled:
            return False

        # Check environment override
        cipdb_env = os.environ.get("CIPDB", "").lower()
        if cipdb_env in ("false", "0", "off"):
            return False

        # ID-based matching
        if id:
            cipdb_id = os.environ.get("CIPDB_ID", "")
            cipdb_ids = os.environ.get("CIPDB_IDS", "")
            
            # If ANY ID env var is set, must match (production mode)
            if cipdb_id or cipdb_ids:
                id_matches = False
                
                # Check CIPDB_ID (single ID)
                if cipdb_id and cipdb_id == id:
                    id_matches = True
                
                # Check CIPDB_IDS (comma-separated IDs)
                elif cipdb_ids:
                    ids_list = [i.strip() for i in cipdb_ids.split(",")]
                    if id in ids_list:
                        id_matches = True
                
                if not id_matches:
                    return False
            # If no ID env vars set, all ID breakpoints work (development mode)

        # Evaluate condition
        if isinstance(condition, bool):
            return condition

        elif isinstance(condition, str):
            # String conditions check environment variables
            if "=" in condition:
                var, val = condition.split("=", 1)
                return os.environ.get(var) == val
            else:
                # Check if env var exists and is truthy
                env_val = os.environ.get(condition, "").lower()
                return env_val in ("true", "1", "yes", "on")

        elif callable(condition):
            try:
                return bool(condition())
            except:
                return False

        # Default to True for unknown types
        return True


# Global condition checker instance
_checker = _ConditionChecker()


def set_trace(
    condition: Union[bool, str, Callable] = True,
    id: Optional[str] = None,
) -> None:
    """
    Set conditional breakpoint.

    Args:
        condition: Debugging condition (default: True)
            - bool: Simple on/off (True/False)
            - str: Environment variable check  
            - callable: Function returning bool
        id: Optional ID for ID-based debugging
            - Only triggers if CIPDB_ID matches or id is in CIPDB_IDS
            - AND condition must also be True

    Behavior:
        - If id provided + env vars set: Must match CIPDB_ID/CIPDB_IDS AND condition (production)
        - If id provided + no env vars: All ID breakpoints work + condition (development)  
        - If no id: Only condition is evaluated
        - Global controls (cipdb.disable(), CIPDB=false) override everything

    Examples:
        >>> import cipdb

        >>> # Simple usage
        >>> cipdb.set_trace()        # Always debug (condition=True)
        >>> cipdb.set_trace(False)   # Never debug (condition=False)

        >>> # ID-based debugging (condition defaults to True)
        >>> cipdb.set_trace(id="validate")  # Debug if "validate" in CIPDB_IDS
        
        >>> # Combined ID + condition
        >>> cipdb.set_trace(error_count > 5, id="validate")  # Debug validate breakpoint only when errors > 5

        >>> # Environment-based
        >>> cipdb.set_trace(os.getenv("DEBUG"))  # Debug if DEBUG env var is set

        >>> # Pure conditional
        >>> cipdb.set_trace(user_count > 100)  # Debug when condition is met
    """
    # Check condition with ID matching
    if not _checker.check(condition, id):
        return

    # Import and call debugger
    try:
        import ipdb

        ipdb.set_trace(sys._getframe().f_back)
    except ImportError:
        import pdb

        pdb.set_trace()


def post_mortem(
    tb=None,
    condition: Union[bool, str, Callable] = True,
    id: Optional[str] = None,
) -> None:
    """
    Conditionally enter post-mortem debugging.

    Args:
        tb: Traceback object (defaults to sys.exc_info()[2])
        condition: Same as set_trace condition
        id: Optional ID for ID-based debugging
    """
    if not _checker.check(condition, id):
        return

    if tb is None:
        tb = sys.exc_info()[2]

    if tb:
        try:
            import ipdb

            ipdb.post_mortem(tb)
        except ImportError:
            import pdb

            pdb.post_mortem(tb)


def disable() -> None:
    """Globally disable all cipdb debugging."""
    _checker.enabled = False


def enable() -> None:
    """Globally enable cipdb debugging."""
    _checker.enabled = True

# EOF
