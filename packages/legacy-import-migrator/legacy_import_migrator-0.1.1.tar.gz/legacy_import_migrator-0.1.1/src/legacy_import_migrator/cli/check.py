"""Check command for legacy import violations in CI."""

import sys
from typing import List, Optional

import click
from rich.console import Console

from ..checker import LegacyImportChecker


@click.command("check")
@click.option(
    "--mode",
    type=click.Choice(["changed", "all"]),
    default="changed",
    help="Check mode: 'changed' files only (default) or 'all' files"
)
@click.option(
    "--base", 
    default="auto",
    help="Base commit for changed files (auto-detected if 'auto')"
)
@click.option(
    "--roots",
    default="src,tests", 
    help="Comma-separated list of root directories to search"
)
@click.option(
    "--legacy-patterns",
    required=True,
    help="Comma-separated list of legacy import patterns to check"
)
@click.option(
    "--allow",
    multiple=True,
    help="Glob patterns for allowed legacy imports (can be used multiple times)"
)
@click.option(
    "--allow-marker",
    default="LEGACY-ALLOW",
    help="Inline marker to allow legacy imports in specific files"
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
def check_command(
    mode: str,
    base: str,
    roots: str,
    legacy_patterns: str,
    allow: tuple[str],
    allow_marker: str,
    verbose: bool,
) -> None:
    """Check for legacy import violations (CI-oriented).
    
    This command is designed for CI environments to prevent introduction
    of new legacy imports. It exits with code 2 if violations are found.
    """
    console = Console()
    
    # Parse inputs
    search_roots = [r.strip() for r in roots.split(",") if r.strip()]
    pattern_list = [p.strip() for p in legacy_patterns.split(",") if p.strip()]
    allow_list = list(allow) if allow else []
    
    if not pattern_list:
        console.print("❌ Error: --legacy-patterns is required", style="red")
        sys.exit(1)
    
    # Create checker
    checker = LegacyImportChecker(
        legacy_patterns=pattern_list,
        allow_patterns=allow_list,
        allow_marker=allow_marker
    )
    
    if verbose:
        console.print(f"🔍 Checking {mode} files for legacy imports...")
        console.print(f"Legacy patterns: {', '.join(pattern_list)}")
        console.print(f"Search roots: {', '.join(search_roots)}")
        if allow_list:
            console.print(f"Allow patterns: {', '.join(allow_list)}")
        console.print()
    
    # Perform check
    try:
        success, violations = checker.check(
            mode=mode,
            base=base,
            search_roots=search_roots,
            verbose=verbose
        )
    except Exception as e:
        if verbose:
            import traceback
            console.print(f"❌ Check failed: {e}", style="red")
            console.print(traceback.format_exc(), style="dim")
        else:
            console.print(f"❌ Check failed: {e}", style="red")
        sys.exit(1)
    
    # Display results
    result_text = checker.format_violations(violations)
    
    if success:
        console.print(result_text, style="green")
        if verbose:
            console.print(f"\n🎉 All {mode} files passed legacy import check!")
    else:
        console.print(result_text, style="red")
        console.print(f"\n💡 Use --verbose for more details about the check process", style="dim")
        
    # Exit with appropriate code
    sys.exit(0 if success else 2)