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

import datetime

import numpy as np

from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures.transforms import UnaryTransform, BinaryTransform
from autoai_ts_libs.deps.tspy.data_structures.transforms.Filter import Filter
from autoai_ts_libs.deps.tspy.data_structures.transforms.FlatMap import FlatMap
from autoai_ts_libs.deps.tspy.data_structures.transforms.Map import Map
from autoai_ts_libs.deps.tspy.data_structures.transforms.MapWithIndex import MapWithIndex
from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage


class BoundTimeSeries:
    """
    A special form of materialized time-series (sorted collection) whose values are of type
    :class:`.Observation`.

    An observation-collection has the following properties:

    1. Sorted by observation time-tick
    2. Support for observations with duplicate time-ticks
    3. Duplicate time-ticks will keep ordering

    Examples
    --------
    create an observation-collection

    >>> import autoai_ts_libs.deps.tspy
    >>> ts_builder = autoai_ts_libs.deps.tspy.builder()
    >>> ts_builder.add(autoai_ts_libs.deps.tspy.Observation(1,1))
    >>> ts_builder.add(autoai_ts_libs.deps.tspy.Observation(2,2))
    >>> ts_builder.add(autoai_ts_libs.deps.tspy.Observation(1,3))
    >>> observations = ts_builder.result()
    >>> observations
    [(1,1),(1,3),(2,2)]

    iterate through this collection

    >>> for o in observations:
        ...print(o.time_tick, ",", o.value)
    1 , 1
    1 , 3
    2 , 2
    """

    def __init__(self, tsc, j_observations=None, py_observations=None):
        self._tsc = tsc
        self._obj_type = None
        self._j_observations = j_observations
        # py_observations currently is only being used for testing purposes (there is no usage within the code)
        # it is almost always safer to use j_observations as py_observations could be None in many cases
        self._py_observations = py_observations

    @property
    def trs(self):
        """
        Returns
        -------
        TRS : :class:`~autoai_ts_libs.deps.tspy.utils.TRS.TRS`
            this time-series time-reference-system
        """
        return self._j_observations.getTRS()

    def contains(self, time_tick):
        """
        Checks for containment of time-tick within the collection

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        bool
            True if an observation in this collection has the given time-tick, otherwise False
        """
        return self._j_observations.contains(time_tick)

    def ceiling(self, time_tick):
        """
        get the ceiling observation for the given time-tick. The ceiling is defined as the the observation which bares
        the same time-tick as the given time-tick, or if one does not exist, the next higher observation. If no such
        observation exists that satisfies these arguments, in the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the ceiling observation
        """
        return self.__obs_as_py(self._j_observations.ceiling(time_tick))

    def floor(self, time_tick):
        """
        get the floor observation for the given time-tick. The floor is defined as the the observation which bares
        the same time-tick as the given time-tick, or if one does not exist, the next lower observation. If no such
        observation exists that satisfies these arguments, in the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the floor observation
        """
        return self.__obs_as_py(self._j_observations.floor(time_tick))

    def higher(self, time_tick):
        """
        get the higher observation for the given time-tick. The higher is defined as the the observation which bares
        a time-tick greater than the given time-tick. If no such observation exists that satisfies these arguments, in
        the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the floor observation
        """
        return self.__obs_as_py(self._j_observations.higher(time_tick))

    def lower(self, time_tick):
        """
        get the lower observation for the given time-tick. The lower is defined as the the observation which bares
        a time-tick less than the given time-tick. If no such observation exists that satisfies these arguments, in
        the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the floor observation
        """
        return self.__obs_as_py(self._j_observations.lower(time_tick))

    def first(self):
        """
        get the first observation in this collection. The first observation is that observation which has the lowest
        timestamp in the collection. If 2 observations have the same timestamp, the first observation that was in the
        collection will be the one returned.

        Returns
        -------
        :class:`.Observation`
            the first observation in this collection
        """
        return self.__obs_as_py(self._j_observations.first())

    def last(self):
        """
        get the last observation in this collection. The last observation is that observation which has the highest
        timestamp in the collection. If 2 observations have the same timestamp, the last observation that was in the
        collection will be the one returned.

        Returns
        -------
        :class:`.Observation`
            the last observation in this collection
        """
        return self.__obs_as_py(self._j_observations.last())

    def is_empty(self):
        """checks if there is any observation

        Returns
        -------
        bool
            True if no observations exist in this collection, otherwise False
        """
        return self._j_observations.isEmpty()

    def __obs_as_py(self, j_observation):
        py_obj, obj_type = self._tsc.java_bridge.cast_to_py_if_necessary(j_observation.getValue(), self._obj_type)
        self._obj_type = obj_type
        return Observation(self._tsc, j_observation.getTimeTick(), py_obj)

    def to_time_series(self, granularity=None, start_time=None):
        """
        convert this collection to a time-series

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
        start_time : datetime, optional
            the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

        Returns
        -------
        :class:`.TimeSeries`
            a new time-series
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries

        if granularity is None and start_time is None:
            return TimeSeries(self._tsc, self._j_observations.toTimeSeries())
        else:
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS

            trs = TRS(self._tsc, granularity, start_time)
            return TimeSeries(self._tsc, self._j_observations.toTimeSeries(trs._j_trs), trs)

    @property
    def size(self):
        """
        Returns
        -------
        int
            the number of observations in this collection
        """
        return self._j_observations.size()

    def _iter_from_python(self, raw=False):
        ttb = self._j_observations.getTimeTickBuffer()
        # if our buffer is actually a dict of buffers, we need to go through each key and iterate through each buffer
        #  simultaneously
        if self._j_observations.bufferIsDict():
            import numpy as np

            mv_ttb = np.asarray(ttb)[ttb.position() : ttb.limit()]
            v = {}
            vector_len = {}
            keys = self._j_observations.getKeys()
            # get each buffer for each key
            for k in keys:
                if self._j_observations.isDirectBuffer(k):
                    v[k] = np.asarray(self._j_observations.getValueBuffer(k))[
                        self._j_observations.getValueBuffer(k)
                        .position() : self._j_observations.getValueBuffer(k)
                        .limit()
                    ]
                else:
                    # todo use the underlying util position and limit
                    current_j_util = self._j_observations.getPythonUtil().getValueUtil(k)
                    v[k] = self._j_observations.getValueList(k).subList(
                        current_j_util.getPosition(), current_j_util.getLimit()
                    )
                vector_len[k] = self._j_observations.getVectorLength(k)

            # if the data is raw, we only return the raw data, as to not incur an object creation overhead cost
            #  todo code duplication as we do not want the raw check inside our loop, consider creating a separate
            #   method
            if raw:
                for i in range(len(mv_ttb)):
                    res_v = {}
                    for k in keys:
                        if vector_len[k] == 0:
                            res_v[k] = v[k][i]
                        else:
                            res_v[k] = v[k][i * vector_len[k] : i * vector_len[k] + vector_len[k]]

                    yield mv_ttb[i], res_v
            # if the data is not raw, we want to return the python Observation objects back
            else:
                for i in range(len(mv_ttb)):
                    res_v = {}
                    for k in keys:
                        if vector_len[k] == 0:
                            res_v[k] = v[k][i]
                        else:
                            res_v[k] = v[k][i * vector_len[k] : i * vector_len[k] + vector_len[k]]

                    yield Observation(self._tsc, mv_ttb[i], res_v, contains_java=False)
        else:
            import numpy as np

            mv_ttb = np.asarray(ttb)[ttb.position() : ttb.limit()]
            # determine how to retrieve our values
            # if our collection is backed by a direct buffer, get the buffer, otherwise get the list
            if self._j_observations.isDirectBuffer():
                vb = self._j_observations.getValueBuffer()
                mv_vb = np.asarray(vb)[
                    self._j_observations.getValueBuffer().position() : self._j_observations.getValueBuffer().limit()
                ]
            else:
                current_j_util = self._j_observations.getPythonUtil()
                mv_vb = self._j_observations.getValueList().subList(
                    current_j_util.getPosition(), current_j_util.getLimit()
                )
            vector_len = self._j_observations.getVectorLength()

            # check if this is a vector time-series or just a plain time-series of values
            if vector_len == 0:

                # if the data is raw, we only return the raw data, as to not incur an object creation overhead cost
                #  todo code duplication as we do not want the raw check inside our loop, consider creating a separate
                #   method
                if raw:
                    for i in range(len(mv_vb)):
                        yield mv_ttb[i], mv_vb[i]
                # if the data is not raw, we want to return the python Observation objects back
                else:
                    for i in range(len(mv_vb)):
                        yield Observation(self._tsc, mv_ttb[i], mv_vb[i], contains_java=False)
            else:
                # if the data is backed by a direct buffer we have to map the data to a list, otherwise we just return
                if self._j_observations.isDirectBuffer():
                    i = 0
                    # if the data is raw, we only return the raw data, as to not incur an object creation overhead cost
                    #  todo code duplication as we do not want the raw check inside our loop, consider creating a separate
                    #   method
                    if raw:
                        while i < len(mv_vb):
                            tt = mv_ttb[int(i / vector_len)]
                            val = mv_vb[i : i + vector_len].tolist()
                            i += vector_len
                            yield tt, val
                    # if the data is not raw, we want to return the python Observation objects back
                    else:
                        while i < len(mv_vb):
                            res = Observation(
                                self._tsc,
                                mv_ttb[int(i / vector_len)],
                                mv_vb[i : i + vector_len].tolist(),
                                contains_java=False,
                            )
                            i += vector_len
                            yield res
                else:
                    i = 0
                    # if the data is raw, we only return the raw data, as to not incur an object creation overhead cost
                    #  todo code duplication as we do not want the raw check inside our loop, consider creating a separate
                    #   method
                    if raw:
                        while i < len(mv_vb):
                            tt = mv_ttb[int(i / vector_len)]
                            val = mv_vb[i : i + vector_len]
                            i += vector_len
                            yield tt, val
                    # if the data is not raw, we want to return the python Observation objects back
                    else:
                        while i < len(mv_vb):
                            res = Observation(
                                self._tsc,
                                mv_ttb[int(i / vector_len)],
                                mv_vb[i : i + vector_len],
                                contains_java=False,
                            )
                            i += vector_len
                            yield res

    def _iter_from_java(self, raw=False):
        j_iterator = self._j_observations.iterator()
        while j_iterator.hasNext():
            j_obs = j_iterator.next()
            py_obj, obj_type = self._tsc.java_bridge.cast_to_py_if_necessary(j_obs.getValue(), self._obj_type)
            self._obj_type = obj_type
            if raw:
                yield j_obs.getTimeTick(), py_obj
            else:
                yield Observation(self._tsc, j_obs.getTimeTick(), py_obj, contains_java=False)

    def _raw_iter(self):
        if self._j_observations.isPythonBacked():
            return self._iter_from_python(raw=True)
        else:
            return self._iter_from_java(raw=True)

    def __iter__(self):
        # todo clean up this method since a lot of logic is here!!!
        if self._j_observations.isPythonBacked():
            return self._iter_from_python()
        else:
            return self._iter_from_java()

    def __str__(self):
        if self._j_observations is None:
            return ""
        else:
            return str(self._j_observations.toString())

    def __repr__(self):
        if self._j_observations is None:
            return ""
        else:
            return str(self._j_observations.toString())

    def __eq__(self, other):
        return self._j_observations.equals(other._j_observations)

    def __len__(self):
        return self.size

    def add_annotation(self, key, annotation_reducer):
        if hasattr(annotation_reducer, "__call__"):
            annotation_reducer = self._tsc.java_bridge.java_implementations.UnaryMapFunction(annotation_reducer)
        return BoundTimeSeries(self._tsc, self._j_observations.addAnnotation(key, annotation_reducer))

    def map_with_annotation(self, func):
        return BoundTimeSeries(
            self._tsc,
            self._j_observations.mapWithAnnotation(self._tsc.java_bridge.java_implementations.BinaryMapFunction(func)),
        )

    def map(self, func):
        from autoai_ts_libs.deps.tspy.functions import expressions

        if hasattr(func, "__call__"):
            if self._tsc.java_bridge_is_default:
                return self.transform(Map(func))
            else:
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.map(
                        expressions._wrap_object_expression(
                            self._tsc.java_bridge.java_implementations.UnaryMapFunction(func)
                        )
                    ),
                )
        else:
            return BoundTimeSeries(
                self._tsc,
                self._j_observations.map(expressions._wrap_object_expression(func)),
            )

    def map_with_index(self, func):
        if hasattr(func, "__call__"):
            if self._tsc.java_bridge_is_default:
                return self.transform(MapWithIndex(func))
            else:
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.mapWithIndex(
                        self._tsc.java_bridge.java_implementations.BinaryMapFunction(func)
                    ),
                )
        else:
            return BoundTimeSeries(
                self._tsc,
                self._j_observations.mapWithIndex(
                    self._tsc.packages.time_series.transforms.utils.python.Expressions.toBinaryMapWithIndexFunction(
                        func
                    )
                ),
            )

    def flatmap(self, func):
        if self._tsc.java_bridge_is_default:
            return self.transform(FlatMap(func))
        else:
            return BoundTimeSeries(
                self._tsc,
                self._j_observations.flatMap(self._tsc.java_bridge.java_implementations.UnaryMapFunction(func)),
            )

    def filter(self, func):
        if hasattr(func, "__call__"):
            if self._tsc.java_bridge_is_default:
                return self.transform(Filter(func))
            else:
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.filter(self._tsc.java_bridge.java_implementations.FilterFunction(func)),
                )
        else:
            return BoundTimeSeries(self._tsc, self._j_observations.filter(func))

    def fillna(self, interpolator, null_value=None):
        if hasattr(interpolator, "__call__"):
            interpolator = self._tsc.java_bridge.java_implementations.Interpolator(interpolator)

        return BoundTimeSeries(self._tsc, self._j_observations.fillna(interpolator, null_value))

    def transform(self, *args):
        if len(args) == 0:
            raise ValueError("must provide at least one argument")
        elif len(args) == 1:
            if issubclass(type(args[0]), UnaryTransform):
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.transform(
                        self._tsc.packages.time_series.core.transform.python.PythonUnaryTransform(
                            self._tsc.java_bridge.java_implementations.JavaToPythonUnaryTransformFunction(args[0])
                        )
                    ),
                )
            else:
                return BoundTimeSeries(self._tsc, self._j_observations.transform(args[0]))
        elif len(args) == 2:
            if issubclass(type(args[1]), BinaryTransform):
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.transform(
                        args[0]._j_observations,
                        self._tsc.packages.time_series.core.transform.python.PythonBinaryTransform(
                            self._tsc.java_bridge.java_implementations.JavaToPythonBinaryTransformFunction(args[1])
                        ),
                    ),
                )
            else:
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.transform(args[0]._j_observations, args[1]),
                )

    def to_segments(self, segment_transform, annotation_map=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        if annotation_map is None:
            return BoundSegmentTimeSeries(self._tsc, self._j_observations.toSegments(segment_transform))
        else:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.toSegments(
                    segment_transform,
                    self._tsc.java_bridge.convert_to_java_map(annotation_map),
                ),
            )

    def segment(self, window, step=1, enforce_size=True):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        return BoundSegmentTimeSeries(self._tsc, self._j_observations.segment(window, step, enforce_size))

    def segment_by(self, func):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        return BoundSegmentTimeSeries(
            self._tsc,
            self._j_observations.segmentBy(self._tsc.java_bridge.java_implementations.UnaryMapFunction(func)),
        )

    def segment_by_time(self, window, step):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        return BoundSegmentTimeSeries(self._tsc, self._j_observations.segmentByTime(window, step))

    def segment_by_anchor(self, func, left_delta, right_delta, perc=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        if hasattr(func, "__call__"):
            func = self._tsc.java_bridge.java_implementations.FilterFunction(func)
        else:
            func = self._tsc.packages.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        if perc is None:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByAnchor(func, left_delta, right_delta),
            )
        else:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByAnchor(func, left_delta, right_delta, perc),
            )

    def segment_by_changepoint(self, change_point=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        if change_point is None:
            return BoundSegmentTimeSeries(self._tsc, self._j_observations.segmentByChangePoint())
        else:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByChangePoint(
                    self._tsc.java_bridge.java_implementations.BinaryMapFunction(change_point)
                ),
            )

    def segment_by_marker(self, *args, **kwargs):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import (
            BoundSegmentTimeSeries,
        )

        arg_len = len(args)

        if arg_len != 0 and len(kwargs) != 0:
            raise ValueError("Can only specify args or kwargs")
        if arg_len != 0:

            # this is a bi-marker (2 marker functions)
            if arg_len > 1 and hasattr(args[1], "__call__"):
                start_marker = args[0]
                end_marker = args[1]
                start_inclusive = args[2] if arg_len > 2 else True
                end_inclusive = args[3] if arg_len > 3 else True
                start_on_first = args[4] if arg_len > 4 else False
                end_on_first = args[5] if arg_len > 5 else True

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
                        self._tsc.java_bridge.java_implementations.FilterFunction(start_marker),
                        self._tsc.java_bridge.java_implementations.FilterFunction(end_marker),
                        start_inclusive,
                        end_inclusive,
                        start_on_first,
                        end_on_first,
                    ),
                )
            # this is a single marker
            else:
                marker = args[0]
                start_inclusive = args[1] if arg_len > 1 else True
                end_inclusive = args[2] if arg_len > 2 else True
                requires_start_and_end = args[3] if arg_len > 3 else False

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
                        self._tsc.java_bridge.java_implementations.FilterFunction(marker),
                        start_inclusive,
                        end_inclusive,
                        requires_start_and_end,
                    ),
                )
        else:

            # this is a bi-marker (2 marker functions)
            if "start_marker" in kwargs and "end_marker" in kwargs:
                start_marker = kwargs["start_marker"]
                end_marker = kwargs["end_marker"]
                start_inclusive = kwargs["start_inclusive"] if "start_inclusive" in kwargs else True
                end_inclusive = kwargs["end_inclusive"] if "end_inclusive" in kwargs else True
                start_on_first = kwargs["start_on_first"] if "start_on_first" in kwargs else False
                end_on_first = kwargs["end_on_first"] if "end_on_first" in kwargs else True

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
                        self._tsc.java_bridge.java_implementations.FilterFunction(start_marker),
                        self._tsc.java_bridge.java_implementations.FilterFunction(end_marker),
                        start_inclusive,
                        end_inclusive,
                        start_on_first,
                        end_on_first,
                    ),
                )
            elif "marker" in kwargs:
                marker = kwargs["marker"]
                start_inclusive = kwargs["start_inclusive"] if "start_inclusive" in kwargs else True
                end_inclusive = kwargs["end_inclusive"] if "end_inclusive" in kwargs else True
                requires_start_and_end = (
                    kwargs["requires_start_and_end"] if "requires_start_and_end" in kwargs else False
                )

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
                        self._tsc.java_bridge.java_implementations.FilterFunction(marker),
                        start_inclusive,
                        end_inclusive,
                        requires_start_and_end,
                    ),
                )
            else:
                raise ValueError(
                    "kwargs must contain at the very least a 'start_marker' and 'end_marker' OR a 'marker' "
                )

    def lag(self, lag_amount):
        return BoundTimeSeries(self._tsc, self._j_observations.lag(lag_amount))

    def shift(self, shift_amount, default_value=None):
        return BoundTimeSeries(self._tsc, self._j_observations.shift(shift_amount, default_value))

    def resample(self, period, func):
        if hasattr(func, "__call__"):
            func = self._tsc.java_bridge.java_implementations.Interpolator(func)

        return BoundTimeSeries(
            self._tsc,
            self._tsc.packages.time_series.core.utils.PythonConnector.resample(self._j_observations, period, func),
        )

    def inner_join(self, time_series, join_func=None):
        if join_func is None:
            join_func = self._tsc.packages.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = (
            self._tsc.java_bridge.java_implementations.BinaryMapFunction(join_func)
            if hasattr(join_func, "__call__")
            else join_func
        )

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.innerJoin(time_series._j_observations, join_func),
        )

    def full_join(self, time_series, join_func=None, left_interp_func=None, right_interp_func=None):
        if join_func is None:
            join_func = self._tsc.packages.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = (
            self._tsc.java_bridge.java_implementations.BinaryMapFunction(join_func)
            if hasattr(join_func, "__call__")
            else join_func
        )

        if hasattr(left_interp_func, "__call__"):
            interpolator_left = self._tsc.java_bridge.java_implementations.Interpolator(left_interp_func)
        else:
            if left_interp_func is None:
                interpolator_left = (
                    self._tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
                )
            else:
                interpolator_left = left_interp_func

        if hasattr(right_interp_func, "__call__"):
            interpolator_right = self._tsc.java_bridge.java_implementations.Interpolator(right_interp_func)
        else:
            if right_interp_func is None:
                interpolator_right = (
                    self._tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
                )
            else:
                interpolator_right = right_interp_func

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.fullJoin(
                time_series._j_observations,
                join_func,
                interpolator_left,
                interpolator_right,
            ),
        )

    def left_join(self, time_series, join_func=None, interp_func=None):
        if join_func is None:
            join_func = self._tsc.packages.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = (
            self._tsc.java_bridge.java_implementations.BinaryMapFunction(join_func)
            if hasattr(join_func, "__call__")
            else join_func
        )

        if hasattr(interp_func, "__call__"):
            interpolator = self._tsc.java_bridge.java_implementations.Interpolator(interp_func)
        else:
            if interp_func is None:
                interpolator = (
                    self._tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
                )
            else:
                interpolator = interp_func

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.leftJoin(time_series._j_observations, join_func, interpolator),
        )

    def right_join(self, time_series, join_func=None, interp_func=None):
        if join_func is None:
            join_func = self._tsc.packages.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = (
            self._tsc.java_bridge.java_implementations.BinaryMapFunction(join_func)
            if hasattr(join_func, "__call__")
            else join_func
        )

        if hasattr(interp_func, "__call__"):
            interpolator = self._tsc.java_bridge.java_implementations.Interpolator(interp_func)
        else:
            if interp_func is None:
                interpolator = (
                    self._tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
                )
            else:
                interpolator = interp_func

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.rightJoin(time_series._j_observations, join_func, interpolator),
        )

    def left_outer_join(self, time_series, join_func=None, interp_func=None):
        """join two time-series based on a temporal left outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.Observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.Observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.Observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.Observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.Observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.Observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.Observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal left outer join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.left_outer_join(orig_right, interp_func=interpolators.next())
        >>> ts
        TimeStamp: 1     Value: [1, 1]
        """
        if join_func is None:
            join_func = self._tsc.packages.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = (
            self._tsc.java_bridge.java_implementations.BinaryMapFunction(join_func)
            if hasattr(join_func, "__call__")
            else join_func
        )

        if hasattr(interp_func, "__call__"):
            interpolator = self._tsc.java_bridge.java_implementations.Interpolator(interp_func)
        else:
            if interp_func is None:
                interpolator = (
                    self._tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
                )
            else:
                interpolator = interp_func

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.leftOuterJoin(time_series._j_observations, join_func, interpolator),
        )

    def right_outer_join(self, time_series, join_func=None, interp_func=None):
        """join two time-series based on a temporal right outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.Observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.Observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.Observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.Observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.Observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.Observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.Observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal right outer join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.right_outer_join(orig_right, interp_func=interpolators.prev())
        >>> ts
        TimeStamp: 2     Value: [1, 1]
        TimeStamp: 5     Value: [4, 4]
        """
        if join_func is None:
            join_func = self._tsc.packages.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = (
            self._tsc.java_bridge.java_implementations.BinaryMapFunction(join_func)
            if hasattr(join_func, "__call__")
            else join_func
        )

        if hasattr(interp_func, "__call__"):
            interpolator = self._tsc.java_bridge.java_implementations.Interpolator(interp_func)
        else:
            if interp_func is None:
                interpolator = (
                    self._tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
                )
            else:
                interpolator = interp_func

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.rightOuterJoin(time_series._j_observations, join_func, interpolator),
        )

    def forecast(self, num_predictions, fm, confidence=None):
        j_fm = self._tsc.packages.time_series.transforms.forecastors.Forecasters.general(fm._j_fm)

        try:
            j_observations = self._j_observations.forecast(
                num_predictions, j_fm, 1.0 if confidence is None else confidence
            )
            ts_builder = self._tsc.java_bridge.builder()
            from autoai_ts_libs.deps.tspy.data_structures import Prediction

            if confidence is None:
                for j_obs in j_observations.iterator():
                    ts_builder.add(
                        (
                            j_obs.getTimeTick(),
                            Prediction(self._tsc, j_obs.getValue()).value,
                        )
                    )
            else:
                for j_obs in j_observations.iterator():
                    ts_builder.add((j_obs.getTimeTick(), Prediction(self._tsc, j_obs.getValue())))
            return ts_builder.result()

        except:
            # if self._tsc._kill_gateway_on_exception:
            #     self._tsc._gateway.shutdown()
            msg = "There was an issue forecasting, this may be caused by incorrect types given to chained operations"
            raise TSErrorWithMessage(msg)

    def reduce(self, *args):
        try:
            if len(args) == 0:
                raise ValueError("must provide at least one argument")
            elif len(args) == 1:
                return self._j_observations.reduce(args[0])
            else:
                return self._j_observations.reduce(args[0]._j_ts, args[1])
        except:
            # if self._tsc._kill_gateway_on_exception:
            #     self._tsc._gateway.shutdown()
            raise TSErrorWithMessage(
                "There was an issue reducing, this may be caused by incorrect types given to " "chained operations"
            )

    def head_set(self, to_time_tick, to_inclusive):
        return BoundTimeSeries(self._tsc, self._j_observations.headSet(to_time_tick, to_inclusive))

    def tail_set(self, from_time_tick, from_inclusive):
        return BoundTimeSeries(self._tsc, self._j_observations.tailSet(from_time_tick, from_inclusive))

    def sub_set(self, from_time_tick, from_inclusive, to_time_tick, to_inclusive):
        return BoundTimeSeries(
            self._tsc,
            self._j_observations.subSet(from_time_tick, from_inclusive, to_time_tick, to_inclusive),
        )

    def to_numpy(self):
        return self._tsc.java_bridge.converters.bound_ts_to_numpy(self)

    def to_df(self, array_index_to_col=False):
        return self._tsc.java_bridge.converters.bound_ts_to_df(self, array_index_to_col)
