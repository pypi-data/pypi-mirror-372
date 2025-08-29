import collections.abc
from typing import Iterable
import inspect
from typing import TypeVar, Any
from sys import version_info
from functools import wraps


# Python 3.8 has improvements like the get_args function and get_origin function. We use the python 3.7 supported ones:
# Python 3.7 uses .__args__ instead of get_args
# and __origin__ instead of get_origin. (but _SpecialForm (i.e. clean Union) doesn't have __origin__)
import feyn
import numpy as np

from typing import _SpecialForm


def check_types(exceptions: Iterable = [], verbose=False):
    def inner(func):
        # Relying on order of args is fragile when using untyped variables, so use inspect here.
        spec = inspect.getfullargspec(func)
        type_hints = spec.annotations

        @wraps(func)
        def wrapper(*args, **kwargs):
            if feyn._disable_type_checks:
                return func(*args, **kwargs)

            params = dict(zip(spec.args, args))
            params.update(kwargs)

            for param_name, param_value in params.items():
                if param_name in exceptions:
                    if verbose:
                        print(f"{param_name} in exceptions ({exceptions}), skipping.")
                        print("---")
                    continue
                if param_name not in type_hints:
                    if verbose:
                        print(f"{param_name} not in type hints, skipping.")
                        print("---")
                    continue
                expected_type = type_hints[param_name]

                verbose and print(
                    f"Validating typedef({param_name}: {expected_type}) - passed({param_value}: {type(param_value)})"
                )

                if not _validate_type(expected_type, param_value, verbose):
                    _raise(param_name, expected_type)
                if verbose:
                    print("---")

            return func(*args, **kwargs)

        return wrapper

    return inner


def _validate_type(expected_type, value, verbose=False) -> bool:
    expected_base_type = getattr(expected_type, "__origin__", None)
    verbose and print(f"(Validating against expected base type: {expected_base_type})")

    validated = False

    if expected_type == Any:
        validated = True
    elif expected_base_type is not None:
        # Unions go here (also catches Optional, since it gets expanded to Union[..., NoneType])
        if isinstance(expected_base_type, _SpecialForm):
            verbose and print(f"{expected_base_type} is special form")
            validated = _validate_union_type(expected_type, value, verbose)

        elif expected_base_type == list:
            verbose and print("Checking type of List")
            # Ensure it's a list and not just an iterable (like a string)
            if isinstance(value, list):
                validated = _validate_iterable_type_args(expected_type, value, verbose)

        elif expected_base_type == collections.abc.Iterable:
            # We don't want to accept strs and feyn models as iterables
            if _value_is_iterable_like(value):
                verbose and print("Checking type of Iterable")
                validated = _validate_iterable_type_args(expected_type, value, verbose)

        elif expected_base_type == dict:
            if type(value) == expected_base_type:
                verbose and print("Checking type of Dict")
                validated = _validate_dictionary(expected_type, value, verbose)

        # This will handle all other types with origins that has no special requirements
        else:
            verbose and print("Falling back on basic type check")
            validated = isinstance(value, expected_base_type)
    else:
        verbose and print("Falling back on basic type check")
        validated = isinstance(value, expected_type)

    verbose and print(f"Validation of {expected_type}: {validated}")
    return validated


def _validate_dictionary(expected_type, dictionary, verbose):
    type_args = getattr(expected_type, "__args__", None)
    verbose and print(f"type args: {type_args}")

    # Each type (key, value) in the dict should be explicitly mapped to one and only one type
    validated = True

    # Empty dicts should validate, so only check if there is a value
    if dictionary and type_args is not None:
        # Check first for the keys, then for the values
        for type_arg, dict_values in zip(
            type_args, [dictionary.keys(), dictionary.values()]
        ):
            if type_arg == Any:
                continue

            # This checks if any of the parameters are special (like Unions)
            if _is_special_type_arg(type_arg):
                verbose and print(f"{type_arg} is special form type arg.")
                # This only validates one level deep, so won't support Dict[..., Union[_SpecialForm[..., ...], ...]] stuff. Can expand if needed.
                validated &= _validate_iterable_type_args(
                    type_arg, dict_values, verbose
                )
            elif _is_list_type_arg(type_arg):
                verbose and print(f"{type_arg} is a list type arg.")

                for maybe_list in dict_values:
                    if not isinstance(maybe_list, list):
                        verbose and print(f"{maybe_list} is not a list.")
                        validated = False
                    else:
                        # Each element in the list needs to be validated as well
                        validated &= _validate_iterable_type_args(
                            type_arg, maybe_list, verbose
                        )

            elif _is_iterable_type_arg(type_arg):
                verbose and print(f"{type_arg} is an iterable type arg")
                for maybe_iterable in dict_values:
                    if not _value_is_iterable_like(maybe_iterable):
                        verbose and print(f"{maybe_iterable} is not an iterable.")
                        validated = False
                    else:
                        # Each element in the list needs to be validated as well
                        validated &= _validate_iterable_type_args(
                            type_arg, maybe_iterable, verbose
                        )
            else:
                verbose and print(f"Using default type checking for {type_arg}.")
                validated &= set(map(type, dict_values)) == set([type_arg])

    return validated


def _validate_union_type(expected_type, value, verbose):
    type_args = getattr(expected_type, "__args__", None)
    if type_args is None:
        return True

    validated = False
    for t in type_args:
        verbose and print(f"Recursively evaluating {t}...")
        validated |= _validate_type(t, value, verbose)
    return validated


def _validate_iterable_type_args(expected_type, value, verbose):
    verbose and print(f"Validating type args for {expected_type}")

    # Python 3.9 no longer has __args__ for naked types, so return None
    type_args = getattr(expected_type, "__args__", None)

    # Special handling for naked types (i.e. List instead of List[str])
    if type_args is None or isinstance(type_args[0], type(TypeVar("T"))):
        return True

    expected_types = set(type_args)
    for t in list(expected_types):
        # Unwrap union types
        if _is_special_type_arg(t):
            verbose and print(f"{t} is special form")
            args = getattr(t, "__args__", None)
            for a in args:
                expected_types.add(a)

    # Add numpy equivalents to the supported options
    for t in list(expected_types):
        for eq in _equivalent_types.get(t, []):
            expected_types.add(eq)

    value_types = set(map(type, value))
    return value_types.issubset(expected_types)


_equivalent_types = {
    int: [np.int_, np.int8, np.int16, np.int32],
    float: [
        int,
        np.int_,
        np.int8,
        np.int16,
        np.int32,
        np.float64,
        np.float16,
        np.float32,
        np.longdouble,
    ],
    bool: [np.bool_],
    str: [np.str_],
}


def _is_special_type_arg(type_arg):
    return hasattr(type_arg, "__origin__") and isinstance(
        type_arg.__origin__, _SpecialForm
    )


def _validate_nested_iterable_type_args(type_arg, iterables, verbose):
    validated = True
    for each_iterable in iterables:
        # Each element in the list needs to be validated as well
        validated &= _validate_iterable_type_args(type_arg, each_iterable, verbose)
    return validated


def _is_list_type_arg(type_arg):
    return hasattr(type_arg, "__origin__") and (type_arg.__origin__ == list)


def _is_iterable_type_arg(type_arg):
    return hasattr(type_arg, "__origin__") and (
        type_arg.__origin__ == collections.abc.Iterable
    )


def _value_is_iterable_like(value):
    return (
        hasattr(value, "__iter__")
        and not type(value) == str
        and not type(value) == feyn.Model
    )


def _raise(param_name, expected_type):
    raise TypeError(
        f"{param_name} should be of type {expected_type}.".replace("typing.", "")
    )
