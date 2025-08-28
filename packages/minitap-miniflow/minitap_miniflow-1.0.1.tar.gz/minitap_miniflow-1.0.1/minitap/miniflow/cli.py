import click
from rich.console import Console

from minitap.miniflow.auth import handle_login, handle_logout, get_user_status
from minitap.miniflow.execution import run_flow_by_id

console = Console()


@click.group()
def cli():
    """A CLI to run miniflows locally."""
    pass


@cli.command()
def login():
    """Authenticate with your miniflow account."""
    handle_login()


@cli.command()
def logout():
    """Log out from your miniflow account."""
    handle_logout()


@cli.command()
def whoami():
    """Check the current authenticated user."""
    get_user_status()


@cli.command()
@click.argument("flow_id")
def run(flow_id: str):
    """Execute a flow by its ID."""
    console.print(f"-> Attempting to run flow: [cyan]{flow_id}[/cyan]")
    run_flow_by_id(flow_id)


if __name__ == "__main__":
    cli()
