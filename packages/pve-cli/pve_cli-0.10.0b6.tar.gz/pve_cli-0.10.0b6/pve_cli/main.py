from pathlib import Path
from typing import Annotated, Optional

import typer

from . import __metadata__, __version__
from .cluster_cmd import cluster_cli
from .guest_cmd import guest_cli
from .util.callbacks import config_argument_callback, endpoint_argument_callback, version_argument_callback
from .util.completion import endpoint_complete
from .vm_cmd import vm_cli

HELP = f"""{__metadata__['Name']} {__version__}

{__metadata__['Summary']}
"""

cli = typer.Typer(help=HELP)
cli.add_typer(guest_cli, name='guest', help='Guest-agent commands')
cli.add_typer(cluster_cli, name='cluster', help='Cluster commands')
cli.add_typer(vm_cli, name='vm', help='VM commands')

default_configpath = Path(typer.get_app_dir('pve-cli')) / 'config.toml'


@cli.callback(context_settings={'help_option_names': ['-h', '--help'], 'max_content_width': 120})
def main(
    _configfile_path: Annotated[
        Path,
        typer.Option(
            '--config',
            '-c',
            encoding='utf-8',
            callback=config_argument_callback,
            is_eager=True,
            expose_value=False,
            help='Config file path',
        ),
    ] = default_configpath,
    endpoint: Annotated[
        str,
        typer.Option(
            '--endpoint',
            '-e',
            callback=endpoint_argument_callback,
            autocompletion=endpoint_complete,
            expose_value=False,
            help='Endpoint from config to connect to.',
        ),
    ] = '',
    _version: Annotated[
        Optional[bool],
        typer.Option(
            '--version',
            '-V',
            callback=version_argument_callback,
            is_eager=True,
            expose_value=False,
            help='Print version and exit',
        ),
    ] = None,
) -> None:
    pass
