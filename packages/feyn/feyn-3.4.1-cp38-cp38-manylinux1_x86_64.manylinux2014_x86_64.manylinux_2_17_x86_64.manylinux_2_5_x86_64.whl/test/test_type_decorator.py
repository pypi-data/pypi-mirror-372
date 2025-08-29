from feyn._typings import check_types
import unittest
from typing import List, Type, Union, Callable, Iterable, Dict, Optional, Set, Any
import sys

import feyn
import pytest

import pandas as pd
import numpy as np
from pandas import DataFrame

from .classes import ErrorTestCase
from . import quickmodels


def function_to_decorate(
    int_param: int,
    str_param: str = "Default",
    bool_param: bool = True,
    untyped_param=1,
    list_param: List[str] = ["Default"],
    naked_list_param: List = ["Default"],
    iterable_param: Iterable[str] = ["Default"],
    model_param: feyn.Model = quickmodels.get_unary_model(),
    list_model_param: List[feyn.Model] = [quickmodels.get_unary_model()],
    dict_param: Dict[str, int] = {"Hello": 1},
    union_param: Union[str, List[str]] = "Default",
    dict_with_union_param: Dict[str, Union[int, float, str]] = {"Hello": 1},
    any_param: Any = None,
    nested_any_param: Dict[str, Any] = None,
    opt_param: Optional[str] = None,
    opt_iterable_param: Optional[Iterable[str]] = None,
    opt_dict_param: Optional[Dict[str, str]] = None,
    nested_opt_param: Optional[List[str]] = None,
    nested_union_opt_param: Optional[Union[List[str], str]] = None,
    pd_dataframe_param: pd.DataFrame = None,
    dataframe_param: DataFrame = None,
    callable_param: Callable = None,
    typed_callable_param: Callable[[int], bool] = None,
    dict_with_list: Dict[int, List[int]] = None,
    dict_with_iterable: Dict[int, Iterable[int]] = None,
    # numpy_array_param: np.array,
    # set_param: Set[str],
):
    return True


class TestTypeDecorator(ErrorTestCase):
    def setUp(self):
        exclude = []
        self.decorated_function = check_types(exclude, verbose=True)(
            function_to_decorate
        )

    def tearDown(self):
        feyn._disable_type_checks = False  # set back to normal

    def test_can_disable_type_checks(self):
        feyn._disable_type_checks = True
        self.assertTrue(self.decorated_function("Wrong type"))

    def test_function_can_be_called_with_positional_args(self):
        self.assertTrue(self.decorated_function(1, list_param=["str"]))

        with self.subTest("Positional args can also be passed as keyword args"):
            self.assertTrue(self.decorated_function(int_param=1, list_param=["str"]))

    def test_check_types_validates_basic_types(self):
        with self.subTest("validates integers"):
            with self.assertRaisesTypeErrorAndContainsParam("int_param"):
                self.decorated_function("Hello")

            self.assertTrue(self.decorated_function(1))

        with self.subTest("validates strings"):
            with self.assertRaisesTypeErrorAndContainsParam("str_param"):
                self.decorated_function(1, 1)

            self.assertTrue(self.decorated_function(1, "Hello"))

        with self.subTest("validates bools"):
            with self.assertRaisesTypeErrorAndContainsParam("bool_param"):
                self.decorated_function(1, "str", "not a bool")

            self.assertTrue(self.decorated_function(1, "Hello", True))

    def test_check_types_validates_named_params(self):
        with self.assertRaisesTypeErrorAndContainsParam("str_param"):
            self.decorated_function(1, str_param=1)

        self.assertTrue(
            self.decorated_function(1, str_param="Hello"),
            "str_param should support str",
        )

    def test_check_types_handles_untyped_params(self):
        self.assertTrue(
            self.decorated_function(1, untyped_param=1, dict_param={"Hello": 1})
        )

        with self.subTest("Still validates other params correctly"):
            with self.assertRaisesTypeErrorAndContainsParam("dict_param"):
                wrong_param = {"Hello": [1], "World": [2]}
                self.decorated_function(
                    1, str_param="Hello", untyped_param=1, dict_param=wrong_param
                )

            with self.assertRaisesTypeErrorAndContainsParam("str_param"):
                wrong_param = 1337
                self.decorated_function(
                    1, str_param=wrong_param, untyped_param=1, dict_param={"Hello": 1}
                )
        with self.subTest("Can handle positional arguments with untyped in between"):
            self.assertTrue(self.decorated_function(1, "Hello", True, 1, ["Hello"]))

    def test_check_types_excludes_params(self):
        exclude = ["int_param"]
        decorated_function = check_types(exclude)(function_to_decorate)

        self.assertTrue(
            decorated_function("str"), "should not validate the excluded parameter"
        )

        with self.subTest("but only excludes the one"):
            with self.assertRaisesTypeErrorAndContainsParam("str_param"):
                decorated_function("str", str_param=1337)

    def test_check_types_handles_lists(self):
        with self.subTest("strings should not be valid lists"):
            with self.assertRaisesTypeErrorAndContainsParam("list_param"):
                self.decorated_function(1, list_param="str")

        with self.subTest("integers should not be valid lists"):
            with self.assertRaisesTypeErrorAndContainsParam("list_param"):
                self.decorated_function(1, list_param=1)

        with self.subTest("Lists of the wrong object should not be valid"):
            with self.assertRaisesTypeErrorAndContainsParam("list_param"):
                self.decorated_function(1, list_param=[1, 2, 3])

        with self.subTest("Lists with mixed objects should not be valid"):
            with self.assertRaisesTypeErrorAndContainsParam("list_param"):
                self.decorated_function(1, list_param=["str", "str", 3])

        with self.subTest("Iterables should not be allowed"):
            with self.assertRaisesTypeErrorAndContainsParam("list_param"):
                self.decorated_function(1, list_param=set(["Hello", "World"]))

        self.assertTrue(
            self.decorated_function(1, list_param=["str"]),
            "list_param should support List[str]",
        )

        self.assertTrue(
            self.decorated_function(1, list_param=[]),
            "list_param should support empty lists",
        )

    def test_check_types_handles_naked_list_parameters(self):
        with self.subTest("strings should not be valid lists"):
            with self.assertRaisesTypeErrorAndContainsParam("naked_list_param"):
                self.decorated_function(1, naked_list_param="str")

        with self.subTest("Lists with mixed objects should be valid"):
            self.assertTrue(
                self.decorated_function(1, naked_list_param=["str", "str", 3]),
            )
        self.assertTrue(
            self.decorated_function(1, naked_list_param=["str"]),
            "naked_list_param should support List[str]",
        )

    def test_check_types_handles_iterables(self):
        with self.subTest("Should support different iterables"):
            self.assertTrue(
                self.decorated_function(1, iterable_param=["str"]),
                "iterable_param should support List[str]",
            )
            self.assertTrue(
                self.decorated_function(1, iterable_param=set(["str"])),
                "iterable_param should support set[str]",
            )
            self.assertTrue(
                self.decorated_function(1, iterable_param={"1": 3, "2": 4}),
                "iterable_param should support Dict[str, Any]",
            )
            self.assertTrue(
                self.decorated_function(1, iterable_param=np.array(["Hello", "World"])),
                "iterable_param should support Dict[str, Any]",
            )
            self.assertTrue(
                self.decorated_function(1, iterable_param=np.array([])),
                "iterable_param should support empty iterables",
            )

        # TODO: Is this always true for us?
        with self.subTest("strings should not be valid iterables"):
            with self.assertRaisesTypeErrorAndContainsParam("iterable_param"):
                self.decorated_function(1, iterable_param="str")

        with self.subTest("integers should not be valid iterables"):
            with self.assertRaisesTypeErrorAndContainsParam("iterable_param"):
                self.decorated_function(1, iterable_param=1)

        with self.subTest("Iterables of the wrong object should not be valid"):
            with self.assertRaisesTypeErrorAndContainsParam("iterable_param"):
                self.decorated_function(1, iterable_param=[1, 2, 3])

        with self.subTest("Iterables with mixed objects should not be valid"):
            with self.assertRaisesTypeErrorAndContainsParam("iterable_param"):
                self.decorated_function(1, iterable_param=["str", "str", 3])

        with self.subTest(
            "While iterable, a feyn model should not be accepted as Iterable(str)"
        ):
            with self.assertRaisesTypeErrorAndContainsParam("iterable_param"):
                self.decorated_function(
                    1, iterable_param=quickmodels.get_unary_model(["x"], "y")
                )

    def test_check_types_handles_qepler_models(self):
        self.assertTrue(
            self.decorated_function(
                1, model_param=quickmodels.get_unary_model(["x"], "y")
            ),
            "feyn models should be allowed",
        )

        with self.subTest("Other types should not be accepted"):
            with self.assertRaisesTypeErrorAndContainsParam("model_param"):
                self.decorated_function(1, model_param=1)

            with self.assertRaisesTypeErrorAndContainsParam("model_param"):
                self.decorated_function(1, model_param="_qepler.Model (1 interactions)")

    def test_check_types_handles_lists_of_qepler_models(self):
        self.assertTrue(
            self.decorated_function(
                1, list_model_param=[quickmodels.get_unary_model(["x"], "y")]
            ),
            "Lists of feyn models should be allowed",
        )

        with self.subTest("Other lists should not be accepted"):
            with self.assertRaisesTypeErrorAndContainsParam("list_model_param"):
                self.decorated_function(1, list_model_param=[1])

            with self.assertRaisesTypeErrorAndContainsParam("list_model_param"):
                self.decorated_function(
                    1, list_model_param=["_qepler.Model (1 interactions)"]
                )

            with self.assertRaisesTypeErrorAndContainsParam("list_model_param"):
                self.decorated_function(
                    1, list_model_param=set([quickmodels.get_unary_model(["x"], "y")])
                )

            with self.assertRaisesTypeErrorAndContainsParam("list_model_param"):
                self.decorated_function(
                    1, list_model_param=quickmodels.get_unary_model(["x"], "y")
                )

    def test_check_types_handles_dictionaries(self):
        self.assertTrue(
            self.decorated_function(1, dict_param={"Hello": 1, "World": 2}),
            "Dict should be allowed",
        )

        self.assertTrue(
            self.decorated_function(1, dict_param={}),
            "Empty dict should be allowed",
        )

        with self.subTest("But should react to bad types in the dict"):
            with self.assertRaisesTypeErrorAndContainsParam("dict_param"):
                self.decorated_function(1, dict_param={"Hello": "1", "World": 2})

            with self.assertRaisesTypeErrorAndContainsParam("dict_param"):
                self.decorated_function(1, dict_param={"Hello": [1], "World": [2]})

            with self.assertRaisesTypeErrorAndContainsParam("dict_param"):
                self.decorated_function(1, dict_param={"Hello": 1, "World": [2]})

    def test_check_types_handles_unions(self):
        self.assertTrue(self.decorated_function(1, union_param="Hello"))
        self.assertTrue(self.decorated_function(1, union_param=["Hello"]))

        with self.subTest("Doesn't accept List of ints"):
            with self.assertRaisesTypeErrorAndContainsParam("union_param"):
                self.decorated_function(1, union_param=[1, 2])

        with self.subTest("Doesn't accept mixed type Lists"):
            with self.assertRaisesTypeErrorAndContainsParam("union_param"):
                self.decorated_function(1, union_param=[1, "2"])
            with self.assertRaisesTypeErrorAndContainsParam("union_param"):
                self.decorated_function(1, union_param=["1", 2])

        with self.subTest("Doesn't accept types not in union"):
            with self.assertRaisesTypeErrorAndContainsParam("union_param"):
                self.decorated_function(1, union_param=1)

        self.assertTrue(self.decorated_function(1, union_param=["1", "2"]))

    def test_check_types_handles_dictionaries_with_union_values(self):
        self.assertTrue(
            self.decorated_function(
                1, dict_with_union_param={"Hello": 1, "World": 2.0, "Other": "Value"}
            ),
            "Dict should be allowed",
        )

        self.assertTrue(
            self.decorated_function(1, dict_with_union_param={}),
            "Empty dict should be allowed",
        )

        with self.subTest("But should react to bad types in the dict"):
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_union_param"):
                self.decorated_function(
                    1, dict_with_union_param={"Hello": [1], "World": [2]}
                )

            with self.assertRaisesTypeErrorAndContainsParam("dict_with_union_param"):
                self.decorated_function(
                    1, dict_with_union_param={"Hello": 1, "World": [2]}
                )

    def test_check_types_handles_any_params(self):
        self.assertTrue(
            self.decorated_function(1, any_param="Hello"),
            "Anything goes",
        )
        self.assertTrue(
            self.decorated_function(1, any_param=1),
            "Anything goes",
        )
        self.assertTrue(
            self.decorated_function(1, any_param=[1]),
            "Anything goes",
        )
        self.assertTrue(
            self.decorated_function(1, any_param=np.int_(1)),
            "Anything goes",
        )

    def test_check_types_handles_nested_any_params(self):
        self.assertTrue(
            self.decorated_function(1, nested_any_param={"Hello": 1}),
            "Anything goes",
        )
        self.assertTrue(
            self.decorated_function(1, nested_any_param={"Hello": "World"}),
            "Anything goes",
        )
        self.assertTrue(
            self.decorated_function(1, nested_any_param={"Hello": [1]}),
            "Anything goes",
        )
        self.assertTrue(
            self.decorated_function(1, nested_any_param={"Hello": np.int_(1)}),
            "Anything goes",
        )

        with self.subTest("But not for the parts that are strict"):
            with self.assertRaisesTypeErrorAndContainsParam("nested_any_param"):
                self.decorated_function(1, nested_any_param={1: np.int_(1)})

    def test_check_types_handles_optional_params(self):
        self.assertTrue(self.decorated_function(1, opt_param="Hello"))
        self.assertTrue(self.decorated_function(1, opt_param=None))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("opt_param"):
                self.decorated_function(1, opt_param=1337)

    def test_check_types_handles_optional_iterable_params(self):
        self.assertTrue(self.decorated_function(1, opt_iterable_param=["Hello"]))
        self.assertTrue(self.decorated_function(1, opt_iterable_param=None))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("opt_iterable_param"):
                self.decorated_function(1, opt_iterable_param=1337)

    def test_check_types_handles_optional_dict_params(self):
        self.assertTrue(self.decorated_function(1, opt_dict_param={"Hello": "World"}))
        self.assertTrue(self.decorated_function(1, opt_dict_param=None))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("opt_dict_param"):
                self.decorated_function(1, opt_dict_param=1337)

    def test_check_types_handles_nested_optional_params(self):
        self.assertTrue(self.decorated_function(1, nested_opt_param=["Hello"]))
        self.assertTrue(self.decorated_function(1, nested_opt_param=None))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("nested_opt_param"):
                self.decorated_function(1, nested_opt_param=1337)
            with self.assertRaisesTypeErrorAndContainsParam("nested_opt_param"):
                self.decorated_function(1, nested_opt_param=[1337])

    def test_check_types_handles_nested_union_optional_params(self):
        self.assertTrue(self.decorated_function(1, nested_union_opt_param=["Hello"]))
        self.assertTrue(self.decorated_function(1, nested_union_opt_param="Hello"))
        self.assertTrue(self.decorated_function(1, nested_union_opt_param=None))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("nested_union_opt_param"):
                self.decorated_function(1, nested_union_opt_param=1337)
            with self.assertRaisesTypeErrorAndContainsParam("nested_union_opt_param"):
                self.decorated_function(1, nested_union_opt_param=[1337])

    def test_check_types_can_handle_dataframes(self):
        self.assertTrue(self.decorated_function(1, pd_dataframe_param=pd.DataFrame()))
        self.assertTrue(self.decorated_function(1, dataframe_param=pd.DataFrame()))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("pd_dataframe_param"):
                self.decorated_function(1, pd_dataframe_param=1337)
            with self.assertRaisesTypeErrorAndContainsParam("dataframe_param"):
                self.decorated_function(1, dataframe_param=1337)
            with self.assertRaisesTypeErrorAndContainsParam("dataframe_param"):
                data = {"a": np.array([1, 2, 3]), "target": np.array([0, 1, 1])}
                self.decorated_function(1, dataframe_param=data)

    def test_check_types_can_handle_callables(self):
        def some_func(param: str) -> bool:
            pass

        def untyped_func(param):
            pass

        self.assertTrue(self.decorated_function(1, callable_param=lambda x: x))
        self.assertTrue(self.decorated_function(1, callable_param=some_func))
        self.assertTrue(
            self.decorated_function(1, typed_callable_param=lambda x: x),
            "The typed callable_params are actually not evaluated or enforced",
        )
        self.assertTrue(
            self.decorated_function(1, typed_callable_param=untyped_func),
            "The typed callable_params are actually not evaluated or enforced",
        )

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("callable_param"):
                self.decorated_function(1, callable_param=1337)
            with self.assertRaisesTypeErrorAndContainsParam("typed_callable_param"):
                self.decorated_function(1, typed_callable_param=1337)

            with self.assertRaisesTypeErrorAndContainsParam("callable_param"):
                self.decorated_function(1, callable_param="some string")
            with self.assertRaisesTypeErrorAndContainsParam("typed_callable_param"):
                self.decorated_function(1, typed_callable_param="some string")

    def test_check_types_handles_nested_iterables(self):
        pass

    def test_check_types_dict_with_list(self):
        self.assertTrue(self.decorated_function(1, dict_with_list={1: [1, 2]}))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_list"):
                self.decorated_function(1, dict_with_list={1: "not_list"})
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_list"):
                self.decorated_function(1, dict_with_list={1: 42})
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_list"):
                self.decorated_function(1, dict_with_list={1: [1, "not_right_type"]})
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_list"):
                self.decorated_function(
                    1, dict_with_list={1: set([1, "not_right_type"])}
                )

    def test_check_types_dict_with_iterable(self):
        self.assertTrue(self.decorated_function(1, dict_with_iterable={1: [1, 2]}))

        with self.subTest("Doesn't accept bad types"):
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_iterable"):
                self.decorated_function(1, dict_with_iterable={1: "not_iterable"})
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_iterable"):
                self.decorated_function(1, dict_with_iterable={1: 42})
            with self.assertRaisesTypeErrorAndContainsParam("dict_with_iterable"):
                self.decorated_function(
                    1, dict_with_iterable={1: [1, "not_right_type"]}
                )
