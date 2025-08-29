import unittest

import feyn
from feyn._program import Program
from pandas import DataFrame
import numpy as np
import io

from . import quickmodels

class TestModel(unittest.TestCase):

    def test_iter(self):
        model = quickmodels.get_simple_binary_model(["x1","x2"], "y")

        self.assertEqual(len(model), 4)

        self.assertEqual(model[0].name, "y")
        self.assertEqual(model[0].fname, "out-linear:1")
        self.assertEqual(model[0].arity, 1)
        self.assertEqual(model[0].children, [1])
        self.assertListEqual(list(model[0].params.keys()), ["scale", "scale_offset", "w", "bias"])

        self.assertEqual(model[1].name, "")
        self.assertEqual(model[1].fname, "add:2")
        self.assertEqual(model[1].arity, 2)
        self.assertEqual(model[1].children, [2, 3])
        self.assertEqual(model[1].params, {})

        # Not important if x1 or x2 is position 2 or 3.
        self.assertEqual(model[2].name, "x1")
        self.assertEqual(model[2].fname, "in-linear:0")
        self.assertEqual(model[2].arity, 0)
        self.assertEqual(model[2].children, [])
        self.assertListEqual(list(model[2].params.keys()), ["scale", "scale_offset", "w", "bias"])

        self.assertEqual(model[3].name, "x2")
        self.assertEqual(model[3].fname, "in-linear:0")
        self.assertEqual(model[3].arity, 0)
        self.assertEqual(model[3].children, [])
        self.assertListEqual(list(model[3].params.keys()), ["scale", "scale_offset", "w", "bias"])


    def test_copy_model(self):
        # Arrange
        model = quickmodels.get_simple_binary_model(["x1","x2"], "y")

        # Act
        model_copy = model.copy()

        # Assert
        with self.subTest("Should predict the same"):
            pred_orig = model.predict(DataFrame({"x1": np.array([1, 2]),"x2": np.array([3, 1])}))
            pred_new  = model_copy.predict(DataFrame({"x1": np.array([1, 2]),"x2": np.array([3, 1])}))
            self.assertTrue((pred_new==pred_orig).all())

        with self.subTest("Inputs and output names preserved"):
            self.assertEqual(model_copy.output, model.output)
            self.assertEqual(model_copy.inputs, model.inputs)


    def test_persist_and_rehydrate(self):
        # Arrange
        graph = quickmodels.get_simple_binary_model(["x1","x2"], "y")

        # Persist it
        file = io.StringIO()
        graph.save(file)

        with self.subTest("Should be loadable"):
            file.seek(0)
            rehydrated_graph = feyn.Model.load(file)

        with self.subTest("Should predict the same"):
            pred_orig = graph.predict(DataFrame({"x1": np.array([1, 2]),"x2": np.array([3, 1])}))
            pred_new  = rehydrated_graph.predict(DataFrame({"x1": np.array([1, 2]),"x2": np.array([3, 1])}))
            self.assertTrue((pred_new==pred_orig).all())

        with self.subTest("Should include a version number"):
            file.seek(0)
            file_contents = file.read()
            self.assertRegex(file_contents, "version")

        with self.subTest("Inputs and output names preserved"):
            self.assertEqual(rehydrated_graph.output, graph.output)
            self.assertEqual(rehydrated_graph.inputs, graph.inputs)


    def test_persist_accepts_file_and_string(self):
        graph = quickmodels.get_simple_binary_model(["x1","x2"], "y")

        with self.subTest("Can save and load with file-like objects"):
            file = io.StringIO()
            graph.save(file)

            file.seek(0)
            rehydrated_graph = feyn.Model.load(file)
            self.assertEqual(graph, rehydrated_graph)

        with self.subTest("Can save and load with a string path"):
            import tempfile

            with tempfile.NamedTemporaryFile() as file:
                path = file.name
                graph.save(path)

                rehydrated_graph = feyn.Model.load(path)
                self.assertEqual(graph, rehydrated_graph)


    def test_edges_and_depth(self):
        # Arrange
        g = quickmodels.get_unary_model(["input"], "y")
        self.assertEqual(g.edge_count, 2)
        self.assertEqual(g.depth, 2)

        g = quickmodels.get_complicated_binary_model(["x1","x2"], "y", "exp:1")
        self.assertEqual(g.edge_count, 4)
        self.assertEqual(g.depth, 3)

    def test_predict_accepts_dicts_with_lists(self):
        # Arrange
        g = quickmodels.get_unary_model(["input"], "y")

        o = g.predict(
            {"input": [42.0, 24, 100, 50]}
        )

        self.assertEqual(len(o), 4)
        self.assertFalse(np.isnan(o).any(), "There should be no nans")

    def test_predict_accepts_Series(self):
        g = quickmodels.get_unary_model(["input"], "y")

        data = DataFrame({"input": np.array([1,2])})
        series = data.iloc[0]
        o = g.predict(series)
        self.assertFalse(np.isnan(o).any(), "There should be no nans")


    def test_init_with_missing_output(self):
        program = Program(["y", "exp:1", "x"], qid=1)
        fnames = ["linear:1","add:2", "linear:1"]

        # Sanity check
        feyn.Model(program, fnames)

        # Missing output
        with self.assertRaises(ValueError):
            feyn.Model(program, fnames[1:])

#    def test_init_invalid_fname(self):
#        program = Program([10000, 1000, 10001], qid=1)
#        names = ["y", "", "x1"]
#        fnames = ["linear","INVALID", "linear"]
#
#        # Missing output
#        with self.assertRaises(ValueError):
#            feyn.Model(program, names, fnames)


    def test_model_handles_nans(self):
        m = quickmodels.get_unary_model()

        with self.subTest("ValueError when Nan in input"):
            with self.assertRaises(ValueError) as ctx:
                data = DataFrame({"x": [np.nan]})
                m.predict(data)

            self.assertIn("nan", str(ctx.exception))

        with self.subTest("ValueError when inf in input"):
            with self.assertRaises(ValueError) as ctx:
                data = DataFrame({"x": [np.inf]})
                m.predict(data)

        with self.subTest("ValueError when Nan in output"):
            with self.assertRaises(ValueError) as ctx:
                data = DataFrame({"x": np.array([1.0]), "y": np.array([np.nan])})
                m.fit(data)
