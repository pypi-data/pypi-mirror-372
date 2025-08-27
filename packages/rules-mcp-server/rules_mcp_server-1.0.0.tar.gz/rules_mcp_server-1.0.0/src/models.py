"""
Data models for MCP Rules Server
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class RuleMetadata:
    """Metadata for a rule domain."""
    
    version: str
    last_updated: str
    description: str
    domain: str
    
    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.version:
            raise ValueError("Version cannot be empty")
        if not self.domain:
            raise ValueError("Domain cannot be empty")
        if not self.description:
            raise ValueError("Description cannot be empty")
    
    @classmethod
    def from_markdown_content(cls, content: str, domain: str) -> "RuleMetadata":
        """Parse metadata from markdown content."""
        metadata = cls._parse_metadata_section(content)
        
        return cls(
            version=metadata.get("version", "1.0"),
            last_updated=metadata.get("last_updated", datetime.now().strftime("%Y-%m-%d")),
            description=metadata.get("description", f"Rules for {domain}"),
            domain=domain
        )
    
    @staticmethod
    def _parse_metadata_section(content: str) -> Dict[str, str]:
        """Parse the metadata section from markdown content."""
        metadata = {}
        
        # Look for metadata section
        metadata_pattern = r"## Metadata\s*\n(.*?)(?=\n##|\n#|$)"
        metadata_match = re.search(metadata_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if metadata_match:
            metadata_content = metadata_match.group(1)
            
            # Parse key-value pairs
            for line in metadata_content.split('\n'):
                line = line.strip()
                if line.startswith('-') and ':' in line:
                    # Format: - Key: Value
                    key_value = line[1:].strip()  # Remove the dash
                    if ':' in key_value:
                        key, value = key_value.split(':', 1)
                        metadata[key.strip().lower().replace(' ', '_')] = value.strip()
        
        return metadata


@dataclass
class RuleContent:
    """Complete rule content with metadata."""
    
    metadata: RuleMetadata
    content: str
    raw_content: str
    
    def __post_init__(self):
        """Validate rule content after initialization."""
        if not self.content:
            raise ValueError("Rule content cannot be empty")
        if not self.raw_content:
            raise ValueError("Raw content cannot be empty")
    
    @classmethod
    def from_file_content(cls, file_content: str, domain: str) -> "RuleContent":
        """Create RuleContent from file content."""
        metadata = RuleMetadata.from_markdown_content(file_content, domain)
        
        # Extract the main content (everything after metadata section)
        content = cls._extract_main_content(file_content)
        
        return cls(
            metadata=metadata,
            content=content,
            raw_content=file_content
        )
    
    @staticmethod
    def _extract_main_content(content: str) -> str:
        """Extract the main rule content, excluding metadata."""
        # Remove metadata section if present
        metadata_pattern = r"## Metadata\s*\n.*?(?=\n##|\n#|$)"
        content_without_metadata = re.sub(metadata_pattern, "", content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        return content_without_metadata.strip()
    
    def get_formatted_content(self) -> str:
        """Get formatted content for tool responses."""
        return f"""# {self.metadata.domain.title()} Rules

{self.content}

---
*Version: {self.metadata.version} | Last Updated: {self.metadata.last_updated}*"""


@dataclass
class ToolInfo:
    """Information about a dynamically created tool."""
    
    name: str
    description: str
    domain: str
    
    def __post_init__(self):
        """Validate tool info after initialization."""
        if not self.name:
            raise ValueError("Tool name cannot be empty")
        if not self.description:
            raise ValueError("Tool description cannot be empty")
        if not self.domain:
            raise ValueError("Tool domain cannot be empty")
    
    @classmethod
    def from_rule_metadata(cls, metadata: RuleMetadata) -> "ToolInfo":
        """Create ToolInfo from RuleMetadata."""
        return cls(
            name=metadata.domain,
            description=f"Get {metadata.description}",
            domain=metadata.domain
        )