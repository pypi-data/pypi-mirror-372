"""
Tests for rule manager
"""

import tempfile
import unittest
from pathlib import Path

from src.config import ServerConfig
from src.rule_manager import RuleManager


class TestRuleManager(unittest.TestCase):
    """Test cases for RuleManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ServerConfig(
            rules_directory=self.temp_dir,
            max_rule_file_size=1024 * 1024
        )
        self.rule_manager = RuleManager(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_rules_empty_directory(self):
        """Test loading rules from empty directory creates defaults."""
        rules = self.rule_manager.load_rules()
        
        # Should create default rules
        self.assertGreater(len(rules), 0)
        self.assertIn("nextjs", rules)
        self.assertIn("security", rules)
        self.assertIn("python", rules)
    
    def test_load_rules_with_custom_file(self):
        """Test loading custom rule file."""
        # Create a custom rule file
        rules_path = Path(self.temp_dir)
        custom_rule = rules_path / "custom.md"
        
        custom_content = """# Custom Rules

## Metadata
- Version: 2.0
- Last Updated: 2025-01-26
- Description: Custom test rules

## Rules
Custom rule content here."""
        
        with open(custom_rule, 'w', encoding='utf-8') as f:
            f.write(custom_content)
        
        rules = self.rule_manager.load_rules()
        
        self.assertIn("custom", rules)
        self.assertEqual(rules["custom"].metadata.version, "2.0")
        self.assertEqual(rules["custom"].metadata.description, "Custom test rules")
    
    def test_get_rule_content(self):
        """Test getting rule content for a domain."""
        # Load default rules first
        self.rule_manager.load_rules()
        
        content = self.rule_manager.get_rule_content("nextjs")
        
        self.assertIsNotNone(content)
        self.assertIn("NextJS Rules", content)
        self.assertIn("Version:", content)
    
    def test_get_rule_content_nonexistent(self):
        """Test getting rule content for non-existent domain."""
        self.rule_manager.load_rules()
        
        content = self.rule_manager.get_rule_content("nonexistent")
        
        self.assertIsNone(content)
    
    def test_get_available_domains(self):
        """Test getting list of available domains."""
        self.rule_manager.load_rules()
        
        domains = self.rule_manager.get_available_domains()
        
        self.assertIsInstance(domains, list)
        self.assertIn("nextjs", domains)
        self.assertIn("security", domains)
        self.assertIn("python", domains)
        # Should be sorted
        self.assertEqual(domains, sorted(domains))
    
    def test_has_domain(self):
        """Test checking if domain exists."""
        self.rule_manager.load_rules()
        
        self.assertTrue(self.rule_manager.has_domain("nextjs"))
        self.assertFalse(self.rule_manager.has_domain("nonexistent"))
    
    def test_get_rule_metadata(self):
        """Test getting metadata for a domain."""
        self.rule_manager.load_rules()
        
        metadata = self.rule_manager.get_rule_metadata("nextjs")
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.domain, "nextjs")
        self.assertEqual(metadata.version, "1.0")
    
    def test_reload_rules(self):
        """Test reloading rules."""
        # Load initial rules
        self.rule_manager.load_rules()
        initial_count = len(self.rule_manager.get_available_domains())
        
        # Add a new rule file
        rules_path = Path(self.temp_dir)
        new_rule = rules_path / "new.md"
        
        with open(new_rule, 'w', encoding='utf-8') as f:
            f.write("# New Rules\n\n## Rules\nNew content")
        
        # Reload rules
        self.rule_manager.reload_rules()
        
        # Should have one more domain
        new_count = len(self.rule_manager.get_available_domains())
        self.assertEqual(new_count, initial_count + 1)
        self.assertTrue(self.rule_manager.has_domain("new"))
    
    def test_file_size_limit(self):
        """Test file size limit enforcement."""
        # Create config with very small file size limit
        small_config = ServerConfig(
            rules_directory=self.temp_dir,
            max_rule_file_size=10  # 10 bytes
        )
        rule_manager = RuleManager(small_config)
        
        # Create a large rule file
        rules_path = Path(self.temp_dir)
        large_rule = rules_path / "large.md"
        
        large_content = "# Large Rules\n" + "x" * 1000  # Much larger than 10 bytes
        
        with open(large_rule, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        rules = rule_manager.load_rules()
        
        # Large file should not be loaded
        self.assertNotIn("large", rules)


if __name__ == "__main__":
    unittest.main()