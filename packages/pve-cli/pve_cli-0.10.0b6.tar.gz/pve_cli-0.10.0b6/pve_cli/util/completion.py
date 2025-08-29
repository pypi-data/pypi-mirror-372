from collections.abc import Iterator

import typer

from ..proxmox.api import Proxmox


def endpoint_complete(ctx: typer.Context, incomplete: str) -> Iterator[tuple[str, str]]:
    config = ctx.obj['config']
    endpoints = config.get('endpoint', {})
    for endpoint in endpoints:
        if endpoint.startswith(incomplete):
            yield endpoint, endpoints[endpoint]['host']


def vm_complete(ctx: typer.Context, incomplete: str) -> Iterator[tuple[str, str]]:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vms = proxmox_api.vm.list_()

    for vm in vms:
        yield str(vm['vmid']), vm['name']
        yield vm['name'], vm['name']


def node_complete(ctx: typer.Context, incomplete: str) -> Iterator[tuple[str, str]]:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    nodes = proxmox_api.node.list_()

    for node in nodes:
        if node['node'].startswith(incomplete):
            yield node['node'], node['node']
