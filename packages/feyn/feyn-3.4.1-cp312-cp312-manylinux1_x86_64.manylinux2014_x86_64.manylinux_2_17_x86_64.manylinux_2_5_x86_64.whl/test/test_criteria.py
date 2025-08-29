import unittest
import pandas as pd

from feyn._criteria import (bic, aic, wide_parsimony,
                            _assign_qcells_by_bootstrap, _assign_qcells_by_clustering,
                            _sort_by_readability, _sort_by_structural_diversity,
                            _compute_height, _compute_average_structural_diversity_difference_scores)
from test import quickmodels


class TestCriteria(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({"x": ["a", "a", "b", "c"], "y": [1, 2, 3, 4]})

    def test_aic_computes(self):
        loss_value = 1e4
        param_count = 10
        n_samples = 100

        _aic = aic(loss_value, param_count, n_samples, 'regression')

        self.assertAlmostEqual(_aic, 941, 0)

    def test_bic_computes(self):
        loss_value = 1e4
        param_count = 10
        n_samples = 100

        _bic = bic(loss_value, param_count, n_samples, 'regression')

        self.assertAlmostEqual(_bic, 967, 0)

    def test_wide_parsimony_computes(self):
        loss_value = 1e4
        param_count = 10
        n_samples = 100
        n_features = 500
        n_inputs = 3

        _wide_parsimony = wide_parsimony(loss_value, param_count, n_samples, n_features, n_inputs,
                                                      'regression')

        self.assertAlmostEqual(_wide_parsimony, 982, 0)

    def test_outside_math_domain_of_log_works_with_epsilon(self):
        loss_value = 0
        param_count = 10
        n_samples = 100
        n_features = 5
        n_inputs = 3

        _bic = bic(loss_value, param_count, n_samples, 'classification')
        _aic = aic(loss_value, param_count, n_samples, 'classification')
        _wide_parsimony = wide_parsimony(loss_value, param_count, n_samples, n_features, n_inputs,
                                                      'regression')

        self.assertGreater(_bic, -1e10)
        self.assertGreater(_aic, -1e10)
        self.assertGreater(_wide_parsimony, -1e10)

    def test_structural_diversity(self):
        ### Define test models
        inputs, self.output = list("abcde"), "output"


        m1 = quickmodels.get_specific_model(inputs, "y", "'a'+'c'")
        m2 = quickmodels.get_specific_model(inputs, "y", "'a'*'c'")
        m3 = quickmodels.get_specific_model(inputs, "y", "'b'*'c'")
        models = [m1, m2, m3]
        # Assign dummy loss and bic values
        for m in models:
            m.bic = bic(
                loss_value=0.1, param_count=m._paramcount, n_samples=10, kind='regression'
            )

        ### Compute structural diversity metric scores
        average_structural_diversity_difference_scores = (
            _compute_average_structural_diversity_difference_scores(
                models
            )
        )
        self.assertAlmostEqual(average_structural_diversity_difference_scores[0], 1.5)
        self.assertAlmostEqual(average_structural_diversity_difference_scores[1], 1.0)
        self.assertAlmostEqual(average_structural_diversity_difference_scores[2], 1.5)

        ### Apply criterion
        # Expecting m2 to be last in sorted order
        models_sorted = _sort_by_structural_diversity(models)
        self.assertEqual(m2, models_sorted[-1])

    def test_qcell_assignment_by_clustering(self):
        num_qcells_to_assign_total = 20
        priority_number = 10
        qid_to_sample_priorities = _assign_qcells_by_clustering(
            self.df,
            priority_number=priority_number,
            num_qcells_to_assign_total=num_qcells_to_assign_total,
            max_num_clusters=2,
        )

        self.assertEqual(
            len(qid_to_sample_priorities.keys()), num_qcells_to_assign_total
        )
        self.assertEqual(len(set(qid_to_sample_priorities[0])), 2)

    def test_qcells_assignment_by_bootstrap(self):
        num_qcells_to_assign_total = 20

        qid_to_sample_priorities = _assign_qcells_by_bootstrap(
            self.df, num_qcells_to_assign_total=num_qcells_to_assign_total
        )

        self.assertEqual(
            len(qid_to_sample_priorities.keys()), num_qcells_to_assign_total
        )

    def test_sort_by_readability(self):
        ### Define test models
        inputs, self.output = list("abcde"), "output"
        m1 = quickmodels.get_specific_model(inputs, "output", "exp(exp(log('a')))")
        m2 = quickmodels.get_specific_model(inputs, "output", "log('a'+'a')+('a'+squared('b'))")
        m3 = quickmodels.get_specific_model(inputs, "output", "(log('a')+'a')+('a'+squared('b'))")
        models = [m1, m2, m3]

        # Assign dummy values
        n_samples = 10
        for m in models:
            m.loss_value = 0.1

        with self.subTest("Height computation"):
            self.assertEqual(_compute_height(0, m1), 4)

        with self.subTest("Sorting by readability"):
            models_sorted = _sort_by_readability(models, n_samples=n_samples)
            self.assertEqual(models_sorted[0], m3)
            self.assertEqual(models_sorted[1], m2)
            self.assertEqual(models_sorted[2], m1)
