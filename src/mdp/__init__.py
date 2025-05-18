"""
Markdown Decision Process (MDP): A framework for analyzing, generating, and optimizing 
Markdown documents through the lens of decision theory and probabilistic modeling.
"""

__version__ = "0.1.0"

from .markchain import MarkChain
from .policy_optimizer import PolicyOptimizer
from .state_space import StateSpace
from .belief_updater import BeliefUpdater
from .markdown_agent import MarkdownAgent
from .document import Document
from .transformations import (
    Transformation,
    HeadingLevelTransformation,
    ListFormatTransformation,
    CodeBlockFormatTransformation,
    LinkFormatTransformation,
    TableFormatTransformation,
    TextStyleTransformation,
    TransformationPipeline
)
from .visualization import (
    plot_document_metrics,
    plot_transitions,
    plot_document_structure,
    plot_readability_comparison,
    plot_filtered_state_space
)
from .pandoc import (
    PandocConverter,
    check_pandoc_installed,
    get_pandoc_version,
    get_supported_formats,
    convert_document,
    convert_with_transformations,
    extract_metadata,
    apply_template,
    PandocNotFoundError
)
from .quality import DocumentQuality

__all__ = [
    "MarkChain",
    "PolicyOptimizer",
    "StateSpace",
    "BeliefUpdater",
    "MarkdownAgent",
    "Document",
    "Transformation",
    "HeadingLevelTransformation",
    "ListFormatTransformation",
    "CodeBlockFormatTransformation",
    "LinkFormatTransformation",
    "TableFormatTransformation",
    "TextStyleTransformation",
    "TransformationPipeline",
    "plot_document_metrics",
    "plot_transitions",
    "plot_document_structure",
    "plot_readability_comparison",
    "plot_filtered_state_space",
    "PandocConverter",
    "check_pandoc_installed",
    "get_pandoc_version",
    "get_supported_formats",
    "convert_document",
    "convert_with_transformations",
    "extract_metadata",
    "apply_template",
    "PandocNotFoundError",
    "DocumentQuality"
] 