""" Functions to automatically handle tasks using best guesses.
"""

from typing import Optional, Dict


def infer_available_threads() -> int:
    """Attempt to infer the amount of threads available. Will always leave one free for system use.

    Returns:
        int -- thread count
    """
    from os import cpu_count

    found_cpus = cpu_count()
    if found_cpus is None:
        threads = 4
    else:
        threads = found_cpus - 1
    return threads


def infer_output_stype(
    kind: str, output_name: str, stypes: Optional[Dict[str, str]] = {}
):
    if kind == "auto":
        stype = stypes.get(output_name, "f")
        if stype not in ["b", "f"]:
            raise ValueError(
                f"The output stype for '{output_name}' must be either 'b' (boolean) or 'f' (float). Was: '{stype}'"
            )
        return stype
    else:
        return kind_to_output_stype(kind)


def kind_to_output_stype(kind: str) -> str:
    """Parse model kind string (like "regression" or "classification") into an output spec for the QLattice."""
    if kind in ["regression", "regressor"]:
        return "f"
    if kind in ["classification", "classifier"]:
        return "b"
    raise ValueError(
        "Model kind not understood. Please choose either a 'regression' or a 'classification'."
    )
