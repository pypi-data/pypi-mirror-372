from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.progress import Progress

from .helper.ui import spinner_col, text_col
from .proxmox import Proxmox, ProxmoxMissingPermissionsError, ProxmoxVMNotFoundError
from .util.completion import vm_complete
from .util.exceptions import PVECLIError

guest_cli = typer.Typer()


@guest_cli.callback()
def guest_cli_callback(
    ctx: typer.Context,
    vm: Annotated[str, typer.Argument(..., autocompletion=vm_complete, help='VM Name or ID', show_default=False)],
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']

    try:
        vm_obj = proxmox_api.vm.get(vm)
    except ProxmoxVMNotFoundError:
        raise PVECLIError(f'VM {vm} was not found.') from None

    # if this is failing we can't even read the name of the vm
    try:
        proxmox_api.permissions.check_vm_read(f'/vms/{vm_obj["vmid"]}')
    except ProxmoxMissingPermissionsError as exc:
        raise PVECLIError(f'Missing permission for VM-Management ({exc.path}): {", ".join(exc.permissions)}') from None

    # check if we have all required permissions
    try:
        proxmox_api.permissions.check_guest_cmd(f'/vms/{vm_obj["vmid"]}')
    except ProxmoxMissingPermissionsError as exc:
        raise PVECLIError(f'Missing permission for VM {vm_obj["name"]} ({exc.path}): {", ".join(exc.permissions)}') from None

    ctx.obj['vm'] = vm_obj


@guest_cli.command()
def start(ctx: typer.Context, command: Annotated[list[str], typer.Argument()]) -> None:
    """Start command on guest"""
    pid = _execute(proxmox_api=ctx.obj['proxmox_api'], vm=ctx.obj['vm'], command=' '.join(command))
    rprint(f'[blue]PID: [green]{pid}')


@guest_cli.command()
def run(ctx: typer.Context, command: Annotated[list[str], typer.Argument()]) -> None:
    """Execute command on guest and return output.

    Exits with the exitcode of the command inside the VM."""
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vm = ctx.obj['vm']
    pid = _execute(proxmox_api=proxmox_api, vm=vm, command=' '.join(command))
    result = proxmox_api.vm.agent.check_exec_status(node=vm['node'], vm_id=vm['vmid'], pid=pid)
    if result['out_data']:
        rprint(result['out_data'])
    raise typer.Exit(code=result['exitcode'])


@guest_cli.command()
def upload(
    ctx: typer.Context,
    source: Annotated[
        Path,
        typer.Argument(
            help='Path of the source file. Use "-" to read from stdin.',
            exists=True,
            dir_okay=False,
            resolve_path=True,
            allow_dash=True,
        ),
    ],
    destination: Annotated[
        Path, typer.Argument(help='Path of the destination file inside the guest.', exists=False, readable=False)
    ],
) -> None:
    """Upload file to guest"""
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vm = ctx.obj['vm']

    with typer.open_file(str(source), mode='rb') as source_stream:
        source_file = source_stream.read()

    with Progress(spinner_col, text_col) as progress:
        task_id = progress.add_task(
            description=f'[white]📤 Uploading {source} to {destination} on {vm["name"]} ({vm["vmid"]})...', total=1
        )
        proxmox_api.vm.agent.file_write(node=vm['node'], vm_id=vm['vmid'], file_path=destination, content=source_file)
        progress.update(
            task_id,
            completed=1,
            refresh=True,
            description=f'[green]✅ Uploaded {source} to {destination} on {vm["name"]} ({vm["vmid"]})',
        )


def _execute(proxmox_api: Proxmox, vm: dict, command: str) -> int:
    rprint(f'[blue]Starting {command} on {vm["name"]} ({vm["vmid"]})')
    return proxmox_api.vm.agent.execute(node=vm['node'], vm_id=vm['vmid'], command=command)
