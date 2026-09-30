# Summary

- [Guiding Principles](./rfd-0001-guiding-principles.md)
- [Strong Separation of Constructing FRP and I/O](./rfd-0002-strong-io-separation.md)
- [Memory Model](./rfd-0003-memory-model.md)
- [Value Model](./rfd-0004-value-model.md)
- [Transaction Protocol and Failure Modes](./rfd-0005-transaction-protocol.md)
- [The I/O Edge: Handles, Drivers, and Threading Modes](./rfd-0006-io-edge.md)
- [Targets: No-std Tiers, Input Slots, and Host Embedding](./rfd-0007-targets.md)

---

- [Glossary](./glossary.md)

# Research

- [Keeping a no-std mode viable in Bough](./research/2026-09-22-no-std-handoff.md)
- [Embedding FRP in a host runtime: requirements from a Bevy port](./research/2026-09-23-frp-host-embedding-requirements.md)
- [Exploring a static, no-alloc core: the handoff](./research/2026-09-23-static-engine-handoff.md)
- [Exploring a static, no-alloc core: the addendum](./research/2026-09-23-static-engine-handoff-addendum.md)
- [A no-allocator core: static engine, bounded dynamic engine, or neither](./research/2026-09-23-static-engine-exploration.md)
- [Bough on the web: what wasm32 and wasm-bindgen impose](./research/2026-09-23-wasm-target-research.md)
- [Building the engine: the architecture brief](./research/2026-09-24-engine-architecture-brief.md)
- [Building the engine: the oracle's specification](./research/2026-09-24-ghc-oracle-spec.md)
- [Building the proposed API: an engine held to GHC](./research/2026-09-24-engine-feasibility-spike.md)
- [Three issues for Sodium's semantics text, drafted](./research/2026-09-25-sodium-issue-drafts.md)
- [Oracle work for the real build: the handoff](./research/handoff-2026-09-25-oracle-work-for-the-real-build.md)
- [Building the I/O edge: one rule, nine steps](./research/2026-09-27-io-edge-spike.md)
- [An FRP literature review for Bough: the handoff](./research/handoff-2026-09-27-frp-literature-review.md)
- [What the FRP literature says to Bough](./research/2026-09-28-frp-literature-review.md)

# Notes

- [Slot churn simulation](./notes/2026-09-23-slot-churn-simulation.md)
- [One rule for the I/O edge](./notes/2026-09-26-io-edge-one-rule.md)
- [What an Oort fighter found first](./notes/2026-09-26-oort-fighter-first-findings.md)
- [Where the I/O edge spike landed](./notes/2026-09-27-io-edge-spike.md)
- [The I/O edge spike's three questions, answered](./notes/2026-09-27-io-edge-questions-answered.md)
- [What the RFD revision will do](./notes/2026-09-27-rfd-revision-grilling.md)
- [Where the RFD revision landed](./notes/2026-09-27-rfd-revision-landed.md)
- [A core that doesn't know its mode](./notes/2026-09-27-mode-generic-core.md)
- [Incremental Collection Propagation](./notes/2026-09-29-incremental-collection-propagation.md)
