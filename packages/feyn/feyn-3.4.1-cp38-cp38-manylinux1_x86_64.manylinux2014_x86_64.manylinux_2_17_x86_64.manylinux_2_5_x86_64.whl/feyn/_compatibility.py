def detect_notebook() -> bool:
    try:
        from IPython import get_ipython

        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter
    except ImportError:
        return False  # IPython not installed


def supports_interactivity() -> bool:
    """Try to detect if we're compatible with interactivity.

    Returns:
        bool -- True if compatible
    """
    try:
        import ipywidgets
    except ImportError:
        return False

    return detect_notebook()
