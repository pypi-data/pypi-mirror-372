import numpy as np
from pandas import DataFrame

from typing import Optional, Iterable, Tuple

def p_value(H0:"ModelMetricsMixin", data:DataFrame, threshold:float, metric="mse") -> float:
    """
    Compute the one-tailed p-value of a hypothesis producing a value equal to or greater than the provided threshold.

    This function first constructs a sample distribution for the provided hypothesis. Assuming that this distribution is a t-distribution, it returns the probability of the hypothesis producing a sample mean as extreme or more extreme than the provided threshold.

    Arguments:
        H0 {ModelMetricsMixin} -- The model representing the null hypothesis.
        data {Iterable} -- Data from which the statistical parameters are computed.
        threshold {float} -- The threshold value we want to test the significance of, with a one-tailed probability.

    Returns:
        float -- The probability of obtaining a value as extreme or more extreme than threshold from H0.
    """

    from scipy.stats import t

    mu_0, stderr_0 = _H0_parameters(H0, data, metric)
    t_score = (threshold - mu_0)/stderr_0        # The t-statistic. Chosen because we dont know the standard deviation of the sample mean

    return t.cdf(t_score, len(data)-1)           # One tailed probability


def plot_p_value(H0:"ModelMetricsMixin", data:DataFrame, threshold:float, metric:str="mse", title:str="Significance of threshold", ax:Optional=None, **kwargs) -> None:
    """
    Plot the distribution of the sample mean of the null statistic H0. Add a vertical line corresponding to the threshold value and fill in the area corresponding to the one-sided p-value.

    Arguments:
        H0 {ModelMetricsMixin} -- The model representing the null hypothesis.
        data {Iterable} -- Data from which the statistical parameters are computed.
        threshold {float} -- The threshold value we want to test the significance of, with a one-tailed probability.

    Keyword Arguments:
        metric {str} -- Metric to use when constructing the test statistic. One of 'mse', 'mae', 'accuracy'. (default: {'mse'})
        ax {Optional} -- Matplotlib axes to plot inside of.
    """

    from scipy.stats import t
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.subplot()

    mu_0, stderr_0 = _H0_parameters(H0, data, metric)
    t_score = (threshold - mu_0)/stderr_0        # The t-statistic. Chosen because we dont know the standard deviation of the sample mean
    pvalue = t.cdf(t_score, len(data)-1)

    x = np.linspace(mu_0-5*stderr_0, mu_0+5*stderr_0, 1000)
    x_threshold = x[x < threshold]

    pd = t.pdf(x, loc=mu_0, scale=stderr_0, df=len(data)-1)

    ax.set_title(title)
    ax.set_ylabel("Probability density")
    ax.set_xlabel(metric)

    ax.plot(x, pd, alpha=0.5, label="H0 distribution")
    ax.fill_between(x_threshold, pd[range(len(x_threshold))], alpha=0.3, label="p-value: %f"%pvalue)
    ax.axvline(threshold, ls="--", lw=2, color="black", label="Threshold value")
    ax.legend()

def _H0_parameters(H0:"ModelMetricsMixin", data:DataFrame, metric) -> Tuple[float, float]:
    """
    Internal function to avoid repeating code.

    Constructs the distribution of H0. Returns the H0 sample mean and the standard error of H0.

    Arguments:
        H0 {ModelMetricsMixin} -- The model representing the null hypothesis.
        data {Iterable} -- Data from which the statistical parameters are computed.
        metric {str} -- Metric to use when constructing the test statistic. One of 'mse', 'mae', 'accuracy'.

    Raises:
        NotImplementedError: 'accuracy' is not yet implemented as a metric. ValueError: metric keyword not understood.

    Returns:
        Tuple[float, float] -- The sample mean and standard error of H0.
    """

    if metric == "mse":
        metric_0 = H0.squared_error(data)
    elif metric == "mae":
        metric_0 = H0.absolute_error(data)
    elif metric == "accuracy":
        raise NotImplementedError
    else:
        raise ValueError("Metric must be one of 'mse','mae', or 'accuracy'")

    mu_0 = metric_0.mean()                       # The sample mean of the H0
    sample_var_0 = metric_0.var()                # The sample variance which appoximates true variance
    stderr_0 = np.sqrt(sample_var_0/len(data))   # The approximate standard deviation of the sample mean (known as the standard error)

    return mu_0, stderr_0
