"""Fusion module for OpenEVLN safety pipeline"""

from .risk_fusion import fuse
from .enhanced_risk_fusion import enhanced_fuse, get_severity_description, get_breadth_description

__all__ = ["fuse", "enhanced_fuse", "get_severity_description", "get_breadth_description"]
