import typer
import os
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from dotenv import load_dotenv

from obsidiantools.api import Vault

app = typer.Typer(
    name="obzen",
    help="CLI tool for managing your personal Obsidian vault",
    add_completion=False,
)

console = Console()

load_dotenv()

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
def import_tasks(
    vault_path: Optional[Path] = typer.Option(
        os.getenv("VAULT_PATH"), "--vault", "-v", help="Path to your Obsidian vault"
    ),
    csv_path: Optional[Path] = typer.Option(
        os.getenv("CSV_PATH"), "--csv", "-c", help="Path to your CSV tasks"
    ),
):
    """Import tasks from the vault."""
    if vault_path is None:
        console.print("[red]Error:[/red] No vault path provided")
        raise typer.Exit(code=1)

    if not os.path.exists(vault_path):
        console.print(f"[red]Error:[/red] Vault path does not exist: {vault_path}")
        raise typer.Exit(code=1)

    vault_path = Path(vault_path)
    console.print(Panel.fit(f"Importing tasks from {vault_path}...", style="cyan"))
    if csv_path is None:
        console.print("[red]Error:[/red] No CSV path provided")
        raise typer.Exit(code=1)

    if not os.path.exists(csv_path):
        console.print(f"[red]Error:[/red] CSV path does not exist: {csv_path}")
        raise typer.Exit(code=1)

    csv_path = Path(csv_path)

    # TODO: Implement task import
    console.print("[green]Done![/green]")


@app.command()
def list(
    vault_path: Optional[Path] = typer.Option(
        os.getenv("VAULT_PATH"), "--vault", "-v", help="Path to your Obsidian vault"
    ),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags"),
):
    """List notes in the vault."""
    if vault_path is None:
        console.print("[red]Error:[/red] No vault path provided")
        raise typer.Exit(code=1)
    
    if not os.path.exists(vault_path):
        console.print(f"[red]Error:[/red] Vault path does not exist: {vault_path}")
        raise typer.Exit(code=1)

    vault_path = Path(vault_path)
    console.print(Panel.fit(f"Listing notes from {vault_path}...", style="cyan"))

    vault = Vault(vault_path).connect()

    table = Table(title="Notes")
    table.add_column("Name", style="cyan")
    table.add_column("Tags", style="magenta")

    tag_filter = None
    if tags:
        tag_filter = [t.strip() for t in tags.split(",")]

    for note in sorted(vault.md_file_index.keys()):
        note_tags = vault.tags_index.get(note, [])
        if tag_filter:
            # Check if any of the filter tags are in note tags
            if not any(f in note_tags for f in tag_filter):
                continue
        table.add_row(note, ", ".join(note_tags) if note_tags else "")

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
