"""
Visualization: A module for visualizing Markdown document metrics and structures.
"""

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import math
from pathlib import Path
try:
    import textstat
    from textstat import (
        flesch_reading_ease,
        flesch_kincaid_grade,
        smog_index,
        coleman_liau_index
    )
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    # Define fallback functions if textstat is not available
    def flesch_reading_ease(text): return 50.0  # Neutral score
    def flesch_kincaid_grade(text): return 8.0   # Grade 8 level
    def smog_index(text): return 10.0            # Neutral SMOG score
    def coleman_liau_index(text): return 12.0    # Grade 12 level
try:
    from wordcloud import WordCloud, STOPWORDS
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    # Define fallback if wordcloud is not available
    class WordCloud:
        def __init__(self, **kwargs):
            pass
        def generate(self, text):
            return None
        def to_image(self):
            return None

from .document import Document
from .markchain import MarkChain
from .state_space import StateSpace
from .quality import DocumentQuality


def plot_document_metrics(metrics_dict: Dict[str, Dict[str, Dict[str, float]]],
                          figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Visualize document metrics comparison.
    
    Args:
        metrics_dict: Dictionary mapping document names to their metrics
                     Format: {'Doc1': {'readability': {...}, 'information_density': {...}}}
        figsize: Figure size (width, height)
        
    Returns:
        Matplotlib figure object
    """
    # Create figure and subplots
    fig, axs = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle("Document Metrics Comparison", fontsize=16)
    
    # Category titles and colors
    categories = ["Readability", "Information Density", "Structural Balance"]
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(metrics_dict)))
    
    # Plot readability metrics
    doc_names = list(metrics_dict.keys())
    
    # Process readability metrics
    readability_metrics = {
        "flesch_reading_ease": "Flesch Reading Ease",
        "flesch_kincaid_grade": "Flesch-Kincaid Grade"
    }
    
    readability_values = {name: [] for name in doc_names}
    for doc_name, metrics in metrics_dict.items():
        for metric in readability_metrics:
            if metric in metrics.get("readability", {}):
                readability_values[doc_name].append(metrics["readability"][metric])
            else:
                readability_values[doc_name].append(0)
    
    # Plot readability
    ax = axs[0]
    x = np.arange(len(readability_metrics))
    width = 0.8 / len(doc_names)
    
    for i, (doc_name, values) in enumerate(readability_values.items()):
        ax.bar(x + i * width - 0.4 + width/2, values, width, label=doc_name, color=colors[i])
    
    ax.set_title(categories[0])
    ax.set_xticks(x)
    ax.set_xticklabels([readability_metrics[m] for m in readability_metrics])
    ax.legend()
    
    # Process information density metrics
    density_metrics = {
        "lexical_diversity": "Lexical Diversity",
        "entropy": "Information Entropy"
    }
    
    density_values = {name: [] for name in doc_names}
    for doc_name, metrics in metrics_dict.items():
        for metric in density_metrics:
            if metric in metrics.get("information_density", {}):
                density_values[doc_name].append(metrics["information_density"][metric])
            else:
                density_values[doc_name].append(0)
    
    # Plot information density
    ax = axs[1]
    x = np.arange(len(density_metrics))
    
    for i, (doc_name, values) in enumerate(density_values.items()):
        ax.bar(x + i * width - 0.4 + width/2, values, width, color=colors[i])
    
    ax.set_title(categories[1])
    ax.set_xticks(x)
    ax.set_xticklabels([density_metrics[m] for m in density_metrics])
    
    # Process structural metrics
    structure_metrics = {
        "heading_distribution": "Heading Distribution",
        "content_variety": "Content Variety"
    }
    
    structure_values = {name: [] for name in doc_names}
    for doc_name, metrics in metrics_dict.items():
        for metric in structure_metrics:
            if metric in metrics.get("structural_balance", {}):
                structure_values[doc_name].append(metrics["structural_balance"][metric])
            else:
                structure_values[doc_name].append(0)
    
    # Plot structural balance
    ax = axs[2]
    x = np.arange(len(structure_metrics))
    
    for i, (doc_name, values) in enumerate(structure_values.items()):
        ax.bar(x + i * width - 0.4 + width/2, values, width, color=colors[i])
    
    ax.set_title(categories[2])
    ax.set_xticks(x)
    ax.set_xticklabels([structure_metrics[m] for m in structure_metrics])
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout for the suptitle
    
    return fig


def plot_transitions(chain: MarkChain, top_n: int = 10, figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Visualize state transitions in a MarkChain.
    
    Args:
        chain: Trained MarkChain object
        top_n: Number of most frequent states to include
        figsize: Figure size (width, height)
        
    Returns:
        Matplotlib figure object
    """
    if not chain.is_trained:
        raise ValueError("MarkChain must be trained before visualizing transitions")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Get top states by frequency
    state_counts = {}
    for state in chain.transitions:
        state_counts[state] = sum(chain.transitions[state].values())
    
    top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_state_names = [s[0] for s in top_states]
    
    # Add nodes for top states
    for state, count in top_states:
        # Truncate long state names
        display_name = state if len(state) <= 15 else state[:12] + "..."
        G.add_node(state, label=display_name, count=count)
    
    # Add edges for transitions between top states
    max_weight = 0
    for source in top_state_names:
        for target in chain.transitions[source]:
            if target in top_state_names:
                weight = chain.transitions[source][target]
                G.add_edge(source, target, weight=weight)
                max_weight = max(max_weight, weight)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title("State Transitions in MarkChain", fontsize=16)
    
    # Calculate node sizes based on frequency
    max_count = max(state_counts.values())
    node_sizes = {state: 300 + (count / max_count) * 1500 for state, count in top_states}
    
    # Calculate positions using a layout algorithm
    pos = nx.spring_layout(G, k=0.8, iterations=100)
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, 
        ax=ax,
        node_size=[node_sizes[n] for n in G.nodes()],
        node_color=plt.cm.viridis(np.linspace(0, 0.8, len(G.nodes()))),
        alpha=0.8
    )
    
    # Draw edges with width based on transition probability
    edges = G.edges(data=True)
    edge_widths = [1 + (e[2]['weight'] / max_weight) * 5 for e in edges]
    
    nx.draw_networkx_edges(
        G, pos, 
        ax=ax,
        width=edge_widths,
        alpha=0.6,
        arrows=True,
        arrowsize=15,
        edge_color='gray'
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos, 
        ax=ax,
        labels={n: G.nodes[n]['label'] for n in G.nodes()},
        font_size=10,
        font_color='black'
    )
    
    # Add legend for node sizes
    sizes = [min(node_sizes.values()), max(node_sizes.values())]
    labels = ["Less frequent", "More frequent"]
    
    # Create dummy scatter plots for the legend
    for size, label in zip(sizes, labels):
        ax.scatter([], [], s=size, label=label, 
                  color=plt.cm.viridis(0.4), alpha=0.8)
    
    ax.legend(scatterpoints=1, title="State Frequency")
    
    # Remove axis
    ax.set_axis_off()
    
    return fig


def plot_document_structure(document: Union[Document, str, Path], 
                           figsize: Tuple[int, int] = (10, 12)) -> plt.Figure:
    """
    Visualize the structure of a markdown document.
    
    Args:
        document: MarkdownDocument instance or path to markdown file or content string
        figsize: Figure size (width, height)
        
    Returns:
        Matplotlib figure object
    """
    # Ensure we have a MarkdownDocument
    if not isinstance(document, Document):
        if isinstance(document, (str, Path)):
            # If it looks like content (has newlines or markdown symbols), treat as content
            if isinstance(document, str) and ('\n' in document or '#' in document):
                document = Document(content=str(document))
            else:
                # Otherwise treat as a file path
                document = Document(str(document))
        else:
            raise TypeError("document must be a MarkdownDocument, string, or Path")
    
    # Get document structure
    structure = document.get_structure()
    
    # Process structure elements
    elements = []
    for i, element in enumerate(structure):
        elem_type = element['type']
        
        if elem_type == 'heading':
            level = element.get('level', 1)
            content = element.get('content', '').strip()
            elements.append({
                'type': 'heading',
                'level': level,
                'content': content,
                'position': i
            })
        elif elem_type in ['paragraph', 'list', 'code']:
            elements.append({
                'type': elem_type,
                'content': element.get('content', ''),
                'position': i
            })
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title("Document Structure Visualization", fontsize=16)
    
    # Set up colors for different element types
    colors = {
        'heading': '#3498db',  # Blue
        'paragraph': '#2ecc71',  # Green
        'list': '#e74c3c',  # Red
        'code': '#f39c12',  # Orange
    }
    
    # Adjust opacity by heading level
    heading_alphas = {
        1: 1.0,
        2: 0.8,
        3: 0.6,
        4: 0.5,
        5: 0.4,
        6: 0.3
    }
    
    # Draw elements
    max_width = 100
    y_spacing = 1
    y_pos = 0
    
    for element in elements:
        elem_type = element['type']
        
        # Calculate width based on content length
        content_len = len(element.get('content', ''))
        width = min(max_width, max(10, content_len / 10))
        
        # Calculate position and size
        if elem_type == 'heading':
            level = element.get('level', 1)
            x_pos = (level - 1) * 10
            height = 2
            color = colors[elem_type]
            alpha = heading_alphas.get(level, 0.5)
            
            # Draw heading block
            ax.add_patch(plt.Rectangle(
                (x_pos, y_pos), width, height, 
                color=color, alpha=alpha
            ))
            
            # Add heading text
            ax.text(
                x_pos + width / 2, y_pos + height / 2, 
                element.get('content', '').replace('#', '').strip(),
                ha='center', va='center', 
                fontsize=12 - level, fontweight='bold'
            )
            
            y_pos += height + y_spacing
            
        else:
            x_pos = 10
            
            # Calculate height based on content
            content_lines = element.get('content', '').count('\n') + 1
            height = max(1, content_lines / 3)
            
            # Draw element block
            ax.add_patch(plt.Rectangle(
                (x_pos, y_pos), width, height, 
                color=colors.get(elem_type, '#bdc3c7'),
                alpha=0.6
            ))
            
            # Add element type label
            ax.text(
                x_pos + width / 2, y_pos + height / 2, 
                elem_type.capitalize(),
                ha='center', va='center'
            )
            
            y_pos += height + y_spacing
    
    # Set axis limits with padding
    ax.set_xlim(-5, max_width + 20)
    ax.set_ylim(y_pos + 5, -5)
    
    # Create legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color=colors['heading'], label='Heading'),
        plt.Rectangle((0, 0), 1, 1, color=colors['paragraph'], label='Paragraph'),
        plt.Rectangle((0, 0), 1, 1, color=colors['list'], label='List'),
        plt.Rectangle((0, 0), 1, 1, color=colors['code'], label='Code Block')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add x-axis label explaining indentation
    ax.set_xlabel("Indentation indicates heading level and content hierarchy")
    
    return fig


def plot_readability_comparison(documents: Dict[str, Union[Document, str, Path]],
                               figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Compare readability metrics across multiple documents.
    
    Args:
        documents: Dictionary mapping document names to either MarkdownDocument instances or paths
        figsize: Figure size (width, height)
        
    Returns:
        Matplotlib figure object
    """
    # Convert all documents to MarkdownDocument instances if needed
    doc_instances = {}
    for name, doc in documents.items():
        if not isinstance(doc, Document):
            doc_instances[name] = Document(doc if isinstance(doc, Path) else str(doc))
        else:
            doc_instances[name] = doc
    
    # Calculate readability metrics
    metrics = {
        'Flesch Reading Ease': {},
        'Flesch-Kincaid Grade': {},
        'SMOG Index': {},
        'Coleman-Liau Index': {}
    }
    
    for name, doc in doc_instances.items():
        text = doc.get_content()
        metrics['Flesch Reading Ease'][name] = flesch_reading_ease(text)
        metrics['Flesch-Kincaid Grade'][name] = flesch_kincaid_grade(text)
        metrics['SMOG Index'][name] = smog_index(text)
        metrics['Coleman-Liau Index'][name] = coleman_liau_index(text)
    
    # Create figure
    fig, axs = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle("Document Readability Comparison", fontsize=16)
    
    # Flatten axes for easier iteration
    axs = axs.flat
    
    # Colors for different documents
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(doc_instances)))
    color_map = {name: color for name, color in zip(doc_instances.keys(), colors)}
    
    # Plot each metric
    for i, (metric_name, values) in enumerate(metrics.items()):
        ax = axs[i]
        
        # Sort values for this metric
        sorted_values = sorted(values.items(), key=lambda x: x[1])
        doc_names = [x[0] for x in sorted_values]
        metric_values = [x[1] for x in sorted_values]
        
        # Plot horizontal bars
        y_pos = range(len(doc_names))
        ax.barh(y_pos, metric_values, align='center', 
               color=[color_map[name] for name in doc_names])
        
        # Add text labels on bars
        for j, value in enumerate(metric_values):
            ax.text(value, j, f' {value:.1f}', va='center')
        
        # Set labels and title
        ax.set_yticks(y_pos)
        ax.set_yticklabels(doc_names)
        ax.set_title(metric_name)
        
        # Add interpretation guidance
        if metric_name == 'Flesch Reading Ease':
            ax.set_xlabel('Higher is easier to read')
        else:
            ax.set_xlabel('Lower grade level is easier')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout for the suptitle
    
    return fig


def plot_filtered_state_space(
    chain: MarkChain,
    filter_func: Callable[[Any], bool] = None,
    highlight_func: Callable[[Any], bool] = None,
    figsize: Tuple[int, int] = (12, 10),
    node_size_factor: float = 1000,
    edge_width_factor: float = 3,
    include_isolated: bool = False
) -> plt.Figure:
    """
    Visualize a filtered view of the state space based on custom filter functions.
    
    This visualization allows for dynamic filtering of states based on their properties,
    and highlighting specific states of interest within the filtered set.
    
    Args:
        chain: Trained MarkChain object
        filter_func: Function that takes a state and returns True if it should be included
                    If None, all states are included
        highlight_func: Function that takes a state and returns True if it should be highlighted
                       If None, no states are highlighted
        figsize: Figure size (width, height)
        node_size_factor: Factor for scaling node sizes
        edge_width_factor: Factor for scaling edge widths
        include_isolated: Whether to include nodes with no connections to other filtered nodes
        
    Returns:
        Matplotlib figure object
    
    Example:
        ```python
        # Only show heading states (assuming states are strings)
        filter_func = lambda state: str(state).startswith('#')
        
        # Highlight H2 headings
        highlight_func = lambda state: str(state).startswith('## ')
        
        fig = plot_filtered_state_space(chain, filter_func, highlight_func)
        plt.show()
        ```
    """
    if not chain.is_trained:
        raise ValueError("MarkChain must be trained before visualizing state space")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Apply filter to states
    all_states = list(chain.transitions.keys())
    if filter_func:
        filtered_states = [state for state in all_states if filter_func(state)]
    else:
        filtered_states = all_states
    
    if not filtered_states:
        raise ValueError("No states match the provided filter criteria")
    
    # Count occurrences for node sizing
    state_counts = {}
    for state in filtered_states:
        state_counts[state] = sum(chain.transitions[state].values())
    
    # Add nodes for filtered states
    for state in filtered_states:
        # Truncate long state names for display
        display_name = str(state)
        if len(display_name) > 15:
            display_name = display_name[:12] + "..."
        
        # Check if state should be highlighted
        is_highlighted = highlight_func(state) if highlight_func else False
        
        G.add_node(state, label=display_name, count=state_counts[state], highlighted=is_highlighted)
    
    # Add edges for transitions between filtered states
    max_weight = 0
    has_any_edge = False
    for source in filtered_states:
        has_edge = False
        for target, weight in chain.transitions[source].items():
            if target in filtered_states:
                G.add_edge(source, target, weight=weight)
                max_weight = max(max_weight, weight)
                has_edge = True
                has_any_edge = True
        
        # Remove isolated nodes if not explicitly included
        if not include_isolated and not has_edge:
            in_edges = False
            for potential_source in filtered_states:
                if potential_source != source and source in chain.transitions[potential_source]:
                    in_edges = True
                    break
            
            if not in_edges:
                G.remove_node(source)
    
    # If we've removed all nodes due to isolation, add them back
    if len(G.nodes()) == 0 and filtered_states:
        for state in filtered_states:
            display_name = str(state)
            if len(display_name) > 15:
                display_name = display_name[:12] + "..."
            
            is_highlighted = highlight_func(state) if highlight_func else False
            G.add_node(state, label=display_name, count=state_counts[state], highlighted=is_highlighted)
        
        # Force include_isolated to True since there are no connections
        include_isolated = True
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title("Filtered State Space Visualization", fontsize=16)
    
    # Calculate node sizes based on frequency
    max_count = max(nx.get_node_attributes(G, 'count').values()) if G.nodes() else 1
    node_sizes = {node: 300 + (G.nodes[node]['count'] / max_count) * node_size_factor 
                  for node in G.nodes()}
    
    # Calculate positions using a layout algorithm
    if has_any_edge:
        pos = nx.spring_layout(G, k=0.8, iterations=100, seed=42)
    else:
        # For disconnected nodes, arrange in a circle
        pos = nx.circular_layout(G)
    
    # Draw regular nodes
    regular_nodes = [n for n in G.nodes() if not G.nodes[n]['highlighted']]
    if regular_nodes:
        nx.draw_networkx_nodes(
            G, pos,
            ax=ax,
            nodelist=regular_nodes,
            node_size=[node_sizes[n] for n in regular_nodes],
            node_color='lightblue',
            alpha=0.7
        )
    
    # Draw highlighted nodes
    highlighted_nodes = [n for n in G.nodes() if G.nodes[n]['highlighted']]
    if highlighted_nodes:
        nx.draw_networkx_nodes(
            G, pos,
            ax=ax,
            nodelist=highlighted_nodes,
            node_size=[node_sizes[n] for n in highlighted_nodes],
            node_color='orange',
            alpha=0.9
        )
    
    # Draw edges with width based on transition probability
    if max_weight > 0:
        edges = G.edges(data=True)
        edge_widths = [1 + (e[2]['weight'] / max_weight) * edge_width_factor for e in edges]
        
        nx.draw_networkx_edges(
            G, pos, 
            ax=ax,
            width=edge_widths,
            alpha=0.6,
            arrows=True,
            arrowsize=15,
            connectionstyle='arc3,rad=0.1'
        )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        labels={n: G.nodes[n]['label'] for n in G.nodes()},
        font_size=10,
        font_weight='bold'
    )
    
    # Add a legend for node types
    if highlighted_nodes:
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                      markersize=10, label='Regular States'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                      markersize=10, label='Highlighted States')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
    
    # Add note for disconnected nodes if applicable
    if not has_any_edge:
        ax.text(0.5, 0.01, 
                "Note: States shown have no direct transitions between them",
                horizontalalignment='center',
                fontsize=10, fontweight='bold',
                transform=ax.transAxes)
    
    # Remove axis
    plt.axis('off')
    plt.tight_layout()
    
    return fig 