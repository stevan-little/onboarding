#!/usr/bin/env python3
"""Print the source of Jupyter / Databricks notebooks as plain text.

Prints markdown and code cells only. Cell OUTPUTS are never printed, because in
this company's notebooks they can contain real client data.

Usage:
    tools/nbcode.py NOTEBOOK.ipynb [...]          # all cells
    tools/nbcode.py --code NOTEBOOK.ipynb         # code cells only
    tools/nbcode.py --outline NOTEBOOK.ipynb      # markdown headings + first line of each code cell

Standard library only. Read-only.
"""

import argparse
import json
import sys
from pathlib import Path


def cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def print_notebook(path: Path, code_only: bool, outline: bool) -> None:
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"!! {path}: cannot read as a notebook ({error})", file=sys.stderr)
        return
    cells = notebook.get("cells", [])
    print(f"######## {path}  ({len(cells)} cells)")
    for number, cell in enumerate(cells, start=1):
        kind = cell.get("cell_type", "?")
        text = cell_source(cell).rstrip()
        if not text or (code_only and kind != "code"):
            continue
        if outline:
            if kind == "markdown":
                for line in text.splitlines():
                    if line.lstrip().startswith("#"):
                        print(f"[{number:>3}] {line.strip()}")
            elif kind == "code":
                first = next((l for l in text.splitlines() if l.strip()), "")
                print(f"[{number:>3}]     {first.strip()[:110]}")
            continue
        print(f"\n# --- cell {number} [{kind}] ---")
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument("--code", action="store_true", help="code cells only")
    parser.add_argument("--outline", action="store_true", help="headings and first lines only")
    args = parser.parse_args()
    for path in args.notebooks:
        print_notebook(path, code_only=args.code, outline=args.outline)


if __name__ == "__main__":
    main()
