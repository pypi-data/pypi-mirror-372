from typing import Iterable, Union, Dict
import feyn
from pandas import DataFrame


class InteractiveMixin:
    def interactive_flow(self, data: DataFrame) -> "SVG":
        """
        For IPython kernels only.

        Requires installing ipywidgets, and enabling the extension in jupyter notebook or jupyter lab.
        Jupyter notebook: jupyter nbextension enable --py widgetsnbextension
        Jupyter lab: jupyter labextension install @jupyter-widgets/jupyterlab-manager

        Plots an interactive version of the flow of activations through the model, for the provided sample. Uses the provided data as background information for visualization.
        """
        feyn.plots.interactive.interactive_activation_flow(self, data)

    def interactive_response_1d(self, data: DataFrame, input_constraints: Dict[str, Union[Iterable, float, str]] = None):
        """
        For IPython kernels only.
        Requires installing ipywidgets, and enabling the extension in jupyter notebook or jupyter lab.
        Jupyter notebook: jupyter nbextension enable --py widgetsnbextension
        Jupyter lab: jupyter labextension install @jupyter-widgets/jupyterlab-manager

        Plot an interactive version of the feyn.plots.plot_model_response_1d (model.plot_response_1d),
        that allows you to change the response variable `by`.

        Arguments:
            model {feyn.Model} -- The model to calculate the response for
            data {DataFrame} -- The data to be analyzed

        Keyword Arguments:
            input_constraints {dict} -- The constraints on the remaining model inputs (default: {None})
        """
        return feyn.plots.interactive.interactive_model_response_1d(self, data, input_constraints)
