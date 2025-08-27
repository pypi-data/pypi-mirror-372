"""
Configuration management for MCP Rules Server
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ServerConfig:
    """Configuration settings for the MCP Rules Server."""
    
    rules_directory: str = "rules"
    server_name: str = "mcp-rules-server"
    server_version: str = "1.0.0"
    watch_files: bool = True
    auto_reload: bool = True
    log_level: str = "INFO"
    max_rule_file_size: int = 1024 * 1024  # 1MB max per rule file
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Ensure rules directory exists
        rules_path = Path(self.rules_directory)
        if not rules_path.exists():
            rules_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_environment(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        return cls(
            rules_directory=os.getenv("RULES_DIRECTORY", "rules"),
            server_name=os.getenv("SERVER_NAME", "mcp-rules-server"),
            server_version=os.getenv("SERVER_VERSION", "1.0.0"),
            watch_files=os.getenv("WATCH_FILES", "true").lower() == "true",
            auto_reload=os.getenv("AUTO_RELOAD", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_rule_file_size=int(os.getenv("MAX_RULE_FILE_SIZE", "1048576")),
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.server_name:
            raise ValueError("Server name cannot be empty")
        
        if not self.server_version:
            raise ValueError("Server version cannot be empty")
        
        if self.max_rule_file_size <= 0:
            raise ValueError("Max rule file size must be positive")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}")
    
    @property
    def rules_path(self) -> Path:
        """Get the rules directory as a Path object."""
        return Path(self.rules_directory)