"""
This module contains reference models that can be used for comparison with feyn models.
"""

import typing
from typing import Optional, Dict
from abc import ABCMeta, abstractmethod

import numpy as np
from pandas import DataFrame

from .._base_reporting_mixin import BaseReportingMixin


class BaseReferenceModel(BaseReportingMixin, metaclass=ABCMeta):
    """Base class for reference models"""

    @abstractmethod
    def predict(self, X: typing.Iterable):
        """Get predictions for a given dataset.

        Arguments:
            data {Iterable} -- Data to predict for.

        Returns:
            Iterable -- The predictions for the data.
        """
        raise NotImplementedError()


class ConstantModel(BaseReferenceModel):
    def __init__(self, output_name: str, const: float):
        """Create a Constant Model on your dataset.

        This will always return the same value, regardless of the samples you provide it.

        Arguments:
            output_name {str} -- The output column of your dataset.
            const {float} -- The constant to return (for instance, you can choose the mean of your dataset).
        """
        self.const = const
        self.output = output_name
        self.inputs = []

    def predict(self, data: typing.Iterable):
        return np.full(len(data), self.const)


class SKLearnClassifier(BaseReferenceModel):
    def __init__(
        self,
        sklearn_classifier: type,
        data: DataFrame,
        output_name: str,
        stypes: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Creates a base SKLearn Classifier on your dataset.

        Arguments:
            sklearn_classifier {type} -- The sklearn model type you want to wrap.
            (example: sklearn.linear_model.LogisticRegression).
            data {DataFrame} -- The data to fit on.
            output_name {str} -- The output column of your dataset.
        """
        from sklearn.compose import make_column_transformer
        from sklearn.preprocessing import OrdinalEncoder

        self.inputs = list(data.columns)
        if output_name in self.inputs:
            self.inputs.remove(output_name)

        self.output = output_name
        self.kind = "classification"

        if stypes:
            self.categorical_features = [
                feature
                for feature in stypes.keys()
                if stypes[feature] in ["c", "cat", "categorical"]
            ]
            data[self.categorical_features] = data[self.categorical_features].astype(
                str
            )
            self.cat_tree_processor = OrdinalEncoder(
                handle_unknown="use_encoded_value", unknown_value=-1
            )
            self.classifier_preprocessor = make_column_transformer(
                (self.cat_tree_processor, self.categorical_features),
                remainder="passthrough",
            )
            X = self.classifier_preprocessor.fit_transform(data[self.inputs])
        else:
            self.cat_tree_processor = None
            self.classifier_preprocessor = None
            X = data[self.inputs].values
        y = data[self.output].values

        self._model = sklearn_classifier(**kwargs)
        self._model.fit(X=X, y=y)

    def predict(self, X: typing.Iterable):
        if type(X).__name__ == "DataFrame":
            if self.classifier_preprocessor:
                X = self.classifier_preprocessor.transform(X[self.inputs])
            else:
                X = X[self.inputs].values

        elif type(X).__name__ == "dict":
            X = np.array([X[col] for col in self.inputs]).T
            if self.classifier_preprocessor:
                X = self.classifier_preprocessor.transform(X)

        pred = self._model.predict_proba(X)[:, 1]
        return pred


class LogisticRegressionClassifier(SKLearnClassifier):
    def __init__(self, data: DataFrame, output_name: str, **kwargs):
        """Create a Logistic Regression Classifier on your dataset.

        This calls sklearn.linear_model.LogisticRegression under the hood.
        It has no special handling for categoricals, so you need to keep that in mind while using it.

        Arguments:
            data {DataFrame} -- The data to fit on.
            output_name {str} -- The output column of your dataset.
        """
        import sklearn.linear_model

        if "penalty" not in kwargs:
            kwargs["penalty"] = None
        super().__init__(
            sklearn.linear_model.LogisticRegression, data, output_name, **kwargs
        )

    def summary(self, ax=None):
        import pandas as pd

        return pd.DataFrame(data={"coeff": self._model.coef_[0]}, index=self.inputs)


class RandomForestClassifier(SKLearnClassifier):
    def __init__(self, data: DataFrame, output_name: str, **kwargs):
        """Create a Random Forest Classifier on your dataset.

        This calls sklearn.ensemble.RandomForestClassifier under the hood.
        It has no special handling for categoricals, so you need to keep that in mind while using it.

        Arguments:
            data {DataFrame} -- The data to fit on.
            output_name {str} -- The output column of your dataset.
        """
        import sklearn.ensemble

        super().__init__(
            sklearn.ensemble.RandomForestClassifier, data, output_name, **kwargs
        )


class GradientBoostingClassifier(SKLearnClassifier):
    def __init__(self, data: DataFrame, output_name: str, **kwargs):
        """Create a Gradient Boosting Classifier on your dataset.

        This calls sklearn.ensemble.GradientBoostingClassifier under the hood.
        It has no special handling for categoricals, so you need to keep that in mind while using it.

        Arguments:
            data {DataFrame} -- The data to fit on.
            output_name {str} -- The output column of your dataset.
        """
        import sklearn.ensemble

        super().__init__(
            sklearn.ensemble.GradientBoostingClassifier, data, output_name, **kwargs
        )


class SKLearnRegressor(BaseReferenceModel):
    def __init__(
        self,
        sklearn_regressor: type,
        data: DataFrame,
        output_name: str,
        stypes: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Creates a base SKLearn regressor on your dataset.

        Arguments:
            sklearn_regressor {type} -- The sklearn model type you want to wrap.
            (example: sklearn.linear_model.LinearRegression).
            data {DataFrame} -- The data to fit on.
            output_name {str} -- The output column of your dataset.
        """
        from sklearn.compose import make_column_transformer
        from sklearn.preprocessing import OrdinalEncoder

        self.inputs = list(data.columns)

        self.output = output_name
        self.kind = "regression"

        if output_name in self.inputs:
            self.inputs.remove(output_name)

        if stypes:
            self.categorical_features = [
                feature
                for feature in stypes.keys()
                if stypes[feature] in ["c", "cat", "categorical"]
            ]
            data[self.categorical_features] = data[self.categorical_features].astype(
                str
            )
            self.cat_tree_processor = OrdinalEncoder(
                handle_unknown="use_encoded_value", unknown_value=-1
            )
            self.classifier_preprocessor = make_column_transformer(
                (self.cat_tree_processor, self.categorical_features),
                remainder="passthrough",
            )
            X = self.classifier_preprocessor.fit_transform(data[self.inputs])
        else:
            self.cat_tree_processor = None
            self.classifier_preprocessor = None
            X = data[self.inputs].values
        y = data[self.output].values

        self.output = output_name

        self._model = sklearn_regressor(**kwargs)
        self._model.fit(X=X, y=y)

    def predict(self, X: typing.Iterable):
        if type(X).__name__ == "DataFrame":
            X = X[self.inputs].values

        elif type(X).__name__ == "dict":
            X = np.array([X[col] for col in self.inputs]).T

        pred = self._model.predict(X)
        return pred


class LinearRegression(SKLearnRegressor):
    def __init__(self, data: DataFrame, output_name: str, **kwargs):
        """Create a Linear Regression model on your dataset.

        This calls sklearn.linear_model.LinearRegression under the hood.
        It has no special handling for categoricals, so you need to keep that in mind while using it.

        Arguments:
            data {DataFrame} -- The data to fit on.
            output_name {str} -- The output column of your dataset.
        """
        import sklearn.linear_model

        super().__init__(
            sklearn.linear_model.LinearRegression, data, output_name, **kwargs
        )
