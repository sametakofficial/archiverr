"""CLI Entry Point - Deprecated"""
from archiverr.__main__ import main

def run_cli():
    """Backward compatibility wrapper"""
    main()

if __name__ == "__main__":
    run_cli()
