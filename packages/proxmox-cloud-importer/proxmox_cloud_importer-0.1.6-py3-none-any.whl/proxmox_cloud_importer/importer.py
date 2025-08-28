"""Core functionality for importing cloud images to Proxmox."""

import hashlib
import logging
import requests
from pathlib import Path
from typing import Optional, Callable
from urllib.parse import urlparse

from plumbum.cmd import qm, qemu_img

from .config import Config, ImageInfo


logger = logging.getLogger(__name__)


class CloudImageImporter:
    """Main class for importing cloud images to Proxmox."""

    def __init__(self, config: Config):
        """Initialize the importer with configuration.

        Args:
            config: Configuration object
        """

        self.config = config
        self.download_path = Path(config.proxmox.temp_download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)

    def get_next_vm_id(self) -> int:
        """Get the next available VM ID starting from configured start ID.

        Returns:
            Next available VM ID
        """

        start_id = self.config.proxmox.default_vm_id_start

        try:
            # Get list of existing VM IDs using qm command
            result = qm["list"]()
            existing_ids = set()

            # Parse qm list output to extract VM IDs
            for line in result.split("\n")[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        try:
                            vm_id = int(parts[0])
                            existing_ids.add(vm_id)
                        except (ValueError, IndexError):
                            continue

            # Find next available ID
            current_id = start_id
            while current_id in existing_ids:
                current_id += 1

            return current_id

        except Exception as e:
            logger.warning(
                f"Could not determine next VM ID, using start ID {start_id}: {e}"
            )
            return start_id

    def download_image(
        self,
        image_id: str,
        output_dir: Optional[Path] = None,
        verify_checksum: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        """Download a cloud image.

        Args:
            image_id: Image identifier
            output_dir: Directory to download to (uses temp dir if None)
            verify_checksum: Whether to verify checksum after download
            progress_callback: Optional callback for download progress

        Returns:
            Path to downloaded file

        Raises:
            ValueError: If image_id not found
            requests.RequestException: If download fails
            Exception: If checksum verification fails
        """

        image_info = self.config.get_image(image_id)
        if not image_info:
            raise ValueError(f"Image '{image_id}' not found in configuration")

        # Determine output directory and filename
        if output_dir is None:
            output_dir = self.download_path
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Extract filename from URL
        parsed_url = urlparse(image_info.url)
        filename = Path(parsed_url.path).name
        if not filename:
            filename = f"{image_id}.{image_info.format}"

        output_path = output_dir / filename

        # Skip download if file already exists and is valid
        if output_path.exists():
            if verify_checksum and (image_info.checksum_url or image_info.checksum):
                try:
                    if self._verify_checksum(output_path, image_info):
                        logger.info(
                            f"File {output_path} already exists and checksum is valid"
                        )
                        return output_path
                    else:
                        logger.info(
                            f"File {output_path} exists but checksum is invalid, re-downloading"
                        )
                        output_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not verify existing file checksum: {e}")
            else:
                logger.info(f"File {output_path} already exists, skipping download")
                return output_path

        # Download the image
        logger.info(f"Downloading {image_info.name} from {image_info.url}")

        response = requests.get(image_info.url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if progress_callback:
                        progress_callback(downloaded_size, total_size)

        logger.info(f"Downloaded {output_path} ({downloaded_size} bytes)")

        # Verify checksum if requested and available
        if verify_checksum and (image_info.checksum_url or image_info.checksum):
            if not self._verify_checksum(output_path, image_info):
                output_path.unlink()  # Remove invalid file
                raise Exception("Checksum verification failed")
            logger.info("Checksum verification passed")

        return output_path

    def _verify_checksum(self, file_path: Path, image_info: ImageInfo) -> bool:
        """Verify file checksum against published checksums or static checksum.

        Args:
            file_path: Path to downloaded file
            image_info: Image information containing checksum URL or static checksum

        Returns:
            True if checksum matches, False otherwise
        """

        # If static checksum is provided, use it for verification
        if image_info.checksum:
            try:
                # Determine hash algorithm based on checksum length
                checksum_length = len(image_info.checksum)
                if checksum_length == 64:  # SHA256
                    hash_algo = "sha256"
                elif checksum_length == 128:  # SHA512
                    hash_algo = "sha512"
                else:
                    logger.warning(f"Unknown checksum format, assuming SHA256")
                    hash_algo = "sha256"
                
                calculated_checksum = self._calculate_file_hash(file_path, hash_algo)
                return calculated_checksum.lower() == image_info.checksum.lower()
                
            except Exception as e:
                logger.error(f"Error verifying static checksum: {e}")
                return False

        # Fall back to checksum URL verification if no static checksum
        if not image_info.checksum_url:
            return True  # No checksum to verify

        try:
            # Download checksum file
            checksum_response = requests.get(image_info.checksum_url)
            checksum_response.raise_for_status()
            checksum_content = checksum_response.text

            # Extract expected checksum for our file
            filename = file_path.name
            expected_checksum = None

            for line in checksum_content.split("\n"):
                if filename in line:
                    # Try different checksum formats (SHA256SUMS, SHA512SUMS, etc.)
                    parts = line.split()
                    if len(parts) >= 2:
                        expected_checksum = parts[0]
                        break

            if not expected_checksum:
                logger.warning(
                    f"Could not find checksum for {filename} in checksum file"
                )
                return True  # Skip verification if checksum not found

            # Calculate file checksum
            hash_algo = "sha256" if "SHA256" in image_info.checksum_url else "sha512"
            calculated_checksum = self._calculate_file_hash(file_path, hash_algo)

            return calculated_checksum.lower() == expected_checksum.lower()

        except Exception as e:
            logger.error(f"Error verifying checksum: {e}")
            return False

    def _calculate_file_hash(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate hash of a file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('sha256' or 'sha512')

        Returns:
            Hexadecimal hash string
        """

        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def import_to_proxmox(
        self,
        image_id: str,
        image_path: Path,
        vm_id: int,
        storage: str,
        template_name: str,
    ) -> None:
        """Import image to Proxmox and create VM template.

        Args:
            image_id: Image identifier
            image_path: Path to downloaded image file
            vm_id: VM ID to use
            storage: Proxmox storage name
            template_name: Name for the template

        Raises:
            Exception: If import process fails
        """
        image_info = self.config.get_image(image_id)
        if not image_info:
            raise ValueError(f"Image '{image_id}' not found in configuration")

        try:
            logger.info(f"Creating VM {vm_id}")

            # Create VM with basic configuration
            qm_create_cmd = qm[
                "create",
                str(vm_id),
                "--name",
                template_name,
                "--memory",
                "2048",
                "--cores",
                "2",
                "--net0",
                "virtio,bridge=vmbr0",
                "--scsihw",
                "virtio-scsi-pci",
            ]

            # Add serial console and qemu guest agent if enabled
            if self.config.settings.qemu_guest_agent:
                qm_create_cmd = qm_create_cmd["--agent", "1"]

            qm_create_cmd()
            logger.info(f"Created VM {vm_id}")

            # Convert image if necessary (some images might need conversion)
            converted_path = image_path
            if image_info.format != "qcow2":
                logger.info(f"Converting image from {image_info.format} to qcow2")
                converted_path = image_path.with_suffix(".qcow2")
                qemu_img[
                    "convert",
                    "-f",
                    image_info.format,
                    "-O",
                    "qcow2",
                    str(image_path),
                    str(converted_path),
                ]()

            # Import disk to VM
            logger.info(f"Importing disk to VM {vm_id}")
            qm["importdisk", str(vm_id), str(converted_path), storage]()

            # Attach the imported disk as scsi0
            # First, find the imported disk
            vm_config = qm["config", str(vm_id)]()

            # Look for unused disk in the output
            unused_disk = None
            for line in vm_config.split("\n"):
                if line.startswith("unused") and storage in line:
                    # Extract the full volume ID after "unused[n]: "
                    parts = line.split(":", 1)  # Split only on first colon
                    if len(parts) >= 2:
                        unused_disk = parts[1].strip()
                    break

            if unused_disk:
                logger.info(f"Attaching disk {unused_disk} as scsi0")
                qm["set", str(vm_id), "--scsi0", f"{unused_disk},discard=on"]()
            else:
                raise Exception("Could not find imported disk to attach")

            # Set boot disk
            qm["set", str(vm_id), "--boot", "order=scsi0"]()

            # Add CloudInit drive if the image supports it
            if image_info.cloud_init:
                logger.info("Adding CloudInit drive")
                qm["set", str(vm_id), "--ide2", f"{storage}:cloudinit"]()
                qm["set", str(vm_id), "--serial0", "socket", "--vga", "serial0"]()

            # Resize disk if default size is specified
            if self.config.settings.default_disk_size != "20G":
                logger.info(
                    f"Resizing disk to {self.config.settings.default_disk_size}"
                )
                qm[
                    "resize",
                    str(vm_id),
                    "scsi0",
                    self.config.settings.default_disk_size,
                ]()

            # Convert to template
            logger.info(f"Converting VM {vm_id} to template")
            qm["template", str(vm_id)]()

            logger.info(
                f"Successfully created template '{template_name}' with ID {vm_id}"
            )

            # Cleanup temporary converted file if created
            if converted_path != image_path and converted_path.exists():
                converted_path.unlink()

            # Cleanup original download if configured
            if self.config.settings.cleanup_downloads and image_path.exists():
                image_path.unlink()
                logger.info(f"Cleaned up downloaded file: {image_path}")

        except Exception as e:
            logger.error(f"Failed to import image to Proxmox: {e}")

            # Cleanup: try to remove the VM if it was created
            try:
                qm["destroy", str(vm_id)]()
                logger.info(f"Cleaned up failed VM {vm_id}")
            except Exception:
                pass  # VM might not have been created

            raise
