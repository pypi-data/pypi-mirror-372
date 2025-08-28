#!/usr/bin/env python3
"""Demo script for Proxmox Cloud Image Importer.

This script demonstrates the basic functionality of the tool
without requiring actual Proxmox server access.
"""

from pathlib import Path
from proxmox_cloud_importer.config import Config
from proxmox_cloud_importer.logging_config import setup_logging


def main():
    """Run the demo."""
    print("=== Proxmox Cloud Image Importer Demo ===\n")

    # Setup logging
    setup_logging(level="INFO")

    # Load configuration
    config_path = Path("images.yaml")
    if not config_path.exists():
        print("❌ Configuration file 'images.yaml' not found!")
        print("Please make sure you're running this from the project root directory.")
        return

    try:
        config = Config.from_file(config_path)
        print("✅ Configuration loaded successfully!")
        print(f"   Found {len(config.images)} cloud images configured")
        print(f"   Default storage: {config.proxmox.default_storage}")
        print(f"   VM ID start: {config.proxmox.default_vm_id_start}")
        print(f"   Download path: {config.proxmox.temp_download_path}")
        print()

        # List available images
        print("📋 Available Cloud Images:")
        print("-" * 80)
        for image_id, image_info in config.images.items():
            print(f"  ID: {image_id}")
            print(f"  Name: {image_info.name}")
            print(f"  OS: {image_info.os_type} {image_info.version}")
            print(f"  Architecture: {image_info.architecture}")
            print(f"  Cloud-init: {'Yes' if image_info.cloud_init else 'No'}")
            print(f"  URL: {image_info.url}")
            print()

        # Demo configuration methods
        print("🔍 Testing configuration methods:")

        # Test getting a specific image
        test_image = config.get_image("ubuntu_22_04")
        if test_image:
            print(f"✅ Found image 'ubuntu_22_04': {test_image.name}")
        else:
            print("❌ Could not find 'ubuntu_22_04' image")

        # Test getting non-existent image
        missing_image = config.get_image("nonexistent")
        if missing_image is None:
            print("✅ Correctly returned None for non-existent image")
        else:
            print("❌ Unexpected result for non-existent image")

        # Test list_images method
        all_images = config.list_images()
        print(f"✅ list_images() returned {len(all_images)} images")

        print("\n🎉 Demo completed successfully!")
        print("\nTo use the actual CLI tool, install dependencies with:")
        print("  uv sync")
        print("\nThen run commands like:")
        print("  uv run proxmox-cloud-importer list")
        print("  uv run proxmox-cloud-importer info ubuntu_22_04")
        print("  uv run proxmox-cloud-importer download ubuntu_22_04 --download-only")

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return 1


if __name__ == "__main__":
    exit(main() or 0)
