#!/usr/bin/env python3
"""
Progress Animations and Transitions.

This module provides animation utilities for smooth transitions
in dynamic progress bar systems.
"""

# IMPORTS
########################################################
# Standard library imports
import math
import time
from enum import Enum
from typing import Callable, Dict, List

# Third-party imports
from rich.progress import Progress

# ENUMS
########################################################
# Animation types and states


class AnimationType(Enum):
    """Types of animations available."""

    FADE_OUT = "fade_out"
    SLIDE_UP = "slide_up"
    SUCCESS_FLASH = "success_flash"
    ERROR_PULSE = "error_pulse"
    PROGRESS_SMOOTH = "progress_smooth"
    SPINNER_SPEED = "spinner_speed"


class AnimationState(Enum):
    """Animation states."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# ANIMATION CLASSES
########################################################
# Core animation classes


class Animation:
    """Base animation class."""

    def __init__(self, animation_type: AnimationType, duration: float = 0.5):
        self.type = animation_type
        self.duration = duration
        self.state = AnimationState.IDLE
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the animation."""
        self.state = AnimationState.RUNNING
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration

    def is_running(self) -> bool:
        """Check if animation is currently running."""
        if self.state != AnimationState.RUNNING:
            return False
        return time.time() < self.end_time

    def get_progress(self) -> float:
        """Get animation progress (0.0 to 1.0)."""
        if not self.is_running():
            return 1.0
        elapsed = time.time() - self.start_time
        return min(elapsed / self.duration, 1.0)

    def complete(self):
        """Mark animation as completed."""
        self.state = AnimationState.COMPLETED


class ProgressAnimations:
    """Provides animation utilities for progress bar transitions."""

    def __init__(self, progress: Progress):
        """Initialize animations with a progress instance.

        Args:
            progress: Rich Progress instance to animate
        """
        self.progress = progress
        self.active_animations: Dict[int, Animation] = {}
        self.animation_callbacks: Dict[AnimationType, Callable] = {
            AnimationType.FADE_OUT: self._fade_out_animation,
            AnimationType.SUCCESS_FLASH: self._success_flash_animation,
            AnimationType.ERROR_PULSE: self._error_pulse_animation,
            AnimationType.PROGRESS_SMOOTH: self._progress_smooth_animation,
        }

    def fade_out_layer(self, task_id: int, duration: float = 0.5):
        """Animate the fade-out of a completed layer.

        Args:
            task_id: Task ID of the layer to fade out
            duration: Duration of the fade-out animation in seconds
        """
        animation = Animation(AnimationType.FADE_OUT, duration)
        self.active_animations[task_id] = animation
        animation.start()

    def success_flash(self, task_id: int, duration: float = 0.3):
        """Flash a layer green briefly to indicate success.

        Args:
            task_id: Task ID of the layer to flash
            duration: Duration of the flash animation in seconds
        """
        animation = Animation(AnimationType.SUCCESS_FLASH, duration)
        self.active_animations[task_id] = animation
        animation.start()

    def error_pulse(self, task_id: int, duration: float = 1.0):
        """Pulse a layer red to indicate an error.

        Args:
            task_id: Task ID of the layer with error
            duration: Duration of the pulse animation in seconds
        """
        animation = Animation(AnimationType.ERROR_PULSE, duration)
        self.active_animations[task_id] = animation
        animation.start()

    def smooth_progress(self, task_id: int, target_value: int, duration: float = 0.5):
        """Smoothly animate progress to a target value.

        Args:
            task_id: Task ID of the layer to animate
            target_value: Target progress value
            duration: Duration of the animation in seconds
        """
        animation = Animation(AnimationType.PROGRESS_SMOOTH, duration)
        animation.target_value = target_value
        animation.start_value = self.progress._tasks[task_id].completed
        self.active_animations[task_id] = animation
        animation.start()

    def update_animations(self):
        """Update all active animations."""
        completed_animations = []

        for task_id, animation in self.active_animations.items():
            if animation.is_running():
                # Get the appropriate animation callback
                callback = self.animation_callbacks.get(animation.type)
                if callback:
                    callback(task_id, animation)
            else:
                completed_animations.append(task_id)

        # Clean up completed animations
        for task_id in completed_animations:
            animation = self.active_animations[task_id]
            animation.complete()
            del self.active_animations[task_id]

    def _fade_out_animation(self, task_id: int, animation: Animation):
        """Internal fade-out animation implementation."""
        progress = animation.get_progress()

        # Calculate opacity (1.0 to 0.0)
        opacity = 1.0 - progress

        # Apply fade effect by modifying the task description
        task = self.progress._tasks[task_id]
        original_desc = getattr(task, "_original_description", task.description)

        if not hasattr(task, "_original_description"):
            task._original_description = task.description

        # Apply opacity effect
        faded_desc = f"[dim]{original_desc}[/dim]" if opacity < 0.5 else original_desc
        self.progress.update(task_id, description=faded_desc)

    def _success_flash_animation(self, task_id: int, animation: Animation):
        """Internal success flash animation implementation."""
        progress = animation.get_progress()

        # Create a pulsing green effect
        intensity = abs(math.sin(progress * math.pi * 4))  # 2 pulses

        task = self.progress._tasks[task_id]
        original_desc = getattr(task, "_original_description", task.description)

        if not hasattr(task, "_original_description"):
            task._original_description = task.description

        # Apply green flash effect
        if intensity > 0.3:
            flash_desc = f"[bold green]{original_desc}[/bold green]"
        else:
            flash_desc = original_desc

        self.progress.update(task_id, description=flash_desc)

    def _error_pulse_animation(self, task_id: int, animation: Animation):
        """Internal error pulse animation implementation."""
        progress = animation.get_progress()

        # Create a pulsing red effect
        intensity = abs(math.sin(progress * math.pi * 6))  # 3 pulses

        task = self.progress._tasks[task_id]
        original_desc = getattr(task, "_original_description", task.description)

        if not hasattr(task, "_original_description"):
            task._original_description = task.description

        # Apply red pulse effect
        if intensity > 0.3:
            pulse_desc = f"[bold red]{original_desc}[/bold red]"
        else:
            pulse_desc = original_desc

        self.progress.update(task_id, description=pulse_desc)

    def _progress_smooth_animation(self, task_id: int, animation: Animation):
        """Internal smooth progress animation implementation."""
        progress = animation.get_progress()

        # Use easing function for smooth animation
        eased_progress = self._ease_out_quad(progress)

        # Calculate current value
        start_val = animation.start_value
        end_val = animation.target_value
        current_val = start_val + (end_val - start_val) * eased_progress

        # Update the progress
        self.progress.update(task_id, completed=int(current_val))

    def _ease_out_quad(self, t: float) -> float:
        """Easing function for smooth animations."""
        return t * (2 - t)

    def restore_original_description(self, task_id: int):
        """Restore the original description of a task."""
        task = self.progress._tasks[task_id]
        if hasattr(task, "_original_description"):
            self.progress.update(task_id, description=task._original_description)
            delattr(task, "_original_description")

    def clear_animations(self):
        """Clear all active animations."""
        for task_id in list(self.active_animations.keys()):
            self.restore_original_description(task_id)
        self.active_animations.clear()


# UTILITY FUNCTIONS
########################################################
# Animation utility functions


def smooth_transition(
    start_value: float,
    end_value: float,
    duration: float,
    callback: Callable[[float], None],
    fps: int = 60,
):
    """Execute a smooth transition between two values.

    Args:
        start_value: Starting value
        end_value: Ending value
        duration: Duration of transition in seconds
        callback: Function to call with current value during transition
        fps: Frames per second for the animation
    """
    frame_time = 1.0 / fps
    total_frames = int(duration * fps)

    for frame in range(total_frames + 1):
        progress = frame / total_frames
        # Use easing function for smooth animation
        eased_progress = progress * (2 - progress)  # ease-out-quad

        current_value = start_value + (end_value - start_value) * eased_progress
        callback(current_value)

        if frame < total_frames:
            time.sleep(frame_time)


def create_loading_animation(
    progress: Progress,
    task_id: int,
    messages: List[str],
    duration: float = 2.0,
):
    """Create a loading animation with cycling messages.

    Args:
        progress: Rich Progress instance
        task_id: Task ID to animate
        messages: List of messages to cycle through
        duration: Total duration of the animation
    """
    if not messages:
        return

    message_duration = duration / len(messages)

    for message in messages:
        progress.update(task_id, description=f"[bold blue]{message}")
        time.sleep(message_duration)


def create_progress_wave(
    progress: Progress,
    task_id: int,
    duration: float = 1.0,
):
    """Create a wave effect across the progress bar.

    Args:
        progress: Rich Progress instance
        task_id: Task ID to animate
        duration: Duration of the wave animation
    """
    fps = 30
    frame_time = 1.0 / fps
    total_frames = int(duration * fps)

    for frame in range(total_frames):
        progress_value = (frame / total_frames) * 100

        # Create wave effect
        wave_desc = f"[bold cyan]Progress: {progress_value:.1f}%[/bold cyan]"

        progress.update(task_id, completed=progress_value, description=wave_desc)
        time.sleep(frame_time)


# CONTEXT MANAGER
########################################################
# Animation context manager


class AnimatedProgress:
    """Context manager for animated progress bars."""

    def __init__(self, progress: Progress):
        """Initialize with a progress instance.

        Args:
            progress: Rich Progress instance
        """
        self.progress = progress
        self.animations = ProgressAnimations(progress)

    def __enter__(self):
        """Enter the animation context."""
        return self.animations

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the animation context and clean up."""
        self.animations.clear_animations()
