#!/usr/bin/env bash
set -euo pipefail

# Prepare a Manjaro ARM Raspberry Pi for the HumAIn OmarchyPi layer.
# This script never writes removable media. It installs software on the current Pi.

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ "$(uname -m)" == "aarch64" ]] || fail "aarch64 required; detected $(uname -m)"
[[ -f /etc/os-release ]] && . /etc/os-release
[[ ${ID:-} == manjaro-arm ]] || fail "Manjaro ARM required; detected ${ID:-unknown}"
command -v pacman >/dev/null || fail "pacman required"
command -v sudo >/dev/null || fail "sudo required for package installation"

OMARCHY_DIR="${OMARCHY_DIR:-$HOME/.local/share/omarchy}"
QUICKSHELL_DIR="${QUICKSHELL_DIR:-$HOME/src/quickshell}"
REPO_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

printf '%s\n' 'Installing ARM-compatible desktop/build prerequisites.'
sudo pacman -S --needed \
  git curl python cmake ninja pkgconf base-devel \
  hyprland uwsm xdg-desktop-portal-hyprland \
  qt6-base qt6-declarative qt6-wayland qt6-shadertools qt6-svg \
  libdrm cli11 vulkan-headers spirv-tools jemalloc \
  foot xdg-utils inotify-tools

if [[ ! -d "$OMARCHY_DIR/.git" ]]; then
  git clone https://github.com/basecamp/omarchy.git "$OMARCHY_DIR"
fi

if [[ ! -x "$HOME/.local/bin/quickshell" ]]; then
  mkdir -p "$(dirname "$QUICKSHELL_DIR")"
  [[ -d "$QUICKSHELL_DIR/.git" ]] || git clone --depth 1 https://git.outfoxxed.me/quickshell/quickshell.git "$QUICKSHELL_DIR"
  cmake -GNinja -B "$QUICKSHELL_DIR/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$HOME/.local" \
    -DCRASH_HANDLER=OFF \
    "$QUICKSHELL_DIR"
  cmake --build "$QUICKSHELL_DIR/build"
  cmake --install "$QUICKSHELL_DIR/build"
fi

printf '%s\n' 'Installing HumAIn OmarchyPi user layer.'
"$REPO_DIR/install.sh"

printf '%s\n' 'Installing first-boot node identity service.'
sudo install -d -m 0755 /usr/local/lib/omarchypi /var/lib/omarchypi
sudo install -m 0644 "$REPO_DIR/bootstrap/node_identity.py" /usr/local/lib/omarchypi/node_identity.py
sudo install -m 0755 "$REPO_DIR/bootstrap/first-boot-node.py" /usr/local/lib/omarchypi/first-boot-node.py
sudo install -m 0644 "$REPO_DIR/bootstrap/omarchypi-first-boot.service" /etc/systemd/system/omarchypi-first-boot.service
sudo systemctl daemon-reload
sudo systemctl enable omarchypi-first-boot.service

printf '%s\n' 'Bootstrap complete. Reboot once, then verify:'
printf '%s\n' '  systemctl status omarchypi-first-boot.service --no-pager'
printf '%s\n' '  cat /var/lib/omarchypi/node.json'
printf '%s\n' '  ~/.local/share/humain-omarchypi/omarchy/humain-demo'
