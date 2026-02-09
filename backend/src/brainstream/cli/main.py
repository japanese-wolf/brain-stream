"""CLI for BrainStream."""

import asyncio
import logging

import typer
from rich.console import Console
from rich.table import Table

from brainstream.core.config import settings

app = typer.Typer(
    name="brainstream",
    help="BrainStream - Topology-based serendipity discovery",
)
console = Console()


@app.command()
def serve(
    host: str = typer.Option(settings.host, help="Host to bind to"),
    port: int = typer.Option(settings.port, help="Port to bind to"),
):
    """Start the API server."""
    import uvicorn

    console.print(f"[bold green]Starting BrainStream API server[/]")
    console.print(f"  Host: {host}:{port}")
    console.print(f"  Data: {settings.data_dir}")

    uvicorn.run(
        "brainstream.main:app",
        host=host,
        port=port,
        reload=settings.debug,
    )


@app.command()
def fetch(
    source: str = typer.Option("", help="Specific source to fetch from (empty = all)"),
    skip_llm: bool = typer.Option(False, "--skip-llm", help="Skip LLM processing"),
):
    """Fetch articles from data sources."""

    async def _fetch():
        from brainstream.core.database import init_db

        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        settings.ensure_data_dir()
        init_db()

        if source:
            from brainstream.services.collector import collect_from_source

            console.print(f"[bold]Fetching from {source}...[/]")
            result = await collect_from_source(source, skip_processing=skip_llm)
            console.print(f"  Fetched: {result.fetched}, New: {result.new}, Processed: {result.processed}")
            if result.errors:
                for err in result.errors:
                    console.print(f"  [red]Error: {err}[/]")
        else:
            from brainstream.services.collector import collect_all

            console.print("[bold]Fetching from all sources...[/]")
            summary = await collect_all(skip_processing=skip_llm)

            table = Table(title="Collection Results")
            table.add_column("Source", style="cyan")
            table.add_column("Fetched", justify="right")
            table.add_column("New", justify="right")
            table.add_column("Processed", justify="right")
            table.add_column("Errors", style="red")

            for s in summary.sources:
                table.add_row(
                    s.source_name,
                    str(s.fetched),
                    str(s.new),
                    str(s.processed),
                    ", ".join(s.errors) if s.errors else "-",
                )

            console.print(table)
            console.print(
                f"\n[bold]Total: {summary.total_fetched} fetched, "
                f"{summary.total_new} new, {summary.total_processed} processed "
                f"({summary.duration_ms}ms)[/]"
            )

    asyncio.run(_fetch())


@app.command()
def status():
    """Show system status (articles, clusters, topology)."""
    from brainstream.core.database import init_db

    settings.ensure_data_dir()
    init_db()

    from brainstream.services.topology import TopologyEngine

    topology = TopologyEngine()
    total = topology.get_total_articles()
    clusters = topology.get_topology_info()

    console.print(f"\n[bold]BrainStream Status[/]")
    console.print(f"  Data directory: {settings.data_dir}")
    console.print(f"  Total articles: {total}")
    console.print(f"  Clusters: {len(clusters)}")

    if clusters:
        table = Table(title="Topic Clusters")
        table.add_column("ID", justify="right")
        table.add_column("Articles", justify="right")
        table.add_column("Density", justify="right")
        table.add_column("Alpha", justify="right")
        table.add_column("Beta", justify="right")
        table.add_column("Sample Titles")

        for c in clusters:
            table.add_row(
                str(c.cluster_id),
                str(c.article_count),
                f"{c.density:.3f}",
                f"{c.alpha:.1f}",
                f"{c.beta:.1f}",
                " | ".join(c.sample_titles[:2]) if c.sample_titles else "-",
            )

        console.print(table)
    else:
        console.print("  [dim]No clusters yet. Run 'brainstream fetch' first.[/]")


@app.command()
def sources():
    """List available data source plugins."""
    from brainstream.plugins.registry import registry

    plugins = registry.list_plugins()

    table = Table(title="Data Sources")
    table.add_column("Name", style="cyan")
    table.add_column("Vendor", style="green")
    table.add_column("Type")
    table.add_column("Description")

    for p in plugins:
        table.add_row(p.name, p.vendor, p.source_type.value, p.description)

    console.print(table)


@app.command()
def version():
    """Show version information."""
    from brainstream import __version__

    console.print(f"BrainStream v{__version__}")


if __name__ == "__main__":
    app()
