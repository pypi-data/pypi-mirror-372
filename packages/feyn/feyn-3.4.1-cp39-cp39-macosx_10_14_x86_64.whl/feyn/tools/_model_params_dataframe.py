import pandas as pd
import feyn

from feyn._typings import check_types


@check_types()
def get_model_parameters(model: feyn.Model, name: str) -> pd.DataFrame:
    """Given a model and the name of one of its input or output nodes,
    get a pandas.DataFrame with the associated parameters. If the node
    is categorical, the function returns the weight associated with each categorical
    value. If the node is numerical, the function returns the scale, weight and
    bias.

    Arguments:
        model {feyn.Model} -- feyn Model of interest.
        name {str} -- Name of the input or output of interest.

    Returns:
        pd.DataFrame -- DataFrame with the parameters.
    """
    if name not in model.inputs+[model.output]:
        raise ValueError(
            f"{name} not in model inputs or output!"
        )

    suffixes = ()
    params_df = None
    for i, elem in enumerate(model):
        if elem.name != name:
            continue

        suffixes += (f'_{i}', )
        if params_df is None:
            params_df = _params_dataframe(elem)
        else:
            params_df = pd.merge(
                params_df, _params_dataframe(elem), left_index=True, right_index=True, suffixes=suffixes
            )

    return params_df


def _params_dataframe(elem):
    params_df = pd.DataFrame()

    if elem.fname == "in-cat:0":
        params_df = pd.DataFrame(elem.params['categories'], columns=['category', elem.name]
        ).set_index('category'
        ).sort_values(by=elem.name, ascending=False)
    elif elem.fname == "in-linear:0" or 'out-' in elem.fname:
        params_df = pd.DataFrame(
            elem.params, index=[elem.name]
        ).T

    return params_df
