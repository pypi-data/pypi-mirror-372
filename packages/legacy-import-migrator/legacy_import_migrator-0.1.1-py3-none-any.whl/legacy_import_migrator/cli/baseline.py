"""Baseline command for managing migration baselines."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..tracker import ImportTracker


@click.command("baseline")
@click.option(
    "--write",
    is_flag=True,
    help="Write current state as new baseline"
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
    "--baseline-file",
    default=".cache/migration_baseline.json",
    help="Path to baseline file"
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
def baseline_command(
    write: bool,
    roots: str,
    legacy_patterns: str,
    allow: tuple[str],
    baseline_file: str,
    verbose: bool,
) -> None:
    """Manage migration baseline for tracking progress.
    
    The baseline represents the initial state of legacy imports when migration
    tracking began. Progress is measured against this baseline.
    """
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
        allow_patterns=allow_list,
        baseline_file=baseline_file
    )
    
    baseline_path = Path(baseline_file)
    
    if write:
        # Write new baseline
        console.print("📊 Creating new migration baseline...", style="blue")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning repository for current state...", total=None)
            
            try:
                # Scan current state
                result = tracker.scan(
                    scope="all",
                    search_roots=search_roots,
                    verbose=verbose
                )
                
                # Write as baseline
                tracker.write_baseline(result)
                
            except Exception as e:
                if verbose:
                    import traceback
                    console.print(f"❌ Baseline creation failed: {e}", style="red")
                    console.print(traceback.format_exc(), style="dim")
                else:
                    console.print(f"❌ Baseline creation failed: {e}", style="red")
                sys.exit(1)
        
        console.print()
        console.print("✅ Baseline created successfully!", style="green bold")
        console.print(f"📄 File: {baseline_path.resolve()}")
        console.print(f"🔢 Blocking imports: {result.blocking_imports}")
        console.print(f"🔢 Total imports: {result.total_imports}")
        console.print(f"📁 Files scanned: {result.files_scanned}")
        
        if verbose:
            console.print()
            console.print("📊 Baseline Summary:", style="blue")
            console.print(f"Repository: {result.repo_root}")
            console.print(f"Commit: {result.baseline_commit or 'unknown'}")
            
            if result.blocking_by_file:
                console.print("Top files with blocking imports:")
                for file_path, count in result.blocking_by_file[:5]:
                    console.print(f"  {file_path}: {count} imports")
        
    else:
        # Show current baseline info
        if not baseline_path.exists():
            console.print("❌ No baseline found!", style="red")
            console.print(f"📄 Expected location: {baseline_path.resolve()}")
            console.print("💡 Use --write to create a new baseline")
            sys.exit(1)
        
        console.print("📊 Current Migration Baseline", style="blue bold")
        console.print("=" * 30, style="dim")
        
        try:
            # Load baseline data
            baseline_data = tracker._load_baseline()
            
            if baseline_data:
                console.print(f"📄 File: {baseline_path.resolve()}")
                
                imports = baseline_data.get("imports", {})
                console.print(f"🔢 Blocking imports: {imports.get('blocking', 'unknown')}")
                console.print(f"🔢 Total imports: {imports.get('total', 'unknown')}")
                
                commit = baseline_data.get("baseline_commit")
                if commit:
                    console.print(f"📝 Commit: {commit}")
                
                created_at = baseline_data.get("created_at")
                if created_at:
                    console.print(f"📅 Created: {created_at}")
                    
            else:
                console.print("❌ Baseline file is empty or corrupted", style="red")
                console.print("💡 Use --write to recreate the baseline")
                
        except Exception as e:
            console.print(f"❌ Error reading baseline: {e}", style="red")
            if verbose:
                import traceback
                console.print(traceback.format_exc(), style="dim")
            sys.exit(1)
        
        console.print()
        console.print("💡 Use 'lim baseline --write' to update the baseline", style="dim")