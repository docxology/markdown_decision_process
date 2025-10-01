"""
Animations: Create dynamic visualizations and animations of markdown transformations.

This module provides thin orchestrators that coordinate between Document, StateSpace,
MarkChain, and visualization components to create comprehensive animated analyses.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, FancyBboxPatch
import networkx as nx
import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Callable
from pathlib import Path
import json

from .document import Document
from .state_space import StateSpace
from .markchain import MarkChain
from .belief_updater import BeliefUpdater
from .visualization import plot_document_structure, plot_transitions


class DocumentEvolutionAnimator:
    """
    Thin orchestrator for animating document evolution through transformations.
    
    This class coordinates visualization of how a document changes through
    a series of transformations, showing before/after comparisons and metrics.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (16, 10)):
        """
        Initialize the animator.
        
        Args:
            figsize: Figure size for animations
        """
        self.figsize = figsize
        self.frames = []
        
    def add_transformation_step(self, 
                               before_doc: Document, 
                               after_doc: Document,
                               transformation_name: str,
                               metrics: Optional[Dict[str, float]] = None) -> None:
        """
        Add a transformation step to the animation.
        
        Args:
            before_doc: Document before transformation
            after_doc: Document after transformation
            transformation_name: Name of the transformation
            metrics: Optional metrics comparing before and after
        """
        self.frames.append({
            'before': before_doc,
            'after': after_doc,
            'name': transformation_name,
            'metrics': metrics or {}
        })
    
    def create_animation(self, output_path: str, fps: int = 1) -> str:
        """
        Create an animated visualization of all transformation steps.
        
        Args:
            output_path: Path to save the animation
            fps: Frames per second
            
        Returns:
            Path to saved animation
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        
        def update(frame_idx):
            for ax in axes.flat:
                ax.clear()
            
            if frame_idx >= len(self.frames):
                return
                
            frame = self.frames[frame_idx]
            
            # Top left: Before structure
            axes[0, 0].set_title(f"Before: {frame['name']}")
            self._plot_document_structure(axes[0, 0], frame['before'])
            
            # Top right: After structure
            axes[0, 1].set_title(f"After: {frame['name']}")
            self._plot_document_structure(axes[0, 1], frame['after'])
            
            # Bottom left: Metrics comparison
            axes[1, 0].set_title("Metrics")
            self._plot_metrics(axes[1, 0], frame['metrics'])
            
            # Bottom right: Transformation info
            axes[1, 1].set_title("Transformation Details")
            self._plot_transformation_info(axes[1, 1], frame)
            
            fig.tight_layout()
        
        anim = animation.FuncAnimation(fig, update, frames=len(self.frames),
                                      interval=1000/fps, repeat=True)
        anim.save(output_path, writer='pillow')
        plt.close()
        
        return output_path
    
    def _plot_document_structure(self, ax, doc: Document):
        """Plot document structure on an axis."""
        stats = doc.get_statistics()
        
        # Create a simple bar chart of element counts
        elements = ['Headings', 'Paragraphs', 'Lists', 'Code']
        counts = [
            stats.get('heading_count', 0),
            stats.get('paragraph_count', 0),
            stats.get('list_count', 0),
            stats.get('code_block_count', 0)
        ]
        
        ax.barh(elements, counts, color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'])
        ax.set_xlabel('Count')
        ax.grid(axis='x', alpha=0.3)
    
    def _plot_metrics(self, ax, metrics: Dict[str, float]):
        """Plot metrics on an axis."""
        if not metrics:
            ax.text(0.5, 0.5, 'No metrics available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return
            
        labels = list(metrics.keys())
        values = list(metrics.values())
        
        ax.bar(range(len(labels)), values, color='#9b59b6')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel('Value')
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_transformation_info(self, ax, frame: Dict):
        """Plot transformation information on an axis."""
        ax.axis('off')
        
        info_text = f"Transformation: {frame['name']}\n\n"
        
        before_stats = frame['before'].get_statistics()
        after_stats = frame['after'].get_statistics()
        
        info_text += "Changes:\n"
        info_text += f"Words: {before_stats['word_count']} → {after_stats['word_count']}\n"
        info_text += f"Headings: {before_stats['heading_count']} → {after_stats['heading_count']}\n"
        info_text += f"Paragraphs: {before_stats['paragraph_count']} → {after_stats['paragraph_count']}\n"
        
        ax.text(0.1, 0.9, info_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', family='monospace')


class StateSpaceEvolutionAnimator:
    """
    Animate the evolution of document state space as content is added.
    
    This thin orchestrator shows how the state transition graph grows and
    evolves as more markdown content is processed.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the state space animator.
        
        Args:
            figsize: Figure size for animations
        """
        self.figsize = figsize
        self.state_spaces = []
        
    def add_snapshot(self, state_space: StateSpace, label: str = ""):
        """
        Add a state space snapshot.
        
        Args:
            state_space: StateSpace instance to snapshot
            label: Label for this snapshot
        """
        # Create a deep copy of the state space state
        snapshot = {
            'states': dict(state_space.states),
            'transitions': {k: dict(v) for k, v in state_space.transitions.items()},
            'label': label,
            'graph': state_space.graph.copy()
        }
        self.state_spaces.append(snapshot)
    
    def create_animation(self, output_path: str, fps: int = 1) -> str:
        """
        Create an animation showing state space evolution.
        
        Args:
            output_path: Path to save animation
            fps: Frames per second
            
        Returns:
            Path to saved animation
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        def update(frame_idx):
            ax1.clear()
            ax2.clear()
            
            if frame_idx >= len(self.state_spaces):
                return
                
            snapshot = self.state_spaces[frame_idx]
            
            # Left: State transition graph
            ax1.set_title(f"State Space: {snapshot['label']}")
            self._plot_state_graph(ax1, snapshot['graph'])
            
            # Right: Statistics
            ax2.set_title("Statistics")
            self._plot_statistics(ax2, snapshot)
            
            fig.tight_layout()
        
        anim = animation.FuncAnimation(fig, update, frames=len(self.state_spaces),
                                      interval=1000/fps, repeat=True)
        anim.save(output_path, writer='pillow')
        plt.close()
        
        return output_path
    
    def _plot_state_graph(self, ax, graph: nx.DiGraph):
        """Plot state transition graph."""
        if not graph.nodes():
            ax.text(0.5, 0.5, 'Empty graph', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return
            
        pos = nx.spring_layout(graph)
        
        # Color nodes by type
        node_colors = []
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_type = node_data.get('type', 'unknown')
            colors = {
                'heading': '#3498db',
                'paragraph': '#2ecc71',
                'list': '#f39c12',
                'code': '#e74c3c'
            }
            node_colors.append(colors.get(node_type, '#95a5a6'))
        
        nx.draw(graph, pos, ax=ax, node_color=node_colors,
               with_labels=False, node_size=300, arrows=True,
               edge_color='#bdc3c7', alpha=0.7)
        ax.axis('off')
    
    def _plot_statistics(self, ax, snapshot: Dict):
        """Plot statistics about the state space."""
        stats = {
            'States': len(snapshot['states']),
            'Transitions': sum(len(v) for v in snapshot['transitions'].values()),
            'Nodes': snapshot['graph'].number_of_nodes(),
            'Edges': snapshot['graph'].number_of_edges()
        }
        
        labels = list(stats.keys())
        values = list(stats.values())
        
        ax.barh(labels, values, color='#9b59b6')
        ax.set_xlabel('Count')
        ax.grid(axis='x', alpha=0.3)


class MarkChainGenerationAnimator:
    """
    Animate the process of text generation from a Markov chain.
    
    Shows how the chain selects states and builds up generated content.
    """
    
    def __init__(self, chain: MarkChain, figsize: Tuple[int, int] = (14, 10)):
        """
        Initialize the generation animator.
        
        Args:
            chain: Trained MarkChain instance
            figsize: Figure size
        """
        self.chain = chain
        self.figsize = figsize
        
    def animate_generation(self, output_path: str, steps: int = 10, fps: int = 1) -> str:
        """
        Animate the generation process.
        
        Args:
            output_path: Path to save animation
            steps: Number of generation steps
            fps: Frames per second
            
        Returns:
            Path to saved animation
        """
        # Record generation steps
        generation_history = []
        current_states = []
        
        # Choose starting state
        if self.chain.start_states:
            import random
            states_list = list(self.chain.start_states.keys())
            weights = [self.chain.start_states[s] for s in states_list]
            current = random.choices(states_list, weights=weights)[0]
        else:
            current = random.choice(list(self.chain.states))
        
        current_states.append(current)
        generation_history.append({
            'state': current,
            'accumulated': [current],
            'transitions': dict(self.chain.transitions.get(current, {}))
        })
        
        # Generate subsequent states
        for _ in range(steps - 1):
            if current not in self.chain.transitions or not self.chain.transitions[current]:
                current = random.choice(list(self.chain.states))
            else:
                next_states = list(self.chain.transitions[current].keys())
                weights = [self.chain.transitions[current][s] for s in next_states]
                current = random.choices(next_states, weights=weights)[0]
            
            current_states.append(current)
            generation_history.append({
                'state': current,
                'accumulated': list(current_states),
                'transitions': dict(self.chain.transitions.get(current, {}))
            })
        
        # Create animation
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        
        def update(frame_idx):
            for ax in axes.flat:
                ax.clear()
            
            if frame_idx >= len(generation_history):
                return
                
            step = generation_history[frame_idx]
            
            # Top left: Current state
            axes[0, 0].set_title(f"Step {frame_idx + 1}: Current State")
            axes[0, 0].text(0.5, 0.5, step['state'][:50] + '...' if len(step['state']) > 50 else step['state'],
                           ha='center', va='center', wrap=True, fontsize=10)
            axes[0, 0].axis('off')
            
            # Top right: Possible transitions
            axes[0, 1].set_title("Transition Probabilities")
            if step['transitions']:
                states = list(step['transitions'].keys())[:5]  # Top 5
                probs = [step['transitions'][s] for s in states]
                total = sum(step['transitions'].values())
                probs = [p/total for p in probs]
                
                axes[0, 1].barh([s[:20] + '...' if len(s) > 20 else s for s in states], probs)
                axes[0, 1].set_xlabel('Probability')
            else:
                axes[0, 1].text(0.5, 0.5, 'No transitions', ha='center', va='center')
                axes[0, 1].axis('off')
            
            # Bottom left: Generated text so far
            axes[1, 0].set_title("Generated Content")
            text = '\n\n'.join(step['accumulated'])
            axes[1, 0].text(0.05, 0.95, text[:200] + '...' if len(text) > 200 else text,
                           transform=axes[1, 0].transAxes, verticalalignment='top',
                           fontsize=8, family='monospace')
            axes[1, 0].axis('off')
            
            # Bottom right: Progress
            axes[1, 1].set_title("Generation Progress")
            axes[1, 1].barh(['Progress'], [frame_idx / len(generation_history)], color='#27ae60')
            axes[1, 1].set_xlim(0, 1)
            axes[1, 1].text(frame_idx / len(generation_history), 0, 
                           f"{frame_idx}/{len(generation_history)}", 
                           ha='left', va='center')
            
            fig.tight_layout()
        
        anim = animation.FuncAnimation(fig, update, frames=len(generation_history),
                                      interval=1000/fps, repeat=True)
        anim.save(output_path, writer='pillow')
        plt.close()
        
        return output_path


class BeliefStateAnimator:
    """
    Animate belief state evolution as a document is analyzed.
    
    Shows how beliefs about document semantics change with each observation.
    """
    
    def __init__(self, updater: BeliefUpdater, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the belief state animator.
        
        Args:
            updater: BeliefUpdater instance
            figsize: Figure size
        """
        self.updater = updater
        self.figsize = figsize
        self.belief_history = []
        
    def add_observation(self, observation: Dict[str, float], label: str = ""):
        """
        Add an observation and record belief state.
        
        Args:
            observation: Observation dictionary
            label: Label for this observation
        """
        self.updater.update_from_observation(observation)
        self.belief_history.append({
            'beliefs': dict(self.updater.beliefs),
            'observation': observation,
            'label': label,
            'entropy': self.updater.calculate_entropy()
        })
    
    def create_animation(self, output_path: str, fps: int = 1) -> str:
        """
        Create animation of belief evolution.
        
        Args:
            output_path: Path to save animation
            fps: Frames per second
            
        Returns:
            Path to saved animation
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        
        def update(frame_idx):
            for ax in axes.flat:
                ax.clear()
            
            if frame_idx >= len(self.belief_history):
                return
                
            step = self.belief_history[frame_idx]
            
            # Top left: Current beliefs
            axes[0, 0].set_title(f"Beliefs: {step['label']}")
            classes = list(step['beliefs'].keys())
            values = list(step['beliefs'].values())
            axes[0, 0].barh(classes, values, color='#3498db')
            axes[0, 0].set_xlim(0, 1)
            axes[0, 0].set_xlabel('Probability')
            axes[0, 0].grid(axis='x', alpha=0.3)
            
            # Top right: Entropy over time
            axes[0, 1].set_title("Belief Entropy")
            entropies = [h['entropy'] for h in self.belief_history[:frame_idx+1]]
            axes[0, 1].plot(range(len(entropies)), entropies, 'o-', color='#e74c3c')
            axes[0, 1].set_xlabel('Observation')
            axes[0, 1].set_ylabel('Entropy')
            axes[0, 1].grid(alpha=0.3)
            
            # Bottom left: Current observation
            axes[1, 0].set_title("Current Observation")
            if step['observation']:
                obs_labels = list(step['observation'].keys())
                obs_values = list(step['observation'].values())
                axes[1, 0].bar(obs_labels, obs_values, color='#2ecc71')
                axes[1, 0].set_ylabel('Value')
                axes[1, 0].tick_params(axis='x', rotation=45)
            else:
                axes[1, 0].text(0.5, 0.5, 'No observation', ha='center', va='center')
                axes[1, 0].axis('off')
            
            # Bottom right: Most likely class
            axes[1, 1].set_title("Most Likely Class")
            most_likely = max(step['beliefs'].items(), key=lambda x: x[1])
            axes[1, 1].text(0.5, 0.6, most_likely[0], 
                           ha='center', va='center', fontsize=20, weight='bold')
            axes[1, 1].text(0.5, 0.4, f"Probability: {most_likely[1]:.2f}",
                           ha='center', va='center', fontsize=14)
            axes[1, 1].axis('off')
            
            fig.tight_layout()
        
        anim = animation.FuncAnimation(fig, update, frames=len(self.belief_history),
                                      interval=1000/fps, repeat=True)
        anim.save(output_path, writer='pillow')
        plt.close()
        
        return output_path


def create_comprehensive_animation(document_path: str, 
                                  output_dir: str = "animations",
                                  transformations: Optional[List] = None) -> Dict[str, str]:
    """
    Thin orchestrator that creates a comprehensive set of animations.
    
    This function coordinates all animation types to provide a complete
    visual analysis of a markdown document.
    
    Args:
        document_path: Path to markdown document
        output_dir: Directory to save animations
        transformations: Optional list of transformations to apply
        
    Returns:
        Dictionary mapping animation types to output paths
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    outputs = {}
    
    # Load document
    doc = Document(file_path=document_path)
    
    # 1. State space evolution
    ss_animator = StateSpaceEvolutionAnimator()
    state_space = StateSpace()
    
    # Add progressive snapshots
    lines = doc.get_content().split('\n\n')
    for i, chunk in enumerate(['\n\n'.join(lines[:j+1]) for j in range(len(lines))]):
        ss = StateSpace()
        ss.parse_markdown(chunk)
        ss_animator.add_snapshot(ss, f"Lines 1-{i+1}")
        if i >= 10:  # Limit frames
            break
    
    outputs['state_space'] = ss_animator.create_animation(
        f"{output_dir}/state_space_evolution.gif", fps=2
    )
    
    # 2. MarkChain generation
    chain = MarkChain()
    chain.train(doc.get_content())
    mc_animator = MarkChainGenerationAnimator(chain)
    outputs['generation'] = mc_animator.animate_generation(
        f"{output_dir}/generation_process.gif", steps=10, fps=1
    )
    
    # 3. Belief state evolution
    updater = BeliefUpdater()
    bs_animator = BeliefStateAnimator(updater)
    
    state_space_full = StateSpace()
    state_space_full.parse_markdown(doc.get_content())
    
    # Add observations progressively
    observations = [
        ({'structure': 0.8, 'readability': 0.6}, "Initial"),
        ({'complexity': 0.7, 'coherence': 0.5}, "Mid"),
        ({'consistency': 0.9, 'structure': 0.9}, "Final")
    ]
    
    for obs, label in observations:
        bs_animator.add_observation(obs, label)
    
    outputs['beliefs'] = bs_animator.create_animation(
        f"{output_dir}/belief_evolution.gif", fps=1
    )
    
    return outputs


