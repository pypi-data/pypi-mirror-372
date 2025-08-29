"""
Simple logging system for LeVibes
"""

import sys
from typing import Optional

class Logger:
    """Simple console logger without emojis or excessive styling"""
    
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
    
    def info(self, message: str, prefix: Optional[str] = None) -> None:
        """Log info message"""
        if not self.quiet:
            output = f"[{prefix}] {message}" if prefix else message
            print(output)
    
    def success(self, message: str, prefix: Optional[str] = None) -> None:
        """Log success message"""
        if not self.quiet:
            output = f"[{prefix}] {message}" if prefix else message
            print(f"✓ {output}")
    
    def warning(self, message: str, prefix: Optional[str] = None) -> None:
        """Log warning message"""
        output = f"[{prefix}] {message}" if prefix else message
        print(f"Warning: {output}")
    
    def error(self, message: str, prefix: Optional[str] = None) -> None:
        """Log error message"""
        output = f"[{prefix}] {message}" if prefix else message
        print(f"Error: {output}", file=sys.stderr)
    
    def progress(self, message: str) -> None:
        """Log progress message"""
        if not self.quiet:
            print(f"→ {message}")

# Global logger instance
logger = Logger()

def set_quiet(quiet: bool) -> None:
    """Set quiet mode"""
    global logger
    logger.quiet = quiet 