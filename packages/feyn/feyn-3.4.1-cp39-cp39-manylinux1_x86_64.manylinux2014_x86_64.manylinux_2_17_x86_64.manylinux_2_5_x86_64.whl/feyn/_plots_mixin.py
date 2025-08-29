from typing import Iterable, Optional, Dict, Union, List, Any
import feyn
from pandas import DataFrame, Series
from matplotlib.axes import Axes
from feyn._typings import check_types


class PlotsMixin:
    @check_types()
    def plot(
        self,
        data: DataFrame,
        compare_data: Optional[Union[DataFrame, List[DataFrame]]] = None,
        labels: Optional[Iterable[str]] = None,
        filename: Optional[str] = None,
    ) -> "feyn.tools._display.HTML":
        """
        Plot the model's summary metrics and some useful plots for its kind.

        This is a shorthand for calling feyn.plots.plot_model_summary.

        Arguments:
            data {DataFrame} -- Data set including both input and expected values.

        Keyword Arguments:
            compare_data {Optional[Union[DataFrame, List[DataFrame]]]} -- Additional data set(s) including both input and expected values. (default: {None})
            labels {Optional[Iterable[str]]} - A list of labels to use instead of the default labels. Must be size 2 if using comparison dataset, else 1.
            filename {Optional[str]} - The filename to use for saving the plot as html.

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: If columns needed for the model are not present in the data.

        Returns:
            HTML -- HTML report of the model summary.
        """
        return feyn.plots._model_summary.plot_model_summary(
            self, data, compare_data=compare_data, labels=labels, filename=filename
        )

    @check_types()
    def plot_flow(
        self,
        data: DataFrame,
        sample: Union[DataFrame, Series],
        filename: Optional[str] = None,
    ) -> "feyn.tools._display.SVG":
        """Plots the flow of activations through the model, for the provided sample. Uses the provided data as background information for visualization.
        Arguments:
            data {DataFrame} -- Data set including both input and expected values.
            sample {Union[DataFrame, Series]} -- A single data sample to plot the activations for.
            filename {Optional[str]} - The filename to use for saving the plot as svg.

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: If columns needed for the model are not present in the data.

        Returns:
            SVG -- SVG object containing the SVG of the model activation flow.
        """
        return feyn.plots.plot_activation_flow(self, data, sample, filename)

    @check_types()
    def plot_response_auto(
        self,
        data: DataFrame,
        ax: Optional[Axes] = None,
        figsize: Optional[tuple] = None,
        filename: Optional[str] = None,
    ) -> None:
        """
        Automatically visualize the response of a model to numerical inputs.

        This function attempts to automatically determine the most interesting inputs to display and fixes the rest to the median if numeric or mode if categorical.
        It also automatically decided whether to plot a 1d or 2d response plot.

        Uses the functions `plot_model_response_1d` or `plot_model_response_2d` internally depending on number of inputs in the model.

        For the 2D plot, the following applies:
        1. A colored background indicating the response of the model in a 2D space given the fixed values. A lighter color corresponds to a bigger output from the model.
        2. Scatter-plotted data on top of the background. In a classification scenario, green corresponds to positive class, and pink corresponds to the negative class. For regression, the color gradient shows the true distribution of the output value. Two sizes are used in the scatterplot, the larger dots correspond to the data that matches the values in fixed and the smaller ones have data different from the values in fixed.

        Arguments:
            model {feyn.Model} -- The feyn Model we want a partial plot of.
            data {DataFrame} -- The data that will be scattered in the model.

        Keyword Arguments:
            fixed {Optional[Dict[str, Any]]} -- Dictionary with values we fix in the model. The key is an input name in the model and the value is a number that the input is fixed to. (default: {None})
            ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the partial plot. (default: {None})
            resolution {int} -- The resolution at which we sample the 2D input space for the background. (default: {1000})
            figsize {Optional[tuple]} -- Size of created figure if no matplotlib axes is passed in ax. (default: {None})
            filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.
        """
        feyn.plots.plot_model_response_auto(self, data, ax, figsize, filename)

    @check_types()
    def plot_response_2d(
        self,
        data: DataFrame,
        fixed: Optional[Dict[str, Any]] = None,
        ax: Optional[Axes] = None,
        resolution: int = 1000,
        cmap: str = "feyn-diverging",
        figsize: Optional[tuple] = None,
        filename: Optional[str] = None,
    ) -> None:
        """
        Visualize the response of a model to numerical inputs. Works for both classification and regression problems. The plot comes in two parts:

        1. A colored background indicating the response of the model in a 2D space given the fixed values. A lighter color corresponds to a bigger output from the model.
        2. Scatter-plotted data on top of the background. In a classification scenario, green corresponds to positive class, and pink corresponds to the negative class. For regression, the color gradient shows the true distribution of the output value. Two sizes are used in the scatterplot, the larger dots correspond to the data that matches the values in fixed and the smaller ones have data different from the values in fixed.

        Arguments:
            model {feyn.Model} -- The feyn Model we want a partial plot of.
            data {DataFrame} -- The data that will be scattered in the model.

        Keyword Arguments:
            fixed {Optional[Dict[str, Any]]} -- Dictionary with values we fix in the model. The key is an input name in the model and the value is a number that the input is fixed to. (default: {None})
            ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the partial plot. (default: {None})
            resolution {int} -- The resolution at which we sample the 2D input space for the background. (default: {1000})
            figsize {Optional[tuple]} -- Size of created figure if no matplotlib axes is passed in ax. (default: {None})
            filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})

        Raises:
            TypeError: if function parameters don't match the correct type.
            ValueError: if the model input names minus the fixed value names are more than two, meaning that you need to fix more values to reduce the dimensionality and make a 2D plot possible.
            ValueError: if fixed contains an input not in the model inputs.
            ValueError: If columns needed for the model are not present in the data.
        """
        feyn.plots.plot_model_response_2d(
            self, data, fixed, ax, resolution, cmap, figsize, filename
        )

    @check_types()
    def plot_response_1d(
        self,
        data: DataFrame,
        by: Optional[str] = None,
        input_constraints: Optional[dict] = None,
        ax: Optional[Axes] = None,
        figsize: tuple = (8, 8),
        filename: Optional[str] = None,
    ) -> None:
        """Plot the response of a model to a single input given by `by`.
        The remaining model inputs are fixed by default as the middle
        quantile (median). Additional quantiles are added if the model has
        a maximum of 3 inputs. You can change this behavior by determining
        `input_contraints` yourself. Any number of model inputs can be added to it.

        Arguments:
            data {DataFrame} -- The dataset to plot on.
            by {str} -- Model input to plot model response by.

        Keyword Arguments:
            input_contraints {Optional[dict]} -- Input values to be fixed (default: {None}).
            ax {Optional[matplotlib.axes]} -- matplotlib axes object to draw to (default: {None}).
            figsize {tuple} -- size of created figure (default: {(8,8)})
            filename {str} -- Path to save plot. If axes is passed then only plot is saved. If no extension is given then .png is used (default: {None})

        Raises:
            TypeError: if function parameters don't match the correct type.
            ValueError: if by is not in the columns of data or inputs to the model.
            ValueError: if by is also in input_constraints.
            ValueError: if input_constraints contains an input that is not in data.
            ValueError: if model.output is not in data.
        """

        feyn.plots.plot_model_response_1d(
            self, data, by, input_constraints, ax, figsize, filename
        )

    @check_types()
    def plot_signal(
        self,
        data: DataFrame,
        corr_func: Optional[str] = None,
        filename: Optional[str] = None,
    ):
        """
        Plot a model displaying the signal path for the provided feyn.Model and DataFrame.

        Arguments:
            dataframe {DataFrame} -- A Pandas DataFrame for showing metrics.

        Keyword Arguments:
            corr_func {Optional[str]} -- A name for the correlation function to use as the node signal, either 'mutual_information', 'pearson' or 'spearman' are available. (default: {None} defaults to 'pearson')
            filename {Optional[str]} - The filename to use for saving the plot as svg.

        Raises:
            TypeError: if function parameters don't match the correct type.
            ValueError: if the name of the correlation function is not understood.
            ValueError: if invalid dataframes are passed.
            ValueError: If columns needed for the model are not present in the data.

        Returns:
            SVG -- SVG of the model signal.
        """
        return feyn.plots.plot_model_signal(
            self, data, corr_func=corr_func, filename=filename
        )
