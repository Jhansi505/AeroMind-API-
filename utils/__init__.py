"""
Utility package for the Agentic AI Drone Project.

This package contains helper modules such as:
- logging utilities
- formatting helpers
- shared constants (future use)

Keeping these utilities separate ensures clean separation
between agent logic, tools, and infrastructure code.
"""

from .logger import get_logger

__all__ = [
    "get_logger"
]
