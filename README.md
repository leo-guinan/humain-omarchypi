# HumAIn OmarchyPi

A reproducible, ARM64 Raspberry Pi 5 integration for a bounded HumAIn public-pointer indicator inside an Omarchy-inspired Manjaro ARM desktop.

This is an experimental ARM lab, not official Omarchy support. It assumes:

- Raspberry Pi 5 running 64-bit Manjaro ARM
- native Hyprland and UWSM
- ARM64 Quickshell installed at `~/.local/bin/quickshell`
- Omarchy checkout at `~/.local/share/omarchy`
- a normal user session; no root SSH is required

## What it installs

- loopback-only HumAIn context service at `127.0.0.1:8787`
- public-only HTTPS pointer resolver
- direct Quickshell bar module showing `◉ HumAIn`
- reproducible terminal demo
- Foot resolver shim when `xdg-terminal-exec` is absent
- idempotent user-systemd setup
- timestamped backups of shell and Hyprland configuration before edits

It does not install Omarchy, replace the OS, read browser history, read cookies, inspect page text, read clipboard contents, accept credentials, or expose a network listener beyond loopback.

## Install on another Pi

There are two supported paths.

### Path A: bootstrap a fresh Manjaro ARM Pi

Start from a verified 64-bit Manjaro ARM image, boot the Pi, and clone this repository. Then run:

```bash
chmod +x bootstrap/prepare-node.sh
./bootstrap/prepare-node.sh
```

This installs the ARM-compatible desktop/build prerequisites, clones Omarchy if needed, builds ARM64 Quickshell with `CRASH_HANDLER=OFF` when Quickshell is absent, installs the HumAIn layer, and enables the first-boot identity service. It never writes an SD card and never enrolls the node into a coordinator.

### Path B: install the HumAIn layer on an already-prepared OmarchyPi

Clone or copy this repository to the Pi, then run:

```bash
chmod +x install.sh
./install.sh
```

The installer fails closed unless it detects `aarch64`, Python 3, curl, an Omarchy checkout, and ARM64 Quickshell. Install those graphical prerequisites separately; the installer does not blindly mix repositories or run the x86_64 Omarchy installer.

After installation:

```bash
systemctl --user status humain-omarchy-context.service --no-pager
curl -fsS http://127.0.0.1:8787/healthz
~/.local/share/humain-omarchypi/omarchy/humain-demo
```

The current Omarchy lab uses `Super+Q` to open the terminal. On an Apple keyboard, this is usually `Command+Q`; on a Windows/Linux keyboard, use the Windows key plus Q. The exact modifier depends on the keyboard mapping.

## Validate a node

After bootstrap and reboot, run the target-side acceptance probe:

```bash
./bootstrap/validate-node.sh
```

It checks architecture, Manjaro ARM, native desktop packages, Quickshell, the shell module, the loopback service, the public-only demo, first-boot service state, and node identity. It does not claim a physical image or second-node pass by itself.

## First bounded swarm layer

The first swarm artifact is a typed health receipt under `swarm/`. It reports node capability and service health only. It does not provide remote execution, desktop control, browser surveillance, credential distribution, or automatic mutation. See `swarm/README.md` and `docs/OMARCHYPI-NODE-ARCHITECTURE.md`.

## Uninstall

```bash
chmod +x uninstall.sh
./uninstall.sh
```

Uninstall removes the service, installed source, QML module, and HumAIn layout entry. It preserves timestamped configuration backups rather than guessing which prior state should be restored.

## Boundary contract

Accepted:

```text
https://example.com/path
```

Rejected:

```text
http://example.com/path
file:///private/file
https://example.com/path?token=secret
https://example.com/path#private
```

A valid response is explicitly:

```text
resolution_state: public_only
private_context: false
actions: []
```

The `demo:unsigned` signature is an adapter marker, not authentication or proof of publisher truth.

## Demo

The demo performs three real requests:

1. loopback health check
2. valid public-pointer resolution with provenance
3. query-string rejection, expected HTTP 422

The final `PASS` means those bounded behaviors ran on the Pi. It does not mean the pointer publisher was authenticated or that private context was accessed.

## Repository layout

```text
src/humain_api/omarchy_context.py  bounded resolver
omarchy/context_server.py          loopback HTTP adapter
omarchy/humainctl.py               CLI / Waybar-compatible adapter
omarchy/humain-demo                evidence-producing demo
omarchy/quickshell-humain/         bar module and terminal shim
omarchy/extension/                 optional explicit-activation browser lens
systemd/                           service template
install.sh                         idempotent ARM-aware installer
uninstall.sh                       reversible removal
 tests/                             boundary and artifact tests
```

## Verification

On a development machine:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile src/humain_api/omarchy_context.py omarchy/context_server.py omarchy/humainctl.py
node --check omarchy/extension/background.js
node --check omarchy/extension/content.js
node --check omarchy/extension/popup.js
```

On a Pi, the strongest receipt is the output of `omarchy/humain-demo` plus the visible `HumAIn` bar indicator.

## Privacy and safety

Keep private data and secrets out of this repository. Do not commit Wi-Fi credentials, SSH keys, provider tokens, browser exports, cookies, screenshots containing private data, or user-specific databases. The Pi adapter is intentionally narrow: a clean public pointer in, a public metadata envelope out, no actions.
