#!/usr/bin/env python3
"""
Import utilities for WOMM CLI.
Handles imports for both development and PyPI installation.
"""

from pathlib import Path
from typing import Any


def import_shared_module(module_name: str) -> Any:
    """Import strict d'un module dans `shared` (sans fallback)."""
    return __import__(f"shared.{module_name}", fromlist=[module_name.split(".")[-1]])


def get_shared_module_path() -> Path:
    """Chemin strict vers le dossier `shared` du projet (sans fallback)."""
    return Path(__file__).parent.parent.parent / "shared"


def get_languages_module_path() -> Path:
    """Chemin strict vers le dossier `womm/languages` (sans fallback)."""
    return Path(__file__).parent.parent / "languages"
