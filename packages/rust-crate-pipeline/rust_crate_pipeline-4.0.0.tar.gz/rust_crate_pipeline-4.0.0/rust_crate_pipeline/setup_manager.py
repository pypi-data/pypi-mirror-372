#!/usr/bin/env python3
"""
Setup Manager for Rust Crate Pipeline

Handles automatic setup and configuration of all dependencies:
- Playwright browser automation
- Crawl4AI web scraping
- Rust analysis tools (cargo-geiger, cargo-outdated, etc.)
- LLM provider configurations
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class SetupManager:
    """Manages setup and configuration of all pipeline dependencies."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.setup_log = []
        self.errors = []

        # Setup paths
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".rust_crate_pipeline"
        self.config_file = self.config_dir / "setup_config.json"

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

    def log_setup_step(self, step: str, status: str, details: str = ""):
        """Log a setup step with status and details."""
        log_entry = {
            "step": step,
            "status": status,
            "details": details,
            "timestamp": (
                asyncio.get_event_loop().time()
                if asyncio.get_event_loop().is_running()
                else 0
            ),
        }
        self.setup_log.append(log_entry)

        if self.verbose:
            status_icon = (
                "✅" if status == "success" else "❌" if status == "error" else "⚠️"
            )
            print(f"{status_icon} {step}: {details}")
        else:
            logger.info(f"Setup {step}: {status} - {details}")

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH."""
        try:
            result = subprocess.run(
                (
                    [command, "--version"]
                    if command != "cargo"
                    else [command, "--version"]
                ),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            return False

    def check_python_package(self, package: str) -> bool:
        """Check if a Python package is installed."""
        try:
            __import__(package)
            return True
        except ImportError:
            return False

    async def setup_playwright(self) -> bool:
        """Setup Playwright browser automation."""
        try:
            self.log_setup_step(
                "Playwright", "started", "Installing Playwright browsers"
            )

            # Check if playwright is installed
            if not self.check_python_package("playwright"):
                self.log_setup_step(
                    "Playwright", "error", "playwright package not found"
                )
                return False

            # Install browsers
            result = subprocess.run(
                ["playwright", "install"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                self.log_setup_step(
                    "Playwright", "success", "Browsers installed successfully"
                )
                return True
            else:
                self.log_setup_step(
                    "Playwright",
                    "error",
                    f"Failed to install browsers: {result.stderr}",
                )
                return False

        except Exception as e:
            self.log_setup_step("Playwright", "error", f"Setup failed: {str(e)}")
            return False

    async def setup_crawl4ai(self) -> bool:
        """Setup Crawl4AI web scraping."""
        try:
            self.log_setup_step("Crawl4AI", "started", "Configuring Crawl4AI")

            # Check if crawl4ai is installed
            if not self.check_python_package("crawl4ai"):
                self.log_setup_step("Crawl4AI", "error", "crawl4ai package not found")
                return False

            # Create Crawl4AI configuration
            crawl4ai_config = {
                "api_key": os.getenv("CRAWL4AI_API_KEY", ""),
                "base_url": "https://api.crawl4ai.com",
                "timeout": 30,
                "max_retries": 3,
            }

            # Save configuration
            config_path = self.config_dir / "crawl4ai_config.json"
            with open(config_path, "w") as f:
                json.dump(crawl4ai_config, f, indent=2)

            self.log_setup_step("Crawl4AI", "success", "Configuration saved")
            return True

        except Exception as e:
            self.log_setup_step("Crawl4AI", "error", f"Setup failed: {str(e)}")
            return False

    async def setup_rust_tools(self) -> bool:
        """Setup Rust analysis tools."""
        try:
            self.log_setup_step(
                "Rust Tools", "started", "Installing Rust analysis tools"
            )

            # Check if cargo is available
            if not self.check_command_available("cargo"):
                self.log_setup_step(
                    "Rust Tools", "error", "cargo not found - Rust not installed"
                )
                return False

            # List of tools to install
            tools = [
                ("cargo-geiger", "cargo-geiger", "Unsafe code detection"),
                ("cargo-outdated", "cargo-outdated", "Dependency updates"),
                ("cargo-license", "cargo-license", "License analysis"),
                ("cargo-tarpaulin", "cargo-tarpaulin", "Code coverage"),
                ("cargo-deny", "cargo-deny", "Comprehensive dependency checking"),
            ]

            installed_tools = []
            failed_tools = []

            for tool_name, install_command, description in tools:
                try:
                    # Check if already installed
                    if self.check_command_available(tool_name):
                        installed_tools.append(tool_name)
                        self.log_setup_step(
                            f"Rust Tool: {tool_name}",
                            "success",
                            f"Already installed - {description}",
                        )
                        continue

                    # Install tool
                    self.log_setup_step(
                        f"Rust Tool: {tool_name}",
                        "started",
                        f"Installing {description}",
                    )

                    result = subprocess.run(
                        ["cargo", "install", install_command],
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes timeout
                    )

                    if result.returncode == 0:
                        installed_tools.append(tool_name)
                        self.log_setup_step(
                            f"Rust Tool: {tool_name}",
                            "success",
                            f"Installed successfully - {description}",
                        )
                    else:
                        failed_tools.append(tool_name)
                        self.log_setup_step(
                            f"Rust Tool: {tool_name}",
                            "error",
                            f"Installation failed: {result.stderr}",
                        )

                except subprocess.TimeoutExpired:
                    failed_tools.append(tool_name)
                    self.log_setup_step(
                        f"Rust Tool: {tool_name}", "error", "Installation timed out"
                    )
                except Exception as e:
                    failed_tools.append(tool_name)
                    self.log_setup_step(
                        f"Rust Tool: {tool_name}",
                        "error",
                        f"Installation failed: {str(e)}",
                    )

            # Save tool status
            rust_tools_config = {
                "installed_tools": installed_tools,
                "failed_tools": failed_tools,
                "total_tools": len(tools),
            }

            config_path = self.config_dir / "rust_tools_config.json"
            with open(config_path, "w") as f:
                json.dump(rust_tools_config, f, indent=2)

            if failed_tools:
                self.log_setup_step(
                    "Rust Tools",
                    "partial",
                    f"Installed {len(installed_tools)}/{len(tools)} tools",
                )
                return False
            else:
                self.log_setup_step(
                    "Rust Tools",
                    "success",
                    f"All {len(tools)} tools installed successfully",
                )
                return True

        except Exception as e:
            self.log_setup_step("Rust Tools", "error", f"Setup failed: {str(e)}")
            return False

    async def setup_llm_providers(self) -> bool:
        """Setup LLM provider configurations."""
        try:
            self.log_setup_step("LLM Providers", "started", "Configuring LLM providers")

            # Create LLM provider configurations
            llm_configs = {
                "ollama": {
                    "enabled": True,
                    "host": "http://localhost:11434",
                    "default_model": "tinyllama",
                    "setup_instructions": "Run 'ollama serve' and 'ollama pull tinyllama'",
                },
                "openai": {
                    "enabled": False,
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": "https://api.openai.com/v1",
                    "setup_instructions": "Set OPENAI_API_KEY environment variable",
                },
                "azure": {
                    "enabled": False,
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
                    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                    "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
                    "setup_instructions": "Set AZURE_OPENAI_* environment variables",
                },
                "llama-cpp": {
                    "enabled": False,
                    "model_path": "",
                    "setup_instructions": "Download a .gguf model file and specify path",
                },
            }

            # Save configurations
            config_path = self.config_dir / "llm_providers_config.json"
            with open(config_path, "w") as f:
                json.dump(llm_configs, f, indent=2)

            self.log_setup_step("LLM Providers", "success", "Configurations saved")
            return True

        except Exception as e:
            self.log_setup_step("LLM Providers", "error", f"Setup failed: {str(e)}")
            return False

    async def setup_environment_variables(self) -> bool:
        """Setup recommended environment variables."""
        try:
            self.log_setup_step(
                "Environment", "started", "Setting up environment variables"
            )

            # Create .env template
            env_template = """# Rust Crate Pipeline Environment Variables
# Copy this to .env file and fill in your values

# Crawl4AI (optional - for enhanced web scraping)
CRAWL4AI_API_KEY=your_crawl4ai_api_key_here

# OpenAI (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name_here

# GitHub Token (optional - for enhanced GitHub analysis)
GITHUB_TOKEN=your_github_token_here

# Pipeline Configuration
RUST_CRATE_PIPELINE_LOG_LEVEL=INFO
RUST_CRATE_PIPELINE_OUTPUT_DIR=./output
"""

            env_path = self.config_dir / ".env.template"
            with open(env_path, "w") as f:
                f.write(env_template)

            self.log_setup_step(
                "Environment", "success", "Environment template created"
            )
            return True

        except Exception as e:
            self.log_setup_step("Environment", "error", f"Setup failed: {str(e)}")
            return False

    async def run_system_checks(self) -> Dict[str, bool]:
        """Run system compatibility checks."""
        try:
            self.log_setup_step(
                "System Checks", "started", "Running compatibility checks"
            )

            checks = {
                "python_version": sys.version_info >= (3, 11),
                "platform_supported": platform.system()
                in ["Windows", "Linux", "Darwin"],
                "git_available": self.check_command_available("git"),
                "curl_available": self.check_command_available("curl"),
                "pip_available": self.check_command_available("pip"),
            }

            # Log check results
            for check_name, passed in checks.items():
                status = "success" if passed else "warning"
                details = "Compatible" if passed else "Not available"
                self.log_setup_step(f"System Check: {check_name}", status, details)

            # Save check results
            config_path = self.config_dir / "system_checks.json"
            with open(config_path, "w") as f:
                json.dump(checks, f, indent=2)

            self.log_setup_step(
                "System Checks", "success", f"Completed {len(checks)} checks"
            )
            return checks

        except Exception as e:
            self.log_setup_step("System Checks", "error", f"Checks failed: {str(e)}")
            return {}

    async def run_full_setup(self) -> bool:
        """Run complete setup process."""
        try:
            print("🚀 Starting Rust Crate Pipeline Setup")
            print("=" * 50)

            # Run system checks first
            system_checks = await self.run_system_checks()

            # Setup components
            setup_results = {
                "playwright": await self.setup_playwright(),
                "crawl4ai": await self.setup_crawl4ai(),
                "rust_tools": await self.setup_rust_tools(),
                "llm_providers": await self.setup_llm_providers(),
                "environment": await self.setup_environment_variables(),
            }

            # Save overall setup results
            overall_results = {
                "system_checks": system_checks,
                "setup_results": setup_results,
                "setup_log": self.setup_log,
                "timestamp": (
                    asyncio.get_event_loop().time()
                    if asyncio.get_event_loop().is_running()
                    else 0
                ),
            }

            config_path = self.config_dir / "setup_results.json"
            with open(config_path, "w") as f:
                json.dump(overall_results, f, indent=2)

            # Print summary
            print("\n" + "=" * 50)
            print("📋 Setup Summary")
            print("=" * 50)

            success_count = sum(1 for result in setup_results.values() if result)
            total_count = len(setup_results)

            for component, success in setup_results.items():
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {component.title()}: {status}")

            print(
                f"\nOverall: {success_count}/{total_count} components configured successfully"
            )

            if success_count == total_count:
                print("\n🎉 Setup completed successfully!")
                print("\nNext steps:")
                print("  1. Set up your LLM provider (see .env.template)")
                print("  2. Run: rust-crate-pipeline --help")
                print("  3. Try: rust-crate-pipeline --crates serde tokio")
            else:
                print(
                    f"\n⚠️  Setup completed with {total_count - success_count} issues"
                )
                print("Check the setup log for details and manual configuration steps")

            return success_count == total_count

        except Exception as e:
            self.log_setup_step("Full Setup", "error", f"Setup failed: {str(e)}")
            return False

    def get_setup_status(self) -> Dict[str, any]:
        """Get current setup status."""
        try:
            setup_results_file = self.config_dir / "setup_results.json"
            if not setup_results_file.exists():
                return {"status": "not_setup", "message": "Setup has not been run"}

            with open(setup_results_file, "r") as f:
                data = json.load(f)

            # Check if all components were successful
            setup_results = data.get("setup_results", {})
            success_count = sum(1 for result in setup_results.values() if result)
            total_count = len(setup_results)

            if success_count == total_count:
                return {
                    "status": "completed",
                    "message": (
                        f"Setup completed successfully "
                        f"({success_count}/{total_count} components)"
                    ),
                    "components": setup_results,
                }
            else:
                return {
                    "status": "partial",
                    "message": (
                        f"Setup completed with issues "
                        f"({success_count}/{total_count} components)"
                    ),
                    "components": setup_results,
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read setup status: {str(e)}",
            }


async def main():
    """Main setup function."""
    import argparse

    parser = argparse.ArgumentParser(description="Rust Crate Pipeline Setup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--check-only", action="store_true", help="Only check current setup status"
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    setup_manager = SetupManager(verbose=args.verbose)

    if args.check_only:
        status = setup_manager.get_setup_status()
        print(json.dumps(status, indent=2))
        return

    success = await setup_manager.run_full_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
