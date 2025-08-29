from typing import Union

from proxmoxer import ProxmoxAPI

from .exceptions import ProxmoxConnectionError, ProxmoxError
from .node import ProxmoxNode
from .permissions import ProxmoxPermissions
from .vm import ProxmoxVM


class ProxmoxCluster:
    def __init__(self, proxmox_api: ProxmoxAPI) -> None:
        self._api = proxmox_api

    def info(self) -> dict:
        for d in self._api.cluster.status.get():
            if d['id'] == 'cluster':
                return dict(d)

        raise ProxmoxError('This should not happen! Object with id "cluster" was not found.')


class Proxmox:
    node: ProxmoxNode
    vm: ProxmoxVM
    cluster: ProxmoxCluster

    def __init__(
        self,
        host: str,
        user: str,
        realm: str,
        token_name: str,
        token_secret: str,
        verify_ssl: Union[bool, str] = True,
        **kwargs: dict,
    ) -> None:
        api = ProxmoxAPI(
            host=host, user=f'{user}@{realm}', token_name=token_name, token_value=token_secret, verify_ssl=verify_ssl, **kwargs
        )

        try:
            api.version.get()
        except ConnectionError as exc:
            raise ProxmoxConnectionError(f'Could not connect to Proxmox API at {api._backend.get_base_url()}') from exc

        self._api: ProxmoxAPI = api
        self.cluster = ProxmoxCluster(proxmox_api=api)
        self.node = ProxmoxNode(proxmox_api=api)
        self.vm = ProxmoxVM(proxmox_api=api)
        self.permissions = ProxmoxPermissions(proxmox_api=api)
