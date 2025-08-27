#!/usr/bin/env python3
"""
Spell Manager - Centralized spell checking logic for WOMM projects.
Handles CSpell installation, configuration, and spell checking operations.
"""

from pathlib import Path
from typing import List, Optional

from ....common.results import SpellResult

# UI imports for integrated display
from ...ui.common.console import (
    print_debug,
    print_error,
    print_header,
    print_info,
    print_success,
    print_system,
    print_warn,
)
from ...ui.common.progress import create_spinner_with_status


class SpellManager:
    """Manages spell checking operations with CSpell."""

    def __init__(self):
        self._cspell_available = None  # Cached availability check
        self._cache_timestamp = None  # Cache invalidation timestamp
        self._cache_timeout = 30  # Cache timeout in seconds

    @property
    def cspell_available(self) -> bool:
        """Check if CSpell is available (cached with timeout)."""
        import time

        from ...utils.spell.cspell_utils import check_cspell_installed

        current_time = time.time()

        # Check if cache is valid (exists and not expired)
        if (
            self._cspell_available is not None
            and self._cache_timestamp is not None
            and (current_time - self._cache_timestamp) < self._cache_timeout
        ):
            return self._cspell_available

        # Cache miss or expired - refresh
        self._cspell_available = check_cspell_installed()
        self._cache_timestamp = current_time
        return self._cspell_available

    @cspell_available.setter
    def cspell_available(self, value: bool):
        """Allow manual override of cspell availability and update cache."""
        import time

        self._cspell_available = value
        self._cache_timestamp = time.time()

    def invalidate_cspell_cache(self):
        """Invalidate the CSpell availability cache."""
        self._cspell_available = None
        self._cache_timestamp = None

    def _ensure_cspell_available(
        self, operation_name: str = "operation"
    ) -> SpellResult:
        """Check CSpell availability with user-friendly display and return result if not available."""
        if self.cspell_available:
            return None  # None means continue with operation
        else:
            print_error("❌ CSpell is not available")
            print_info('💡 Install CSpell using: "womm spell install"')
            return SpellResult(
                success=False,
                message=f'CSpell is not available for {operation_name}. Run "womm spell install" first.',
                error="cspell_not_available",
            )

    def install_cspell(self) -> SpellResult:
        """Install CSpell and dictionaries globally with integrated UI."""
        print_header("📦 CSpell Installation")

        try:
            # Check if CSpell is already available
            if self.cspell_available:
                print_success("✅ CSpell is already available")
            else:
                print_error("❌ CSpell is not available")

                # Install CSpell via DevToolsManager (ensures Node via runtime_manager)
                print_info("📦 Installing CSpell...")
                from ..dependencies.dev_tools_manager import dev_tools_manager

                tool_result = dev_tools_manager.install_dev_tool(
                    language="universal", tool_type="spell_checking", tool="cspell"
                )

                if not tool_result.success:
                    print_error(
                        f"❌ CSpell installation failed: {tool_result.error or 'Unknown error'}"
                    )
                    return SpellResult(
                        success=False,
                        message=tool_result.error
                        or "Failed to install CSpell via dev tools manager",
                        error="cspell_install_failed",
                    )

                # Invalidate cache and refresh cspell availability check after installation
                self.invalidate_cspell_cache()
                from ...utils.spell.cspell_utils import check_cspell_installed

                self.cspell_available = check_cspell_installed()

                if self.cspell_available:
                    print_success("✅ CSpell installed successfully")
                else:
                    print_error("❌ CSpell installation verification failed")
                    return SpellResult(
                        success=False,
                        message="CSpell installation verification failed",
                        error="cspell_verification_failed",
                    )

            # Install essential dictionaries
            print_info("🔧 Starting dictionary setup...")
            dict_result = self.setup_dictionaries()

            if not dict_result.success:
                return dict_result

            # Final success message
            print_success("✅ CSpell and dictionaries are ready")
            return SpellResult(
                success=True,
                message="CSpell and dictionaries are ready",
                data={
                    "cspell_installed": True,
                    "dictionaries_setup": dict_result.success,
                },
            )

        except Exception as e:
            print_error(f"❌ Installation error: {e}")
            return SpellResult(
                success=False,
                message=f"Installation error: {e}",
                error="installation_error",
            )

    def setup_dictionaries(self) -> SpellResult:
        """Install essential CSpell dictionaries globally with integrated UI."""
        try:
            with create_spinner_with_status("Setting up dictionaries...") as (
                progress,
                task,
            ):
                progress.update(task, status="Checking CSpell availability...")

                # Ensure CSpell is available first
                if not self.cspell_available:
                    progress.update(task, status="CSpell not available")
                    print_error("❌ CSpell must be installed first")
                    print_system("💡 Install CSpell using: womm devtools install")
                    return SpellResult(
                        success=False,
                        message="CSpell must be installed before setting up dictionaries",
                        error="cspell_not_available",
                    )

                progress.update(task, status="Installing essential dictionaries...")

                # Install essential dictionaries
                dictionaries = [
                    "@cspell/dict-typescript",
                    "@cspell/dict-node",
                    "@cspell/dict-npm",
                    "@cspell/dict-html",
                    "@cspell/dict-css",
                    "@cspell/dict-python",
                    "@cspell/dict-django",
                    "@cspell/dict-flask",
                    "@cspell/dict-companies",
                    "@cspell/dict-software-terms",
                    "@cspell/dict-lorem-ipsum",
                ]

                # Install each dictionary using dev_tools_manager's npm capability
                installed_count = 0
                failed_dictionaries = []

                for dictionary in dictionaries:
                    progress.update(task, status=f"Installing {dictionary}...")
                    try:
                        # Use dev_tools_manager's JavaScript tool installation method
                        from ..dependencies.dev_tools_manager import dev_tools_manager

                        # Use the private method directly since dictionaries aren't in the dev tools config
                        success = dev_tools_manager._install_javascript_tool(dictionary)

                        if success:
                            installed_count += 1
                        else:
                            failed_dictionaries.append(dictionary)
                    except Exception:
                        failed_dictionaries.append(dictionary)

                # Return results based on success rate
                if installed_count == 0:
                    progress.update(task, status="No dictionaries installed")
                    progress.stop()
                    return SpellResult(
                        success=False,
                        message="Failed to install any dictionaries",
                        error="all_dictionaries_failed",
                    )
                elif failed_dictionaries:
                    progress.update(task, status="Partial installation completed")
                    progress.stop()
                    print_success(
                        f"✅ Installed {installed_count}/{len(dictionaries)} dictionaries"
                    )
                    print_system(f"⚠️ Failed: {', '.join(failed_dictionaries)}")
                    return SpellResult(
                        success=True,
                        message=f"Installed {installed_count}/{len(dictionaries)} dictionaries successfully",
                        data={
                            "failed": failed_dictionaries,
                            "installed": installed_count,
                        },
                    )
                else:
                    progress.update(task, status="All dictionaries installed!")
                    progress.stop()
                    print_success(
                        f"✅ All {installed_count} essential dictionaries installed successfully"
                    )
                    return SpellResult(
                        success=True,
                        message=f"All {installed_count} essential dictionaries installed successfully",
                        data={"installed": installed_count},
                    )

        except Exception as e:
            print_error(f"❌ Dictionary setup error: {e}")
            return SpellResult(
                success=False,
                message=f"Dictionary setup error: {e}",
                error="dictionary_setup_error",
            )

    def perform_setup_project(
        self, project_name: str, project_type: Optional[str] = None
    ) -> SpellResult:
        """Set up CSpell configuration for a project with integrated UI."""
        print_header("CSpell Project Setup")

        # Check CSpell availability - early return if not available
        cspell_check = self._ensure_cspell_available("project setup")
        if cspell_check is not None:  # Error occurred
            return cspell_check

        try:
            with create_spinner_with_status("Setting up CSpell configuration...") as (
                progress,
                task,
            ):
                # Determine project path
                progress.update(task, status="Determining project path...")
                project_path = (
                    Path.cwd() / project_name if project_name != "." else Path.cwd()
                )

                # Detect project type if not provided
                progress.update(task, status="Detecting project type...")
                if not project_type:
                    from ...utils.spell.cspell_utils import detect_project_type

                    detected_type = detect_project_type(project_path)
                    project_type = detected_type if detected_type else "generic"

                # Use cspell_utils for sophisticated template-based setup
                progress.update(task, status="Creating CSpell configuration...")
                from ...utils.spell.cspell_utils import setup_project_cspell

                success = setup_project_cspell(project_path, project_type, project_name)

                if success:
                    progress.update(task, status="Configuration created successfully!")
                    print_success(
                        f"✅ CSpell configured for {project_name} ({project_type})"
                    )
                    print_success("✅ CSpell setup completed successfully")
                    return SpellResult(
                        success=True,
                        message=f"CSpell configured for {project_name} ({project_type})",
                    )
                else:
                    progress.update(task, status="Configuration failed")
                    print_error("❌ Failed to setup CSpell configuration")
                    print_error(
                        "❌ CSpell setup failed: Failed to create CSpell configuration"
                    )
                    return SpellResult(
                        success=False,
                        message="Failed to create CSpell configuration",
                        error="setup_failed",
                    )

        except Exception as e:
            print_error(f"❌ Setup error: {e}")
            print_error(f"❌ CSpell setup failed: {e}")
            return SpellResult(
                success=False,
                message=f"Failed to setup CSpell: {e}",
                error="setup_failed",
            )

    def display_project_status(
        self, project_path: Optional[Path] = None
    ) -> SpellResult:
        """Get and display CSpell configuration status for a project with integrated UI."""
        if project_path is None:
            project_path = Path.cwd()

        print_header("📊 CSpell Project Status")

        # Check and display CSpell availability (non-blocking for status command)
        if not self.cspell_available:
            print_error("❌ CSpell is not installed")
            print_info('💡 Install using: "womm spell install"')

        try:
            with create_spinner_with_status("Analyzing project...") as (progress, task):
                progress.update(task, status="Gathering project information...")

                # Use cspell_utils for the actual status gathering
                from ...utils.spell.cspell_utils import get_project_status

                status = get_project_status(project_path)

                progress.update(task, status="Analyzing configuration...")

                # Add some additional WOMM-specific checks
                dict_dir = project_path / ".cspell-dict"
                if dict_dir.exists():
                    dict_files = list(dict_dir.glob("*.txt"))
                    status["dict_files"] = [f.name for f in dict_files]
                    status["total_words"] = sum(
                        len(f.read_text().splitlines()) for f in dict_files
                    )
                else:
                    status["dict_files"] = []
                    status["total_words"] = 0

                progress.update(task, status="Status analysis complete!")

            # Display results with nice UI (AFTER spinner closes)
            print("")
            if status["config_exists"]:
                print_success("✅ CSpell configuration found")
                print_system(f"📁 Words count: {status.get('words_count', 0)}")
            else:
                print_error("❌ No CSpell configuration found")
                print_system("💡 Run: womm spell setup <project_name>")

            # Display status with nice formatting (from original display_project_status)
            print("")
            configured_text = "✅" if status.get("config_exists") else "❌"
            print_system(f"Project configured: {configured_text}")

            if status.get("config_path"):
                print_system(f"Config file: {status['config_path']}")

            if status.get("words_count"):
                print_info(f"Custom words: {status['words_count']}")

            return SpellResult(
                success=True,
                message="Project status retrieved successfully",
                data=status,
            )

        except Exception as e:
            print_error(f"❌ Error getting project status: {e}")
            return SpellResult(
                success=False,
                message=f"Failed to get status: {e}",
                error="status_failed",
            )

    def add_words(
        self, words: List[str], project_path: Optional[Path] = None
    ) -> SpellResult:
        """Add words to CSpell configuration with integrated UI."""
        if project_path is None:
            project_path = Path.cwd()

        print_system(f"Adding {len(words)} words to CSpell configuration...")

        try:
            with create_spinner_with_status("Adding words to configuration...") as (
                progress,
                task,
            ):
                progress.update(task, status="Validating configuration...")

                # Use cspell_utils for the actual operation
                from ...utils.spell.cspell_utils import add_words_to_config

                progress.update(task, status="Adding words...")
                success = add_words_to_config(project_path, words)

                if success:
                    progress.update(task, status="Words added successfully!")
                    print_success("✅ Added words to CSpell configuration")
                    return SpellResult(
                        success=True,
                        message=f"Added {len(words)} words to configuration",
                    )
                else:
                    progress.update(task, status="Failed to add words")
                    print_error("❌ Failed to add words to configuration")
                    return SpellResult(
                        success=False,
                        message="Failed to add words to configuration",
                        error="add_words_failed",
                    )

        except Exception as e:
            print_error(f"❌ Error adding words: {e}")
            return SpellResult(
                success=False,
                message=f"Failed to add words: {e}",
                error="add_words_failed",
            )

    def perform_add_words(
        self,
        words: Optional[List[str]] = None,
        file_path: Optional[Path] = None,
        interactive: bool = False,
        project_path: Optional[Path] = None,
    ) -> SpellResult:
        """Add words to CSpell configuration with integrated UI and option handling."""
        if project_path is None:
            project_path = Path.cwd()

        print_header("➕ Add Words to CSpell Configuration")

        # Check CSpell availability - early return if not available
        cspell_check = self._ensure_cspell_available("add words")
        if cspell_check is not None:  # Error occurred
            return cspell_check

        try:
            # Handle interactive mode
            if interactive:
                print_info("📝 Interactive mode: Enter word to add")
                word = input("Enter word to add: ").strip()
                if word:
                    words = [word]
                    print_success(f"✅ Word '{word}' queued for addition")
                else:
                    print_error("❌ No word provided")
                    return SpellResult(
                        success=False,
                        message="No word provided",
                        error="no_word_provided",
                    )

            # Handle file input
            if file_path:
                print_info(f"📄 Adding words from file: {file_path}")

                if not file_path.exists():
                    print_error(f"❌ File not found: {file_path}")
                    return SpellResult(
                        success=False,
                        message=f"File not found: {file_path}",
                        error="file_not_found",
                    )

                try:
                    words = file_path.read_text(encoding="utf-8").splitlines()
                    words = [w.strip() for w in words if w.strip()]

                    if not words:
                        print_error("❌ No words found in file")
                        return SpellResult(
                            success=False,
                            message="No words found in file",
                            error="no_words_in_file",
                        )

                    return self.add_words(words, project_path)

                except Exception as e:
                    print_error(f"❌ Failed to read file: {e}")
                    return SpellResult(
                        success=False,
                        message=f"Failed to add words from file: {e}",
                        error="file_read_failed",
                    )

            # Handle command line words
            elif words:
                print_info(f"📝 Adding {len(words)} words from command line")
                return self.add_words(words, project_path)

            # No input provided
            else:
                print_error("❌ No input provided")
                print_info("💡 Specify words, --file, or --interactive")
                return SpellResult(
                    success=False,
                    message="Specify words, --file, or --interactive",
                    error="no_input_provided",
                )

        except Exception as e:
            print_error(f"❌ Error during word addition: {e}")
            return SpellResult(
                success=False,
                message=f"Failed to add words: {e}",
                error="add_words_failed",
            )

    def perform_add_all_dictionaries(
        self, force: bool = False, project_path: Optional[Path] = None
    ) -> SpellResult:
        """Add all dictionaries from .cspell-dict/ to CSpell configuration with integrated UI."""
        if project_path is None:
            project_path = Path.cwd()

        print_header("📚 Add All Dictionaries")

        # Check CSpell availability - early return if not available
        cspell_check = self._ensure_cspell_available("add dictionaries")
        if cspell_check is not None:  # Error occurred
            return cspell_check

        try:
            # Get dictionary information
            from ...utils.spell.dictionary_utils import get_dictionary_info

            dict_info = get_dictionary_info()

            # Check if directory exists
            if not dict_info["directory_exists"]:
                print_error("❌ .cspell-dict directory not found")
                print_info("💡 Create the directory and add dictionary files (.txt)")
                return SpellResult(
                    success=False,
                    message=".cspell-dict directory not found",
                    error="dict_dir_not_found",
                )

            # Check if directory is empty
            if dict_info["total_files"] == 0:
                print_error("❌ .cspell-dict directory is empty")
                print_info("💡 Add .txt files with one word per line")
                return SpellResult(
                    success=False,
                    message=".cspell-dict directory is empty",
                    error="dict_dir_empty",
                )

            # Show what will be added
            print_info("📚 Dictionary Information")
            status_text = "✅" if dict_info["directory_exists"] else "❌"
            print_system(f"  Directory exists: {status_text}")
            print_system(f"  Total files: {dict_info['total_files']}")
            if dict_info["files"]:
                print_system("  Files:")
                for file_path in dict_info["files"]:
                    print_system(f"    - {file_path}")

            # Confirm unless --force
            if not force:
                response = (
                    input("Continue with adding all dictionaries? (y/N): ")
                    .lower()
                    .strip()
                )
                if response not in ["y", "yes"]:
                    print_info("ℹ️ Operation cancelled by user")
                    return SpellResult(
                        success=False,
                        message="Operation cancelled by user",
                        error="user_cancelled",
                    )

            # Add all dictionaries
            print_info(f"🔄 Processing {dict_info['total_files']} dictionary files...")
            success_count = 0
            error_count = 0

            for file_path in dict_info["files"]:
                try:
                    # Read words from file directly
                    words = Path(file_path).read_text(encoding="utf-8").splitlines()
                    words = [w.strip() for w in words if w.strip()]

                    if words:
                        result = self.add_words(words, project_path)
                        if result.success:
                            success_count += 1
                            print_system(f"  ✅ {file_path}")
                        else:
                            error_count += 1
                            print_system(f"  ❌ {file_path}")
                    else:
                        error_count += 1
                        print_system(f"  ❌ {file_path} (no words found)")

                except Exception as e:
                    error_count += 1
                    print_system(f"  ❌ {file_path} (error: {e})")

            # Return results
            if error_count == 0:
                print_success(f"✅ All {success_count} dictionaries added successfully")
                return SpellResult(
                    success=True,
                    message=f"All {success_count} dictionaries added successfully",
                )
            elif success_count > 0:
                print_success(
                    f"✅ {success_count} dictionaries added, {error_count} failed"
                )
                return SpellResult(
                    success=True,
                    message=f"{success_count} dictionaries added, {error_count} failed",
                )
            else:
                print_error("❌ No dictionaries could be added")
                return SpellResult(
                    success=False,
                    message="No dictionaries could be added",
                    error="all_dictionaries_failed",
                )

        except Exception as e:
            print_error(f"❌ Error processing dictionaries: {e}")
            return SpellResult(
                success=False,
                message=f"Failed to add dictionaries: {e}",
                error="add_all_failed",
            )

    def perform_list_dictionaries(
        self, project_path: Optional[Path] = None
    ) -> SpellResult:
        """List available dictionaries in .cspell-dict/ with integrated UI."""
        if project_path is None:
            project_path = Path.cwd()

        print_header("📚 Available Dictionaries")

        try:
            from ...utils.spell.dictionary_utils import get_dictionary_info

            dict_info = get_dictionary_info()

            # Display dictionary information
            status_text = "✅" if dict_info["directory_exists"] else "❌"
            print_system(f"  Directory exists: {status_text}")
            print_system(f"  Total files: {dict_info['total_files']}")

            if dict_info["files"]:
                print_system("  Files:")
                for file_path in dict_info["files"]:
                    print_system(f"    - {file_path}")
            else:
                print_info("💡 No dictionary files found in .cspell-dict/")

            return SpellResult(
                success=True,
                message="Dictionary list retrieved successfully",
                data=dict_info,
            )

        except Exception as e:
            print_error(f"❌ Error listing dictionaries: {e}")
            return SpellResult(
                success=False,
                message=f"Failed to list dictionaries: {e}",
                error="list_failed",
            )

    def perform_spell_check(
        self,
        path: Optional[Path] = None,
        json_output: Optional[Path] = None,
    ) -> SpellResult:
        """Perform complete spell check with integrated UI and availability checks."""
        if path is None:
            path = Path.cwd()

        # Show header first
        print_header("🔍 CSpell Spell Check")

        # Show start message
        print_info(f"🔍 Starting spell check for: {path}")
        print_debug(f"Debug: path={path}")

        # Check CSpell availability - early return if not available
        cspell_check = self._ensure_cspell_available("spell check")
        if cspell_check is not None:  # Error occurred
            return cspell_check

        try:
            with create_spinner_with_status("Running spell check...") as (
                progress,
                task,
            ):
                progress.update(task, status="Initializing spell check...")

                # Use cspell_utils for the actual operation
                from ...utils.spell.cspell_utils import run_spellcheck

                progress.update(task, status=f"Processing {path}...")

                spell_results = run_spellcheck(path)

                if spell_results["success"]:
                    progress.update(task, status="Spell check completed!")
                    progress.stop()
                    print("")

                    # Afficher le résumé
                    summary = spell_results["summary"]
                    issues = spell_results["issues"]

                    if issues:
                        print_warn(
                            f"⚠️  Spell check completed with {summary['issues_found']} issues found in {summary['files_checked']} files"
                        )
                        message = f"Spell check completed with {summary['issues_found']} issues found"
                    else:
                        print_success(
                            "✅ Spell check completed successfully - No issues found"
                        )
                        message = "Spell check completed successfully - No issues found"

                    # Afficher les erreurs si présentes avec tableau optimisé
                    if issues:
                        print_debug(f"📋 Found {len(issues)} spelling issues:")
                        print("")

                        # Utiliser la fonction UI dédiée pour afficher le tableau
                        from ...ui.spell.spell import display_spell_issues_table

                        display_spell_issues_table(issues)
                        print("")

                    # Export JSON si demandé
                    if json_output is not None:
                        self._export_spell_results_to_json(
                            path, summary, issues, json_output
                        )

                    return SpellResult(
                        success=True,
                        message=message,
                        data={
                            "path": str(path),
                            "summary": summary,
                            "issues": issues,
                            "json_output": json_output,
                        },
                    )
                else:
                    progress.update(task, status="Spell check failed")
                    print_error("❌ Spell check failed")
                    message = "Spell check failed"

                    print_error("❌ Spell check failed: spellcheck_failed")

                    return SpellResult(
                        success=False,
                        message=message,
                        error="spellcheck_failed",
                        data={"path": str(path)},
                    )

        except Exception as e:
            print_error(f"❌ Error during spell check: {e}")
            return SpellResult(
                success=False,
                message=f"Spell check error: {e}",
                error="spellcheck_failed",
            )

    def _export_spell_results_to_json(
        self,
        path: Path,
        summary: dict,
        issues: list,
        export_path: Path,
    ) -> None:
        """Export spell check results to JSON file."""
        try:
            # Le chemin d'export est déjà déterminé dans spell_check
            export_dir = export_path

            # Créer le dossier d'export s'il n'existe pas
            export_dir.mkdir(parents=True, exist_ok=True)

            # Générer un nom de fichier unique avec timestamp
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = path.name if path.is_file() else path.name
            filename = f"spell-check_{project_name}_{timestamp}.json"
            export_file = export_dir / filename

            # Préparer les données à exporter
            export_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "path": str(path),
                    "project_name": project_name,
                    "export_file": str(export_file),
                },
                "summary": summary,
                "issues": issues,
                "files_analysis": {},
            }

            # Ajouter une analyse par fichier
            files_issues = {}
            for issue in issues:
                file_path = issue["file"]
                if file_path not in files_issues:
                    files_issues[file_path] = []
                files_issues[file_path].append(issue)

            for file_path, file_issues_list in files_issues.items():
                export_data["files_analysis"][file_path] = {
                    "total_issues": len(file_issues_list),
                    "issues": file_issues_list,
                }

            # Écrire le fichier JSON
            import json

            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print_success(f"✅ Results exported to: {export_file}")
            print_system(
                f"📊 Summary: {summary['issues_found']} issues in {summary['files_checked']} files"
            )

        except Exception as e:
            print_error(f"❌ Failed to export results: {e}")


# GLOBAL INSTANCE
########################################################

spell_manager = SpellManager()
