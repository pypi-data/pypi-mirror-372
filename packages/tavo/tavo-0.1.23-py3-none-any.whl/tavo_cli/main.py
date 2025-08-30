"""
Bino CLI Main Entry Point

CLI bootstrap using Typer for routing commands: create, install, dev, build, start.
"""

import typer
from typing import Optional
from pathlib import Path
import sys
import logging

from .commands import create as create_module, build as build_module, install as install_module
from .commands import dev as dev_module, start as start_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="tavo",
    help="Bino full-stack framework CLI - Python backend + Rust/SWC React SSR",
    add_completion=False
)


@app.command()
def create(
    directory: str = typer.Argument(..., help="Target directory for new project"),
    template: Optional[str] = typer.Option("default", help="Template to use")
) -> None:
    """Create a new Bino project from template."""
    try:
        target_dir = Path(directory).resolve()
        create_module.create_project(target_dir, template)
        typer.echo(f"✅ Created new Bino project in {target_dir}")
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def install() -> None:
    """Install Python and Node.js dependencies."""
    try:
        install_module.install_dependencies()
        typer.echo("✅ Dependencies installed successfully")
    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def dev(
    host: str = typer.Option("localhost", help="Host to bind to"),
    port: int = typer.Option(3000, help="Port to bind to"),
    reload: bool = typer.Option(True, help="Enable auto-reload")
) -> None:
    """Start development server with HMR."""
    try:
        dev_module.start_dev_server(host, port, reload)
    except KeyboardInterrupt:
        typer.echo("\n👋 Development server stopped")
    except Exception as e:
        logger.error(f"Dev server failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def build(
    output_dir: Optional[str] = typer.Option("dist", help="Output directory"),
    production: bool = typer.Option(True, help="Production build")
) -> None:
    """Build project for production."""
    try:
        output_path = Path(output_dir) if output_dir else Path("dist")
        build_module.build_project(output_path, production)
        typer.echo(f"✅ Build completed in {output_path}")
    except Exception as e:
        logger.error(f"Build failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def start(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    workers: int = typer.Option(1, help="Number of worker processes")
) -> None:
    """Start production server."""
    try:
        start_module.start_production_server(host, port, workers)
    except KeyboardInterrupt:
        typer.echo("\n👋 Production server stopped")
    except Exception as e:
        logger.error(f"Production server failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()

# Unit tests as comments:
# 1. test_create_project_success() - verify project creation with valid directory
# 2. test_install_deps_handles_missing_files() - test graceful handling of missing package files
# 3. test_cli_help_output() - verify help text is displayed correctly