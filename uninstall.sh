#!/usr/bin/env bash
set -euo pipefail

HOME_DIR=${HOME:?HOME is required}
INSTALL_ROOT="${HOME_DIR}/.local/share/humain-omarchypi"
SERVICE_NAME=humain-omarchy-context.service

systemctl --user disable --now "$SERVICE_NAME" 2>/dev/null || true
rm -f "${HOME_DIR}/.config/systemd/user/${SERVICE_NAME}"
systemctl --user daemon-reload 2>/dev/null || true
rm -rf "$INSTALL_ROOT"
rm -f "${HOME_DIR}/.config/omarchy/bar/modules/humain.qml"
if [[ -f "${HOME_DIR}/.local/bin/xdg-terminal-exec" ]] && grep -q "ARM-lab compatibility shim" "${HOME_DIR}/.local/bin/xdg-terminal-exec"; then
  rm -f "${HOME_DIR}/.local/bin/xdg-terminal-exec"
fi

# Deliberately preserve shell.json and Hyprland backups. Remove only our layout entry.
python3 - <<'PY'
import json
from pathlib import Path
p = Path.home() / ".config/omarchy/shell.json"
if p.exists():
    data = json.loads(p.read_text())
    for section in data.get("bar", {}).get("layout", {}).values():
        if isinstance(section, list):
            section[:] = [item for item in section if item.get("id") != "leo.humain"]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY

printf 'Removed HumAIn OmarchyPi files. Timestamped configuration backups were preserved.\n'
