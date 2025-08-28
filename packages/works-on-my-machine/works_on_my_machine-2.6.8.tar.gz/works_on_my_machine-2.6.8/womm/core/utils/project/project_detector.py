#!/usr/bin/env python3
"""
Universal project type detector for Dev Tools.

This module automatically detects the project type (Python, JavaScript, etc.)
and launches the appropriate tool for creation or configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ProjectDetector:
    """Project type detector based on present files."""

    # Sensitive file patterns to exclude from scan
    SECURITY_EXCLUSIONS = [
        ".env*",
        ".secret*",
        "*password*",
        "*secret*",
        "*.key",
        "*.pem",
        "*.crt",
        "credentials/**",
        "keys/**",
    ]

    # File signatures to detect project type
    PROJECT_SIGNATURES = {
        "python": {
            "files": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"],
            "dirs": ["venv", ".venv", "__pycache__"],
            "extensions": [".py"],
            "priority": 10,
            "description": "Python Project",
        },
        "javascript": {
            "files": [
                "package.json",
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",
            ],
            "dirs": ["node_modules", ".npm"],
            "extensions": [".js", ".jsx", ".ts", ".tsx"],
            "priority": 10,
            "description": "JavaScript/Node.js Project",
        },
        "react": {
            "files": ["package.json"],
            "dirs": ["node_modules", "public", "src"],
            "extensions": [".jsx", ".tsx"],
            "content_markers": {"package.json": ['"react":', '"@types/react":']},
            "priority": 15,
            "description": "React Project",
        },
        "vue": {
            "files": ["package.json"],
            "dirs": ["node_modules"],
            "extensions": [".vue"],
            "content_markers": {"package.json": ['"vue":', '"@vue/']},
            "priority": 15,
            "description": "Vue.js Project",
        },
        "generic": {
            "files": [],
            "dirs": [],
            "extensions": [],
            "priority": 1,
            "description": "Generic Project",
        },
    }

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize the project type detector."""
        self.project_path = project_path or Path.cwd()

    def detect_project_type(self) -> Tuple[str, int]:
        """
        Detect the project type.

        Returns:
            Tuple (project_type, confidence_score)
        """
        scores = {}

        for project_type, signature in self.PROJECT_SIGNATURES.items():
            if project_type == "generic":
                continue

            score = self._calculate_score(signature)
            if score > 0:
                scores[project_type] = score

        if not scores:
            return "generic", 0

        # Return the type with the best score
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type[0], best_type[1]

    def _is_security_excluded(self, file_path: Path) -> bool:
        """Check if a file is excluded for security reasons."""
        file_str = str(file_path)
        file_name = file_path.name.lower()
        for pattern in self.SECURITY_EXCLUSIONS:
            # Handle simple patterns
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(file_name, pattern.lower()):
                    return True
                if fnmatch.fnmatch(file_str.lower(), pattern.lower()):
                    return True
            else:
                # Exact match
                if pattern in file_name or pattern in file_str.lower():
                    return True

        return False

    def _calculate_score(self, signature: Dict) -> int:
        """Calculate the matching score for a signature."""
        score = 0

        # Check files
        for file_pattern in signature.get("files", []):
            file_path = self.project_path / file_pattern
            if file_path.exists() and not self._is_security_excluded(file_path):
                score += signature.get("priority", 1)

        # Check directories
        for dir_pattern in signature.get("dirs", []):
            dir_path = self.project_path / dir_pattern
            if dir_path.exists() and not self._is_security_excluded(dir_path):
                score += signature.get("priority", 1) // 2

        # Check extensions with security exclusion
        extensions = signature.get("extensions", [])
        if extensions:
            found_files = 0
            for ext in extensions:
                for file_path in self.project_path.glob(f"**/*{ext}"):
                    if not self._is_security_excluded(file_path):
                        found_files += 1
                        break  # One file per extension is enough

            if found_files > 0:
                score += min(found_files, 3) * (signature.get("priority", 1) // 3)

        # Check content markers with security exclusion
        content_markers = signature.get("content_markers", {})
        for file_name, markers in content_markers.items():
            file_path = self.project_path / file_name
            if file_path.exists() and not self._is_security_excluded(file_path):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    for marker in markers:
                        if marker in content:
                            score += signature.get("priority", 1)
                except Exception as e:
                    logging.debug(
                        f"Failed to read file {file_path}: {e}"
                    )  # Ignore read errors

        return score

    def get_available_types(self) -> List[Tuple[str, str]]:
        """Return the list of available project types."""
        return [
            (ptype, signature["description"])
            for ptype, signature in self.PROJECT_SIGNATURES.items()
            if ptype != "generic"
        ]


def interactive_project_selection() -> str:
    """
    Interactive interface to select project type.

    TODO: This function contains UI logic and should be moved to ui/ package.
    For now, logging statements replace print() to maintain functionality.
    """
    detector = ProjectDetector()
    available_types = detector.get_available_types()

    logging.info("🎯 What type of project do you want to create?")

    for i, (_ptype, description) in enumerate(available_types, 1):
        logging.info(f"{i}. {description}")

    logging.info(f"{len(available_types) + 1}. Automatic detection")

    while True:
        try:
            choice = input("Your choice (number): ").strip()

            if choice == str(len(available_types) + 1):
                # Automatic detection
                detected_type, confidence = detector.detect_project_type()
                if confidence > 0:
                    logging.info(
                        f"✅ Detected: {detector.PROJECT_SIGNATURES[detected_type]['description']}"
                    )
                    return detected_type
                else:
                    logging.warning("⚠️  No type detected, using Python type by default")
                    return "python"

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_types):
                selected_type = available_types[choice_idx][0]
                logging.info(f"✅ Selected: {available_types[choice_idx][1]}")
                return selected_type
            else:
                logging.warning("❌ Invalid choice, please try again")

        except (ValueError, KeyboardInterrupt):
            logging.warning("❌ Invalid choice, please try again")


def launch_project_setup(
    project_type: str, project_name: Optional[str] = None, current_dir: bool = False
):
    """Launch the appropriate setup script."""
    devtools_path = Path(__file__).parent.parent

    if project_type in ["python"]:
        script_path = (
            devtools_path / "languages" / "python" / "scripts" / "setup_project.py"
        )
    elif project_type in ["javascript", "react", "vue"]:
        script_path = (
            devtools_path / "languages" / "javascript" / "scripts" / "setup_project.py"
        )
    else:
        logging.error(f"❌ Project type '{project_type}' not supported")
        return 1

    if not script_path.exists():
        logging.error(f"❌ Script not found: {script_path}")
        return 1

    # Build command
    cmd = [sys.executable, str(script_path)]

    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    # Add type for JavaScript
    if project_type in ["react", "vue", "javascript"]:
        js_type = "node" if project_type == "javascript" else project_type
        cmd.extend(["--type", js_type])

    logging.info(f"🚀 Launching: {' '.join(cmd)}")

    # Launch script
    from ...utils.cli_utils import run_command

    result = run_command(cmd, f"Configuring {project_type} project")
    return 0 if result.success else 1


def main():
    """Run the universal detector main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal project detector and creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Interactive mode
    new-project

    # Direct creation
    new-project my-project

    # Configure current directory
    new-project --current-dir

    # With specific type
    new-project my-api --type=python
        """,
    )

    parser.add_argument("project_name", nargs="?", help="Name of the project to create")
    parser.add_argument(
        "--current-dir", action="store_true", help="Configure current directory"
    )
    parser.add_argument(
        "--type",
        choices=["python", "javascript", "react", "vue"],
        help="Specific project type",
    )
    parser.add_argument(
        "--detect", action="store_true", help="Only detect project type"
    )

    args = parser.parse_args()

    # Detection mode only
    if args.detect:
        detector = ProjectDetector()
        detected_type, confidence = detector.detect_project_type()
        logging.info(f"Detected type: {detected_type} (confidence: {confidence})")
        return 0

    # Determine project type
    if args.type:
        project_type = args.type
        logging.info(f"🎯 Specified type: {project_type}")
    elif args.current_dir:
        # Automatically detect for current directory
        detector = ProjectDetector()
        project_type, confidence = detector.detect_project_type()

        if confidence > 0:
            logging.info(
                f"✅ Detected type: {detector.PROJECT_SIGNATURES[project_type]['description']}"
            )
        else:
            logging.warning("⚠️  No type detected, manual selection required")
            project_type = interactive_project_selection()
    else:
        # Interactive mode
        project_type = interactive_project_selection()

    # Launch configuration
    return launch_project_setup(
        project_type=project_type,
        project_name=args.project_name,
        current_dir=args.current_dir,
    )


# NOTE: Main function removed - utility modules should not have main execution code.
# This function should be called from appropriate CLI modules instead.
