# Netbox Sync Status

Netbox Sync Status is a [NetBox](https://github.com/netbox-community/netbox) plugin that adds the capability for systems to report back to netbox if a given sync went well.
One usecase is when using webhooks to sync database to other systems like, backup, aaa, dns it's possible to report the status back to netbox.

It works by having the user create a number of `Sync Systems` and assign what object types they can be used on, each sync system can then report back a `Sync Status`, so that users will be able to see how it went. 

A full log of how all sync's went is saved so you can go back in history and view errors if needed.

If needed it's also possible to run a re-sync for an update, behind the scenes this will trigger and update event, and netbox will automatically call the needed webhooks.

API's are available to report sync status back, and other general functions that might be needed.

## Compatibility

This plugin in compatible with [NetBox](https://netbox.readthedocs.org/) 4.1 and later.

## Installation

If Netbox was installed according to the standard installation instructions. It may be necessary to activate the virtual environment.

```
source /opt/netbox/venv/bin/activate
```

The plugin is available as a Python package in pypi and can be installed with pip

```
pip install netbox-sync-status
```
Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:
```
PLUGINS = ["netbox-sync-status"]
```
Restart NetBox and add `netbox-sync-status` to your local_requirements.txt

## Screenshots
<p align="middle">
    <img align="top" src="/screenshots/sync_status_list.png?raw=true" width="32%" />
    <img align="top" src="/screenshots/sync_status_list.png?raw=true" width="32%" /> 
    <img align="top" src="/screenshots/sync_system_view.png?raw=true" width="32%" />
</p>


## Contributing
Developing tools for this project based on [ntc-netbox-plugin-onboarding](https://github.com/networktocode/ntc-netbox-plugin-onboarding) repo.

Issues and pull requests are welcomed.
