import packaging.version
from proxmoxer import ProxmoxAPI

from .exceptions import ProxmoxMissingPermissionsError


class ProxmoxPermissions:
    def __init__(self, proxmox_api: ProxmoxAPI) -> None:
        self._api = proxmox_api
        self._release = packaging.version.parse(proxmox_api.version.get()['release'])

    def check(self, path: str, permissions: list[str]) -> None:
        existing_permissions = self._api.access.permissions.get(path=path)[path]
        missing_permissions = []
        for permission in permissions:
            if permission not in existing_permissions:
                missing_permissions.append(permission)
        if missing_permissions:
            raise ProxmoxMissingPermissionsError(path, missing_permissions)


    @property
    def vm_read(self) -> list[str]:
        return ['VM.Audit']

    @property
    def guest_cmd(self) -> list[str]:
        # before proxmox 9 this was VM.Monitor
        if self._release < packaging.version.Version('9.0'):
            return ['VM.Monitor']

        return ['VM.GuestAgent.Unrestricted']

    def check_vm_read(self, path: str) -> None:
        self.check(path, self.vm_read)

    def check_guest_cmd(self, path: str) -> None:
        self.check(path, self.guest_cmd)
