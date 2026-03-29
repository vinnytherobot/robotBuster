"""
Example of how to use RobotBuster as a library.
"""

import asyncio
from pathlib import Path
from robotbuster import RobotScanner, ScanConfig


async def main():
    # 1. Define your configuration
    config = ScanConfig(
        target="https://httpbin.org",
        wordlist=Path("wordlist.txt"),
        concurrency=10,
        status_codes={200, 301, 302, 403, 404}, # We include 404 to see it working
        verbose=True
    )

    # 2. Create a dummy wordlist for this example
    with open("wordlist.txt", "w") as f:
        f.write("status/200\nstatus/404\nstatus/301\nget\nip")

    print(f"🚀 Starting scan on {config.target}...")

    # 3. Initialize and run the scanner
    async with RobotScanner(config) as scanner:
        # We can iterate over the scan generator
        async for result in scanner.scan():
            # 'scanner.scan()' is an AsyncGenerator that yields ScanResult objects
            pass # scanner.check_route also prints to console by default

    # 4. Access final statistics
    summary = scanner.get_summary()
    print("\n📊 Scan Summary:")
    print(f"   - Total Requests: {summary['total_requests']}")
    print(f"   - Findings: {summary['findings']}")
    print(f"   - Requests/sec: {summary['requests_per_second']:.2f}")

    # 5. Clean up example file
    import os
    os.remove("wordlist.txt")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan aborted.")
