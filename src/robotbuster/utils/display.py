"""Display and formatting utilities for RobotBuster."""

from datetime import datetime
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from ..core.models import ScanConfig, ScanResult, ScanStats


class DisplayManager:
    """Manager for terminal display and formatting."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize with rich console.
        
        Args:
            console: Rich console object
        """
        self.console = console or Console()

    def print_banner(self) -> None:
        """Print the application banner."""
        banner_text = r"""
  ____        _           _   ____                _            
 |  _ \  ___ | |__   ___ | |_| __ ) _   _ ___| |_ ___ _ __ 
 | |_) / _ \| '_ \ / _ \| __|  _ \| | | / __| __/ _ \ '__|
 |  _ < (_) | |_) | (_) | |_| |_) | |_| \__ \ ||  __/ |   
 |_| \_\___/|_.__/ \___/ \__|____/ \__,_|___/\__\___|_|   
        """
        self.console.print(Panel(
            Text(banner_text, style="bold cyan", justify="left"),
            subtitle="[bold white]v2.1 Modern & Professional[/bold white]",
            subtitle_align="right",
            border_style="bright_blue",
            box=box.DOUBLE_EDGE
        ))

    def print_scan_banner(self, config: ScanConfig, total_routes: int) -> None:
        """Print scan parameters banner.
        
        Args:
            config: Scan configuration
            total_routes: Number of routes to scan
        """
        self.print_banner()
        
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_row("[bold blue]Target:[/bold blue]", f"[white]{config.target}[/white]")
        info_table.add_row("[bold blue]Wordlist:[/bold blue]", f"[white]{config.wordlist}[/white] ([cyan]{total_routes:,} routes[/cyan])")
        info_table.add_row("[bold blue]Concurrency:[/bold blue]", f"[white]{config.concurrency} tasks[/white]")
        info_table.add_row("[bold blue]Status Filters:[/bold blue]", f"[white]{', '.join(map(str, config.status_codes))}[/white]")
        info_table.add_row("[bold blue]Timeout:[/bold blue]", f"[white]{config.timeout}s[/white]")
        
        if config.delay > 0:
            info_table.add_row("[bold blue]Delay:[/bold blue]", f"[white]{config.delay}s[/white]")
            
        self.console.print(Panel(info_table, title="[bold green]Scan Parameters[/bold green]", border_style="bright_blue"))

    def print_finding(self, result: ScanResult, verbose: bool = False) -> None:
        """Print a single scan finding.
        
        Args:
            result: Scan finding result
            verbose: Enable verbose info
        """
        status_style = "green" if result.status_code < 300 else "yellow" if result.status_code < 400 else "red"
        
        finding_text = (
            f"[bold blue]{datetime.now().strftime('%H:%M:%S')}[/bold blue] "
            f"[{status_style}]FOUND[/{status_style}] "
            f"[white]{result.url}[/white] "
            f"([bold cyan]Status: {result.status_code}[/bold cyan] | Size: {result.content_length:,})"
        )
        
        if result.title:
            finding_text += f" - [italic yellow]Title: {result.title}[/italic yellow]"
            
        self.console.print(finding_text)
        
        if verbose and result.headers:
            header_table = Table(title="[dim]Response Headers[/dim]", box=box.MINIMAL, show_header=False)
            for k, v in result.headers.items():
                header_table.add_row(f"[dim]{k}[/dim]", f"[dim]{v}[/dim]")
            self.console.print(header_table)

    def print_summary(self, stats: ScanStats, results: List[ScanResult]) -> None:
        """Print the final scan summary table.
        
        Args:
            stats: Scan statistics
            results: List of found results
        """
        if not results:
            self.console.print("\n[bold yellow]Scan finished. No routes found with the specified status codes.[/bold yellow]")
            return

        table = Table(title="\n[bold green]Scan Results Summary[/bold green]", box=box.ROUNDED, header_style="bold magenta", expand=True)
        table.add_column("Status", justify="center", style="cyan")
        table.add_column("Size (Bytes)", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Full URL", style="blue")

        for item in sorted(results, key=lambda x: x.status_code):
            status_style = "green" if item.status_code < 300 else "yellow" if item.status_code < 400 else "red"
            time_fmt = f"{item.response_time*1000:.0f}ms"
            table.add_row(
                f"[{status_style}]{item.status_code}[/{status_style}]",
                f"{item.content_length:,}",
                time_fmt,
                item.url
            )

        self.console.print(table)
        
        # Stats Panel
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_row("[bold blue]Requests:[/bold blue]", f"[white]{stats.total_requests:,}[/white]")
        stats_table.add_row("[bold blue]Findings:[/bold blue]", f"[white]{stats.findings:,} ({stats.findings/stats.total_requests*100:.1f}% hit rate)[/white]")
        stats_table.add_row("[bold blue]Speed:[/bold blue]", f"[white]{stats.requests_per_second:.1f} req/s[/white]")
        stats_table.add_row("[bold blue]Success Rate:[/bold blue]", f"[white]{stats.success_rate:.1f}%[/white]")
        stats_table.add_row("[bold blue]Duration:[/bold blue]", f"[white]{stats.duration:.2f}s[/white]")
        
        self.console.print(Panel(stats_table, title="[bold green]Final Statistics[/bold green]", border_style="bright_blue"))
        self.console.print(f"\n[bold green]✔[/bold green] Finished! Found [bold cyan]{len(results)}[/bold cyan] routes.")

    def get_progress(self) -> Progress:
        """Create and return a configured Rich Progress bar.
        
        Returns:
            Rich progress bar
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, complete_style="bright_cyan", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
            expand=True
        )
