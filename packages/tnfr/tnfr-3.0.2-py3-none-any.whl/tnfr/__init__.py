from __future__ import annotations
"""
TNFR — Teoría de la Naturaleza Fractal Resonante
API pública del paquete.

Ecuación nodal:
    ∂EPI/∂t = νf · ΔNFR(t)
"""

__version__ = "3.0.2"

# -------------------------------------------------------------------
# 1) Registrar alias en sys.modules ANTES de cargar submódulos que
#    hacen imports absolutos (p.ej. `from constants import ...`).
#    Orden: constants -> helpers -> operators -> observers
#    Luego: dynamics / ontosim (que dependen de los anteriores)
# -------------------------------------------------------------------
import sys as _sys

# 1.a constants (no depende de helpers/otros)
from . import constants as _constants
_sys.modules.setdefault("constants", _constants)

# 1.b helpers (usa: from constants import ...)
from . import helpers as _helpers
_sys.modules.setdefault("helpers", _helpers)

# 1.c operators (usa: from constants/helpers import ...)
from . import operators as _operators
_sys.modules.setdefault("operators", _operators)

# 1.d observers (usa: from constants/helpers import ...)
from . import observers as _observers
_sys.modules.setdefault("observers", _observers)

# 2) dynamics / ontosim (ya con alias creados)
from . import dynamics as _dynamics
from . import ontosim as _ontosim
_sys.modules.setdefault("dynamics", _dynamics)
_sys.modules.setdefault("ontosim",  _ontosim)

# 3) Re-exports de la API pública
from .dynamics import step, run, set_delta_nfr_hook
from .ontosim import preparar_red
from .observers import attach_standard_observer, coherencia_global, orden_kuramoto

__all__ = [
    "preparar_red",
    "step", "run", "set_delta_nfr_hook",
    "attach_standard_observer", "coherencia_global", "orden_kuramoto",
    "__version__",
]
