"""CLI interface for Proxmox Cloud Image Importer."""

import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.panel import Panel

from .config import Config
from .importer import CloudImageImporter
from .logging_config import setup_logging

console = Console()


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="images.yaml",
    help="Path to the configuration YAML file",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set the logging level",
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Path to log file (optional)",
)
@click.pass_context
def cli(
    ctx: click.Context, config: Path, log_level: str, log_file: Optional[Path]
) -> None:
    """Proxmox Cloud Image Importer CLI.

    A tool for importing cloud images to Proxmox server with support for
    multiple distributions and automatic VM template creation.
    """
    # Setup logging first
    setup_logging(level=log_level, log_file=log_file)

    ctx.ensure_object(dict)
    try:
        ctx.obj["config"] = Config.from_file(config)
        ctx.obj["importer"] = CloudImageImporter(ctx.obj["config"])
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List available cloud images."""

    config: Config = ctx.obj["config"]

    console.print(Panel.fit("Available Cloud Images", style="blue"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("OS Type", style="yellow")
    table.add_column("Version", style="blue")
    table.add_column("Architecture", style="red")
    table.add_column("Description")

    for image_id, image_info in config.images.items():
        table.add_row(
            image_id,
            image_info.name,
            image_info.os_type,
            image_info.version,
            image_info.architecture,
            image_info.description[:50] + "..."
            if len(image_info.description) > 50
            else image_info.description,
        )

    console.print(table)


@cli.command()
@click.argument("image_id")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Directory to download the image to",
)
@click.option(
    "--verify/--no-verify",
    default=True,
    help="Verify checksum after download",
)
@click.pass_context
def download(
    ctx: click.Context, image_id: str, output_dir: Optional[Path], verify: bool
) -> None:
    """Download a cloud image."""

    config: Config = ctx.obj["config"]
    importer: CloudImageImporter = ctx.obj["importer"]

    if image_id not in config.images:
        console.print(f"[red]Error: Image '{image_id}' not found[/red]")
        available_images = ", ".join(config.images.keys())
        console.print(f"Available images: {available_images}")
        raise click.Abort()

    image_info = config.images[image_id]

    console.print(Panel.fit(f"Downloading {image_info.name}", style="green"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Downloading...", total=100)

        try:
            file_path = importer.download_image(
                image_id,
                output_dir=output_dir,
                verify_checksum=verify,
                progress_callback=lambda current, total: progress.update(
                    task, completed=(current / total) * 100 if total > 0 else 0
                ),
            )
            progress.update(task, completed=100)
            console.print(f"[green]✓[/green] Downloaded to: {file_path}")

        except Exception as e:
            console.print(f"[red]✗ Download failed: {e}[/red]")
            raise click.Abort()


@cli.command()
@click.argument("image_id")
@click.option(
    "--vm-id",
    type=int,
    help="Proxmox VM ID (auto-generated if not specified)",
)
@click.option(
    "--storage",
    type=str,
    help="Proxmox storage name",
)
@click.option(
    "--template-name",
    type=str,
    help="Name for the VM template",
)
@click.option(
    "--download-only",
    is_flag=True,
    help="Only download, don't import to Proxmox",
)
@click.pass_context
def import_image(
    ctx: click.Context,
    image_id: str,
    vm_id: Optional[int],
    storage: Optional[str],
    template_name: Optional[str],
    download_only: bool,
) -> None:
    """Import a cloud image to Proxmox."""
    config: Config = ctx.obj["config"]
    importer: CloudImageImporter = ctx.obj["importer"]

    if image_id not in config.images:
        console.print(f"[red]Error: Image '{image_id}' not found[/red]")
        available_images = ", ".join(config.images.keys())
        console.print(f"Available images: {available_images}")
        raise click.Abort()

    image_info = config.images[image_id]

    # Use defaults if not specified
    vm_id = vm_id or importer.get_next_vm_id()
    storage = storage or config.proxmox.default_storage
    template_name = template_name or f"{image_info.name}-template"

    console.print(Panel.fit(f"Importing {image_info.name}", style="blue"))
    console.print(f"VM ID: {vm_id}")
    console.print(f"Storage: {storage}")
    console.print(f"Template Name: {template_name}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        # Step 1: Download
        download_task = progress.add_task("Downloading image...", total=100)
        try:
            file_path = importer.download_image(
                image_id,
                progress_callback=lambda current, total: progress.update(
                    download_task, completed=(current / total) * 100 if total > 0 else 0
                ),
            )
            progress.update(download_task, completed=100)
            console.print(f"[green]✓[/green] Downloaded: {file_path}")
        except Exception as e:
            console.print(f"[red]✗ Download failed: {e}[/red]")
            raise click.Abort()

        if download_only:
            console.print("[green]Download completed. Skipping Proxmox import.[/green]")
            return

        # Step 2: Import to Proxmox
        import_task = progress.add_task("Importing to Proxmox...", total=None)
        try:
            importer.import_to_proxmox(
                image_id,
                file_path,
                vm_id=vm_id,
                storage=storage,
                template_name=template_name,
            )
            progress.update(import_task, completed=100)
            console.print(
                f"[green]✓[/green] Successfully imported VM {vm_id} as template '{template_name}'"
            )

        except Exception as e:
            console.print(f"[red]✗ Import failed: {e}[/red]")
            raise click.Abort()


@cli.command()
@click.argument("image_id")
@click.pass_context
def info(ctx: click.Context, image_id: str) -> None:
    """Show detailed information about a cloud image."""

    config: Config = ctx.obj["config"]

    if image_id not in config.images:
        console.print(f"[red]Error: Image '{image_id}' not found[/red]")
        available_images = ", ".join(config.images.keys())
        console.print(f"Available images: {available_images}")
        raise click.Abort()

    image_info = config.images[image_id]

    info_panel = Panel.fit(f"Cloud Image Information: {image_id}", style="cyan")
    console.print(info_panel)

    info_table = Table(show_header=False, box=None)
    info_table.add_column("Field", style="bold blue", no_wrap=True)
    info_table.add_column("Value", style="green")

    info_table.add_row("Name", image_info.name)
    info_table.add_row("Description", image_info.description)
    info_table.add_row("OS Type", image_info.os_type)
    info_table.add_row("Version", image_info.version)
    info_table.add_row("Architecture", image_info.architecture)
    info_table.add_row("Format", image_info.format)
    info_table.add_row("Cloud-Init", "Yes" if image_info.cloud_init else "No")
    info_table.add_row("URL", image_info.url)
    info_table.add_row("Checksum URL", image_info.checksum_url or "N/A")

    console.print(info_table)


def main() -> None:
    """Main entry point for the CLI."""

    cli()
