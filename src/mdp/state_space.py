"""
StateSpace: A module for visualizing the state space and transition probabilities
of markdown documents as a directed graph.
"""

import os
import re
import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Set, Union, Any

from .document import Document

class StateSpace:
    """
    Visualizes the state space of markdown documents as a directed graph,
    highlighting transition probabilities between different elements.
    """
    
    def __init__(self, simplify_states: bool = True, min_count: int = 2):
        """
        Initialize a StateSpace instance.
        
        Args:
            simplify_states: Whether to simplify state representations
            min_count: Minimum transition count to include in visualization
        """
        self.simplify_states = simplify_states
        self.min_count = min_count
        self.transitions = defaultdict(Counter)
        self.state_metadata = {}
        self.states = {}
        self.features = {}
        self.graph = nx.DiGraph()
        
    def analyze(self, markdown_input: Union[str, Document]) -> None:
        """
        Analyze a markdown document or directory to build the state space.
        
        Args:
            markdown_input: Path to a markdown file or directory containing markdown files, or a Document object.
        """
        if isinstance(markdown_input, Document):
            self._process_document(markdown_input.get_content())
        elif os.path.isdir(markdown_input):
            md_files = [os.path.join(markdown_input, f) for f in os.listdir(markdown_input)
                        if f.endswith('.md')]
            for file_path in md_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._process_document(content)
        else:
            with open(markdown_input, 'r', encoding='utf-8') as f:
                content = f.read()
                self._process_document(content)
                
    def parse_markdown(self, content: str) -> None:
        """
        Parse markdown content and populate the state space.
        
        Args:
            content: Markdown content string
        """
        self._process_document(content)
        
    def parse_markdown_file(self, file_path: str) -> None:
        """
        Parse markdown from a file and populate the state space.
        
        Args:
            file_path: Path to the markdown file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self._process_document(content)
    
    def add_state(self, state_data: Dict[str, Any]) -> str:
        """
        Add a state to the state space.
        
        Args:
            state_data: Dictionary containing state metadata
            
        Returns:
            str: The state ID
        """
        # Generate a state ID based on the state type and content
        state_type = state_data.get('type', 'unknown')
        
        if state_type == 'header':
            state_id = f"h{state_data.get('level', 1)}"
        elif state_type == 'list':
            list_type = state_data.get('list_type', 'unordered')
            state_id = 'ul' if list_type == 'unordered' else 'ol'
        elif state_type == 'code':
            language = state_data.get('language', '')
            state_id = f"code:{language}" if language else "code"
        elif state_type == 'paragraph':
            state_id = 'p'
        else:
            state_id = state_type
            
        # Add to states and graph
        self.states[state_id] = state_data
        if not self.graph.has_node(state_id):
            self.graph.add_node(state_id, **state_data)
        else: # Update attributes if node exists
            nx.set_node_attributes(self.graph, {state_id: state_data})
        
        # Add to state_metadata if not already present, using the provided state_data
        if state_id not in self.state_metadata:
            self.state_metadata[state_id] = state_data
            # Ensure count is initialized if this is the first time seeing the state_id
            if 'count' not in self.state_metadata[state_id]:
                 self.state_metadata[state_id]['count'] = 0
            
        return state_id
    
    def add_transition(self, source: str, target: str, weight: float = 1.0) -> None:
        """
        Add a transition between two states.
        
        Args:
            source: Source state ID
            target: Target state ID
            weight: Transition weight
        """
        self.transitions[source][target] += weight
        self.graph.add_edge(source, target, weight=weight)
    
    def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state data by ID.
        
        Args:
            state_id: State ID
            
        Returns:
            Optional[Dict[str, Any]]: State data or None if not found
        """
        return self.states.get(state_id)
    
    def get_transitions(self, state_id: str) -> Dict[str, float]:
        """
        Get transitions from a state.
        
        Args:
            state_id: State ID
            
        Returns:
            Dict[str, float]: Dictionary mapping target state IDs to transition weights
        """
        return dict(self.transitions.get(state_id, {}))
    
    def get_successor_states(self, state_id: str) -> List[str]:
        """
        Get successor states for a given state.
        
        Args:
            state_id: State ID
            
        Returns:
            List[str]: List of successor state IDs
        """
        return list(self.transitions.get(state_id, {}).keys())
    
    def get_features(self, state_id: str) -> Dict[str, Any]:
        """
        Get features for a state.
        
        Args:
            state_id: State ID
            
        Returns:
            Dict[str, Any]: State features
        """
        if state_id in self.features:
            return self.features[state_id]
        
        # Extract features from state metadata
        metadata = self.state_metadata.get(state_id, {})
        features = {
            'type': metadata.get('type', 'unknown'),
            'count': metadata.get('count', 0)
        }
        
        # Add type-specific features
        if features['type'] == 'header':
            features['level'] = metadata.get('level', 1)
        elif features['type'] == 'list':
            features['list_type'] = metadata.get('list_type', 'unordered')
        elif features['type'] == 'code':
            features['language'] = metadata.get('language', '')
            
        self.features[state_id] = features
        return features
    
    def calculate_transition_probabilities(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate transition probabilities between states.
        
        Returns:
            Dict[str, Dict[str, float]]: Dictionary mapping source states to dictionaries 
                                         mapping target states to probabilities
        """
        probabilities = {}
        
        for source, targets in self.transitions.items():
            total_transitions = sum(targets.values())
            
            if total_transitions > 0:
                probabilities[source] = {
                    target: count / total_transitions
                    for target, count in targets.items()
                }
                
        return probabilities
    
    def get_state_sequence(self, content: str) -> List[str]:
        """
        Extract a sequence of states from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            List[str]: Sequence of state IDs
        """
        return list(self._parse_states(content))
    
    def extract_structure(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract document structure from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            List[Dict[str, Any]]: List of document structure elements
        """
        structure = []
        states = self._parse_states(content)
        
        content_lines = content.split('\n')
        current_line = 0
        
        for state in states:
            metadata = self._get_state_metadata(state)
            element = {
                'type': metadata.get('type', 'unknown'),
                'state': state
            }
            
            # Find the content for this state
            for i in range(current_line, len(content_lines)):
                line = content_lines[i]
                
                # Simplistic matching based on state type
                if (metadata.get('type') == 'header' and line.startswith('#')) or \
                   (metadata.get('type') == 'list' and (line.startswith('- ') or line.startswith('* '))) or \
                   (metadata.get('type') == 'code' and line.startswith('```')):
                    element['content'] = line
                    current_line = i + 1
                    break
            
            structure.append(element)
            
        return structure
    
    def get_markdown(self, state_sequence: List[str]) -> str:
        """
        Convert a sequence of states back to markdown content.
        
        Args:
            state_sequence: Sequence of state IDs
            
        Returns:
            str: Markdown content
        """
        lines = []
        
        for state in state_sequence:
            metadata = self._get_state_metadata(state)
            
            if metadata.get('type') == 'header':
                level = metadata.get('level', 1)
                lines.append('#' * level + ' Header')
            elif metadata.get('type') == 'paragraph':
                lines.append('This is a paragraph.')
            elif metadata.get('type') == 'list':
                list_type = metadata.get('list_type', 'unordered')
                if list_type == 'unordered':
                    lines.append('- List item')
                else:
                    lines.append('1. List item')
            elif metadata.get('type') == 'code':
                language = metadata.get('language', '')
                lines.append(f'```{language}')
                lines.append('Code block')
                lines.append('```')
            else:
                lines.append(state)
                
            # Add blank line between elements
            lines.append('')
            
        return '\n'.join(lines)
    
    def calculate_pagerank(self) -> Dict[str, float]:
        """
        Calculate PageRank for all states in the graph.
        
        Returns:
            Dict[str, float]: Dictionary mapping state IDs to PageRank values
        """
        if not self.graph.nodes():
            return {}
            
        return nx.pagerank(self.graph)
    
    def save(self, file_path: str) -> None:
        """
        Save the state space to a file.
        
        Args:
            file_path: Path to save the state space
        """
        data = {
            'transitions': {source: dict(targets) for source, targets in self.transitions.items()},
            'state_metadata': self.state_metadata,
            'states': self.states,
            'features': self.features
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, file_path: str) -> None:
        """
        Load the state space from a file.
        
        Args:
            file_path: Path to load the state space from
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.transitions = defaultdict(Counter)
        for source, targets in data.get('transitions', {}).items():
            self.transitions[source].update(targets)
            
        self.state_metadata = data.get('state_metadata', {})
        self.states = data.get('states', {})
        self.features = data.get('features', {})
        
        # Rebuild the graph
        self.graph = nx.DiGraph()
        
        for state, metadata in self.state_metadata.items():
            self.graph.add_node(state, **metadata)
            
        for source, targets in self.transitions.items():
            for target, weight in targets.items():
                self.graph.add_edge(source, target, weight=weight)
    
    def visualize(self, output_path: str = 'markdown_state_space.png', 
                 title: str = 'Markdown State Space') -> None:
        """
        Generate a visualization of the markdown state space.
        
        Args:
            output_path: Path to save the visualization
            title: Title for the visualization
        """
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes with metadata
        for state, metadata in self.state_metadata.items():
            G.add_node(state, **metadata)
        
        # Add edges with weights
        for source, targets in self.transitions.items():
            for target, count in targets.items():
                if count >= self.min_count:
                    G.add_edge(source, target, weight=count, 
                               width=1.0 + count / 5.0,
                               label=str(count))
        
        # Skip visualization if graph is empty
        if not G.nodes():
            print("No states found that meet the minimum transition count.")
            return
            
        # Create figure
        plt.figure(figsize=(14, 10))
        plt.title(title, fontsize=16)
        
        # Define node colors based on state type
        node_colors = {
            'header': '#ff7f0e',  # orange
            'paragraph': '#1f77b4',  # blue
            'list': '#2ca02c',  # green
            'code': '#d62728',  # red
            'blank': '#7f7f7f',  # gray
            'other': '#9467bd'   # purple
        }
        
        colors = [node_colors.get(G.nodes[n].get('type', 'other'), '#9467bd') 
                  for n in G.nodes()]
        
        # Compute node size based on frequency
        sizes = [300 + G.nodes[n].get('count', 0) * 10 for n in G.nodes()]
        
        # Layout
        if len(G) < 10:
            pos = nx.spring_layout(G, k=0.5, iterations=100)
        else:
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                pos = nx.spring_layout(G, k=0.5, iterations=100)
        
        # Draw
        nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, alpha=0.8)
        
        # Draw edges with varying thickness
        for u, v, attr in G.edges(data=True):
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=attr.get('width', 1.0), 
                                  alpha=0.7, arrowsize=15, edge_color='#888888')
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        # Draw edge labels for significant transitions
        edge_labels = {(u, v): attr.get('label', '') for u, v, attr in G.edges(data=True) 
                      if attr.get('weight', 0) > max(self.min_count, 3)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                      markerfacecolor=color, markersize=10, label=state_type)
                          for state_type, color in node_colors.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Save figure
        plt.tight_layout()
        plt.axis('off')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"State space visualization saved to {output_path}")
    
    def print_statistics(self) -> None:
        """Print statistics about the markdown state space."""
        print(f"State Space Statistics:")
        print(f"Total unique states: {len(self.state_metadata)}")
        
        # Count state types
        state_types = Counter()
        for state, metadata in self.state_metadata.items():
            state_types[metadata.get('type', 'unknown')] += 1
            
        print("\nState distribution:")
        for state_type, count in state_types.most_common():
            print(f"  {state_type}: {count}")
        
        # Analyze transitions
        total_transitions = sum(sum(counter.values()) for counter in self.transitions.values())
        print(f"\nTotal transitions: {total_transitions}")
        
        # Most common transitions
        print("\nMost common transitions:")
        top_transitions = []
        for source, targets in self.transitions.items():
            for target, count in targets.items():
                top_transitions.append((source, target, count))
                
        top_transitions.sort(key=lambda x: x[2], reverse=True)
        for source, target, count in top_transitions[:10]:
            s_type = self.state_metadata.get(source, {}).get('type', 'unknown')
            t_type = self.state_metadata.get(target, {}).get('type', 'unknown')
            print(f"  {s_type} → {t_type}: {count}")
    
    def _process_document(self, content: str) -> None:
        """
        Process a markdown document to extract states and transitions.
        
        Args:
            content: Markdown content
        """
        states_representations = list(self._parse_states(content)) # These are strings like 'h1', 'p'
        
        if not states_representations:
            return
            
        # First pass: ensure all states are added via self.add_state
        # and update their counts in self.state_metadata
        for state_repr in states_representations:
            metadata = self._get_state_metadata(state_repr) # Get full metadata dict for the state representation
            # self.add_state will use metadata to derive the same state_repr as its state_id (e.g. 'h1')
            # and populate self.states[state_repr], self.graph (if new node), and self.state_metadata[state_repr] (if new state_id)
            actual_state_id = self.add_state(metadata) # actual_state_id should be same as state_repr
            
            # Increment count for the current state_id in self.state_metadata.
            # self.add_state ensures self.state_metadata[actual_state_id] exists and initializes count if new.
            self.state_metadata[actual_state_id]['count'] = self.state_metadata[actual_state_id].get('count', 0) + 1

        # Second pass: add transitions
        if len(states_representations) > 1:
            for i in range(len(states_representations) - 1):
                source_repr = states_representations[i]
                target_repr = states_representations[i+1]
                
                # self.transitions uses the state representations as keys
                self.transitions[source_repr][target_repr] += 1 
                
                # Add edge to graph (nodes are guaranteed to exist by the first pass calling self.add_state)
                if not self.graph.has_edge(source_repr, target_repr):
                    self.graph.add_edge(source_repr, target_repr, weight=1)
                else:
                    # Ensure 'weight' attribute exists before incrementing
                    if 'weight' not in self.graph[source_repr][target_repr]:
                         self.graph[source_repr][target_repr]['weight'] = 0 # Should be initialized to 1 by previous add_edge
                    self.graph[source_repr][target_repr]['weight'] += 1
    
    def _parse_states(self, content: str):
        """
        Parse markdown content into states.
        
        Args:
            content: Markdown content
            
        Yields:
            str: State representation
        """
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                yield 'blank'
                i += 1
                continue
                
            # Headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                yield f'h{level}'
                i += 1
                continue
                
            # Lists
            list_match = re.match(r'^([*\-+]|\d+\.)\s+(.+)$', line)
            if list_match:
                if list_match.group(1) in ['*', '-', '+']:
                    yield 'ul'  # Unordered list
                else:
                    yield 'ol'  # Ordered list
                i += 1
                continue
                
            # Code blocks
            if line.startswith('```'):
                language = line[3:].strip()
                if language:
                    yield f'code:{language}'
                else:
                    yield 'code'
                    
                # Skip to end of code block
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                i += 1  # Skip the closing ```
                continue
                
            # Assume paragraph for all other content
            yield 'p'
            
            # Skip to the end of the paragraph
            i += 1
            while i < len(lines) and lines[i].strip() and not (
                lines[i].strip().startswith('#') or 
                lines[i].strip().startswith('```') or
                re.match(r'^([*\-+]|\d+\.)\s+(.+)$', lines[i].strip())
            ):
                i += 1
    
    def _get_state_metadata(self, state: str) -> Dict[str, Any]:
        """
        Get metadata for a state.
        
        Args:
            state: State representation
            
        Returns:
            Dict[str, Any]: State metadata
        """
        metadata = {'type': 'other', 'count': 0}
        
        # Headers
        header_match = re.match(r'^h(\d)$', state)
        if header_match:
            metadata['type'] = 'header'
            metadata['level'] = int(header_match.group(1))
            return metadata
            
        # Lists
        if state == 'ul':
            metadata['type'] = 'list'
            metadata['list_type'] = 'unordered'
            return metadata
        elif state == 'ol':
            metadata['type'] = 'list'
            metadata['list_type'] = 'ordered'
            return metadata
            
        # Code blocks
        code_match = re.match(r'^code:(.*)$', state)
        if code_match or state == 'code':
            metadata['type'] = 'code'
            if code_match:
                metadata['language'] = code_match.group(1)
            return metadata
            
        # Paragraphs
        if state == 'p':
            metadata['type'] = 'paragraph'
            return metadata
            
        # Blank lines
        if state == 'blank':
            metadata['type'] = 'blank'
            return metadata
            
        return metadata 