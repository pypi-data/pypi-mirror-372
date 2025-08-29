"""Feyn is the main Python module to build and execute models that utilizes a QLattice.

The QLattice stores and updates probabilistic information about the mathematical relationships (models) between observable quantities.

The workflow is typically:

# Instantiate a QLattice
>>> ql = feyn.QLattice()

# Sample models from the QLattice
>>> models = ql.sample_models(data.columsn, output="out")

# Fit the list of models to a dataset
>>> models = feyn.fit_models(models, data)

# Pick the best Model from the fitted models
>>> best = models[0]

# Update the QLattice with this model to explore similar models.
>>> ql.update(best)

# Or use the model to make predictions
>>> predicted_y = model.predict(new_data)
"""

from ._logging import _init_logger, _configure_notebook_logger

_configure_notebook_logger()
_logger = _init_logger(__name__)

from ._version import _read_version, _read_git_sha
from ._functions import FNAME_MAP, FNAMES
from ._model import Model
from ._qlattice import QLattice
from ._svgrenderer import show_model, _render_svg
from ._trainer import fit_models

from ._selection import prune_models, get_diverse_models
from ._validation import validate_data

from ._qlattice import connect_qlattice

from . import tools
from . import losses
from . import _criteria
from . import filters
from . import metrics
from . import plots
from . import reference
from . import datasets

from .plots import Theme

_current_renderer = _render_svg
_disable_type_checks = False

__all__ = [
    "fit_models",
    "prune_models",
    "get_diverse_models",
    "show_model",
    "Model",
    "validate_data",
    "QLattice",
    "Theme",
]

__version__ = _read_version()
__git_sha__ = _read_git_sha()


from . import _checklicense

_checklicense.verify_license()
