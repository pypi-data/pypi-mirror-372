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
"""The `workflows` within the `watson_core` library are essentially "super blocks" -- blocks
that call other blocks and compose an execution graph that describes how the output of one
block feeds into another block. Each `workflow` adheres to a contract that extends the contract
of a block, offering `.__init__()`, `.load()`, `.run()`, `.save()`, and `.train()` methods.
"""

from .base import workflow, WorkflowLoader, WorkflowSaver
