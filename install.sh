#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
USER_HOME=${HOME:?HOME is required}
INSTALL_ROOT="${USER_HOME}/.local/share/humain-omarchypi"
SERVICE_NAME=humain-omarchy-context.service
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[[ "$(uname -m)" == "aarch64" ]] || fail "Raspberry Pi ARM64 only; detected $(uname -m)"
command -v python3 >/dev/null || fail "python3 is required"
command -v curl >/dev/null || fail "curl is required"
[[ -d "${USER_HOME}/.local/share/omarchy" ]] || fail "Omarchy checkout not found at ~/.local/share/omarchy"
[[ -x "${USER_HOME}/.local/bin/quickshell" ]] || fail "ARM64 Quickshell not found at ~/.local/bin/quickshell"

mkdir -p "$INSTALL_ROOT" "${USER_HOME}/.config/systemd/user" "${USER_HOME}/.config/omarchy/bar/modules" "${USER_HOME}/.local/bin"
cp -a "$REPO_ROOT/src" "$REPO_ROOT/omarchy" "$REPO_ROOT/systemd" "$INSTALL_ROOT/"

service_path="${USER_HOME}/.config/systemd/user/${SERVICE_NAME}"
cat > "$service_path" <<EOF
[Unit]
Description=HumAIn Omarchy local public-pointer context adapter
After=network.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_ROOT}
ExecStart=/usr/bin/python3 ${INSTALL_ROOT}/omarchy/context_server.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
EOF

cp -a "$REPO_ROOT/omarchy/quickshell-humain/custom-humain.qml" "${USER_HOME}/.config/omarchy/bar/modules/humain.qml"

# Install a user-owned resolver only when the platform has no resolver.
if ! command -v xdg-terminal-exec >/dev/null 2>&1; then
  cp -a "$REPO_ROOT/omarchy/quickshell-humain/xdg-terminal-exec" "${USER_HOME}/.local/bin/xdg-terminal-exec"
  chmod 755 "${USER_HOME}/.local/bin/xdg-terminal-exec"
fi

# Add the direct QML module once, preserving a timestamped backup.
shell_config="${USER_HOME}/.config/omarchy/shell.json"
[[ -f "$shell_config" ]] || fail "Omarchy shell config not found at $shell_config"
cp -a "$shell_config" "${shell_config}.bak.${TIMESTAMP}-humain-omarchypi"
python3 - "$shell_config" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
bar = data.setdefault("bar", {})
layout = bar.setdefault("layout", {})
for section in ("left", "center", "right"):
    layout[section] = [item for item in layout.get(section, []) if item.get("id") != "leo.humain"]
layout.setdefault("right", []).insert(0, {
    "id": "leo.humain",
    "type": "qml",
    "source": "~/.config/omarchy/bar/modules/humain.qml",
})
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY

# If the stock config points at missing Kitty, use the installed resolver.
hypr_config="${USER_HOME}/.config/hypr/hyprland.conf"
if [[ -f "$hypr_config" ]] && grep -q '^\$terminal = kitty$' "$hypr_config"; then
  cp -a "$hypr_config" "${hypr_config}.bak.${TIMESTAMP}-humain-terminal"
  python3 - "$hypr_config" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
s = s.replace("$terminal = kitty", "$terminal = %s/.local/bin/xdg-terminal-exec" % Path.home(), 1)
p.write_text(s)
PY
fi

systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"

# Reload if available; a login/reboot is not required for the service.
if command -v omarchy-shell >/dev/null 2>&1; then
  omarchy-shell shell reloadConfig >/dev/null 2>&1 || true
fi

printf 'Installed HumAIn OmarchyPi at %s\n' "$INSTALL_ROOT"
printf 'Service: %s\n' "$(systemctl --user is-active "$SERVICE_NAME")"
printf 'Health: '
curl -fsS http://127.0.0.1:8787/healthz
printf '\nNext: run %s/omarchy/humain-demo\n' "$INSTALL_ROOT"
