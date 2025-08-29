from __future__ import annotations
import argparse
from pathlib import Path
from .core import analyze, pretty_rel
from . import __version__

def parse_args():
    p = argparse.ArgumentParser(
        prog="snaketrail",
        description="List transitive local imports and unused Python files under a project root."
    )
    p.add_argument("entry", help="Entry python file (e.g., Handler.py)")
    p.add_argument("--root", type=Path, default=None, help="Project root (defaults to CWD)")
    p.add_argument("--verbose", "-v", action="store_true", help="Print resolution attempts")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p.parse_args()

def main() -> int:
    args = parse_args()
    root = (args.root or Path.cwd()).resolve()
    entry = Path(args.entry).resolve()

    if not entry.exists():
        print(f"File not found: {entry}")
        return 2

    deps, unused = analyze(entry, root, verbose=args.verbose)

    print(f"Local imports (transitive) under {root}:")
    for p in deps:
        print(" -", pretty_rel(root, p))

    print(f"\nUnused local Python files under {root} ({len(unused)}):")
    if unused:
        for p in unused:
            print(" -", pretty_rel(root, p))
    else:
        print(" (none)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
