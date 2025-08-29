<!-- ---
!-- Timestamp: 2025-08-29 04:53:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/cipdb/README.md
!-- --- -->

# cipdb - Conditional iPDB

Simple conditional debugging for Python with ID-based breakpoint control.

[![PyPI version](https://badge.fury.io/py/cipdb.svg)](https://badge.fury.io/py/cipdb)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install cipdb
```

## Quick Start

### Control by Global State Call in Python

```python
# Disable all debugging programmatically
cipdb.disable()
```

# Disable all debugging by Environmental Variable

``` python
CIPDB_ID=false python your_script.py
```

### Control by Boolean

```python
import cipdb

cipdb.set_trace()       # Identical with ipdb.set_trace()
cipdb.set_trace(False)  # Identical with pass
cipdb.set_trace(os.getenv("DEBUG")) # Development vs Production
cipdb.set_trace(os.getenv("AGENT_ID")=="DebuggingAgent_01") # Runner Specific for debugging by multiple agent
```

### Control by Breakpoint IDs
``` python
# your_script.py
def process_user(user):
    cipdb.set_trace(id="validate")
    validate(user)
    
    cipdb.set_trace(id="save")
    save_user(user)
    
    cipdb.set_trace(id="notify")
    send_notification(user)
```

``` bash
# Development mode: All ID breakpoints work (no env vars needed)
python your_script.py                            # All ID breakpoints trigger

# Production mode: Control with environment variables
CIPDB_IDS=validate,save python your_script.py   # Only stops at validate and save
CIPDB_IDS=save python your_script.py            # Only stops at save
CIPDB_ID=save python your_script.py             # Only stops at save (Equivalent to CIPDB_IDS=save)
```

## Priority Logic

Global Control > `CIPDB=false` Environmental Variable > ID Matching > Boolean Conditioning

## License

MIT

<!-- EOF -->