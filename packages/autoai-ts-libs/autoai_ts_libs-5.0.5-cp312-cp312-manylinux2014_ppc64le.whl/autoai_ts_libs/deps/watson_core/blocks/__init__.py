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
"""The `blocks` within the `watson_core` library are essentially the conduits of algorithms.
Each block follows sets of principles about how they work including `.__init__()`, `.load()`,
`.run()`, `.save()`, and `.train()`. Blocks often require each other as inputs and support many
models.
"""

#################
## Core Blocks ##
#################

from .base import block, BlockSaver
