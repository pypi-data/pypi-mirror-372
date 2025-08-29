"""A collection of filters to use with feyn Models."""

from typing import List, Union

import feyn


class Complexity:
    """Use this class to get a filter for selecting models with a specific complexity."""

    def __init__(self, complexity: int):
        self.complexity = int(complexity)

    def __call__(self, model: feyn.Model) -> bool:
        return model.edge_count == self.complexity


class ContainsInputs:
    """Use this class to get a filter for including only models that contain specific named inputs."""

    def __init__(self, input_name: Union[str, List[str]]):
        if isinstance(input_name, str):
            input_name = [input_name]

        self.names = input_name

    def __call__(self, model: feyn.Model) -> bool:
        return all(name in model.inputs for name in self.names)


class ExcludeFunctions:
    """Use this class to get a filter for excluding models that contain any of the named functions.
    Providing the name of the function is sufficient. If arity is additionally provided for any function (eg. 'gaussian:2'), all functions must have their arity provided to avoid ambiguity.
    """

    def __init__(self, functions: Union[str, List[str]]):
        if isinstance(functions, str):
            functions = [functions]

        # Use the arity-defined function names if all the passed functions contain arity
        func_contains_arity = [len(f.split(":")) == 2 for f in functions]
        self.use_arity = all(func_contains_arity)

        if not self.use_arity:
            if any(func_contains_arity):
                # If only some are provided, raise
                raise ValueError(
                    "If providing an arity for the function, all functions must have provided arity"
                )

        self.functions = functions

    def __call__(self, model: feyn.Model) -> bool:
        for e in model:
            func = e.fname
            if not self.use_arity:
                # Remove arities for comparison if not provided
                func = e.fname.split(":")[0]

            if func in self.functions:
                return False

        return True


class ContainsFunctions:
    """Use this class to get a filter for including only models that exclusively consist of the named functions.
    Providing the name of the function is sufficient. If arity is additionally provided for any function (eg. 'gaussian:2'), all functions must have their arity provided to avoid ambiguity.
    """

    def __init__(self, functions: Union[str, List[str]]):
        if isinstance(functions, str):
            functions = [functions]

        # Use the arity-defined function names if all the passed functions contain arity
        func_contains_arity = [len(f.split(":")) == 2 for f in functions]
        self.use_arity = all(func_contains_arity)

        if not self.use_arity:
            if any(func_contains_arity):
                # If only some are provided, raise
                raise ValueError(
                    "If providing an arity for the function, all functions must have provided arity"
                )

        self.functions = functions

    def __call__(self, model: feyn.Model) -> bool:
        used_functions = [e.fname for e in model if e.name == ""]
        if not self.use_arity:
            # Remove arities for comparison if not provided
            used_functions = [f.split(":")[0] for f in used_functions]

        return used_functions == self.functions
