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
"""This module contains the python protobuf messages defined in the protobuf interfaces.
These are used as a backend and for serialization of watson_core objects but should generally
be used only internally or by those intending to serialze data structures. Otherwise,
you are probably interested in the classes found directly in data_model.
"""

# Standard
import importlib
import inspect
import os


def import_protobufs(proto_dir, package_base_name, current_globals):
    """Add protobuf definitions to the data model so that we can create custom models.
    To do this, we need to provide the path to the proto directory, the base package
    name, and the globals dict for the package being initialized. Usually this will be called
    in your __init__.py within your protobufs package, and look a lot like the following.

    import os

    # Get the import helper from the core
    from autoai_ts_libs.deps.watson_core.data_model.protobufs import import_protobufs
    wnlp_proto_dir = os.path.dirname(os.path.realpath(__file__))

    # Import all probobufs as extensions to the core
    import_protobufs(wnlp_proto_dir, __name__, globals())

    While we could do something like this with introspection, things (unfortunately) don't play
    nice with inspecting a wheel whose contents have been compiled to bytecode. :(

    Args:
        proto_dir: str
            Path to the proto directory, i.e., the directory that you __init__ protobuf file is in.
        package_base_name: str
            full name of your package, e.g., __name__ from the __init__ protobufs file.
        current_globals: dict
            global dictionary from your protobuf package __init__ file.
    """
    # One way we would like to figure out how to do this sort of thing with introspection.
    # Something like the below works, but it breaks if the extension wheel is compiled to
    # bytecode, because the caller_module ends up as None. Keeping it for reference in case
    # someone else finds a way to solve this though!
    #
    # caller = inspect.stack()[1]
    # caller_module = inspect.getmodule(caller[0])
    # caller_filename = caller_module.__file__
    # proto_dir = os.path.dirname(os.path.realpath(caller_filename))
    # current_globals = caller_module.__dict__
    # package_base_name = caller_module.__name__

    # look for *_pb2.py files in proto_dir, we will consider these to be our protobuf files
    module_names = [filename.rstrip(".py") for filename in os.listdir(proto_dir) if filename.endswith("_pb2.py")]

    # if there are no modules discovered, fallback to looking for .pyc files
    # this is necessary for binary-only releases
    if not module_names:
        module_names = [filename.rstrip(".pyc") for filename in os.listdir(proto_dir) if filename.endswith("_pb2.pyc")]

    # dynamically load all protobuf files as relative modules
    all_modules = [
        importlib.import_module("." + module_name, package=package_base_name) for module_name in module_names
    ]

    # name of protobuf package to use, we ignore anything not in watson_core_data_model for now
    _package_name = "watson_core_data_model"

    # add all protobuf messages to current module and to the core's data_model
    all_enum_names = []
    for module in all_modules:
        if module.DESCRIPTOR.package.startswith(_package_name):
            for message_name in module.DESCRIPTOR.message_types_by_name.keys():
                message_val = getattr(module, message_name)
                current_globals[message_name] = message_val
                globals()[message_name] = message_val
            for enum_name in module.DESCRIPTOR.enum_types_by_name.keys():
                enum_val = getattr(module, enum_name)
                current_globals[enum_name] = enum_val
                globals()[enum_name] = enum_val
                all_enum_names.append(enum_name)
    current_globals["all_enum_names"] = all_enum_names


# invoke the proto extension function on the protos for the core
core_proto_dir = os.path.dirname(os.path.realpath(__file__))
import_protobufs(core_proto_dir, __name__, globals())
