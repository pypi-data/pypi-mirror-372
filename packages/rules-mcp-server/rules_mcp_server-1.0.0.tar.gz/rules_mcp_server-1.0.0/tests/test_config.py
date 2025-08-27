"""
Tests for configuration management
"""

import os
import tempfile
import unittest
from pathlib import Path

from src.config import ServerConfig


class TestServerConfig(unittest.TestCase):
    """Test cases for ServerConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ServerConfig()
        
        self.assertEqual(config.server_name, "mcp-rules-server")
        self.assertEqual(config.server_version, "1.0.0")
        self.assertEqual(config.rules_directory, "rules")
        self.assertTrue(config.watch_files)
        self.assertTrue(config.auto_reload)
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.max_rule_file_size, 1024 * 1024)
    
    def test_from_environment(self):
        """Test configuration from environment variables."""
        # Set environment variables
        env_vars = {
            "RULES_DIRECTORY": "/custom/rules",
            "SERVER_NAME": "custom-server",
            "SERVER_VERSION": "2.0.0",
            "WATCH_FILES": "false",
            "AUTO_RELOAD": "false",
            "LOG_LEVEL": "DEBUG",
            "MAX_RULE_FILE_SIZE": "2097152",
        }
        
        # Temporarily set environment variables
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            config = ServerConfig.from_environment()
            
            self.assertEqual(config.rules_directory, "/custom/rules")
            self.assertEqual(config.server_name, "custom-server")
            self.assertEqual(config.server_version, "2.0.0")
            self.assertFalse(config.watch_files)
            self.assertFalse(config.auto_reload)
            self.assertEqual(config.log_level, "DEBUG")
            self.assertEqual(config.max_rule_file_size, 2097152)
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    def test_validation_success(self):
        """Test successful configuration validation."""
        config = ServerConfig()
        # Should not raise any exception
        config.validate()
    
    def test_validation_empty_server_name(self):
        """Test validation with empty server name."""
        config = ServerConfig(server_name="")
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("Server name cannot be empty", str(context.exception))
    
    def test_validation_empty_server_version(self):
        """Test validation with empty server version."""
        config = ServerConfig(server_version="")
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("Server version cannot be empty", str(context.exception))
    
    def test_validation_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = ServerConfig(log_level="INVALID")
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("Invalid log level", str(context.exception))
    
    def test_validation_negative_file_size(self):
        """Test validation with negative max file size."""
        config = ServerConfig(max_rule_file_size=-1)
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("Max rule file size must be positive", str(context.exception))
    
    def test_rules_path_property(self):
        """Test rules_path property returns correct Path object."""
        config = ServerConfig(rules_directory="custom/rules")
        
        self.assertIsInstance(config.rules_path, Path)
        self.assertEqual(config.rules_path, Path("custom/rules"))


if __name__ == "__main__":
    unittest.main()