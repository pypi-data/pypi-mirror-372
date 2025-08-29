import math
import numpy as np


class ExplainerModel:
    """ Form a binary matrix with all combinations of features
        deciding which features to fix and which to vary through random sampling.
        This matrix is m by 2^m.

        For a single instance.
    """
    def __init__(self, no_features, bg_data, max_samples=10000):
        self.m = no_features
        # Use all samples and no more, if smaller than max_samples
        self.features = list(bg_data.keys())
        self.dtypes = dict([(col, bg_data[col].dtype) for col in bg_data])

        # We no longer deal with the pandas/np dict structure from now on
        self.bg_data = self._unwrap_np_dict(bg_data)
        self.no_samples = max_samples if len(self.bg_data) > max_samples else len(self.bg_data)

        self.size = 2**self.m
        self.X = np.zeros(shape=(self.size, self.m))

        for i in range(0, self.size):
            self.X[i, :] = self._get_binary_array(i, length=self.m)

        self._add_intercept()

        # Pre-sample bg_data so we don't have to do this for each instance we want to predict.
        # Minor (potentially unnecessary) optimization
        self.sample_matrix = self._short_sample(self.bg_data, self.no_samples)

        # Required for the linear regressor
        self.sample_weights = self._get_sample_weights()
        self.lr_X = self._get_lr_X()
        self.initialize_background_matrix()

    @staticmethod
    def _unwrap_np_dict(data):
        # Transpose to ensure we are oriented row-wise
        return np.array([data[col] for col in data.keys()]).T

    @staticmethod
    def _short_sample(data, no_samples):
        """ Sample function that does not oversample nor sample with replacement.

        Arguments:
            data {[np.array]} -- numpy array
            no_samples {[type]} -- number of samples to take up till len(data)
        """
        permutation = np.random.permutation(no_samples)
        return data[permutation]

    def initialize_background_matrix(self):
        # Get the relevant rows out of the X matrix.
        # We would have chopped off the first and last row anyway, so no need to deal with them
        self._rows = self.X[1:-1, 1:]  # Also ignore intercept column

        # We tile the dataset to preserve the order in the repeats.
        # Tiling preserves the order of the matrix, so we can "apply" it multiple times as a whole, once for each row.
        # This is also useful for splitting and averaging later to get the y_vector
        self._df_rep = np.tile(self.sample_matrix, (len(self._rows), 1))

        # Providing an index makes it slightly easier to debug how things get repeated
        # TODO: Is this still useful????
        self._repeated_index = np.tile(range(0, len(self.sample_matrix)), len(self._rows))

    def _add_intercept(self):
        ones = np.ones((self.X.shape[0], 1))
        self.X = np.concatenate((ones, self.X), axis=1)

    def get_y_vector(self, model, instance, baseline, prediction):
        """
            instance and bg_data will have to be pd or numpy dict
            They have to be pre-pruned for unused features
        """
        # Note: The following relies on pre-processed matrices from the init function :)
        instance_columns = instance.keys()

        instance_values = np.array(list(instance.values())).T

        # Repeat instance to be as large as the repeated sample_dataframe to make it easier to vectorize merging values
        instance_rep = np.repeat(instance_values, len(self._df_rep), axis=0)

        # We want to extract each row's average prediction on the background data, so we shuffle the rows and
        # apply to the tiled dataset [1,2,3] => [1, 1, 1, 2, 2, 2, 3, 3, 3] with np.repeat([1,2,3], 3)
        rows_rep = np.repeat(self._rows, len(self.sample_matrix), axis=0)

        # Replace the cells where the rows == 0 with whatever's in the background data.
        instance_rep[rows_rep == 0] = self._df_rep[rows_rep == 0]

        # TODO: quite a waste of time..
        # Translate back to a dict of numpy arrays that feyn understands...
        # Transpose to column orientation
        samples_dict = {col: instance_rep.T[i] for i, col in enumerate(instance_columns)}

        # Reset the dtype to its original after repeat stuff since numpy will coerce to one type.
        for col in samples_dict:
            samples_dict[col] = samples_dict[col].astype(self.dtypes[col])

        sample_predictions = model.predict(samples_dict)

        splits = np.split(sample_predictions, len(self._rows))
        # Assign the averages as y and make sure y gets shape (self.size (-chopped), 1)
        y = np.average(splits, axis=1).reshape(-1, 1)

        # Calculate the lr_y shap contribution vector from y
        last_col = self.get_last_column()

        # Unfold the single instance prediction
        # prediction = model.predict(instance)[0]
        # use prediction in function call instead to save time...
        last_shap_contribution = last_col * prediction

        inverse_contribution = (1-last_col) * baseline

        lr_y = y - last_shap_contribution - inverse_contribution
        return lr_y

    def _get_lr_X(self):
        """ Returns the X matrix for the linear regressor

        Returns:
            X -- np.array matrix
        """
        #  Chop and do some value replacements for X to constrain the linear model according to two rules:
        #  1. The top shap value should be the baseline
        #  2. All of the shap values should sum up to the prediction of the instance

        # Chop the first and last row and column
        alt_X = self.X.copy()[1:-1, 1:-1]

        # Form a matrix for the last column that is the same width as the chopped X
        last_col = self.get_last_column()
        # Axis one, to get it to repeat columnwise rather tthan row-wise
        last_col_repeat = np.repeat(last_col, alt_X.shape[1], axis=1)

        lr_X = alt_X - last_col_repeat
        return lr_X

    def get_last_column(self):
        """Returns the last column of X, chopping off the top and bottom

        Returns:
            X -- np.array
        """
        return self.X[1:-1, -1:].copy()

    @staticmethod
    def _get_binary_array(n, length):
        b = np.zeros(length)
        # Get a binary string, reverse it and iterate over it
        for i, c in enumerate('{0:b}'.format(n)[::-1]):
            b[i] = int(c)
        return b

    @staticmethod
    def binom(n, k):
        n = int(n)
        k = int(k)
        fact = math.factorial
        return (fact(n)) / (fact(k)*fact(n-k))

    def _get_sample_weights(self):
        X_middle_rows = self.X.copy()[1:-1, 1:]  # Disregard the intercept column
        # For each row in X, sum the 1's
        sum_x_vector = X_middle_rows.sum(axis=1)

        sample_weights = np.zeros(len(sum_x_vector))
        m = self.m

        for i, row in enumerate(sum_x_vector):
            num = m - 1
            denom = self.binom(m, row) * (row) * (m - row)
            sample_weights[i] = num / denom

        return sample_weights
