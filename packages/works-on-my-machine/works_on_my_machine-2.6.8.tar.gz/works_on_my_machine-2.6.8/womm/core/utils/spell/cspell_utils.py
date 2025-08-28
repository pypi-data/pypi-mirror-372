#!/usr/bin/env python3
"""
CSpell Utils - Utility functions for CSpell configuration and operations.
Pure utility functions without UI - used by SpellManager.
Handles CSpell configuration, project detection, and file operations.
"""

import json
import logging
import os
import platform
import shutil
from pathlib import Path
from typing import List, Optional

from ....common.security import run_silent
from ..system.user_path_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)


def check_cspell_installed() -> bool:
    """Check if CSpell is installed."""
    # Check via shutil.which (PATH)
    cspell_path = shutil.which("cspell")

    if cspell_path is not None:
        logging.debug("CSpell found via shutil.which")
        return True

    # Check via npx (common fallback) - direct subprocess for Windows compatibility
    try:
        result = run_silent(
            "npx cspell --version",
            timeout=10,
        )

        logging.debug(
            f"npx cspell --version result: returncode={result.returncode}, stdout='{result.stdout.strip()}'"
        )
        if result.returncode == 0 and result.stdout.strip():
            logging.debug("CSpell found via npx")
            # Tentative d'ajout au PATH pour les futures utilisations
            try:
                _try_add_cspell_to_path_if_found_via_npx()
            except Exception as e:
                logging.debug(f"Failed to add CSpell to PATH: {e}")
            return True
    except Exception as e:
        logging.debug(f"npx cspell check failed: {e}")

    # Check via npm (final fallback)
    try:
        result = run_silent(["npm", "list", "-g", "cspell"])

        logging.debug(
            f"npm list -g cspell result: success={result.success}, stdout='{result.stdout}'"
        )
        return result.success and "cspell@" in result.stdout
    except Exception:
        return False


def _try_add_cspell_to_path_if_found_via_npx() -> bool:
    """Tente d'ajouter CSpell au PATH utilisateur si trouvé via npx pour optimiser les futures utilisations."""
    try:
        # Vérifier que npm est disponible d'abord
        npm_path = shutil.which("npm")
        if not npm_path:
            logging.debug("npm not found in PATH")
            return False

        # Méthode 1: Utiliser 'npx --no-install cspell --version' pour vérifier si CSpell est déjà installé
        try:
            result = run_silent(
                ["npx", "--no-install", "cspell", "--version"],
                timeout=10,
            )

            if result.returncode == 0:
                logging.debug("CSpell already accessible via npx")
                # CSpell est déjà accessible, pas besoin de modifier le PATH
                return True
        except Exception as e:
            logging.debug(f"npx check failed: {e}")

        # Méthode 2: Vérifier dans npm list globalement installé
        try:
            result = run_silent(
                [npm_path, "list", "-g", "--depth=0", "cspell"],
                timeout=10,
            )

            if result.returncode == 0 and "cspell@" in result.stdout:
                logging.debug("CSpell found in global npm packages")
                # Récupérer le dossier bin global
                bin_result = run_silent(
                    [npm_path, "config", "get", "prefix"],
                    timeout=5,
                )

                if bin_result.returncode == 0 and bin_result.stdout.strip():
                    npm_prefix = Path(bin_result.stdout.strip())
                    # Sur Windows, les binaires npm globaux sont dans prefix/bin ou prefix
                    npm_bin_path = (
                        npm_prefix / "bin"
                        if (npm_prefix / "bin").exists()
                        else npm_prefix
                    )
                    logging.debug(f"Found npm global bin path: {npm_bin_path}")

                    # Ajouter au PATH si CSpell y est présent
                    return _add_npm_bin_to_path(npm_bin_path)

        except Exception as e:
            logging.debug(f"npm list check failed: {e}")

        # Méthode 3: Utiliser 'npm root -g' pour trouver le dossier node_modules global
        try:
            result = run_silent(
                [npm_path, "root", "-g"],
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                global_modules = Path(result.stdout.strip())
                cspell_module = global_modules / "cspell"

                if cspell_module.exists():
                    logging.debug(f"Found CSpell module at: {cspell_module}")
                    # Dériver le chemin bin à partir du node_modules global
                    npm_bin_path = global_modules.parent / "bin"
                    return _add_npm_bin_to_path(npm_bin_path)

        except Exception as e:
            logging.debug(f"npm root check failed: {e}")

        logging.warning("Could not locate CSpell installation through npm methods")
        return False

    except Exception as e:
        logging.error(f"Error in CSpell PATH detection: {e}")
        return False


def _add_npm_bin_to_path(npm_bin_path: Path) -> bool:
    """Ajoute le dossier bin npm au PATH si CSpell y est trouvé."""
    try:
        if not npm_bin_path.exists():
            logging.warning(f"npm bin path does not exist: {npm_bin_path}")
            return False

        # Sur Windows, npm crée des fichiers .cmd
        cspell_path = npm_bin_path / "cspell.cmd"
        if not cspell_path.exists():
            # Fallback pour autres OS
            cspell_path = npm_bin_path / "cspell"
            if not cspell_path.exists():
                logging.warning(f"CSpell binary not found in: {npm_bin_path}")
                return False

        logging.info(f"Found CSpell binary: {cspell_path}")

        # Ajouter au PATH utilisateur en utilisant la même logique que l'installer
        logging.debug(f"Adding to PATH: {npm_bin_path}")
        success = _add_directory_to_user_path(str(npm_bin_path))

        if success:
            logging.debug(
                f"Successfully added CSpell directory to user PATH: {npm_bin_path}"
            )
            return True
        else:
            logging.warning(f"Failed to add CSpell directory to PATH: {npm_bin_path}")
            return False

    except Exception as e:
        logging.error(f"Error adding npm bin to PATH: {e}")
        return False


def _add_directory_to_user_path(directory_path: str) -> bool:
    """Ajoute un répertoire au PATH utilisateur."""
    try:
        if platform.system() == "Windows":
            # Méthode Windows : modifier le registre utilisateur
            result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"],
            )

            if result.returncode == 0:
                current_user_path = extract_path_from_reg_output(result.stdout)
                if not current_user_path:
                    current_user_path = ""

                # Vérifier si déjà présent
                if directory_path in current_user_path:
                    logging.debug("Directory already in user PATH")
                    return True

                # Ajouter le nouveau chemin
                new_user_path = (
                    f"{current_user_path};{directory_path}"
                    if current_user_path
                    else directory_path
                )
                new_user_path = deduplicate_path_entries(new_user_path)

                # Modifier le registre
                reg_result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_user_path,
                        "/f",
                    ],
                )

                if reg_result.returncode == 0:
                    # Mettre à jour la session courante aussi
                    current_session_path = os.environ.get("PATH", "")
                    if directory_path not in current_session_path:
                        os.environ["PATH"] = f"{current_session_path};{directory_path}"
                    return True

            return False

        else:
            # Méthode Unix : ajouter au shell profile
            shell_profiles = ["~/.bashrc", "~/.zshrc", "~/.profile"]

            for profile_file in shell_profiles:
                profile_path = Path(profile_file).expanduser()
                if profile_path.exists():
                    content = profile_path.read_text()
                    export_line = f'export PATH="$PATH:{directory_path}"'

                    if directory_path not in content:
                        # Ajouter la ligne d'export
                        profile_path.write_text(content + f"\n{export_line}\n")

                    # Mettre à jour la session courante
                    current_path = os.environ.get("PATH", "")
                    if directory_path not in current_path:
                        os.environ["PATH"] = f"{current_path}:{directory_path}"
                    return True

            return False

    except Exception as e:
        logging.error(f"Error adding directory to PATH: {e}")
        return False


def setup_project_cspell(
    project_path: Path, project_type: str, project_name: str
) -> bool:
    """Configure CSpell for a specific project."""
    devtools_path = Path.home() / ".womm"

    if project_type == "python":
        template_path = (
            devtools_path
            / "languages"
            / "python"
            / "templates"
            / "cspell.json.template"
        )
    elif project_type == "javascript":
        template_path = (
            devtools_path
            / "languages"
            / "javascript"
            / "templates"
            / "cspell.json.template"
        )
    else:
        logging.error(f"Project type not supported: {project_type}")
        return False

    if not template_path.exists():
        logging.error(f"Template not found: {template_path}")
        return False

    # Lire le template
    template_content = template_path.read_text(encoding="utf-8")

    # Replace placeholders
    config_content = template_content.replace("{{PROJECT_NAME}}", project_name)

    # Write configuration
    config_file = project_path / "cspell.json"
    config_file.write_text(config_content, encoding="utf-8")

    logging.info(f"CSpell configuration created: {config_file}")
    return True


def run_spellcheck(path: Path) -> dict:
    """Run spell check and return detailed results."""
    if not check_cspell_installed():
        logging.error("CSpell not installed - use: spellcheck --install")
        return {
            "success": False,
            "error": "CSpell not installed",
            "issues": [],
            "summary": {"files_checked": 0, "issues_found": 0},
        }

    # Utiliser le CLI manager standard
    from ..cli_utils import run_command

    # Vérifier si cspell est directement disponible dans le PATH
    cspell_path = shutil.which("cspell")
    cspell_direct_available = cspell_path is not None

    # Choisir la commande appropriée
    if cspell_direct_available:
        # Utiliser le chemin complet pour éviter les problèmes Windows
        cmd = [str(cspell_path), "lint", str(path)]
        cmd_description = f"Spell check - {path.name}"
    else:
        cmd = ["npx", "cspell", "lint", str(path)]
        cmd_description = f"Spell check - {path.name} (via npx)"

    cmd.extend(["--no-progress", "--show-context"])
    logging.debug(f"Checking: {path}")
    interactive_mode = False

    # Exécution avec shell=True pour Windows (nécessaire pour les commandes .cmd/.bat)
    result = run_command(cmd, cmd_description, shell=True)  # noqa: S604

    logging.debug(
        f"CSpell command result: success={result.success}, returncode={result.returncode}"
    )
    logging.debug(f"CSpell stdout: {result.stdout}")
    logging.debug(f"CSpell stderr: {result.stderr}")

    # Analyser les résultats
    issues = []
    summary = {"files_checked": 0, "issues_found": 0}

    if interactive_mode:
        # En mode interactif, on ne parse pas la sortie car elle est gérée par CSpell
        # On considère que l'opération a réussi si CSpell s'est terminé normalement
        summary = {"files_checked": 1, "issues_found": 0}  # Valeur par défaut
    elif result.stdout:
        # Parser la sortie de CSpell pour extraire les erreurs (mode normal)
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if ":" in line and ("Unknown word" in line or "Spelling error" in line):
                # Format: file:line:col - Error message -- Context
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    try:
                        line_num = int(parts[1])
                        col_num = int(parts[2])
                    except ValueError:
                        line_num = 0
                        col_num = 0

                    error_info = parts[3].strip()
                    # Extraire le mot et le contexte
                    if "--" in error_info:
                        error_parts = error_info.split("--", 1)
                        word_info = error_parts[0].strip()
                        context = error_parts[1].strip() if len(error_parts) > 1 else ""
                    else:
                        word_info = error_info
                        context = ""

                    # Extraire le mot problématique
                    word = ""
                    if "(" in word_info and ")" in word_info:
                        word = word_info.split("(")[1].split(")")[0]
                    elif "Unknown word" in word_info:
                        word = word_info.replace("Unknown word", "").strip()

                    issues.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "column": col_num,
                            "word": word,
                            "message": word_info,
                            "context": context,
                        }
                    )

        # Compter les fichiers et erreurs
        files_checked = len({issue["file"] for issue in issues})
        summary = {"files_checked": files_checked, "issues_found": len(issues)}

    # CSpell retourne code 1 quand des erreurs sont trouvées, ce qui est normal
    success = result.success or result.returncode == 1

    return {
        "success": success,
        "issues": issues,
        "summary": summary,
        "raw_output": result.stdout,
        "raw_stderr": result.stderr,
    }


def detect_project_type(project_path: Path) -> Optional[str]:
    """Detect project type."""
    # Python
    if any(
        (project_path / f).exists()
        for f in ["setup.py", "pyproject.toml", "requirements.txt"]
    ):
        return "python"

    # JavaScript/Node.js
    if any((project_path / f).exists() for f in ["package.json", "node_modules"]):
        return "javascript"

    return None


def add_words_to_config(project_path: Path, words: List[str]) -> bool:
    """Add words to CSpell configuration."""
    try:
        config_path = project_path / "cspell.json"

        if not config_path.exists():
            return False

        config = json.loads(config_path.read_text(encoding="utf-8"))

        if "words" not in config:
            config["words"] = []

        # Add new words
        added_count = 0
        for word in words:
            if word not in config["words"]:
                config["words"].append(word)
                added_count += 1

        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        return True

    except Exception:
        return False


def get_project_status(project_path: Path) -> dict:
    """Get detailed status of CSpell project configuration."""
    status = {
        "cspell_installed": check_cspell_installed(),
        "config_exists": False,
        "config_path": None,
        "project_type": None,
        "words_count": 0,
        "dictionaries": [],
        "last_check": None,
        "issues_count": 0,
    }

    # Check if CSpell config exists
    config_file = project_path / "cspell.json"
    if config_file.exists():
        status["config_exists"] = True
        status["config_path"] = str(config_file)

        try:
            config_data = json.loads(config_file.read_text(encoding="utf-8"))
            status["words_count"] = len(config_data.get("words", []))
            status["dictionaries"] = config_data.get("dictionaries", [])
        except Exception as e:
            logging.debug(f"Failed to read CSpell config: {e}")

    # Detect project type
    status["project_type"] = detect_project_type(project_path)

    return status


def add_words_from_file(project_path: Path, file_path: Path) -> bool:
    """Add words from a file to CSpell configuration."""
    if not file_path.exists():
        logging.error(f"File not found: {file_path}")
        return False

    try:
        words = []
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    words.extend(line.split())

        if not words:
            logging.warning("No words found in file")
            return False

        return add_words_to_config(project_path, words)

    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return False
