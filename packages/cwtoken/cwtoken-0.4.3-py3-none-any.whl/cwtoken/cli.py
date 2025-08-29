import click
from .utils import test_connection
from .gui import main as run_gui  # assuming relative import

@click.group()
def cli():
    """cwtoken command-line interface."""
    pass

@cli.command()
def test():
    """Test the API connection"""
    test_connection()

@cli.command()
def gui():
    """Launch the GUI app"""
    run_gui()

if __name__ == "__main__":
    cli()
