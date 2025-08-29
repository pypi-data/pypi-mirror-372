"""Command-line interface for CRISP package."""

import sys
import argparse
from CRISP._version import __version__
from CRISP.tests.runner import run_tests

def main():
    """Main entry point for the CRISP command-line tool."""
    parser = argparse.ArgumentParser(description="CRISP: Concurrent Remote Interactive Simulation Program")
    parser.add_argument('--version', action='version', version=f'CRISP {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='CRISP commands')
    
    # Add test subcommand
    test_parser = subparsers.add_parser('test', help='Run CRISP test suite')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'test':
        sys.exit(run_tests())
    elif not args.command:
        parser.print_help()
        return 0
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
