import math
from enum import Enum

from typing import Iterable, Dict, Tuple, List, Union
from logging import getLogger, WARNING, INFO

from pandas import Series, to_datetime, DataFrame
from pandas.api.types import (
    CategoricalDtype,
    is_numeric_dtype,
    is_string_dtype,
    infer_dtype,
)

from feyn._compatibility import detect_notebook

_logger = getLogger(__name__)


class SType(Enum):
    BOOL = "b"
    CAT = "c"
    NUM = "f"
    SKIP = "skip"


class ColumnTypeMessage:
    level = WARNING

    def __init__(self, message):
        self.message = message


class HighCardinalityMessage(ColumnTypeMessage): ...


class RedundancyMessage(ColumnTypeMessage):
    level = INFO


class NotSupportedMessage(ColumnTypeMessage):
    level = INFO


class log_type_warnings:
    def __init__(self, warnings):
        self.warnings = warnings
        self._has_logged = False
        self._is_notebook = detect_notebook()

    def __call__(self):
        # Only log once if not in a notebook context
        if self._is_notebook or not self._has_logged:
            for w in self.warnings:
                _logger.log(w.level, w.message)
            self._has_logged = True


def remove_skipped_inputs(input_names: Iterable[str], stypes: Dict[str, str]):
    skipped_inputs = [input for input, stype in stypes.items() if stype == "skip"]

    if len(skipped_inputs) > 0:
        input_names = list(filter(lambda i: i not in skipped_inputs, input_names))
        stypes = {input: stype for input, stype in stypes.items() if stype != "skip"}

    return input_names, stypes


def infer_stypes(
    df: DataFrame, output_name: str, capture_warnings: bool = False
) -> Union[Dict[str, str], Tuple[Dict[str, str], List[ColumnTypeMessage]]]:
    """Infer the stypes of a dataframe based on the data itself.

    Arguments:
        df {DataFrame} -- The DataFrame to infer types for.
        output_name {str} -- The name of the output used for training.

    Keyword Arguments:
        capture_warnings {bool} -- Whether to log warnings directly (False) or return them as a list (True) (default: {False})

    Returns:
        Union[Dict[str, str], Tuple[Dict[str, str], List[ColumnTypeMessage]]] -- The dictionary of stypes. Optionaly a list of warning messages if capture_warnings = True.
    """
    stats = [SeriesStatistics(df[s]) for s in df]
    stypes = {s.name: s.infer_stype(output_name).value for s in stats}

    warnings = []
    for s in stats:
        warnings.extend(s.warnings)

    if capture_warnings:
        return stypes, warnings

    for w in warnings:
        _logger.log(w.level, w.message)

    return stypes


class SeriesStatistics:
    def __init__(self, series: Series):
        self.name = series.name
        self.series = series
        self.dt = series.dtype

        # Threshold heuristics
        self.redundancy_length_threshold = 10
        self.cardinality_threshold = 0.5

        # Computed properties used for type inferral
        self.len = len(self.series)
        self.nanlen = self.series.isna().sum()
        self.non_nan_len = self.len - self.nanlen
        self.nunique = self.series.nunique(dropna=True)
        self.ord_threshold = int(math.log2(self.len))
        try:
            self.inferred_type = infer_dtype(series)
        except TypeError:
            self.inferred_type = None

        self.warnings = []

    def _is_binary(self) -> bool:
        """Returns true of the column is binary, regardless of the value types.
        It discounts NaN values when determining whether a column has only two distinct values.

        Returns:
            bool -- Whether the column is binary (only has two distinct values)
        """
        if self.nunique == 2:
            return True
        return False

    def _is_constant(self) -> bool:
        return self.nunique == 1 and self.len > self.redundancy_length_threshold

    def _is_likely_ordinal(self) -> bool:
        # Not sure how to differentiate this from the nominal values without counting the entries
        return self._is_likely_nominal()

    def _is_likely_nominal(self) -> bool:
        # Could consider a fixed threshold for numerical values, like 5.
        # Large datasets of course allow more variation before cardinality becomes an issue, but it doesn't increase the likelihood that it's nominal.
        return self.nunique <= min(5, self.ord_threshold)

    def _is_continuous(self) -> bool:
        """Returns true if a column contains numerical values that are continuous.

        Returns:
            bool -- Whether a column contains continuous values
        """
        # Note: Piggybacking on pandas' inferred dtype. Might come at a performance cost.
        return self.inferred_type in ["floating", "mixed-integer-float", "decimal"]

    def __check_continuous(self) -> bool:
        if self._is_numerical():
            # Super expensive, even with apply. But let's benchmark it
            decimals = self.series.apply(math.modf[0])
            return decimals.any(lambda x: x != 0)
        return False

    def _is_ID_like(self) -> bool:
        """Returns true if the column looks like an ID (all unique values).
        It discounts missing values in the count of uniqueness.

        Returns:
            bool -- Whether the column looks like an ID
        """
        return (
            self.non_nan_len == self.nunique
            and self.len > self.redundancy_length_threshold
        )

    def _is_high_cardinality(self) -> bool:
        """Returns true if the column has high cardinality.

        Returns:
            bool -- Whether a column is high cardinality
        """
        # Base category limit before considering it high cardinality even for large datasets
        if self.nunique > 50:
            return True

        if self.non_nan_len > 0:
            unique_ratio = self.nunique / self.non_nan_len

            if unique_ratio > self.cardinality_threshold:
                return True

        return False

    def _is_likely_datetime(self) -> bool:
        """Returns true only if it looks like a datetime

        Returns:
            bool -- whether the column is a date
        """
        if "time" in self.inferred_type:
            # Not sure this ever happens unless it's been loaded as a datetime
            return True

        if self.inferred_type == "string":
            try:
                # We don't want to treat just numbers as dates (like years)!
                self.series.astype("int64")
                return False
            except:
                try:
                    to_datetime(self.series, format="ISO8601")
                    return True
                except:
                    return False

        return False

    def _is_string_type(self) -> bool:
        """Returns true if the dtype of the column is a string (or an object containing strings)

        Returns:
            bool -- Whether the column is a string
        """
        # Fallback on checking the inferred type in case of missing type initialisation
        return is_string_dtype(self.dt) or self.inferred_type in ["string"]

    def _is_numerical(self) -> bool:
        """Returns true if the dtype of the column is numerical (integer or float of any kind)

        Returns:
            bool -- Whether the column is numerical
        """
        # Fallback on checking the inferred type in case of missing type initialisation
        return is_numeric_dtype(self.dt) or self.inferred_type in [
            "floating",
            "integer",
            "decimal",
            "mixed-integer-float",
        ]

    def _is_categorical(self) -> bool:
        """Returns true if the dtype of the column is categorical

        Returns:
            bool -- Whether the column is categorical
        """
        # Fallback on checking the inferred type in case of missing type initialisation
        return isinstance(self.dt, CategoricalDtype) or self.inferred_type in [
            "categorical"
        ]

    def _is_mixed_type(self) -> bool:
        """Returns true if a column has inconsistent or mixed types.
        Note: Not implemented yet and always returns False.

        Returns:
            bool -- Whether a column has mixed types
        """
        return self.inferred_type in ["mixed", "mixed-integer"]

    def _warn(self, warning):
        self.warnings.append(warning)

    def infer_stype(self, output_name: str) -> SType:
        """Assumes that data validation happens elsewhere, and just tries to guess what it is. So it ignores missing values, invalid boolean types, etc.
        Errors will happen downstream and notify the user to fix if the contents of a column are not usable for the stype (such as yes/no for binary)

        Arguments:
            output_name {str} -- The column name for the output

        Returns:
            SType -- An Enum for the stype.
        """
        self.warnings = []

        if self.name == output_name:
            # No other type inferring will be done for the output column. Any errors will happen downstream.
            if self._is_binary():
                return SType.BOOL
            return SType.NUM

        # Detect values to reject for training first (constant, mixed)
        if self._is_constant():
            # Could introduce an stype to skip the value during training or produce an error.
            self._warn(
                RedundancyMessage(
                    f"Column '{self.name}' is constant (contains only one value) and will be skipped."
                )
            )
            return SType.SKIP

        if self._is_mixed_type():
            # Could introduce an stype to skip the value during training or produce an error.
            self._warn(
                NotSupportedMessage(
                    f"Column '{self.name}' contains mixed types for values and will be skipped."
                )
            )
            return SType.SKIP

        if self._is_continuous():
            return SType.NUM

        if self._is_numerical():
            if self._is_binary():
                # NUM appears to perform better during training for numerical binary columns, eventhough it shouldn't. More testing needed.
                # In addition, it has fewer parameters, so results in a better pick order using bic.
                return SType.NUM
            elif self._is_likely_ordinal() or self._is_likely_nominal():
                if self._is_high_cardinality():
                    # Note: we'll never actually be in a high-cardinality situation while we have the ordinal threshold set low for numerical columns
                    self._warn(
                        HighCardinalityMessage(
                            f"Column '{self.name}' has high cardinality and might produce models less likely to generalise if used as a categorical input."
                        )
                    )
                    return SType.NUM
                return SType.CAT
            else:
                if self._is_ID_like():
                    # Could warn here, or introduce an stype to skip the value during training.
                    self._warn(
                        RedundancyMessage(
                            f"Column '{self.name}' looks like an ID column and has been skipped."
                        )
                    )

                    return SType.SKIP
                return SType.NUM

        if self._is_likely_datetime():
            self._warn(
                NotSupportedMessage(
                    f"Column '{self.name}' looks like a timestamp. Timestamps are currently not supported by Feyn and will be skipped."
                )
            )
            return SType.SKIP

        # Check strings last, since arrays with integers and nan's get dtype object and return True for strings
        if self._is_string_type() or self._is_categorical():
            if self._is_high_cardinality():
                self._warn(
                    HighCardinalityMessage(
                        f"Column '{self.name}' has high cardinality and might produce models less likely to generalise when used as a categorical input."
                    )
                )
                # Note: Could reduce dimensionality by automatically grouping low-frequency features in the future.
                return SType.CAT
            return SType.CAT

        return SType.NUM
