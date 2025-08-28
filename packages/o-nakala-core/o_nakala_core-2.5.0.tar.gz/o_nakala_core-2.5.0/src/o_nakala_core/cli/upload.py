#!/usr/bin/env python3
"""
CLI interface for NAKALA upload functionality.
This module provides the command-line interface for the upload functionality.
"""


def main() -> None:
    """Main entry point for o-nakala-upload CLI command."""
    # Import and execute the upload module main function
    from o_nakala_core.upload import main as upload_main

    upload_main()


if __name__ == "__main__":
    main()
