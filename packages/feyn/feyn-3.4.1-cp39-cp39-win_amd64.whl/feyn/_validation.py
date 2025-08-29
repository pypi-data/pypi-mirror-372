"""A collection of helper functions to validate functions in feyn"""

import pandas as pd
from feyn import Model

from typing import Dict, Optional, Iterable, Union
from ._typings import _validate_iterable_type_args, check_types


def _validate_bool_values(y_true):
    unique_values = set(y_true)
    allowed_values = {1, 0, True, False, 1.0, 0.0}
    disallowed = unique_values.difference(allowed_values)
    if len(disallowed) > 0:
        return False

    return True


def _validate_category_number(y_true):
    unique_values = set(y_true)
    if len(unique_values) != 2:
        return False

    return True


def _validate_prob_values(y_pred):
    if not all([value <= 1 and 0 <= value for value in y_pred]):
        return False

    return True


from feyn.tools._auto import infer_output_stype


@check_types()
def validate_data(
    data: pd.DataFrame,
    kind: str,
    output_name: str,
    stypes: Optional[Dict[str, str]] = {},
):
    """Validates a pandas dataframe for known data issues.


    Arguments:
        data {pd.DataFrame} -- The data to validate
        kind {str} -- The kind of output - classification or regression
        output_name {str} -- The name of the output

    Keyword Arguments:
        stypes {Optional[Dict[str, str]]} -- The stypes you want to assign to your inputs (default: {})

    Raises:
        ValueError: When output values do not match output type
        ValueError: When categorical stypes are not defined for categorical inputs
        ValueError: When nan values exist for numerical inputs
    """
    output_stype = infer_output_stype(kind, output_name, stypes)

    if output_stype == "f":
        _validate_regression_output_non_numerical_values(data, output_name)

    if output_stype == "b":
        if not _validate_bool_values(data[output_name]):
            raise ValueError(
                f"{output_name} must be an iterable of booleans or 0s and 1s"
            )
        if not _validate_category_number(data[output_name]):
            raise ValueError(f"{output_name} must contain exactly two categories")

    _validate_categorical_stypes(data, stypes)
    _check_num_cols_for_nan_values(data, stypes)


def _validate_categorical_stypes(data: pd.DataFrame, stypes: Dict[str, str]):
    def is_stype_categorical(c):
        try:
            return stypes[c] in ["c", "cat", "categorical"]
        except KeyError:
            return False

    object_columns = [c for c in data.columns if data.dtypes[c] == "object"]
    problematic_columns = [c for c in object_columns if not is_stype_categorical(c)]

    if len(problematic_columns) > 0:
        raise ValueError(
            f"The column(s) {', '.join(problematic_columns)} are of type object, but have not been declared as categorical in stypes"
        )


def _validate_regression_output_non_numerical_values(
    data: pd.DataFrame, output_name: str
):
    is_numerical = _validate_iterable_type_args(
        Iterable[float], data[output_name], verbose=False
    )

    if not is_numerical:
        raise ValueError(f"The output column '{output_name}' has non-numerical values")


def _check_num_cols_for_nan_values(data, stypes):
    def is_stype_numerical(c):
        try:
            return stypes[c] in ["f", "float", "numerical"]
        except KeyError:
            return True

    num_columns = [c for c in data.columns if is_stype_numerical(c)]
    columns_with_nan_values = list(
        data[num_columns].columns[data[num_columns].isna().sum() > 0]
    )

    if columns_with_nan_values:
        raise ValueError(
            f"The following columns contain Nan values: {columns_with_nan_values}"
        )


def _validate_data_columns_for_model(
    model: Model, data: Union[pd.DataFrame, pd.Series], output=True
):
    """Validates that the dataframe contains the columns present in the model

    Arguments:
        model {Model} -- The model to validate for
        data {Union[pd.DataFrame, pd.Series]} -- The data to validate on

    Keyword Arguments:
        output {bool} -- Whether to also validate the output of the model
    """
    columns = []
    if type(data).__name__ == "DataFrame":
        columns = data.columns
    elif type(data).__name__ == "Series":
        columns = data.index.tolist()

    if output and model.output not in columns:
        raise ValueError(f"Output '{model.output}' not found in data.")

    for input in model.inputs:
        if input not in columns:
            raise ValueError(f"Input '{input}' not found in data.")

    return True
