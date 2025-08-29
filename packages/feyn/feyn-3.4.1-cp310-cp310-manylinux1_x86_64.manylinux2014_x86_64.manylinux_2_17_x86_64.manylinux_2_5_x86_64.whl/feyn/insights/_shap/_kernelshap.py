import numpy as np
from ._explainermodel import ExplainerModel
from feyn.tools._linear_model import LinearRegression

class KernelShap:
    """Calculates the SHAP values for a given feyn.Model with your provided instances"""

    def __init__(self, model, bg_data, max_samples=10000):
        """Initialize the KernelShap class.

        Arguments:
            model {feyn.Model} -- the model you want importances for.
            bg_data {dict{(str, np.array)} or pd.Dataframe} -- the background data (normally your training set).

        Keyword Arguments:
            max_samples {int} -- The maximum amount of samples from your background data used in computation. It will never use more than are in your dataframe. (default: {10000})
        """
        self.model = model
        self.features = model.features

        self.bg_data = self._sanitize_dataframe(bg_data, self.features)

        self.explainer_model = ExplainerModel(
            no_features=len(self.features),
            bg_data=self.bg_data,
            max_samples=max_samples,
        )
        self.baseline = self.model.predict(self.bg_data).mean()

    @staticmethod
    def _sanitize_dataframe(maybe_df, features=None):
        if type(maybe_df).__name__ == "DataFrame":
            data = {col: maybe_df[col].values for col in maybe_df.columns}
        else:
            data = maybe_df

        if features is None:
            return data
        return {col: data[col] for col in features}

    def _get_feature_indices(self, feature_list):
        indices = []
        # Yo, the order in which we do this is important
        # because order of features can be shuffled in the model...
        for feat in self.features:
            indices.append(list(feature_list).index(feat))

        return indices

    def SHAP(self, instances):
        """Calculates the SHAP values for the provided instances

        Arguments:
            instances {dict(str, np.array) or pd.DataFrame} -- One or more instances to get SHAP values for.

        Returns:
            [np.array] -- A numpy array (matrix) containing feature importances for your instances
        """
        # Prepare result dataframe for all columns in instance (even unused ones)
        # Note: This discards indices if it's a pandas dataframe
        dict_instances = self._sanitize_dataframe(instances)
        instance_features = dict_instances.keys()

        cols = len(instance_features)
        rows = len(list(dict_instances.values())[0])
        shap_df = np.zeros(shape=(rows, cols))

        # shap only for the features we need
        shap_values = np.zeros(shape=(rows, len(self.features)))
        # preload predictions
        predictions = self.model.predict(instances)

        for i in range(rows):
            # Only get the features we need
            instance = {
                col: np.array([dict_instances[col][i]]) for col in self.features
            }

            # Extract the prediction to shave off some milliseconds for each instance
            prediction = predictions[i]

            if len(self.features) < 2:
                shap_values[i] = prediction - self.baseline
            else:
                #  Get the target y to put into the Linear regressor
                lr_y = self.explainer_model.get_y_vector(
                    self.model, instance, self.baseline, prediction
                )
                #  Get the X to put into the Linear regressor
                lr_X = self.explainer_model.lr_X

                # Form the sample weights for the linear regressor
                sample_weights = self.explainer_model.sample_weights

                #  Predict the target with a linear regressor
                lr = LinearRegression(fit_intercept=False)
                lr.fit(X=lr_X, y=lr_y, sample_weights=sample_weights)

                #  The first and last shap value is restricted to respectively the baseline and
                #  the coefficients of the lr
                shap_values[i] = np.append(
                    lr.coef, prediction - (lr.coef.sum() + self.baseline)
                )

        shap_df[:, self._get_feature_indices(instance_features)] = shap_values
        return shap_df
