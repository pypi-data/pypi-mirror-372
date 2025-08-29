from typing import Tuple, Union
import pandas as pd


def make_classification(
    n_samples: int = 100,
    n_features: int = 20,
    stratify: bool = False,
    shuffle_features: bool = False,
    shuffle_split: bool = True,
    random_state: Union[bool, None] = None,
    **kwargs,
) -> Tuple:
    """Uses sklearn.datasets.make_classification to create a classification problem
    and returns train and test DataFrames.
    Keyword arguments are parameters in sklearn.datasets.make_classification and
    sklearn.model_selection.train_test_split.

    Args:
        n_samples (int, optional): The number of samples. Defaults to 100.
        n_features (int, optional): The number of features. Defaults to 20.
        stratify (bool, optional): Stratifies the train, test split by the output variable y. Defaults to False.
        shuffle_features (bool, optional): Whether or not to shuffle the samples and the features. Defaults to False.
        shuffle_split (bool, optional): Whether or not to shuffle the data before doing the train-test split. Defaults to True.
        random_state (int or None, optional): Determines the seed for the randomness associated with creating an splitting the synthetic data set. Defaults to None.

    Returns:
        train, test: The training and test set of the classification problem
    """
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    cls_kwargs = _determine_classifier_kwargs(shuffle_features, **kwargs)
    split_kwargs = _determine_split_kwargs(shuffle_split, **kwargs)

    X, y = make_classification(
        n_samples, n_features, random_state=random_state, **cls_kwargs
    )

    data = pd.DataFrame(X, columns=[f"x{i}" for i in range(X.shape[1])])
    data["y"] = y

    if stratify:
        split_kwargs["stratify"] = data["y"]

    train, test = train_test_split(data, random_state=random_state, **split_kwargs)

    return train, test


def make_regression(
    n_samples: int = 100,
    n_features: int = 20,
    stratify: bool = False,
    shuffle_features: bool = False,
    shuffle_split: bool = True,
    random_state: Union[bool, None] = None,
    **kwargs,
) -> Tuple:
    """Uses sklearn.datasets.make_regression to create a regression problem
    and returns train and test DataFrames.
    Keyword arguments are parameters in sklearn.datasets.make_regression and
    sklearn.model_selection.train_test_split.

    Args:
        n_samples (int, optional): The number of samples. Defaults to 100.
        n_features (int, optional): The number of features. Defaults to 20.
        stratify (bool, optional): Stratifies the train, test split by the output variable y. Defaults to False.
        shuffle_features (bool, optional): Whether or not to shuffle the samples and the features. Defaults to False.
        shuffle_split (bool, optional): Whether or not to shuffle the data before doing the train-test split. Defaults to True.
        random_state (int or None, optional): Determines the seed for the randomness associated with creating an splitting the synthetic data set. Defaults to None.

    Returns:
        Tuple: [description]
    """
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split

    reg_kwargs = _determine_reg_kwargs(shuffle_features, **kwargs)
    split_kwargs = _determine_split_kwargs(shuffle_split, **kwargs)

    X, y = make_regression(
        n_samples, n_features, random_state=random_state, **reg_kwargs
    )

    data = pd.DataFrame(X, columns=[f"x{i}" for i in range(X.shape[1])])
    data["y"] = y

    if stratify:
        split_kwargs["stratify"] = data["y"]

    train, test = train_test_split(data, random_state=random_state, **split_kwargs)

    return train, test


def _determine_classifier_kwargs(shuffle_features, **kwargs):

    cls_kwarg_names = [
        "n_informative",
        "n_redundant",
        "n_repeated",
        "n_classes",
        "n_clusters_per_class",
        "weights",
        "flip_y",
        "class_sep",
        "hypercube",
        "shift",
        "scale",
    ]

    cls_kwargs = {}
    if kwargs:
        cls_kwargs = {key: kwargs[key] for key in kwargs if key in cls_kwarg_names}
    cls_kwargs["shuffle"] = shuffle_features

    return cls_kwargs


def _determine_split_kwargs(shuffle_split, **kwargs):

    split_kwarg_names = [
        "test_size",
        "train_size",
    ]

    split_kwargs = {}
    if kwargs:
        split_kwargs = {key: kwargs[key] for key in kwargs if key in split_kwarg_names}
    split_kwargs["shuffle"] = shuffle_split

    return split_kwargs


def _determine_reg_kwargs(shuffle_features, **kwargs):

    reg_kwarg_names = [
        "n_informative",
        "n_targets",
        "bias",
        "effective_rank",
        "tail_strength",
        "noise",
    ]

    reg_kwargs = {}
    if kwargs:
        reg_kwargs = {key: kwargs[key] for key in kwargs if key in reg_kwarg_names}

    reg_kwargs["shuffle"] = shuffle_features

    return reg_kwargs
