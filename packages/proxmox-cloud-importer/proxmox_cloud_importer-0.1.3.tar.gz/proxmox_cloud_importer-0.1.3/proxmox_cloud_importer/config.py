"""Configuration handling for Proxmox Cloud Image Importer."""

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ImageInfo:
    """Information about a cloud image."""

    name: str
    description: str
    url: str
    format: str
    os_type: str
    version: str
    architecture: str
    checksum_url: Optional[str] = None
    cloud_init: bool = True


@dataclass
class ProxmoxConfig:
    """Proxmox-specific configuration."""

    default_storage: str = "local-lvm"
    default_vm_id_start: int = 9000
    temp_download_path: str = "/tmp/cloud-images"


@dataclass
class Settings:
    """Global settings."""

    verify_checksums: bool = True
    cleanup_downloads: bool = True
    default_disk_size: str = "20G"
    qemu_guest_agent: bool = True


@dataclass
class Config:
    """Main configuration class."""

    images: Dict[str, ImageInfo]
    proxmox: ProxmoxConfig
    settings: Settings

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            Config: Parsed configuration object

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Parse images
        images = {}
        for image_id, image_data in data.get("images", {}).items():
            images[image_id] = ImageInfo(
                name=image_data["name"],
                description=image_data["description"],
                url=image_data["url"],
                format=image_data["format"],
                os_type=image_data["os_type"],
                version=image_data["version"],
                architecture=image_data["architecture"],
                checksum_url=image_data.get("checksum_url"),
                cloud_init=image_data.get("cloud_init", True),
            )

        # Parse proxmox config
        proxmox_data = data.get("proxmox", {})
        proxmox = ProxmoxConfig(
            default_storage=proxmox_data.get("default_storage", "local-lvm"),
            default_vm_id_start=proxmox_data.get("default_vm_id_start", 9000),
            temp_download_path=proxmox_data.get(
                "temp_download_path", "/tmp/cloud-images"
            ),
        )

        # Parse settings
        settings_data = data.get("settings", {})
        settings = Settings(
            verify_checksums=settings_data.get("verify_checksums", True),
            cleanup_downloads=settings_data.get("cleanup_downloads", True),
            default_disk_size=settings_data.get("default_disk_size", "20G"),
            qemu_guest_agent=settings_data.get("qemu_guest_agent", True),
        )

        return cls(images=images, proxmox=proxmox, settings=settings)

    def get_image(self, image_id: str) -> Optional[ImageInfo]:
        """Get image information by ID.

        Args:
            image_id: Image identifier

        Returns:
            ImageInfo or None if not found
        """

        return self.images.get(image_id)

    def list_images(self) -> Dict[str, ImageInfo]:
        """Get all available images.

        Returns:
            Dictionary of image_id -> ImageInfo
        """

        return self.images.copy()
