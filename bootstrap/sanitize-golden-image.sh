#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  printf 'Run as root on the image before first boot.\n' >&2
  exit 1
fi
if [[ ${OMARCHYPI_SANITIZE_CONFIRM:-} != YES ]]; then
  printf 'DRY RUN. Set OMARCHYPI_SANITIZE_CONFIRM=YES to remove machine identity and private image state.\n'
  printf 'This removes SSH host keys, machine-id, logs, DHCP leases, node identity, and user authorized_keys.\n'
  exit 0
fi

rm -f /etc/ssh/ssh_host_* 2>/dev/null || true
truncate -s 0 /etc/machine-id
rm -f /var/lib/dbus/machine-id
rm -rf /var/log/journal/* /var/lib/systemd/coredump/* 2>/dev/null || true
rm -f /var/lib/systemd/network/*lease* /var/lib/dhcpcd5/*lease* 2>/dev/null || true
rm -rf /var/lib/omarchypi

for home in /home/*; do
  [[ -d "$home" ]] || continue
  rm -f "$home/.bash_history" "$home/.zsh_history"
  rm -f "$home/.ssh/authorized_keys"
done

rm -f /etc/hostname
printf 'omarchypi-baseline\n' > /etc/hostname
printf 'sanitized; first-boot identity service must run on next boot\n'
