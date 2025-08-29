################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
"""
Generated protobuf files for the library.
"""

# Standard
import os

# First Party
# Get the import helper from the core
from autoai_ts_libs.deps.watson_core.data_model.protobufs import import_protobufs

proto_dir = os.path.dirname(os.path.realpath(__file__))

# Import all probobufs as extensions to the core
import_protobufs(proto_dir, __name__, globals())
