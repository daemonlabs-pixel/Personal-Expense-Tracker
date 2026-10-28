
from database.connection import initialize_database
from ui.cli import run_cli


def main():
    """Initialize the application and start the command-line interface."""
    initialize_database()
    run_cli()


if __name__ == "__main__":
    main()
