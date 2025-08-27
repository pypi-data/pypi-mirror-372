"""
Tests for data models
"""

import unittest
from datetime import datetime

from src.models import RuleMetadata, RuleContent, ToolInfo


class TestRuleMetadata(unittest.TestCase):
    """Test cases for RuleMetadata class."""
    
    def test_valid_metadata_creation(self):
        """Test creating valid metadata."""
        metadata = RuleMetadata(
            version="1.0",
            last_updated="2025-01-26",
            description="Test rules",
            domain="test"
        )
        
        self.assertEqual(metadata.version, "1.0")
        self.assertEqual(metadata.last_updated, "2025-01-26")
        self.assertEqual(metadata.description, "Test rules")
        self.assertEqual(metadata.domain, "test")
    
    def test_empty_version_validation(self):
        """Test validation with empty version."""
        with self.assertRaises(ValueError) as context:
            RuleMetadata(
                version="",
                last_updated="2025-01-26",
                description="Test rules",
                domain="test"
            )
        
        self.assertIn("Version cannot be empty", str(context.exception))
    
    def test_empty_domain_validation(self):
        """Test validation with empty domain."""
        with self.assertRaises(ValueError) as context:
            RuleMetadata(
                version="1.0",
                last_updated="2025-01-26",
                description="Test rules",
                domain=""
            )
        
        self.assertIn("Domain cannot be empty", str(context.exception))
    
    def test_from_markdown_content_with_metadata(self):
        """Test parsing metadata from markdown with metadata section."""
        content = """# Test Rules

## Metadata
- Version: 2.0
- Last Updated: 2025-01-26
- Description: Advanced test rules

## Rules
Some rule content here."""
        
        metadata = RuleMetadata.from_markdown_content(content, "test")
        
        self.assertEqual(metadata.version, "2.0")
        self.assertEqual(metadata.last_updated, "2025-01-26")
        self.assertEqual(metadata.description, "Advanced test rules")
        self.assertEqual(metadata.domain, "test")
    
    def test_from_markdown_content_without_metadata(self):
        """Test parsing metadata from markdown without metadata section."""
        content = """# Test Rules

## Rules
Some rule content here."""
        
        metadata = RuleMetadata.from_markdown_content(content, "test")
        
        self.assertEqual(metadata.version, "1.0")  # Default
        self.assertEqual(metadata.description, "Rules for test")  # Default
        self.assertEqual(metadata.domain, "test")
        # last_updated should be today's date
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(metadata.last_updated, today)
    
    def test_parse_metadata_section(self):
        """Test parsing metadata section with various formats."""
        content = """## Metadata
- Version: 1.5
- Last Updated: 2025-01-25
- Description: Complex rules with special characters!
- Custom Field: Custom Value

## Other Section"""
        
        metadata = RuleMetadata._parse_metadata_section(content)
        
        self.assertEqual(metadata["version"], "1.5")
        self.assertEqual(metadata["last_updated"], "2025-01-25")
        self.assertEqual(metadata["description"], "Complex rules with special characters!")
        self.assertEqual(metadata["custom_field"], "Custom Value")


class TestRuleContent(unittest.TestCase):
    """Test cases for RuleContent class."""
    
    def test_valid_rule_content_creation(self):
        """Test creating valid rule content."""
        metadata = RuleMetadata(
            version="1.0",
            last_updated="2025-01-26",
            description="Test rules",
            domain="test"
        )
        
        rule_content = RuleContent(
            metadata=metadata,
            content="Rule content here",
            raw_content="# Test\nRule content here"
        )
        
        self.assertEqual(rule_content.metadata, metadata)
        self.assertEqual(rule_content.content, "Rule content here")
        self.assertEqual(rule_content.raw_content, "# Test\nRule content here")
    
    def test_empty_content_validation(self):
        """Test validation with empty content."""
        metadata = RuleMetadata(
            version="1.0",
            last_updated="2025-01-26",
            description="Test rules",
            domain="test"
        )
        
        with self.assertRaises(ValueError) as context:
            RuleContent(
                metadata=metadata,
                content="",
                raw_content="# Test"
            )
        
        self.assertIn("Rule content cannot be empty", str(context.exception))
    
    def test_from_file_content(self):
        """Test creating RuleContent from file content."""
        file_content = """# NextJS Rules

## Metadata
- Version: 1.2
- Last Updated: 2025-01-26
- Description: NextJS best practices

## Rules

### Performance
- Use Next.js Image component
- Implement proper caching

### Security
- Validate all inputs
- Use HTTPS in production"""
        
        rule_content = RuleContent.from_file_content(file_content, "nextjs")
        
        self.assertEqual(rule_content.metadata.version, "1.2")
        self.assertEqual(rule_content.metadata.domain, "nextjs")
        self.assertEqual(rule_content.metadata.description, "NextJS best practices")
        self.assertIn("Performance", rule_content.content)
        self.assertIn("Security", rule_content.content)
        self.assertNotIn("## Metadata", rule_content.content)  # Should be removed
    
    def test_extract_main_content(self):
        """Test extracting main content without metadata."""
        content = """# Test Rules

## Metadata
- Version: 1.0
- Description: Test

## Rules
Main content here

### Subsection
More content"""
        
        main_content = RuleContent._extract_main_content(content)
        
        self.assertNotIn("## Metadata", main_content)
        self.assertNotIn("Version: 1.0", main_content)
        self.assertIn("Main content here", main_content)
        self.assertIn("### Subsection", main_content)
    
    def test_get_formatted_content(self):
        """Test getting formatted content for tool responses."""
        metadata = RuleMetadata(
            version="1.0",
            last_updated="2025-01-26",
            description="Test rules",
            domain="test"
        )
        
        rule_content = RuleContent(
            metadata=metadata,
            content="Rule content here",
            raw_content="# Test\nRule content here"
        )
        
        formatted = rule_content.get_formatted_content()
        
        self.assertIn("# Test Rules", formatted)
        self.assertIn("Rule content here", formatted)
        self.assertIn("Version: 1.0", formatted)
        self.assertIn("Last Updated: 2025-01-26", formatted)


class TestToolInfo(unittest.TestCase):
    """Test cases for ToolInfo class."""
    
    def test_valid_tool_info_creation(self):
        """Test creating valid tool info."""
        tool_info = ToolInfo(
            name="nextjs",
            description="Get NextJS rules",
            domain="nextjs"
        )
        
        self.assertEqual(tool_info.name, "nextjs")
        self.assertEqual(tool_info.description, "Get NextJS rules")
        self.assertEqual(tool_info.domain, "nextjs")
    
    def test_empty_name_validation(self):
        """Test validation with empty name."""
        with self.assertRaises(ValueError) as context:
            ToolInfo(
                name="",
                description="Get rules",
                domain="test"
            )
        
        self.assertIn("Tool name cannot be empty", str(context.exception))
    
    def test_from_rule_metadata(self):
        """Test creating ToolInfo from RuleMetadata."""
        metadata = RuleMetadata(
            version="1.0",
            last_updated="2025-01-26",
            description="NextJS best practices",
            domain="nextjs"
        )
        
        tool_info = ToolInfo.from_rule_metadata(metadata)
        
        self.assertEqual(tool_info.name, "nextjs")
        self.assertEqual(tool_info.description, "Get NextJS best practices")
        self.assertEqual(tool_info.domain, "nextjs")


if __name__ == "__main__":
    unittest.main()