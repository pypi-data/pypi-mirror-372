"""Legacy import tracker module.

This module provides AST-based legacy import scanning and tracking functionality
for Python codebases undergoing namespace migrations.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Default ignore patterns for common directories
DEFAULT_IGNORE_DIRS = {
    ".git", ".venv", ".mypy_cache", ".pytest_cache", "__pycache__",
    ".tox", ".coverage", "node_modules", "dist", "build"
}

# Default allow patterns for migration tracking
DEFAULT_ALLOW_PATTERNS = [
    "tests/namespace/**",
    "tests/deprecation/**",
    "tests/**/test_*deprecation*.py",
    "experiments/**",
]


@dataclass
class ImportSite:
    """Represents a single legacy import site in the codebase."""
    path: Path
    lineno: int
    module: str  # full module name found (e.g., "src.legacy_module.submodule")


@dataclass
class MigrationProgress:
    """Represents the progress of a legacy import migration."""
    repo_root: Path
    scope: str
    files_scanned: int
    blocking_imports: int
    allowed_imports: int
    total_imports: int
    baseline_blocking: int
    progress_percent: float
    blocking_by_file: List[Tuple[str, int]]
    baseline_file: Optional[Path] = None
    baseline_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        result = {
            "version": "1.0",
            "repo_root": str(self.repo_root),
            "scope": self.scope,
            "files_scanned": self.files_scanned,
            "imports": {
                "blocking": self.blocking_imports,
                "allowed": self.allowed_imports,
                "total": self.total_imports,
                "baseline_blocking": self.baseline_blocking,
                "progress_percent": self.progress_percent,
            },
            "blocking_by_file": self.blocking_by_file,
        }
        
        if self.baseline_file:
            result["baseline"] = {
                "file": str(self.baseline_file),
                "commit": self.baseline_commit or "",
            }
            
        return result


class ImportTracker:
    """Tracks legacy imports in Python codebases."""
    
    def __init__(
        self,
        legacy_patterns: Optional[List[str]] = None,
        allow_patterns: Optional[List[str]] = None,
        baseline_file: str = ".cache/migration_baseline.json",
    ):
        """Initialize the tracker.
        
        Args:
            legacy_patterns: List of legacy import patterns to track
            allow_patterns: List of glob patterns for allowed legacy imports
            baseline_file: Path to baseline file for tracking progress
        """
        self.legacy_patterns = legacy_patterns or []
        self.allow_patterns = (allow_patterns or []) + DEFAULT_ALLOW_PATTERNS
        self.baseline_file = Path(baseline_file)
        
    def _repo_root(self) -> Path:
        """Get the repository root directory."""
        try:
            result = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], 
                text=True, 
                encoding="utf-8",
                errors="replace"
            ).strip()
            return Path(result)
        except Exception:
            return Path.cwd().resolve()
            
    def _to_posix_rel(self, root: Path, path: Path) -> str:
        """Convert path to POSIX relative path."""
        try:
            return str(path.resolve().relative_to(root).as_posix())
        except ValueError:
            return str(path)
            
    def _is_legacy_import(self, module_name: str) -> bool:
        """Check if a module name matches legacy patterns."""
        return any(
            module_name == pattern or module_name.startswith(pattern + ".")
            for pattern in self.legacy_patterns
        )
        
    def _extract_ast_imports(self, file_path: Path) -> List[ImportSite]:
        """Extract legacy imports from a Python file using AST."""
        sites = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError):
            return sites
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_legacy_import(alias.name):
                        sites.append(ImportSite(
                            path=file_path,
                            lineno=node.lineno,
                            module=alias.name
                        ))
            elif isinstance(node, ast.ImportFrom) and node.module:
                if self._is_legacy_import(node.module):
                    sites.append(ImportSite(
                        path=file_path,
                        lineno=node.lineno,
                        module=node.module
                    ))
                    
        return sites
        
    def _is_allowed(self, rel_path: str, content: str) -> bool:
        """Check if file is allowed to have legacy imports."""
        # Check for inline allow marker
        if "LEGACY-ALLOW" in content:
            return True
            
        # Check glob patterns
        return any(fnmatch(rel_path, pattern) for pattern in self.allow_patterns)
        
    def _iter_py_files(self, root: Path, search_roots: List[str]) -> Iterable[Path]:
        """Iterate over Python files in search roots."""
        for root_str in search_roots:
            search_path = root / root_str
            if not search_path.exists():
                continue
                
            for py_file in search_path.rglob("*.py"):
                # Skip ignored directories
                if any(part in DEFAULT_IGNORE_DIRS for part in py_file.parts):
                    continue
                yield py_file
                
    def _auto_base(self, root: Path, verbose: bool = False) -> Optional[str]:
        """Automatically determine base commit for changed files."""
        # Try merge-base with common branch names
        candidates = ["origin/main", "origin/master", "main", "master"]
        
        for candidate in candidates:
            try:
                result = subprocess.check_output(
                    ["git", "merge-base", candidate, "HEAD"],
                    cwd=root,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stderr=subprocess.DEVNULL,
                )
                sha = result.strip()
                if sha and verbose:
                    print(f"Using base: {candidate} -> {sha}", file=sys.stderr)
                return sha
            except subprocess.CalledProcessError:
                continue
                
        # Fallback: use second most recent commit
        try:
            result = subprocess.run(
                ["git", "rev-list", "--max-count=2", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            )
            commits = result.stdout.strip().split("\n")
            if len(commits) > 1:
                return commits[1]
        except subprocess.CalledProcessError:
            pass
            
        return None
        
    def _get_changed_files(self, root: Path, base: str, search_roots: List[str]) -> List[Path]:
        """Get list of changed Python files."""
        try:
            result = subprocess.check_output(
                ["git", "diff", "--name-only", f"{base}...HEAD"],
                cwd=root,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            changed_files = result.strip().split("\n") if result.strip() else []
            
            # Filter to Python files in search roots
            py_files = []
            for file_str in changed_files:
                if not file_str.endswith(".py"):
                    continue
                file_path = root / file_str
                if not file_path.exists():
                    continue
                    
                # Check if file is in search roots
                for search_root in search_roots:
                    if file_path.is_relative_to(root / search_root):
                        py_files.append(file_path)
                        break
                        
            return py_files
        except subprocess.CalledProcessError:
            return []
            
    def _load_baseline(self) -> Dict[str, Any]:
        """Load baseline data from file."""
        if not self.baseline_file.exists():
            return {}
            
        try:
            with open(self.baseline_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
            
    def _save_baseline(self, data: Dict[str, Any]) -> None:
        """Save baseline data to file."""
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    def scan(
        self, 
        scope: str = "all",
        base: Optional[str] = None,
        search_roots: Optional[List[str]] = None,
        verbose: bool = False
    ) -> MigrationProgress:
        """Scan for legacy imports and return progress information.
        
        Args:
            scope: 'all' to scan all files, 'changed' to scan changed files only
            base: Base commit for changed file detection (auto-detected if None)
            search_roots: Directories to search in (default: ['src', 'tests'])
            verbose: Enable verbose output
            
        Returns:
            MigrationProgress object with scan results
        """
        if not search_roots:
            search_roots = ["src", "tests"]
            
        root = self._repo_root()
        
        # Determine files to scan
        if scope == "changed":
            if not base or base == "auto":
                base = self._auto_base(root, verbose)
            if base:
                py_files = self._get_changed_files(root, base, search_roots)
            else:
                py_files = list(self._iter_py_files(root, search_roots))
        else:
            py_files = list(self._iter_py_files(root, search_roots))
            
        # Scan files for legacy imports
        blocking_sites: List[ImportSite] = []
        allowed_sites: List[ImportSite] = []
        per_file_counts: Counter[str] = Counter()
        
        for py_file in py_files:
            rel_path = self._to_posix_rel(root, py_file)
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                content = ""
                
            sites = self._extract_ast_imports(py_file)
            if not sites:
                continue
                
            if self._is_allowed(rel_path, content):
                allowed_sites.extend(sites)
            else:
                blocking_sites.extend(sites)
                per_file_counts[rel_path] += len(sites)
                
        # Load baseline for progress calculation
        baseline = self._load_baseline()
        baseline_blocking = baseline.get("imports", {}).get("blocking", len(blocking_sites))
        baseline_commit = baseline.get("baseline_commit")
        
        # Calculate progress
        progress_percent = 0.0
        if baseline_blocking > 0:
            progress_percent = max(0.0, (1.0 - len(blocking_sites) / baseline_blocking) * 100.0)
            
        # Create blocking_by_file list
        blocking_by_file = [(path, count) for path, count in per_file_counts.most_common()]
        
        return MigrationProgress(
            repo_root=root,
            scope=scope,
            files_scanned=len(py_files),
            blocking_imports=len(blocking_sites),
            allowed_imports=len(allowed_sites),
            total_imports=len(blocking_sites) + len(allowed_sites),
            baseline_blocking=baseline_blocking,
            progress_percent=progress_percent,
            blocking_by_file=blocking_by_file,
            baseline_file=self.baseline_file if self.baseline_file.exists() else None,
            baseline_commit=baseline_commit,
        )
        
    def write_baseline(self, progress: Optional[MigrationProgress] = None) -> None:
        """Write current state as baseline.
        
        Args:
            progress: MigrationProgress to use as baseline. If None, scans current state.
        """
        if progress is None:
            progress = self.scan(scope="all")
            
        # Get current commit hash
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=progress.repo_root,
                text=True,
                encoding="utf-8",
                errors="replace"
            ).strip()
        except subprocess.CalledProcessError:
            commit = "unknown"
            
        baseline_data = {
            "imports": {
                "blocking": progress.blocking_imports,
                "total": progress.total_imports,
            },
            "baseline_commit": commit,
            "created_at": progress.repo_root.name,  # Placeholder timestamp
        }
        
        self._save_baseline(baseline_data)