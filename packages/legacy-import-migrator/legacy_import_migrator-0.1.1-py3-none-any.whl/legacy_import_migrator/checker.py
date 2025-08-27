"""Legacy import checker module.

This module provides CI-oriented checking for legacy imports in changed files,
designed to prevent introduction of new legacy imports during development.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

from .tracker import ImportTracker


class LegacyImportChecker:
    """CI-oriented checker for legacy imports in changed files."""
    
    def __init__(
        self,
        legacy_patterns: List[str],
        allow_patterns: Optional[List[str]] = None,
        allow_marker: str = "LEGACY-ALLOW"
    ):
        """Initialize the checker.
        
        Args:
            legacy_patterns: List of legacy import patterns to check for
            allow_patterns: List of glob patterns for allowed legacy imports
            allow_marker: Inline marker to allow legacy imports in specific files
        """
        self.legacy_patterns = legacy_patterns
        self.allow_patterns = allow_patterns or []
        self.allow_marker = allow_marker
        
        # Create regex pattern for quick text-based checking
        escaped_patterns = [re.escape(p) for p in legacy_patterns]
        pattern_str = r"^\s*(?:from|import)\s+(?:src\.)?(?:" + "|".join(escaped_patterns) + r")\b"
        self.import_regex = re.compile(pattern_str, re.MULTILINE)
        
    def _resolve_base(self, base: str) -> str:
        """Resolve 'auto' base to an actual commit SHA."""
        if base != "auto":
            return base
            
        candidates = [
            "origin/HEAD",
            "origin/main", 
            "origin/master",
        ]
        
        for candidate in candidates:
            try:
                sha = subprocess.check_output(
                    ["git", "merge-base", candidate, "HEAD"],
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stderr=subprocess.DEVNULL,
                ).strip()
                if sha:
                    return sha
            except Exception:
                continue
                
        # Fallback to previous commit
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD~1"],
                text=True,
                encoding="utf-8", 
                errors="replace",
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            # Fallback to initial commit
            result = subprocess.check_output(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                text=True,
                encoding="utf-8",
                errors="replace",
                stderr=subprocess.DEVNULL,
            )
            return result.splitlines()[0]
            
    def _get_changed_files(self, base: str) -> List[Path]:
        """Get changed Python files since base commit."""
        base = self._resolve_base(base)
        
        try:
            result = subprocess.check_output(
                ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", f"{base}..HEAD"],
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            files = [Path(p) for p in result.splitlines() if p.strip()]
            # Filter to Python files only
            return [f for f in files if f.suffix == ".py" and f.exists()]
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}", file=sys.stderr)
            return []
            
    def _get_all_files(self, search_roots: List[str]) -> List[Path]:
        """Get all Python files in search roots."""
        files: List[Path] = []
        
        for root_str in search_roots:
            root_path = Path(root_str)
            if not root_path.exists():
                continue
            files.extend(p for p in root_path.rglob("*.py") if p.is_file())
            
        return files
        
    def _is_file_allowed(self, file_path: Path) -> bool:
        """Check if a file is allowed to have legacy imports."""
        # Check glob patterns against relative path
        rel_path = str(file_path)
        for pattern in self.allow_patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                return True
                
        # Check file content for allow marker
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if self.allow_marker in content:
                return True
        except (OSError, UnicodeDecodeError):
            pass
            
        return False
        
    def _check_file_for_legacy_imports(self, file_path: Path) -> List[Tuple[int, str]]:
        """Check a single file for legacy imports.
        
        Returns:
            List of (line_number, import_line) tuples
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            return []
            
        violations = []
        for match in self.import_regex.finditer(content):
            # Calculate line number
            line_no = content[:match.start()].count('\n') + 1
            line_content = match.group().strip()
            violations.append((line_no, line_content))
            
        return violations
        
    def check(
        self,
        mode: str = "changed", 
        base: str = "auto",
        search_roots: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Tuple[bool, List[Tuple[Path, List[Tuple[int, str]]]]]:
        """Check for legacy imports.
        
        Args:
            mode: 'changed' to check changed files, 'all' to check all files
            base: Base commit for changed mode (default: 'auto')
            search_roots: Directories to search (default: ['src', 'tests'])
            verbose: Enable verbose output
            
        Returns:
            Tuple of (success, violations) where violations is a list of
            (file_path, [(line_no, import_line), ...]) tuples
        """
        if search_roots is None:
            search_roots = ["src", "tests"]
            
        # Get files to check
        if mode == "changed":
            files_to_check = self._get_changed_files(base)
            # Filter to search roots
            filtered_files = []
            for file_path in files_to_check:
                for root in search_roots:
                    try:
                        if file_path.is_relative_to(Path(root)):
                            filtered_files.append(file_path)
                            break
                    except ValueError:
                        # File not relative to this root
                        continue
            files_to_check = filtered_files
        else:
            files_to_check = self._get_all_files(search_roots)
            
        if verbose:
            print(f"Checking {len(files_to_check)} files for legacy imports...", file=sys.stderr)
            
        # Check each file
        violations = []
        
        for file_path in files_to_check:
            # Skip allowed files
            if self._is_file_allowed(file_path):
                if verbose:
                    print(f"Skipping allowed file: {file_path}", file=sys.stderr)
                continue
                
            # Check for legacy imports
            file_violations = self._check_file_for_legacy_imports(file_path)
            if file_violations:
                violations.append((file_path, file_violations))
                if verbose:
                    print(f"Found {len(file_violations)} violations in {file_path}", file=sys.stderr)
                    
        success = len(violations) == 0
        return success, violations
        
    def format_violations(self, violations: List[Tuple[Path, List[Tuple[int, str]]]]) -> str:
        """Format violations for display."""
        if not violations:
            return "✅ No legacy import violations found."
            
        lines = [f"❌ Found {len(violations)} files with legacy imports:"]
        lines.append("")
        
        for file_path, file_violations in violations:
            lines.append(f"📄 {file_path}:")
            for line_no, import_line in file_violations:
                lines.append(f"  Line {line_no}: {import_line}")
            lines.append("")
            
        lines.append("💡 To fix these violations:")
        lines.append("  - Update imports to use the new namespace")
        lines.append(f"  - Or add '{self.allow_marker}' comment to allow specific files")
        lines.append("  - Or update allow patterns in configuration")
        
        return "\n".join(lines)