# Ansible Infrastructure

This directory contains the server-side automation for Xray nodes used by the Android app.

The repository stores only safe templates.
Do not commit real server IPs, passwords, UUIDs, or REALITY private keys.

## Layout

- `ansible.cfg`: local Ansible defaults
- `inventory/hosts.yml.example`: sample inventory
- `inventory/group_vars/vpn_nodes.yml.example`: sample shared variables
- `playbooks/ping.yml`: connectivity check
- `playbooks/bootstrap.yml`: Python bootstrap and host facts
- `playbooks/site.yml`: full Xray deployment
- `roles/xray/`: Xray installation and configuration role

## Local setup

1. Copy `inventory/hosts.yml.example` to `inventory/hosts.yml`
2. Copy `inventory/group_vars/vpn_nodes.yml.example` to `inventory/group_vars/vpn_nodes.yml`
3. Fill in your real server addresses and Xray credentials
4. Run `ansible-playbook playbooks/ping.yml -k`
5. Run `ansible-playbook playbooks/site.yml -k`

## Notes

- `-k` is required when SSH access uses a password
- If `sudo` prompts for a password, add `-K`
- The role assumes a Debian-based Linux host with `systemd`
