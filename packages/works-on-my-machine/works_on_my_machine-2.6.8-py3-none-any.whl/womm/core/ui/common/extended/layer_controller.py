#!/usr/bin/env python3
"""
Layer Controller for Dynamic Progress Bars.

This module provides utilities for managing individual layers within
dynamic progress bar systems.
"""

# IMPORTS
########################################################
# Standard library imports
from enum import Enum
from typing import Dict, List, Optional

# Third-party imports
from rich.progress import Progress

# Local imports

# ENUMS
########################################################
# Layer state management


class LayerState(Enum):
    """Represents the current state of a layer."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"


class LayerType(Enum):
    """Represents the type of a layer."""

    PROGRESS = "progress"
    STEPS = "steps"
    SPINNER = "spinner"
    DOWNLOAD = "download"


# MAIN CLASS
########################################################
# Layer management class


class LayerController:
    """Manages individual layers within a dynamic progress bar.

    This class handles the lifecycle of individual layers including
    creation, updates, completion, and removal with fine-grained control.
    """

    def __init__(self, progress: Progress):
        """Initialize the layer controller.

        Args:
            progress: Rich Progress instance to manage
        """
        self.progress = progress
        self.layers = {}  # task_id -> layer_metadata
        self.active_layers = []  # List of active task IDs
        self.completed_layers = []  # List of completed task IDs

    def create_layer(self, layer_config: Dict) -> int:
        """Create a new layer in the progress bar.

        Args:
            layer_config: Layer configuration dictionary containing:
                - name: Layer identifier name
                - type: Layer type (progress, steps, spinner, download)
                - description: Display description
                - style: Rich style string
                - total: Total items (for progress/download)
                - steps: List of step names (for steps type)
                - total_size: Total size in bytes (for download)
                - filename: Filename (for download)

        Returns:
            Task ID of the created layer
        """
        layer_name = layer_config.get("name", f"Layer_{len(self.layers)}")
        layer_type = LayerType(layer_config.get("type", "progress"))
        layer_desc = layer_config.get("description", layer_name)
        layer_style = layer_config.get("style", "default")

        # Initialize common fields for all layer types
        common_fields = {
            "details": "",  # Initialize details field for all types
        }

        # Create task based on layer type
        if layer_type == LayerType.STEPS:
            steps = layer_config.get("steps", [])
            task_id = self.progress.add_task(
                f"[{layer_style}]{layer_desc}",
                total=len(steps),
                steps=steps,
                **common_fields,
            )
        elif layer_type == LayerType.SPINNER:
            spinner_fields = {
                **common_fields,
                "status": "",  # Initialize status field for spinner
            }
            task_id = self.progress.add_task(
                f"[{layer_style}]{layer_desc}",
                total=None,  # Indeterminate
                **spinner_fields,
            )
        elif layer_type == LayerType.DOWNLOAD:
            total_size = layer_config.get("total_size", 100)
            filename = layer_config.get("filename", "")
            download_fields = {
                **common_fields,
                "filename": filename,
            }
            task_id = self.progress.add_task(
                f"[{layer_style}]{layer_desc}", total=total_size, **download_fields
            )
        else:  # LayerType.PROGRESS
            layer_total = layer_config.get("total")
            task_id = self.progress.add_task(
                f"[{layer_style}]{layer_desc}", total=layer_total, **common_fields
            )

        # Store layer metadata
        self.layers[task_id] = {
            "name": layer_name,
            "type": layer_type,
            "config": layer_config,
            "state": LayerState.ACTIVE,
            "created_description": f"[{layer_style}]{layer_desc}",
        }

        self.active_layers.append(task_id)
        return task_id

    def update_layer(self, task_id: int, progress_value: int, details: str = ""):
        """Update a layer's progress.

        Args:
            task_id: Task ID of the layer to update
            progress_value: Progress value (0-100 or step index)
            details: Additional details to display
        """
        if task_id not in self.layers:
            return

        layer_metadata = self.layers[task_id]
        layer_type = layer_metadata["type"]

        if layer_type == LayerType.STEPS:
            # Handle step-based layer
            task = self.progress._tasks[task_id]
            steps = getattr(task, "steps", [])

            if steps and progress_value < len(steps):
                current_step = steps[progress_value]
                step_progress = (
                    f"Step {progress_value + 1}/{len(steps)}: {current_step}"
                )

                self.progress.update(
                    task_id,
                    completed=progress_value,
                    description=f"{layer_metadata['created_description']} - {step_progress}",
                    details=details,
                )
            else:
                self.progress.update(task_id, completed=progress_value, details=details)
        elif layer_type == LayerType.SPINNER:
            # Handle spinner layer - update status message
            self.progress.update(
                task_id,
                status=details,  # Use details as status message
            )
        elif layer_type == LayerType.DOWNLOAD:
            # Handle download layer - update progress and details
            self.progress.update(task_id, completed=progress_value, details=details)
        else:  # LayerType.PROGRESS
            # Handle regular progress layer
            self.progress.update(task_id, completed=progress_value, details=details)

    def complete_layer(self, task_id: int):
        """Mark a layer as completed.

        Args:
            task_id: Task ID of the layer to complete
        """
        if task_id not in self.layers:
            return

        layer_metadata = self.layers[task_id]
        layer_type = layer_metadata["type"]

        # Mark as completed (100%)
        if layer_type == LayerType.STEPS:
            steps = layer_metadata["config"].get("steps", [])
            self.progress.update(task_id, completed=len(steps))
        elif layer_type == LayerType.SPINNER:
            # Spinners don't have completion progress, just update status
            self.progress.update(task_id, status="Completed")
        else:
            total = layer_metadata["config"].get("total", 100)
            if layer_type == LayerType.DOWNLOAD:
                total = layer_metadata["config"].get("total_size", 100)
            self.progress.update(task_id, completed=total)

        # Update metadata
        layer_metadata["state"] = LayerState.COMPLETED

    def remove_layer(self, task_id: int):
        """Remove a layer from the progress bar.

        Args:
            task_id: Task ID of the layer to remove
        """
        if task_id not in self.layers:
            return

        # Remove from progress bar
        self.progress.remove_task(task_id)

        # Update tracking lists
        if task_id in self.active_layers:
            self.active_layers.remove(task_id)

        # Move to completed list if not already there
        layer_name = self.layers[task_id]["name"]
        if layer_name not in self.completed_layers:
            self.completed_layers.append(layer_name)

        # Remove from layers dict
        del self.layers[task_id]

    def complete_and_remove_layer(self, task_id: int):
        """Complete a layer and then remove it (disappearing effect).

        Args:
            task_id: Task ID of the layer to complete and remove
        """
        self.complete_layer(task_id)
        self.remove_layer(task_id)

    def set_layer_error(self, task_id: int, error_message: str):
        """Mark a layer as having an error.

        Args:
            task_id: Task ID of the layer with error
            error_message: Error message to display
        """
        if task_id not in self.layers:
            return

        layer_metadata = self.layers[task_id]
        layer_metadata["state"] = LayerState.ERROR

        # Update with error styling
        self.progress.update(
            task_id,
            description=f"[red]{layer_metadata['created_description']}[/red]",
            details=f"[red]Error: {error_message}[/red]",
        )

    def pause_layer(self, task_id: int):
        """Pause a layer's progress.

        Args:
            task_id: Task ID of the layer to pause
        """
        if task_id not in self.layers:
            return

        layer_metadata = self.layers[task_id]
        layer_metadata["state"] = LayerState.PAUSED

        # Update with paused styling
        self.progress.update(
            task_id,
            description=f"[yellow]{layer_metadata['created_description']} (Paused)[/yellow]",
        )

    def resume_layer(self, task_id: int):
        """Resume a paused layer.

        Args:
            task_id: Task ID of the layer to resume
        """
        if task_id not in self.layers:
            return

        layer_metadata = self.layers[task_id]
        if layer_metadata["state"] == LayerState.PAUSED:
            layer_metadata["state"] = LayerState.ACTIVE

            # Restore original description
            self.progress.update(
                task_id, description=layer_metadata["created_description"]
            )

    def get_active_layers(self) -> List[int]:
        """Get list of currently active layer task IDs.

        Returns:
            List of active task IDs
        """
        return self.active_layers.copy()

    def get_layer_info(self, task_id: int) -> Optional[Dict]:
        """Get information about a specific layer.

        Args:
            task_id: Task ID of the layer

        Returns:
            Layer metadata dictionary or None if not found
        """
        return self.layers.get(task_id)

    def get_layers_by_state(self, state: LayerState) -> List[int]:
        """Get layers filtered by their state.

        Args:
            state: Layer state to filter by

        Returns:
            List of task IDs with the specified state
        """
        return [
            task_id
            for task_id, metadata in self.layers.items()
            if metadata["state"] == state
        ]

    def get_layers_by_type(self, layer_type: LayerType) -> List[int]:
        """Get layers filtered by their type.

        Args:
            layer_type: Layer type to filter by

        Returns:
            List of task IDs with the specified type
        """
        return [
            task_id
            for task_id, metadata in self.layers.items()
            if metadata["type"] == layer_type
        ]
