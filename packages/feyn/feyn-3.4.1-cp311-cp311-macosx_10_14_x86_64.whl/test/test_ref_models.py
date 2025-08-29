import unittest

import pandas as pd
import numpy.testing
import numpy as np

import feyn.reference

class TestReferenceModels(unittest.TestCase):
    def setUp(self):
        self.x = np.array([1,2,3,4,5])
        self.y = np.array([0,1,1,1,0])
        self.X = self.x.reshape(-1, 1)
        self.df = pd.DataFrame({"x": self.x, "y": self.y})
        self.output_name = "y"
        self.random_state = 42

    def test_constant_model(self):
        const = 42
        cm = feyn.reference.ConstantModel(self.output_name, const)
        self.assertIsNotNone(cm.predict(self.df))

    def test_sklearn_classifier(self):
        from sklearn.svm import SVC
        ref_model_preds = feyn.reference.SKLearnClassifier(SVC, self.df, self.output_name, random_state=self.random_state, probability=True).predict(self.df)
        sklearn_native_preds = SVC(random_state=self.random_state, probability=True).fit(self.X, self.y).predict_proba(self.X)[:, -1] # type: ignore
        numpy.testing.assert_allclose(ref_model_preds, sklearn_native_preds)

    def test_sklearn_regressor(self):
        from sklearn.linear_model import ElasticNet
        ref_model_preds = feyn.reference.SKLearnRegressor(ElasticNet, self.df, self.output_name, random_state=self.random_state).predict(self.df)
        sklearn_native_preds = ElasticNet(random_state=self.random_state).fit(self.X, self.y).predict(self.X)
        numpy.testing.assert_allclose(ref_model_preds, sklearn_native_preds)

    def test_random_forest_classifier(self):
        from  sklearn.ensemble import RandomForestClassifier
        ref_model_preds = feyn.reference.RandomForestClassifier(self.df, self.output_name, random_state=self.random_state).predict(self.df)
        sklearn_native_preds = RandomForestClassifier(random_state=self.random_state).fit(self.X, self.y).predict_proba(self.X)[:, -1] # type: ignore
        numpy.testing.assert_allclose(ref_model_preds, sklearn_native_preds)

    def test_gradient_boosting_classifer(self):
        from  sklearn.ensemble import GradientBoostingClassifier
        ref_model_preds = feyn.reference.GradientBoostingClassifier(self.df, self.output_name, random_state=self.random_state).predict(self.df)
        sklearn_native_preds = GradientBoostingClassifier(random_state=self.random_state).fit(self.X, self.y).predict_proba(self.X)[:, -1] # type: ignore
        numpy.testing.assert_allclose(ref_model_preds, sklearn_native_preds)

    def test_linear_regression(self):
        from  sklearn.linear_model import LinearRegression
        ref_model_preds = feyn.reference.LinearRegression(self.df, self.output_name).predict(self.df)
        sklearn_native_preds = LinearRegression().fit(self.X, self.y).predict(self.X)
        numpy.testing.assert_allclose(ref_model_preds, sklearn_native_preds)

    def test_stypes(self):
        from feyn.reference import LinearRegression, LogisticRegressionClassifier
        df = pd.DataFrame({"x": self.x, "cat_col": np.array(["k","i","t","t","y"]), "y": self.y})
        stypes = {"cat_col": None}
        with self.subTest("Test stypes of Linear Regression"):
            stypes["cat_col"] = "c"
            self.assertIsNotNone(LinearRegression(df, self.output_name, stypes=stypes))
            stypes["cat_col"] = "cat"
            self.assertIsNotNone(LinearRegression(df, self.output_name, stypes=stypes))
            stypes["cat_col"] = "categorical"
            self.assertIsNotNone(LinearRegression(df, self.output_name, stypes=stypes))


        with self.subTest("Test stypes of Logistic Regression"):
            stypes["cat_col"] = "c"
            self.assertIsNotNone(LogisticRegressionClassifier(df, self.output_name, stypes=stypes))
            stypes["cat_col"] = "cat"
            self.assertIsNotNone(LogisticRegressionClassifier(df, self.output_name, stypes=stypes))
            stypes["cat_col"] = "categorical"
            self.assertIsNotNone(LogisticRegressionClassifier(df, self.output_name, stypes=stypes))

