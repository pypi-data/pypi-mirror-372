from pandas import DataFrame
import logging


class QLatticeNotebookMixin:
    def expand_auto_run(self, *args, **kwargs):
        """Expand the auto_run function into a jupyter notebook cell.
        Takes the same signature as `ql.auto_run` to automatically populate parameters.

        Note: This is experimental, and will inspect the locals to try to guess the passed arguments.
        This might result in it latching onto an unrelated variable that happens to have the same value, so always sanity check your parameters.
        """
        cell_contents = self._auto_run_decomposition_inner(*args, **kwargs)
        _create_new_cell("".join(cell_contents))
        logging.getLogger(__name__).info(f"Created cell with auto_run template.")

    def _auto_run_decomposition_inner(self, *args, **kwargs):
        import inspect

        # Go back twice because this function expects to be wrapped
        frame = inspect.currentframe().f_back.f_back

        source_lines = inspect.getsourcelines(self.auto_run)[0]

        imports = ["# Dependencies\n", "import feyn\n", "\n"]
        extension_behaviour = []

        source_args = []
        auto_run_code = ["# auto_run code expansion:\n"]
        skip = True
        docstring_count = 0
        for line in source_lines:
            # Ignore function header
            if "@check_types" in line:
                continue
            if "def auto_run" in line:
                continue
            if "->" in line:
                continue
            # We're stripping this out of a function context, so skip returns.
            if line.lstrip().startswith("return"):
                continue

            # Ignore docstrings
            if '"""' in line:
                docstring_count += 1

            if skip and not docstring_count:
                # TODO: Fix the fullargspec resolution for more reliable parameter name and default value fetching.
                source_args.append(line.lstrip().replace(",\n", "").split(":"))

            if skip:
                if docstring_count == 2:
                    skip = False
                continue

            # De-indent and replace self with ql.
            sanitized_line = line[8:].replace("self.", "ql.")
            if sanitized_line == "":
                sanitized_line = "\n"  # Fix returns
            auto_run_code.append(sanitized_line)

        arg_lines = ["# Parameters\n"]

        for i, a in enumerate(source_args):
            varname = a[0].replace("'", "")
            if varname == "self":
                varname = "ql"
                value = f"feyn.QLattice({self._random_seed if self._random_seed != -1 else ''})"
            else:
                value = "'<INSERT HERE>'"
                if i <= len(args):
                    value = _get_var_name(args[i - 1], frame=frame)
                    if value is None:
                        value = args[i - 1]
                        if type(value) == DataFrame:
                            # We don't want to ever expand an inline dataframe
                            value = None
                        elif type(value) == str:
                            value = f'"{value}"'
                elif varname in kwargs:
                    call_varname = _get_var_name(kwargs[varname], frame=frame)
                    if call_varname is None:
                        value = kwargs[varname]
                        if type(value) == str:
                            value = f'"{value}"'
                    else:
                        value = call_varname
                elif len(a) > 1:
                    type_split = a[1].split("=")
                    if len(type_split) > 1:
                        value = type_split[1].lstrip()

            arg_lines.append(f"{varname} = {value}\n")

        cell_contents = (
            imports + arg_lines + ["\n"] + extension_behaviour + auto_run_code
        )
        return cell_contents


def _create_new_cell(contents):
    from IPython.core.getipython import get_ipython

    shell = get_ipython()
    shell.set_next_input(contents, replace=False)


def _get_var_name(var, frame):
    local_names = frame.f_locals
    for name in local_names:
        if name in ["_", "__"]:  # ignore previous cell jupyter magic
            continue
        if id(var) == id(local_names[name]):
            return name
    return None
