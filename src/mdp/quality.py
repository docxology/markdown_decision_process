"""
DocumentQuality module for analyzing and measuring the quality of markdown documents.

This module provides metrics for assessing readability, information density,
and structural balance of markdown documents through the lens of value functions
in a Markov Decision Process.
"""

from typing import Dict, Any, List, Optional, Union
import re
import math
from pathlib import Path
import numpy as np
import textstat
from textstat import flesch_reading_ease, flesch_kincaid_grade, smog_index, coleman_liau_index

from .document import Document
from .state_space import StateSpace


class DocumentQuality:
    """
    Analyzes markdown documents and computes quality metrics.
    
    This class serves as the value function assessor in the MDP framework,
    providing reward signals based on document characteristics.
    """
    
    def __init__(self, 
                 readability_weight: float = 0.4,
                 information_density_weight: float = 0.3,
                 structural_balance_weight: float = 0.3,
                 target_audience: str = "general"):
        """
        Initialize the DocumentQuality analyzer.
        
        Args:
            readability_weight: Weight for readability metrics (0.0 to 1.0)
            information_density_weight: Weight for information density metrics (0.0 to 1.0)
            structural_balance_weight: Weight for structural balance metrics (0.0 to 1.0)
            target_audience: Target audience profile ("general", "technical", "academic")
        """
        # Validate weights sum to 1.0
        total_weight = readability_weight + information_density_weight + structural_balance_weight
        if not math.isclose(total_weight, 1.0, abs_tol=0.01):
            weights_sum = readability_weight + information_density_weight + structural_balance_weight
            # Normalize weights
            readability_weight /= weights_sum
            information_density_weight /= weights_sum
            structural_balance_weight /= weights_sum
            
        self.readability_weight = readability_weight
        self.information_density_weight = information_density_weight
        self.structural_balance_weight = structural_balance_weight
        self.target_audience = target_audience

    def analyze_document(self, document: Union[Document, str, Path]) -> Dict[str, Any]:
        """
        Analyze a markdown document and return quality metrics.
        
        Args:
            document: MarkdownDocument instance, path to a markdown file, or content string
            
        Returns:
            Dictionary of quality metrics organized by category
        """
        # Ensure we have a MarkdownDocument
        if not isinstance(document, Document):
            if isinstance(document, (str, Path)) and Path(document).exists():
                document = Document(file_path=document)
            else:
                document = Document(content=str(document))
        
        # Get document structure
        structure = document.get_structure()
        
        # Calculate metrics for each category
        readability = self._calculate_readability_metrics(document, structure)
        information_density = self._calculate_information_density_metrics(document, structure)
        structural_balance = self._calculate_structural_balance_metrics(document, structure)
        
        # Calculate overall score
        overall_score = (
            self.readability_weight * readability.get('overall_readability', 0) +
            self.information_density_weight * information_density.get('overall_density', 0) +
            self.structural_balance_weight * structural_balance.get('overall_balance', 0)
        )
        
        # Determine overall semantic class based on metrics
        overall_semantic_class = self._determine_semantic_class(
            readability, information_density, structural_balance
        )
        
        return {
            'readability': readability,
            'information_density': information_density,
            'structural_balance': structural_balance,
            'overall_score': overall_score,
            'overall_semantic_class': overall_semantic_class
        }
        
    def _calculate_readability_metrics(self, 
                                      document: Document, 
                                      structure: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate readability metrics for the document.
        
        Args:
            document: MarkdownDocument instance
            structure: Document structure from get_structure()
            
        Returns:
            Dictionary of readability metrics
        """
        text = document.get_content()
        
        # Count sentences, words, and syllables
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = []
        for sentence in sentences:
            words.extend([w for w in re.findall(r'\b[a-zA-Z]+\b', sentence) if w])
        
        word_count = len(words)
        sentence_count = len(sentences)
        
        if word_count == 0 or sentence_count == 0:
            return {
                'avg_words_per_sentence': 0,
                'avg_sentence_length': 0,
                'complex_word_percentage': 0,
                'flesch_reading_ease': 0,
                'overall_readability': 0
            }
        
        # Calculate average words per sentence
        avg_words_per_sentence = word_count / sentence_count
        
        # Calculate average sentence length (in characters)
        sentence_lengths = [len(s) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / sentence_count
        
        # Calculate syllable count (approximate)
        def count_syllables(word):
            word = word.lower()
            # Count vowel groups as syllables
            count = len(re.findall(r'[aeiouy]+', word))
            # Adjust for common patterns
            if word.endswith('e'):
                count -= 1
            if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
                count += 1
            if count == 0:
                count = 1
            return count
        
        syllable_count = sum(count_syllables(word) for word in words)
        
        # Calculate complex words (words with 3+ syllables)
        complex_words = [word for word in words if count_syllables(word) >= 3]
        complex_word_percentage = len(complex_words) / word_count if word_count > 0 else 0
        
        # Calculate Flesch Reading Ease score
        flesch_reading_ease_score = flesch_reading_ease(text)
        # Normalize to 0-1 range
        normalized_flesch = max(0, min(flesch_reading_ease_score, 100)) / 100
        
        # Calculate overall readability score (0-1 range)
        overall_readability = (
            normalized_flesch * 0.5 +
            (1 - min(complex_word_percentage, 0.5) / 0.5) * 0.3 +
            (1 - min(avg_words_per_sentence, 30) / 30) * 0.2
        )
        
        return {
            'avg_words_per_sentence': avg_words_per_sentence,
            'avg_sentence_length': avg_sentence_length,
            'complex_word_percentage': complex_word_percentage,
            'flesch_reading_ease': flesch_reading_ease_score,
            'overall_readability': overall_readability
        }
        
    def _calculate_information_density_metrics(self, 
                                             document: Document, 
                                             structure: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate information density metrics for the document.
        
        Args:
            document: MarkdownDocument instance
            structure: Document structure from get_structure()
            
        Returns:
            Dictionary of information density metrics
        """
        # Count different types of elements
        element_counts = {
            'paragraph': 0,
            'heading': 0,
            'list': 0,
            'code': 0,
            'blockquote': 0,
            'table': 0,
            'link': 0,
            'image': 0
        }
        
        # Count all elements
        for element in structure:
            element_type = element['type']
            if element_type in element_counts:
                element_counts[element_type] += 1
        
        # Count total elements
        total_elements = sum(element_counts.values())
        
        # Calculate code density
        code_density = element_counts['code'] / max(1, total_elements)
        
        # Calculate list and table density (information-rich elements)
        structured_info_density = (element_counts['list'] + element_counts['table']) / max(1, total_elements)
        
        # Calculate media density
        media_density = element_counts['image'] / max(1, total_elements)
        
        # Calculate link density
        link_density = element_counts['link'] / max(1, total_elements)
        
        # Calculate text content word count and unique word ratio
        text = document.get_content()
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        unique_words = len(set(words))
        word_count = len(words)
        
        lexical_diversity = unique_words / max(1, word_count)
        
        # Calculate overall information density score (0-1 range)
        overall_density = (
            code_density * 0.3 +
            structured_info_density * 0.25 +
            media_density * 0.15 +
            link_density * 0.1 +
            lexical_diversity * 0.2
        )
        
        return {
            'code_density': code_density,
            'structured_info_density': structured_info_density,
            'media_density': media_density,
            'link_density': link_density,
            'lexical_diversity': lexical_diversity,
            'overall_density': overall_density
        }
        
    def _calculate_structural_balance_metrics(self, 
                                            document: Document, 
                                            structure: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate structural balance metrics for the document.
        
        Args:
            document: MarkdownDocument instance
            structure: Document structure from get_structure()
            
        Returns:
            Dictionary of structural balance metrics
        """
        # Extract headings and their levels
        headings = []
        for element in structure:
            if element['type'] == 'heading':
                headings.append({
                    'level': element['level'],
                    'text': element['text']
                })
        
        # Check if document has a title (h1)
        has_title = any(h['level'] == 1 for h in headings)
        
        # Check header hierarchy validity
        hierarchy_valid = True
        max_level_seen = 0
        for heading in headings:
            if heading['level'] > max_level_seen + 1:
                hierarchy_valid = False
                break
            max_level_seen = max(max_level_seen, heading['level'])
        
        # Calculate hierarchy score
        if len(headings) <= 1:
            hierarchy_score = 1.0 if has_title else 0.5
        else:
            hierarchy_score = 1.0 if hierarchy_valid and has_title else 0.5 if hierarchy_valid or has_title else 0.0
        
        # Calculate section balance
        sections = []
        current_section = {'heading': None, 'elements': []}
        
        for element in structure:
            if element['type'] == 'heading':
                if current_section['elements']:
                    sections.append(current_section)
                current_section = {'heading': element, 'elements': []}
            else:
                current_section['elements'].append(element)
                
        # Add the final section
        if current_section['elements']:
            sections.append(current_section)
            
        # Calculate section length balance
        section_lengths = [len(s['elements']) for s in sections]
        
        if not section_lengths:
            section_balance = 0.0
        elif len(section_lengths) == 1:
            section_balance = 1.0
        else:
            avg_length = sum(section_lengths) / len(section_lengths)
            # Calculate coefficient of variation (lower is better)
            variance = sum((length - avg_length) ** 2 for length in section_lengths) / len(section_lengths)
            std_dev = math.sqrt(variance)
            cv = std_dev / avg_length if avg_length > 0 else 0
            # Convert to a 0-1 score (1 is perfectly balanced)
            section_balance = max(0, 1 - min(cv, 1))
        
        # Calculate content type distribution
        element_types = [element['type'] for element in structure]
        unique_types = set(element_types)
        type_balance = len(unique_types) / 8  # Normalize by number of possible types
        
        # Calculate overall structural balance score (0-1 range)
        overall_balance = (
            hierarchy_score * 0.4 +
            section_balance * 0.4 +
            type_balance * 0.2
        )
        
        return {
            'has_title': has_title,
            'hierarchy_valid': hierarchy_valid,
            'hierarchy_score': hierarchy_score,
            'section_balance': section_balance,
            'type_balance': type_balance,
            'overall_balance': overall_balance
        }
        
    def _determine_semantic_class(self, 
                                readability: Dict[str, float],
                                information_density: Dict[str, float],
                                structural_balance: Dict[str, float]) -> str:
        """
        Determine the overall semantic class of the document based on metrics.
        
        Args:
            readability: Readability metrics
            information_density: Information density metrics
            structural_balance: Structural balance metrics
            
        Returns:
            String describing the document's semantic class
        """
        readability_score = readability.get('overall_readability', 0)
        density_score = information_density.get('overall_density', 0)
        balance_score = structural_balance.get('overall_balance', 0)
        
        # Determine document class based on metrics
        if readability_score > 0.8 and balance_score > 0.8:
            if density_score > 0.7:
                return "comprehensive_reference"
            else:
                return "clear_instructional"
        elif density_score > 0.8:
            if readability_score < 0.4:
                return "technical_dense"
            else:
                return "information_rich"
        elif balance_score < 0.3:
            return "poorly_structured"
        elif readability_score < 0.3:
            return "difficult_reading"
        else:
            return "balanced_document"
            
    def compare_documents(self, 
                       doc1: Union[Document, str, Path],
                       doc2: Union[Document, str, Path]) -> Dict[str, Any]:
        """
        Compare two documents and return their relative quality metrics.
        
        Args:
            doc1: First document (MarkdownDocument, path, or content string)
            doc2: Second document (MarkdownDocument, path, or content string)
            
        Returns:
            Dictionary containing comparison metrics
        """
        metrics1 = self.analyze_document(doc1)
        metrics2 = self.analyze_document(doc2)
        
        # Calculate differences
        differences = {
            'readability_diff': metrics2['readability']['overall_readability'] - metrics1['readability']['overall_readability'],
            'information_density_diff': metrics2['information_density']['overall_density'] - metrics1['information_density']['overall_density'],
            'structural_balance_diff': metrics2['structural_balance']['overall_balance'] - metrics1['structural_balance']['overall_balance'],
            'overall_score_diff': metrics2['overall_score'] - metrics1['overall_score']
        }
        
        # Determine which document is better overall
        if differences['overall_score_diff'] > 0.05:
            comparison_result = "second_document_better"
        elif differences['overall_score_diff'] < -0.05:
            comparison_result = "first_document_better"
        else:
            comparison_result = "documents_similar"
            
        return {
            'doc1_metrics': metrics1,
            'doc2_metrics': metrics2,
            'differences': differences,
            'comparison_result': comparison_result
        }

    def get_all_metrics(self) -> Dict[str, float]:
        """Calculates all quality metrics for the document."""
        # Ensure content is loaded for textstat analysis
        content = self.document.get_content()
        if not content:
            return {metric: 0.0 for metric in self.metrics_registry}

        # if not self.document.elements: # Use parsed elements if available # Old line
        if not self.document.get_elements(): # Use parsed elements if available. get_elements() ensures parsing.
            # This case implies content is empty or parsing yielded nothing, 
            # but content check above should handle empty content.
            # If get_elements() is empty but content is not, metrics might still be calculable.
            pass 

        results = {}
        # ... existing code ...
        return results 