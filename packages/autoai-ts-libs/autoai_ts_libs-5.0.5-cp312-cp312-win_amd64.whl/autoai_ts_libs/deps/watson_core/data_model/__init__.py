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
"""Common data model containing all data structures that are passed in and out of blocks."""

# Third party
from google.protobuf.internal.python_message import GeneratedProtocolMessageType
from google.protobuf.pyext.cpp_message import (
    GeneratedProtocolMessageType as CPPGeneratedProtocolMessageType,
)

# Local
from . import protobufs
from . import base

from .streams import data_stream
from .streams.data_stream import *

from . import enums
from .enums import *

from . import producer
from .producer import *

from . import data_backends


def default_wrap_protobufs(protos_module, current_globals):
    """This function decorates the current globals with auto-generated protobuf
    wrapper classes for all classes that don't have a manually created class.

    Args:
        protos_module:  ModuleType
            The module holding the generated protobuf classes
        current_globals:  dict
            The globals() for the current data_model module
    """
    for attr_name, attr_val in vars(protos_module).items():
        if (
            isinstance(attr_val, GeneratedProtocolMessageType) or isinstance(attr_val, CPPGeneratedProtocolMessageType)
        ) and attr_name not in current_globals:
            current_globals[attr_name] = base._DataBaseMetaClass.__new__(
                base._DataBaseMetaClass,
                attr_name,
                (base.DataBase,),
                {"_proto_class": attr_val},
            )
