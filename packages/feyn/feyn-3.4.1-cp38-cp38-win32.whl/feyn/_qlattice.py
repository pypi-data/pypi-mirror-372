"""Classes and functions to interact with a remote QLattice."""

from typing import Dict, List, Optional, Iterable, Union
import random

import numpy as np
import pandas as pd
from lark.exceptions import UnexpectedInput
import logging

import feyn
import _qepler
from feyn import Model
from feyn._typings import check_types

from ._ql_notebook_mixin import QLatticeNotebookMixin
from ._compatibility import detect_notebook

from ._basealgo import BaseAlgorithm
from ._program import Program
from ._query import Query


class QLattice(QLatticeNotebookMixin if detect_notebook() else object):
    def __init__(self, random_seed: int = -1):
        """Construct a new 'QLattice' object."""
        self._basealgo = BaseAlgorithm()
        self._random_seed = random_seed

        if random_seed != -1:
            random.seed(random_seed)
            np.random.seed(random_seed)
            _qepler.srand(random_seed)

    @check_types()
    def update(self, models: Iterable[Model]):
        """Update QLattice with learnings from a list of models. When updated, the QLattice learns to produce models that are similar to what is included in the update. Without updating, the QLattice will keep generating models with a random structure.

        Arguments:
            models {Union[Model, Iterable[Model]]} -- The models to use in a QLattice update.

        Raises:
            TypeError: if inputs don't match the correct type.
        """

        self._basealgo.update(models)

    @check_types()
    def sample_models(
        self,
        input_names: Iterable[str],
        output_name: str,
        kind: str = "auto",
        stypes: Optional[Dict[str, str]] = None,
        max_complexity: int = 10,
        query_string: Optional[str] = None,
        function_names: Optional[List[str]] = None,
    ) -> List[feyn.Model]:
        """
        Sample models from the QLattice simulator. The QLattice has a probability density for generating different models, and this function samples from that density.

        Arguments:
            input_names {List[str]} -- The names of the inputs.
            output_name {str} -- The name of the output.

        Keyword Arguments:
            kind {str} -- Specify the kind of models that are sampled. One of ["auto", "classification", "regression"]. If "auto" and no stype is given for the output, it defaults to "regression". (default: {"auto"})
            stypes {Optional[Dict[str, str]]} -- An optional map from input names to semantic types. (default: {None})
            max_complexity {int} -- The maximum complexity for sampled models. Currently the maximum number of edges that the graph representation of the models has. (default: {10})
            query_string {Optional[str]} -- An optional query string for specifying specific model structures. (default: {None})
            function_names {Optional[List[str]]} -- A list of function names to use in the QLattice simulation. Defaults to all available functions being used. (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: if input_names contains duplicates.
            ValueError: if max_complexity is negative.
            ValueError: if kind is not a regressor or classifier.
            ValueError: if function_names is not recognised.
            ValueError: if query_string is invalid.

        Returns:
            List[Model] -- The list of sampled models.
        """
        if len(input_names) == 0:
            raise ValueError("input_names cannot be empty.")
        if len(list(input_names)) != len(set(input_names)):
            raise ValueError("input_names must consist of only unique values.")
        if max_complexity <= 0:
            raise ValueError(
                f"max_complexity must be greater than 0, but was {max_complexity}."
            )
        for name in input_names:
            if ":" in name:
                raise ValueError(
                    f"Input names with a colon ':' are not allowed, please rename '{name}'."
                )
        max_complexity = min(max_complexity, Program.SIZE - 1)

        stypes = stypes or {}
        stypes[output_name] = feyn.tools.infer_output_stype(kind, output_name, stypes)

        # "skip" is a meta stype not supported during training, so we want to remove the inputs if they exist and remove the stypes from the stypes dict.
        input_names, stypes = feyn.tools._data.remove_skipped_inputs(
            input_names, stypes
        )

        if output_name in input_names:
            input_names = list(input_names)
            input_names.remove(output_name)

        function_names = _get_fnames(function_names)

        res = []

        query_string = query_string or "_"
        try:
            query = Query(
                query_string, max_complexity, input_names, function_names, output_name
            )
        except UnexpectedInput as ui:
            query_mistake = ui.get_context(query_string)
            mistake_here = (
                " " * ui.pos_in_stream + "This is where something went wrong!"
            )
            raise ValueError(
                f"\nFailed to parse the following query string:\n\n{query_mistake + mistake_here}\n\nYou can read more about using the query language here:\nhttps://docs.abzu.ai/docs/guides/advanced/query_language.html\n"
            ) from None

        programs = self._basealgo.generate_programs(query)

        for p in programs:
            model = p.to_model(stypes)
            if model is None:
                # Silently ignore invalid programs
                continue

            if any([i not in input_names for i in model.inputs]):
                # Silently ignore models that have inputs not provided in the data due to user changing inputs. The next epoch will have a fresh state.
                continue

            res.append(model)

        return res

    def reset(self, random_seed=-1):
        """Deprecated. Create a new QLattice with the constructor instead.
        Clear all learnings in this QLattice.

        Keyword Arguments:
            random_seed {int} -- If not -1, seed the qlattice and feyn random number generator to get reproducible results. (default: {-1})
        """

        if random_seed != -1:
            random.seed(random_seed)
            np.random.seed(random_seed)
            _qepler.srand(random_seed)

        self._basealgo = BaseAlgorithm()

        log = logging.getLogger(__name__)
        log.warning(
            "Deprecation: The reset() function is deprecated. Instantiating a new feyn.QLattice() now achieves the same result."
        )

    def update_priors(self, priors: Dict, reset: bool = True):
        """Update input priors for the QLattice

        Keyword Arguments:
            priors - a dictionary of prior probabilities of each input to impact the output.
            reset - a boolean determining whether to reset the current priors, or merge with the existing priors.
        """
        priors = list(priors.items())

        self._basealgo.update_priors(priors, reset)

    @check_types()
    def auto_run(
        self,
        data: pd.DataFrame,
        output_name: str,
        kind: str = "auto",
        stypes: Optional[Dict[str, str]] = None,
        n_epochs: int = 10,
        threads: Union[int, str] = "auto",
        max_complexity: int = 10,
        query_string: Optional[str] = None,
        loss_function: Optional[str] = None,
        criterion: Optional[str] = "bic",
        sample_weights: Optional[Iterable[float]] = None,
        function_names: Optional[List[str]] = None,
        starting_models: Optional[List[feyn.Model]] = None,
    ) -> List[feyn.Model]:
        """A convenience function for running the QLattice simulator for many epochs. This process can be interrupted with a KeyboardInterrupt, and you will get back the best models that have been found thus far. Roughly equivalent to the following:

        >>> priors = feyn.tools.estimate_priors(data, output_name)
        >>> ql.update_priors(priors)
        >>> models = []
        >>> for i in range(n_epochs):
        >>>     models += ql.sample_models(data, output_name, kind, stypes, max_complexity, query_string, function_names)
        >>>     models = feyn.fit_models(models, data, loss_function, criterion, None, sample_weights)
        >>>     models = feyn.prune_models(models)
        >>>     ql.update(models)
        >>> best = feyn.get_diverse_models(models, n=10)

        Arguments:
            data {Iterable} -- The data to train models on. Input names are inferred from the columns (pd.DataFrame) or keys (dict) of this variable.
            output_name {str} -- The name of the output.

        Keyword Arguments:
            kind {str} -- Specify the kind of models that are sampled. One of ["auto", "classification", "regression"]. If "auto" is chosen, it will default to "regression" unless the output_name is assigned stype "b", in which case it becomes "classification". (default: {"auto"})
            stypes {Optional[Dict[str, str]]} -- An optional map from input names to semantic types. If None, it will automatically infer the stypes based on the data. (default: {None})
            n_epochs {int} -- Number of training epochs. (default: {10})
            threads {int} -- Number of concurrent threads to use for fitting. If a number, that many threads are used. If "auto", set to your CPU count - 1. (default: {"auto"})
            max_complexity {int} -- The maximum complexity for sampled models. (default: {10})
            query_string {Optional[str]} -- An optional query string for specifying specific model structures. (default: {None})
            loss_function {Optional[Union[str, Callable]]} -- The loss function to optimize models for. If None (default), 'MSE' is chosen for regression problems and 'binary_cross_entropy' for classification problems. (default: {None})
            criterion {Optional[str]} -- Sort by information criterion rather than loss. Either "aic", "bic" or None (loss). (default: {"bic"})
            sample_weights {Optional[Iterable[float]]} -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample. (default: {None})
            function_names {Optional[List[str]]} -- A list of function names to use in the QLattice simulation. Defaults to all available functions being used. (default: {None})
            starting_models {Optional[List[feyn.Model]]} -- A list of preexisting feyn models you would like to start finding better models from. The inputs and output of these models should match the other arguments to this function. (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.

        Returns:
            List[feyn.Model] -- The best models found during this run.
        """
        from time import time

        warnings = []
        # Use experimental stype inferral if stypes are not defined
        if not stypes:
            stypes, warnings = feyn.tools.infer_stypes(
                data, output_name, capture_warnings=True
            )
        display_stype_warnings = feyn.tools._data.log_type_warnings(warnings)

        feyn.validate_data(data, kind, output_name, stypes)

        if n_epochs <= 0:
            raise ValueError("n_epochs must be 1 or higher.")

        if threads == "auto":
            threads = feyn.tools.infer_available_threads()
        elif isinstance(threads, str):
            raise ValueError("threads must be a number, or string 'auto'.")

        models = []
        if starting_models is not None:
            models = [m.copy() for m in starting_models]
        m_count = len(models)

        priors = feyn.tools.estimate_priors(data, output_name)
        self.update_priors(priors)

        try:
            start = time()
            for epoch in range(1, n_epochs + 1):
                new_sample = self.sample_models(
                    data,
                    output_name,
                    kind,
                    stypes,
                    max_complexity,
                    query_string,
                    function_names,
                )
                models += new_sample
                m_count += len(new_sample)

                models = feyn.fit_models(
                    models,
                    data=data,
                    loss_function=loss_function,
                    criterion=criterion,
                    n_samples=None,
                    sample_weights=sample_weights,
                    threads=threads,
                )
                models = feyn.prune_models(models)
                elapsed = time() - start

                if len(models) > 0:
                    display_stype_warnings()
                    feyn.show_model(
                        models[0],
                        feyn.tools.get_progress_label(
                            epoch, n_epochs, elapsed, m_count
                        ),
                        update_display=True,
                    )

                self.update(models)

            best = feyn.get_diverse_models(models)
            return best

        except KeyboardInterrupt:
            best = feyn.get_diverse_models(models)
            return best


def connect_qlattice(server=None, qlattice=None, api_token=None) -> QLattice:
    """
    Deprecated. Use feyn.QLattice() instead.
    Utility function for connecting to a QLattice. A QLattice (short for Quantum Lattice) is a device which can be used to generate and explore a vast number of models linking a set of input observations to an output prediction. The actual QLattice runs on a dedicated computing cluster which is operated by Abzu. The `feyn.QLattice` class provides a client interface to communicate with, sample models from, and update the QLattice.

    Returns:
        QLattice -- The QLattice
    """

    log = logging.getLogger(__name__)
    log.warning(
        "Deprecation: The connect_qlattice() is deprecated. Use the `feyn.QLattice()` constructor instead."
    )

    return QLattice()


def _get_fnames(fnames: Optional[List[str]]):
    all_fnames = feyn.FNAMES

    if not fnames:
        return all_fnames

    function_names = []
    for name in fnames:
        if name == "gaussian":
            function_names.append("gaussian:1")
            function_names.append("gaussian:2")
        elif name in ["add", "multiply"]:
            function_names.append(name + ":2")
        elif name in ["log", "exp", "sqrt", "linear", "squared", "inverse", "tanh"]:
            function_names.append(name + ":1")
        else:
            raise ValueError(f"{name} is not a valid function name.")

    return function_names


# Magic signature population
if hasattr(QLattice, "expand_auto_run"):
    QLattice.expand_auto_run.__annotations__ = QLattice.auto_run.__annotations__
    QLattice.expand_auto_run.__annotations__["return"] = "IPython cell"
    QLattice.expand_auto_run.__wrapped__ = QLattice.auto_run
