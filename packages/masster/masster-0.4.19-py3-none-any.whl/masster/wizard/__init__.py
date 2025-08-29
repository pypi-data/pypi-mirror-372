"""
Wizard module for automated processing of mass spectrometry studies.

This module provides the Wizard class for fully automated processing of MS data
from raw files to final study results, including batch conversion, assembly,
alignment, merging, plotting, and export.
"""

from .wizard import Wizard, wizard_def

__all__ = ["Wizard", "wizard_def"]
