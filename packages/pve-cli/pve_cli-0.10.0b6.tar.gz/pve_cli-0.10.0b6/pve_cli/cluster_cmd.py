import json
import tempfile
import time
from datetime import timedelta
from typing import Annotated

import typer
from rich import box
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, TimeElapsedColumn
from rich.table import Table

from .helper.conversion import b2gb
from .helper.migration import check_vm_migrate, migrate_vms
from .helper.ui import spinner_col, text_col, usage_bar
from .proxmox import Proxmox
from .util.constants import PARALLEL_MIGRATION_DEFAULT, PARALLEL_MIGRATION_TYPE
from .util.exceptions import PVECLIError, PVECLIMigrationCheckError

cluster_cli = typer.Typer()
vm_mapping_cli = typer.Typer()
cluster_cli.add_typer(vm_mapping_cli, name='vm-mapping')


@cluster_cli.callback()
def cluster_cli_callback(
    ctx: typer.Context,
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    ctx.obj['nodes'] = proxmox_api.node.list_()
    ctx.obj['cluster'] = proxmox_api.cluster.info()


def try_migration_rescue_dump(
    api: Proxmox, dest_node: str, vmid_list: list[int], parallel_migrations: int, with_local_disks: bool, vms_all: list
) -> None:
    migration_failed = migrate_vms(
        api=api,
        dest_node=dest_node,
        vmid_list=vmid_list,
        parallel_migrations=parallel_migrations,
        with_local_disks=with_local_disks,
    )
    if migration_failed:
        with tempfile.NamedTemporaryFile(mode='wt', delete=False, prefix='pve-cli', suffix='.json') as tmpfile:
            json.dump({vm['vmid']: vm['node'] for vm in vms_all}, tmpfile, indent=2)
            raise PVECLIError(f'Migration failed. Aborting cluster reboot. Initial VM-Mapping has been saved to {tmpfile.name}')


@cluster_cli.command()
def reboot(
    ctx: typer.Context,
    restore_vm_mapping: Annotated[
        bool, typer.Option('--restore-vm-mapping', help='Restore VMs to their original node after it has rebooted.')
    ] = False,
    parallel_migrations: PARALLEL_MIGRATION_TYPE = PARALLEL_MIGRATION_DEFAULT,
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    nodes = ctx.obj['nodes']

    if len(nodes) < 2:
        raise PVECLIError('This command requires at least two nodes to work.')

    vms_all = proxmox_api.vm.list_()
    node_migration_map = {nodes[i]['node']: nodes[i - 1]['node'] for i in range(len(nodes))}

    first_node = nodes[0]['node']
    penultimate_node = nodes[-2]['node']
    last_node = nodes[-1]['node']
    nodes_vms_to_migrate_map = {
        node_data['node']: [
            vm
            for vm in vms_all
            if vm['status'] == 'running' and 'do-not-migrate' not in vm.get('tags', []) and vm['node'] == node_data['node']
        ]
        for node_data in nodes
    }
    with_local_disks = False

    # check if all migrations would be possible
    migration_blockers = []
    for node, vms_to_migrate in nodes_vms_to_migrate_map.items():
        if (not restore_vm_mapping) and node == first_node:
            # if we are NOT restoring vms to their original node: the vms from node 1 will be migrated to node n and node n-1
            dest_nodes = [penultimate_node, last_node]
        else:
            dest_nodes = [node_migration_map[node]]

        for dest_node in dest_nodes:
            for vm in vms_to_migrate:
                try:
                    migration_check_result = check_vm_migrate(proxmox_api=proxmox_api, vm=vm, dest_node=dest_node)
                    if migration_check_result['local_disks']:
                        with_local_disks = True
                except PVECLIMigrationCheckError as err:
                    migration_blockers.append(err)

    if migration_blockers:
        raise PVECLIError(
            'Can not automatically reboot cluster because running VM(s) are not online-migration ready:\n'
            + '\n'.join([blocker.message for blocker in migration_blockers])
        )

    for node_data in nodes:
        node = node_data['node']
        dest_node = node_migration_map[node]
        if (not restore_vm_mapping) and node == last_node:
            # if we are NOT restoring vms to their original node: on node n are currently running the vms from node 1 and node n
            vms_to_migrate = nodes_vms_to_migrate_map[node] + nodes_vms_to_migrate_map[first_node]
        else:
            vms_to_migrate = nodes_vms_to_migrate_map[node]

        try_migration_rescue_dump(
            proxmox_api, dest_node, [vm['vmid'] for vm in vms_to_migrate], parallel_migrations, with_local_disks, vms_all
        )

        with Progress(spinner_col, TimeElapsedColumn(), text_col) as progress:
            task_id = progress.add_task(description=f'[white]Rebooting {node}...', total=1)
            proxmox_api.node.reboot(node)
            # wait for node to go offline
            while proxmox_api.node.get(node)['status'] == 'online':
                time.sleep(10)  # it is not necessary to check this to often, check node status every 10 seconds should be fine
            # wait for node to come online
            while proxmox_api.node.get(node)['status'] != 'online':
                time.sleep(10)  # it is not necessary to check this to often, check node status every 10 seconds should be fine
            progress.update(task_id, completed=1, refresh=True, description=f'[green]Done: Rebooted {node}')

        # if we are restoring vms to their original node: bring vms back to their original node
        if restore_vm_mapping:
            try_migration_rescue_dump(
                proxmox_api, node, [vm['vmid'] for vm in vms_to_migrate], parallel_migrations, with_local_disks, vms_all
            )

    # if we are NOT restoring vms to their original node: migrate vms from first node to empty node
    if not restore_vm_mapping:
        # move vms from node 1 currently running on node n-1 to node n
        first_node_vms = nodes_vms_to_migrate_map[first_node]
        try_migration_rescue_dump(
            proxmox_api, last_node, [vm['vmid'] for vm in first_node_vms], parallel_migrations, with_local_disks, vms_all
        )


@cluster_cli.command('list')
def list_(ctx: typer.Context) -> None:
    cluster = ctx.obj['cluster']
    nodes = ctx.obj['nodes']

    table = Table(title=f'Nodes in cluster {cluster["name"]}', box=box.ROUNDED)
    table.add_column('Node')
    table.add_column('Status', justify='center')
    table.add_column('Cores', justify='right')
    table.add_column('CPU Usage')
    table.add_column('RAM')
    table.add_column('RAM Usage')
    table.add_column('Disk Usage')
    table.add_column('Uptime')

    for node in nodes:
        online = node['status'] == 'online'
        status = '🚀 online' if online else f'💀 {node["status"]}'
        ram = int(b2gb(node['maxmem'])) if online else 'N/A'
        cpu_bar = usage_bar(node['cpu']) if online else 'N/A'
        ram_bar = usage_bar(node['mem'] / node['maxmem']) if online else 'N/A'
        disk_bar = usage_bar(node['disk'] / node['maxdisk']) if online else 'N/A'

        table.add_row(
            node['node'],
            status,
            str(node['maxcpu']) if online else 'N/A',
            cpu_bar,
            f'{ram} GiB' if online else 'N/A',
            ram_bar,
            disk_bar,
            str(timedelta(seconds=node['uptime'])) if online else 'N/A',
        )

    console = Console()
    console.print(table)


@vm_mapping_cli.command('dump')
def mapping_dump(
    ctx: typer.Context,
    outfile: Annotated[typer.FileTextWrite, typer.Argument(help='JSON output filepath')],
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vms = proxmox_api.vm.list_()

    result = {vm['vmid']: vm['node'] for vm in vms}
    json.dump(result, outfile, indent=2)


@vm_mapping_cli.command('restore')
def mapping_restore(
    ctx: typer.Context,
    infile: Annotated[typer.FileText, typer.Argument(help='JSON input file (created with dump-vms')],
    verbose: Annotated[bool, typer.Option('--verbose', '-v', help='Verbose output')] = False,
    force: Annotated[bool, typer.Option('--force', '-f', help='Force VM migration')] = False,
    parallel_migrations: PARALLEL_MIGRATION_TYPE = PARALLEL_MIGRATION_DEFAULT,
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vms = proxmox_api.vm.list_()
    nodes = ctx.obj['nodes']

    mapping = json.load(infile)

    migration_vms: dict[str, list[dict]] = {node['node']: [] for node in nodes}
    for vm in vms:
        try:
            wanted_node = mapping[str(vm['vmid'])]
        except KeyError:
            continue

        if wanted_node == vm['node']:
            if verbose:
                rprint(spinner_col.finished_text, f'[green]✅ VM {vm["name"]} ({vm["vmid"]}) is on node {wanted_node}')
        else:
            migration_vms[wanted_node].append(vm)

    for dest_node, vms_to_migrate in migration_vms.items():
        if vms_to_migrate:
            with_local_disks = False
            for vm in vms_to_migrate:
                if 'do-not-migrate' in vm.get('tags', []) and not force:
                    rprint(
                        spinner_col.finished_text,
                        f'[red]❌ VM {vm["name"]} ({vm["vmid"]}) was not migrated because of "do-not-migrate" tag. '
                        f'Use --force to migrate anyways.',
                    )
                    vms_to_migrate.remove(vm)
                    continue

                migration_check_result = check_vm_migrate(proxmox_api=proxmox_api, dest_node=dest_node, vm=vm)
                if migration_check_result['local_disks']:
                    with_local_disks = True

            migrate_vms(
                api=proxmox_api,
                dest_node=dest_node,
                vmid_list=[vm['vmid'] for vm in vms_to_migrate],
                parallel_migrations=parallel_migrations,
                with_local_disks=with_local_disks,
            )
