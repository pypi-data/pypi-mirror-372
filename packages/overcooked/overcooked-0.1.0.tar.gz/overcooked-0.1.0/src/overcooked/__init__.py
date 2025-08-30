from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from . import env
from .env import Overcooked
from .mdp import Action, OvercookedEnv, OvercookedGridworld, OvercookedState, Recipe


from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("overcooked")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback pratique en dev/CI

__all__ = [
    "Overcooked",
    "env",
    "Action",
    "OvercookedEnv",
    "OvercookedGridworld",
    "OvercookedState",
    "Recipe",
    "__version__",
]
