"""Typer CLI application for RobotBuster."""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional, Set

import typer
from rich.console import Console

from ..core.scanner import RobotScanner
from ..core.models import ScanConfig
from ..core.exceptions import RobotBusterError
from ..utils.display import DisplayManager

app = typer.Typer(
    name="robotbuster",
    help="Modern, fast, and professional directory brute-force tool",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()
display = DisplayManager(console)


def parse_status_codes(value: str) -> Set[int]:
    """Parse comma-separated status codes.
    
    Args:
        value: Comma-separated status codes
        
    Returns:
        Set of status codes
    """
    if not value:
        return {200, 204, 301, 302, 307, 401, 403}
        
    try:
        codes = {int(s.strip()) for s in value.split(",")}
        return codes
    except ValueError:
        raise typer.BadParameter("Status codes must be comma-separated integers.")


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target URL to scan (e.g., https://example.com)"),
    wordlist: Path = typer.Option(
        ..., "--wordlist", "-w", 
        help="Path to wordlist file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    concurrency: int = typer.Option(
        20, "--tasks", "-t", 
        help="Number of concurrent requests",
        min=1,
        max=1000
    ),
    status: str = typer.Option(
        None, "--status", "-s",
        help="Comma-separated status codes to filter (default: 200,204,301,302,307,401,403)",
        callback=parse_status_codes
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output file to save found routes",
        writable=True,
    ),
    timeout: float = typer.Option(
        10.0, "--timeout", "-T",
        help="Request timeout in seconds"
    ),
    delay: float = typer.Option(
        0.0, "--delay", "-d",
        help="Delay between requests in seconds"
    ),
    user_agent: str = typer.Option(
        "RobotBuster/2.1", "--user-agent", "-ua",
        help="Custom User-Agent string"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output (headers, calibration)"
    ),
    follow_redirects: bool = typer.Option(
        False, "--follow", "-f",
        help="Follow HTTP redirects"
    ),
):
    """
    [bold cyan]Scan[/bold cyan] a target URL for hidden directories and routes.
    """
    
    # Map status callback result if None
    if status is None:
        status = {200, 204, 301, 302, 307, 401, 403}

    # Create config
    config = ScanConfig(
        target=target,
        wordlist=wordlist,
        concurrency=concurrency,
        status_codes=status,
        output_file=output,
        timeout=timeout,
        delay=delay,
        user_agent=user_agent,
        verbose=verbose,
        follow_redirects=follow_redirects,
    )

    async def run_scan():
        try:
            async with RobotScanner(config) as scanner:
                # Use scanner.get_progress() if we want more control,
                # but currently scanner.scan() handles its own progress if we use it with gather.
                # Actually scanner.scan() in its current form uses yield.
                # Let's adapt it to use progress bar here.
                
                # We need to know total routes first to show progress
                from ..utils.wordlist import WordlistManager
                routes = await WordlistManager().load_wordlist(config.wordlist)
                
                display.print_scan_banner(config, len(routes))
                
                with display.get_progress() as progress:
                    task_id = progress.add_task(f"[cyan]Scanning {len(routes):,} routes...", total=len(routes))
                    
                    # Create tasks for concurrent scanning
                    tasks = []
                    for route in routes:
                        tasks.append(scanner.check_route(route, progress, task_id))
                    
                    # Store results in scanner.results as they complete
                    # scanner.check_route handles adding to results and immediate display
                    await asyncio.gather(*tasks)
                    
                # Final summary
                display.print_summary(scanner.stats, scanner.results)
                
        except RobotBusterError as e:
            console.print(f"[bold red]Configuration Error:[/bold red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    try:
        asyncio.run(run_scan())
    except KeyboardInterrupt:
        console.print("\n[bold red]Scan aborted by user. Exiting...[/bold red]")
        sys.exit(0)


@app.command()
def version():
    """Display version information."""
    display.print_banner()
    console.print(f"RobotBuster Version: [bold cyan]2.1.0[/bold cyan]")


def main():
    """Main entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
