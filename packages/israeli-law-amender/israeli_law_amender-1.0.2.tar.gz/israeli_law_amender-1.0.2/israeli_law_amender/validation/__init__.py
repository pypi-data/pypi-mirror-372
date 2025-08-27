"""
Validation modules for law amendments.

This module contains different layers of validation:
- Layer 1: Basic text comparison and fuzzy matching
- Layer 2: Amendment-centric validation using NLP
- Layer 3: LLM-based comprehensive validation
"""

from .layer1_validation import (
    read_law_json_to_flat_text,
    compare_fuzzy_match,
    generate_html_diff_report
)

__all__ = [
    'read_law_json_to_flat_text',
    'compare_fuzzy_match', 
    'generate_html_diff_report'
] 