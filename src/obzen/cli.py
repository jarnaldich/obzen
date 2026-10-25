import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

app = typer.Typer(
    name="obzen",
    help="CLI tool for managing your personal Obsidian vault",
    add_completion=False,
)

console = Console()


@app.command()
def init(
    vault_path: Path = typer.Option(
        ..., "--vault", "-v", help="Path to your Obsidian vault"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """Initialize obzen configuration for a vault."""
    console.print(f"[green]Initializing obzen for vault:[/green] {vault_path}")
    # TODO: Save config
    console.print("[green]Done![/green]")


@app.command()
def list(
    vault_path: Optional[Path] = typer.Option(
        None, "--vault", "-v", help="Path to your Obsidian vault"
    ),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags"),
):
    """List notes in the vault."""
    console.print(Panel.fit("Listing notes...", style="cyan"))
    # TODO: Implement with obsidiantools
    table = Table(title="Notes")
    table.add_column("Name", style="cyan")
    table.add_column("Tags", style="magenta")
    console.print(table)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    vault_path: Optional[Path] = typer.Option(
        None, "--vault", "-v", help="Path to your Obsidian vault"
    ),
):
    """Search notes in the vault."""
    console.print(f"[yellow]Searching for:[/yellow] {query}")
    # TODO: Implement search


@app.command()
def stats(
    vault_path: Optional[Path] = typer.Option(
        None, "--vault", "-v", help="Path to your Obsidian vault"
    ),
):
    """Show vault statistics."""
    console.print(Panel.fit("Vault Statistics", style="green"))
    # TODO: Implement stats


if __name__ == "__main__":
    app()
