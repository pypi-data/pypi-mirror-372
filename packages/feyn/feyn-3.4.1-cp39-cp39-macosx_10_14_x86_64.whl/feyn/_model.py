"""Class for a feyn Model. A feyn Model is a composition of mathematical functions from some input features to an output."""

import json
import logging
from pathlib import Path
from typing import AnyStr, TextIO, Union, Optional, List
from unicodedata import name
from pandas import DataFrame
import numpy as np

import feyn
from ._program import Program
from ._base_reporting_mixin import BaseReportingMixin
from ._plots_mixin import PlotsMixin
from ._interactivemixin import InteractiveMixin
from ._compatibility import supports_interactivity
from ._functions import MIGRATION_CODES_TO_FNAME_MAP, MIGRATION_FNAME_TO_FNAME_MAP

# Update this number whenever there are breaking changes to save/load
# Then use it intelligently in Model.load.
SCHEMA_VERSION = "2022-06-30"

PathLike = Union[AnyStr, Path]


class Element:
    def __init__(self, model: "Model", ix: int) -> None:
        self._model = model
        self._ix = ix

    @property
    def fname(self):
        return self._model.fnames[self._ix]

    @property
    def name(self):
        return self._model.names[self._ix]

    @property
    def params(self):
        return self._model.params[self._ix]

    @property
    def tooltip(self):
        # TODO: element tooltips - validate KEvin did a good job
        if self.fname == "in-linear:0" or self.fname == "out-linear:1":
            return f"{self.name}\nlinear:\nscale={self.params['scale']:6f}\nscale offset={self.params['scale_offset']:6f}\nw={self.params['w']:.6f}\nbias={self.params['bias']:.4f}"
        elif self.fname == "linear":
            return f"linear:\nw={self.params['w']:.6f}\nbias={self.params['bias']:.4f}"
        elif self.fname == "out-lr:1":
            return f"{self.name}\nlogistic:\nw={self.params['w']:.4f}\nbias={self.params['bias']:.4f}"
        elif self.fname == "in-cat:0":
            return (
                f"{self.name}\ncategorical with {len(self.params['categories'])} values\nbias={self.params['bias']:.4f}"
            )
        else:
            return self.fname.split(":")[0]

    @property
    def arity(self):
        return int(self.fname.split(":")[1])

    @property
    def children(self):
        if self.arity == 0:
            return []

        if self.arity == 1:
            return [self._ix + 1]

        if self.arity == 2:
            first_child_ix = self._ix + 1
            second_child_ix = self._model.find_end(first_child_ix)

            return [first_child_ix, second_child_ix]

        raise ValueError("Internal error")


def parameter_completion(params, fnames):
    if params is None:
        params = [{} for _ in fnames]

    if len(fnames) != len(params):
        raise ValueError("length of 'params' does not match program")

    for ix, fname in enumerate(fnames):
        p = params[ix]
        if fname in {"linear:1", "out-lr:1"}:
            if "w" not in p:
                p["w"] = np.random.rand() * 4 - 2
            if "bias" not in p:
                p["bias"] = np.random.rand() * 4 - 2
        elif fname == "in-linear:0":
            if "scale" not in p:
                p["scale"] = 1.0
            if "scale_offset" not in p:
                p["scale_offset"] = 0.0
            if "w" not in p:
                p["w"] = np.random.rand() * 4 - 2
            if "bias" not in p:
                p["bias"] = np.random.rand() * 4 - 2
        elif fname == "out-linear:1":
            if "scale" not in p:
                p["scale"] = 1.0
            if "scale_offset" not in p:
                p["scale_offset"] = 0.0
            if "w" not in p:
                p["w"] = np.random.rand() * 4 - 2
            if "bias" not in p:
                p["bias"] = 0
        elif fname == "in-cat:0":
            if "categories" not in p:
                p["categories"] = []
            if "bias" not in p:
                p["bias"] = 0

    return params


class Model(
    BaseReportingMixin,
    PlotsMixin,
    InteractiveMixin if supports_interactivity() else object,
):
    """
    A Model represents a single mathematical equation which can be used for predicting.

    The constructor is for internal use.
    """

    def __init__(self, program, fnames, params=None):
        proglen = len(program)

        if proglen != len(fnames):
            raise ValueError("length of 'fnames' does not match program")

        invalid_fnames = set(fnames).difference(feyn.FNAME_MAP.keys())
        if invalid_fnames:
            raise ValueError("Invalid fnames: %r" % invalid_fnames)

        self.loss_values: List[float] = []
        self.loss_value: Union[float, None] = None
        self.age = 0

        self._program = program
        self.names = [code if ":" not in code else "" for code in program]

        self.fnames = fnames

        self.params = parameter_completion(params, fnames)

        self._sample_count = 0

        self._elements = [Element(self, ix) for ix in range(len(self.fnames))]

    @property
    def _paramcount(self):
        res = 0
        for ix, fname in enumerate(self.fnames):
            if fname == "in-cat:0":
                res += len(self.params[ix]["categories"]) - 1
            else:
                res += feyn.FNAME_MAP[fname]["paramcount"]

        return res

    def predict(self, X: DataFrame) -> np.ndarray:
        """
        Calculate predictions based on input values. Note that for classification tasks the output are probabilities.

        >>> model.predict({ "age": [34, 78], "sex": ["male", "female"] })
        [0.85, 0.21]

        Arguments:
            X {DataFrame} -- The input values as a pandas.DataFrame.

        Returns:
            np.ndarray -- The calculated predictions.
        """
        activations = self._get_activations(X, protected=True)
        return activations[0]

    def _get_activations(self, X: DataFrame, protected=True) -> np.ndarray:
        """
        Calculate predictions based on input values. Note that for classification tasks the output are probabilities.

        >>> model.predict({ "age": [34, 78], "sex": ["male", "female"] })
        [0.85, 0.21]

        Arguments:
            X {DataFrame} -- The input values as a pandas.DataFrame.

        Returns:
            np.ndarray -- The calculated predictions.
        """
        if type(X).__name__ == "dict":
            for k in X:
                if type(X[k]).__name__ == "list":
                    X[k] = np.array(X[k])

        # Magic support for pandas Series
        if type(X).__name__ == "Series":
            X = {idx: np.array([X[idx]]) for idx in X.index}

        # Magic support for pandas DataFrame
        if type(X).__name__ == "DataFrame":
            X = {col: X[col].values for col in X.columns}

        func_key = "func_protected" if protected else "func"

        activations = [None] * len(self)
        for ix in reversed(range(len(self))):
            elem = self[ix]

            fdict = feyn.FNAME_MAP[elem.fname]
            if func_key in fdict:
                func = fdict[func_key]
            else:
                func = fdict["func"]

            if elem.name and ix != 0:
                activations[ix] = func(elem.params, X[elem.name])
            else:
                children = elem.children
                if elem.arity == 1:
                    activations[ix] = func(elem.params, activations[children[0]])

                else:
                    activations[ix] = func(elem.params, activations[children[0]], activations[children[1]])

        return np.array(activations)

    @property
    def edge_count(self) -> int:
        """Get the total number of edges in the graph representation of this model."""
        return len(self.fnames) - 1

    @property
    def depth(self) -> int:
        """Get the depth of the graph representation of the model. In general, it is better to evaluate the complexity of models using the edge_count (or max_complexity) properties"""
        return max(self.depths())

    def find_end(self, ix: int) -> int:
        l = 1
        while True:
            a = self[ix].arity
            l += a - 1
            ix += 1

            if l == 0:
                return ix

    def depths(self) -> List[int]:
        """Get the depths of each element in the program."""
        res = [-1] * len(self)

        # By convention the root of the program is at depth 1.
        # This leaves space for an output node at depth 0
        res[0] = 0
        for ix, _ in enumerate(self):
            arity = self[ix].arity
            d = res[ix]
            if arity >= 1:
                res[ix + 1] = d + 1
            if arity == 2:
                c2 = self.find_end(ix + 1)
                res[c2] = d + 1
        return res

    @property
    def output(self) -> str:
        """Get the name of the output node."""
        return self.names[0]

    @property
    def target(self) -> str:
        """Get the name of the output node. Does the same as 'output'"""
        return self.output

    @property
    def features(self):
        """Get the name of the input features of the model. Does the same as 'inputs'"""
        return self.inputs

    @property
    def inputs(self):
        """Get the name of the input features of the model."""
        return sorted(list(set([name for name in self.names[1:] if name != ""])))

    @property
    def kind(self):
        return "classification" if self[0].fname == "out-lr:1" else "regression"

    def save(self, file: Union[PathLike, TextIO]) -> None:
        """
        Save the `Model` to a file-like object.

        The file can later be used to recreate the `Model` with `Model.load`.

        Arguments:
            file -- A file-like object or path to save the model to.
        """

        as_dict = {
            "program": self._program.to_json(),
            "params": self.params,
            "fnames": self.fnames,
        }

        as_dict["version"] = SCHEMA_VERSION

        if isinstance(file, (str, bytes, Path)):
            with open(file, mode="w") as f:
                json.dump(as_dict, f)
        else:
            json.dump(as_dict, file)

    @staticmethod
    def load_old_model_version(serialized_model: dict) -> "Model":
        new_codes = []
        new_fnames = []
        for ix, name in enumerate(serialized_model["names"]):
            code = serialized_model["program"]["codes"][ix]
            fname = serialized_model["fnames"][ix]
            if code // 10000:
                new_fnames.append(MIGRATION_FNAME_TO_FNAME_MAP[fname])
                new_codes.append(name)
            else:
                new_codes.append(MIGRATION_CODES_TO_FNAME_MAP[code])
                new_fnames.append(MIGRATION_CODES_TO_FNAME_MAP[code])

        program = Program.from_json(
            {"codes": new_codes, "qid": serialized_model["program"]["qid"], "data": serialized_model["program"]["data"]}
        )

        return Model(program, new_fnames, serialized_model["params"])

    @staticmethod
    def is_old_model_version(serialized_model: dict) -> bool:
        first_code = serialized_model["program"]["codes"][0]
        if isinstance(first_code, int):
            return True
        return False

    @staticmethod
    def load(file: Union[PathLike, TextIO]) -> "Model":
        """
        Load a `Model` from a file.

        Usually used together with `Model.save`.

        Arguments:
            file -- A file-like object or a path to load the `Model` from.

        Returns:
            Model -- The loaded `Model`-object.
        """
        if isinstance(file, (str, bytes, Path)):
            with open(file, mode="r") as f:
                as_dict = json.load(f)
        else:
            as_dict = json.load(file)

        if Model.is_old_model_version(as_dict):
            log = logging.getLogger(__name__)
            log.warning(
                "Deprecation: Your model is serialized with an old version of Feyn. Save the model again to get the updated serialization. Future versions will not load this file."
            )
            return Model.load_old_model_version(as_dict)

        return Model(
            Program.from_json(as_dict["program"]),
            as_dict["fnames"],
            as_dict["params"],
        )

    def __hash__(self):
        return hash(self._program)

    def __eq__(self, other):
        return other.__hash__() == self.__hash__()

    def __len__(self):
        return len(self.names)

    def __iter__(self):
        return iter(self._elements)

    def __getitem__(self, ix):
        return self._elements[ix]

    def fit(self, data: DataFrame, loss_function="squared_error", sample_weights=None, n_samples=20000):
        """
        Fit this specific `Model` with the given data set.

        Arguments:
            data -- Training data including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.
            loss_function -- Name of the loss function or the function itself. This is the loss function to use for fitting. Can either be a string or one of the functions provided in `feyn.losses`.
            sample_weights -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample

        """
        feyn.fit_models([self], data, loss_function, sample_weights=sample_weights, n_samples=n_samples)

    def _repr_svg_(self):
        return feyn._current_renderer(self)

    def _repr_html_(self):
        return feyn._current_renderer(self)

    def savefig(self, filename: str) -> str:
        """Save model as an svg file.

        Args:
            filename (str): the filename of the file to save. Includes the filepath and file extension.

        """
        from .tools._display import SVG
        svg = SVG(self._repr_svg_())
        
        return svg.save(filename)

    def sympify(self, signif: int = 6, symbolic_lr=False, symbolic_cat=True, include_weights=True):
        """
        Convert the model to a sympy expression.
        This function requires sympy to be installed.

        Arguments:
            signif -- the number of significant digits in the parameters of the model
            symbolic_lr -- express logistic regression wrapper as part of the expression

        Returns:
            expression -- a sympy expression

        """
        return feyn.tools.sympify_model(
            self, signif=signif, symbolic_lr=symbolic_lr, symbolic_cat=symbolic_cat, include_weights=include_weights
        )

    def copy(self) -> "Model":
        """Return a copy of self."""
        return Model(self._program.copy(), list(self.fnames), params=list(self.params))

    def show(
        self,
        label: Optional[str] = None,
        update_display: bool = False,
        filename: Optional[str] = None,
    ):
        """Updates the display in a python notebook with the graph representation of a model

        Keyword Arguments:
            label {Optional[str]} -- A label to add to the rendering of the model (default is None).
            update_display {bool} -- Clear output and rerender figure (defaults to False).
            filename {Optional[str]} -- The filename to use for saving the plot as html (defaults to None).
        """
        feyn._svgrenderer.show_model(self, label, update_display, filename)

    def get_parameters(self, name: str):
        """Given a model and the name of one of its input or output nodes,
        get a pandas.DataFrame with the associated parameters. If the node
        is categorical, the function returns the weight associated with each categorical
        value. If the node is numerical, the function returns the scale, weight and
        bias.

        Arguments:
            name {str} -- Name of the input or output of interest.

        Returns:
            pd.DataFrame -- DataFrame with the parameters.
        """
        return feyn.tools.get_model_parameters(self, name=name)

    def to_query_string(self):
        """Returns the query string representation for the given model."""
        model_elems = [elem for elem in self]

        def _element_query_string(elem):
            if elem.arity == 0:
                return f'"{elem.name}"'
            elif elem.arity == 1:
                child = model_elems[elem.children[0]]
                child_string = _element_query_string(child)

                return f"{elem.fname}({child_string})"
            elif elem.arity == 2:
                child0 = model_elems[elem.children[0]]
                child1 = model_elems[elem.children[1]]

                child_string0 = _element_query_string(child0)
                child_string1 = _element_query_string(child1)

                return f"{elem.fname}({child_string0}, {child_string1})"
            else:
                raise ValueError("Element arity not recognized.")

        query_string = _element_query_string(self[1]).replace(":1", "").replace(":2", "")
        return query_string
