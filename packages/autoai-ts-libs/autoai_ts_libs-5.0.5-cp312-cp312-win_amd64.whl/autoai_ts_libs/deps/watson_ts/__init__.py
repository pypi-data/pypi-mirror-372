################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
"""
The Watson TS library provides a unified python interface for Watson timeseries
alogirthms through Watson Core.
"""

# First Party
from autoai_ts_libs.deps.watson_core import beta
from autoai_ts_libs.deps.watson_core.model_manager import *
import import_tracker

# Local
from . import config
from .config import *
from .toolkit.extras import get_extras_modules

# Import the core workloads of the library with lazy import errors to allow for
# independent dependency sets


with import_tracker.lazy_import_errors(get_extras_modules=get_extras_modules):
    # Local
    from . import blocks, workflows
