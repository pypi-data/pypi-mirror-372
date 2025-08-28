#!/usr/bin/env python3
"""
CLI interface for NAKALA curator functionality.
This module provides the command-line interface for the curator functionality.
"""


def main() -> None:
    """Main entry point for o-nakala-curator CLI command."""
    # Import and execute the curator module main function
    from o_nakala_core.curator import main as curator_main

    curator_main()


if __name__ == "__main__":
    main()
