from pathlib import Path

import toml
import typer
from rich import print as rprint

from .exceptions import PVECLIError
from .validators import config_validate, endpoint_validate
from .. import __version__
from ..proxmox.api import Proxmox
from ..proxmox.exceptions import ProxmoxConnectionError


def config_argument_callback(ctx: typer.Context, configfile_path: Path) -> None:
    if configfile_path.exists():
        with configfile_path.open('rt') as configfile:
            config = toml.loads(configfile.read())
        config_validate(config)
    else:
        if ctx.resilient_parsing:
            return
        raise PVECLIError(f'No config file found, please create one at {configfile_path}')

    defaults = dict(config.pop('defaults', {}))
    ctx.default_map = ctx.default_map or {}  # preserve existing defaults
    ctx.default_map.update(defaults)

    ctx.ensure_object(dict)
    ctx.obj['config'] = config


def version_argument_callback(flag: bool) -> None:
    if flag:
        rprint(f'[bold][green]pve-cli Version:[/green] [blue]{__version__}[blue][/bold]')
        raise typer.Exit()


def endpoint_argument_callback(ctx: typer.Context, endpoint: str) -> None:
    config = ctx.obj['config']
    endpoint_validate(config, endpoint)
    cluster_config = config['endpoint'][endpoint]

    if not cluster_config.get('verify_ssl', True):
        import urllib3

        urllib3.disable_warnings()

    try:
        proxmox_api = Proxmox(**cluster_config)
    except ProxmoxConnectionError as exc:
        raise PVECLIError(str(exc)) from None

    ctx.ensure_object(dict)
    ctx.obj['proxmox_api'] = proxmox_api
