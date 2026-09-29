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
- [Building the I/O edge: one rule, nine steps](./research/2026-09-27-io-edge-spike.md)
- [An FRP literature review for Bough: the handoff](./research/handoff-2026-09-27-frp-literature-review.md)
- [What the FRP literature says to Bough](./research/2026-09-28-frp-literature-review.md)

# Notes

- [Requirements for the Bough FRP engine](./notes/2026-09-21-design-requirements.md)
- [Slot churn simulation](./notes/2026-09-23-slot-churn-simulation.md)
- [Changes to Bough RFDs](./notes/2026-09-25-changes-to-the-rfds.md)
- [What an Oort fighter found first](./notes/2026-09-26-oort-fighter-first-findings.md)
- [A core that doesn't know its mode](./notes/2026-09-27-mode-generic-core.md)
- [Incremental Collection Propagation](./notes/2026-09-29-incremental-collection-propagation.md)
- [The cost: edge complexity gets concentrated](./notes/2026-10-06-edge-complexity-cost.md)
- [Bough as the composition layer for IO-less protocols](./notes/2026-10-06-io-less-composition.md)
- [Middleware is just a pattern; edge composition is the real gap](./notes/2026-10-06-middleware-and-edge-composition.md)
- [Swappable edges: client/server as two graphs, migration, and a free differential test](./notes/2026-10-06-swappable-edges.md)
- [What the expressibility port has to express](./notes/2026-10-08-mema-expressibility-scope.md)
- [What a thousand rows cost](./notes/2026-09-29-row-cost-probe.md)
