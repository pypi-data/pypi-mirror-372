"""Functions to compute metrics and scores"""

import numpy as np
import pandas as pd
import logging
from typing import Iterable, Dict, List, Tuple

import feyn.losses
from ._mutual import calculate_mi
from ._linear import calculate_pc
from ._spearman import calculate_spear

from feyn._validation import _validate_data_columns_for_model

_logger = logging.getLogger(__name__)


def accuracy_score(true: Iterable[bool], pred: Iterable[float]) -> float:
    """
    Compute the accuracy score of predictions

    The accuracy score is useful to evaluate classification models. It is the fraction of the predictions that are correct. Formally it is defined as:

    (number of correct predictions) / (total number of predictions)

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values (will be rounded)

    Returns:
        accuracy score for the predictions
    """
    correct = np.equal(true, np.round(pred))
    return np.mean(correct)


def accuracy_threshold(
    true: Iterable[bool], pred: Iterable[float]
) -> Tuple[float, float]:
    """
    Compute the accuracy score of predictions with optimal threshold

    The accuracy score is useful to evaluate classification models. It is the fraction of the predictions that are correct. Accuracy is normally calculated under the assumption that the threshold that separates true from false is 0.5. Hovever, this is not the case when a model was trained with another population composition than on the one which is used.

    This function first computes the threshold limining true from false classes that optimises the accuracy. It then returns this threshold along with the accuracy that is obtained using it.

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values

    Returns a tuple with:
        threshold that maximizes accuracy
        accuracy score obtained with this threshold
    """
    fpr, tpr, _thresholds = roc_curve(true, pred)

    # Also compute accuracy and the threshold that maximises it
    num_pos_class = true.sum()
    num_neg_class = len(true) - num_pos_class

    tp = tpr * num_pos_class
    tn = (1 - fpr) * num_neg_class
    acc = (tp + tn) / (num_pos_class + num_neg_class)

    best_threshold = _thresholds[np.argmax(acc)]
    return best_threshold, np.amax(acc)


def roc_curve(
    true: Iterable[bool], pred: Iterable[float]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate the Receiver Operator Characteristics.

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values

    Returns:
        fpr: np.array[float] - Increasing false positive rates
        tpr: np.array[float] - Increasing true positive rates
        thresholds: np.array[float] - Thresholds used
    """
    from sklearn.metrics import roc_curve

    return roc_curve(true, pred)


def roc_auc_score(true: Iterable[bool], pred: Iterable[float]) -> float:
    """
    Calculate the Area Under Curve (AUC) of the ROC curve.

    A ROC curve depicts the ability of a binary classifier with varying threshold.

    The area under the curve (AUC) is the probability that said classifier will
    attach a higher score to a random positive instance in comparison to a random
    negative instance.

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values

    Returns:
        AUC score for the predictions
    """
    fpr, tpr, _ = roc_curve(true, pred)

    trapz = getattr(np, "trapezoid", np.trapz) # Fallback to pre-numpy 2.0.0 trapz if the function doens't exist
    if callable(trapz):
        auc_score = trapz(tpr, fpr)  # Calculating the integral under the ROC curve
    else:
        raise AttributeError("Your current version of numpy doesn't support the trapezoid function. Try updating to a newer version")

    return auc_score


def r2_score(true: Iterable[float], pred: Iterable[float]) -> float:
    """
    Compute the r2 score

    The r2 score for a regression model is defined as
    1 - rss/tss

    Where rss is the residual sum of squares for the predictions, and tss is the total sum of squares.
    Intutively, the tss is the resuduals of a so-called "worst" model that always predicts the mean. Therefore, the r2 score expresses how much better the predictions are than such a model.

    A result of 0 means that the model is no better than a model that always predicts the mean value
    A result of 1 means that the model perfectly predicts the true value

    It is possible to get r2 scores below 0 if the predictions are even worse than the mean model.

    Arguments:
        true {Iterable[float]} -- Expected values
        pred {Iterable[float]} -- Predicted values

    Returns:
        r2 score for the predictions
    """

    mean = true.mean()

    rss = np.sum(
        (true - pred) ** 2
    )  # Residual sum of squares (this is the squared loss of this predition)
    tss = np.sum(
        (true - mean) ** 2
    )  # Total sum of squares (this is the squared loss of a model that predicts the mean)

    # r2 score expresses how much better the predictions are compared to a model that predicts the mean
    return 1 - rss / tss


def mae(true: Iterable[float], pred: Iterable[float]):
    """
    Compute the mean absolute error

    Arguments:
        true {Iterable[float]} -- Expected values
        pred {Iterable[float]} -- Predicted values

    Returns:
        float -- MAE for the predictions
    """
    return feyn.losses.absolute_error(true, pred).mean()


def mse(true: Iterable[float], pred: Iterable[float]):
    """
    Compute the mean squared error

    Arguments:
        true {Iterable[float]} -- Expected values
        pred {Iterable[float]} -- Predicted values

    Returns:
        float -- MSE for the predictions
    """
    return feyn.losses.squared_error(true, pred).mean()


def rmse(true: Iterable[float], pred: Iterable[float]):
    """
    Compute the root mean squared error

    Arguments:
        true {Iterable[float]} -- Expected values
        pred {Iterable[float]} -- Predicted values

    Returns:
        float -- RMSE for the predictions
    """
    return np.sqrt(feyn.losses.squared_error(true, pred).mean())


def get_summary_metrics_classification(
    true: Iterable[bool], pred: Iterable[float]
) -> Dict[str, float]:
    """
    Get summary metrics for classification

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values

    Returns:
        dict[str, float] -- A dictionary of summary metrics
    """
    precision, recall = precision_recall(true, np.round(pred))  # Round just in case
    return {
        "Accuracy": accuracy_score(true, pred),
        "AUC": roc_auc_score(true, pred),
        "Precision": precision,
        "Recall": recall,
    }


def get_summary_metrics_regression(
    true: Iterable[float], pred: Iterable[float]
) -> Dict[str, float]:
    """
    Get summary metrics for regression

    Arguments:
        true {Iterable[float]} -- Expected values
        pred {Iterable[float]} -- Predicted values

    Returns:
        dict[str, float] -- A dictionary of summary metrics
    """
    return {
        "R2": r2_score(true, pred),
        "RMSE": rmse(true, pred),
        "MAE": np.mean(feyn.losses.absolute_error(true, pred)),
    }


def confusion_matrix(true: Iterable[bool], pred: Iterable[float]) -> np.ndarray:
    """
    Compute a Confusion Matrix.

    Arguments:
        true {Iterable[bool]} -- Expected values (Truth - containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values

    Returns:
        [cm] -- a numpy array with the confusion matrix
    """

    classes = np.union1d(pred, true)

    sz = len(classes)
    matrix = np.zeros((sz, sz), dtype=int)
    for tc in range(sz):
        pred_tc = pred[true == classes[tc]]
        for pc in range(sz):
            matrix[(tc, pc)] = len(pred_tc[pred_tc == classes[pc]])
    return matrix


def precision_recall(
    true: Iterable[bool], pred: Iterable[float]
) -> Tuple[float, float]:
    """
    Get precision and recall

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]) -- Predicted values

    Returns:
        Tuple[Float, Float]: precision, recall
    """
    cm = confusion_matrix(true, pred)

    tp = cm[1][1]
    fn = cm[1][0]
    fp = cm[0][1]

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    return precision, recall


def f1_score(true: Iterable[bool], pred: Iterable[float]):
    """Get F1 score

    Args:
        true (Iterable[bool]): Expected values (containing values of 0 or 1)
        pred (Iterable[float]): Predicted values

    Returns:
        f1 score
    """
    precision, recall = precision_recall(true, pred)
    f1_score = (2 * precision * recall) / (precision + recall)
    return f1_score


def false_positive_rate(true: Iterable[bool], pred: Iterable[float]) -> float:
    """Get the false-positive rate for a set of predictions on a dataset.

    Arguments:
        true {Iterable[bool]} -- Expected values (containing values of 0 or 1)
        pred {Iterable[float]} -- Predicted values

    Returns:
        float -- The false-positive rate
    """
    cm = confusion_matrix(true, pred)

    fp = cm[0][1]
    tn = cm[0][0]

    return fp / (fp + tn)


def segmented_loss(
    model: feyn.Model,
    data: pd.DataFrame,
    by: str = None,
    loss_function: str = "squared_error",
) -> Tuple[List, List, List]:
    """Compute the bins, counts and statistic values used for plotting the segmented loss.

    Arguments:
        model {feyn.Model} -- The model to calculate the segmented loss for
        data {DataFrame} -- The data to calculate the segmented loss on

    Keyword Arguments:
        by {str} -- The input or output to segment by (default: {None})
        loss_function {str} -- The loss function to use (default: {"squared_error"})

    Returns:
        Tuple[List, List, List] -- bins, counts and statistics

    Raises:
        ValueError: if by is not in data.
        ValueError: If columns needed for the model are not present in the data.
    """
    if type(data).__name__ != "DataFrame":
        _logger.warning(
            "Deprecation: using Iterables other than DataFrames are deprecated and will be removed in future versions of Feyn."
        )
        data = pd.DataFrame(data)

    _validate_data_columns_for_model(model, data)

    if by is None:
        by = model.output
    elif by not in data:
        raise ValueError(f"Argument `by`='{by}' not in data.")

    if data[by].dtype == object or len(np.unique(data[by])) < 10:
        return _discrete_segmented_loss(model, data, by, loss_function)
    else:
        return _continuous_segmented_loss(model, data, by, loss_function)


def _discrete_segmented_loss(model, data, by, loss_function):
    loss_function = feyn.losses._get_loss_function(loss_function)
    output = model.output

    pred = model.predict(data)

    bins = []
    cnt = []
    stats = []
    for cat in np.unique(data[by]):
        bool_index = data[by] == cat
        subset = {key: values[bool_index] for key, values in data.items()}
        pred_subset = pred[bool_index]

        loss = np.mean(loss_function(subset[output], pred_subset))

        bins.append(cat)
        cnt.append(len(pred_subset))
        stats.append(loss)

    return bins, cnt, stats


def _significant_digits(x, p):
    mags = 10 ** (p - 1 - np.floor(np.log10(x)))
    return np.round(x * mags) / mags


def _continuous_segmented_loss(model, data, by, loss_function):
    bincnt = 12
    loss_function = feyn.losses._get_loss_function(loss_function)
    output = model.output

    pred = model.predict(data)

    bins = []
    cnt = []
    stats = []

    mn = np.min(data[by])
    mx = np.max(data[by])
    stepsize = _significant_digits((mx - mn) / bincnt, 2)

    lower = mn
    while lower < mx:
        upper = lower + stepsize

        bool_index = (data[by] >= lower) & (data[by] < upper)
        subset = {key: values[bool_index] for key, values in data.items()}
        pred_subset = pred[bool_index]

        if len(pred_subset) == 0:
            loss = np.nan
        else:
            loss = np.mean(loss_function(subset[output], pred_subset))
        bins.append((lower, upper))
        cnt.append(len(pred_subset))
        stats.append(loss)

        lower = upper

    return bins, cnt, stats


def get_mutual_information(model: feyn.Model, data: pd.DataFrame) -> List[float]:
    """
    Calculate the mutual information between each node of the provided model and the output.

    Arguments:
        model {feyn.Model} -- The Model
        data {DataFrame} -- The data

    Returns:
        List[float] -- The mutual information between each node and the output, in Model node order.

    Raises:
        ValueError: If columns needed for the model are not present in the data.
    """
    if type(data).__name__ != "DataFrame":
        _logger.warning(
            "Deprecation: using Iterables other than DataFrames are deprecated and will be removed in future versions of Feyn."
        )
        data = pd.DataFrame(data)

    _validate_data_columns_for_model(model, data)

    ret = []

    data_output = data[model.output]
    activations = model._get_activations(data)
    for n in range(len(model)):
        ret.append(calculate_mi([activations[n], data_output]))

    return ret


def get_pearson_correlations(model: feyn.Model, data: pd.DataFrame) -> List[float]:
    """
    Calculate the pearson correlation coefficient between each node of the model and the output.

    Arguments:
        model {feyn.Model} -- The Model
        data {DataFrame} -- The data

    Returns:
        List[float] -- The pearson correlation between each node and the output, in Model node order.

    Raises:
        ValueError: If columns needed for the model are not present in the data.
    """
    if type(data).__name__ != "DataFrame":
        _logger.warning(
            "Deprecation: using Iterables other than DataFrames are deprecated and will be removed in future versions of Feyn."
        )
        data = pd.DataFrame(data)

    _validate_data_columns_for_model(model, data)

    ret = []

    data_output = data[model.output]
    activations = model._get_activations(data)
    for n in range(len(model)):
        ret.append(calculate_pc(activations[n], data_output))

    return ret


def get_spearmans_correlations(model: feyn.Model, data: pd.DataFrame):
    """
    Calculate the Spearman's correlation coefficient between each node of the model and the output.


    Arguments:
        model {feyn.Model} -- The Model
        data {DataFrame} -- The data

    Returns:
        List[float] -- The spearman correlation between each node and the output, in Model node order.

    Raises:
        ValueError: If columns needed for the model are not present in the data.
    """
    if type(data).__name__ != "DataFrame":
        _logger.warning(
            "Deprecation: using Iterables other than DataFrames are deprecated and will be removed in future versions of Feyn."
        )
        data = pd.DataFrame(data)

    _validate_data_columns_for_model(model, data)

    ret = []

    data_output = data[model.output]
    activations = model._get_activations(data)
    for n in range(len(model)):
        ret.append(calculate_spear(activations[n], data_output))

    return ret


def get_summary_information(model: feyn.Model, df: pd.DataFrame) -> Dict[str, float]:
    """
    Get summary metrics for the provided model.

    This wraps functions get_summary_metrics_classification and get_summary_metrics_regression, automatically detecting what to output based on the model kind and the output node.

    Arguments:
        model {feyn.Model} -- The model to summarise
        df {pd.DataFrame} -- The data

    Returns:
        Dict[str, float] -- A dictionary of summary metrics.

    Raises:
        ValueError: If columns needed for the model are not present in the data.
    """
    _validate_data_columns_for_model(model, df)

    true = df[model.output]
    pred = model.predict(df)

    if model.kind == "classification":
        return get_summary_metrics_classification(true, pred)
    else:
        return get_summary_metrics_regression(true, pred)
