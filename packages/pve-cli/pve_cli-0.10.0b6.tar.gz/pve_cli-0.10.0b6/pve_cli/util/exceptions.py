from click import ClickException


class PVECLIError(ClickException):
    pass


class PVECLIMigrationCheckError(PVECLIError):
    pass


class PVECLIMigrationError(PVECLIError):
    pass


class InvalidConfigError(PVECLIError):
    pass
