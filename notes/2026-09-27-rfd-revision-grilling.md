# What the RFD revision will do

_2026-09-27. We grilled the revision that brings RFDs 1 to 7 and the
glossary up to both spikes: the engine spike, with
[its answers](../research/2026-09-24-engine-feasibility-spike.md), and
the I/O edge spike, with
[its research note](../research/2026-09-27-io-edge-spike.md) and
[the answers to its questions](./2026-09-27-io-edge-questions-answered.md).
Each question had its prerequisites settled first. The answers bind the
revision, and so do the conclusions they forced, listed after them._

## The answers

1. **Scope.** Both spikes, in one revision of RFDs 1 to 7 and the
   glossary. Where the spikes disagree, the later step we agreed wins.
2. **Delivery.** A new branch off `spike/engine-feasibility`, one commit
   per document, in a PR stacked on the research PR.
3. **State.** Every RFD stays in `discussion`. Zefira moves each to
   `published` once she has read its revised text.
4. **Detail.** The RFDs state the observable rules, and a mechanism only
   where a claim or a target forces it, with its reason beside it. The
   rest is cited to the research notes.
5. **What ran.** Nothing is stated as fact that hasn't run. Plans stay,
   marked as not built, with their open questions named. What can't
   happen goes.
6. **The poison window.** Fixed. Where panics unwind, a guard around
   graph code marks the poison in both handles as the panic leaves, so
   every call says `Poisoned` at once, from any thread. The
   transaction-in-progress flag stays the poison. On wasm a panic is a
   trap and nothing runs after it, so a call there says `FromGraphCode`
   until something calls into the runtime again. RFD 5, RFD 7 and the
   docs say so. On wasm, `std::thread::panicking()` stays true after a
   trap, which the step may use.
7. **The drop check.** It also counts kept once-listeners still waiting
   in either handle's queue. The rule is one sentence: no kept
   once-listener may still be waiting.
8. **Error families.** The types split, so no enum carries a variant its
   call can't return: a handle's `transaction` loses `ForeignGraph`, and
   `Transaction`'s once-listeners lose `Poisoned`. Handle calls keep no
   panicking form. That's the one exception to the `try_` rule, since a
   handler called from C can't unwind.
9. **RFD 3's requirement.** It stays strict, and names its one exception
   where it's stated: a guard hidden in graph state holds its memory
   until the runtime drops, and the derive catches the common case by
   name.
10. **A name.** "The graph code re-entrancy check" replaces "the guard"
    for the check that refuses a handle's call from graph code.
11. **Test affordances.** Six. `statistics` joins them: phase counters
    behind a cargo feature, compiled out without it.
12. **Sequencing.** This note, then the spike steps below, then the
    revision, in the same session.

## Before the revision

Five steps on bough's `spike/io-edge`, each with its interface and tests
agreed before its code:

1. Mark the poison in both handles as a panic leaves graph code.
2. Count kept once-listeners waiting in the queues at the drop check.
3. Build the first spike's answer 4: a `Clone`-free materializer that
   splits a stream of pairs into two linear streams. Its name comes with
   its interface.
4. Split the error types.
5. Rename `set_collect_after_every_transaction` to
   `set_collect_after_every_unit`. It collects after each whole unit, and
   a child transaction is a transaction too.

Then the passages get mapped again against the new head, since the map
behind this grilling was made against `1a2fe9d`. The revision describes
`e14c2a2..` that head.

## What follows from the answers

**How it's written.** In place, with no change history. Trade-offs and
rejected alternatives go into the sections they belong to, as RFD 1's
records policy says. That includes checking every declared switch
candidate at build, which was raised under the engine spike's answer 2
and never tried.

**Superseded, so not written as recorded.**
- Collection "when the next transaction opens", from the engine spike's
  answer 5. It runs after each whole unit, the build included.
- `GraphDropped`, which is `IoError::Gone`.
- `anchor(&T)`, which is `anchor(T) -> Anchored<T>`.
- One `RemoteTransaction`, which is two types.
- A pump that runs whatever has arrived. It runs only calls made before
  it began.
- The one-rule note's root on a waiting send, and its `Weak`.

**Corrected.**
- The engine spike's answer 7: a thumbv7m build with neither `std` nor
  `critical-section` keeps the `Io` too.
- RFD 6's "costs nothing": the graph code re-entrancy check costs about
  six instructions a transaction.
- RFD 4's "a chain cannot be stored in a value or returned from build
  until it is materialized" goes. Chain adapters are `Trace`.
- RFD 2's argument against an `Output` wrapper, that it would be needed
  inside every `construct`, is rewritten. `b.anchor` is that step.

**Mechanism.** Stamps, pump serials, owner counts, the waiting-call enum
and the `Driver` trait stay in the research notes, and the enum's size
isn't named. RFD 7 keeps the per-slot pending flag, since a static slot
on a Cortex-M0 can't reach anything the runtime owns. RFD 6 names
`IoTransaction` and `RemoteTransaction`, and their one difference: a
listener tied to a remote's unit must be `Send`.

**Plans, marked as not built.**
- The core driver. How it stops, and what it does with a panic, are
  open; `shutdown` and bough-gtk's `Driver` are the model.
- The bounded tier. Open: every handle call allocates and the queues
  grow; which enums get `Exhausted`; whether `IoError` needs a
  queue-full case; whether it needs the 24-byte waiting call.
- The debug dump, and the UI benchmark shape.
- `construct`'s creation-time cut is described as the engine does it.
  The oracle experiment in the handoff stays open.

**RFD 1.** The oracle is GHC, in CI on a fixed seed, with a scheduled job
on fresh seeds. "Exact fidelity means we inherit the corners" is
qualified by the policy for where Sodium's text contradicts itself. The
wasip1 leg runs the engine's own tests, since GHC can't run there. The
benchmarks name fan-out beside shallow and frame, and the 5% gate.

**Sodium's contradictions.** Each difference is named at its operation,
in RFD 4 or 5, and RFD 1's policy lists the cases.

**Bare metal.** Interrupts stay on slots. A `RemoteIo` call from an
interrupt handler is documented misuse, since it allocates, and the
`RemoteIo`'s graph code re-entrancy check stays `std`-only.

**Hosts.** GTK joins RFD 7's hosts, with two lessons: a host that drops
its runtime from C calls `shutdown`, and a list view's rows are right a
pump later.

**Words.**
- In prose, "runtime" means bough's `Runtime`. An executor is an
  executor, and a host is a host.
- "Graph" means the network of nodes.
- A handle is an `Io` or a `RemoteIo`. A guard is a `Listener` or an
  `Anchor`.
- A unit is a transaction with its children, however it started: a
  `Runtime` call, a slot's drain, or a queued call.
- A call's stamp stays out of the RFDs, so "stamp" keeps its one
  meaning.
- An `Anchored`'s clones share one root, which ends with the last clone.
  The glossary still avoids "owner".
- "Drop guard" and "mutex guard" keep their Rust senses.

## Defaults

- The revision's branch is `rfd/revision-after-the-spikes`.
- The glossary is its first commit, then RFDs 1 to 7 in order, since
  every RFD uses the glossary's words.

## Addendum, 2026-09-27: the poison step

The first step landed as `fa9afdf` on `spike/io-edge`. It marks the
poison at each entry that can poison, not only around graph code: a
panic in a listener, a transaction's closure or a collection's `Drop`
poisons too, and before the step a handle's call after one was queued
and lost. It costs two instructions a send.
