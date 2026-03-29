"""Core scanner implementation for RobotBuster."""

import asyncio
import random  # nosec B403
import time
from pathlib import Path
from typing import List, Set, Optional, AsyncGenerator, Callable
from datetime import datetime

import httpx
from rich.progress import Progress, TaskID
from rich.console import Console

from .models import ScanConfig, ScanResult, ScanStats, WildcardInfo
from .exceptions import NetworkError, TimeoutError, ConnectionError, WildcardDetected
from ..utils.display import DisplayManager
from ..utils.wordlist import WordlistManager


class RobotScanner:
    """Main scanner class for RobotBuster."""

    def __init__(self, config: ScanConfig):
        """Initialize scanner with configuration.

        Args:
            config: Scan configuration object
        """
        self.config = config
        self.stats = ScanStats()
        self.wildcard = WildcardInfo()
        self.results: List[ScanResult] = []
        self.console = Console()
        self.display = DisplayManager(self.console)
        self.semaphore = asyncio.Semaphore(config.concurrency)
        self.client: Optional[httpx.AsyncClient] = None

        # Prepare custom headers
        self.headers = {
            "User-Agent": config.user_agent,
            **config.headers,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def _setup_client(self) -> None:
        """Set up HTTP client with configuration."""
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.config.timeout,
            follow_redirects=self.config.follow_redirects,
            max_redirects=self.config.max_redirects,
        )

    async def calibrate(self) -> WildcardInfo:
        """Calibrate for wildcard responses.

        This method sends a request to a random, non-existent path
        to detect if the server returns wildcard responses (e.g.,
        all paths return 200 with the same content).

        Returns:
            WildcardInfo with detection results
        """
        if not self.client:
            await self._setup_client()

        # Generate random path that shouldn't exist
        random_path = f"robotbuster_calibration_{int(time.time() * 1000)}"
        url = f"{self.config.target}/{random_path}"

        try:
            if self.config.verbose:
                self.console.print(
                    f"[blue]ℹ[/blue] Calibrating on: [white]{url}[/white]"
                )

            response = await self.client.get(url)

            # Check if this looks like a wildcard
            status = response.status_code
            size = len(response.content)

            if status in self.config.status_codes:
                self.wildcard.status_code = status
                self.wildcard.content_length = size
                self.wildcard.content = response.text[:200]
                self.wildcard.detected = True

                self.console.print(
                    f"[yellow]⚠ Warning:[/yellow] Wildcard detected! "
                    f"The server returned [cyan]{status}[/cyan] for non-existent paths.",
                    style="yellow"
                )

        except Exception as e:
            if self.config.verbose:
                self.console.print(
                    f"[red]Calibration Error:[/red] {e}",
                    style="red"
                )

        return self.wildcard

    async def check_route(
        self,
        route: str,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None
    ) -> Optional[ScanResult]:
        """Check a single route for existence.

        Args:
            route: Route to check
            progress: Optional progress bar
            task_id: Optional task ID for progress bar

        Returns:
            ScanResult if route is found, None otherwise
        """
        if not self.client:
            await self._setup_client()

        # Skip empty routes
        if not route:
            if progress and task_id:
                progress.advance(task_id)
            return None

        url = f"{self.config.target}/{route.lstrip('/')}"
        start_time = time.time()

        async with self.semaphore:
            try:
                # Add delay if configured
                if self.config.delay > 0:
                    await asyncio.sleep(self.config.delay)

                response = await self.client.get(url)
                response_time = time.time() - start_time

                # Update statistics
                self.stats.total_requests += 1
                self.stats.successful_requests += 1

                # Check if this is a finding and not a wildcard
                status = response.status_code
                size = len(response.content)
                is_finding = status in self.config.status_codes
                is_wildcard = self.wildcard.matches(status, size)

                if is_finding and not is_wildcard:
                    # Extract title if HTML
                    title = None
                    if 'html' in response.headers.get('content-type', '').lower():
                        try:
                            import re
                            title_match = re.search(
                                r'<title[^>]*>(.*?)</title>',
                                response.text,
                                re.IGNORECASE
                            )
                            if title_match:
                                title = title_match.group(1).strip()
                        except Exception:  # nosec B110
                            pass

                    result = ScanResult(
                        url=url,
                        status_code=status,
                        content_length=size,
                        response_time=response_time,
                        title=title,
                        headers=dict(response.headers),
                        body_preview=response.text[:200] if response.text else None,
                    )

                    self.results.append(result)
                    self.stats.findings += 1

                    # Display finding
                    self.display.print_finding(result, self.config.verbose)

                    # Save to output file if configured
                    if self.config.output_file:
                        self._save_result(result)

                    return result

            except httpx.TimeoutException:
                self.stats.total_requests += 1
                self.stats.failed_requests += 1
                if self.config.verbose:
                    self.console.print(f"[red]Timeout:[/red] {url}")
            except httpx.RequestError as e:
                self.stats.total_requests += 1
                self.stats.failed_requests += 1
                if self.config.verbose:
                    self.console.print(f"[red]Error:[/red] {url} - {str(e)}")
            except Exception as e:
                self.stats.total_requests += 1
                self.stats.failed_requests += 1
                if self.config.verbose:
                    self.console.print(f"[red]Unexpected Error:[/red] {url} - {str(e)}")
            finally:
                if progress and task_id:
                    progress.advance(task_id)

        return None

    async def scan(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AsyncGenerator[ScanResult, None]:
        """Perform the directory scan.

        Args:
            progress_callback: Optional callback for progress updates

        Yields:
            ScanResult objects as they are found
        """
        # Load wordlist
        wordlist_manager = WordlistManager()
        try:
            routes = await wordlist_manager.load_wordlist(self.config.wordlist)
        except Exception as e:
            raise NetworkError(f"Failed to load wordlist: {e}")

        if not routes:
            self.console.print("[red]Error: Wordlist is empty[/red]")
            return

        # Calibrate for wildcards
        await self.calibrate()

        self.stats.total_requests = len(routes)
        self.stats.start_time = time.time()

        # Display scan banner
        self.display.print_scan_banner(self.config, len(routes))

        # Create tasks for concurrent scanning
        tasks = []
        for route in routes:
            task = self.check_route(route)
            tasks.append(task)

        # Run all tasks and collect results
        for result in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(result, ScanResult):
                yield result

        # Update final statistics
        self.stats.end_time = time.time()

    def _save_result(self, result: ScanResult) -> None:
        """Save a result to the output file.

        Args:
            result: ScanResult to save
        """
        if not self.config.output_file:
            return

        try:
            with open(self.config.output_file, "a", encoding="utf-8") as f:
                line = f"{result.url} [{result.status_code}]"
                if result.title:
                    line += f" - {result.title}"
                f.write(line + "\n")
        except Exception as e:
            self.console.print(
                f"[red]Error saving result:[/red] {e}",
                style="red"
            )

    def get_summary(self) -> dict:
        """Get scan summary statistics.

        Returns:
            Dictionary with summary statistics
        """
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "findings": self.stats.findings,
            "duration": self.stats.duration,
            "requests_per_second": self.stats.requests_per_second,
            "success_rate": self.stats.success_rate,
            "wildcard_detected": self.wildcard.detected,
        }