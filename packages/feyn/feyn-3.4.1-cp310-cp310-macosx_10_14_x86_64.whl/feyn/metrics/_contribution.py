import math
from feyn.metrics._normalization import normalized_mi
from feyn import Model
from pandas import DataFrame
from typing import Callable, List


def _get_parent_indices(model):
    parent = [None for i in range(len(model))]
    for i, el in enumerate(model._elements):
        for child in el.children:
            parent[child] = i
    return parent


def _get_input_indices(model):
    inputs = []
    for i, el in enumerate(model._elements):
        if el.name and "out" not in el.fname:
            inputs.append(i)
    return inputs


def _recurse_significance(model, node, parents, contributions):
    current_node = model[node]
    if "out" in current_node.fname:
        # We don't want to include the contributions of the output node (performance of the model)
        return 1

    p = parents[node]

    # Arity 1 nodes should have unit mi with the previous node since it's a transformation.
    return contributions[node] * _recurse_significance(model, p, parents, contributions)


def get_ranked_contributors(
    model: Model, df: DataFrame, corr_func: Callable = normalized_mi
) -> List[str]:
    """Get a ranked list of the inputs in order of influence on the model output

    Arguments:
        model {Model} -- The model to rank inputs for
        df {DataFrame} -- The dataframe the model was trained on

    Keyword Arguments:
        corr_func {Callable} -- The function to use for calculating the relative activation correlations of the model (default: {normalized_mi})

    Returns:
        List[str] -- The ranked input names
    """
    inputs = _get_input_indices(model)
    parents = _get_parent_indices(model)

    contributions = _get_relative_node_to_parent_correlation(model, df, corr_func)

    significance = {}
    for i in inputs:
        significance[model[i].name] = math.fabs(
            _recurse_significance(model, i, parents, contributions)
        )

    return sorted(significance, key=significance.get, reverse=True)


def _get_relative_node_to_parent_correlation(model, data, corr_func):
    """
    Calculate the correlation between each node and its parent node of the model, using the provided corr_func.
    """
    if data is None:
        return None

    # Magic support for dataframes
    if type(data).__name__ == "DataFrame":
        data = {col: data[col].values for col in data.columns}

    data_output = data[model.output]
    activations = model._get_activations(data)

    ret = [corr_func(activations[0], data_output)]
    parents = _get_parent_indices(model)
    for n in range(1, len(model)):
        # Get the correlation between a node and its parent
        ret.append(corr_func(activations[n], activations[parents[n]]))

    return ret
