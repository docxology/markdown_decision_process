"""
Versioning for Markdown Decision Process.

This module provides versioning capabilities for Markdown documents,
including version tracking, diffing, and history management.
"""

import os
import re
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import difflib
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class Version:
    """Represents a version of a document."""
    id: str
    content: str
    timestamp: str
    author: str = "Unknown"
    message: str = ""
    parent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, content: str, message: str = "", author: str = "Unknown", 
              parent_id: Optional[str] = None, tags: Optional[List[str]] = None) -> "Version":
        """
        Create a new version.
        
        Args:
            content: Document content
            message: Version message
            author: Version author
            parent_id: ID of the parent version
            tags: List of tags for this version
            
        Returns:
            New Version instance
        """
        version_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        return cls(
            id=version_id,
            content=content,
            timestamp=timestamp,
            author=author,
            message=message,
            parent_id=parent_id,
            tags=tags or []
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the version to a dictionary.
        
        Returns:
            Dictionary representation of the version
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Version":
        """
        Create a version from a dictionary.
        
        Args:
            data: Dictionary representation of a version
            
        Returns:
            Version instance
        """
        return cls(
            id=data["id"],
            content=data["content"],
            timestamp=data["timestamp"],
            author=data["author"],
            message=data["message"],
            parent_id=data["parent_id"],
            tags=data["tags"],
            metadata=data["metadata"]
        )
    
    def compute_hash(self) -> str:
        """
        Compute a hash of the version content.
        
        Returns:
            Hash of the content
        """
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


class VersionHistory:
    """Manages version history for a document."""
    
    def __init__(self):
        """Initialize the version history."""
        self.versions: Dict[str, Version] = {}
        self.current_id: Optional[str] = None
        self.branch_heads: Dict[str, str] = {"main": None}
        self.current_branch: str = "main"
    
    def add_version(self, version: Version, set_as_current: bool = True) -> str:
        """
        Add a version to the history.
        
        Args:
            version: Version to add
            set_as_current: Whether to set this as the current version
            
        Returns:
            ID of the added version
        """
        self.versions[version.id] = version
        
        if self.branch_heads[self.current_branch] is None or set_as_current:
            self.branch_heads[self.current_branch] = version.id
            
        if set_as_current:
            self.current_id = version.id
            
        return version.id
    
    def get_version(self, version_id: Optional[str] = None) -> Optional[Version]:
        """
        Get a specific version.
        
        Args:
            version_id: ID of the version to get, or None for the current version
            
        Returns:
            Version instance, or None if not found
        """
        if version_id is None:
            version_id = self.current_id
            
        if version_id is None:
            return None
            
        return self.versions.get(version_id)
    
    def get_history(self, branch: Optional[str] = None) -> List[Version]:
        """
        Get the version history.
        
        Args:
            branch: Branch to get history for, or None for the current branch
            
        Returns:
            List of versions in chronological order
        """
        if branch is None:
            branch = self.current_branch
            
        head_id = self.branch_heads.get(branch)
        if head_id is None:
            return []
            
        history = []
        version_id = head_id
        
        while version_id is not None:
            version = self.versions.get(version_id)
            if version is None:
                break
                
            history.append(version)
            version_id = version.parent_id
            
        return list(reversed(history))
    
    def create_branch(self, name: str, from_version_id: Optional[str] = None) -> bool:
        """
        Create a new branch.
        
        Args:
            name: Name of the branch
            from_version_id: ID of the version to branch from, or None for the current version
            
        Returns:
            True if the branch was created, False otherwise
        """
        if name in self.branch_heads:
            return False
            
        if from_version_id is None:
            from_version_id = self.current_id
            
        if from_version_id is None:
            return False
            
        self.branch_heads[name] = from_version_id
        return True
    
    def switch_branch(self, branch: str) -> bool:
        """
        Switch to a different branch.
        
        Args:
            branch: Name of the branch to switch to
            
        Returns:
            True if the branch was switched, False otherwise
        """
        if branch not in self.branch_heads:
            return False
            
        self.current_branch = branch
        self.current_id = self.branch_heads[branch]
        return True
    
    def merge_branch(self, branch: str, message: str = "Merge", 
                    author: str = "Unknown") -> Optional[str]:
        """
        Merge a branch into the current branch.
        
        Args:
            branch: Name of the branch to merge
            message: Merge commit message
            author: Merge commit author
            
        Returns:
            ID of the merge commit, or None if the merge failed
        """
        if branch not in self.branch_heads or self.current_id is None:
            return None
            
        source_id = self.branch_heads[branch]
        target_id = self.current_id
        
        source = self.versions.get(source_id)
        target = self.versions.get(target_id)
        
        if source is None or target is None:
            return None
            
        # Simple text-based merge (real implementation would be more sophisticated)
        merged_content = self._merge_text(source.content, target.content)
        
        # Create merge commit
        merge_version = Version.create(
            content=merged_content,
            message=message,
            author=author,
            parent_id=target_id,
            tags=["merge", f"branch:{branch}"]
        )
        
        # Add metadata about the merge
        merge_version.metadata["merged_from"] = source_id
        merge_version.metadata["merged_branch"] = branch
        
        return self.add_version(merge_version)
    
    def _merge_text(self, source: str, target: str) -> str:
        """
        Merge two text contents.
        
        Args:
            source: Source content
            target: Target content
            
        Returns:
            Merged content
        """
        # This is a very simple merge strategy
        # A real implementation would use a more sophisticated algorithm
        
        # Split into lines
        source_lines = source.splitlines()
        target_lines = target.splitlines()
        
        # Use Python's difflib for a simple merge
        differ = difflib.Differ()
        diff = list(differ.compare(target_lines, source_lines))
        
        # Process diff to create merged content
        merged_lines = []
        for line in diff:
            if line.startswith('  '):  # Common line
                merged_lines.append(line[2:])
            elif line.startswith('+ '):  # Line from source
                merged_lines.append(line[2:])
            # Skip lines starting with '- ' (lines only in target)
        
        return '\n'.join(merged_lines)
    
    def revert_to(self, version_id: str, message: str = "Revert", 
                author: str = "Unknown") -> Optional[str]:
        """
        Revert to a previous version.
        
        Args:
            version_id: ID of the version to revert to
            message: Revert commit message
            author: Revert commit author
            
        Returns:
            ID of the revert commit, or None if the revert failed
        """
        if version_id not in self.versions or self.current_id is None:
            return None
            
        target = self.versions.get(version_id)
        
        if target is None:
            return None
            
        # Create revert commit
        revert_version = Version.create(
            content=target.content,
            message=message,
            author=author,
            parent_id=self.current_id,
            tags=["revert", f"revert-to:{version_id}"]
        )
        
        # Add metadata about the revert
        revert_version.metadata["reverted_to"] = version_id
        
        return self.add_version(revert_version)
    
    def diff_versions(self, from_id: str, to_id: Optional[str] = None) -> List[str]:
        """
        Get the diff between two versions.
        
        Args:
            from_id: ID of the base version
            to_id: ID of the target version, or None for the current version
            
        Returns:
            List of diff lines
        """
        if to_id is None:
            to_id = self.current_id
            
        if from_id not in self.versions or to_id not in self.versions:
            return []
            
        from_version = self.versions[from_id]
        to_version = self.versions[to_id]
        
        from_lines = from_version.content.splitlines()
        to_lines = to_version.content.splitlines()
        
        return list(difflib.unified_diff(
            from_lines, 
            to_lines,
            f"version:{from_id}",
            f"version:{to_id}",
            lineterm=""
        ))
    
    def save(self, path: Union[str, Path]) -> bool:
        """
        Save the version history to a file.
        
        Args:
            path: Path to save the history to
            
        Returns:
            True if the history was saved successfully, False otherwise
        """
        try:
            data = {
                "versions": {k: v.to_dict() for k, v in self.versions.items()},
                "current_id": self.current_id,
                "branch_heads": self.branch_heads,
                "current_branch": self.current_branch
            }
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            return True
        except Exception:
            return False
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> Optional["VersionHistory"]:
        """
        Load version history from a file.
        
        Args:
            path: Path to load the history from
            
        Returns:
            VersionHistory instance, or None if loading failed
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            history = cls()
            history.versions = {k: Version.from_dict(v) for k, v in data["versions"].items()}
            history.current_id = data["current_id"]
            history.branch_heads = data["branch_heads"]
            history.current_branch = data["current_branch"]
            
            return history
        except Exception:
            return None


class VersionedDocument:
    """A document with version history."""
    
    def __init__(self, initial_content: str = "", author: str = "Unknown"):
        """
        Initialize a versioned document.
        
        Args:
            initial_content: Initial document content
            author: Author of the initial version
        """
        self.history = VersionHistory()
        
        # Create initial version
        if initial_content:
            initial_version = Version.create(
                content=initial_content,
                message="Initial version",
                author=author
            )
            self.history.add_version(initial_version)
    
    @property
    def content(self) -> str:
        """
        Get the current content of the document.
        
        Returns:
            Current document content, or empty string if no versions exist
        """
        current = self.history.get_version()
        return current.content if current else ""
    
    def commit(self, content: str, message: str = "", author: str = "Unknown") -> str:
        """
        Commit a new version.
        
        Args:
            content: New document content
            message: Commit message
            author: Commit author
            
        Returns:
            ID of the new version
        """
        current_id = self.history.current_id
        
        version = Version.create(
            content=content,
            message=message,
            author=author,
            parent_id=current_id
        )
        
        return self.history.add_version(version)
    
    def checkout(self, version_id: str) -> bool:
        """
        Checkout a specific version.
        
        Args:
            version_id: ID of the version to checkout
            
        Returns:
            True if the checkout was successful, False otherwise
        """
        if version_id not in self.history.versions:
            return False
            
        self.history.current_id = version_id
        return True
    
    def get_version_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all versions.
        
        Returns:
            List of version information dictionaries
        """
        result = []
        
        for version_id, version in self.history.versions.items():
            result.append({
                "id": version_id,
                "author": version.author,
                "message": version.message,
                "timestamp": version.timestamp,
                "is_current": version_id == self.history.current_id
            })
            
        # Sort by timestamp
        result.sort(key=lambda v: v["timestamp"])
        
        return result
    
    def save(self, path: Union[str, Path]) -> bool:
        """
        Save the versioned document.
        
        Args:
            path: Path to save the document to
            
        Returns:
            True if the document was saved successfully, False otherwise
        """
        return self.history.save(path)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> Optional["VersionedDocument"]:
        """
        Load a versioned document.
        
        Args:
            path: Path to load the document from
            
        Returns:
            VersionedDocument instance, or None if loading failed
        """
        history = VersionHistory.load(path)
        
        if history is None:
            return None
            
        doc = cls()
        doc.history = history
        
        return doc


def create_version(content: str, message: str = "", author: str = "Unknown") -> Version:
    """
    Create a new version.
    
    Args:
        content: Document content
        message: Version message
        author: Version author
        
    Returns:
        New Version instance
    """
    return Version.create(content, message, author)


def diff_text(text1: str, text2: str) -> List[str]:
    """
    Generate a diff between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        List of diff lines
    """
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    return list(difflib.unified_diff(
        lines1,
        lines2,
        "text1",
        "text2",
        lineterm=""
    ))


def apply_diff(text: str, diff_lines: List[str]) -> str:
    """
    Apply a diff to text.
    
    Args:
        text: Base text
        diff_lines: Diff lines
        
    Returns:
        Text with diff applied
    """
    # Skip diff headers (first 2 lines)
    lines = diff_lines[2:]
    
    # Parse diff
    text_lines = text.splitlines()
    result_lines = text_lines.copy()
    
    line_num = 0
    for diff_line in lines:
        if diff_line.startswith('---') or diff_line.startswith('+++'):
            continue
            
        if diff_line.startswith('-'):
            # Remove line
            if line_num < len(result_lines):
                result_lines.pop(line_num)
        elif diff_line.startswith('+'):
            # Add line
            result_lines.insert(line_num, diff_line[1:])
            line_num += 1
        else:
            # Context line
            line_num += 1
    
    return '\n'.join(result_lines)


def init_versioning(path: Union[str, Path], initial_content: str = "") -> VersionedDocument:
    """
    Initialize versioning for a document.
    
    Args:
        path: Path to store the version history
        initial_content: Initial document content
        
    Returns:
        VersionedDocument instance
    """
    doc = VersionedDocument(initial_content)
    doc.save(path)
    return doc 