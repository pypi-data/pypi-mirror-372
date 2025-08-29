import numpy as np


class LinearRegression:
    def __init__(self, fit_intercept: bool =True):
        self.fit_intercept = fit_intercept

    def fit(self, X, y, sample_weights=None):
        inv, mul = np.linalg.inv, np.matmul

        if sample_weights is None:
            K = np.identity(len(y))
        else:
            K = np.diag(sample_weights)

        if self.fit_intercept:
            X = self._add_intercept(X)

        # w = (X.T * K * X)^-1 * (X.T * K * y)
        XtKX_inv = inv(mul(mul(X.T, K), X))
        XtKy = mul(mul(X.T, K), y)

        self.coef = mul(XtKX_inv, XtKy)

        # sklearn compatible api
        self.coef_ = self.coef[:-1]
        if self.fit_intercept:
            self.intercept_ = self.coef[-1]

    @staticmethod
    def _add_intercept(X):
        ones = np.ones((X.shape[0], 1))
        return np.concatenate((X, ones), axis=1)

    def predict(self, X):
        if self.fit_intercept:
            X = self._add_intercept(X)
        return np.matmul(X, self.coef)
