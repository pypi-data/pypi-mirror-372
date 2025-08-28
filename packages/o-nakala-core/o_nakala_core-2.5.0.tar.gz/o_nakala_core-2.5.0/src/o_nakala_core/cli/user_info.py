#!/usr/bin/env python3
"""
CLI interface for NAKALA user info functionality.
This module provides the command-line interface for the user info functionality.
"""


def main() -> None:
    """Main entry point for o-nakala-user-info CLI command."""
    # Import and execute the user_info module main function
    from o_nakala_core.user_info import main as user_info_main

    user_info_main()


if __name__ == "__main__":
    main()
