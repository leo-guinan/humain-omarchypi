#!/usr/bin/env bash
set -euo pipefail

fail=0
check() {
  local name=$1; shift
  if "$@" >/dev/null 2>&1; then printf 'PASS %s\n' "$name"; else printf 'FAIL %s\n' "$name"; fail=1; fi
}

check architecture test "$(uname -m)" = aarch64
check manjaro-arm sh -c '. /etc/os-release && test "${ID:-}" = manjaro-arm'
check hyprland pacman -Q hyprland
check uwsm pacman -Q uwsm
check foot pacman -Q foot
check quickshell test -x "$HOME/.local/bin/quickshell"
check shell-config test -s "$HOME/.config/omarchy/shell.json"
check bar-module test -s "$HOME/.config/omarchy/bar/modules/humain.qml"
check context-service systemctl --user is-active humain-omarchy-context.service
check context-health curl --max-time 10 -fsS http://127.0.0.1:8787/healthz
check demo "$HOME/.local/share/humain-omarchypi/omarchy/humain-demo"
check node-identity test -s /var/lib/omarchypi/node.json
check first-boot systemctl is-enabled omarchypi-first-boot.service

if (( fail )); then
  printf 'VALIDATION FAIL\n' >&2
  exit 1
fi
printf 'VALIDATION PASS\n'
