import click

from bizon.engine.engine import RunnerFactory
from bizon.engine.runner.config import LoggerLevel
from bizon.source.discover import discover_all_sources

from .utils import (
    parse_from_yaml,
    set_custom_source_path_in_config,
    set_log_level,
    set_runner_in_config,
)


@click.group()
def cli():
    """Bizon CLI."""
    pass


# Create a 'destination' group under 'bizon'
@cli.group()
def source():
    """Subcommands for handling sources."""
    pass


@source.command()
def list():
    """List available sources."""

    click.echo("Retrieving available sources...")
    sources = discover_all_sources()

    click.echo("Available sources:")
    for source_name, source_model in sources.items():
        if not source_model.available_streams:
            click.echo(
                f"{source_name} - NOT AVAILABLE, run 'pip install bizon[{source_name}]' to install missing dependencies."
            )
        else:
            click.echo(f"{source_name} - {source_model.available_streams}")


# Create a 'destination' group under 'bizon'
@cli.group()
def stream():
    """Subcommands for handling streams."""
    pass


@stream.command()
@click.argument("source_name", type=click.STRING)
def list(source_name: str):  # noqa
    """List available streams for a source."""
    sources = discover_all_sources()
    source_model = sources.get(source_name)
    if not source_model:
        click.echo(f"Source {source_name} not found.")
        return

    click.echo(f"Available streams for {source_name}:")
    for stream in source_model.streams:
        stream_mode = "[Supports incremental]" if stream.supports_incremental else "[Full refresh only]"
        click.echo(f"{stream_mode} - {stream.name}")


# Create a 'destination' group under 'bizon'
@cli.group()
def destination():
    """Subcommands for handling destinations."""
    pass


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--custom-source",
    required=False,
    type=click.Path(exists=True),
    help="Custom Python file implementing a Bizon source.",
)
@click.option(
    "--runner",
    required=False,
    type=click.Choice(["thread", "process", "stream"]),
    default="thread",
    show_default=True,
    help="Runner type to use. Thread or Process.",
)
@click.option(
    "--log-level",
    required=False,
    type=click.Choice([level.name for level in LoggerLevel]),
    show_default=True,
    help="Log level to use.",
)
def run(
    filename: str,
    custom_source: str,
    runner: str,
    log_level: LoggerLevel,
    help="Run a bizon pipeline from a YAML file.",
):
    """Run a bizon pipeline from a YAML file."""

    # Parse config from YAML file as a dictionary
    config = parse_from_yaml(filename)

    # Set debug mode
    set_log_level(config=config, level=log_level)

    # Override source_file_path param in config
    set_custom_source_path_in_config(config=config, custom_source=custom_source)

    # Override runner param in config
    set_runner_in_config(config=config, runner=runner)

    runner = RunnerFactory.create_from_config_dict(config=config)
    result = runner.run()

    if result.is_success:
        click.secho("Pipeline finished successfully.", fg="green")

    else:
        raise click.exceptions.ClickException(result.to_string())


if __name__ == "__main__":
    cli()
