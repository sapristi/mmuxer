# Services

This folder contains files that can be used to run mmuxer as a service:

## Docker

The [Dockerfile](./Dockerfile) can be used to create a docker image (yeah it's pretty simple).
Note that docker secrets can be used for the settings values (like `password`).

## Systemd

The [mmuxer-user.service](./mmuxer-user.service) file can be used to run mmuxer as a user systemd service, by placing it in `~/.config/systemd/user/mmuxer.service`. It expects to find the configuration file at `~/.config/mmuxer/config.yaml`.

Alternatively [mmuxer-user.service](./mmuxer-user.service) file can be used to run mmuxer as a user systemd service, by placing it in `/etc/systemd/systemd/system/mmuxer.service`. It expects to find the configuration file at `/etc/mmuxer/config.yaml`.

Note that using [`systemd-creds`](https://www.freedesktop.org/software/systemd/man/systemd-creds.html) might be a nice addition to store the password, but it isn't widely available yet.
