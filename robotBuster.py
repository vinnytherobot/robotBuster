import os
import asyncio
import httpx
import argparse
from datetime import datetime
from pytz import timezone
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from rich import box

# Configuration & Constants
DEFAULT_CONCURRENCY = 20
DEFAULT_TIMEOUT = 10
DEFAULT_STATUS_CODES = [200, 204, 301, 302, 307, 401, 403]
USER_AGENT = "RobotBuster/2.0 (Modern Route Enumerator)"

console = Console()

class RobotBuster:
    def __init__(self, url, wordlist, concurrency, status_codes, output=None):
        self.url = url.rstrip('/')
        self.wordlist_path = wordlist
        self.concurrency = concurrency
        self.status_codes = status_codes
        self.output = output
        self.found_routes = []
        self.semaphore = asyncio.Semaphore(concurrency)
        self.client = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=False
        )

    def print_banner(self):
        banner_text = r"""
  ____        _           _   ____                _            
 |  _ \  ___ | |__   ___ | |_| __ ) _   _ ___| |_ ___ _ __ 
 | |_) / _ \| '_ \ / _ \| __|  _ \| | | / __| __/ _ \ '__|
 |  _ < (_) | |_) | (_) | |_| |_) | |_| \__ \ ||  __/ |   
 |_| \_\___/|_.__/ \___/ \__|____/ \__,_|___/\__\___|_|   
        """
        console.print(Panel(
            Text(banner_text, style="bold cyan", justify="left"),
            subtitle="[bold white]v2.0 Modern & Fast[/bold white]",
            subtitle_align="right",
            border_style="bright_blue",
            box=box.DOUBLE_EDGE
        ))
        
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_row("[bold blue]Target:[/bold blue]", f"[white]{self.url}[/white]")
        info_table.add_row("[bold blue]Wordlist:[/bold blue]", f"[white]{self.wordlist_path}[/white]")
        info_table.add_row("[bold blue]Concurrency:[/bold blue]", f"[white]{self.concurrency} tasks[/white]")
        info_table.add_row("[bold blue]Status Filters:[/bold blue]", f"[white]{', '.join(map(str, self.status_codes))}[/white]")
        
        console.print(Panel(info_table, title="[bold green]Scan Parameters[/bold green]", border_style="bright_blue"))

    async def check_route(self, route, progress, task_id, wildcard_status, wildcard_size):
        if not route:
            progress.advance(task_id)
            return

        full_url = f"{self.url}/{route.lstrip('/')}"
        
        async with self.semaphore:
            try:
                response = await self.client.get(full_url)
                
                # Check if it's a finding AND NOT a wildcard/false positive
                is_hit = response.status_code in self.status_codes
                is_false_positive = (response.status_code == wildcard_status and len(response.content) == wildcard_size)
                
                if is_hit and not is_false_positive:
                    status_style = "green" if response.status_code < 300 else "yellow" if response.status_code < 400 else "red"
                    self.found_routes.append({
                        "route": route,
                        "status": response.status_code,
                        "size": len(response.content),
                        "url": full_url
                    })
                    # Log finding immediately above the progress bar
                    progress.console.print(
                        f"[bold blue]{datetime.now().strftime('%H:%M:%S')}[/bold blue] "
                        f"[{status_style}]FOUND[/{status_style}] "
                        f"[white]{full_url}[/white] "
                        f"([bold cyan]Status: {response.status_code}[/bold cyan] | Size: {len(response.content)})"
                    )
                    
                    if self.output:
                        with open(self.output, "a") as f:
                            f.write(f"{full_url} [{response.status_code}]\n")
            except httpx.RequestError:
                pass
            finally:
                progress.advance(task_id)

    async def calibrate(self):
        """Check for wildcard 404 responses that might clutter results."""
        random_path = f"robotbuster_{datetime.now().timestamp()}"
        full_url = f"{self.url}/{random_path}"
        
        try:
            console.print(f"[bold blue]ℹ[/bold blue] Calibrating on: [white]{full_url}[/white]")
            response = await self.client.get(full_url)
            if response.status_code in self.status_codes:
                console.print(
                    f"[bold yellow]⚠ Warning:[/bold yellow] Wildcard detected! The server returned [bold cyan]{response.status_code}[/bold cyan] for a non-existent path. "
                    f"Results may include false positives.", 
                    style="yellow"
                )
                return response.status_code, len(response.content)
        except Exception as e:
            console.print(f"[bold red]Calibration Error:[/bold red] {e}")
        
        return None, None

    async def run(self):
        try:
            with open(self.wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                routes = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/bold red] Wordlist '{self.wordlist_path}' not found.", style="red")
            return

        self.print_banner()
        
        # Performance/Accuracy calibration
        wildcard_status, wildcard_size = await self.calibrate()
        
        total_routes = len(routes)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, complete_style="bright_cyan", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            expand=True
        ) as progress:
            task_id = progress.add_task(f"[cyan]Scanning {total_routes} routes...", total=total_routes)
            
            # Pass wildcard info to check_route
            tasks = [self.check_route(route, progress, task_id, wildcard_status, wildcard_size) for route in routes]
            await asyncio.gather(*tasks)

        await self.client.aclose()
        self.print_results()

    def print_results(self):
        if not self.found_routes:
            console.print("\n[bold yellow]Scan finished. No routes found with the specified status codes.[/bold yellow]")
            return

        table = Table(title="\n[bold green]Scan Summary[/bold green]", box=box.ROUNDED, header_style="bold magenta", expand=True)
        table.add_column("Status", justify="center", style="cyan")
        table.add_column("Size (Bytes)", justify="right")
        table.add_column("Route", style="white")
        table.add_column("Full URL", style="blue")

        for item in sorted(self.found_routes, key=lambda x: x['status']):
            status_style = "green" if item['status'] < 300 else "yellow" if item['status'] < 400 else "red"
            table.add_row(
                f"[{status_style}]{item['status']}[/{status_style}]",
                f"{item['size']:,}",
                item['route'],
                item['url']
            )

        console.print(table)
        console.print(f"\n[bold green]✔[/bold green] Finished! Found [bold cyan]{len(self.found_routes)}[/bold cyan] routes.")
        if self.output:
            console.print(f"[bold blue]ℹ[/bold blue] Results saved to: [bold white]{self.output}[/bold white]")

def main():
    parser = argparse.ArgumentParser(description="RobotBuster v2.0 - Fast & Modern Route Enumerator")
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-t", "--tasks", type=int, default=DEFAULT_CONCURRENCY, help=f"Number of concurrent tasks (default: {DEFAULT_CONCURRENCY})")
    parser.add_argument("-s", "--status", type=str, help=f"Comma-separated status codes to filter (default: {','.join(map(str, DEFAULT_STATUS_CODES))})")
    parser.add_argument("-o", "--output", help="Output file to save found routes")
    parser.add_argument("-v", "--version", action="version", version="RobotBuster v2.0")

    args = parser.parse_args()

    # Parse status codes
    if args.status:
        try:
            status_codes = [int(s.strip()) for s in args.status.split(",")]
        except ValueError:
            console.print("[bold red]Error:[/bold red] Invalid status code list.", style="red")
            return
    else:
        status_codes = DEFAULT_STATUS_CODES

    buster = RobotBuster(
        url=args.url,
        wordlist=args.wordlist,
        concurrency=args.tasks,
        status_codes=status_codes,
        output=args.output
    )

    try:
        asyncio.run(buster.run())
    except KeyboardInterrupt:
        console.print("\n[bold red]Scan aborted by user. Exiting...[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")

if __name__ == "__main__":
    main()
