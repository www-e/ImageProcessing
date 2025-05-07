"""
Enhancement filters module
Imports and re-exports enhancement functions from various filter modules
"""
from filters.enhancement_filters import (
    apply_brightness_contrast, apply_exposure, apply_vibrance,
    apply_clarity, apply_shadows_highlights
)

# Re-export the functions
__all__ = [
    'apply_brightness_contrast',
    'apply_exposure',
    'apply_vibrance',
    'apply_clarity',
    'apply_shadows_highlights'
]
