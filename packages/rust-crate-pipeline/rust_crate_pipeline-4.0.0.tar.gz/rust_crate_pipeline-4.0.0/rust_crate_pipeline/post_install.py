#!/usr/bin/env python3
"""
Post-install script for rust-crate-pipeline

This script runs automatically after pip installation to set up
Playwright, Crawl4AI, and Rust tools.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the package to the path so we can import our modules
package_dir = Path(__file__).parent
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

try:
    from setup_manager import SetupManager
except ImportError:
    SetupManager = None


async def post_install_setup():
    """Run post-install setup."""
    print("🚀 Rust Crate Pipeline Post-Install Setup")
    print("=" * 50)
    print("Setting up Playwright, Crawl4AI, and Rust tools...")
    print("This may take a few minutes.")
    print()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        setup_manager = SetupManager(verbose=True)
        success = await setup_manager.run_full_setup()

        if success:
            print("\n🎉 Post-install setup completed successfully!")
            print("\nYou can now use the pipeline:")
            print("  rust-crate-pipeline --help")
            print("  rust-crate-pipeline --crates serde tokio")
        else:
            print("\n⚠️  Post-install setup completed with some issues.")
            print("You can run setup manually later:")
            print("  rust-crate-pipeline --setup")
            print("  rust-crate-setup --verbose")

        return success

    except Exception as e:
        print(f"\n❌ Post-install setup failed: {e}")
        print("You can run setup manually later:")
        print("  rust-crate-pipeline --setup")
        return False


def main():
    """Main entry point for post-install script."""
    try:
        success = asyncio.run(post_install_setup())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Post-install script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
