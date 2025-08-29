import numpy as np


class GLM_Bernoulli:
    """Generalized Linear Model for the Bernoulli family.
    Parameters are found using the Iteratively Reweighted
    Least Squares (IRLS) method for maximum likelihood
    estimation.
    """
    def __init__(self, n_iter=20, epsilon=1.e-8):
        if n_iter < 2:
            raise Warning("Number of iterations should be more than 1!")

        self.n_iter = n_iter
        self.epsilon = epsilon

    def fit(self, X, Y, offset=None):

        if not np.all(offset):
            offset = np.zeros_like(Y)

        if np.all(np.isclose(Y, _inv_logit(offset), rtol=1.e-8, atol=1.e-10)):
            raise Warning("Perfect match between Y and g^-1(offset)!")
        self.params = _IRLS(X, Y, offset, self.n_iter, self.epsilon)
        self.offset = offset

    def predict(self, X):
        if self.offset is None:
            off_set = np.zeros(X.shape[0])
        else:
            off_set = self.offset
        # Model for E[Y | X]
        E_Y = _inv_logit(np.matmul(X, self.params) + off_set)
        return E_Y


def _IRLS(X, Y, offset=None, n_iter=20, epsilon=1.e-8):
    """Iteratively Reweighted Least Squares (IRLS) procedure used
    to compute the Maximum Likelihood Estimation in GLMs using
    weighted least squares
    """
    if offset is None:
        offset = np.zeros_like(Y)

    # Beginning of IRLS algorithm
    # Step1: initialize mu_k and beta_k
    mu_k = (Y.copy() + 0.5) / 2  # Taken from statsmodels
    beta_k = _WLS(X, _logit(mu_k) - offset, np.ones_like(mu_k))

    for k in range(n_iter):

        beta_old = beta_k.copy()

        # Step2: calculate the adjusted dependent responses
        Z_k = np.matmul(X, beta_k) + _logit_prime(mu_k) * (Y - mu_k)

        # Step3: calculate weights
        W_k = (1 / _logit_prime(mu_k))

        # Step4: calculate WLS for Z_k as response, X as the regressors with weights W_k
        beta_k = _WLS(X, Z_k, W_k)

        mu_k = _inv_logit(np.matmul(X, beta_k) + offset)

        if np.all(np.abs(beta_old - beta_k) < epsilon) and (k > 0):
            return beta_k

    if not np.all(np.abs(beta_old - beta_k) < epsilon):
        raise Warning("Limit of iterations achieved without desired convergence!")


def _WLS(X, Y, W):
    """Weighted Least Squares (WLS) fit for
    solving X * beta + epsilon = Y, where
    epsilon ~ Gauss(0, W^-1). A problem of
    heteroskedacity.

    Arguments:
        X {array_like} -- Input variables
        Y {array_like} -- Output variable
        W {array_like} -- Diagonal of covariance matrix
    """
    if len(W.shape) == 1:
        W = W[:, np.newaxis]
    XW = (X * W).T
    beta_hat = np.matmul(np.linalg.inv(np.matmul(XW, X)), np.matmul(XW, Y))

    return beta_hat


def _logit(x):
    """Link function of the Bernoulli family
    """
    y = np.log(x / (1 - x))
    return y


def _inv_logit(x):
    """Inverse link function
    """
    y = 1 / (1 + np.exp(-x))
    return y


def _logit_prime(x):
    """Derivative of the link function
    """
    y = 1 / (x * (1 - x))
    return y
