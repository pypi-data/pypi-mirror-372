from __future__ import annotations
"""
TNFR — Teoría de la Naturaleza Fractal Resonante
API pública del paquete.

Principio operativo (ecuación nodal):
    ∂EPI/∂t = νf · ΔNFR(t)

Re-exporta:
- preparar_red
- step, run, set_delta_nfr_hook
- attach_standard_observer, coherencia_global, orden_kuramoto
"""

__version__ = "3.0.1"

# -------------------------------------------------------------------
# 1) Registrar alias ANTES de importar submódulos que usan imports
#    absolutos (p.ej. `from constants import DEFAULTS`)
# -------------------------------------------------------------------
import sys as _sys

from . import constants as _constants
from . import helpers as _helpers
from . import operators as _operators
from . import observers as _observers

_sys.modules.setdefault("constants", _constants)
_sys.modules.setdefault("helpers", _helpers)
_sys.modules.setdefault("operators", _operators)
_sys.modules.setdefault("observers", _observers)

# -------------------------------------------------------------------
# 2) Ahora sí: importar módulos que dependen de esos alias
# -------------------------------------------------------------------
from .dynamics import step, run, set_delta_nfr_hook
from .ontosim import preparar_red
from .observers import attach_standard_observer, coherencia_global, orden_kuramoto

# (opcional) exponer también alias para `dynamics` y `ontosim`
# si algún código externo hace `from dynamics import run`, etc.
import types as _types
import importlib as _importlib

_dynamics_mod = _importlib.import_module(__name__ + ".dynamics")
_ontosim_mod  = _importlib.import_module(__name__ + ".ontosim")
_sys.modules.setdefault("dynamics", _dynamics_mod)
_sys.modules.setdefault("ontosim",  _ontosim_mod)

# -------------------------------------------------------------------
# 3) API pública
# -------------------------------------------------------------------
__all__ = [
    "preparar_red",
    "step", "run", "set_delta_nfr_hook",
    "attach_standard_observer", "coherencia_global", "orden_kuramoto",
    "__version__",
]
