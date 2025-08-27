"""
Rule management for MCP Rules Server
"""

import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

from .config import ServerConfig
from .models import RuleContent, RuleMetadata


logger = logging.getLogger(__name__)


class RuleManager:
    """Manages loading, caching, and accessing rule content."""
    
    def __init__(self, config: ServerConfig):
        """Initialize the rule manager."""
        self.config = config
        self._rules_cache: Dict[str, RuleContent] = {}
        self._lock = threading.RLock()
        self._loaded = False
        
        logger.info(f"Initialized RuleManager with rules directory: {config.rules_directory}")
    
    def load_rules(self) -> Dict[str, RuleContent]:
        """Load all rule files from the rules directory."""
        with self._lock:
            self._rules_cache.clear()
            rules_path = self.config.rules_path
            
            if not rules_path.exists():
                logger.warning(f"Rules directory does not exist: {rules_path}")
                self._create_default_rules()
                # After creating defaults, continue to load them
            
            # Check if directory is empty
            md_files = list(rules_path.glob("*.md"))
            if not md_files:
                logger.info("No rule files found, creating defaults")
                self._create_default_rules()
            
            # Load all .md files in the rules directory
            for rule_file in rules_path.glob("*.md"):
                try:
                    domain = rule_file.stem  # filename without extension
                    content = self._load_rule_file(rule_file, domain)
                    if content:
                        self._rules_cache[domain] = content
                        logger.info(f"Loaded rules for domain: {domain}")
                except Exception as e:
                    logger.error(f"Failed to load rule file {rule_file}: {e}")
            
            self._loaded = True
            logger.info(f"Loaded {len(self._rules_cache)} rule domains")
            return self._rules_cache.copy()
    
    def _load_rule_file(self, file_path: Path, domain: str) -> Optional[RuleContent]:
        """Load a single rule file."""
        try:
            # Check file size
            if file_path.stat().st_size > self.config.max_rule_file_size:
                logger.error(f"Rule file {file_path} exceeds maximum size limit")
                return None
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            if not file_content.strip():
                logger.warning(f"Rule file {file_path} is empty")
                return None
            
            # Create RuleContent from file content
            rule_content = RuleContent.from_file_content(file_content, domain)
            return rule_content
            
        except Exception as e:
            logger.error(f"Error loading rule file {file_path}: {e}")
            return None
    
    def get_rule_content(self, domain: str) -> Optional[str]:
        """Get formatted rule content for a domain."""
        with self._lock:
            if not self._loaded:
                self.load_rules()
            
            rule_content = self._rules_cache.get(domain)
            if rule_content:
                return rule_content.get_formatted_content()
            
            logger.warning(f"No rules found for domain: {domain}")
            return None
    
    def get_available_domains(self) -> List[str]:
        """Get list of available rule domains."""
        with self._lock:
            if not self._loaded:
                self.load_rules()
            
            return sorted(list(self._rules_cache.keys()))
    
    def reload_rules(self) -> None:
        """Reload all rules from disk."""
        logger.info("Reloading rules from disk")
        self.load_rules()
    
    def has_domain(self, domain: str) -> bool:
        """Check if a domain exists."""
        with self._lock:
            if not self._loaded:
                self.load_rules()
            
            return domain in self._rules_cache
    
    def get_rule_metadata(self, domain: str) -> Optional[RuleMetadata]:
        """Get metadata for a specific domain."""
        with self._lock:
            if not self._loaded:
                self.load_rules()
            
            rule_content = self._rules_cache.get(domain)
            return rule_content.metadata if rule_content else None
    
    def _create_default_rules(self) -> None:
        """Create default rule files if rules directory is empty."""
        logger.info("Creating default rule files")
        
        rules_path = self.config.rules_path
        rules_path.mkdir(parents=True, exist_ok=True)
        
        # Default NextJS rules
        nextjs_content = """# NextJS Rules

## Metadata
- Version: 1.0
- Last Updated: 2025-01-26
- Description: NextJS development best practices and guidelines

## Performance Rules

### Image Optimization
- Always use Next.js Image component instead of regular img tags
- Implement proper image sizing and lazy loading
- Use appropriate image formats (WebP, AVIF when supported)

### Code Splitting
- Use dynamic imports for large components
- Implement route-based code splitting
- Lazy load components that are not immediately visible

### Caching
- Implement proper caching strategies for API routes
- Use ISR (Incremental Static Regeneration) for dynamic content
- Configure proper cache headers for static assets

## Security Rules

### Input Validation
- Validate all user inputs on both client and server side
- Use proper sanitization for user-generated content
- Implement CSRF protection for forms

### Authentication
- Use secure authentication methods (NextAuth.js recommended)
- Implement proper session management
- Use HTTPS in production environments

### API Security
- Validate API route inputs
- Implement rate limiting for API endpoints
- Use proper error handling without exposing sensitive information

## Development Best Practices

### File Structure
- Follow Next.js 13+ app directory structure
- Use consistent naming conventions
- Organize components in feature-based folders

### TypeScript
- Use TypeScript for better type safety
- Define proper interfaces for props and API responses
- Enable strict mode in TypeScript configuration

### Testing
- Write unit tests for utility functions
- Implement integration tests for API routes
- Use end-to-end testing for critical user flows"""

        # Default Security rules
        security_content = """# Security Rules

## Metadata
- Version: 1.0
- Last Updated: 2025-01-26
- Description: General security best practices and guidelines

## Input Validation

### User Input
- Never trust user input - validate everything
- Use parameterized queries to prevent SQL injection
- Sanitize all user-generated content before display
- Implement proper input length limits

### File Uploads
- Validate file types and extensions
- Scan uploaded files for malware
- Store uploads outside web root
- Implement file size limits

## Authentication & Authorization

### Password Security
- Enforce strong password policies
- Use secure password hashing (bcrypt, Argon2)
- Implement account lockout after failed attempts
- Use multi-factor authentication when possible

### Session Management
- Use secure session tokens
- Implement proper session timeout
- Regenerate session IDs after login
- Use secure cookie flags (HttpOnly, Secure, SameSite)

## Data Protection

### Sensitive Data
- Never store passwords in plain text
- Encrypt sensitive data at rest
- Use HTTPS for all data transmission
- Implement proper key management

### API Security
- Use API keys and rate limiting
- Implement proper CORS policies
- Validate all API inputs
- Use OAuth 2.0 for third-party integrations

## Infrastructure Security

### Server Configuration
- Keep all software updated
- Disable unnecessary services
- Use firewalls and intrusion detection
- Implement proper logging and monitoring

### Environment Variables
- Never commit secrets to version control
- Use environment variables for configuration
- Rotate API keys and secrets regularly
- Use secret management services in production"""

        # Default Python rules
        python_content = """# Python Rules

## Metadata
- Version: 1.0
- Last Updated: 2025-01-26
- Description: Python development best practices and coding standards

## Code Style

### PEP 8 Compliance
- Use snake_case for variables and functions
- Use PascalCase for classes
- Limit lines to 79 characters
- Use 4 spaces for indentation (no tabs)

### Naming Conventions
- Use descriptive variable names
- Avoid single-letter variables (except for loops)
- Use UPPER_CASE for constants
- Prefix private methods with underscore

## Best Practices

### Error Handling
- Use specific exception types
- Always handle exceptions appropriately
- Use try-except-finally blocks properly
- Log errors with sufficient context

### Function Design
- Keep functions small and focused
- Use type hints for better code documentation
- Return consistent types
- Avoid deep nesting (max 3-4 levels)

### Data Structures
- Use appropriate data structures for the task
- Prefer list comprehensions over loops when readable
- Use sets for membership testing
- Use dictionaries for key-value mappings

## Security Practices

### Input Validation
- Validate all external inputs
- Use parameterized queries for database operations
- Sanitize user data before processing
- Implement proper authentication and authorization

### Dependencies
- Keep dependencies updated
- Use virtual environments
- Pin dependency versions in requirements.txt
- Regularly audit dependencies for vulnerabilities

## Performance

### Optimization
- Profile code before optimizing
- Use generators for large datasets
- Implement caching where appropriate
- Avoid premature optimization

### Memory Management
- Close files and database connections properly
- Use context managers (with statements)
- Be mindful of memory usage with large datasets
- Use appropriate data types for memory efficiency"""

        # Write default rule files
        default_rules = {
            "nextjs.md": nextjs_content,
            "security.md": security_content,
            "python.md": python_content
        }
        
        for filename, content in default_rules.items():
            rule_file = rules_path / filename
            if not rule_file.exists():
                with open(rule_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created default rule file: {filename}")
        
        # Load the newly created rules (but avoid infinite recursion)
        for rule_file in rules_path.glob("*.md"):
            try:
                domain = rule_file.stem
                content = self._load_rule_file(rule_file, domain)
                if content:
                    self._rules_cache[domain] = content
                    logger.info(f"Loaded default rules for domain: {domain}")
            except Exception as e:
                logger.error(f"Failed to load default rule file {rule_file}: {e}")