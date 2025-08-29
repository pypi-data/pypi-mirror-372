import unittest
import pandas as pd

from feyn.tools._model_params_dataframe import (
    get_model_parameters,
    _params_dataframe
)

from .. import quickmodels


class TestFeatParamDF(unittest.TestCase):

    def setUp(self) -> None:
        self.simple_model = quickmodels.get_simple_binary_model(
            ['banana', 'x'],
            'y',
            stypes={'banana': 'c'}
        )
        self.simple_model[0].params.update({
            'scale': 0.5,
            'w': -1.22,
            'bias': 0.023
        })
        self.simple_model[2].params.update({
            'categories': [('u', -0.026), ('m', 0.016), ('y', 0.026)],
            'bias': 0.51
        })
        self.simple_model[3].params.update({
            'scale': 0.5,
            'w': -0.55,
            'bias': 0.046
        })

    def test_raises_value_error_when_input_not_in_model(self):
        with self.assertRaises(ValueError) as ctx:
            name = 'kittens'
            get_model_parameters(
                self.simple_model, name=name
            )
        self.assertEqual(
            f"{name} not in model inputs or output!", str(ctx.exception)
        )

    def test_params_dataframe(self):
        model = self.simple_model
        with self.subTest(
            "If elem is a categorical input, index should be category and column should be the input name"
        ):
            expected = ['banana']
            actual = _params_dataframe(model[2]).columns
            self.assertListEqual(expected, list(actual))

        with self.subTest(
            "If elem is a numerical input, columns should be the input name"
        ):
            expected = ['x']
            actual = _params_dataframe(model[3]).columns
            self.assertListEqual(expected, list(actual))

        with self.subTest(
            "If elem is a numerical output, columns should be the models output"
        ):
            expected = [model.output]
            actual = _params_dataframe(model[0]).columns
            self.assertListEqual(expected, list(actual))

        with self.subTest(
            "If elem is any other function"
        ):
            expected = pd.DataFrame()
            actual = _params_dataframe(model[1])
            pd.testing.assert_frame_equal(expected, actual)

    def test_get_model_parameters_simple_model(self):
        model = self.simple_model
        with self.subTest(
            "If input is categorical"
        ):
            expected = pd.DataFrame(
                [('y', 0.026), ('m', 0.016), ('u', -0.026)],
                columns=['category', 'banana']
            ).set_index('category')
            actual = get_model_parameters(model, 'banana')
            pd.testing.assert_frame_equal(expected, actual)

        with self.subTest(
            "If input is numerical"
        ):
            expected = pd.DataFrame(
                data=[0.5, 0.0, -0.55, 0.046],
                columns=['x'],
                index=['scale', 'scale_offset', 'w', 'bias']
            )
            actual = get_model_parameters(model, 'x')
            pd.testing.assert_frame_equal(expected, actual)

        with self.subTest(
            "If input is the output"
        ):
            expected = pd.DataFrame(
                data=[0.5, 0.0, -1.22, 0.023],
                columns=[model.output],
                index=['scale', 'scale_offset', 'w', 'bias']
            )
            actual = get_model_parameters(model, 'y')
            pd.testing.assert_frame_equal(expected, actual)

    def test_get_model_parameters_complex_model(self):
        complex_model = quickmodels.get_quaternary_model(
            ['banana', 'x', 'banana', 'x'], 'y', stypes={'banana': 'c'}
        )
        for idx, elem in enumerate(complex_model):
            if elem.fname == "in-cat:0":
                complex_model[idx].params.update({
                        'categories': [('y', 0.1), ('u', 0.2), ('m', 0.3)],
                        'bias': 0.01
                })
            elif elem.fname == "in-linear:0" or 'out-' in elem.fname:
                complex_model[idx].params.update({
                    'scale': 0.5,
                    'w': 1.,
                    'bias': 0.05
                })

        with self.subTest(
            "If categorical input has multiple inputs, the columns should be the input name suffixed with the model index"
        ):
            expected = ['banana_4', 'banana_6']
            actual = get_model_parameters(complex_model, 'banana').columns
            self.assertListEqual(expected, list(actual))

        with self.subTest(
            "If numerical input has multiple inputs, the columns should be input_[elem_index], \
                where elem_index corresponds to the index of each input"
        ):
            expected = ['x_5', 'x_7']
            actual = get_model_parameters(complex_model, 'x').columns
            self.assertListEqual(expected, list(actual))
