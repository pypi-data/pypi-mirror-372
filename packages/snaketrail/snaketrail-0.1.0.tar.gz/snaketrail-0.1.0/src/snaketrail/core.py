from __future__ import annotations
import ast
from pathlib import Path
from collections import deque
from typing import Optional, List, Set, Tuple

# Directories to ignore when scanning .py files on disk
IGNORED_DIRS = {
    "__pycache__", ".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache",
    "build", "dist", ".tox", "venv", ".venv", "ENV", "env", ".idea", ".vscode",
    "node_modules"
}

def read_ast(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

def _candidate_paths(base: Path, parts: List[str]) -> List[Path]:
    """
    Filesystem targets for a dotted module under 'base':
      - module.py
      - module/__init__.py
      - module/ (namespace package; no __init__.py)
    """
    c: List[Path] = []
    p = base.joinpath(*parts)
    file = p.with_suffix(".py")
    if file.exists():
        c.append(file)
    if p.is_dir():
        init = p / "__init__.py"
        if init.exists():
            c.append(init)
        else:
            c.append(p)  # namespace package marker (PEP 420)
    return c

def resolve_absolute(module: str, root: Path) -> Optional[Path]:
    for cand in _candidate_paths(root, module.split(".")):
        if cand.exists() and (cand.is_file() or cand.is_dir()):
            return cand
    return None

def resolve_relative(file_path: Path, level: int, module: Optional[str], name: Optional[str], root: Path) -> Optional[Path]:
    """
    Resolve 'from .module import name' relative to file_path (with namespace support).
    """
    base = file_path.parent
    for _ in range(max(level - 1, 0)):
        if base.parent == base:
            break
        base = base.parent
    target = base if not module else base.joinpath(*module.split("."))
    candidates: List[Path] = []
    if name:
        candidates += [target.joinpath(name).with_suffix(".py"),
                       target / name / "__init__.py",
                       target / name]
    else:
        candidates += [target.with_suffix(".py"),
                       target / "__init__.py",
                       target]
    for c in candidates:
        try:
            c = c.resolve()
        except Exception:
            continue
        if c.exists() and (c.is_file() or c.is_dir()) and str(c).startswith(str(root.resolve())):
            return c
    return None

def local_imports_for(file_path: Path, root: Path, verbose: bool=False) -> List[Path]:
    """
    Return direct local imports (files or namespace dirs) for a single file.
    """
    tree = read_ast(file_path)
    results: Set[Path] = set()
    root_resolved = root.resolve()

    def log(*a):
        if verbose: print("[resolve]", *a)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                p = resolve_absolute(mod, root)
                log(f"import {mod} -> {p}")
                if p:
                    results.add(p)

        elif isinstance(node, ast.ImportFrom):
            level = node.level or 0
            mod = node.module  # may be None

            if level == 0:
                # Try BOTH "mod.name" and "mod" for absolute from-imports
                for alias in node.names:
                    name = None if alias.name == "*" else alias.name
                    tried = []
                    if mod and name:
                        m = f"{mod}.{name}"
                        p = resolve_absolute(m, root)
                        tried.append(m)
                        if p:
                            log(f"from {mod} import {name} -> {p}")
                            results.add(p)
                            continue
                    if mod:
                        m = mod
                        p = resolve_absolute(m, root)
                        tried.append(m)
                        log(f"from {mod} import {name or '*'} -> {p} (tried {', '.join(tried)})")
                        if p:
                            results.add(p)
            else:
                for alias in node.names:
                    name = None if alias.name == "*" else alias.name
                    p = resolve_relative(file_path, level, mod, name, root)
                    log(f"from {'.'*level}{mod or ''} import {name or '*'} -> {p}")
                    if p:
                        results.add(p)

    return sorted({p for p in results if str(p.resolve()).startswith(str(root_resolved))})

def walk_local_graph(entry: Path, root: Path, verbose: bool=False) -> List[Path]:
    """
    Transitive closure over local file dependencies.
    (Does not descend into namespace-package directories.)
    """
    seen: Set[Path] = set()
    order: List[Path] = []
    q = deque([entry.resolve()])
    while q:
        f = q.popleft()
        if f in seen:
            continue
        seen.add(f)
        if f != entry.resolve():
            order.append(f)
        for dep in local_imports_for(f, root, verbose):
            # Traverse only into files; namespace-package dirs are markers only
            if dep.is_file() and dep not in seen:
                q.append(dep)
    # de-dup preserve order
    out, s = [], set()
    for p in order:
        if p not in s:
            s.add(p); out.append(p)
    return out

def all_local_python_files(root: Path) -> List[Path]:
    root = root.resolve()
    files: List[Path] = []
    for p in root.rglob("*.py"):
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        files.append(p.resolve())
    return sorted(files)

def include_package_inits(used: Set[Path], root: Path) -> Set[Path]:
    """Mark classic package __init__.py files as used when a module inside is used."""
    root = root.resolve()
    extended = set(used)
    for f in list(used):
        if f.is_dir():
            continue
        cur = f.parent
        while root in cur.parents or cur == root:
            init = cur / "__init__.py"
            if init.exists():
                extended.add(init.resolve())
            if cur == root:
                break
            cur = cur.parent
    return extended

def pretty_rel(root: Path, p: Path) -> str:
    try:
        rel = p.relative_to(root)
    except ValueError:
        return str(p)
    if p.is_dir():
        return f"{rel}/ [namespace package]"
    return str(rel)

def analyze(entry: Path, root: Path, verbose: bool=False) -> Tuple[List[Path], List[Path]]:
    """
    Returns (deps, unused) where:
      deps   = transitive local imports (files or namespace dirs)
      unused = local .py files under root not referenced (excluding this tool)
    """
    root = root.resolve()
    entry = entry.resolve()
    deps = walk_local_graph(entry, root, verbose)

    # Build unused list
    all_py = set(all_local_python_files(root))
    used: Set[Path] = set(deps) | {entry.resolve()}
    used = include_package_inits(used, root)

    # Don't count this tool itself if it lives inside the tree
    try:
        self_path = Path(__file__).resolve()
        all_py.discard(self_path)
    except Exception:
        pass

    unused = sorted(p for p in all_py if p not in used)
    return deps, unused
