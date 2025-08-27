"""Tests for the ImportTracker class."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from legacy_import_migrator.tracker import ImportSite, ImportTracker, MigrationProgress


def test_import_site_creation():
    """Test ImportSite dataclass creation."""
    site = ImportSite(
        path=Path("test.py"),
        lineno=10,
        module="legacy_module"
    )
    
    assert site.path == Path("test.py")
    assert site.lineno == 10
    assert site.module == "legacy_module"


def test_migration_progress_to_dict():
    """Test MigrationProgress to_dict conversion."""
    progress = MigrationProgress(
        repo_root=Path("/test/repo"),
        scope="all",
        files_scanned=100,
        blocking_imports=5,
        allowed_imports=2,
        total_imports=7,
        baseline_blocking=10,
        progress_percent=50.0,
        blocking_by_file=[("test.py", 3), ("other.py", 2)],
    )
    
    result = progress.to_dict()
    
    assert result["version"] == "1.0"
    assert result["imports"]["blocking"] == 5
    assert result["imports"]["progress_percent"] == 50.0
    assert result["blocking_by_file"] == [("test.py", 3), ("other.py", 2)]


def test_import_tracker_initialization():
    """Test ImportTracker initialization."""
    tracker = ImportTracker(
        legacy_patterns=["old_module", "legacy_pkg"],
        allow_patterns=["tests/**"],
    )
    
    assert "old_module" in tracker.legacy_patterns
    assert "legacy_pkg" in tracker.legacy_patterns
    assert "tests/**" in tracker.allow_patterns


def test_is_legacy_import():
    """Test legacy import pattern matching."""
    tracker = ImportTracker(legacy_patterns=["old_module", "legacy_pkg"])
    
    assert tracker._is_legacy_import("old_module")
    assert tracker._is_legacy_import("old_module.submodule") 
    assert tracker._is_legacy_import("legacy_pkg")
    assert tracker._is_legacy_import("legacy_pkg.utils")
    assert not tracker._is_legacy_import("new_module")
    assert not tracker._is_legacy_import("some.old_module")  # Not a prefix match


def test_extract_ast_imports():
    """Test AST-based import extraction."""
    tracker = ImportTracker(legacy_patterns=["old_module"])
    
    # Create a temporary Python file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
import old_module
from old_module import something
from old_module.submodule import func
import new_module  # This should not be detected
from new_module import other
""")
        temp_path = Path(f.name)
    
    try:
        sites = tracker._extract_ast_imports(temp_path)
        
        # Should find 3 legacy imports
        assert len(sites) == 3
        
        # Check that all sites have the correct module
        modules = [site.module for site in sites]
        assert "old_module" in modules
        assert "old_module" in modules  # from old_module import something
        assert "old_module.submodule" in modules
        
    finally:
        temp_path.unlink()


def test_is_allowed():
    """Test file allowance checking."""
    tracker = ImportTracker(
        legacy_patterns=["old_module"],
        allow_patterns=["tests/**", "examples/*"]
    )
    
    # Test glob pattern matching
    assert tracker._is_allowed("tests/test_file.py", "")
    assert tracker._is_allowed("tests/subdir/test.py", "") 
    assert tracker._is_allowed("examples/demo.py", "")
    assert not tracker._is_allowed("src/main.py", "")
    
    # Test inline marker
    assert tracker._is_allowed("src/main.py", "# This file has LEGACY-ALLOW marker")
    assert not tracker._is_allowed("src/main.py", "# Regular file content")


@patch("legacy_import_migrator.tracker.subprocess.check_output")
def test_repo_root(mock_subprocess):
    """Test repository root detection."""
    mock_subprocess.return_value = "/test/repo\n"
    
    tracker = ImportTracker(legacy_patterns=["old"])
    root = tracker._repo_root()
    
    assert root == Path("/test/repo")
    mock_subprocess.assert_called_once()


def test_to_posix_rel():
    """Test relative path conversion.""" 
    tracker = ImportTracker(legacy_patterns=["old"])
    
    root = Path("/test/repo")
    file_path = Path("/test/repo/src/main.py")
    
    result = tracker._to_posix_rel(root, file_path)
    assert result == "src/main.py"