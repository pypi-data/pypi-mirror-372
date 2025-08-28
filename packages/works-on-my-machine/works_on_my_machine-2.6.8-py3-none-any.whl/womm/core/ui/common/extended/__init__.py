#!/usr/bin/env python3
"""
Extended UI components for advanced progress tracking.

This module provides advanced progress bar implementations with dynamic
layers, animations, and enhanced user experience features.
"""

# IMPORTS
########################################################
# Local imports
from .dynamic_progress import DynamicLayeredProgress, create_dynamic_layered_progress
from .layer_controller import LayerController, LayerState, LayerType
from .progress_animations import (
    AnimatedProgress,
    AnimationState,
    AnimationType,
    ProgressAnimations,
    create_loading_animation,
    create_progress_wave,
    smooth_transition,
)

# EXPORTS
########################################################
__all__ = [
    "DynamicLayeredProgress",
    "create_dynamic_layered_progress",
    "LayerController",
    "LayerState",
    "LayerType",
    "ProgressAnimations",
    "AnimatedProgress",
    "AnimationType",
    "AnimationState",
    "smooth_transition",
    "create_loading_animation",
    "create_progress_wave",
]
