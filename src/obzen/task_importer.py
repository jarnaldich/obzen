"""Load task CSV exports into a single dataframe."""

from pathlib import Path

import os
import sqlite3
import pandas as pd
from rich.console import Console
from rich.table import Table
from obsidiantools.api import Vault

console = Console()


class TaskImporter:
    """Read all CSV files in a directory into one concatenated dataframe.

    Every CSV in ``csv_dir`` is expected to share the same structure, so the
    files are stacked rowwise. The resulting dataframe is available through
    the ``dataframe`` (and ``df``) attributes.
    """

    def __init__(self, csv_dir: str | Path, vault_dir: Path) -> None:
        self.db_path = os.getenv("DB_PATH", "tasks.db")
        self.conn = sqlite3.connect(self.db_path)
        self.csv_dir = Path(csv_dir)
        self.vault_dir = Path(vault_dir)
        self.vault = Vault(self.vault_dir).connect()
        self.dataframe = self.load_csvs()
        self._remove_dups()
        self._remove_in_sqlite()
        self._remove_in_vault()  # Assuming this is a method to remove tasks already in the vault
        self._show_summary()
        # Printem l'esquema del dataframe
        console.print(self.dataframe.info())
        #self._save_sqlite()

    def _remove_in_vault(self) -> None:
        """
        Remove rows from the dataframe whose titles already exist in the vault
        directory.
        """
        before = len(self.dataframe)

        notes = {
            k: v 
            for k, v in self.vault.md_file_index.items() 
            if "TaskNotes/Tasks" in str(v)
        }

        print(notes)

        # Remove rows from the dataframe whose titles match any note in the TaskNotes directory
        self.dataframe = self.dataframe[~self.dataframe["Títol"].isin(notes.keys())]

        after = len(self.dataframe)
        console.print(f"[green]Removed {before - after} row(s) already in the vault[/green]")

    def _remove_in_sqlite(self) -> None:
        """
        Remove rows from the dataframe whose titles already exist in the SQLite database.
        """
        query = "SELECT * FROM tasks"
        try:
            existing_df = pd.read_sql(query, self.conn)
            before = len(self.dataframe)
            # Merge by Títol to find duplicates in the SQLite database
            self.dataframe = self.dataframe.merge(existing_df, on="Títol", how="left", indicator=True)
            self.dataframe = self.dataframe[self.dataframe["_merge"] == "left_only"]
            self.dataframe.drop(columns=["_merge"], inplace=True)
            after = len(self.dataframe)
            console.print(f"[green]Removed {before - after} row(s) already in SQLite database[/green]")
        except Exception:
            console.print("[yellow]No existing SQLite database or table found, skipping removal[/yellow]")

    def _save_sqlite(self) -> None:
        """
        Save the dataframe to a SQLite database in the vault directory.
        append to the existing table if it already exists.
        """

        self.dataframe.to_sql("tasks", self.conn, if_exists="append", index=False)
        console.print(f"[green]Saved tasks to SQLite database at {self.db_path}[/green]")

    def _remove_dups(self) -> None:
        """
        Searches for rows with the same field 'Títol' and removes them as duplicates.
        """
        before = len(self.dataframe)
        self.dataframe.drop_duplicates(subset=["Títol"], inplace=True)
        after = len(self.dataframe)
        console.print(f"[green]Removed {before - after} duplicate row(s)[/green]")

    def load_csvs(self) -> pd.DataFrame:
        """Load and concatenate every ``*.csv`` file in ``csv_dir``."""
        if not self.csv_dir.is_dir():
            raise NotADirectoryError(
                f"CSV directory does not exist or is not a directory: {self.csv_dir}"
            )

        csv_files = sorted(self.csv_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in: {self.csv_dir}")

        frames: list[pd.DataFrame] = []
        loaded_files: list[Path] = []
        for csv_file in csv_files:
            console.print(f"[cyan]Loading CSV:[/cyan] {csv_file.name}")
            try:
                # The separator is ;, has a header, and everything is quoted
                frames.append(pd.read_csv(csv_file, sep=";", header=0, quotechar='"'))
            except pd.errors.EmptyDataError:
                console.print(f"[yellow]Skipping empty CSV:[/yellow] {csv_file.name}")
                continue
            loaded_files.append(csv_file)

        if not frames:
            raise ValueError(f"All CSV files in {self.csv_dir} are empty")

        for frame, csv_file in zip(frames, loaded_files):
            frame["source_file"] = csv_file.name

        dataframe = pd.concat(frames, ignore_index=True)

        # Add a new column "state" with default value "new"
        dataframe["state"] = "new"

        # Keep the files that contributed rows for the summary.
        self.loaded_files = loaded_files
        return dataframe

    def _show_summary(self) -> None:
        """Print a short summary and preview so the load is visible."""
        rows, columns = self.dataframe.shape
        console.print(
            f"[green]Loaded {len(self.loaded_files)} CSV file(s) from[/green] "
            f"{self.csv_dir} [green]into a dataframe with[/green] "
            f"{rows} row(s) x {columns} column(s)"
        )

        preview = Table(title="Task CSV preview", show_lines=False)
        for column in self.dataframe.columns:
            preview.add_column(str(column), overflow="fold")
        for _, row in self.dataframe.head(5).iterrows():
            preview.add_row(*(str(value) for value in row))
        console.print(preview)
