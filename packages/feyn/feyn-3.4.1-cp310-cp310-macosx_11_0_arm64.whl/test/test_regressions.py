"""
This file contains regression errors observed in production. Some of these tests may
be a bit gnarly formulated, they may be a bit more fragile, and they probably do not
smell like a requirement specification for the feyn.

The idea is, that these can be deleted whenever they become too annoying.
"""


import logging
import tempfile
import numpy as np
import pandas as pd

import feyn
from . import quickmodels

import unittest


class TestMiscRegressions(unittest.TestCase):
    def test_filter_works_with_numpy_int(self):
        inputs, output = list("abc"), "output"

        models = [
            quickmodels.get_unary_model(inputs, output),  # Complexity 2
            quickmodels.get_simple_binary_model(inputs, output),  # Complexity 3
        ]

        n2 = sum(map(lambda m: m.edge_count == 2, models))
        complexity_filter = feyn.filters.Complexity(np.int64(2))

        filtered_models = list(filter(complexity_filter, models))
        self.assertEqual(n2, len(filtered_models))

    def test_load_old_model_works(self):
        old_model_json = '{"program": {"codes": [10004, 2002, 10008, 2002, 10005, 2002, 10006, 10007, 2002, 2002, 10007, 10007, 10008, 1000, 10006, 1006, 10007, 10007, 10008, 2001, 1001, 2001, 2000, 10005, 2001, 10006, 1007, 2000, 2000, 2002, 10008, 10006], "data": {"pid": 13031248653188551984, "ppid": 0, "action": "n", "ix": 0, "generation": 0}, "qid": 0}, "params": [{"w": 1.0549659212594091, "bias": 2.082783433703324}, {}, {"scale": 6.721046399661164, "scale_offset": 0.4998450190228302, "w": -0.0032650443816880214, "bias": 1.2324539274728752, "detect_scale": 0}, {}, {"scale": 2.3689436314209007, "scale_offset": 0.5013280131257022, "w": 0.18506176542066283, "bias": -0.9117780481292873, "detect_scale": 0}, {}, {"scale": 2.865410015752139, "scale_offset": 0.49867192590363246, "w": -1.1014038079007502, "bias": 1.9365820489161851, "detect_scale": 0}, {"scale": 2.0079301009389385, "scale_offset": 0.4928482629433965, "w": -0.9879552463027522, "bias": 1.0153944846251604, "detect_scale": 0}], "names": ["is_active", "", "target_binding_pred", "", "dGdist_pred", "", "nucleobase_pred", "sugar_pred"], "fnames": ["out:lr", "multiply", "in:linear", "multiply", "in:linear", "multiply", "in:linear", "in:linear"], "version": "2021-08-30"}'
        with tempfile.NamedTemporaryFile("wt") as fd:
            fd.write(old_model_json)
            fd.flush()
            logger = logging.getLogger(feyn._model.__name__) 
            mock_data = pd.DataFrame({"target_binding_pred": [0.9], "dGdist_pred": [0.7], "nucleobase_pred": [0.55], "sugar_pred": [0.99], "is_active": [1]})

            with self.assertLogs(logger, level="WARNING") as cm:
                model = feyn.Model.load(fd.name)
                self.assertTrue("Deprecation" in cm.output[0])
                # Model can be used to predict
                model.predict(mock_data)
                # Model can be used by qepler
                model.fit(mock_data)
                # Model can be used to update qlattice
                ql = feyn.QLattice()
                ql.update([model])

                # Try load/save/load
                model.save(fd.name)
                model_new = feyn.Model.load(fd.name)
                self.assertEqual(model, model_new)