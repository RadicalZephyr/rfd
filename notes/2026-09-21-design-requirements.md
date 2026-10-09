# Requirements for the Bough FRP engine

_2026-09-21. Gathered from the first design conversation, before the
RFDs were revised, and kept as written. It scoped the FRP literature
review._

Every requirement Zefira articulated, gathered from the design conversation and
from RFD-0001, which predates it. Requirements are what was asked for; the
decisions taken to satisfy them are in the RFDs and are referenced, not
repeated. Where a requirement was stated in Zefira's own words, those words are
quoted.

## R1. Derive the design from the denotational semantics

The engine implements the Sodium denotational semantics, version 1.1, as the
executable Haskell in the SodiumFRP repository
(`denotational/Reactive/Sodium/Denotational.hs`). Fidelity is exact:
deviations are only permitted where the semantics are silent, and any deviation
we later want is a semantics change requiring its own RFD.

From RFD-0001, which states this as the first guiding principle:

> This means that first and foremost Bough needs to correctly implement the
> Sodium FRP denotational semantics (modulo API names).

Consequence accepted: the odd corners come with it. `listen_steps` fires on a
step to an equal value. `switch_cell` emits a step at creation and at every
switch, even when the new inner is quiet. `switch_stream` uses the old stream
at the switch instant while `switch_cell` uses the new cell's post-instant
value. `merge` is left-biased.

## R2. Fast under every workload, with a stated bar

> The workload is "any of the above". we can't know ahead of time how a user
> will want to use the library so let's say we want to be fast under all the
> situations you mentioned.

The three workload shapes, blessed as the acceptance test:

| Shape | Description |
|---|---|
| UI | Ten thousand nodes, ten switches deep, one input per transaction, ten listeners touched. |
| Frame | A thousand inputs per transaction into ten thousand nodes, most of them affected. |
| Shallow | One input through three adapters, plus a variant with a `share` in the middle so one real node hop is measured. |

The bar: **within a factor of three of hand-written imperative Rust on
realistic per-node payloads**, meaning 50 to 100 nanoseconds of the user's own
work per node. Overhead on trivial payloads is reported alongside as
information, not as a bar. Each shape has a hand-written imperative baseline in
the bench crate, timed by the same harness.

Measurement: criterion by hand for the bar; `iai-callgrind` in CI as an
instruction-count regression gate.

From RFD-0001:

> FRP is a higher-level abstraction and as such we expect to sacrifice some
> performance for the sake of safety and ergonomics. But Bough is still a Rust
> library so we should not leave any obvious performance wins on the table.

## R3. No memory leaks, and a checkable mechanism for the user's part

> I also need to state that the memory leak you accepted is an unacceptable.
> there has to exist a mechanism to let the user inform us of the dependency
> and prevent the leak.

The leak in question is a cycle through values: a cell whose value holds a
token upstream of itself, which `sodium-rust` still leaks despite its
per-closure dependency declarations. Requirements:

- No configuration of the graph may leak, including cycles through values.
- Whatever the user must declare has to be checkable, and its failure mode must
  be loud rather than silent.
- Tests must be able to assert the absence of leaks.

Satisfied by RFD-0003: tracing collection from explicit roots, `Trace` on cell
value types, `Build::depends` for non-upstream captures, stale-token errors as
the failure mode, a collection-stress setting and a public live-node count.

## R4. Structurally impossible to mix I/O and FRP construction

> It should be structurally impossible for a user to mix the library primitives
> meant for interfacing with I/O while building FRP logic. In `sodium-rust` the
> public `Stream` and `Cell` types contain both the I/O-facing API and the
> FRP-facing API, so it's trivial for a user to call `Cell::values` or for them
> to call `send` on a sink inside code running in arbitrary node in the graph
> and think they're still in the world of FRP. The API should guide the user
> towards writing correct FRP code, that follows roughly this ordering:
>
> - construct pure FRP logic graph once during construction. runtime
>   construction is handled purely through `switch`.
> - get I/O handles to the "edge" of their graph and wire these up to interface
>   with their I/O primitives
> - I/O code drives sends into the FRP graph (input), and responds to FRP
>   output with listener functions that drive other I/O as necessary. This is
>   just "turning the crank" on the FRP graph, which may reconfigure itself
>   while running.

This is the requirement RFD-0002 exists to satisfy. Its consequences include:
the `Build` and `Graph` split; inert tokens with no methods of their own;
listeners with no graph access; nothing adding logic after build except through
`construct` and switch; and `listen` accepting only materialized nodes, never a
chain, so no adapter can be applied from I/O code.

A corollary Zefira added later, as a correctness fix: Sodium's `updates` and
`value` are documented as operational primitives, so they belong to I/O code,
not to `Cell`.

## R5. Usable from any threaded or async runtime, with minimal friction

> A requirement I haven't stated yet is that a user should be able to use the
> `bough` engine with any threaded or async runtime they want, with minimal
> friction. The `bough` engine remains single threaded, but it should be usable
> in multi-threaded and async contexts where the I/O world is using those
> modes.

With the worked case that must be expressible without the user writing channel
plumbing:

> If `Graph` is required for `send` how can we model a chat room using async
> I/O? Basic sketch, is that we have one `input` that takes a username and
> message text. Separate async tasks listen for messages on sockets from each
> user, need to call `send` with their fixed username, and the text received
> from the socket. Forcing the user to use channels to manually route all I/O
> to a singular FRP entrypoint that holds the singular owned `Graph` seems
> unnecessarily restrictive, but building such infrastructure automatically
> requires choosing a specific channel implementation.

And the constraint that rules out the obvious fix of per-integration ownership:

> The concern about a singular owned `Graph` still holds though, just one level
> up. What if the user wants their bough engine to bridge I/O from multiple
> different such integrations?

Requirements extracted: the engine core stays single-threaded; the library does
not choose a channel implementation for its users; several integrations must be
able to feed one graph; and no integration may own the graph. Satisfied by
RFD-0006: `Remote`, the inbox, the waker hook and `pump` in the core, with
adapter crates as adapters only, and the `Local`/`Threaded` mode parameter so a
graph can live in a spawned task.

## R6. Safe, idiomatic Rust that makes correct code easy and incorrect code hard

From RFD-0001:

> Bough's public API surface should be entirely safe Rust and take advantage of
> Rust's type system to the fullest to provide an ergonomic and idiomatic
> experience writing FRP in Rust. Writing correct FRP code in Bough should be
> easy and obvious, violating the expectations of the Bough FRP engine should
> be as difficult and awkward as possible.

Specific commitments this produced:

- Move-only `Stream<A>` so a second consumer is a compile error, with `share`
  as the explicit fan-out that forces `Clone`.
- `Clone` required only where a value is genuinely duplicated, so non-`Clone`
  values flow through streams.
- Stream functions take events by value, so the identity function is `|a| a`.
- Cell values are read by reference and never cloned by the engine.
- `sample` returns a reference from a shared borrow, so several samples compose
  in one expression.
- Errors split: deterministic construction errors panic, I/O-phase errors have
  `try_` siblings. One error enum per family of operations sharing failure
  modes, **with no variant an operation cannot return**.
- Operations on collected nodes whose effect the semantics cannot observe are a
  debug panic and a release no-op, counted, following the integer-overflow
  precedent: "the model is to help developers catch the send as an error during
  development but silently ignore it in release."

## R7. Naming: spell words out

No single-letter suffixes and no abbreviations, except where Rust precedent
exists (`*_mut`, `try_*`, `filter_map`). Sodium's names are kept where they are
good and replaced where they are poor, with a translation table for readers
coming from the book. Names must reinforce concepts rather than fight them:

> we should name the associated type on `Source` `Event` instead of `Item`. The
> analogy with `Iterator` is only helpful for building the code and this helps
> the API names reinforce the concepts rather than fighting them.

No type may collide with a standard library concept: `Pin` was rejected for
this reason.

## R8. A shared, written vocabulary

A glossary at `GLOSSARY.md` in the `rfd` repository root, published as a
Glossary chapter of the RFD book. It is a glossary and nothing else: opinionated,
with an `_Avoid_` list per term, no implementation detail.

## R9. Documentation follows Diátaxis

Reference is rustdoc. Tutorials, how-to guides and explanation live in an
mdBook at `book/` in the `bough` repository, published to GitHub Pages on every
`v*` tag.

## R10. Design decisions are recorded as RFDs

Oxide Request for Discussion format, in `bough-frp/rfd`, each carrying a `State`
line and both of us on the authors line. A decision is recorded when something
costly to undo is about to depend on it. Trade-offs and rejected alternatives go
into the section they belong to, not into a change history:

> Include the reasoning and rejected alternatives in the relevant RFDs.

## R11. Process

- Agree the interface and the tests before non-trivial code.
- One branch and one pull request per unit of work; Zefira reviews and merges.
- Increments small enough to review in five minutes.
- CI runs format, clippy with warnings denied, tests in debug and release
  (the two differ by design), the oracle property tests, and the
  instruction-count regression gate.
- The engine crate has zero runtime dependencies; the derive sits behind a
  feature.
- Nothing is pushed to the `sodium` fork, which stays the semantics reference.
- Facts are looked up, never assumed: when a technical detail is uncertain,
  propose a concrete experiment and run it.

## R12. Library first, and a foundation for tooling

From RFD-0001:

> Bough is first and foremost meant to be used as a library from within Rust.

> Once we have a solid base to work from building a more full-featured FRP
> based app framework on top of Bough is an explicit goal.

The framework goal produced one concrete requirement during the design: loops
must be declarable in one place and closable in another, so a framework can own
the declare and the close while user code builds the middle. This is why the
closure-scoped loop form was dropped in favour of the flat declare-and-close
form.

## Out of scope, stated explicitly

- `no_std`. Standard library only.
- A continuous-time module.
- Sodium's partitions: one `Graph` type.
- Sodium's `Lazy` family in v1; it may return later for the initial-value case.
- `listenWeak`, `listenOnce`, `addCleanup`, `Transaction.post`, `onStart`.
- Adapter crates in v1. `bough-tokio` is the first follow-on.
- A queue type in the core. Queues belong to the adapter crates.
