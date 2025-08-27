#!/usr/bin/env python3
"""
Spell UI - Rich UI components for spell checking operations.
Separation of UI concerns from business logic following the Manager-Tools-UI pattern.
"""

from typing import Dict, List

from rich.table import Table

from ..common.console import console


def display_spell_issues_table(issues: List[Dict]) -> None:
    """
    Display spell check issues in a Rich table format.

    Args:
        issues: List of spelling issues with file, word, line information
    """
    if not issues:
        return

    # Créer un tableau pour un affichage plus clair
    table = Table(
        title="Spelling Issues Summary",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )

    table.add_column("File", style="cyan", width=30)
    table.add_column("Issues", style="yellow", justify="center", width=10)
    table.add_column("Sample Issues", style="white", width=50)

    # Grouper par fichier
    files_issues = {}
    for issue in issues:
        file_path = issue["file"]
        if file_path not in files_issues:
            files_issues[file_path] = []
        files_issues[file_path].append(issue)

    # Ajouter les lignes au tableau
    for file_path, file_issues_list in files_issues.items():
        # Créer un aperçu des erreurs
        sample_issues = []
        for issue in file_issues_list[:3]:  # Limiter à 3 exemples
            word = issue.get("word", "")
            line = issue.get("line", 0)
            if word and line > 0:
                sample_issues.append(f"'{word}' (l.{line})")
            elif word:
                sample_issues.append(f"'{word}'")

        sample_text = ", ".join(sample_issues)
        if len(file_issues_list) > 3:
            sample_text += f" (+{len(file_issues_list) - 3} more)"

        table.add_row(str(file_path), str(len(file_issues_list)), sample_text)

    console.print(table)


def display_spell_summary(summary: Dict, issues: List[Dict]) -> None:
    """
    Display spell check summary information.

    Args:
        summary: Summary statistics from spell check
        issues: List of issues found
    """
    from ..common.console import print_success, print_warn

    if issues:
        print_warn(
            f"⚠️  Spell check completed with {summary['issues_found']} issues found in {summary['files_checked']} files"
        )
    else:
        print_success("✅ Spell check completed successfully - No issues found")


def display_spell_status_table(status: Dict[str, str]) -> None:
    """
    Display CSpell project status in table format.

    Args:
        status: Status information about CSpell configuration
    """
    # Cette fonction sera implémentée si nécessaire
    # Pour l'instant, on garde l'affichage simple dans spell_manager


def create_spell_progress_table(files: List[str]) -> None:
    """
    Create a progress table for spell checking multiple files.

    Args:
        files: List of files being processed
    """
    # Cette fonction sera implémentée si nécessaire
    # Pour l'instant, on utilise les spinners existants
