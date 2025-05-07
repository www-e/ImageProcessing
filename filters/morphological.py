"""
Morphological filters module
Imports and re-exports morphological functions from various filter modules
"""
from filters.morphological_filters import (
    apply_dilation, apply_erosion, apply_opening, apply_closing
)
from filters.black_tophat import apply_black_tophat
from filters.morphological_gradient import apply_morphological_gradient
from filters.hit_miss_transform import apply_hit_miss_transform
from filters.thinning import apply_thinning
from filters.thickening import apply_thickening
from filters.skeletonization import apply_skeletonization

# Import tophat from morphological_filters
from filters.morphological_filters import apply_tophat

# Re-export the functions
__all__ = [
    'apply_dilation',
    'apply_erosion',
    'apply_opening',
    'apply_closing',
    'apply_tophat',
    'apply_black_tophat',
    'apply_morphological_gradient',
    'apply_hit_miss_transform',
    'apply_thinning',
    'apply_thickening',
    'apply_skeletonization'
]
