import numpy as np
from typing import Optional, List
from feyn import _logger


class DisplayHelper:
    """A barebones display helper class that allows saving the output as a file."""

    def __init__(self, data, supports_ext: Optional[List[str]] = None):
        self.data = data
        self._supports_ext = supports_ext

    def __repr__(self):
        return self.data

    def _ext_handler(self, file_ext: str):
        """Extension handler that can be overridden to support multiple extensions or conversion

        Keyword Arguments:
            file_ext {str} -- file extension from splitext

        Returns:
            Any -- Content that will be written to a file
        """
        return self.data

    def save(self, filename: str) -> str:
        """Save data contents to file.
        Args:
            filename (str): the filename or path of the file to save.
        Returns:
            The path where the file was saved.
        """
        from os.path import splitext, abspath

        filename, file_ext = splitext(filename)

        if self._supports_ext is not None and file_ext not in self._supports_ext:
            default_ext = self._supports_ext[0]
            if file_ext != "":
                _logger.warning(
                    f"Extension '{file_ext}' not supported. Will save using the default '{default_ext}' instead."
                )
            file_ext = default_ext

        path = filename + file_ext

        with open(path, "w") as fd:
            fd.write(self._ext_handler(file_ext))

        return abspath(path)


class HTML(DisplayHelper):
    """A barebones HTML display helper class that allows saving the output as a file."""

    def __init__(self, data):
        super().__init__(data, [".html"])

    def _repr_html_(self):
        return self.__repr__()

    def __html__(self):
        return self.__repr__()


class SVG(DisplayHelper):
    """A barebones SVG display helper class that allows saving the output as a file."""

    def __init__(self, data):
        super().__init__(data, [".svg", ".html"])

    def _repr_svg_(self):
        return self.__repr__()

    def _repr_html_(self):
        return self.__repr__()


def get_progress_label(
    epoch: int,
    epochs: int,
    elapsed_seconds: Optional[float] = None,
    model_count: Optional[int] = None,
) -> str:
    """Gives a label for use with feyn.show_model based on epochs, max_epochs, time elapsed and model_count

    Arguments:
        epoch {int} -- The current epoch
        epochs {int} -- Total amount of epochs
        elapsed_seconds {Optional[float]} -- seconds elapsed so far
        model_count {Optional[int]} -- Models investigated so far

    Returns:
        str -- A string label displaying progress
    """
    epoch_status = f"Epoch no. {epoch}/{epochs}"
    model_status = ""
    elapsed_status = ""

    if model_count is not None:
        model_status = f" - Tried {model_count} models"
    if elapsed_seconds is not None:
        if epoch < epochs:
            elapsed_status = f" - Elapsed: {_time_to_hms(elapsed_seconds)} of {_time_to_hms(np.ceil(elapsed_seconds/epoch*epochs), most_signif=True)}. (est.)"
        else:
            elapsed_status = f" - Completed in {_time_to_hms(elapsed_seconds)}."

    return f"{epoch_status}{model_status}{elapsed_status}"


def _time_to_hms(tis: float, most_signif: bool = False) -> str:
    s = int(tis % 60)
    m = int(tis // 60 % 60)
    h = int(tis // 3600)
    if most_signif:
        return f"{h + m/60:.1f}h" if h else f"{m+s/60:.1f}m" if m else f"{s}s"
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s" if m else f"{s}s"
