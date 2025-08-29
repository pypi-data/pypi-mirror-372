from ._api import cfit, cfit_grid, cfit_gui, cfit_grid_gui
from . import data
from .version import version as __version__

# Then you can be explicit to control what ends up in the namespace,
__all__ = ['cfit', 'cfit_grid', 'cfit_gui', 'cfit_grid_gui', 'data']
