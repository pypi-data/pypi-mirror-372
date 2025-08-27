"""
Spell checking utility modules for Works On My Machine.

This package contains pure utility functions for spell checking operations.
"""

# Import utility functions for external use
from .cspell_utils import (
    add_words_to_config,
    check_cspell_installed,
    get_project_status,
    run_spellcheck,
    setup_project_cspell,
)
from .dictionary_utils import (
    add_all_dictionaries,
    add_all_dictionaries_from_dir,
    get_dictionary_info,
    list_available_dictionaries,
)

__all__ = [
    "check_cspell_installed",
    "run_spellcheck",
    "setup_project_cspell",
    "get_project_status",
    "add_words_to_config",
    "add_all_dictionaries",
    "add_all_dictionaries_from_dir",
    "get_dictionary_info",
    "list_available_dictionaries",
]
