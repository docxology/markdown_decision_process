"""
Search configuration for Markdown Decision Process.

This module provides configuration options for searching in Markdown documents,
including search parameters, result formatting, and indexing options.
"""

from typing import Dict, List, Optional, Union, Any, Set
from enum import Enum
import re
from pathlib import Path
import json


class SearchMode(Enum):
    """Enum for different search modes."""
    EXACT = "exact"       # Exact string matching
    FUZZY = "fuzzy"       # Fuzzy matching with tolerance for typos
    REGEX = "regex"       # Regular expression matching
    SEMANTIC = "semantic" # Semantic matching based on meaning


class ElementType(Enum):
    """Enum for different Markdown element types."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
    IMAGE = "image"
    LINK = "link"
    ALL = "all"


class SearchConfig:
    """Configuration for Markdown document searches."""
    
    def __init__(self, 
                mode: SearchMode = SearchMode.EXACT,
                case_sensitive: bool = False,
                element_types: Optional[List[ElementType]] = None,
                max_results: int = 100,
                context_lines: int = 0,
                include_metadata: bool = False):
        """
        Initialize the search configuration.
        
        Args:
            mode: Search mode (EXACT, FUZZY, REGEX, SEMANTIC)
            case_sensitive: Whether the search is case sensitive
            element_types: List of element types to search in
            max_results: Maximum number of results to return
            context_lines: Number of context lines to include around matches
            include_metadata: Whether to include element metadata in results
        """
        self.mode = mode
        self.case_sensitive = case_sensitive
        self.element_types = element_types or [ElementType.ALL]
        self.max_results = max_results
        self.context_lines = context_lines
        self.include_metadata = include_metadata
        
        # Fuzzy search parameters
        self.fuzzy_threshold = 0.8  # Minimum similarity score (0-1)
        self.fuzzy_ignore_case = not case_sensitive
        
        # Semantic search parameters
        self.semantic_model = None
        self.semantic_threshold = 0.7  # Minimum similarity score (0-1)
        
        # Advanced options
        self.highlight_matches = True
        self.highlight_style = "**{match}**"  # Format for highlighting matches
        self.sort_by = "relevance"  # Options: relevance, position, element_type
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "mode": self.mode.value,
            "case_sensitive": self.case_sensitive,
            "element_types": [et.value for et in self.element_types],
            "max_results": self.max_results,
            "context_lines": self.context_lines,
            "include_metadata": self.include_metadata,
            "fuzzy_threshold": self.fuzzy_threshold,
            "fuzzy_ignore_case": self.fuzzy_ignore_case,
            "semantic_threshold": self.semantic_threshold,
            "highlight_matches": self.highlight_matches,
            "highlight_style": self.highlight_style,
            "sort_by": self.sort_by
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SearchConfig":
        """
        Create a configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Returns:
            SearchConfig instance
        """
        config = cls()
        
        if "mode" in config_dict:
            config.mode = SearchMode(config_dict["mode"])
        
        if "case_sensitive" in config_dict:
            config.case_sensitive = config_dict["case_sensitive"]
        
        if "element_types" in config_dict:
            config.element_types = [ElementType(et) for et in config_dict["element_types"]]
        
        if "max_results" in config_dict:
            config.max_results = config_dict["max_results"]
        
        if "context_lines" in config_dict:
            config.context_lines = config_dict["context_lines"]
        
        if "include_metadata" in config_dict:
            config.include_metadata = config_dict["include_metadata"]
        
        if "fuzzy_threshold" in config_dict:
            config.fuzzy_threshold = config_dict["fuzzy_threshold"]
        
        if "fuzzy_ignore_case" in config_dict:
            config.fuzzy_ignore_case = config_dict["fuzzy_ignore_case"]
        
        if "semantic_threshold" in config_dict:
            config.semantic_threshold = config_dict["semantic_threshold"]
        
        if "highlight_matches" in config_dict:
            config.highlight_matches = config_dict["highlight_matches"]
        
        if "highlight_style" in config_dict:
            config.highlight_style = config_dict["highlight_style"]
        
        if "sort_by" in config_dict:
            config.sort_by = config_dict["sort_by"]
        
        return config
    
    def save(self, output_path: Union[str, Path]) -> None:
        """
        Save the configuration to a file.
        
        Args:
            output_path: Path to save the configuration to
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, input_path: Union[str, Path]) -> "SearchConfig":
        """
        Load a configuration from a file.
        
        Args:
            input_path: Path to load the configuration from
            
        Returns:
            SearchConfig instance
        """
        with open(input_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)


class SearchIndex:
    """Index for efficient searching of Markdown documents."""
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """
        Initialize the search index.
        
        Args:
            config: Search configuration
        """
        self.config = config or SearchConfig()
        self.documents = {}
        self.inverted_index = {}  # Maps terms to document IDs and positions
        self.element_index = {}   # Maps element types to document IDs and positions
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a document to the index.
        
        Args:
            doc_id: Document identifier
            content: Document content
            metadata: Document metadata
        """
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata or {}
        }
        
        # Process the document and update indexes
        self._index_document(doc_id, content)
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Remove a document from the index.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if the document was removed, False otherwise
        """
        if doc_id not in self.documents:
            return False
        
        # Remove from documents
        del self.documents[doc_id]
        
        # Remove from inverted index
        for term, postings in list(self.inverted_index.items()):
            if doc_id in postings:
                del self.inverted_index[term][doc_id]
                if not self.inverted_index[term]:
                    del self.inverted_index[term]
        
        # Remove from element index
        for element_type, elements in list(self.element_index.items()):
            if doc_id in elements:
                del self.element_index[element_type][doc_id]
                if not self.element_index[element_type]:
                    del self.element_index[element_type]
        
        return True
    
    def search(self, query: str, config: Optional[SearchConfig] = None) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query
            config: Search configuration (overrides the index configuration)
            
        Returns:
            List of search results
        """
        search_config = config or self.config
        
        if search_config.mode == SearchMode.EXACT:
            return self._exact_search(query, search_config)
        elif search_config.mode == SearchMode.FUZZY:
            return self._fuzzy_search(query, search_config)
        elif search_config.mode == SearchMode.REGEX:
            return self._regex_search(query, search_config)
        elif search_config.mode == SearchMode.SEMANTIC:
            return self._semantic_search(query, search_config)
        else:
            raise ValueError(f"Unsupported search mode: {search_config.mode}")
    
    def _index_document(self, doc_id: str, content: str) -> None:
        """
        Index a document.
        
        Args:
            doc_id: Document identifier
            content: Document content
        """
        # Split content into terms
        terms = self._tokenize(content)
        
        # Build inverted index
        for position, term in enumerate(terms):
            if term not in self.inverted_index:
                self.inverted_index[term] = {}
            
            if doc_id not in self.inverted_index[term]:
                self.inverted_index[term][doc_id] = []
            
            self.inverted_index[term][doc_id].append(position)
        
        # Build element index
        for element_type in ElementType:
            if element_type == ElementType.ALL:
                continue
                
            elements = self._extract_elements(content, element_type)
            
            if elements:
                if element_type.value not in self.element_index:
                    self.element_index[element_type.value] = {}
                
                self.element_index[element_type.value][doc_id] = elements
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into terms.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of terms
        """
        # Simple whitespace and punctuation tokenization
        terms = re.findall(r'\w+', text.lower())
        return terms
    
    def _extract_elements(self, content: str, element_type: ElementType) -> List[Dict[str, Any]]:
        """
        Extract elements of a specific type from content.
        
        Args:
            content: Document content
            element_type: Type of element to extract
            
        Returns:
            List of elements with positions and text
        """
        elements = []
        
        if element_type == ElementType.HEADING:
            # Extract headings
            for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
                elements.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(2),
                    "level": len(match.group(1))
                })
        
        elif element_type == ElementType.PARAGRAPH:
            # Extract paragraphs (simple approach)
            paragraphs = re.split(r'\n\s*\n', content)
            offset = 0
            for paragraph in paragraphs:
                if paragraph.strip() and not paragraph.strip().startswith(('#', '-', '*', '```')):
                    elements.append({
                        "start": offset,
                        "end": offset + len(paragraph),
                        "text": paragraph
                    })
                offset += len(paragraph) + 2  # +2 for the newlines
        
        elif element_type == ElementType.LIST:
            # Extract lists
            for match in re.finditer(r'((?:[\*\-]\s+.+\n?)+)', content):
                elements.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(1),
                    "type": "unordered"
                })
            
            for match in re.finditer(r'((?:\d+\.\s+.+\n?)+)', content):
                elements.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(1),
                    "type": "ordered"
                })
        
        elif element_type == ElementType.CODE_BLOCK:
            # Extract code blocks
            for match in re.finditer(r'```(\w*)\n(.*?)```', content, re.DOTALL):
                elements.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(2),
                    "language": match.group(1) or "plain"
                })
        
        return elements
    
    def _exact_search(self, query: str, config: SearchConfig) -> List[Dict[str, Any]]:
        """
        Perform exact search.
        
        Args:
            query: Search query
            config: Search configuration
            
        Returns:
            List of search results
        """
        results = []
        
        for doc_id, document in self.documents.items():
            content = document["content"]
            
            # Case sensitivity
            search_content = content if config.case_sensitive else content.lower()
            search_query = query if config.case_sensitive else query.lower()
            
            # Find all matches
            matches = []
            start = 0
            while True:
                pos = search_content.find(search_query, start)
                if pos == -1:
                    break
                
                matches.append({
                    "start": pos,
                    "end": pos + len(query),
                    "text": content[pos:pos + len(query)]
                })
                
                start = pos + 1
            
            if matches:
                results.append({
                    "doc_id": doc_id,
                    "matches": matches[:config.max_results],
                    "metadata": document["metadata"] if config.include_metadata else None
                })
        
        return results[:config.max_results]
    
    def _fuzzy_search(self, query: str, config: SearchConfig) -> List[Dict[str, Any]]:
        """
        Perform fuzzy search.
        
        Args:
            query: Search query
            config: Search configuration
            
        Returns:
            List of search results
        """
        # For simplicity, we'll use a basic character-level similarity measure
        # In a real implementation, this would use more sophisticated fuzzy matching
        results = []
        
        for doc_id, document in self.documents.items():
            content = document["content"]
            
            # Case sensitivity
            search_content = content if config.case_sensitive else content.lower()
            search_query = query if config.case_sensitive else query.lower()
            
            # Find potential matches (windows of text around query length)
            matches = []
            query_len = len(search_query)
            
            for i in range(len(search_content) - query_len + 1):
                window = search_content[i:i+query_len]
                similarity = self._calculate_similarity(window, search_query)
                
                if similarity >= config.fuzzy_threshold:
                    matches.append({
                        "start": i,
                        "end": i + query_len,
                        "text": content[i:i+query_len],
                        "similarity": similarity
                    })
            
            if matches:
                # Sort by similarity (highest first)
                matches.sort(key=lambda x: x["similarity"], reverse=True)
                
                results.append({
                    "doc_id": doc_id,
                    "matches": matches[:config.max_results],
                    "metadata": document["metadata"] if config.include_metadata else None
                })
        
        return results[:config.max_results]
    
    def _regex_search(self, query: str, config: SearchConfig) -> List[Dict[str, Any]]:
        """
        Perform regex search.
        
        Args:
            query: Search query (regex pattern)
            config: Search configuration
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            # Compile regex
            flags = 0 if config.case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags)
            
            for doc_id, document in self.documents.items():
                content = document["content"]
                
                # Find all matches
                matches = []
                for match in pattern.finditer(content):
                    matches.append({
                        "start": match.start(),
                        "end": match.end(),
                        "text": match.group(0)
                    })
                
                if matches:
                    results.append({
                        "doc_id": doc_id,
                        "matches": matches[:config.max_results],
                        "metadata": document["metadata"] if config.include_metadata else None
                    })
        except re.error:
            # Invalid regex pattern
            pass
        
        return results[:config.max_results]
    
    def _semantic_search(self, query: str, config: SearchConfig) -> List[Dict[str, Any]]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            config: Search configuration
            
        Returns:
            List of search results
        """
        # This is a placeholder for semantic search
        # A real implementation would use embeddings and vector similarity
        results = []
        
        # For now, just return an empty result
        return results
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity (simple Levenshtein-based measure).
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
            
        # Calculate Levenshtein distance
        m, n = len(str1), len(str2)
        d = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            d[i][0] = i
        for j in range(n + 1):
            d[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                d[i][j] = min(
                    d[i-1][j] + 1,      # deletion
                    d[i][j-1] + 1,      # insertion
                    d[i-1][j-1] + cost  # substitution
                )
        
        # Convert to similarity score (0-1)
        max_len = max(m, n)
        distance = d[m][n]
        similarity = 1.0 - (distance / max_len) if max_len > 0 else 1.0
        
        return similarity


# Default search configurations
DEFAULT_SEARCH_CONFIG = SearchConfig()

# Predefined configurations
FUZZY_SEARCH_CONFIG = SearchConfig(
    mode=SearchMode.FUZZY,
    fuzzy_threshold=0.7,
    highlight_matches=True
)

REGEX_SEARCH_CONFIG = SearchConfig(
    mode=SearchMode.REGEX,
    case_sensitive=True,
    highlight_matches=True
)

HEADING_SEARCH_CONFIG = SearchConfig(
    element_types=[ElementType.HEADING],
    highlight_matches=True
)


def create_config(mode: str = "exact", 
                case_sensitive: bool = False,
                element_types: Optional[List[str]] = None,
                max_results: int = 100) -> SearchConfig:
    """
    Create a search configuration with common parameters.
    
    Args:
        mode: Search mode ("exact", "fuzzy", "regex", "semantic")
        case_sensitive: Whether the search is case sensitive
        element_types: List of element types to search in
        max_results: Maximum number of results to return
        
    Returns:
        SearchConfig instance
    """
    config = SearchConfig(
        mode=SearchMode(mode),
        case_sensitive=case_sensitive,
        max_results=max_results
    )
    
    if element_types:
        config.element_types = [ElementType(et) for et in element_types]
    
    return config 