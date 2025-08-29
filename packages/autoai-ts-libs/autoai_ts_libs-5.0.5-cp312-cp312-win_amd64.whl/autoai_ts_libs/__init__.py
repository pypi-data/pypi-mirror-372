################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################


try:
    import ai4ml_ts
except:
    import sys
    from autoai_ts_libs import watfore

    sys.modules["ai4ml_ts.estimators"] = watfore

from autoai_ts_libs.version import __version__

import logging

# disable debug messages in the notebook
for x in ("h5py._conv", "blib2to3", "autoai_ts_libs.deps.tspy.data_structures.context"):
    logging.getLogger(x).setLevel(logging.WARNING)
