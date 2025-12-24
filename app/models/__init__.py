"""app.models package: re-export model classes from submodules.

This package replaces the former flat app/models.py module. Django will
import `app.models` (this package) and discover models defined in the
submodules below.
"""

from .accounts import *  # noqa: F401,F403
from .bnb import *  # noqa: F401,F403
from .verification import *  # noqa: F401,F403
