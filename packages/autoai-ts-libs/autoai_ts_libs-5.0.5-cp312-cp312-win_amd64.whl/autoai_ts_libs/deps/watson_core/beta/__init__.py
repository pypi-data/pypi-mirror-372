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
"""This builds the catalog from a config and allows a user to access
methods directly with watson_nlp.beta.<method>
"""
from autoai_ts_libs.deps.watson_core.beta.catalog.factory import build_catalog_from_config

# This seems sketchy AF
import autoai_ts_libs.deps.watson_core as watson_core

BETA_CATALOG = build_catalog_from_config(watson_core.lib_config)

if BETA_CATALOG is not None:
    get_models = BETA_CATALOG.models
    download = BETA_CATALOG.cache
    downloaded = BETA_CATALOG.cached
    load = BETA_CATALOG.load
    save = BETA_CATALOG.save
    exists = BETA_CATALOG.exists
    print_tree = BETA_CATALOG.print_tree
    delete = BETA_CATALOG.delete

__all__ = ["BETA_CATALOG"]
