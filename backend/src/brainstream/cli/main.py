"""CLI commands for BrainStream."""

import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

app = typer.Typer(
    name="brainstream",
    help="Intelligence hub for cloud and AI updates",
    no_args_is_help=True,
)
console = Console()


@app.command()
def open(
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run server on"),
    no_scheduler: bool = typer.Option(False, "--no-scheduler", help="Disable background fetch scheduler"),
    fetch_interval: int = typer.Option(30, "--fetch-interval", help="Minutes between auto-fetches"),
) -> None:
    """Start BrainStream and open the dashboard in your browser."""
    from brainstream.core.config import settings

    console.print(Panel.fit(
        "[bold blue]BrainStream[/bold blue] - Intelligence Hub",
        subtitle="Starting server...",
    ))

    # Set environment variables for scheduler
    os.environ["BRAINSTREAM_SCHEDULER"] = "false" if no_scheduler else "true"
    os.environ["BRAINSTREAM_FETCH_INTERVAL"] = str(fetch_interval)

    url = f"http://{settings.host}:{port}"

    console.print(f"Server: [link={url}]{url}[/link]")
    console.print(f"API Docs: [link={url}/docs]{url}/docs[/link]")
    console.print(f"Scheduler: {'[red]disabled[/red]' if no_scheduler else f'[green]enabled[/green] (every {fetch_interval} min)'}")

    if not no_browser:
        console.print(f"\nOpening browser...")
        webbrowser.open(url)

    console.print("\n[dim]Press Ctrl+C to stop[/dim]\n")

    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "brainstream.main:app",
            host=settings.host,
            port=port,
            reload=settings.debug,
        )
    except ImportError:
        console.print("[red]Error: uvicorn not installed. Run: pip install brainstream[/red]")
        raise typer.Exit(1)


@app.command()
def setup() -> None:
    """Interactive setup wizard for first-time configuration."""
    from brainstream.core.config import settings

    console.print(Panel.fit(
        "[bold blue]BrainStream Setup Wizard[/bold blue]",
        subtitle="Let's configure your intelligence hub",
    ))

    # Ensure data directory exists
    data_dir = settings.ensure_data_dir()
    console.print(f"Data directory: [cyan]{data_dir}[/cyan]")

    # LLM Provider selection
    console.print("\n[bold]Step 1: LLM Provider[/bold]")
    console.print("BrainStream uses your existing CLI tools for LLM processing.")

    llm_choice = Prompt.ask(
        "Which CLI do you have?",
        choices=["claude", "copilot", "none"],
        default="claude",
    )

    if llm_choice == "none":
        console.print("[yellow]Warning: Without an LLM CLI, articles won't be summarized.[/yellow]")
        console.print("Install Claude Code: https://claude.ai/code")
        console.print("Or GitHub Copilot CLI: gh extension install github/gh-copilot")

    # Verify CLI is available
    if llm_choice == "claude":
        result = subprocess.run(["which", "claude"], capture_output=True)
        if result.returncode != 0:
            console.print("[yellow]Warning: 'claude' command not found.[/yellow]")
        else:
            console.print("[green]✓ Claude Code detected[/green]")

    elif llm_choice == "copilot":
        result = subprocess.run(["gh", "copilot", "--version"], capture_output=True)
        if result.returncode != 0:
            console.print("[yellow]Warning: 'gh copilot' not available.[/yellow]")
        else:
            console.print("[green]✓ GitHub Copilot CLI detected[/green]")

    # Tech stack selection
    console.print("\n[bold]Step 2: Your Tech Stack[/bold]")
    console.print("Select the technologies you want to track (comma-separated):")
    console.print("  AWS services: lambda, ec2, s3, rds, dynamodb, ecs, eks")
    console.print("  GCP services: cloud-run, gke, bigquery, cloud-functions")
    console.print("  AI/LLM: openai, anthropic, gemini, langchain")

    tech_input = Prompt.ask(
        "Technologies",
        default="lambda,openai,anthropic",
    )
    tech_stack = [t.strip() for t in tech_input.split(",") if t.strip()]

    # Preferred vendors
    console.print("\n[bold]Step 3: Preferred Vendors[/bold]")
    console.print("Which vendors' updates should be prioritized?")

    vendors_input = Prompt.ask(
        "Vendors (comma-separated)",
        default="AWS,OpenAI",
    )
    preferred_vendors = [v.strip() for v in vendors_input.split(",") if v.strip()]

    # Save configuration
    config_path = data_dir / "config.json"
    config = {
        "llm_provider": llm_choice,
        "tech_stack": tech_stack,
        "preferred_vendors": preferred_vendors,
    }
    config_path.write_text(json.dumps(config, indent=2))

    console.print(f"\n[green]✓ Configuration saved to {config_path}[/green]")
    console.print("\nRun [bold cyan]brainstream open[/bold cyan] to start!")


@app.command()
def fetch(
    source: Optional[str] = typer.Argument(None, help="Specific source to fetch (e.g., 'aws-whatsnew')"),
    skip_llm: bool = typer.Option(False, "--skip-llm", help="Skip LLM processing"),
) -> None:
    """Fetch latest updates from all sources (or a specific one)."""
    import asyncio

    async def _fetch():
        from brainstream.core.database import init_db
        from brainstream.services import collect_all, collect_from_source

        # Initialize database
        await init_db()

        # Load user config for tech stack
        from brainstream.core.config import settings

        tech_stack = []
        config_path = settings.data_dir / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            tech_stack = config.get("tech_stack", [])

        if source:
            console.print(f"Fetching from: [cyan]{source}[/cyan]")
            result = await collect_from_source(
                source,
                tech_stack=tech_stack,
                skip_processing=skip_llm,
            )
            console.print(f"  Fetched: {result.fetched}")
            console.print(f"  New: {result.new}")
            console.print(f"  Processed: {result.processed}")
            if result.errors:
                for err in result.errors:
                    console.print(f"  [red]Error: {err}[/red]")
        else:
            console.print("Fetching from all sources...")
            summary = await collect_all(
                tech_stack=tech_stack,
                skip_processing=skip_llm,
            )

            for src in summary.sources:
                status = "[green]✓[/green]" if not src.errors else "[red]✗[/red]"
                console.print(f"  {status} {src.source_name}: {src.new} new ({src.processed} processed)")

            console.print(f"\n[bold]Total:[/bold] {summary.total_new} new articles")

    console.print("[bold]Fetching updates...[/bold]")

    try:
        asyncio.run(_fetch())
        console.print("\n[green]✓ Fetch complete[/green]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show collection status and statistics."""
    import asyncio

    from brainstream.core.config import settings

    console.print(Panel.fit(
        "[bold blue]BrainStream Status[/bold blue]",
    ))

    data_dir = settings.data_dir
    config_path = data_dir / "config.json"

    if config_path.exists():
        config = json.loads(config_path.read_text())
        console.print(f"LLM Provider: [cyan]{config.get('llm_provider', 'not set')}[/cyan]")
        console.print(f"Tech Stack: [cyan]{', '.join(config.get('tech_stack', []))}[/cyan]")
        console.print(f"Preferred Vendors: [cyan]{', '.join(config.get('preferred_vendors', []))}[/cyan]")
    else:
        console.print("[yellow]Not configured. Run: brainstream setup[/yellow]")

    console.print(f"\nData Directory: [dim]{data_dir}[/dim]")

    # Get database stats
    async def _get_stats():
        from sqlalchemy import func, select

        from brainstream.core.database import get_session, init_db
        from brainstream.models.article import Article, DataSource

        try:
            await init_db()
            async with get_session() as session:
                # Count articles
                result = await session.execute(select(func.count(Article.id)))
                total_articles = result.scalar() or 0

                # Count processed articles
                result = await session.execute(
                    select(func.count(Article.id)).where(Article.processed_at.isnot(None))
                )
                processed_articles = result.scalar() or 0

                # Count sources
                result = await session.execute(select(func.count(DataSource.id)))
                total_sources = result.scalar() or 0

                # Get source details
                result = await session.execute(select(DataSource))
                sources = result.scalars().all()

                return total_articles, processed_articles, total_sources, sources
        except Exception:
            return None, None, None, []

    stats = asyncio.run(_get_stats())
    total_articles, processed_articles, total_sources, sources = stats

    if total_articles is not None:
        console.print(f"\n[bold]Database Statistics:[/bold]")
        console.print(f"  Articles: [cyan]{total_articles}[/cyan] ({processed_articles} processed)")
        console.print(f"  Sources: [cyan]{total_sources}[/cyan]")

        if sources:
            console.print(f"\n[bold]Data Sources:[/bold]")
            table = Table(show_header=True, header_style="bold")
            table.add_column("Source")
            table.add_column("Vendor")
            table.add_column("Status")
            table.add_column("Last Fetched")

            for src in sources:
                status_color = "green" if src.fetch_status == "healthy" else "yellow"
                last_fetched = src.last_fetched_at.strftime("%Y-%m-%d %H:%M") if src.last_fetched_at else "Never"
                table.add_row(
                    src.name,
                    src.vendor,
                    f"[{status_color}]{src.fetch_status}[/{status_color}]",
                    last_fetched,
                )

            console.print(table)
    else:
        console.print("\n[dim]Database not initialized[/dim]")


@app.command()
def config(
    key: Optional[str] = typer.Argument(None, help="Configuration key to view or set"),
    value: Optional[str] = typer.Argument(None, help="New value to set"),
) -> None:
    """View or modify configuration."""
    from brainstream.core.config import settings

    config_path = settings.data_dir / "config.json"

    if not config_path.exists():
        console.print("[yellow]No configuration found. Run: brainstream setup[/yellow]")
        raise typer.Exit(1)

    config_data = json.loads(config_path.read_text())

    if key is None:
        # Show all config
        console.print("[bold]Current Configuration:[/bold]")
        for k, v in config_data.items():
            console.print(f"  {k}: [cyan]{v}[/cyan]")
    elif value is None:
        # Show specific key
        if key in config_data:
            console.print(f"{key}: [cyan]{config_data[key]}[/cyan]")
        else:
            console.print(f"[red]Unknown key: {key}[/red]")
    else:
        # Set value
        config_data[key] = value
        config_path.write_text(json.dumps(config_data, indent=2))
        console.print(f"[green]✓ Set {key} = {value}[/green]")


@app.command()
def sources() -> None:
    """List available data sources."""
    from brainstream.plugins.registry import registry

    plugins = registry.list_plugins()

    console.print(Panel.fit("[bold blue]Available Data Sources[/bold blue]"))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Vendor")
    table.add_column("Type")
    table.add_column("Description")

    for plugin in plugins:
        table.add_row(
            plugin.name,
            plugin.vendor,
            plugin.source_type.value,
            plugin.description[:50] + "..." if len(plugin.description) > 50 else plugin.description,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(plugins)} sources[/dim]")


@app.command()
def version() -> None:
    """Show BrainStream version."""
    from brainstream import __version__

    console.print(f"BrainStream [bold blue]v{__version__}[/bold blue]")


if __name__ == "__main__":
    app()
