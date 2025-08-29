################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""Top-level configuration for the `watson_core` library.  Mainly used for model management and
version.
"""

import os


from ..toolkit.errors import error_handler
from .config import *
from . import catalog

lib_config = Config.get_config(
    "watson_core",
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.yml"),
)

# Update the global error configurations
error_handler.ENABLE_ERROR_CHECKS = lib_config.enable_error_checks
error_handler.MAX_EXCEPTION_LOG_MESSAGES = lib_config.max_exception_log_messages
