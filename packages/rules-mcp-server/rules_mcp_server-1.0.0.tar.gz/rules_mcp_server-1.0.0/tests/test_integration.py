"""
Integration tests for MCP Rules Server
"""

import tempfile
import threading
import time
import unittest
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.config import ServerConfig
from src.file_watcher import FileWatcher
from src.rule_manager import RuleManager
from src.tool_factory import ToolFactory


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ServerConfig(
            rules_directory=self.temp_dir,
            watch_files=True,
            auto_reload=True
        )
        self.mcp_server = FastMCP("test-server")
        self.rule_manager = RuleManager(self.config)
        self.tool_factory = ToolFactory(self.rule_manager, self.mcp_server)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_rule_loading_and_tool_creation(self):
        """Test complete workflow from rule loading to tool creation."""
        # Load rules (should create defaults)
        rules = self.rule_manager.load_rules()
        
        # Verify default rules were created
        self.assertGreater(len(rules), 0)
        self.assertIn("nextjs", rules)
        self.assertIn("security", rules)
        self.assertIn("python", rules)
        
        # Register tools
        self.tool_factory.register_all_tools()
        
        # Verify tools were registered
        registered_tools = self.tool_factory.get_registered_tools()
        self.assertIn("nextjs", registered_tools)
        self.assertIn("security", registered_tools)
        self.assertIn("python", registered_tools)
        self.assertIn("list_domains", registered_tools)
        self.assertIn("get_domain_info", registered_tools)
        
        # Test getting rule content
        nextjs_content = self.rule_manager.get_rule_content("nextjs")
        self.assertIsNotNone(nextjs_content)
        self.assertIn("NextJS Rules", nextjs_content)
    
    def test_file_watching_and_reload(self):
        """Test file watching and automatic reload functionality."""
        # Load initial rules
        self.rule_manager.load_rules()
        initial_domains = self.rule_manager.get_available_domains()
        
        # Set up file watcher with callback
        reload_called = threading.Event()
        
        def reload_callback():
            self.rule_manager.reload_rules()
            self.tool_factory.register_all_tools()
            reload_called.set()
        
        file_watcher = FileWatcher(self.config, reload_callback)
        
        try:
            # Start file watcher
            self.assertTrue(file_watcher.start())
            self.assertTrue(file_watcher.is_running())
            
            # Add a new rule file
            rules_path = Path(self.temp_dir)
            new_rule = rules_path / "test.md"
            
            with open(new_rule, 'w', encoding='utf-8') as f:
                f.write("""# Test Rules

## Metadata
- Version: 1.0
- Description: Test rules for integration testing

## Rules
Test rule content here.""")
            
            # Wait for file watcher to trigger reload
            reload_triggered = reload_called.wait(timeout=5.0)
            self.assertTrue(reload_triggered, "File watcher did not trigger reload")
            
            # Verify new domain was loaded
            new_domains = self.rule_manager.get_available_domains()
            self.assertIn("test", new_domains)
            self.assertEqual(len(new_domains), len(initial_domains) + 1)
            
        finally:
            file_watcher.stop()
    
    def test_concurrent_rule_access(self):
        """Test concurrent access to rule content."""
        # Load rules
        self.rule_manager.load_rules()
        
        # Function to access rules concurrently
        results = []
        errors = []
        
        def access_rules():
            try:
                for _ in range(10):
                    content = self.rule_manager.get_rule_content("nextjs")
                    if content:
                        results.append(len(content))
                    time.sleep(0.01)  # Small delay to increase chance of race conditions
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=access_rules)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")
        self.assertGreater(len(results), 0, "No successful rule accesses")
        
        # All results should be the same (same content length)
        if results:
            expected_length = results[0]
            for result in results:
                self.assertEqual(result, expected_length, "Inconsistent rule content")
    
    def test_error_handling_invalid_rule_file(self):
        """Test error handling with invalid rule files."""
        # First create default rules
        self.rule_manager.load_rules()
        
        # Create an invalid rule file
        rules_path = Path(self.temp_dir)
        invalid_rule = rules_path / "invalid.md"
        
        # Write invalid content (empty file)
        with open(invalid_rule, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Reload rules - should handle invalid file gracefully
        rules = self.rule_manager.load_rules()
        
        # Invalid rule should not be loaded
        self.assertNotIn("invalid", rules)
        
        # But other default rules should still be loaded
        self.assertIn("nextjs", rules)
    
    def test_tool_registration_after_rule_changes(self):
        """Test that tools are properly re-registered after rule changes."""
        # Initial setup
        self.rule_manager.load_rules()
        self.tool_factory.register_all_tools()
        
        initial_tools = self.tool_factory.get_registered_tools()
        initial_count = len([t for t in initial_tools.values() if t.domain != "utility"])
        
        # Add a new rule file
        rules_path = Path(self.temp_dir)
        new_rule = rules_path / "custom.md"
        
        with open(new_rule, 'w', encoding='utf-8') as f:
            f.write("""# Custom Rules

## Metadata
- Version: 1.0
- Description: Custom rules for testing

## Rules
Custom rule content.""")
        
        # Reload and re-register
        self.rule_manager.reload_rules()
        self.tool_factory.register_all_tools()
        
        # Verify new tool was registered
        updated_tools = self.tool_factory.get_registered_tools()
        updated_count = len([t for t in updated_tools.values() if t.domain != "utility"])
        
        self.assertEqual(updated_count, initial_count + 1)
        self.assertIn("custom", updated_tools)
        self.assertEqual(updated_tools["custom"].description, "Get Custom rules for testing")
    
    def test_server_startup_and_shutdown(self):
        """Test server startup and shutdown procedures."""
        # This test verifies the components can be initialized and cleaned up properly
        
        # Initialize all components
        self.rule_manager.load_rules()
        self.tool_factory.register_all_tools()
        
        file_watcher = FileWatcher(self.config, lambda: None)
        
        try:
            # Start file watcher
            started = file_watcher.start()
            self.assertTrue(started)
            self.assertTrue(file_watcher.is_running())
            
            # Verify everything is working
            domains = self.rule_manager.get_available_domains()
            self.assertGreater(len(domains), 0)
            
            tools = self.tool_factory.get_registered_tools()
            self.assertGreater(len(tools), 0)
            
        finally:
            # Clean shutdown
            file_watcher.stop()
            self.assertFalse(file_watcher.is_running())


if __name__ == "__main__":
    unittest.main()