################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2024-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
"""
This module implements a decorator that can be used to add conversion logic from
pd.DataFrame to Timeseries objects for function arguments. This is used to
enable native DataFrame workflows while implementing individual blocks against
the standard Timeseries object type.
"""

# Standard
from functools import partial
from typing import Any, Callable, Iterable, List, Optional, Tuple, Union
import copy
import inspect
import warnings

# Third Party
import wrapt

# Local
from ..blocks.watson_core_mixins import WatsonCoreBlockWrapper
from .conversions import (  # MTS Converters; MTS OR TS Converters
    KEY_SOURCE_ARG,
    TIMESTAMP_SOURCE_ARG,
    VALUE_SOURCE_ARG,
    _to_dm_converter,
    _to_tspy_converter,
    _to_tspy_mts_converter,
)
from autoai_ts_libs.deps.watson_ts import base_mixins

## Public ######################################################################
import autoai_ts_libs.deps.watson_ts.base_mixins as base_mixins


def tspy_mts_arg(
    wrapped: Optional[Callable] = None,
    *,
    arg_name: Optional[str] = None,
    key_col_arg: Union[Iterable[str], str] = KEY_SOURCE_ARG,
    ts_col_arg: str = TIMESTAMP_SOURCE_ARG,
    val_col_arg: str = VALUE_SOURCE_ARG,
    inverse_conversion: bool = True,
    persist_source_args: bool = False,
    shape_change=False,
    **kwargs,
):
    return _arg_converter_decorator(
        wrapped,
        converter=_to_tspy_mts_converter,
        arg_name=arg_name,
        key_col_arg=key_col_arg,
        ts_col_arg=ts_col_arg,
        val_col_arg=val_col_arg,
        inverse_conversion=inverse_conversion,
        persist_source_args=persist_source_args,
        shape_change=shape_change,
        **kwargs,
    )


# TS OR MTS ARGUMENTS #
def tspy_arg(
    wrapped: Optional[Callable] = None,
    *,
    arg_name: Optional[str] = None,
    key_col_arg: Union[Iterable[str], str] = KEY_SOURCE_ARG,
    ts_col_arg: str = TIMESTAMP_SOURCE_ARG,
    val_col_arg: str = VALUE_SOURCE_ARG,
    inverse_conversion: bool = True,
    persist_source_args: bool = False,
    ignore_types=None,
    shape_change=False,
    **kwargs,
):
    return _arg_converter_decorator(
        wrapped,
        converter=_to_tspy_converter,
        arg_name=arg_name,
        key_col_arg=key_col_arg,
        ts_col_arg=ts_col_arg,
        val_col_arg=val_col_arg,
        inverse_conversion=inverse_conversion,
        persist_source_args=persist_source_args,
        ignore_types=ignore_types,
        shape_change=shape_change,
        **kwargs,
    )


def dm_arg(
    wrapped: Optional[Callable] = None,
    *,
    arg_name: Optional[str] = None,
    key_col_arg: Union[Iterable[str], str] = KEY_SOURCE_ARG,
    ts_col_arg: str = TIMESTAMP_SOURCE_ARG,
    val_col_arg: str = VALUE_SOURCE_ARG,
    inverse_conversion: bool = True,
    ignore_types=None,
    persist_source_args=False,
    **kwargs,
):
    return _arg_converter_decorator(
        wrapped,
        converter=_to_dm_converter,
        arg_name=arg_name,
        key_col_arg=key_col_arg,
        ts_col_arg=ts_col_arg,
        val_col_arg=val_col_arg,
        inverse_conversion=inverse_conversion,
        ignore_types=ignore_types,
        persist_source_args=persist_source_args,
        **kwargs,
    )


## Implementation Details ######################################################


def _arg_converter_decorator(
    wrapped: Optional[Callable] = None,
    *,
    converter: Callable,
    arg_name: Optional[str] = None,
    key_col_arg: Union[Iterable[str], str],
    ts_col_arg: str = "ts_col",
    val_col_arg: str = "val_col",
    inverse_conversion: bool = True,
    ignore_types=None,
    persist_source_args=False,
    shape_change=False,
    **bound_converter_kwargs,
):
    """This is the main converter implementation that is implemented above by
    the various public directional decorators

    KWArgs:
        converter:  Callable
            The converter to call for this decorator implementation
        arg_name:  Optional[str]
            The name of the argument that is convertable to a DataFrame. For
            single-argument functions, this can be omitted
        ts_col_arg:  str
            The name of the argument to add to the signature of the wrapped
            function that will be used to specify the column containing the
            timestamp series.
        val_col_arg:  str
            The name of the argument to add to the signature of the wrapped
            function that will be used to specify the column containing the
            value series.
        inverse_conversion: bool
            if True, will convert the output of the block back to the input type, otherwise will output as is
            (default is True)
        **bound_converter_kwargs:
            Additional key/value pairs that should be bound into the converter
            call
    """
    # Handle without parens
    if wrapped is None:
        return partial(
            _arg_converter_decorator,
            converter=converter,
            arg_name=arg_name,
            key_col_arg=key_col_arg,
            ts_col_arg=ts_col_arg,
            val_col_arg=val_col_arg,
            inverse_conversion=inverse_conversion,
            ignore_types=ignore_types,
            persist_source_args=persist_source_args,
            shape_change=shape_change,
            **bound_converter_kwargs,
        )

    # Get the names of the arguments for the passed in function
    sig = inspect.signature(wrapped)

    # If no arg name given and there is a single argument to this function,
    # use that name
    # todo: adding no cover to this til I see where exactly it gets used
    if arg_name is None:  # pragma: no cover
        fn_args = list(sig.parameters)
        # If this is a member function, strip off the first arg name. Since
        # at the point member functions have not yet been bound, we need to
        # attempt to deduce this with trickery. To do so, we look at the
        # qualname versus the name. This gets tricky for inline functions or
        # nested functions, so we split off any '<globals>.' or '<locals>.'
        # names.
        local_qualname = wrapped.__qualname__.split(">.")[-1]
        fn_name = wrapped.__name__
        if local_qualname != fn_name:
            fn_args = fn_args[1:]
        assert len(fn_args) == 1, f"Cannot infer arg_name for functions with multiple arguments: {fn_args}"
        arg_name = fn_args[0]

    # Make sure the arg name belongs with this function
    assert arg_name in sig.parameters, f"Invalid argument not in wrapped function {arg_name}"
    arg_pos = list(sig.parameters).index(arg_name)

    # The function that replaces the wrapped function. This is where the
    # conversion logic lives that will be invoked at runtime.
    @wrapt.decorator(adapter=_argspec_factory(wrapped, [(key_col_arg, None), (ts_col_arg, None), (val_col_arg, None)]))
    def decorator(wrapped, instance, args, kwargs):
        # If this is a member function, we need to incorporate the positional
        # arg for the instance in the function
        pos_increment = 0 if instance is None else -1
        lookup_pos = arg_pos + pos_increment

        # Find the named argument
        if len(args) > lookup_pos:
            in_pos_args = True
            arg_val = args[lookup_pos]
        else:
            in_pos_args = False
            arg_val = kwargs.get(arg_name)

        # if the instance does not exist, but it is given in kwargs (decorator not part of class)
        # set the instance
        if not instance and "instance" in kwargs:
            instance = kwargs["instance"]

        # If a value is provided for the arg, check to see if it's a data
        # frame and convert it accordingly
        is_type_to_ignore = ignore_types and type(arg_val) in ignore_types
        # add a check to see if we should just continue without datamodel if correct type
        # todo this will need to be added with watson core as well
        if isinstance(instance, base_mixins.SKLearnEstimatorWrapper) and not is_type_to_ignore:
            is_type_to_ignore = instance._is_type_to_ignore(arg_val)

        if arg_val is not None and not is_type_to_ignore:
            # Shallow copy the kwargs so that mutating ops don't accidentally
            # mutate a shared kwargs dict
            kwargs = copy.copy(kwargs)

            key_source_in_kwargs = key_col_arg in kwargs
            ts_source_in_kwargs = ts_col_arg in kwargs
            val_source_in_kwargs = val_col_arg in kwargs

            # Get the columns and make sure they're given
            if persist_source_args:
                key_col_name = kwargs.get(key_col_arg, None)
                ts_col_name = kwargs.get(ts_col_arg, None)
                val_col_name = kwargs.get(val_col_arg, None)
            else:
                key_col_name = kwargs.pop(key_col_arg, None)
                ts_col_name = kwargs.pop(ts_col_arg, None)
                val_col_name = kwargs.pop(val_col_arg, None)

            # if the class already has these protected attributes specified, use them if not already set
            if isinstance(instance, base_mixins.SKLearnEstimatorWrapper):
                ts_col_name = instance.block_ts_col_name(ts_col_name)
                key_col_name = instance.block_key_col_name(key_col_name)
                val_col_name = instance.block_value_col_name(val_col_name)
            # this is a watson core block which just uses the key_source, timestamp_source, value_source
            elif isinstance(instance, WatsonCoreBlockWrapper):
                params = instance.get_params()
                if not key_source_in_kwargs:
                    key_col_name = params.get("key_source", None)
                if not ts_source_in_kwargs:
                    ts_col_name = params.get("timestamp_source", None)
                if not val_source_in_kwargs:
                    val_col_name = params.get("value_source", None)

            # Call the converter
            # NOTE: The converters will handle type-specific validation errors
            # todo maybe we should add a inverse conversion to the output of this
            updated_arg_val, inverse_conversion_func = converter(
                input_arg=arg_val,
                **{
                    KEY_SOURCE_ARG: key_col_name,
                    TIMESTAMP_SOURCE_ARG: ts_col_name,
                    VALUE_SOURCE_ARG: val_col_name,
                },
                **bound_converter_kwargs,
            )

            # we are coming from a SKLearnEstimatorWrapper, we need to make sure to map the columns properly if required
            # if isinstance(updated_arg_val, dm.TimeSeries) and isinstance(instance, base_mixins.SKLearnEstimatorWrapper):
            #     instance._convert_columns_to_internal_type(updated_arg_val)

            # Place the updated arugment back in the appropriate place
            if in_pos_args:
                args = list(args)
                args[lookup_pos] = updated_arg_val
            else:
                kwargs[arg_name] = updated_arg_val

            # todo if we pass this along we may be able to use this in models if the output is a certain type and
            #  we want the user to get the same type
            #  how does this get pickled???
            # kwargs["_inverse_conversion_func"] = inverse_conversion_func

        # Invoke the wrapped function with the updated arguments
        # todo: might need to include the key/ts/value sources in kwargs here for kshape
        wrapped_output = wrapped(*args, **kwargs)

        if not is_type_to_ignore and inverse_conversion:
            return inverse_conversion_func(wrapped_output, shape_change)
        else:
            # todo: this is where the reverse mapping happens for the sklearn wrapper at the moment
            # sklearn wrapper has its own implementation for inverse conversion
            # this could also be done in the class, but thought it would make sense to have the decorator handle this
            # only issue with having it here is we bypass this if the type is already correct, in which case maybe it
            # should be done in the SKLearnWrapper
            # anomaly detection will be 2 columns ts, anomaly
            if isinstance(instance, base_mixins.SKLearnEstimatorWrapper) and wrapped_output is not instance:
                # convert to df with the underlying instance implementation from SKLearnEstimatorWrapper
                # df_out = instance._reverse_map_to_df(arg_val, wrapped_output)
                # wrap in a data model
                # based on the arg_val type, convert from data model to that type
                return wrapped_output
            else:
                return wrapped_output

    # Silence the warning coming out of wrapt for using deprecated APIs
    warnings.filterwarnings(
        "ignore",
        message="`formatargspec` is deprecated since Python 3.5. Use `signature` and the `Signature` object directly",
    )
    return decorator(wrapped)


def _argspec_factory(
    wrapped: Callable,
    extra_kwonly: Optional[List[Tuple[str, Any]]] = None,
) -> inspect.FullArgSpec:
    """This factory will create a new FullArgSpec for the wrapped function with
    the extra keyword-only args added.
    """
    argspec = inspect.getfullargspec(wrapped)
    kwonlyargs = list(argspec.kwonlyargs or [])
    kwonlydefaults = argspec.kwonlydefaults or {}
    for name, dflt in extra_kwonly:
        assert name not in kwonlydefaults, f"Adding kwarg [{name}] conflicts with existing kwarg!"
        kwonlyargs.append(name)
        kwonlydefaults[name] = dflt
    return inspect.FullArgSpec(
        args=argspec.args,
        varargs=argspec.varargs,
        varkw=argspec.varkw,
        defaults=argspec.defaults,
        kwonlyargs=kwonlyargs,
        kwonlydefaults=kwonlydefaults,
        annotations=argspec.annotations,
    )
