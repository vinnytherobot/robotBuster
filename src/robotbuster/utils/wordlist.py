"""Wordlist management and processing utilities for RobotBuster."""

import os
from pathlib import Path
from typing import List, Set, Optional

import asyncio


class WordlistManager:
    """Manager for wordlist loading, deduplication, and manipulation."""

    def __init__(self):
        """Initialize wordlist manager."""
        pass

    async def load_wordlist(self, wordlist_path: Path) -> List[str]:
        """Load wordlist from file with basic preprocessing.
        
        Args:
            wordlist_path: Path to the wordlist file
            
        Returns:
            List of unique, non-empty routes
            
        Raises:
            FileNotFoundError: If wordlist file doesn't exist
            PermissionError: If file cannot be read
        """
        if not wordlist_path.exists():
            raise FileNotFoundError(f"Wordlist file not found: {wordlist_path}")
            
        # We run the file reading in a thread pool to avoid blocking the event loop
        # since reading large files can be slow.
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_load_wordlist, wordlist_path)

    def _sync_load_wordlist(self, wordlist_path: Path) -> List[str]:
        """Synchronous part of wordlist loading.
        
        Args:
            wordlist_path: Path to wordlist file
            
        Returns:
            Processed list of routes
        """
        routes: Set[str] = set()
        
        try:
            with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    route = line.strip()
                    if route and not route.startswith("#"):
                        routes.add(route.lstrip('/'))
        except Exception:
            raise
            
        return sorted(list(routes))

    def filter_extensions(self, routes: List[str], extensions: Set[str]) -> List[str]:
        """Filter routes by given extensions.
        
        Args:
            routes: List of routes
            extensions: Set of allowed extensions (.php, .html)
            
        Returns:
            Filtered list of routes
        """
        if not extensions:
            return routes
            
        # Ensure extensions start with a dot
        exts = {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}
        
        filtered = []
        for route in routes:
            # Add routes that either have the extension or are directories (no dot)
            if any(route.endswith(ext) for ext in exts) or '.' not in route:
                filtered.append(route)
                
        return filtered

    def append_extensions(self, routes: List[str], extensions: List[str]) -> List[str]:
        """Create new route variants by appending extensions.
        
        Args:
            routes: Base routes list
            extensions: List of extensions to append
            
        Returns:
            Expanded list of routes
        """
        if not extensions:
            return routes
            
        expanded = []
        for route in routes:
            expanded.append(route)
            for ext in extensions:
                ext_dot = ext if ext.startswith('.') else f'.{ext}'
                expanded.append(f"{route}{ext_dot}")
                
        return list(set(expanded))
