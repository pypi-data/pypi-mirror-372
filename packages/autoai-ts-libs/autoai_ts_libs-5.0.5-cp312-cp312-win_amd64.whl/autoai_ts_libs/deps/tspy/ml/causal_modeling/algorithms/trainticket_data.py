#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2024-2025 All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

"""
Routines to process trainticket log data for ingestion by causality algorithms
"""

import pandas as pd
import autoai_ts_libs.deps.tspy
import os
import numpy as np


def events_from_logs(datapath, json_filename):
    """
    This function processes microservice logs which are in json format
    and outputs event data. Events in this context are anomalous logs
    output by microservices.

    The microservice logs come from trainticket application.
    For information about this application, please see:
    https://github.com/FudanSELab/train-ticket

    This function performs the following steps:
    1. Loads json log data into a pandas df, fill in the null values.
    2. Move logs into WC TS datastructure.
    4. Filter out anomalous logs based on certain criteria.
    5. Select relevant fields _ts, _app .

    The final result can contain rows with duplicate (_ts, _app) pairs
    At this point we do not know how to remove row duplicates from WC TS.
    Therefore downstream processing will need to handle removal of
    such duplicates if required.

    Event data can be used by causal algorithms such as L0Hawkes, etc.

    Parameters
    ----------

    datapath: string
        Directory where the json log filename exists.
    json_filename: string
        Name of the log json filename, possibly zipped.

    Returns
    -------

    result: autoai_ts_libs.deps.tspy
        Processed events as WC time series with (_ts, _app) pairs.
        Two print statements inform the user of the input size
        and processed output size.
    """

    errorlog = os.path.join(datapath, json_filename)
    dfel = pd.read_json(errorlog, lines=True)
    print("Logs loaded into pandas dataframe, size:", dfel.shape)

    # Select relevant fields needed for causality.
    dfel = dfel[["_ts", "level", "_line", "_app"]]

    # We use 4 fields from the log data: _ts, _level, _line, _app
    # Fill null values to avoid WC TS loading issues.
    dfel["level"].fillna("NULL", inplace=True)
    dfel["_line"].fillna("NULL", inplace=True)
    dfel["_app"].fillna("NULL", inplace=True)

    # load into WC TS
    wc_dfel = autoai_ts_libs.deps.tspy.time_series(dfel, ts_column="_ts", value_column=["level", "_line", "_app"])

    # filter out relevant error logs
    estr1 = 'HTTP/1.1" 500'
    estr2 = "500 Internal Server Error] with root cause"
    estr3 = "ERROR"
    wc_dferr = wc_dfel.filter(lambda d: (estr1 in d["_line"]) or (estr2 in d["_line"]) or (estr3 in d["level"]))

    # remove '_app' = 'istio-proxy'
    estr4 = "istio-proxy"
    wc_dferr = wc_dferr.filter(lambda d: (estr4 not in d["_app"]))

    # select only _ts, _app fields
    wc_dferr = wc_dferr.map(lambda d: d["_app"])

    # print final shape
    print("Filtered error logs loaded in WC TS, size:", wc_dferr.to_df().shape)

    return wc_dferr


def ts_from_events(events, freq, rtype="ts"):
    """
    This function converts event data to timeseries data as counts of events
    within each time bin.
    The resulting timeseries is of shape T x L where
    T is the number of time bins
    L is the number of labels
    and each entry (i, j) counts number of labels j within time-bin i.
    The width of the time-bin is specified by the freq parameter (in pandas format).
    The output of this function is a timeseries that can be used
    by causal algorithms such as MMPC, NG, etc.

    Note duplicate rows are removed from event data before binning.

    Parameters
    ----------

    events : WC TS / pandas dataframe of tuples (timestamp, label)
        The column names must be timestamp, value (in WC / df)
    freq: string
        Width of time bin in pandas format e.g. '10S', '15T', etc.
        See: https://pandas.pydata.org/docs/user_guide/timeseries.html#offset-aliases
    rtype: string, 'ts' or 'df'
        return type can be WC timeseries (ts) or a pandas dataframe (df).
        Default is 'ts'

    Returns
    -------

    result: WC TS or pandas dataframe depending on rtype.
        data with T rows and (L + 1) columens.
        The first column is the timestamp, rest of columns are the L label names.
    """

    if isinstance(events, autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries):
        df = events.to_df()
    elif isinstance(events, pd.DataFrame):
        df = events
    else:
        print("events must be of type WC ts or pandas dataframe")

    df = df.drop_duplicates()

    a = df["timestamp"].min().floor("s")
    b = df["timestamp"].max().ceil("s")

    r = pd.date_range(a, b, freq=freq)
    x = np.repeat(np.array(r), 2, axis=0)[1:-1]
    x = np.array(x)[:].reshape(-1, 2)

    labels = df["value"].unique()

    mat = np.zeros((x.shape[0], len(labels)))

    for l in range(len(labels)):
        for j in range(x.shape[0]):
            label = labels[l]
            mat[j, l] = sum(df[df["timestamp"].between(x[j, 0], x[j, 1])]["value"] == label)

    final_df = pd.DataFrame(x[:, 0], columns=["timestamp"])

    final_df[labels] = mat

    if rtype == "df":
        return final_df
    elif rtype == "ts":
        final_df = final_df.set_index("timestamp")
        wcts = autoai_ts_libs.deps.tspy.time_series(final_df)
        return wcts
    else:
        print("Error: rtype should be 'ts' or 'df' ")
        return 0


def events_with_int_timestamps(events, precision="0.001s"):
    """
    This function retrives event data stored in WC TS object into
    a numpy array with *integer* timestamps.

    Parameters
    ----------

    events: WC or pandas dataframe with (timestamp, label) tuples.
    precision : precision of timestamp in pandas format
        e.g. '1s', '0.01s', etc.
        see: https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.delta.html

    Returns
    -------

    result: two 1-d numpy arrays
        timestamp_list_array: integer timestamps,
        event_type_list_array: labels
    """

    if isinstance(events, autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries):
        data = events.to_df()
    elif isinstance(events, pd.DataFrame):
        data = events
    else:
        print("events must be of type WC ts or pandas dataframe")

    timestamp_list = (data["timestamp"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(precision)
    event_type_list = data[value_column].values

    timestamp_list_array = np.array(timestamp_list).astype(np.dtype(int))
    event_type_list_array = np.array(event_type_list)

    return (timestamp_list_array, event_type_list_array)
