"""MAIS - ML Model Audit & Inspection System."""

from mais.application.factories import MAISFactory
from mais.application.mais_facade import MAIS

# Export main class and factory
__all__ = ["MAIS", "MAISFactory"]
