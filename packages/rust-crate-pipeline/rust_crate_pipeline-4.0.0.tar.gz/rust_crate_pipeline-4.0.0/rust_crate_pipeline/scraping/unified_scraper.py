import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import aiohttp

try:
    from crawl4ai import (AsyncWebCrawler, BrowserConfig, CrawlerRunConfig,
                          LLMConfig, LLMExtractionStrategy)
except ImportError:
    AsyncWebCrawler = None
    BrowserConfig = None
    CrawlerRunConfig = None
    LLMExtractionStrategy = None
    LLMConfig = None


class ScrapingError(Exception):
    pass


@dataclass
class ScrapingResult:
    url: str
    title: str
    content: str
    structured_data: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    extraction_method: str = "unknown"
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: str(
            asyncio.get_event_loop().time()
            if asyncio.get_event_loop().is_running()
            else time.time()
        )
    )

    def __post_init__(self) -> None:
        if self.timestamp == "0":
            import time

            self.timestamp = str(time.time())


class UnifiedScraper:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.crawler: Optional[Any] = None
        self.browser_config: Optional[Any] = None
        self.github_token = os.getenv("GITHUB_TOKEN")
        self._initialize_crawler()

    def _initialize_crawler(self) -> None:
        if AsyncWebCrawler is None:
            self.logger.warning("Crawl4AI not available - using basic scraping mode")
            return

        try:
            if BrowserConfig:
                self.browser_config = BrowserConfig(
                    headless=self.config.get("headless", True),
                    browser_type=self.config.get("browser_type", "chromium"),
                    verbose=self.config.get("verbose", False),
                )
            self.crawler = AsyncWebCrawler(config=self.browser_config)
            self.logger.info("✅ Crawl4AI crawler initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Crawl4AI: {e}")
            self.crawler = None

    async def __aenter__(self) -> "UnifiedScraper":
        if self.crawler and hasattr(self.crawler, "start"):
            try:
                await self.crawler.start()
            except Exception as e:
                self.logger.warning(f"Failed to start crawler: {e}")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        if self.crawler and hasattr(self.crawler, "stop"):
            try:
                await self.crawler.stop()
            except Exception as e:
                self.logger.warning(f"Error stopping crawler: {e}")

    async def scrape_url(
        self,
        url: str,
        doc_type: str = "general",
        extraction_schema: Optional[Dict[str, Any]] = None,
    ) -> ScrapingResult:
        if not self.crawler:
            raise ScrapingError("No crawler backend available")

        try:
            # Configure crawler run parameters
            config_params: Dict[str, Any] = {
                "word_count_threshold": self.config.get("word_count_threshold", 10),
                "screenshot": self.config.get("screenshot", False),
            }

            # Add CSS selectors based on document type
            if doc_type == "docs":
                config_params["css_selector"] = "main"
            elif doc_type == "readme":
                config_params["css_selector"] = "article, .readme, main"

            # Update with any additional crawl config
            config_params.update(self.config.get("crawl_config", {}))

            # Ensure max_retries is not passed to CrawlerRunConfig
            config_params.pop("max_retries", None)

            crawl_config = (
                CrawlerRunConfig(**config_params) if CrawlerRunConfig else config_params
            )

            # Set up extraction strategy if schema provided
            extraction_strategy = None
            if extraction_schema and LLMExtractionStrategy and LLMConfig:
                # Get LLM configuration from config or use defaults
                llm_provider = self.config.get("llm_provider", "ollama")
                llm_api_base = self.config.get("llm_api_base", "http://localhost:11434")
                llm_model = self.config.get("llm_model", "deepseek-coder:6.7b")
                llm_api_token = self.config.get("llm_api_token", "no-token-needed")

                # Create LLM config
                llm_config = LLMConfig(
                    provider=llm_provider,
                    api_token=llm_api_token,
                    api_base=llm_api_base,
                    model=llm_model,
                    max_tokens=self.config.get("max_tokens", 2048),
                    temperature=self.config.get("temperature", 0.7),
                )

                instruction = (
                    f"Extract structured data from this {doc_type} content "
                    "according to the provided schema."
                )
                extraction_strategy = LLMExtractionStrategy(
                    llm_config=llm_config,
                    schema=extraction_schema,
                    extraction_type="schema",
                    instruction=instruction,
                )

            # Run the crawl
            result = await self.crawler.arun(
                url=url, config=crawl_config, extraction_strategy=extraction_strategy
            )

            # Handle result (Crawl4AI returns direct result, not container)
            if not result:
                raise ScrapingError("Crawl returned no result")

            if not result.success:
                error_message = getattr(
                    result, "error_message", "Crawl was not successful"
                )
                raise ScrapingError(f"Crawl failed: {error_message}")

            markdown_content = getattr(result, "markdown", "") or ""
            extracted_content = getattr(result, "extracted_content", None)

            structured_data = self._process_extracted_content(extracted_content)
            quality_score = self._calculate_quality_score(
                markdown_content, structured_data
            )

            return ScrapingResult(
                url=url,
                title=self._extract_title(markdown_content),
                content=markdown_content,
                structured_data=structured_data,
                quality_score=quality_score,
                extraction_method="crawl4ai",
                metadata={
                    "doc_type": doc_type,
                    "content_length": len(markdown_content),
                    "has_structured_data": bool(structured_data),
                    "crawl_success": result.success,
                },
            )

        except Exception as e:
            self.logger.error(f"Scraping error for {url}: {e}")
            raise ScrapingError(f"Failed to scrape {url}: {str(e)}")

    async def _fetch_github_data(self, repo_url: str) -> Dict[str, Any]:
        """Fetch GitHub repository data using the GitHub API"""
        if not self.github_token:
            self.logger.warning(
                "GITHUB_TOKEN not available - skipping GitHub data fetch"
            )
            return {"error": "No GitHub token available"}

        if not repo_url or "github.com" not in repo_url:
            return {"error": "Not a GitHub repository"}

        # Extract owner/repo from URL
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return {"error": "Could not parse GitHub repository URL"}

        owner, repo_name = match.groups()
        repo_name = repo_name.replace(".git", "").split(".")[0]

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.github_token}",
            "User-Agent": "SigilDERG-Data-Production/1.0",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Fetch repository info
                api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        repo_data = await response.json()

                        # Also fetch README if available
                        readme_url = (
                            f"https://api.github.com/repos/{owner}/{repo_name}/readme"
                        )
                        readme_content = ""
                        try:
                            async with session.get(
                                readme_url, headers=headers
                            ) as readme_response:
                                if readme_response.status == 200:
                                    readme_data = await readme_response.json()
                                    if readme_data.get("content"):
                                        import base64

                                        readme_content = base64.b64decode(
                                            readme_data["content"]
                                        ).decode("utf-8")
                        except Exception as e:
                            self.logger.debug(
                                f"Could not fetch README for {owner}/{repo_name}: {e}"
                            )

                        return {
                            "owner": owner,
                            "repo": repo_name,
                            "full_name": repo_data.get("full_name"),
                            "description": repo_data.get("description"),
                            "stars": repo_data.get("stargazers_count", 0),
                            "forks": repo_data.get("forks_count", 0),
                            "language": repo_data.get("language"),
                            "license": repo_data.get("license", {}).get("name")
                            if repo_data.get("license")
                            else None,
                            "created_at": repo_data.get("created_at"),
                            "updated_at": repo_data.get("updated_at"),
                            "pushed_at": repo_data.get("pushed_at"),
                            "default_branch": repo_data.get("default_branch"),
                            "open_issues": repo_data.get("open_issues_count", 0),
                            "readme_content": readme_content,
                            "archived": repo_data.get("archived", False),
                            "disabled": repo_data.get("disabled", False),
                            "private": repo_data.get("private", False),
                            "url": repo_url,
                            "api_url": api_url,
                            "status": "success",
                        }
                    elif response.status == 404:
                        return {
                            "error": f"Repository {owner}/{repo_name} not found",
                            "status": "not_found",
                        }
                    elif response.status == 403:
                        return {
                            "error": "GitHub API rate limit exceeded or access denied",
                            "status": "rate_limited",
                        }
                    else:
                        return {
                            "error": f"GitHub API returned status {response.status}",
                            "status": "api_error",
                        }

        except Exception as e:
            self.logger.error(f"Error fetching GitHub data for {repo_url}: {e}")
            return {
                "error": f"Failed to fetch GitHub data: {str(e)}",
                "status": "error",
            }

    async def scrape_crate_documentation(
        self, crate_name: str, repository_url: Optional[str] = None
    ) -> Dict[str, ScrapingResult]:
        results: Dict[str, ScrapingResult] = {}

        urls = {
            "crates_io": f"https://crates.io/crates/{crate_name}",
            "docs_rs": f"https://docs.rs/{crate_name}",
            "lib_rs": f"https://lib.rs/crates/{crate_name}",
        }

        # Scrape the standard sources
        for source, url in urls.items():
            try:
                result = await self.scrape_url(url, doc_type="docs")
                results[source] = result
            except ScrapingError as e:
                self.logger.warning(f"Failed to scrape {source} for {crate_name}: {e}")
                results[source] = ScrapingResult(
                    url=url,
                    title=f"{crate_name} - {source}",
                    content="",
                    error=str(e),
                    extraction_method="failed",
                )

        # Add GitHub data if repository URL is provided
        if repository_url and "github.com" in repository_url:
            try:
                github_data = await self._fetch_github_data(repository_url)

                if github_data.get("status") == "success":
                    # Create a successful ScrapingResult with GitHub data
                    github_content = self._format_github_content(github_data)
                    results["github"] = ScrapingResult(
                        url=repository_url,
                        title=f"{crate_name} - GitHub Repository",
                        content=github_content,
                        structured_data=github_data,
                        quality_score=self._calculate_github_quality_score(github_data),
                        extraction_method="github_api",
                        metadata={
                            "repo_stats": {
                                "stars": github_data.get("stars", 0),
                                "forks": github_data.get("forks", 0),
                                "open_issues": github_data.get("open_issues", 0),
                                "language": github_data.get("language"),
                                "license": github_data.get("license"),
                            }
                        },
                    )
                else:
                    # Create a failed ScrapingResult with error info
                    results["github"] = ScrapingResult(
                        url=repository_url,
                        title=f"{crate_name} - GitHub Repository (Error)",
                        content="",
                        error=github_data.get("error", "Unknown GitHub API error"),
                        extraction_method="github_api_failed",
                        metadata={
                            "github_status": github_data.get("status", "unknown")
                        },
                    )

            except Exception as e:
                self.logger.error(f"Error processing GitHub data for {crate_name}: {e}")
                results["github"] = ScrapingResult(
                    url=repository_url or "",
                    title=f"{crate_name} - GitHub Repository (Exception)",
                    content="",
                    error=f"Exception while fetching GitHub data: {str(e)}",
                    extraction_method="github_api_exception",
                )
        else:
            # No GitHub repository or not a GitHub URL
            results["github"] = None

        return results

    def _process_extracted_content(
        self, content: Optional[Union[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        if not content:
            return {}

        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_content": content}

        return content if isinstance(content, dict) else {}

    def _calculate_quality_score(
        self, content: str, structured_data: Dict[str, Any]
    ) -> float:
        if not content:
            return 0.0

        score = 0.0

        content_length = len(content)
        if content_length > 1000:
            score += 3.0
        elif content_length > 500:
            score += 2.0
        elif content_length > 100:
            score += 1.0

        if structured_data:
            score += 2.0

        if "title" in content.lower() or "description" in content.lower():
            score += 1.0

        return min(score, 10.0)

    def _extract_title(self, markdown: str) -> str:
        lines = markdown.split("\n")
        for line in lines[:5]:
            if line.startswith("# "):
                return line[2:].strip()
        return "Untitled"

    def _format_github_content(self, github_data: Dict[str, Any]) -> str:
        """Format GitHub repository data into readable content"""
        content_parts = []

        if github_data.get("full_name"):
            content_parts.append(f"# {github_data['full_name']}")

        if github_data.get("description"):
            content_parts.append(f"\n{github_data['description']}")

        stats = []
        if github_data.get("stars"):
            stats.append(f"⭐ {github_data['stars']} stars")
        if github_data.get("forks"):
            stats.append(f"🍴 {github_data['forks']} forks")
        if github_data.get("open_issues"):
            stats.append(f"🐛 {github_data['open_issues']} open issues")

        if stats:
            content_parts.append(f"\n**Statistics:** {' • '.join(stats)}")

        if github_data.get("language"):
            content_parts.append(f"\n**Primary Language:** {github_data['language']}")

        if github_data.get("license"):
            content_parts.append(f"\n**License:** {github_data['license']}")

        if github_data.get("readme_content"):
            content_parts.append(
                f"\n\n## README\n\n{github_data['readme_content'][:2000]}..."
            )

        return "\n".join(content_parts)

    def _calculate_github_quality_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate quality score for GitHub repository data"""
        score = 2.0  # Base score for successful GitHub fetch

        # Repository activity indicators
        if github_data.get("stars", 0) > 100:
            score += 2.0
        elif github_data.get("stars", 0) > 10:
            score += 1.0

        if github_data.get("forks", 0) > 10:
            score += 1.0

        # Recent activity
        if github_data.get("pushed_at"):
            try:
                from datetime import datetime, timezone

                import dateutil.parser

                pushed_date = dateutil.parser.parse(github_data["pushed_at"])
                days_ago = (datetime.now(timezone.utc) - pushed_date).days
                if days_ago < 30:
                    score += 2.0
                elif days_ago < 365:
                    score += 1.0
            except Exception:
                pass

        # Documentation
        if github_data.get("readme_content"):
            score += 2.0

        if github_data.get("description"):
            score += 1.0

        return min(score, 10.0)

    async def close(self) -> None:
        if self.crawler and hasattr(self.crawler, "stop"):
            try:
                await self.crawler.stop()
            except Exception as e:
                self.logger.warning(f"Error closing crawler: {e}")


async def quick_scrape(url: str, **kwargs: Any) -> ScrapingResult:
    async with UnifiedScraper() as scraper:
        return await scraper.scrape_url(url, **kwargs)
