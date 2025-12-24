"""
Split models shim: import models from submodules.
This file keeps Django model discovery working while actual models live
in the `app/models/` package: `accounts.py`, `bnb.py`, and `verification.py`.
"""

from .accounts import *  # noqa: F401,F403
from .bnb import *  # noqa: F401,F403
from .verification import *  # noqa: F401,F403