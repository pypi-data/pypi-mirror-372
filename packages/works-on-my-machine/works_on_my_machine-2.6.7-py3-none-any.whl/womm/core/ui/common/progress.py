#!/usr/bin/env python3
"""
Progress utilities using Rich for beautiful progress bars.
"""

# IMPORTS
########################################################
# Standard library imports
import time
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional, Tuple

# Third-party imports
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

# Local imports
from .console import PATTERN_COLORS

# CONFIGURATION
########################################################
# Global variables and settings

console = Console()

pattern_color = PATTERN_COLORS.get("SYSTEM", "white")

# Build prefix with Rich markup
prefix = f"[{pattern_color}]• [bold {pattern_color}]{'SYSTEM'.ljust(8)}[/bold {pattern_color}][dim white]:: [/dim white]"


# MAIN FUNCTIONS
########################################################
# Core progress bar functionality


@contextmanager
def create_progress(
    description: str = "Working...",
    total: Optional[int] = None,
    transient: bool = False,
):
    """Create a progress bar context manager."""
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=transient,
    )

    with progress:
        task = progress.add_task(description, total=total)
        yield progress, task


# SPINNER FUNCTIONS
########################################################
# Spinner-based progress indicators


@contextmanager
def create_spinner(
    description: str = "Working...",
) -> Generator[Tuple[Progress, int], None, None]:
    """Create a simple spinner with description."""
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=None)
        yield progress, task


@contextmanager
def create_spinner_with_status(
    description: str = "Working...",
) -> Generator[Tuple[Progress, int], None, None]:
    """Create a spinner that can update status messages."""
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[dim]{task.fields[status]}"),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=None, status="")
        yield progress, task


# DOWNLOAD FUNCTIONS
########################################################
# File download progress indicators


@contextmanager
def create_download_progress(
    description: str = "Downloading...",
) -> Generator[Tuple[Progress, int], None, None]:
    """Create a download progress bar with speed and size information."""
    progress = Progress(
        TextColumn(prefix),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        DownloadColumn(),
        TransferSpeedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=100)
        yield progress, task


@contextmanager
def create_file_download_progress(
    filename: str, total_size: int, description: str = "Downloading file..."
) -> Generator[Tuple[Progress, int], None, None]:
    """
    Create a progress bar for downloading a specific file.

    Args:
        filename: Name of the file being downloaded
        total_size: Total size in bytes
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TextColumn("[dim]{task.fields[filename]}"),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=total_size, filename=filename)
        yield progress, task


# DEPENDENCY FUNCTIONS
########################################################
# Dependency installation and management progress


@contextmanager
def create_dependency_progress(
    dependencies: List[str], description: str = "Installing dependencies..."
) -> Generator[Tuple[Progress, int, str], None, None]:
    """
    Create a progress bar for dependency installation.

    Args:
        dependencies: List of dependency names
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}"),
        TextColumn("[dim]Dependency {task.fields[current]}/{task.fields[total]}"),
        TextColumn("[dim]{task.fields[dependency]}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(
            description,
            total=len(dependencies),
            current=1,
            total_deps=len(dependencies),
            dependency="",
        )

        for i, dependency in enumerate(dependencies):
            progress.update(
                task,
                description=f"[bold green]Installing {dependency}",
                current=i + 1,
                dependency=dependency,
            )
            yield progress, task, dependency
            progress.advance(task)
            time.sleep(0.1)


@contextmanager
def create_package_install_progress(
    packages: List[Tuple[str, str]], description: str = "Installing packages..."
) -> Generator[Tuple[Progress, int, str, str], None, None]:
    """
    Create a progress bar for package installation with version info.

    Args:
        packages: List of tuples (package_name, version)
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        TextColumn("[dim]Package {task.fields[current]}/{task.fields[total]}"),
        TextColumn("[dim]{task.fields[package]}"),
        TextColumn("[dim]{task.fields[version]}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(
            description,
            total=len(packages),
            current=1,
            total_packages=len(packages),
            package="",
            version="",
        )

        for i, (package_name, version) in enumerate(packages):
            progress.update(
                task,
                description=f"[bold cyan]Installing {package_name}",
                current=i + 1,
                package=package_name,
                version=version,
            )
            yield progress, task, package_name, version
            progress.advance(task)
            time.sleep(0.1)


# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def track_installation_steps(steps: list, description: str = "Installation Progress"):
    """Track installation steps with progress bar."""
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=len(steps))

        for i, step in enumerate(steps):
            progress.update(task, description=f"Step {i + 1}/{len(steps)}: {step}")
            yield step
            progress.advance(task)


# STEP-BASED PROGRESS FUNCTIONS
########################################################
# Step-based progress bar implementations


@contextmanager
def create_step_progress(
    steps: List[str],
    description: str = "Processing...",
    show_step_numbers: bool = True,
    show_time: bool = True,
):
    """
    Create a step-based progress bar with detailed step information.

    Args:
        steps: List of step names
        description: Main description
        show_step_numbers: Show step numbers (e.g., "Step 1/5")
        show_time: Show elapsed and remaining time
    """
    # Build columns based on options
    columns = [
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
    ]

    if show_step_numbers:
        columns.append(
            TextColumn("[dim]Step {task.fields[step]}/{task.fields[total_steps]}")
        )

    columns.extend(
        [
            TextColumn("[dim]{task.fields[current_step]}"),
            BarColumn(),
            TaskProgressColumn(),
        ]
    )

    if show_time:
        columns.extend(
            [
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ]
        )

    progress = Progress(*columns, console=console)

    with progress:
        task = progress.add_task(
            description,
            total=len(steps),
            step=1,
            total_steps=len(steps),
            current_step="",
        )

        # Return the progress, task and steps for the context manager
        yield progress, task, steps

        # The caller will iterate through steps and call advance manually


@contextmanager
def create_file_copy_progress(
    files: List[str],
    description: str = "Copying files...",
) -> Generator[Tuple[Progress, int, str], None, None]:
    """
    Create a progress bar specifically for file copying operations.

    Args:
        files: List of file paths to copy
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold magenta]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[current_file]}"),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=len(files), current_file="")

        # Return the progress and task for the context manager
        yield progress, task, files

        # The caller will iterate through files and call advance manually


@contextmanager
def create_installation_progress(
    steps: List[Tuple[str, str]],
    description: str = "Installation in progress...",
):
    """
    Create a progress bar for installation processes with step details.

    Args:
        steps: List of tuples (step_name, step_description)
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}"),
        TextColumn("[dim]Step {task.fields[step]}/{task.fields[total_steps]}"),
        TextColumn("[dim]{task.fields[step_detail]}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(
            description,
            total=len(steps),
            step=1,
            total_steps=len(steps),
            step_detail="",
        )

        for i, (step_name, step_detail) in enumerate(steps):
            progress.update(
                task,
                description=f"[bold green]{step_name}",
                step=i + 1,
                step_detail=step_detail,
            )
            yield progress, task, step_name, step_detail
            progress.advance(task)
            time.sleep(0.1)


@contextmanager
def create_build_progress(
    phases: List[Tuple[str, int]],
    description: str = "Building project...",
):
    """
    Create a progress bar for build processes with weighted phases.

    Args:
        phases: List of tuples (phase_name, weight_percentage)
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        TextColumn("[dim]{task.fields[current_phase]}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[bold yellow]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=100, current_phase="")

        current_progress = 0
        for phase_name, weight in phases:
            progress.update(task, current_phase=phase_name)
            yield progress, task, phase_name, weight
            current_progress += weight
            progress.update(task, completed=current_progress)


@contextmanager
def create_deployment_progress(
    stages: List[str],
    description: str = "Deploying...",
):
    """
    Create a progress bar for deployment processes.

    Args:
        stages: List of deployment stage names
        description: Main description
    """
    progress = Progress(
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold magenta]{task.description}"),
        TextColumn("[dim]Stage {task.fields[stage]}/{task.fields[total_stages]}"),
        TextColumn("[dim]{task.fields[current_stage]}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(
            description,
            total=len(stages),
            stage=1,
            total_stages=len(stages),
            current_stage="",
        )

        for i, stage in enumerate(stages):
            progress.update(
                task,
                description=f"[bold magenta]{stage}",
                stage=i + 1,
                current_stage=stage,
            )
            yield progress, task, stage
            progress.advance(task)
            time.sleep(0.1)


# LAYERED PROGRESS FUNCTIONS
########################################################
# Multi-level progress bar implementations


@contextmanager
def create_layered_progressbar(
    layers: List[Dict[str, any]],
    show_time: bool = True,
) -> Generator[Tuple[Progress, Dict[str, int]], None, None]:
    """
    Create a multi-level progress bar with dynamic layers.

    Args:
        layers: List of layer configurations, each containing:
            - 'name': Layer name/description
            - 'total': Total items for this layer (optional, None for indeterminate)
            - 'description': Display description for the layer
            - 'style': Rich style for this layer (optional)
            - 'type': Layer type - 'progress' (default) or 'steps'
            - 'steps': List of step names (required if type='steps')
        show_time: Show elapsed and remaining time

    Returns:
        Tuple of (progress_object, task_ids_dict)
    """
    # Build columns for the main progress bar
    columns = [
        TextColumn(prefix),
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[details]}"),  # Additional details column
    ]

    if show_time:
        columns.extend(
            [
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ]
        )

    progress = Progress(*columns, console=console)

    with progress:
        # Create tasks for each layer
        task_ids = {}

        for i, layer in enumerate(layers):
            layer_name = layer.get("name", f"Layer_{i}")
            layer_type = layer.get("type", "progress")
            layer_desc = layer.get("description", layer_name)
            layer_style = layer.get("style", "default")

            if layer_type == "steps":
                # Handle step-based layer
                steps = layer.get("steps", [])
                layer_total = len(steps)
                task_id = progress.add_task(
                    f"[{layer_style}]{layer_desc}",
                    total=layer_total,
                    details="",  # Initialize details field
                    steps=steps,  # Store steps for later use
                )
            else:
                # Handle regular progress layer
                layer_total = layer.get("total", None)
                task_id = progress.add_task(
                    f"[{layer_style}]{layer_desc}",
                    total=layer_total,
                    details="",  # Initialize details field
                )

            task_ids[layer_name] = task_id

        yield progress, task_ids


def update_layer_step(
    progress: Progress, task_id: int, step_index: int, details: str = ""
):
    """
    Update a step-based layer to show current step progress.

    Args:
        progress: Progress object
        task_id: Task ID of the layer
        step_index: Current step index (0-based)
        step_name: Name of the current step
        details: Additional details to display
    """
    # Get the task to access stored steps
    task = progress._tasks[task_id]
    steps = getattr(task, "steps", [])

    if steps and step_index < len(steps):
        current_step = steps[step_index]
        step_progress = f"Step {step_index + 1}/{len(steps)}: {current_step}"

        # Update the task with step information
        progress.update(
            task_id,
            completed=step_index,
            description=f"{task.description} - {step_progress}",
            details=details,
        )
    else:
        # Fallback if no steps available
        progress.update(task_id, completed=step_index, details=details)
