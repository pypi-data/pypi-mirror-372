#!/usr/bin/env python3
"""
Configure logging levels for CLI Arena to reduce verbosity.
Run this before evaluations to set appropriate logging levels.
"""

import logging
import os
import sys

def configure_logging(verbose=False):
    """
    Configure logging to reduce verbosity while keeping essential information.
    
    Args:
        verbose: If True, show detailed logs. If False, show condensed logs.
    """
    
    # Set the root logger level
    root_level = logging.DEBUG if verbose else logging.WARNING
    logging.getLogger().setLevel(root_level)
    
    # Configure specific loggers
    loggers_config = {
        # Keep harness at INFO level for essential progress updates
        'cli_arena.harness': logging.INFO,
        
        # Reduce agent verbosity unless in verbose mode
        'cli_arena.agents.claude_code': logging.WARNING if not verbose else logging.INFO,
        'cli_arena.agents.gemini_cli': logging.WARNING if not verbose else logging.INFO,
        'cli_arena.agents.aider': logging.WARNING if not verbose else logging.INFO,
        'cli_arena.agents.openai_codex': logging.WARNING,  # Already condensed
        
        # Reduce Docker and recording noise
        'cli_arena.recording': logging.WARNING,
        'docker': logging.WARNING,
        
        # Keep evaluation metrics at INFO
        'cli_arena.evaluation': logging.INFO,
    }
    
    for logger_name, level in loggers_config.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Configure output format - more condensed
    if not verbose:
        # Condensed format without logger name and level
        formatter = logging.Formatter('%(message)s')
    else:
        # Standard format with timestamp
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Apply formatter to all handlers
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)
    
    print(f"✅ Logging configured: {'VERBOSE' if verbose else 'CONDENSED'} mode")

def setup_condensed_logging():
    """Quick setup for condensed logging."""
    configure_logging(verbose=False)

def setup_verbose_logging():
    """Quick setup for verbose logging."""
    configure_logging(verbose=True)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['--verbose', '-v']:
        setup_verbose_logging()
    else:
        setup_condensed_logging()
    
    # Set environment variable for child processes
    os.environ['ARENA_LOG_LEVEL'] = 'CONDENSED' if len(sys.argv) <= 1 else 'VERBOSE'