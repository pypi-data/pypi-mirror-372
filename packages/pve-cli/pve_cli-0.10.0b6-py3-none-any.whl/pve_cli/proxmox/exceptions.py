class ProxmoxError(Exception):
    pass


class ProxmoxConnectionError(ProxmoxError):
    pass


class ProxmoxVMNotFoundError(ProxmoxError):
    pass


class ProxmoxNodeNotFoundError(ProxmoxError):
    pass


class ProxmoxMissingPermissionsError(ProxmoxError):
    def __init__(self, path: str, permissions: list[str]) -> None:
        super().__init__(f'Missing permission for "{path}": {", ".join(permissions)}')
        self.path = path
        self.permissions = permissions


class ProxmoxVMIDExistsError(ProxmoxError):
    pass
