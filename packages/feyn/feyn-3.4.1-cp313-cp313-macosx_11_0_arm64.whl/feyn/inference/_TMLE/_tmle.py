import numpy as np
from ._glm_bernoulli import GLM_Bernoulli


class TMLE:
    """Calculates the Targeted Maximum Likelihood for some data
    and feyn.Model exposure and outcome models.
    """

    def __init__(
        self, data, outcome_model, exposure_model, alpha=0.05, continuous_bound=5.0e-6
    ) -> None:
        """Initialize the TMLE class

        Arguments:
            data {dict(str, np.array) or pd.DataFrame} -- dataset to calculate TMLE
            outcome_model {feyn.Model} -- model for the outcome variable
            exposure_model {feyn.Model} -- model for the exposure variable

        Keyword Arguments:
            alpha {float} -- significance of confidence interval (default: {0.05})
            continuous_bound {float} -- significance of bounded
            variables to the (0., 1.) interval (default: {0.0005})
        """

        self.data = data

        if all(hasattr(outcome_model, attr) for attr in ["target", "predict"]):
            self.outcome_model = outcome_model
            self.outcome = outcome_model.target
        else:
            raise AttributeError(
                "The outcome model should have the attributes 'target' and 'predict'!"
            )

        if all(
            hasattr(exposure_model, attr) for attr in ["target", "predict", "features"]
        ):
            self.exposure_model = exposure_model
            self.exposure = exposure_model.target
            self.confounders = exposure_model.features
        else:
            raise AttributeError(
                "The exposure model should have the attributes 'target', 'features' and 'predict'!"
            )

        # Bounding
        self.outcome_min = data[self.outcome].min()
        self.outcome_max = data[self.outcome].max()

        # Inference measures
        self.bound = continuous_bound
        self.alpha = alpha

        self.ate = None
        self.ate_se = None
        self.ate_ci = None

        # Step 1: E[Y | A, X]
        O_Aactual, OA1, OA0 = self._get_outcome_predictions()

        # Step 2: P(A | X)
        pi_1, pi_0 = self._exposure_probability()

        HA1, HA0, HA = self._predefined_covariates(pi_1, pi_0)

        # Step 3+4: Update the expectation of your predicted outcomes
        self.OA_star, self.OA1_star, self.OA0_star = self._update_OAS(
            O_Aactual, OA0, OA1, HA0, HA1
        )
        self.HA = HA

    def _get_outcome_predictions(self):
        # Predicting outcomes for treatment = 1 only
        df_A1 = self.data.copy()
        df_A1[self.exposure] = np.ones(df_A1[self.exposure].shape[0])
        OA1 = self.outcome_model.predict(df_A1)

        # Predicting outcomes for treatment = 0 only
        df_A0 = self.data.copy()
        df_A0[self.exposure] = np.zeros(df_A0[self.exposure].shape[0])
        OA0 = self.outcome_model.predict(df_A0)

        # Predicting outcomes for original dataset
        O_actual = self.outcome_model.predict(self.data)

        return O_actual, OA1, OA0

    def _exposure_probability(self):
        pi_1 = self.exposure_model.predict(self.data)
        pi_0 = 1 - pi_1
        return pi_1, pi_0

    def _predefined_covariates(self, pi_1, pi_0):
        # Check for probability values outside of (0, 1)!
        if (
            np.any(pi_1 <= 0)
            or np.any(pi_1 > 1.0)
            or np.any(pi_0 <= 0)
            or np.any(pi_0 > 1)
        ):
            raise ValueError("Probability values outside the (0, 1] interval!")
        else:
            # Calculate H_a: if A = 1 then 1 / prob else -1 / prob
            HA = self.data[self.exposure] * (1 / pi_1) - (
                1 - self.data[self.exposure]
            ) * (1.0 / pi_0)

            HA1 = np.where(HA > 0, HA, 0)
            HA0 = np.where(HA < 0, HA, 0)

        return HA1, HA0, HA

    # Bounding according to TMLE and making sure no values are equal to 0 or 1
    def _unit_bounding(self, y):
        y_star = (y - self.outcome_min) / (self.outcome_max - self.outcome_min)  # line
        y_star = np.where(y_star < self.bound, self.bound, y_star)
        y_star = np.where(y_star > 1 - self.bound, 1 - self.bound, y_star)
        return y_star

    def _unit_unbounding(self, ystar):
        y = ystar * (self.outcome_max - self.outcome_min) + self.outcome_min
        return y

    @staticmethod
    def _logit(p):
        y = np.log(np.divide(p, 1.0 - p))
        return y

    @staticmethod
    def _inv_logit(p):
        y = 1 / (1 + np.exp(-p))
        return y

    def _get_GLM(self, O_actual, HA0, HA1):
        # Get bounded prediction and truth
        bounded_outcome = self._unit_bounding(self.data[self.outcome])
        bounded_O_actual = self._unit_bounding(O_actual)

        # try except
        try:
            glm = GLM_Bernoulli()
            glm.fit(
                X=np.column_stack([HA1, HA0]),
                Y=bounded_outcome,
                offset=self._logit(bounded_O_actual),
            )
        except Exception as inst:
            print(
                'Error in the Generalized Linear Model from statsmodels: "%s".' % inst
            )
            raise

        return glm

    def _update_OAS(self, OA, OA0, OA1, HA0, HA1):
        # Step 3: Solve the Efficient Influence Function
        EIF = self._get_GLM(OA, HA0, HA1)

        OA1 = self._unit_bounding(OA1)
        OA0 = self._unit_bounding(OA0)
        OA = self._unit_bounding(OA)

        # Fluctuation parameter
        delta = EIF.params

        OA1 = self._inv_logit(self._logit(OA1) + delta[0] * HA1)
        OA0 = self._inv_logit(self._logit(OA0) + delta[1] * HA0)
        OA = EIF.predict(np.column_stack((HA1, HA0)))

        OA1 = self._unit_unbounding(OA1)
        OA0 = self._unit_unbounding(OA0)
        OA = self._unit_unbounding(OA)

        return OA, OA1, OA0

    def ATE(self):
        """Calculates the Average Treatment Effect (ATE), standard errors
        and confidence intervals.
        """
        truth = self.data[self.outcome]
        n_samples = truth.shape[0]

        # Step 5: Calculate ATE
        self.ate = np.nanmean(self.OA1_star - self.OA0_star)

        # Step 6: Calculate SE and CI
        zalpha = 1.96

        influence_func = (
            self.HA * (truth - self.OA_star)
            + (self.OA1_star - self.OA0_star)
            - self.ate
        )
        seIF = np.sqrt(np.nanvar(influence_func, ddof=1) / n_samples)
        self.ate_se = seIF
        self.ate_ci = [self.ate - zalpha * seIF, self.ate + zalpha * seIF]

    def summary(self):

        from IPython.display import display

        if self.ate is None:
            self.ATE()

        print("======================================================================")
        print("                       TMLE w. QLattice                 ")
        print("======================================================================")
        print("Targeted Maximum Likelihood applied with QLattice models.\n")
        print("Average Treatment Effect: ", round(float(self.ate), 3))
        print(
            str(round(100 * (1 - self.alpha), 1))
            + "% two-sided CI: ("
            + str(round(self.ate_ci[0], 3)),
            ",",
            str(round(self.ate_ci[1], 3)) + ")",
        )
        print(
            "\n======================================================================"
        )
        print("                       Outcome model")
        print("======================================================================")

        display(self.outcome_model)

        print("======================================================================")
        print("                       Exposure model")
        print("======================================================================")

        display(self.exposure_model)
        print(
            "======================================================================\n"
        )
