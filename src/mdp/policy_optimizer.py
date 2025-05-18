"""
PolicyOptimizer: A module for transforming Markdown documents to optimize for 
specific reward functions, inspired by Markov Decision Process policies.
"""

import re
import math
from typing import Dict, List, Callable, Optional, Union, Tuple, Any

class PolicyOptimizer:
    """
    Optimizes Markdown documents according to specified reward functions
    and a stochastic policy that guides state transitions.
    """
    
    def __init__(
        self, 
        reward_weights: Dict[str, float] = None,
        custom_rewards: Dict[str, Callable] = None,
        learning_rate: float = 0.1,
        max_iterations: int = 100
    ):
        """
        Initialize a PolicyOptimizer instance.
        
        Args:
            reward_weights: Weights for different reward components
            custom_rewards: Custom reward functions
            learning_rate: Learning rate for policy optimization
            max_iterations: Maximum number of iterations for optimization
        """
        self.reward_weights = reward_weights or {
            "readability": 1.0,
            "information_density": 0.5,
            "structure_clarity": 0.8,
        }
        
        self.custom_rewards = custom_rewards or {}
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        
        # Register default reward functions
        self.default_rewards = {
            "readability": self._readability_reward,
            "information_density": self._information_density_reward,
            "structure_clarity": self._structure_clarity_reward,
        }
    
    def transform(self, markdown_path: str) -> str:
        """
        Transform a markdown document to optimize its reward.
        
        Args:
            markdown_path: Path to the markdown file
            
        Returns:
            Optimized markdown content
        """
        # Read the markdown file
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the document into a state structure
        document_structure = self._parse_document(content)
        
        # Apply optimizations iteratively
        for _ in range(self.max_iterations):
            # Calculate current reward
            current_reward = self._calculate_total_reward(document_structure)
            
            # Try possible transformations
            best_structure = document_structure
            best_reward = current_reward
            
            for transform in self._get_possible_transforms(document_structure):
                transformed = self._apply_transform(document_structure, transform)
                reward = self._calculate_total_reward(transformed)
                
                if reward > best_reward:
                    best_structure = transformed
                    best_reward = reward
            
            # If no improvement, stop
            if best_reward <= current_reward:
                break
                
            document_structure = best_structure
            
        # Convert optimized structure back to markdown
        return self._structure_to_markdown(document_structure)
    
    def _parse_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown document into a structured representation.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of document elements with metadata
        """
        lines = content.split('\n')
        elements = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Headers
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                text = line[level:].strip()
                elements.append({
                    'type': 'header',
                    'level': level,
                    'text': text,
                    'content': line
                })
                i += 1
                
            # Lists
            elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                list_items = []
                list_type = 'unordered' if line.startswith(('- ', '* ')) else 'ordered'
                
                while i < len(lines) and (
                    lines[i].strip().startswith('- ') or 
                    lines[i].strip().startswith('* ') or 
                    re.match(r'^\d+\.', lines[i].strip())
                ):
                    list_items.append(lines[i])
                    i += 1
                
                elements.append({
                    'type': 'list',
                    'list_type': list_type,
                    'items': list_items,
                    'content': '\n'.join(list_items)
                })
                
            # Code blocks
            elif line.startswith('```'):
                code_lines = [line]
                lang = line[3:].strip()
                i += 1
                
                while i < len(lines) and not lines[i].strip() == '```':
                    code_lines.append(lines[i])
                    i += 1
                    
                if i < len(lines):
                    code_lines.append(lines[i])
                    i += 1
                    
                elements.append({
                    'type': 'code',
                    'language': lang,
                    'lines': code_lines[1:-1] if len(code_lines) > 2 else [],
                    'content': '\n'.join(code_lines)
                })
                
            # Blank lines
            elif not line:
                elements.append({
                    'type': 'blank',
                    'content': ''
                })
                i += 1
                
            # Regular paragraphs
            else:
                paragraph_lines = [line]
                i += 1
                
                while i < len(lines) and lines[i].strip() and not (
                    lines[i].strip().startswith('#') or 
                    lines[i].strip().startswith('- ') or 
                    lines[i].strip().startswith('* ') or 
                    re.match(r'^\d+\.', lines[i].strip()) or
                    lines[i].strip().startswith('```')
                ):
                    paragraph_lines.append(lines[i])
                    i += 1
                    
                text = ' '.join([l.strip() for l in paragraph_lines])
                elements.append({
                    'type': 'paragraph',
                    'text': text,
                    'content': '\n'.join(paragraph_lines)
                })
                
        return elements
    
    def _calculate_total_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate the total reward for a document structure.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Total reward value
        """
        total_reward = 0.0
        
        # Apply all reward functions
        for reward_name, weight in self.reward_weights.items():
            if reward_name in self.custom_rewards:
                reward_func = self.custom_rewards[reward_name]
            elif reward_name in self.default_rewards:
                reward_func = self.default_rewards[reward_name]
            else:
                continue
                
            reward = reward_func(document_structure)
            total_reward += weight * reward
            
        return total_reward
    
    def _readability_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate readability reward based on sentence length, paragraph length,
        and structure clarity.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Readability reward value
        """
        reward = 0.0
        
        for element in document_structure:
            if element['type'] == 'paragraph':
                text = element['text']
                
                # Penalize extremely long paragraphs
                paragraph_length = len(text.split())
                if paragraph_length > 200:
                    reward -= (paragraph_length - 200) * 0.01
                    
                # Analyze sentences
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    words = sentence.strip().split()
                    
                    # Reward moderately sized sentences
                    if 5 <= len(words) <= 25:
                        reward += 0.5
                    elif len(words) > 25:
                        reward -= (len(words) - 25) * 0.05
            
            # Reward appropriate header levels
            elif element['type'] == 'header':
                if element['level'] <= 3:
                    reward += 1.0
                    
            # Reward lists (easy to scan)
            elif element['type'] == 'list':
                reward += 0.5 * len(element['items'])
                
        return reward
    
    def _information_density_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate information density reward based on keyword concentration,
        code blocks, and substantive content.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Information density reward value
        """
        reward = 0.0
        total_content = ""
        
        # Collect all textual content
        for element in document_structure:
            if element['type'] in ('paragraph', 'header'):
                total_content += " " + element.get('text', '')
                
        # Analyze keyword density
        words = total_content.lower().split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
            
        # Reward code blocks (high information density)
        code_block_count = sum(1 for e in document_structure if e['type'] == 'code')
        reward += code_block_count * 2.0
        
        # Calculate word frequency
        word_freq = {}
        for word in words:
            word = re.sub(r'[^\w]', '', word)
            if len(word) >= 4:  # Only count substantive words
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Reward for diverse vocabulary (higher information)
        unique_words = len(word_freq)
        diversity_ratio = unique_words / max(1, word_count)
        reward += diversity_ratio * 10
        
        return reward
    
    def _structure_clarity_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate structure clarity reward based on heading hierarchy,
        section balance, and overall organization.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Structure clarity reward value
        """
        reward = 0.0
        
        # Check for document title (h1)
        has_title = any(e['type'] == 'header' and e['level'] == 1 
                        for e in document_structure)
        if has_title:
            reward += 3.0
            
        # Track header levels to check hierarchy
        current_level = 0
        sections = []
        current_section = []
        
        for element in document_structure:
            if element['type'] == 'header':
                # New section encountered
                if current_section:
                    sections.append((current_level, current_section))
                    
                current_level = element['level']
                current_section = [element]
                
                # Penalize skipping header levels (e.g., h1 -> h3)
                if current_level > 1 and current_level - 1 > current_level:
                    reward -= 1.0
            else:
                current_section.append(element)
                
        # Add the last section
        if current_section:
            sections.append((current_level, current_section))
            
        # Reward balanced sections
        section_sizes = [len(s[1]) for s in sections]
        if section_sizes:
            avg_size = sum(section_sizes) / len(section_sizes)
            for size in section_sizes:
                balance = 1.0 - min(abs(size - avg_size) / max(avg_size, 1.0), 0.8)
                reward += balance
                
        # Reward logical grouping of elements
        for level, section in sections:
            # Reward paragraphs after headers
            for i in range(len(section) - 1):
                if section[i]['type'] == 'header' and section[i+1]['type'] == 'paragraph':
                    reward += 0.5
                    
            # Reward lists after introductory paragraphs
            for i in range(len(section) - 1):
                if section[i]['type'] == 'paragraph' and section[i+1]['type'] == 'list':
                    reward += 0.5
        
        return reward
    
    def _get_possible_transforms(self, document_structure: List[Dict[str, Any]]) -> List[Dict]:
        """
        Generate possible transformations of the document.
        
        Args:
            document_structure: Current document structure
            
        Returns:
            List of possible transformations
        """
        transforms = []
        
        # Split long paragraphs
        for i, element in enumerate(document_structure):
            if element['type'] == 'paragraph':
                text = element['text']
                words = text.split()
                
                if len(words) > 150:
                    transforms.append({
                        'type': 'split_paragraph',
                        'index': i
                    })
        
        # Add section headers before long content blocks
        for i in range(1, len(document_structure)):
            if all(document_structure[j]['type'] not in ('header', 'blank') 
                   for j in range(max(0, i-5), i)):
                transforms.append({
                    'type': 'add_header',
                    'index': i
                })
        
        # Convert paragraphs to lists where appropriate
        for i, element in enumerate(document_structure):
            if element['type'] == 'paragraph':
                text = element['text']
                sentences = re.split(r'[.!?]+', text)
                
                # Check if paragraph has list-like sentences
                if len(sentences) >= 3 and all(len(s.strip()) > 0 for s in sentences):
                    similar_starts = 0
                    for j in range(1, len(sentences)):
                        words1 = sentences[j-1].strip().lower().split()
                        words2 = sentences[j].strip().lower().split()
                        
                        if words1 and words2 and words1[0] == words2[0]:
                            similar_starts += 1
                    
                    if similar_starts >= len(sentences) // 2:
                        transforms.append({
                            'type': 'convert_to_list',
                            'index': i
                        })
        
        return transforms
    
    def _apply_transform(
        self, document_structure: List[Dict[str, Any]], transform: Dict
    ) -> List[Dict[str, Any]]:
        """
        Apply a transformation to the document structure.
        
        Args:
            document_structure: Current document structure
            transform: Transformation to apply
            
        Returns:
            Transformed document structure
        """
        result = document_structure.copy()
        
        if transform['type'] == 'split_paragraph':
            idx = transform['index']
            element = result[idx]
            
            if element['type'] != 'paragraph':
                return result
                
            text = element['text']
            sentences = re.split(r'([.!?]+)', text)
            
            # Rejoin sentences with their punctuation
            if len(sentences) % 2 == 0:
                sentences.append('')
            
            complete_sentences = [''.join(sentences[i:i+2]).strip() 
                                  for i in range(0, len(sentences), 2)]
            
            # Find a good split point (around the middle)
            mid = len(complete_sentences) // 2
            
            first_half = ' '.join(complete_sentences[:mid])
            second_half = ' '.join(complete_sentences[mid:])
            
            # Create new paragraph elements
            first_element = {
                'type': 'paragraph',
                'text': first_half,
                'content': first_half
            }
            second_element = {
                'type': 'paragraph',
                'text': second_half,
                'content': second_half
            }
            
            # Replace original with split paragraphs
            result[idx] = first_element
            result.insert(idx + 1, second_element)
            
        elif transform['type'] == 'add_header':
            idx = transform['index']
            
            # Infer a header title from the following content
            title = 'Section'
            if idx < len(result):
                next_element = result[idx]
                if next_element['type'] == 'paragraph':
                    words = next_element['text'].split()[:5]
                    title = ' '.join(words) + '...'
                elif next_element['type'] == 'list':
                    if next_element['items']:
                        first_item = next_element['items'][0]
                        title = re.sub(r'^[-*\d.]\s+', '', first_item)[:20] + '...'
            
            # Determine appropriate heading level
            level = 2  # Default to h2
            for i in range(idx - 1, -1, -1):
                if result[i]['type'] == 'header':
                    # Use one level deeper than the previous header
                    level = min(result[i]['level'] + 1, 3)
                    break
            
            header_element = {
                'type': 'header',
                'level': level,
                'text': title,
                'content': '#' * level + ' ' + title
            }
            
            result.insert(idx, header_element)
            
        elif transform['type'] == 'convert_to_list':
            idx = transform['index']
            element = result[idx]
            
            if element['type'] != 'paragraph':
                return result
                
            text = element['text']
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            
            list_items = ['- ' + s for s in sentences]
            
            list_element = {
                'type': 'list',
                'list_type': 'unordered',
                'items': list_items,
                'content': '\n'.join(list_items)
            }
            
            result[idx] = list_element
            
        return result
    
    def _structure_to_markdown(self, document_structure: List[Dict[str, Any]]) -> str:
        """
        Convert a document structure back to markdown.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Markdown content
        """
        markdown_lines = []
        
        for i, element in enumerate(document_structure):
            # Add spacing between elements
            if i > 0 and element['type'] != 'blank' and document_structure[i-1]['type'] != 'blank':
                markdown_lines.append('')
                
            markdown_lines.append(element['content'])
            
        return '\n'.join(markdown_lines) 