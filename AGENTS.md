# AGENTS.md

`obzen` is a Python 3.11+ Typer/Rich CLI for querying Obsidian vaults through
`obsidiantools`. It is a single `src`-layout package; there are no tests, lint,
typecheck, or CI configs yet.

## Commands

`uv` is not on this shell's `PATH` (it lives at `~/.local/bin/uv`); use the full
path or add `$HOME/.local/bin` to `PATH`.

```sh
~/.local/bin/uv sync --locked          # sync from the committed uv.lock
~/.local/bin/uv run obzen --help       # run the console script
.venv/bin/obzen --help                 # equivalent, using the existing venv
.venv/bin/obzen list -v /path/to/vault --tags foo,bar
```

- Change dependencies with `uv add` / `uv lock`; do not hand-edit `uv.lock`.
- Do not run `python -m obzen.cli`: `obzen/__init__.py` imports `cli`, so runpy
  warns that `obzen.cli` is already in `sys.modules`. Use the `obzen` script.

## Layout and entrypoints

- `pyproject.toml` exposes `obzen = "obzen:main"`;
  `src/obzen/__init__.py:main` delegates to `cli.app`.
- All commands are `@app.command()` functions in `src/obzen/cli.py`. Add new
  commands there and print through the module-level Rich `console`.
- Vault data comes from `obsidiantools.api.Vault(path).connect()`. Indexes such
  as `md_file_index` and `tags_index` are only populated after `connect()`;
  `tags_index` maps filename to a `list[str]` (`[]` when untagged).

## Current behavior

- Every command takes `-v/--vault`; there is no persisted vault config yet.
  `init`, `search`, and `stats` are stubs/TODOs. `list` requires an explicit
  vault path and exits with code 1 when it is omitted.
- No test suite exists. If you add tests, also add pytest as a dev dependency
  and configure it; don't assume `uv run pytest` already works.
