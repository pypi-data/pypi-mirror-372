################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
# *****************************************************************#
# (C) Copyright IBM Corporation 2020.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""Top-level configuration for the `watson_nlp` library. Mainly used for model management & version."""

# Standard
import os

# First Party
from autoai_ts_libs.deps.watson_core import ModelManager
from autoai_ts_libs.deps.watson_core.config import Config, compare_versions, get_credentials_or_default
from autoai_ts_libs.deps.watson_core.config.catalog import ModelCatalog, ResourceCatalog, WorkflowCatalog
import autoai_ts_libs.deps.watson_core as watson_core

lib_config = watson_core.config.Config.get_config(
    "watson_ts", os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.yml")
)

MODEL_CATALOG = watson_core.catalog.ModelCatalog({}, lib_config.library_version, lib_config.artifactory_base_path)
RESOURCE_CATALOG = watson_core.catalog.ResourceCatalog({}, lib_config.library_version, lib_config.artifactory_base_path)
WORKFLOW_CATALOG = watson_core.catalog.WorkflowCatalog({}, lib_config.library_version, lib_config.artifactory_base_path)

# aliases helpers for users
get_models = MODEL_CATALOG.get_models
get_alias_models = MODEL_CATALOG.get_alias_models
get_latest_models = MODEL_CATALOG.get_latest_models
get_resources = RESOURCE_CATALOG.get_resources
get_alias_resources = RESOURCE_CATALOG.get_alias_resources
get_latest_resources = RESOURCE_CATALOG.get_latest_resources
get_workflows = WORKFLOW_CATALOG.get_workflows

MODEL_MANAGER = ModelManager(lib_config.artifactory_base_path, MODEL_CATALOG, RESOURCE_CATALOG, WORKFLOW_CATALOG)

download = MODEL_MANAGER.download
extract = MODEL_MANAGER.extract
fetch = MODEL_MANAGER.fetch
load = MODEL_MANAGER.load
download_and_load = MODEL_MANAGER.download_and_load
resolve_and_load = MODEL_MANAGER.resolve_and_load
