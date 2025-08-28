"""
FunctAI - DSPy-powered function decorators for AI-enhanced programming.

A library that seamlessly integrates AI capabilities into Python functions
using DSPy's powerful prompting and optimization framework.
"""

from functai.core import (
    magic,
    step,
    final,
    optimize,
    parallel,
    use,
    format_prompt,
    inspect_history_text,
)

__version__ = "0.1.2"

__all__ = [
    "magic",
    "step", 
    "final",
    "optimize",
    "parallel",
    "use",
    "format_prompt",
    "inspect_history_text",
]
