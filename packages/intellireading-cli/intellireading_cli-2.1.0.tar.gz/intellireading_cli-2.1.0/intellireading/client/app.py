import click
from intellireading.client.commands import (
    metaguide_epub_cmd,
    metaguide_xhtml_cmd,
    metaguide_dir_cmd,
)


@click.group(
    name="Intellireading",
    chain=True,
    help="A set of tools designed to improve your reading experience.",
)
@click.option(
    "--log_level",
    default="WARNING",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="The log level to use for logging (default: INFO). Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL",
)
@click.pass_context
def cli(ctx: click.Context, log_level: str):
    ctx.ensure_object(dict)

    import logging

    logging.basicConfig(level=log_level)
    pass


cli.add_command(metaguide_epub_cmd)
cli.add_command(metaguide_dir_cmd)
cli.add_command(metaguide_xhtml_cmd)


def entrypoint():
    cli(obj={})


if __name__ == "__main__":
    entrypoint()
