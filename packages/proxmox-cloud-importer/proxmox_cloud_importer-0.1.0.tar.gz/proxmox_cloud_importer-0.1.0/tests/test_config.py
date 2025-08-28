"""Tests for configuration loading functionality."""

import pytest
import tempfile
import yaml
from pathlib import Path

from proxmox_cloud_importer.config import Config, ImageInfo, ProxmoxConfig, Settings


def test_config_from_file():
    """Test loading configuration from YAML file."""
    # Create a temporary YAML configuration
    config_data = {
        "images": {
            "test_image": {
                "name": "Test Image",
                "description": "A test image",
                "url": "https://example.com/test.img",
                "format": "qcow2",
                "os_type": "ubuntu",
                "version": "20.04",
                "architecture": "amd64",
                "checksum_url": "https://example.com/checksum",
                "cloud_init": True,
            }
        },
        "proxmox": {
            "default_storage": "local-lvm",
            "default_vm_id_start": 9000,
            "temp_download_path": "/tmp/test-images",
        },
        "settings": {
            "verify_checksums": True,
            "cleanup_downloads": False,
            "default_disk_size": "30G",
            "qemu_guest_agent": True,
        },
    }

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_config_path = Path(f.name)

    try:
        # Load configuration
        config = Config.from_file(temp_config_path)

        # Verify images
        assert len(config.images) == 1
        assert "test_image" in config.images

        image = config.images["test_image"]
        assert image.name == "Test Image"
        assert image.description == "A test image"
        assert image.url == "https://example.com/test.img"
        assert image.format == "qcow2"
        assert image.os_type == "ubuntu"
        assert image.version == "20.04"
        assert image.architecture == "amd64"
        assert image.checksum_url == "https://example.com/checksum"
        assert image.cloud_init is True

        # Verify proxmox config
        assert config.proxmox.default_storage == "local-lvm"
        assert config.proxmox.default_vm_id_start == 9000
        assert config.proxmox.temp_download_path == "/tmp/test-images"

        # Verify settings
        assert config.settings.verify_checksums is True
        assert config.settings.cleanup_downloads is False
        assert config.settings.default_disk_size == "30G"
        assert config.settings.qemu_guest_agent is True

    finally:
        # Clean up
        temp_config_path.unlink()


def test_config_get_image():
    """Test getting image by ID."""
    config = Config(
        images={
            "ubuntu": ImageInfo(
                name="Ubuntu",
                description="Ubuntu image",
                url="https://example.com/ubuntu.img",
                format="qcow2",
                os_type="ubuntu",
                version="22.04",
                architecture="amd64",
            )
        },
        proxmox=ProxmoxConfig(),
        settings=Settings(),
    )

    # Test existing image
    image = config.get_image("ubuntu")
    assert image is not None
    assert image.name == "Ubuntu"

    # Test non-existing image
    image = config.get_image("nonexistent")
    assert image is None


def test_config_list_images():
    """Test listing all images."""
    config = Config(
        images={
            "ubuntu": ImageInfo(
                name="Ubuntu",
                description="Ubuntu image",
                url="https://example.com/ubuntu.img",
                format="qcow2",
                os_type="ubuntu",
                version="22.04",
                architecture="amd64",
            ),
            "debian": ImageInfo(
                name="Debian",
                description="Debian image",
                url="https://example.com/debian.img",
                format="qcow2",
                os_type="debian",
                version="12",
                architecture="amd64",
            ),
        },
        proxmox=ProxmoxConfig(),
        settings=Settings(),
    )

    images = config.list_images()
    assert len(images) == 2
    assert "ubuntu" in images
    assert "debian" in images
    assert images["ubuntu"].name == "Ubuntu"
    assert images["debian"].name == "Debian"


def test_config_file_not_found():
    """Test handling of missing configuration file."""
    with pytest.raises(FileNotFoundError):
        Config.from_file(Path("nonexistent.yaml"))


def test_config_defaults():
    """Test configuration with default values."""
    config_data = {
        "images": {
            "minimal": {
                "name": "Minimal Image",
                "description": "A minimal test image",
                "url": "https://example.com/minimal.img",
                "format": "qcow2",
                "os_type": "ubuntu",
                "version": "22.04",
                "architecture": "amd64",
                # No checksum_url or cloud_init specified
            }
        }
        # No proxmox or settings specified
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_config_path = Path(f.name)

    try:
        config = Config.from_file(temp_config_path)

        # Check defaults
        image = config.images["minimal"]
        assert image.checksum_url is None
        assert image.cloud_init is True  # Default value

        # Check proxmox defaults
        assert config.proxmox.default_storage == "local-lvm"
        assert config.proxmox.default_vm_id_start == 9000
        assert config.proxmox.temp_download_path == "/tmp/cloud-images"

        # Check settings defaults
        assert config.settings.verify_checksums is True
        assert config.settings.cleanup_downloads is True
        assert config.settings.default_disk_size == "20G"
        assert config.settings.qemu_guest_agent is True

    finally:
        temp_config_path.unlink()
