import numpy as np

from feyn.insights import KernelShap
from feyn.plots._themes import Theme
from feyn.plots._table_writer import TableWriter

from feyn import Model

import matplotlib.pyplot as plt
from matplotlib import colors, colorbar

from typing import Optional, Iterable


class TableStyling:
    def __init__(
        self, style: Optional[str] = "bar", only_color_features: Optional[bool] = True
    ):
        self.style = style
        self.only_color_features = only_color_features


class FeatureImportanceTable:
    def __init__(
        self,
        model: Model,
        dataframe: Iterable,
        bg_data: Optional[Iterable] = None,
        max_ref_samples: Optional[int] = 100,
        max_rows: Optional[int] = 10,
        style: Optional[str] = "bar",
        only_color_features: Optional[bool] = True,
    ):
        """Computes and renders a table with feature importances for the model

        Arguments:
            model -- a feyn Model
            dataframe -- a Dataframe you want to compute importances for (expensive - consider filtering what you need to know about beforehand)

        Keyword Arguments:
            bg_data -- a Dataframe used to compute background on. Should usually be your training set. (default: {None})
            max_ref_samples -- How many max samples to take from bg_data for computing color-range limits (expensive) (default: {100})
            max_rows -- How many rows of the dataframe to display - note: this doesn't impact your IPython config (default: {10})
            style -- Whether to render it as a bar-chart dataframe ('bar') or heatmap-style ('fill') (default: {'bar'})
            only_color_features -- Only fill color for features that are in the model (ignore 0's) (default: {True})

        Raises:
            Exception: Raises on bad parameters
        """
        self.data = dataframe
        self.max_rows = (
            len(self.data)
            if max_rows is None or max_rows > len(self.data)
            else max_rows
        )

        if style not in ["bar", "fill"]:
            raise Exception(
                f"Style {style} not recognized. Must be either 'bar' or 'fill'"
            )

        self.model = model
        self.features = model.features
        self.styling = TableStyling(style, only_color_features)

        # Do the actual calculations
        self.importance_values, self.bg_importance = self._get_importances(
            self.model, self.data, bg_data, max_ref_samples
        )

        self.max_value = self._calculate_max_value(
            self.importance_values, self.bg_importance, bg_data
        )

    def write_table(self):
        table = ""
        if type(self.data).__name__ == "DataFrame":
            table = TableWriter(
                self.data,
                max_rows=self.max_rows,
                cell_styles=self._calculate_col_gradient_bar_pd,
            )
        else:
            styles = self._calculate_col_gradient_bar()
            table = TableWriter(self.data, max_rows=self.max_rows, cell_styles=styles)

        if self.styling.style == "fill":
            _plot_colorbar(self.max_value)
        return table._repr_html_()

    def _repr_html_(self):
        return self.write_table()

    @staticmethod
    def _get_importances(model, data, bg_data, max_ref_samples):
        has_bg_data = bg_data is not None

        # Just default if nothing supplied
        bg_data = bg_data if has_bg_data else data

        shap_explainer = KernelShap(model, bg_data)

        importance_values = shap_explainer.SHAP(data)

        if has_bg_data:
            max_ref_samples = (
                max_ref_samples if len(bg_data) > max_ref_samples else len(bg_data)
            )
            sanitized = _sanitize_dataframe(bg_data)
            bg_importance = shap_explainer.SHAP(
                _short_sample(sanitized, max_ref_samples)
            )
        else:
            bg_importance = importance_values

        return importance_values, bg_importance

    @staticmethod
    def _calculate_max_value(importance_values, bg_importance, bg_data):
        # Only use the bg_importances to compute absmax if it's different from the input dataframe
        if bg_data is not None:
            all_importances = np.vstack([bg_importance, importance_values])
            # Define the absmax from what it's seen, and the newly predicted values
            absmax = _get_absmax(all_importances)

            # Add a tiny visual buffer if we have uncertain absmax (we've only used a subset of the bg_data)
            if len(bg_importance) < len(bg_data):
                std_dev = all_importances.std()
                absmax = absmax + std_dev
        else:
            absmax = _get_absmax(importance_values)

        return absmax

    def _calculate_col_gradient_bar_pd(self, series):
        """Parameters:
            series: The series to get the styles for
        Returns: styles for a pandas dataframe as a bar chart"""
        # Get the index of the series in our supplied dataframe
        # This is pandas specific, but we also know we're in panda land.
        col_idx = list(self.data.columns).index(series.name)
        importance_series = self.importance_values[: self.max_rows, col_idx]
        if self.styling.only_color_features and series.name not in self.features:
            return ["" for i in range(len(importance_series))]

        return _get_col_styles(importance_series, self.max_value, self.styling.style)

    def _calculate_col_gradient_bar(self):
        """Returns: styles as an np.array for a table as a bar chart"""

        keys = list(self.data.keys())
        styles = np.empty(shape=(len(self.data[keys[0]]), len(keys)), dtype=object)
        for idx, col in enumerate(keys):
            if self.styling.only_color_features and col not in self.features:
                continue

            importance_series = self.importance_values[:, idx]
            styles[:, idx] = _get_col_styles(
                importance_series, self.max_value, self.styling.style
            )

        return styles[: self.max_rows, :]


def _get_absmax(x):
    return max(x.max(), np.abs(x.min()))


def _get_col_styles(importance_series, max_value, style):
    if style == "bar":
        percentages = _get_percentages(importance_series, max_value)
        return [_get_gradient_string(pct) for pct in percentages]
    elif style == "fill":
        normalizer = colors.Normalize(-max_value, max_value)
        normed_df = normalizer(importance_series)

        abzu_cmap = plt.cm.get_cmap("feyn-signal")
        colorlist = [colors.rgb2hex(x) for x in abzu_cmap(normed_df)]
        return ["background-color: %s" % color for color in colorlist]

    # This shouldn't happen
    return ["" for i in range(len(importance_series))]


def _get_percentages(importance_series, max_value):
    return [_get_percent_color(v, max_value) for v in importance_series]


def _get_percent_color(value, absmax):
    """Related to a bar chart, returns the percent coloring in either
    direction assuming 50% is the middle
    """
    return 50 + value / absmax * 50


def _get_gradient_string(value):
    highlight = Theme.color("highlight")
    accent = Theme.color("accent")
    if value > 50:
        # Try to make sure you can always see the sliver of contribution, even if it's small.
        value = max(53, value)
        return f"background: linear-gradient(90deg, transparent 50.0%, {highlight} 50.0%, {highlight} {value}%, transparent {value}%)"
    elif value < 50:
        value = min(47, value)
        return f"background: linear-gradient(90deg, transparent {value}%, {accent} {value}%, {accent} 50.0%, transparent 50.0%)"
    else:
        return "background-color: default"


def _short_sample(data, no_samples):
    """Sample function that does not oversample nor sample with replacement.

    Arguments:
        data {[np_dict]} -- a dictionary of numpy arrays
        no_samples {[type]} -- number of samples to take up till len(data)
    """
    length = len(data[list(data.keys())[0]])
    permutation = np.random.permutation(length)

    return {col: data[col][permutation][:no_samples] for col in data}


def _sanitize_dataframe(maybe_df):
    if type(maybe_df).__name__ == "DataFrame":
        data = {col: maybe_df[col].values for col in maybe_df.columns}
    else:
        data = maybe_df

    return data


def _plot_colorbar(absmax):
    fig, ax = plt.subplots(figsize=(5, 0.5))
    fig.subplots_adjust(bottom=0.5)

    cb = colorbar.ColorbarBase(
        ax,
        cmap=plt.cm.get_cmap("feyn-signal"),
        norm=colors.Normalize(vmin=-absmax, vmax=absmax),
        orientation="horizontal",
    )
    cb.set_label("Contribution (SHAP)")
    return fig
