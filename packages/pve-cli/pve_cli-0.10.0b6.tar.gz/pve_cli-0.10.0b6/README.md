# pve-cli

CLI Tool to manage VMs and more on proxmox clusters

## Features

### Prevent migration

Migration of a VM by pve-cli can be prevented if the tag `do-not-migrate` is added to the VM. The migration of VMs with this tags can be forced with `--force`.
This is implemented for the commands `pve-cli vm VM migrate`, `pve-cli cluster reboot` and `pve-cli cluster vm-mapping restore`.

## Config

For config option reference see `config.example.toml`.
The config file path can be provided via command line option `--config`/`-c` and is searched by default in the following
paths:

* Linux (Unix): `~/.config/pve-cli/config.toml`
* MacOS: `~/Library/Application Support/pve-cli/config.toml`
* Windows: `C:\Users\<user>\AppData\Local\pve-cli\config.toml`

This leverages the [`get_app_dir`](https://click.palletsprojects.com/en/8.1.x/api/#click.get_app_dir) method
from [`click`](https://click.palletsprojects.com).

## Required PVE Permissions

For full functionallity following permissions are required:
* `Sys.Audit`
* `Sys.PowerMgmt`
* `VM.Audit`
* `VM.GuestAgent.Unrestricted`
* `VM.Migrate`
* `VM.PowerMgmt`

With the following line in `/etc/pve/user.cfg` you can create a role `CLI-Tool`:
```
role:CLI-Tool:Sys.Audit,Sys.PowerMgmt,VM.Audit,VM.GuestAgent.Unrestricted,VM.Migrate,VM.PowerMgmt:
```

Until PVE 9 instead of `VM.GuestAgent.Unrestricted` the permission `VM.Monitor` was needed.