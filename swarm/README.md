# Bounded swarm health receipts

`health_receipt.py` defines `omarchypi.health.v1`, a strict observation envelope for the first swarm layer.

It records only:

- node ID and role
- declared capabilities
- observed timestamp
- software version
- HumAIn context-service state
- desktop observation state
- explicit `lan-only` scope

It does not authenticate a node, authorize an action, expose private context, or provide remote execution. The `receipt_id` is an integrity hash, not a signature and not proof that the node is truthful.

The protocol is intentionally boring. Authentication, enrollment, revocation, and a coordinator are separate future layers.
