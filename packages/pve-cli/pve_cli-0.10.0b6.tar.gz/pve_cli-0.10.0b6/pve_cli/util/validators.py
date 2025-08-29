import inspect

import typer

from .exceptions import InvalidConfigError
from ..proxmox import Proxmox
from ..proxmox.exceptions import ProxmoxNodeNotFoundError


def endpoint_validate(config: dict, endpoint: str) -> None:
    endpoints = config.get('endpoint', {})
    if endpoint not in endpoints:
        raise typer.BadParameter(
            f'Config for endpoint "{endpoint}" could not be found in configured endpoints: {", ".join(endpoints)}.'
        )


def config_validate(config: dict) -> None:
    endpoints_config = config.get('endpoint', {})
    default_endpoint = config.get('defaults', {}).get('endpoint', None)
    if default_endpoint is not None and default_endpoint not in endpoints_config:
        raise InvalidConfigError(
            f'The configured default cluster "{default_endpoint}" '
            f'has no configuration section in the config. (available: {", ".join(endpoints_config)})'
        )

    required_keys = [
        param.name
        for param in inspect.signature(Proxmox.__init__).parameters.values()
        if param.default == inspect.Parameter.empty and param.name not in ['self', 'kwargs']
    ]

    invalid_cluster_config = False
    err_msg = []
    for cluster_name, cluster_config in endpoints_config.items():
        missing_keys = [key for key in required_keys if key not in cluster_config]
        if missing_keys:
            err_msg.append(f'  {cluster_name}: {", ".join(missing_keys)}')
            invalid_cluster_config = True

    if invalid_cluster_config:
        raise InvalidConfigError('Missing keys in config for clusters:\n{}'.format('\n'.join(err_msg)))


def node_validate(ctx: typer.Context, node: str) -> str:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    try:
        proxmox_api.node.get(node)
    except ProxmoxNodeNotFoundError as err:
        raise typer.BadParameter(f'Node {node} does not exist.') from err
    return node
