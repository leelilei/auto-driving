"""
ChinaTravel Baseline Methods

This module implements various baseline methods for travel planning:
- B0: Direct Prompting
- B1: Few-shot Prompting
- B2: Chain-of-Thought
- B3: ReAct (optional)
"""

from .base import BaselineMethod
from .direct import DirectBaseline
from .fewshot import FewshotBaseline
from .cot import ChainOfThoughtBaseline

__all__ = [
    'BaselineMethod',
    'DirectBaseline',
    'FewshotBaseline',
    'ChainOfThoughtBaseline',
]
