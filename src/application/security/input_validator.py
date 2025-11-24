"""Input validation service for user requests."""

from typing import Any
import re


class InputValidator:
    """
    Validates and sanitizes user input for security and safety.
    """
    
    def __init__(self, max_length: int = 5000):
        """
        Initialize input validator.
        
        Args:
            max_length: Maximum allowed input length
        """
        self.max_length = max_length
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup validation patterns."""
        # Patterns for potentially dangerous content
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'on\w+\s*=',  # Event handlers
        ]
    
    def validate(self, input_text: str) -> str:
        """
        Validate and sanitize input text.
        
        Args:
            input_text: Raw user input
            
        Returns:
            Validated and sanitized input
            
        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(input_text, str):
            raise ValueError("Input must be a string")
        
        if len(input_text) > self.max_length:
            raise ValueError(f"Input exceeds maximum length of {self.max_length} characters")
        
        if not input_text.strip():
            raise ValueError("Input cannot be empty")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, input_text, re.IGNORECASE | re.DOTALL):
                raise ValueError("Input contains potentially unsafe content")
        
        # Basic sanitization - remove null bytes
        sanitized = input_text.replace('\x00', '')
        
        return sanitized.strip()
