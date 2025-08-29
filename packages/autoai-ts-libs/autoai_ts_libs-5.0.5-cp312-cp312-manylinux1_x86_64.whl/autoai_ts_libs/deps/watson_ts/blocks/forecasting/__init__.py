################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
"""
Forecasting blocks solve the problem of predicting future values of a
timeseries
"""

# Local
from ...toolkit.hoist_module_imports import hoist_module_imports
from . import (
    arima,
    bats,
    fctk_deepar_estimator,
    fctk_l2f,
    fctk_lightgbm_ray,
    fctk_linear_regression,
    fctk_random_forest,
    hws_additive,
    hws_multiplicative,
    srom_mt2r,
    stat_forecasters,
)

# Block classes hoisted to the top level
# NOTE: These must come after the module imports so that the block modules
#   themselves can be tracked cleanly for optional modules
hoist_module_imports(globals())
