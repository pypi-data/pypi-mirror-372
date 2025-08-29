################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
"""
Common data model containing all data structures that are passed in and out of
blocks.
"""

# ordering is important here to permit protobuf loading and dynamic
# `watson_core` setup
# pylint: disable=wrong-import-order,wrong-import-position

# Standard
from typing import Union

# Third Party
import pandas as pd

# First Party
# Import core enums and add in from this data model
from autoai_ts_libs.deps.watson_core.data_model import default_wrap_protobufs, enums

# Local
# Import the protobufs
from . import protobufs

enums.import_enums(globals())


# First Party
# Import producer and data streams from the core
from autoai_ts_libs.deps.watson_core.data_model import *

# Local
from .time_types import (
    PeriodicTimeSequence,
    PointTimeSequence,
    Seconds,
    TimeDuration,
    TimePoint,
    ValueSequence,
)

from .timeseries import TimeSeries  # isort:skip
from .multi_timeseries import MultiTimeSeries  # isort:skip

default_wrap_protobufs(protobufs, globals())

AnyTimeSeriesType = Union[
    MultiTimeSeries,
    pd.DataFrame,
    "pyspark.sql.DataFrame",
    "tspy.data_structures.TimeSeries",
    "tspy.data_structures.MultiTimeSeries",
]
