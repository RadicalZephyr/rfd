# Guiding Principles for Bough Design

**State:** discussion · **Authors:** Zefira Shannon, Claude

Bough aims to be the go-to Functional Reactive Programming library in
Rust, and there are a number of ideals we want to strive for:

## Strong Adherence to the Sodium FRP Denotational Semantics

Software needs to be more composable. Instead of using LLMs to
generate reams of new code in existing languages we should build better
tools and languages that are expressive enough that we don't need to
use LLMs.

Having a library that lets you leverage compositionality and a direct
path to creating a functional-core imperative shell architecture for
complex event driven programs in Rust would be a strong step in this
direction.

This means that first and foremost Bough needs to correctly implement
the Sodium FRP denotational semantics (modulo API names).

## Safe and Idiomatic Rust API

Rust is a great foundation to build systems software in, but sometimes
it's not the best tool for every job. Building a higher level
abstraction like a library for Functional Reactive Programming that is
deeply integrated with Rust seems like it could give us the best of
both worlds.

Similarly, Sodium is a well-design minimal FRP library but the Rust
port is clearly designed to conform to the standard Sodium API and
doesn't do much to take advantage of Rust's type system to provide a
safe and ergonomic API.

Bough's public API surface should be entirely safe Rust and take
advantage of Rust's type system to the fullest to provide an ergonomic
and idiomatic experience writing FRP in Rust. Writing correct FRP code
in Bough should be easy and obvious, violating the expectations of the
Bough FRP engine should be as difficult and awkward as possible.

## As Performant as Possible

FRP is a higher-level abstraction and as such we expect to sacrifice
some performance for the sake of safety and ergonomics. But Bough is
still a Rust library so we should not leave any obvious performance
wins on the table.

## Usable as a Library

Bough is first and foremost meant to be used as a library from within
Rust.

## Easy to Build More Tooling On

Once we have a solid base to work from building a more full-featured
FRP based app framework on top of Bough is an explicit goal.

## Policies

These are standing rules rather than decisions. They apply to every RFD
and every increment, and changing one is a change to this document.

### The Semantics Are the Test

The executable denotational semantics in the Sodium repository
(`denotational/Reactive/Sodium/Denotational.hs`, version 1.1) are the
oracle, run as they stand. `bough-oracle` vendors the Haskell unedited
and runs it under GHC, over lists of time-stamped values. Every primitive
is property-tested against it with random programs and random input
events. For each observed node and transaction, a test compares the
events and steps in order, the order of listener calls across nodes, and
a sample of every observed cell after every transaction. Behaviour the
semantics cannot express (listeners, roots, collection, the handles I/O
code calls through) gets its own property tests with random observation
patterns, and the public live-node count is the leak assertion.

The text hangs on some legal loops, so the oracle computes loops by fixed
point: a round for each instant the answer chains through, which took a
counter over 20,000 transactions more than a minute. Porting the text to
Rust was the plan, and it's shelved: a port would need the same machinery,
and running the text itself found four defects in it. Running GHC only by
hand lost too, since it would leave the one check that holds the engine
to the text out of CI. GHC runs in CI on a fixed seed, and a scheduled
job runs fresh seeds and reports each failure with its seed. Neither job
exists yet: CI skips the oracle today.

Only the Haskell is vendored, `Denotational.hs` and `sodium.hs`, under
their BSD licence. The accompanying document has no numbered sections,
only figures, so a test cites the clause and the figure it holds the
engine to, and stays correct after the internals it was written against
are replaced. The random-program generator produces loops and diamonds
through loops from its first version, because every correctness problem
the Bevy port's research met involved a loop, and the `lift2` shape it
filed as `sodium-rust#52`, a cell held through a loop lifted together
with something upstream of itself, is a fixed test written against the
specification. The engine's own tests are to run on `wasm32-wasip1` under
wasmtime too ([RFD 7](./rfd-0007-targets.md)). GHC can't run there, so
the oracle stays on the host. That job isn't built.

Exact fidelity means we inherit the corners. `listen_steps` fires on a
step to an equal value. `switch_cell` emits a step at creation and at
every switch, even when the new inner is quiet. `switch_stream` uses
the old stream at the switch instant while `switch_cell` uses the new
cell's
post-instant value. `merge` takes a combining function, called as
`f(left, right)` when both streams fire in one instant; `or_else` is
the left-biased one. Changing any of these is a semantics change and
needs its own RFD, not an implementation choice.

The one exception is where the text breaks its own rules: time order,
and things existing from their creation. There the text isn't the
authority. Bough follows the rule, names the difference where the
operation is described, in [RFD 4](./rfd-0004-value-model.md) or
[RFD 5](./rfd-0005-transaction-protocol.md), and a test pins the text's
answer beside Bough's. There are three cases so far:

- F6: a `switch_cell` created after its outer stepped, whose steps the
  text puts out of time order, before its creation, and from the old
  inner.
- F7: a `split` fed by its own children, whose events the text puts out
  of time order.
- F89: a `split` or a `defer` built at a child instant, which in the text
  replays events from before it existed.

The oracle patches the text for F6 and F7. Its patch for F89 isn't built:
the random programs keep splits and defers out of the bodies that may run
at a child instant, and a fixed test pins both answers. Whether the same
cut applies to `construct` is an experiment the oracle work still
carries. The three are
[drafted as issues for Sodium](./research/2026-09-25-sodium-issue-drafts.md),
and none is posted.

### Test Affordances

Six, and nothing beyond them, because test-only introspection is how
it leaks into the engine:

- `set_collect_after_every_unit`, a setting on the runtime that collects
  after every unit;
- a debug dump of the graph behind a cargo feature, which isn't built
  yet;
- node ids allocated deterministically in creation order, so a failure
  reproduces;
- the public live-node count;
- `set_shuffle_seed`, a seeded setting that shuffles listener dispatch
  order and the evaluation order of independent nodes, so the property
  tests run under random orders and a user's tests surface
  order-dependent listeners;
- `statistics`, phase counters such as evaluations, behind a cargo
  feature and compiled to nothing without it, so that a test can pin a
  claim its own closures can't see, such as a fused chain running once
  per step.

The shuffle is what makes the claim that order cannot matter a test that
can fail rather than a sentence. None of them shows which child instant
an event fell in, so the oracle's tests don't compare child indices.

### What Fast Means

Four benchmark shapes, each with a hand-written imperative baseline,
timed by criterion by hand:

- UI: ten thousand nodes, ten switches deep, one input per
  transaction, ten listeners touched. The baseline is an observer
  registry with boxed callbacks, because dynamic wiring is intrinsic
  to the shape. It isn't built yet.
- Frame: a thousand inputs per transaction into ten thousand nodes
  with most of them affected. The baseline is a loop over the values.
- Shallow: one input through three adapters, plus a variant with a
  `share` in the middle so one real node hop is measured. The baseline
  is plain function calls.
- Fan-out: one send to a shared input with sixty-four listeners. The
  baseline is the same sixty-four closures, boxed and called in a loop.

The bar is a factor of three against the baseline on realistic per-node
payloads of 50 to 100 nanoseconds of the user's own work. Overhead on
trivial payloads is reported alongside as information, not as a bar; no
design with transactions, generation checks and a dirty walk gets under
roughly ten times a tight loop on trivial payloads, and the answer to
that is the usual FRP advice, cells of collections rather than
collections of cells. `iai-callgrind` runs shallow, plain and shared,
frame and fan-out on every pull request as a regression gate on
instruction counts, and a rise of more than 5% fails. It does not
measure the bar, because instruction counts do not track wall-clock
across cache effects. Code size on wasm32 is to be reported as
information in the same way, with no gate, and nothing reports it yet
([RFD 7](./rfd-0007-targets.md)).

### Targets

Native with `std`, bare metal on Cortex-M without it, the web through
`wasm32-unknown-unknown` and wasm-bindgen, and Bevy as a host are
first-class targets. A decision that breaks one is a decision to
revisit, and continuous integration checks the core for each of them on
every push ([RFD 7](./rfd-0007-targets.md)).

### Dependencies

The engine crate depends on no other crate in its default feature set. A feature may add one when it is the seam an ecosystem already
implements, as `critical-section` is for bare metal. `proptest`,
`criterion` and `iai-callgrind` are development dependencies.

### Naming

No single-letter suffixes and no abbreviations, except where Rust
precedent exists (`*_mut`, `try_*`, `filter_map`). We can afford to
spell words out. Sodium's names are kept where they are good and
replaced where they are poor; the translation table lives in the
crate-level documentation and in the explanation book.

### Documentation

[Diátaxis](https://diataxis.fr/). Reference is rustdoc. Tutorials,
how-to guides and explanation live in an mdBook at `book/` in the
`bough` repository, published to GitHub Pages on every `v*` tag.

### Records

RFDs carry a `State` line using Oxide's states: `prediscussion`,
`ideation`, `discussion`, `published`, `committed`, `abandoned`. A
decision is recorded when something costly to undo is about to depend
on it. Trade-offs and rejected alternatives go into the section they
belong to, not into a change history.
