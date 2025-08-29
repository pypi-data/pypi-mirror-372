#!/usr/bin/env python3
"""
Command-line interface for cipdb.

Usage:
    python -m cipdb [options] <script.py> [args...]
    
Examples:
    # Run script with all breakpoints enabled
    python -m cipdb script.py
    
    # Run script with specific breakpoint ID
    python -m cipdb --id validate script.py
    
    # Run script with environment variable
    python -m cipdb --env DEBUG=true script.py
    
    # Show available environment variables and status
    python -m cipdb --status
"""

import argparse
import os
import sys
from typing import List, Optional

from ._core import enable, disable


def setup_environment(env_vars: Optional[List[str]] = None, cipdb_id: Optional[str] = None, cipdb_ids: Optional[str] = None) -> None:
    """Set up environment variables for cipdb."""
    if env_vars:
        for env_var in env_vars:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                os.environ[key] = value
            else:
                os.environ[env_var] = 'true'
    
    if cipdb_id:
        os.environ['CIPDB_ID'] = cipdb_id
    
    if cipdb_ids:
        os.environ['CIPDB_IDS'] = cipdb_ids


def show_status() -> None:
    """Show current cipdb configuration and environment."""
    print("cipdb Status")
    print("=" * 40)
    
    # Check global state
    from ._core import _checker
    print(f"Global enabled: {_checker.enabled}")
    
    # Show relevant environment variables
    env_vars = ['CIPDB', 'CIPDB_ID', 'CIPDB_IDS', 'DEBUG']
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.environ.get(var, '<not set>')
        print(f"  {var}: {value}")
    
    # Show usage examples
    print("\nUsage Examples:")
    print("  python -m cipdb script.py")
    print("  python -m cipdb --id validate script.py")
    print("  python -m cipdb --ids validate,save script.py")
    print("  python -m cipdb --env DEBUG=true script.py")
    print("  CIPDB_ID=batch-2 python -m cipdb script.py")


def main() -> None:
    """Main entry point for cipdb CLI."""
    parser = argparse.ArgumentParser(
        description="Run Python scripts with cipdb conditional debugging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cipdb script.py                      # Run with all breakpoints enabled
  python -m cipdb --id validate script.py       # Run with specific breakpoint ID
  python -m cipdb --ids validate,save script.py # Run with multiple breakpoint IDs
  python -m cipdb --env DEBUG=true script.py    # Set environment variable
  python -m cipdb --disable script.py           # Run with debugging disabled
  python -m cipdb --status                       # Show current status
        """
    )
    
    parser.add_argument(
        '--id', 
        dest='cipdb_id',
        help='Set CIPDB_ID to run specific breakpoint'
    )
    
    parser.add_argument(
        '--ids',
        dest='cipdb_ids', 
        help='Set CIPDB_IDS to run multiple breakpoints (comma-separated)'
    )
    
    parser.add_argument(
        '--env', '--environment',
        dest='env_vars',
        action='append',
        help='Set environment variable (KEY=value or KEY for truthy)'
    )
    
    parser.add_argument(
        '--disable',
        action='store_true',
        help='Globally disable all cipdb breakpoints'
    )
    
    parser.add_argument(
        '--enable',
        action='store_true', 
        help='Globally enable cipdb breakpoints (default)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show cipdb status and environment variables'
    )
    
    parser.add_argument(
        'script',
        nargs='?',
        help='Python script to run'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='Arguments to pass to the script'
    )
    
    # Parse known args to allow passing unknown args to the script
    args, unknown_args = parser.parse_known_args()
    
    # Set up environment first (even for status command)
    setup_environment(args.env_vars, args.cipdb_id, args.cipdb_ids)
    
    # Handle status command
    if args.status:
        show_status()
        return
    
    # Require script unless showing status
    if not args.script:
        parser.error("script is required unless using --status")
    
    # Handle global enable/disable
    if args.disable:
        disable()
    elif args.enable:
        enable()
    
    # Prepare script arguments
    script_args = [args.script] + args.args + unknown_args
    
    # Update sys.argv to match what the script expects
    sys.argv = script_args
    
    # Run the script
    try:
        # Read and execute the script
        with open(args.script, 'rb') as f:
            script_code = compile(f.read(), args.script, 'exec')
        
        # Set up globals for the script
        script_globals = {
            '__file__': args.script,
            '__name__': '__main__',
            '__doc__': None,
            '__package__': None,
        }
        
        # Execute the script
        exec(script_code, script_globals)
        
    except FileNotFoundError:
        print(f"Error: Script '{args.script}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Let the exception propagate naturally
        raise


if __name__ == '__main__':
    main()