"""
Atomic HTTP client utilities - extracted from duplicate network patterns
"""
import logging
import os
import re
import subprocess
import tempfile
import time
import tomllib
from typing import Any, Dict, List, Optional

import requests
from requests_cache import CachedSession


class HTTPClientUtils:
    """Atomic unit for HTTP client operations"""

    @staticmethod
    def create_cached_session(cache_name: str, cache_ttl: int) -> CachedSession:
        """Create a standardized cached session - atomic unit"""
        return CachedSession(cache_name, expire_after=cache_ttl)

    @staticmethod
    def fetch_with_retry(
        session: requests.Session,
        url: str,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[requests.Response]:
        """Fetch URL with exponential backoff retry - atomic unit"""
        for attempt in range(max_retries):
            try:
                response = session.get(url, headers=headers or {})
                if response.ok:
                    return response
                else:
                    logging.warning(
                        f"HTTP {response.status_code} for {url} on attempt {attempt + 1}"
                    )
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")

            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                wait_time = 2**attempt
                time.sleep(wait_time)

        return None

    @staticmethod
    def extract_github_repo_info(repo_url: str) -> Optional[tuple[str, str]]:
        """Extract owner/repo from GitHub URL - atomic unit"""
        if not repo_url or "github.com" not in repo_url:
            return None

        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if match:
            owner, repo_name = match.groups()
            # Handle .git extensions
            repo_name = repo_name.split(".")[0]
            return owner, repo_name

        return None

    @staticmethod
    def get_github_headers(token: Optional[str] = None) -> Dict[str, str]:
        """Get standardized GitHub API headers - atomic unit"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        return headers


class MetadataExtractor:
    """Atomic unit for extracting metadata from different sources"""

    @staticmethod
    def extract_code_snippets(
        content: str,
        max_snippets: int = 5,
        compile_check: bool = True,
    ) -> List[str]:
        """
        Extract high-quality Rust or TOML snippets from markdown content.

        When ``compile_check`` is enabled (default), each candidate snippet is
        validated by invoking ``rustc`` for Rust or parsing with ``tomllib`` for
        TOML. This provides high-quality results but can incur a performance
        cost (especially for Rust, which spawns a compiler process). Disabling
        ``compile_check`` skips these validations and accepts snippets after
        only a basic length check, which is much faster but may include
        syntactically invalid code.

        Args:
            content: Markdown content to search for snippets.
            max_snippets: Maximum number of snippets to return.
            compile_check: If True, verify Rust snippets compile and TOML
                snippets parse; if False, only a length/quality filter is applied.
        """
        if not content:
            return []

        # Match fenced code blocks like ```rust ...``` or ```toml ...``` (case-insensitive)
        pattern = re.compile(r"```(rust|toml)[^\n]*\n([\s\S]*?)```", re.IGNORECASE)
        snippets: List[str] = []

        for lang, code in pattern.findall(content):
            cleaned = code.strip()
            if len(cleaned) < 20:  # Length filter for quality
                continue

            if compile_check:
                if lang.lower() == "rust":
                    if not MetadataExtractor._compiles_rust(cleaned):
                        continue
                elif lang.lower() == "toml":
                    if not MetadataExtractor._valid_toml(cleaned):
                        continue

            snippets.append(cleaned)
            if len(snippets) >= max_snippets:
                break

        return snippets

    @staticmethod
    def _compiles_rust(code: str) -> bool:
        """Check if a Rust snippet compiles."""
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".rs", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_path = tmp.name
            result = subprocess.run(
                ["rustc", "--crate-type", "lib", tmp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    @staticmethod
    def _valid_toml(code: str) -> bool:
        """Check if a TOML snippet is syntactically valid."""
        try:
            tomllib.loads(code)
            return True
        except Exception:
            return False

    @staticmethod
    def extract_readme_sections(readme: str) -> Dict[str, str]:
        """Extract sections from README based on markdown headers - atomic unit"""
        if not readme:
            return {}

        sections: Dict[str, str] = {}
        current_section = "intro"
        current_content: List[str] = []

        lines = readme.split("\n")
        for line in lines:
            if line.startswith("#"):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = line.strip("#").strip().lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    @staticmethod
    def create_empty_metadata() -> Dict[str, Any]:
        """Create standardized empty metadata structure - atomic unit"""
        return {
            "name": "",
            "version": "",
            "description": "",
            "repository": "",
            "keywords": [],
            "categories": [],
            "readme": "",
            "downloads": 0,
            "github_stars": 0,
            "dependencies": [],
            "code_snippets": [],
            "features": [],
            "readme_sections": {},
            "source": "unknown",
        }