# OmarchyPi Node Architecture

Status: design baseline — 2026-08-23

## Objective

Turn the verified Raspberry Pi 5 ARM lab into a repeatable OmarchyPi node that can be cloned onto new Raspberry Pis and later participate in a bounded local swarm.

The node contract is:

```text
Manjaro ARM → Hyprland/UWSM → ARM64 Quickshell → selected Omarchy shell
→ HumAIn public-only local adapter → bounded node health/identity layer
```

This is an unsupported ARM port inspired by Omarchy, not the official x86_64 Omarchy installer.

## Two deliverables, not one

### A. Golden image

A sanitized bootable image made from the verified baseline Pi.

Use it for:

- fast demonstrations
- a small controlled number of identical bench nodes
- hardware-specific Pi 5 bring-up

It must be sanitized before publication or cloning:

- remove SSH host keys
- remove user SSH authorized keys unless explicitly re-provisioned
- regenerate machine identity
- clear DHCP leases and network-specific state
- clear logs, shell history, caches, temporary files, and demo receipts
- remove the current hostname and static node identity
- preserve the Omarchy/Quickshell/HumAIn software baseline
- run a first-boot node enrollment service

The image is a delivery artifact, not the source of truth.

### B. Bootstrap installer

A source-controlled build path that starts from a verified Manjaro ARM image and installs the same layers.

It must:

1. verify `aarch64` and Raspberry Pi hardware
2. install only ARM-compatible packages
3. build or install ARM64 Quickshell with explicit `CRASH_HANDLER=OFF` if required
4. install selected Omarchy shell files and Pi-safe configuration
5. install Foot and the XDG resolver shim if required
6. install HumAIn and the loopback user service
7. configure first-boot identity generation
8. run acceptance checks
9. produce a receipt with versions, paths, service states, and boundary tests

The bootstrap path is slower but is the reproducibility and recovery path.

## Image pipeline

The image pipeline should be host-driven and non-destructive by default:

```text
verified Manjaro ARM source
  → ARM build workspace
  → package/build layer
  → first-boot provisioning layer
  → sanitization check
  → compressed image + SHA-256 + manifest
```

Do not make the Mac's current root disk or an unconfirmed removable disk a target. Any SD-card write requires fresh device identity confirmation immediately before writing.

The first implementation can use the working Pi as a read-only source for a private golden image, but the public release should be produced from a reproducible build workspace once the bootstrap path exists. A raw 119 GB clone would preserve too much dead weight and too much identity.

## First-boot node identity

Each node receives a new identity on first boot. The identity is not a secret and must not be used as an authentication credential.

Suggested local record:

```json
{
  "schema": "omarchypi.node.v1",
  "node_id": "omarchypi-<random-suffix>",
  "role": "edge-display",
  "capabilities": ["public-pointer", "quickshell-bar", "health"],
  "created_at": "<first-boot-time>",
  "network_scope": "lan-only"
}
```

The node must not auto-enroll into a remote control plane merely because it booted. Enrollment is explicit and operator-gated.

## Swarm layer: first safe version

The first swarm is a health-and-observation network, not a command-and-control network.

Allowed in v0:

- node identity announcement on the local network or to an explicitly configured coordinator
- health, version, capability, and uptime receipts
- bounded public-pointer resolution receipts
- operator-requested status collection
- offline queueing of non-sensitive health events

Not allowed in v0:

- arbitrary remote shell execution
- remote desktop control
- browser history, cookies, clipboard, page text, or filesystem surveillance
- automatic credential distribution
- automatic software mutation across nodes
- public exposure or reverse tunnels
- autonomous financial, deployment, or destructive hardware actions

A swarm message should be typed and bounded, for example:

```json
{
  "schema": "omarchypi.node.health.v1",
  "node_id": "omarchypi-abc123",
  "observed_at": "2026-08-23T00:00:00Z",
  "software": {"omarchypi": "0.1.0"},
  "capabilities": ["public-pointer", "health"],
  "health": {"context_service": "active", "desktop": "observed"},
  "network_scope": "lan-only"
}
```

The coordinator, if added, should be a separate opt-in component. The Pi remains functional when it is absent.

## Trust boundary

```text
local display shell
  → local loopback adapter
  → explicit public pointer
  → public-only metadata

optional node health
  → explicit LAN/coordinator endpoint
  → typed health receipt only
```

No private context should cross the HumAIn adapter boundary. No node should infer permission from network reachability. A node being visible on the LAN is not authorization.

## Acceptance gates for a fresh Pi

```text
G1  verified ARM image boots
G2  hardware identity and architecture are correct
G3  network and LAN-only SSH work
G4  Hyprland starts
G5  ARM64 Quickshell renders selected Omarchy shell
G6  reboot returns to the graphical shell
G7  HumAIn service is active on 127.0.0.1:8787
G8  valid public pointer returns public_only
G9  query string and fragment are rejected with 422
G10 visible HumAIn bar module appears
G11 node identity is unique and no source identity remains
G12 power-loss recovery returns to the intended node state
G13 swarm health announcement is opt-in and bounded
```

A fresh-card pass must include actual receipts, not “the installer completed.”

## Recommended implementation order

1. Add `bootstrap/` scripts and a prerequisite manifest to this repository.
2. Add a first-boot identity/sanitization service.
3. Add an image-builder wrapper that consumes a verified Manjaro ARM source image.
4. Produce a private golden image and boot a second Pi from it.
5. Run G1–G12 on the second Pi.
6. Add the opt-in typed health receipt protocol.
7. Add a coordinator only after two independent nodes pass the local health protocol.

The first two nodes should be boring. If they begin exhibiting emergent behavior before the receipts exist, that is not intelligence. It is usually a shell script.
