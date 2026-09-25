# Building the proposed API: an engine held to GHC

_2026-09-24. A research note for the Bough design, answering one question:
can the API that RFDs 2 to 7 propose be built as they say? The spike that
answers it is throwaway. Its code is on `spike/engine-feasibility` in the
`bough` repository, at `06972e0`, and it is not meant to merge. It followed
two briefs, kept beside this note:
[the architecture brief](./2026-09-24-engine-architecture-brief.md) and
[the oracle's specification](./2026-09-24-ghc-oracle-spec.md). Nothing here
has authority over the RFDs; the questions at the end are for Zefira._

## The answer first

It can, with changes. Every signature in the skeleton now has a body, and the
engine gives the semantics' answer on every program the spike ran against it.
The oracle is the vendored `Denotational.hs` under GHC 9.4.7, never edited.
About 72,000 random programs agree with it on every event, every step and
every sample. Each program runs up to fourteen ways: both modes, plain, under
three seeds of the order shuffle, with each transaction's sends permuted two
ways, and collecting after every transaction. The fixed tests quote GHC's
answers for the loop shapes RFD 1 promises, sodium-rust#52 and the
health-and-shield slice among them. Seventy deliberate breaks of the engine
each fail a test; a few are one break tried again at a later stage.

The transaction RFD 5 derives on paper holds in its hard parts. The evaluation
loop is flat and checks nothing on its fast path. Memoized pull covers a
`switch_cell`'s read past the instant and the nodes a `construct` builds.
Child transactions run depth first with shared indices. Collection traces from
explicit roots and needs no new kind of root. The engine has no `unsafe`, and
`Graph<Threaded>: Send` is a fact the compiler derives rather than a promise.
The core builds for every target RFD 7 names. A graph that is not growing
allocates nothing per transaction.

What did not hold falls in four groups.

1. **The semantics text.** It hangs on a legal loop whose events depend on
   values, so the oracle computes loops as fixed points (F1). Three of its
   clauses give answers out of time order or before a node exists: `SwitchC`
   for a switch created late, `Split` fed by its own children, and `Split`
   built at a child instant (F6, F7, F89). The oracle patches the first two.
2. **Rules the RFDs state wrongly.** The loop rule (F3). "Cell listeners run
   for every marked cell" (F4). Relinking one switch at a time (F46). RFD 3's
   collection trigger and its timing (F64, F65). "Upstream captures need no
   declaration" (F62). When the guard on remote sends is armed (F74). What
   `Remote` needs from a target (F70). The engine does what the semantics need
   instead, and each is below with its reproduction.
3. **The public API.** Thirteen groups of changes. None of them changes the
   RFDs' own examples, which compile and run. One conflict between RFD 2 and
   RFD 4 needs a decision (F59).
4. **Costs.** The share shape runs at 2.47 times its baseline, against a bar of
   3. A switch's relink check walks everything upstream of its new inner.
   Fusion costs compile time per chain shape. Collection's declarations are a
   real burden in code that selects among tokens.

## What ran

| Piece | Where | What it is |
|---|---|---|
| The semantics | `bough-oracle/haskell/Reactive/Sodium/Denotational.hs`, `sodium.hs` | Vendored unchanged from SodiumFRP/sodium at `a6f5b31`, under its BSD licence. Its twenty vectors pass under GHC 9.4.7. |
| The oracle | `bough-oracle/haskell/Oracle*.hs`, `bough-oracle/src/{program,ghc,answer}.rs` | An interpreter over the text's constructors for programs described as data. Closures cannot cross a process boundary, so every function is an integer expression both sides evaluate the same way. Loops by fixed point; F6 and F7 patched in `Oracle/Derived.hs`. A Rust client keeps a pool of GHC processes. 181 Haskell cases. |
| The engine | `bough/src` | Every stage behind the skeleton's signatures. |
| The comparison | `bough-oracle/src/{build,generate,compare}.rs`, `bough-oracle/tests/engine.rs` | Random well-typed programs, built with the Bough API, run, and compared with GHC's answer: per observed node and per transaction, the events and steps in order; the order of listener calls across nodes; and a sample of every observed cell after every transaction. |
| The fixed tests' GHC programs | `bough-oracle/haskell/probes` | The programs behind every value a fixed engine test quotes, each beside its output; `tests/probes.rs` checks they still give it. |

The random programs in the long runs:

| Round | Programs | Seed | What they carry |
|---|---|---|---|
| First-order core and cells | about 35,000 | several, and 20260924 | about 28 definitions and 11 observed nodes each |
| Loops and child transactions | 4,000 | 3 | 81–83% with loops, 44–47% with a loop through child transactions |
| Switches | 8,192 | 20260924 | 74% with a switch the comparison sees, 85% of those one that moved |
| `construct` | 16,384 | 20260924 | 68–70% with constructs, nested, at child instants, and RFD 4's screens |
| The input-slot fold law | 8,192 | 20260924 | 27,329 pumped runs between 41,331 other transactions |

Every `cargo test` also runs 1,024 random programs and 512 fold-law programs
against GHC.

Toolchains: rustc 1.94.1 (e408947bf 2026-03-25), and 1.85.1 for the minimum
supported version; GHC 9.4.7 with HUnit 1.6.2.0, Ubuntu 24.04's packages; one
x86-64 machine with four cores. Every commit on the branch was checked on its
own: `cargo fmt`, clippy with warnings as errors, the tests, a thumbv6m build
and 1.85. The early commits also ran the tests in release and every target
check CI runs, each on its own. The later ones ran the tests with
`BOUGH_ORACLE=skip` each on its own, as CI does, and the rest at the last
commit of each batch. At the last commit, 530 tests pass.

To run it again, from the `bough` repository:

```sh
cargo test --workspace --all-features                   # everything; about 26 s once built
PROPTEST_CASES=16384 PROPTEST_RNG_SEED=20260924 cargo test -p bough-oracle --release --test engine
BOUGH_ORACLE=skip cargo test --workspace --all-features  # without GHC
```

## The engine in one paragraph

Nodes live in an arena of parallel vectors, addressed by tokens of index,
generation and graph id. Every value, closure and chain the graph stores is
erased into the mode's carrier, `Box<dyn Any>` in `Local` and
`Box<dyn Any + Send>` in `Threaded`, and only inside `Accepts::erase`. That is
why the compiler derives `Graph<Threaded>: Send`, and why a missing bound fails
to compile inside the engine rather than in a user's program. A node's program
leaves the arena while it runs and its data stays behind, so a node can read
itself and a closure can be handed the build context. A transaction marks the
affected region depth first, read-through cells included, and evaluates it
backwards in a flat loop. It runs the nodes created during it by pull over
their dependencies, and commits. Then it relinks switches on the final graph,
dispatches listeners in evaluation order, and runs child transactions depth
first. The architecture brief has the rest; its addendum lists where the
engine left it.

## What held

- **The transaction gives the semantics exactly**, the dynamic cases
  included. A `switch_cell` reads its new inner's value after the instant by
  pulling it out of order: one pull when that inner comes later in the order,
  none when it came first, and the evaluation loop checks nothing. Nodes a
  `construct` builds at an instant see that instant's events. Steps views of
  read-through cells carry the value after the instant. Split children share
  indices and run depth first. The engine matched GHC on the first run of every
  fixed program in the stages for children, switches and `construct`.
- **Fusion** (RFD 4). `input.map(f).filter(p).snapshot(c, g).hold(b, 0)` is one
  node with one monomorphized program, and its snapshot reads the value from
  before the instant.
- **`sample` returns `&A`** from `&Graph` and from `&Build`, through a
  `OnceCell` memo cleared at commit through `&mut`. Two samples compose in one
  expression, and a sample held across `send` is E0502.
- **A read-through function runs at most once per step**, even with a steps
  view and a cell listener on the same cell. The value a steps view computes is
  promoted into the memo at commit, so RFD 4's "may run twice" is too
  pessimistic (F17, F29).
- **No allocation per transaction.** Zero allocations over 30,000 steady-state
  transactions through every node kind, over 40,000 switch moves, over 1,000
  collections, and over 20,000 rounds of slot writes and pumps. A remote unit
  costs its sending thread one allocation, as RFD 6 sanctions.
- **The targets** (RFD 7). The core is `no_std` over `alloc` and checks for
  thumbv6m, thumbv7m and thumbv7em without `std`, for wasm32 with and without
  it, and on 1.85. Release builds for thumbv6m and thumbv7m instantiate every
  node kind. thumbv6m with `critical-section` keeps input slots, `connect`,
  `set_waker` and `pump`. The engine is `#![forbid(unsafe_code)]`.
- **Order independence is a test that can fail.** Every test runs under the
  seeded shuffle of RFD 1's fifth affordance with identical results, and a
  mutation that evaluates forward under the shuffle is caught.
- **The memory model's roots suffice.** Tracing from the build's return value,
  live listeners and live anchors collects cycles through values, and every
  random program still agrees with GHC when the graph collects after every
  transaction. `live_nodes` works as the leak assertion: a navigation that
  builds a screen per event stays bounded.
- **The I/O edge composes.** One `Local` graph with `Rc` state in its listener
  is fed at once by a task on a second executor, a plain thread with a
  `Remote`, and an input slot. A thread driver is 58 lines, a future driver 7,
  a one-task executor 9. RFD 6's chat room runs as written, with std threads
  and channels in place of tokio. The input-slot fold law holds against GHC.
- **RFD 1's fixed loop shapes.** The engine gives GHC's values on the
  sodium-rust#52 shape (health 100 in all four rows, where sodium-rust 2.1.3
  gives 60 in two), its reductions, and every step of the seven-instant
  health-and-shield slice.
- **`State<S>`**, as decided for in-place accumulation. Two new types, twelve
  changed signatures, one associated type, no existing test changed, and
  readable errors: ``no method named `steps` found for struct `State<A>` ``.
- **The performance bar, narrowly.** The share shape runs at 159 ns against a
  64 ns baseline with a 56 ns payload of the user's own work, 2.47 times, under
  the bar of 3 (F24).

## The semantics text

Any executable oracle meets these, whether it runs under GHC or is a Rust port.

- **F1. The text hangs on a legal loop.** `c = Hold 0 (Filter (<= 10)
  (Snapshot (\_ n -> n + 1) ticks c)) [0]`, a counter that stops at ten, never
  returns. `at` walks the whole step list, and the filter cannot decide the
  event at t without `at c t`; `takeWhile` in `at` does not help. The oracle
  computes every loop as a fixed point. Each loop reference replays the
  previous round's steps, starting from a cell that never steps, and the text's
  equations run unchanged until the steps repeat. A well-founded loop needs at
  most one round per distinct loop time, plus one, and where lazy knot-tying
  terminates the two agree. A Rust port, which RFD 1 plans, would need explicit
  laziness to tie any knot, and would then meet the same wall.
- **F6. `SwitchC` goes wrong for a switch created after its outer stepped.**
  Its steps come out of time order, include times before its creation, and
  start from the old inner. Bough reaches it by building a `switch_cell` of an
  older outer inside `construct`. The oracle switches over the outer chopped at
  creation, as Sodium's Java does.
- **F7. `Split` is out of time order when a split is fed by its own
  children.** `concatMap` gives 1, 2, 10, 11, 20, 21 where time order is 1, 10,
  11, 2, 20, 21, and a merge downstream then sees two events at one instant.
  The oracle sorts by time, stably.
- **F89. `Split` built at a child instant replays events from before it
  existed.** A split built at `[1,0]` turns the event of `[1]` into children
  `[1,1]` and `[1,2]`, which come after the split exists, so they are
  observable. The engine and Java give none of them. The oracle is not patched
  for it; the generator keeps splits and defers out of bodies that may run at a
  child instant, and a fixed test pins both answers. Question 8.
- **F44. `Execute` and `SwitchS` have no creation time either**, but for them
  the events before a node exists are unobservable: nothing built later sees
  them.
- **F22. A loop through `defer` with no filter never ends**, in the text and in
  the engine: `send` never returns. The loop rule does not bound a transaction.
- **F2.** Sodium's common tests put both split children at `[0,0]`; the text
  gives `[0,0]` and `[0,1]`. They compare values per instant only, so it is
  harmless there.
- **F21.** The PDF has no numbered sections, only figures E.1 to E.20; the
  markdown in bevy-sodium numbers the book's Appendix E and transcribes the
  book, not the PDF. A test cites the text's clause and figure.
- **F20.** Upstream sodium-rust loses health's step only at instants where heal
  and damage both fire into the merge; "stopped updating at all" (RFD 1, record
  0003) overstates it.

## Where the RFDs are wrong

### RFD 1

- The oracle can be GHC. The pool of processes answered every random program
  with none lost. RFD 1 says GHC does not run in CI, so the spike sets
  `BOUGH_ORACLE=skip` there. Question 1.
- A fixed-point loop costs a round for each instant its answer chains
  through, and each round runs the equations again. At the random programs'
  ten transactions that is cheap; a counter over 20,000 transactions ran for
  more than a minute.
- The five test affordances cannot show which child instant an event fell in.
  The comparison checks the order of events within a transaction, not their
  child indices; simultaneity across nodes is checked through nodes that
  combine them and through the order of listener calls.

### RFD 2

- **F3. The loop rule.** "Every path from the definition back to the forward
  token passes through a hold, an accumulator, a split or a defer" accepts
  `c = hold 0 (merge ticks (map (+1) (steps c)))`, since the path passes
  through the hold. The text diverges on it and no evaluation order exists: a
  hold delays reads made before the instant (`snapshot`, `gate`, `sample`, a
  `switch_stream`'s selection), not its steps views. The engine checks that the
  dependency graph stays acyclic, where those reads and `depends` are not
  dependencies and a split's capture and output have none between them. It
  checks at close, at a switch's first link and at relink, and refuses that
  program at close with the cycle's nodes. A test rewires one loop in every
  random program into a same-instant cycle, and the engine refuses every one.
  Question 2.
- **F58.** A `construct`'s nodes are linked at creation, not at commit. A new
  node can close a cycle only through a close or a switch, where it is refused.
- **F59. RFD 2 and RFD 4 conflict.** One `construct` cannot both put a linear
  screen stream in the hold for the `Clone`-free `switch_stream` and send that
  screen's input token to I/O. The construct's output is linear, and sharing a
  `(Stream<Ev>, Input<u32>)` is E0277. It works with `Shared` screens, which
  need `Ev: Clone`, or with a `Clone`-free materializer that splits a stream of
  pairs. Question 4.
- **F12.** Coalescing inputs are not new: Java has `StreamSink(f)` and
  `CellSink(init, f)`, both folding left.
- **F27.** `apply` needs `Leaf`: a cell cannot hold a bare `Box<dyn Fn>`, which
  is not `Trace`; `Leaf<Box<dyn Fn(&A) -> B>>` works with `|f, a| f(a)`.

### RFD 3

- **F62. "Upstream captures need no declaration" is false through switches.**
  A capture that is upstream only through a switch's current selection needs
  one. A navigation `construct` captures `clicks`; a quiet page is selected;
  nothing reaches `clicks`; the construct's next run is a stale-token panic.
  `map_to(token)` needs one too: it is not a closure, and its value is not
  traced.
- **F61, F85, F92. The declaration burden is heavy** where code selects among
  tokens. The engine's own tests needed 68 `depends` calls, 10 anchors for
  tokens a `construct` built, and 13 nodes returned from build closures; 23 of
  33 switch tests failed until declared. The ordinary switch idiom, a closure
  choosing among tokens, needs every candidate declared, and a missing one
  fails at the first move rather than at build: without the declarations every
  random shard failed within four programs. Constructs need three kinds: a
  captured shared stream, a sampled outer cell, and the cells a pick lists.
  Question 3.
- **F64. The automatic trigger never fires on allocation.** "Nodes allocated
  plus roots released since the last collection exceed the live count"
  compares with a live count that already includes every node allocated since
  then. The engine compares with the count the last collection left.
- **F65. Collecting "after a transaction" breaks receive-then-wire** (RFD 4).
  It frees an input a `construct` built and a listener just delivered, before
  I/O code can anchor it. The engine collects when the next transaction opens.
  So the first transaction after the build collects whatever the build closure
  did not root, and an undeclared capture fails at the first send, without the
  stress setting. Question 5.
- **F63.** `depends` has no inverse: a declaration made on a long-lived node
  from inside a `construct` kept fifty screens instead of one.
- **F66.** Garbage is evaluated until it is collected. After 9,000 screens the
  navigation costs 596 µs per transaction without collection and 528 ns with
  it. A dropped handle counts as one released root however much it unrooted.
- **F86.** A same-instant cycle that no root reaches is collected before a
  switch can move into it, so it is never refused.
- **F69.** "A token upstream of itself" is not a cycle a count cannot see; the
  cycle needs the token's node to depend on the cell. Both shapes are
  collected.

### RFD 4

- **F9. The build-time panic on a steps view of an in-place accumulator
  cannot be complete.** A loop closed later, or a `switch_cell` selecting one
  at run time, puts a steps view over it. Decided: `State<S>`, the answer RFD 4
  already named.
- **F14. A `switch_stream`'s outer is neither a dependency nor reach alone.**
  As a dependency it refuses the legal navigation loop through its selection.
  As reach alone, a selector step while the old inner is quiet never relinks.
  It is a watcher: marking follows it only to queue a relink.
- **F36. Fusion costs compile time per chain shape.** Every materializer is
  compiled again for each nested chain type. A program built from data must
  bound the depth: two adapters gave 182 chain types per mode and a 36 s
  release build of the test binary; three gave 1,640 and 367 s. Typing
  `Snapshot` and `Gate` by token kind, `Cell` or `State`, multiplies the chain
  types by 1.65 at depth two (F37).
- **F51.** "A second `switch_stream` on a cell of linear streams is a
  build-time error" holds only for the same cell and its loop aliases; through
  a `switch_cell` it is a run-time panic that poisons.

### RFD 5

- **F4, F16. "Cell listeners run for every marked cell" over-fires.** Marking
  reaches more than what steps: a hold behind a filter that rejects is marked
  and does not step. Read-through cells are ordered, not merely marked, and
  settle "stepped if and only if a dependency stepped" without running user
  code; listeners and memo clears use stepped. The random tests catch a
  mutation that steps every marked cell within the first ten programs.
- **F15.** Nodes created during a transaction run by pull over their
  dependencies, not in creation order: a loop's forward token is created
  before its definition.
- **F46. Relinking one switch at a time refuses a legal program:** two
  switches that reverse a dependency between them in one instant. A's forward;
  p = A + 10; B switching from p to a constant; y = B + 100; A switching from x
  to y. Checked one move at a time it reads as a cycle, and GHC gives A 1 → 102
  and B 11 → 2. The engine moves every switch first and checks the final graph.
  Only a fixed test guards it, since the generator never makes this reversal
  (F88). F47: the one-consumer claims on linear streams are all released before
  any is made, or two switches trading streams panic in one queue order. F48: a
  `switch_stream`'s first link runs its inner at that instant.
- **F19, F56, F57, F87. A cycle through a switch's read past the instant
  overflows the stack** unless each read guards it. All three designs
  overflowed on one. `construct` reaches another with no sample in graph code,
  since a closure's own stream fires at its instant, and a snapshot at
  transaction zero reaches it too. Relink read new selections before checking
  them. Each read now carries Brent's cycle detection over the `switch_cell`s
  it passes, three integers down the call stack, and panics, which poisons. It
  costs about 2 ns per `switch_cell` passed.
- **F11.** Transaction zero has child transactions: a `defer` of a
  `steps_with_current` built in the build fires at `[0,0]`.
- **F72, F73. The error enums fit, with three additions.**
  `PumpError::ForeignGraph`, since a remote transaction's closure runs on the
  driver, and `GraphDropped` on both remote enums. "The offending unit is
  dropped" makes a stale send observable when the unit also carries a live
  send: `try_pump` drops the unit as RFD 5 says, and the release `pump` skips
  the stale send, counts it and runs the rest, following the rule for
  unobservable operations. F25, F68: a foreign or stale token panics before
  `Graph::send` opens its transaction, while inside `Transaction::send` the
  same panic poisons.

### RFD 6

- **F74. The guard, armed "when a transaction begins", refuses I/O code:**
  `graph.transaction(|tx| { tx.send(a, 1); remote.send(a, 2) })`, and a remote
  transaction's own sends. The engine arms it around graph code only:
  evaluation, commit, construct closures and a split's iterator. It costs 12
  instructions per transaction on the share shape, and covers its own graph
  only (F75). Question 6.
- **F77.** A pump runs the units queued when it reaches it. A unit a listener
  queues runs at the next pump; otherwise a listener that always sends keeps
  one pump from returning.
- **F23, F38. A helper generic over the mode cannot write its own closures.**
  `fn f<M: Mode + Accepts<u32>>(b: &mut Build<M>, s: Stream<u32>) -> Cell<u32>
  { s.map(|x| x + 1).hold(b, 0) }` is E0277, since the bound it needs names a
  closure type. It works with the caller's closures, with function pointers, or
  through a per-mode trait one macro implements, which is how the oracle's
  builder runs every program in both modes.
- **F71.** `RemoteTransaction` gains a lifetime, so its sends go straight into
  the transaction the driver opened, unboxed.
- **F79.** The core's thread driver stays in a test. RFD 6 does not say how it
  stops or what it does when a transaction panics, and those would be its API.

### RFD 7

- **F70. `Remote` needs a lock, not only pointer atomics.** `core` and `alloc`
  have no safe lock to share between threads, and a spin lock needs `unsafe`
  and deadlocks against an interrupt. `InputSlot` and `connect` need `std` or
  `critical-section`; `Remote` needs that and pointer atomics. A thumbv7m build
  with neither keeps `pump` and `set_waker` only. Question 7.
- **F76.** A slot feeds one input of one graph: `connect` panics on a connected
  slot, and a dropped graph disconnects its slots. `InputSlot::set_waker` is
  redundant with `Graph::set_waker` once a slot is connected.
- **F42.** The child scheduler must be iterative: a recursive one overflows a
  256 KiB stack on a countdown 100,000 levels deep. The iterative one keeps one
  empty buffer per depth ever reached.
- **F78.** std's mutex is unfair: a writer hammering a slot held off the
  driver's drain for a whole 20,000-write burst. The slot never grows; only
  latency suffers.

### The glossary

- "Loop" states RFD 2's rule, which F3 replaces.
- "Read-through cell": its function "runs only on read" is wrong once steps
  views exist, and the token types are five with `State` (F28).

## The public API, as changed

Each change is named, with its reason, in the commit that makes it.

| Change | Why | Finding |
|---|---|---|
| `Source` sealed and `'static`, with hidden `dependency`, `read_cells`, `pull`; `'static` on the `Stream` and `Shared` impls | Fusion needs a typed pull through every adapter, and a checked downcast needs `'static` | F10 |
| `Node` sealed, with hidden `node_token`, `pull_inner`, `LINEAR` | A listener and a `switch_stream` take or clone as the type says | F10 |
| `Mode` gains hidden `Carrier`, `erase_send`, `Flag: FlagOps`; `Accepts<T>: Mode` gains hidden `erase` | `Graph<Threaded>: Send` derived by the compiler | F8 |
| `M: Accepts<…>` on `input`, `input_coalescing`, `node`, `merge`, `or_else`, `accumulate_mut`, `scan`, `split`, `defer`, `construct`, `switch_stream`, `StreamLoop::close` | A slot keeps a value between transactions; without the bound a `Threaded` graph holding `Rc` type-checks against the skeleton | F8 |
| `State<S>`, `CellRef`, `Lift::Output`, `Cell<State<A>>::switch_cell` | The build-time panic cannot be complete | F9 |
| `StateLoop` and `Build::state_loop` | A loop closed with a `State` needs a forward with no stream view | F33 |
| `snapshot` and `gate` take `C: CellRef`; `Snapshot<S, C, F>`, `Gate<S, C>` | They read a `State` too | F31 |
| `anchor`, `try_anchor` take any `&T: Trace` | Tokens from a `construct` arrive in a tuple or struct | F67 |
| `RemoteTransaction<'a>` | Sends go into the driver's transaction unboxed | F71 |
| `PumpError::ForeignGraph`; `GraphDropped` on both remote error enums | Found at pump; a remote whose graph is gone | F72 |
| `InputSlot` and `connect` need `std` or `critical-section`; `Remote` also pointer atomics | No safe lock otherwise | F70 |
| `connect` panics on a connected slot | A slot feeds one input | F76 |
| `Graph::set_shuffle_seed`; `Graph::statistics` under the `statistics` feature | RFD 1's affordances had no API in the skeleton | |

## Questions for Zefira

Each has a recommendation; the evidence is above.

1. **The oracle.** (a) Keep GHC as the oracle and run it in CI: an apt
   install, and the suite runs in about 26 s once built. (b) Port the
   semantics to Rust as RFD 1 plans, with fixed-point loops. (c) GHC locally,
   skipped in CI, as the spike has it. *Recommended: (a).* F1 means a port
   needs the fixed-point machinery anyway, and the harness exists and has
   found four defects in the text itself. RFD 1's policy line changes.
2. **The loop rule.** Replace RFD 2's rule and the glossary's with the
   dependency-graph rule of F3. *Recommended: yes.*
3. **Declarations through switches** (F61, F62, F85, F92). (a) Keep RFD 3's
   model and document the burden: whatever a closure chooses among, or a
   `map_to` names, is declared. (b) A switch constructor that takes its
   candidates, so they reach without a declaration. *Recommended: (a) now*, and
   measure the burden on a real application before (b).
4. **The screen pattern** (F59). (a) A `Clone`-free materializer that splits a
   stream of pairs into two linear streams. (b) Require `Shared` screens and
   `Ev: Clone`. *Recommended: (a)*; it keeps RFD 4's `Clone`-free path whole.
5. **Collection** (F64, F65). Collect when the next transaction opens, with the
   trigger measured against the live count the last collection left.
   *Recommended: yes*, with its consequence stated in RFD 3: the first send
   collects whatever the build did not root.
6. **The guard** (F74). Arm it around graph code, not for the whole
   transaction. *Recommended: yes.*
7. **The targets** (F70). Input slots need `std` or `critical-section`, and
   `Remote` also pointer atomics. *Recommended: yes*; the alternative is
   `unsafe` in the core.
8. **A third patch to the oracle** (F89). Restrict `Split`'s input to events at
   or after its creation, the way F6 chops `SwitchC`'s outer, so the random
   programs can split inside bodies at child instants. *Recommended: yes*; the
   answer the text gives there is one no implementation gives.

The rest are corrections to the RFDs' text with no choice in them: F4, F11,
F12, F14, F15, F17, F19, F22, F27, F28, F36, F42, F46 to F48, F51, F56 to F58,
F63, F66, F69, F71 to F73, F76, F77.

## What the spike did not settle

- **Performance beyond the share shape.** The frame shape runs 52 ns per node.
  RFD 1's UI shape was not built. The relink check costs about 9 ns per node
  upstream of the new inner (F50): 121 µs per switch with ten thousand upstream
  nodes, which the UI shape would feel.
- **Two things untested against GHC.** Loops inside construct bodies, since the
  oracle runs bodies for events before their construct existed (O4); and the
  engine's pull of new nodes out of creation order inside a body, which only a
  loop closed at build exercises.
- **Child indices** are not compared, as above.
- **The bounded tier, the Bevy and web adapters, and the `debug-dump`
  feature** were out of scope.
- **The oracle's own gaps**, all minor: O4 above; the Haskell unit tests run
  without a time limit (O5); a GHC build orphaned by killing the test binary
  leaks a process (O6).

## Every finding

Numbers are the ones the `bough` commits and comments cite. O1 to O6 are the
oracle's review findings.

**The semantics and the research**

- F1. The text hangs on a legal loop whose events depend on values; loops are computed by fixed point.
- F2. Sodium's common tests give split children the wrong times.
- F6. `SwitchC` for a switch created after its outer stepped is out of time order; patched.
- F7. `Split` fed by its own children is out of time order; patched.
- F20. sodium-rust#52 loses steps only where heal and damage fire together.
- F21. The PDF has no numbered sections.
- F22. A loop through `defer` with no filter never ends.
- F44. `Execute` and `SwitchS` have no creation time; unobservable.
- F89. `Split` has no creation time, and that is observable at child instants.

**Loops and the protocol**

- F3. RFD 2's loop rule accepts a same-instant cycle through a steps view; the dependency graph must stay acyclic.
- F4. "Every marked cell" over-fires; cells use stepped.
- F11. Transaction zero has children.
- F13. The skeleton's `defer` documentation said "a child transaction of its own"; `defer` shares index 0.
- F15. New nodes run by pull, not in creation order.
- F16. Read-through cells are ordered.
- F17. A read-through function runs once per step with a steps view.
- F19. A cycle through a post-instant read overflowed the stack in every design.
- F40. The engine matched GHC on every child-transaction scenario.
- F41. The design's sketch read an iterator past its first `None`.
- F42. The child scheduler must be iterative.
- F45. The engine matched GHC on every switch program.
- F46. Relinking one switch at a time refuses a legal program.
- F47. Linear-stream claims must be released before any is made.
- F48. A `switch_stream`'s first link runs its inner.
- F49. A read of a `switch_cell` before its first link overflowed the stack (see F56).
- F50. The relink check costs about 9 ns per upstream node.
- F51. The one-switch rule is partly a run-time check.
- F55. `construct` works as `Execute` with no design change.
- F56. F49 is reachable with no sample; Brent's cycle detection guards every read.
- F57. Relink read new selections before checking them.
- F58. A construct's nodes are linked at creation.

**Values, cells and the API**

- F8. The skeleton's `Threaded` mode was unsound; erasure inside `Accepts` makes `Send` a compiler fact.
- F9. The build-time panic for in-place accumulators cannot be complete; `State<S>`.
- F10. `Source` and `Node` are sealed with hidden methods.
- F12. Coalescing inputs are not new.
- F14. A `switch_stream`'s outer is a watcher.
- F18. `once` is the only adapter whose denotation needs a creation time.
- F23. A helper generic over the mode cannot write its own closures.
- F25. Where a foreign token poisons and where it does not.
- F26. `#[must_use]` on `Listener` is worth adding.
- F27. `apply` needs `Leaf`.
- F28. The glossary's read-through entry and token count.
- F29. A promoted memo is reused across inputs.
- F30. What `State<S>` cost.
- F31. `Snapshot` and `Gate` carry the token type.
- F32. The engine matches GHC on the sodium-rust#52 shape and the health-and-shield slice.
- F33. `StateLoop` is new.
- F34. The allocation test counted libtest's own thread.
- F37. Typing adapters by token kind multiplies chain types.
- F38. A per-mode trait lets a builder run in both modes.
- F39. The settle rule governs transaction zero too.
- F43. `split` and `defer` need `Accepts` bounds.
- F52. `switch_stream` needs an `Accepts` bound.
- F59. RFD 2 and RFD 4 conflict over screens that carry their own inputs.
- F60. A swapped build context is caught by the nested build.

**Memory**

- F61. `Trace` plus `depends` suffice; the burden is heavy.
- F62. Captures reached through a switch need a declaration.
- F63. `depends` has no inverse.
- F64. The automatic trigger never fires on allocation.
- F65. Collecting after a transaction breaks receive-then-wire.
- F66. Garbage is evaluated until collected.
- F67. `anchor` takes any `&T: Trace`.
- F68. The error enums fit collection.
- F69. RFD 3's cycle wording.
- F85. The switch idiom needs every candidate declared.
- F86. An unrooted cycle is collected before it can be refused.
- F92. Constructs need three kinds of declaration.

**The I/O edge**

- F70. `Remote` and input slots need a lock.
- F71. `RemoteTransaction` has a lifetime.
- F72. `PumpError::ForeignGraph` and `GraphDropped`.
- F73. Dropping a unit whole makes a stale send observable.
- F74. The guard is armed around graph code.
- F75. The guard covers its own graph.
- F76. The slot rules RFD 7 leaves open.
- F77. A pump runs the units queued when it reaches them.
- F78. std's mutex is unfair.
- F79. Drivers are a few dozen lines, and the edge composes.
- F80. The edge allocates only on the sending side.
- F81. Where the edge departs from the brief.
- F82. Fifty `compile_fail` tests refuse `Rc` in `Threaded`.
- F83. thumbv6m keeps input slots and `pump` with `critical-section`.
- F91. The fold law holds against GHC.

**Performance and the tests**

- F24. The share shape is 2.47 times its baseline.
- F35. Tens of thousands of first-order programs agree with GHC; twelve mutations caught.
- F36. Fusion costs compile time per chain shape.
- F53. Programs with loops and children agree; nine mutations caught.
- F54. More materializers raise the build time of the test binary.
- F84. Programs with switches agree; twelve mutations caught.
- F87. The random tests found both switch overflows independently.
- F88. The generator never makes F46's legal reversal.
- F90. Programs with constructs agree.

**The oracle**

- O1. A fixed round cap refused long well-founded loops, and nested loops failed on the outer's start; fixed.
- O2. The iteration leaked 583 MB on a long counter; fixed.
- O3. GHC's derived `Read` accepts bare negative numbers.
- O4. Construct bodies run for events before their construct existed.
- O5. The Haskell unit tests have no time limit.
- O6. A GHC build orphaned by SIGKILL leaks.

## Addendum, 2026-09-25: question 3, revisited

_Zefira reopened question 3 after reading this note, and proposed a
different model for capture declarations. The spike proves it in three
commits on the same branch, from `06972e0` to `4dc2ff4`. It replaces the
recommendation above._

### The model

The graph traces every value it holds. A closure is the one thing it
cannot look inside. So every value a `move` closure captures that holds a
token is declared, with `depends`, on the node the closure belongs to. For
an adapter, that is the node its chain becomes.

The rule finds every capture. Graph closures are `'static`, so a closure
can only hold a token by owning it: without `move`, the compiler refuses
the borrow (E0373). It never asks whether a capture is upstream, which is
the question F62 showed a switch can change at run time. It covers F62 and
F92's three kinds of capture alike. Declaring a token the node reaches
anyway costs one reach entry.

### What the adapters hold

A chain already reported the cells `snapshot` and `gate` read, through a
hidden `read_cells`, and every materializer recorded them as reach. That
was `Trace` under another name. Adapters get no graph context, so a token
an adapter holds matters only if it can leave in an event:

| Adapter | Holds | Seen by the collector | Needs a declaration |
|---|---|---|---|
| `map(f)` | a closure | no | what `f` can return |
| `filter(p)` | a closure | no | never: `p` returns `bool` |
| `filter_map(f)` | a closure | no | what `f` can return |
| `map_to(v)` | a value | yes, now | never |
| `snapshot(c, f)` | a cell and a closure | the cell | what `f` can return |
| `gate(c)` | a cell | yes | never |
| `once()` | a flag | nothing to see | never |

`map_to` was the one gap. It holds a value for as long as its chain lives,
and nothing looked inside it. The rule asks for more than the table needs,
a filter's captures for one, at one reach entry each.

### What changed on the spike

- **F93. Chains are `Trace`.** `Source` requires `Trace` in place of
  `read_cells`. `snapshot` and `gate` visit their cell, `map_to` its
  value, and the other adapters pass the walk to their source. A
  materializer traces the chain once, when it builds the node, and records
  what the walk finds besides the dependency. A chain never changes after
  it is built, so once is enough. No node's reach changed. (`cb8b274`)
- **F94. `map_to` requires `Trace` of its value.** RFD 3 puts the bound on
  the operations that persist a value, and `map_to` is one. A token in the
  value is in the node's reach with no declaration. The program that was a
  stale token without a declaration now runs without one. Every `map_to`
  in the repository already passed a `Trace` value; a foreign type goes in
  a `Leaf`. (`99458fe`)
- **F95. `depends` takes any `Trace` value, as `anchor` does (F67).** A
  struct or a `Vec` of tokens a closure captures is declared as one value.
  A new test moves a struct of panels, one of them in a `Vec`, into a
  closure that picks among them. One declaration keeps every panel, and
  without it the first move is a stale token. Inline slices of tokens
  compile unchanged. Five places named the element type `&dyn TokenRef`
  and now name `&dyn Trace`, since turning one trait object into another
  needs Rust 1.86 and the minimum is 1.85. Two of them built a `Vec` of
  tokens by hand, and are one value now. (`4dc2ff4`)

The 532 tests pass in debug and in release, and 8,192 random programs
with seed 20260924 still agree with GHC.

### What it does not change

- A forgotten declaration is still a stale token at use, not a compile
  error.
- A value is traced when it is declared, and a chain when its node is
  built. A token added later through interior mutability is not seen.
  That takes a hand-written `Trace`, and the I/O code that adds the token
  anchors it, as RFD 3 already asks.
- Adapter types implement the public `Trace` now, so a chain satisfies a
  `Trace` bound. A chain that is never built does nothing, so that is
  harmless.

### Question 3, as it stands

(a), with this model. RFD 3 changes in four places: the capture paragraph
states the `move` rule; `map_to` joins the operations that persist a
value; reach includes what a chain holds; and `depends` takes any `Trace`
value. (b), a switch constructor that takes its candidates, is not needed.
Closure-taking twins that take their captures as an argument were
considered and rejected: they double the API, and they are another way to
write `depends`.
