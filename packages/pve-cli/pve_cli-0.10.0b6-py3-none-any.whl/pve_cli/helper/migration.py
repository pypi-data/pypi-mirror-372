import time

from proxmoxer import ResourceException
from rich.progress import Progress, TaskID

from .ui import spinner_col, text_col
from ..proxmox import Proxmox
from ..util.constants import PARALLEL_MIGRATION_DEFAULT
from ..util.exceptions import PVECLIMigrationCheckError, PVECLIMigrationError


def check_vm_migrate(proxmox_api: Proxmox, vm: dict, dest_node: str) -> dict:
    try:
        migrate_check_result = proxmox_api.vm.migrate_check(node=vm['node'], vm_id=vm['vmid'], target=dest_node)
    except ResourceException as err:
        raise PVECLIMigrationCheckError(f'Can not migrate VM {vm["name"]} ({vm["vmid"]}): {err.content}') from err

    # check for local disks. if they have a replication on the destination node, the vm can be migrated, else throw an error.
    if migrate_check_result['local_disks']:
        local_disks_without_replication = [
            f'{disk["drivename"]} ({disk["volid"]})' for disk in migrate_check_result['local_disks'] if disk['replicate'] == 0
        ]
        local_disks_with_replication = [
            f'{disk["drivename"]} ({disk["volid"]})' for disk in migrate_check_result['local_disks'] if disk['replicate'] == 1
        ]
        if local_disks_without_replication:
            raise PVECLIMigrationCheckError(
                f'Can not migrate VM {vm["name"]} ({vm["vmid"]}) because of local disks'
                f' without replication: {", ".join(local_disks_without_replication)}.'
            )
        if local_disks_with_replication:
            replications = proxmox_api.vm.get_replications(node=vm['node'], vm_id=vm['vmid'])
            target_replication = [replication for replication in replications if replication['target'] == dest_node]
            if not target_replication:
                raise PVECLIMigrationCheckError(
                    f'Can not migrate VM {vm["name"]} ({vm["vmid"]}) because of disks have'
                    f' no replication to {dest_node}: {", ".join(local_disks_with_replication)}.'
                )

    # check for local resources
    if migrate_check_result['local_resources']:
        raise PVECLIMigrationCheckError(
            f'Can not migrate VM {vm["name"]} ({vm["vmid"]}) '
            f'gbecause of local resources {migrate_check_result["local_resources"]}.'
        )

    # check if the destination node is an allowed node if vm is stopped
    if vm['status'] == 'stopped' and dest_node not in migrate_check_result['allowed_nodes']:
        raise PVECLIMigrationCheckError(
            f'Can not migrate VM {vm["name"]} ({vm["vmid"]}). '
            f'Migration to {dest_node} is not allowed because of {migrate_check_result["not_allowed_nodes"][dest_node]}.'
        )

    return migrate_check_result


def check_migration_status(
    proxmox_api: Proxmox,
    rich_progress: Progress,
    dest_node: str,
    running_tasks_upids: list,
    running_tasks_map: dict[str, tuple[dict, TaskID]]
) -> bool:
    failed = False
    for upid in running_tasks_upids:
        vm, task_id = running_tasks_map[upid]
        status = proxmox_api.node.task_status(vm['node'], upid)
        if status['status'] == 'stopped':
            if status['exitstatus'] == 'OK':
                rich_progress.update(
                    task_id,
                    completed=1,
                    refresh=True,
                    description=f'[green]✅ Migrated {vm["name"]} ({vm["vmid"]}) from {vm["node"]} to {dest_node}',
                )
            else:
                rich_progress.update(
                    task_id,
                    completed=1,
                    refresh=True,
                    description=f'[red]❌ Failed migrating {vm["name"]} ({vm["vmid"]}) '
                    f'from {vm["node"]} to {dest_node}: {status["exitstatus"]}',
                )
                failed = True
            running_tasks_upids.remove(upid)
    return failed


def migrate_vms(
    api: Proxmox,
    dest_node: str,
    vmid_list: list[int],
    parallel_migrations: int = PARALLEL_MIGRATION_DEFAULT,
    with_local_disks: bool = False
) -> bool:
    migration_failed = False
    running_tasks: dict[str, tuple[dict, TaskID]] = {}
    running_tasks_list: list[str] = []
    vm_list_working_copy = vmid_list[:]  # copy list to not empty the actual list
    if parallel_migrations == 0:
        parallel_migrations = len(vm_list_working_copy)

    with Progress(spinner_col, text_col) as progress:
        while vm_list_working_copy:
            while len(running_tasks_list) < parallel_migrations and vm_list_working_copy:
                vm_id = vm_list_working_copy.pop()
                vm = api.vm.get(vm_id)

                # sometimes the api is checked to fast after reboot
                _loop_counter = 0
                while vm['status'] != 'running':
                    if _loop_counter > 30:  # this state should not exist longer than a few seconds, aborting after a minute
                        raise PVECLIMigrationError(
                            f'The VM {vm_id} is not running 60s after migration. This should not happen!'
                        )

                    time.sleep(2)
                    vm = api.vm.get(vm_id)
                    _loop_counter += 1

                upid = api.vm.migrate(
                    node=vm['node'], vm_id=vm['vmid'], target_node=dest_node, with_local_disks=with_local_disks
                )
                task_id = progress.add_task(
                    description=f'[white]🚚 Migrating {vm["name"]} ({vm["vmid"]}) from {vm["node"]} to {dest_node}...', total=1
                )
                running_tasks[upid] = (vm, task_id)
                running_tasks_list.append(upid)

            time.sleep(3)  # it is not necessary to check this to often, check migration status every 3 seconds should be fine
            migration_failed = migration_failed or check_migration_status(
                proxmox_api=api,
                rich_progress=progress,
                dest_node=dest_node,
                running_tasks_upids=running_tasks_list,
                running_tasks_map=running_tasks,
            )
            if migration_failed:
                break

        while running_tasks_list:
            time.sleep(3)  # it is not necessary to check this to often, check migration status every 3 seconds should be fine
            migration_failed = migration_failed or check_migration_status(
                proxmox_api=api,
                rich_progress=progress,
                dest_node=dest_node,
                running_tasks_upids=running_tasks_list,
                running_tasks_map=running_tasks,
            )

    return migration_failed
