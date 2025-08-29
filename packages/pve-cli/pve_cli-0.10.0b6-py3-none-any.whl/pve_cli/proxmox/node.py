from operator import itemgetter

from proxmoxer import ProxmoxAPI

from .exceptions import (
    ProxmoxNodeNotFoundError,
)


class ProxmoxNode:
    def __init__(self, proxmox_api: ProxmoxAPI) -> None:
        self._api = proxmox_api

    def list_(self) -> list:
        nodes = self._api.nodes.get()
        return sorted(nodes, key=itemgetter('node'))

    def get(self, node: str) -> dict:
        nodes = self.list_()
        for node_dict in nodes:
            if node_dict['node'] == node:
                return dict(node_dict)
        raise ProxmoxNodeNotFoundError(f'Node {node} was not found.')

    def reboot(self, node: str) -> None:
        self._api.nodes(node).status.post(command='reboot')

    def task_status(self, node: str, upid: str) -> dict:
        status = self._api.nodes(node).tasks(upid).status.get()
        return dict(status)
