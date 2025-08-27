"""Scan command for legacy import tracker."""

import json
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..tracker import ImportTracker


@click.command("scan")
@click.option(
    "--scope",
    type=click.Choice(["all", "changed"]),
    default="all",
    help="Scope of scan: 'all' files or 'changed' files only"
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
    help="Comma-separated list of legacy import patterns to track"
)
@click.option(
    "--allow",
    multiple=True,
    help="Glob patterns for allowed legacy imports (can be used multiple times)"
)
@click.option(
    "--json-out",
    type=click.Path(),
    help="Output results to JSON file"
)
@click.option(
    "--fail-when-blocking",
    is_flag=True,
    help="Exit with code 2 when blocking imports are found"
)
@click.option(
    "--print-files",
    is_flag=True,
    help="Print files with blocking imports"
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
def scan_command(
    scope: str,
    base: str,
    roots: str,
    legacy_patterns: str,
    allow: tuple[str],
    json_out: Optional[str],
    fail_when_blocking: bool,
    print_files: bool,
    verbose: bool,
) -> None:
    """Scan for legacy imports and report progress."""
    console = Console()
    
    # Parse inputs
    search_roots = [r.strip() for r in roots.split(",") if r.strip()]
    pattern_list = [p.strip() for p in legacy_patterns.split(",") if p.strip()]
    allow_list = list(allow) if allow else []
    
    if not pattern_list:
        console.print("❌ Error: --legacy-patterns is required", style="red")
        sys.exit(1)
    
    # Create tracker
    tracker = ImportTracker(
        legacy_patterns=pattern_list,
        allow_patterns=allow_list
    )
    
    # Perform scan with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=json_out is not None  # Disable progress bar for JSON output
    ) as progress:
        task = progress.add_task(
            f"Scanning {scope} files for legacy imports...", 
            total=None
        )
        
        try:
            result = tracker.scan(
                scope=scope,
                base=base if base != "auto" else None,
                search_roots=search_roots,
                verbose=verbose
            )
        except Exception as e:
            if verbose:
                import traceback
                console.print(f"❌ Scan failed: {e}", style="red")
                console.print(traceback.format_exc(), style="dim")
            else:
                console.print(f"❌ Scan failed: {e}", style="red")
            sys.exit(1)
    
    # Output results
    if json_out:
        # JSON output
        json_data = result.to_dict()
        output_path = Path(json_out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
            
        if not (json_out == "/dev/stdout" or json_out == "-"):
            console.print(f"📊 Results written to {json_out}")
    
    # Human-readable output (always show unless quiet)
    _print_results(console, result, print_files, verbose)
    
    # Exit with appropriate code
    if fail_when_blocking and result.blocking_imports > 0:
        sys.exit(2)


def _print_results(console: Console, result, print_files: bool, verbose: bool) -> None:
    """Print human-readable results."""
    console.print()
    console.print("📊 Legacy Import Migration Progress", style="bold blue")
    console.print("=" * 40, style="dim")
    
    # Summary
    console.print(f"Repository: {result.repo_root.name}")
    console.print(f"Scope: {result.scope}")
    console.print(f"Files scanned: {result.files_scanned}")
    console.print()
    
    # Import statistics
    blocking_style = "red" if result.blocking_imports > 0 else "green"
    console.print(
        f"Legacy imports: {result.blocking_imports} blocking, "
        f"{result.allowed_imports} allowed, "
        f"{result.total_imports} total",
        style=blocking_style
    )
    
    if result.baseline_blocking > 0:
        progress_style = "green" if result.progress_percent > 0 else "yellow"
        console.print(
            f"Progress: {result.progress_percent:.1f}% "
            f"({result.baseline_blocking - result.blocking_imports} imports resolved)",
            style=progress_style
        )
    
    if result.baseline_commit:
        console.print(f"Baseline: {result.baseline_commit[:8]} (file: {result.baseline_file.name})", style="dim")
    
    console.print()
    
    # Files with blocking imports
    if result.blocking_imports > 0 and (print_files or verbose):
        console.print("📄 Files with blocking imports:", style="yellow")
        for file_path, count in result.blocking_by_file[:10]:  # Show top 10
            console.print(f"  {file_path}: {count} imports")
            
        if len(result.blocking_by_file) > 10:
            console.print(f"  ... and {len(result.blocking_by_file) - 10} more files")
        console.print()
    
    # Status
    if result.blocking_imports == 0:
        console.print("✅ No blocking legacy imports found!", style="green bold")
    else:
        console.print(f"⚠️  Found {result.blocking_imports} blocking legacy imports", style="yellow bold")
        console.print("💡 Use --print-files to see detailed file list", style="dim")