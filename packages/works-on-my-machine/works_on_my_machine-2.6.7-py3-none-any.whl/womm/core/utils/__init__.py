"""
Tools modules for Works On My Machine.

This package contains specialized tools like CSpell and dictionary management.
"""

from .spell.cspell_utils import (
    check_cspell_installed,
    run_spellcheck,
    setup_project_cspell,
)
from .spell.dictionary_utils import add_all_dictionaries, get_dictionary_info

__all__ = [
    "setup_project_cspell",
    "run_spellcheck",
    "check_cspell_installed",
    "add_all_dictionaries",
    "get_dictionary_info",
]
