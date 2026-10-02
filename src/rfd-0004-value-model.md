# Value Model: Linear Streams, Explicit Sharing, and Where Clone Happens

**State:** discussion · **Authors:** Zefira Shannon, Claude

Sodium hands values around by reference in garbage-collected
languages, and `sodium-rust` requires `Clone` on everything and clones
at every fan-out. Bough puts `Clone` only where a value is genuinely
duplicated, lets non-`Clone` values flow through streams, and makes
the user confront the point where duplication happens. This RFD is
also where the distinction between shared nodes and intermediate
combinators that the `bough` repository's README promises becomes
concrete.

## By Value Through Streams, By Reference From Cells

Stream functions take their event by value and return owned
values: `map` takes `A` and returns `B`, `snapshot` takes `A` and
`&B`, `merge` takes `A, A`, and `filter` takes `&A` since it does not
consume. The identity function is `|a| a`, not `|a| a.clone()`. Cell
functions take references: `map_cell` and `lift` take `&A`,
`accumulate` takes `A, &S` and returns `S`, and `scan` takes `A, &S`
and returns `(B, S)`. Stream listeners take `A`; cell listeners take
`&A`.

A reference to a cell's value lives for exactly one call. A stored
closure is `'static`, and the reference it receives has an anonymous
lifetime bounded by the call, so keeping it is a compile error rather
than a rule. Keeping a cell value means cloning it, and the clone is a
snapshot as of that instant. The one way to see a later change through
a kept value is interior mutability inside the value, and that breaks
every FRP system identically, because a listener that mutates through
an `Rc<RefCell<_>>` rewrites every past snapshot. That is a user
violation, not something this model introduces.

## Streams Are Linear; Fan-Out Is Explicit

A `Stream<A>` is move-only and has exactly one consumer. Every
constructor consumes it. Using it twice is a compile error, and the
fix is to say so: `share(b)` returns a `Shared<A>`, which is `Copy`,
requires `A: Clone`, and clones on every read. Both implement
`Source`, a trait with an associated `Event` type the way `Iterator`
has `Item`, so every constructor accepts either through one trait, and
the dependency is compiled into the node at construction: a linear
dependency takes the event out of the slot, a shared one clones it.
`listen` is the exception: it accepts the two node types only, through
`Node`, which adapter types do not implement, so no chain can be
listened to ([RFD 2](./rfd-0002-strong-io-separation.md)).

Linearity is what lets `hold` and `merge` drop their `Clone` bounds.
The hold is the sole consumer and moves the event into its
committed value; merge moves whichever input fired through its
function. The `Clone` points that remain are the operations that
genuinely duplicate a value:

- `share`;
- `map_to`, which emits one value repeatedly;
- `steps` and `steps_with_current`, which emit a value the cell also
  keeps;
- a caller of `sample` who clones; `sample` itself returns a reference
  and has no bound.

The listeners `listen_steps` and `listen_cell`, the I/O forms of the
two stream views ([RFD 2](./rfd-0002-strong-io-separation.md)), read
the committed value after commit by reference and need no `Clone`.

We considered a single `Copy` stream token with a build-time panic on
a second consumer. It finds the bug on first run; the move-only token
finds it at compile time, which is the point of the model. The cost is
that a linear stream inside a value is unreachable for derivation,
because cell values are read by reference and a function on
`Cell<Item>` cannot move `item.clicks` out. Any stream that travels
inside a value must be shared, which is the confrontation we want. I/O
code receives a linear stream only as a by-value event, and a
collection runs after each unit, so a construct sends what it builds
out anchored, with `b.anchor` ([RFD 3](./rfd-0003-memory-model.md)).
Since listeners have no runtime access, I/O code then listens through
the `Runtime` after `send` returns, or through a handle from the
listener, which takes effect at the next pump.

A cell can hold linear tokens directly, `hold(b, init)` over a stream
of streams, and `switch_stream` may switch over such a cell, exactly
one switch per such cell. A second switch over the same cell, or over
a loop's forward and its definition, is a panic at build. A
`switch_cell` can still select, at run time, a cell whose streams
another switch already takes from, since which cell it selects is only
known then, and that is a run-time panic that poisons the runtime. This
is the `Clone`-free path for the main dynamic pattern: `construct`
builds a screen, a hold keeps the current one, one switch reads its
events. Requiring `Shared` for every switched stream would put a
`Clone` bound on every dynamically constructed event type, which undoes
half the benefit.

A construct often makes a screen together with its own input, and
then the screen goes into the hold and the input out to I/O code. The
construct's output is linear, so it can't go both ways, and sharing
it would need the screen's events to be `Clone`. `unzip` splits a
stream of pairs into two linear streams with no `Clone`: each pair's
halves move apart in the same instant. It denotes two maps, one taking
each half, so the oracle needs nothing new.

```rust
let made = opens.construct(b, |b, id| {
    let (keys, keys_in) = b.input::<u32>();
    let screen = keys.map(move |key| id * 100 + key).node(b);
    (screen, b.anchor(keys_in))
});
let (screens, inputs) = made.unzip(b);   // screens to the hold, inputs to I/O code
let shown = screens.hold(b, idle).switch_stream(b);
```

We considered requiring `Shared` screens instead, which puts the
`Clone` bound back on every screen's events.

## Chains Fuse, Iterator Style

Nothing can observe the values between the adapters of a linear stream,
so the adapters fuse the way iterator adapters do. `map`, `filter`,
`filter_map`, `map_to`, `snapshot`, `gate` and `once` are adapters: each
returns its own type, such as `Map<S, F>`, all of them `Source`, and
none takes a build context. A chain is a linear sequence of adapters
with no materializer. `Source` carries its event as an associated
type, `Event`, rather than a type parameter: an adapter such as
`Map<S, F>` cannot implement a generic `Source<A>`, because `A` would
appear only in its bounds (E0207), which a stub of the API surface
confirmed. A chain becomes one node with one
monomorphized closure when something materializes it: `hold`,
`accumulate`, `accumulate_mut`, `scan`, `share`, `node`, `unzip`,
`merge`, `or_else`, `split`, `defer`, `construct`, `switch_stream`,
and on cells `map_cell`, `lift` and `switch_cell`. Those take `b`.

```rust
input.map(f).filter(p).snapshot(c, g).hold(b, 0)
```

A chain is `Trace`, so it can be stored in a value or returned from
build like any other `Trace` value, and one that no materializer
consumes does nothing, like an iterator before `collect`; `node(b)`
materializes a chain as a linear stream with an identity of its own.
The marking
walk and the dependents lists see one node per chain, and the
per-adapter cost is a direct call, so a chain costs what the imperative
baseline costs. The alternatives were one node per adapter, a virtual
call and a slot per adapter, and boxed adapters appended to a chain
node, which removes the bookkeeping but keeps a virtual call per
adapter. Fusion is the iterator-like API the `bough` README promises,
and it is the cheap version of a compiled graph for the one case that
dominates real graphs; the node graph itself stays an interpreter
([RFD 5](./rfd-0005-transaction-protocol.md)).

Fusion costs compile time per chain shape, since every materializer is
compiled again for each nested chain type. A program that builds its
chains from data has to bound their depth: on the engine spike, the
test binary that builds programs from data had 182 chain types per
mode and a 36 s release build at a depth of two adapters, and 1,640
and 367 s at three
([research](./research/2026-09-24-engine-feasibility-spike.md)).

`once` carries its state inside the fused closure and sets it during
evaluation. A chain evaluates at most once per transaction, so
this is indistinguishable from updating at commit.

## Cells

A hold is the stateful cell: it moves its event into its committed
value at commit, and an accumulator is stateful the same way.
`map_cell`, `lift` and `switch_cell` are read-through: they compute
from their inputs' current values when read and memoize the result, so
the function runs zero times if the cell is never read and at most
once per step. A cell read once per frame while its input
steps a thousand times per frame costs one call.

A read-through cell is a node with an identity, and its inputs are its
dependencies: it steps whenever an input steps. The marking walk
reaches it through the dependents lists like any stream node and
orders it like one, but settling it runs no user code: marking reaches
more than what steps, since a hold behind a filter that rejects is
marked and doesn't step, so a read-through cell stepped if and only if
one of its dependencies stepped. At commit the memo of every
read-through cell that stepped is cleared; after commit its listeners
run, and the first read computes the new value. Nothing less would
make `listen_cell` on a read-through cell fire at all, since a listener
needs a step to fire on. The first draft kept read-through cells
outside the dependents graph and compared version counters on read,
and under it the flagship example in
[RFD 2](./rfd-0002-strong-io-separation.md), a listener on a
`map_cell`, would have fired once at registration and never again.

The memo is a `core::cell::OnceCell<A>`. It hands out `&A` from a
shared borrow, which is what lets two samples compose in one
expression, and it can only be cleared through `&mut`, which commit
has and no reader does: holding a sampled reference across a `send` is
a borrow error (E0502), not a rule. The engine's tests pin both.
`OnceCell` is `Send` when `A` is, which is all `Runtime<Threaded>`
needs, since every entry that drives the runtime takes `&mut self` and
contention cannot occur;
the first draft named a `Cell`-style slot and a mutex, and neither can
return a reference, because `Cell` has no `borrow` and a mutex guard
dies at the end of `sample`.

Functions must be pure. The engine calls a read-through function at
most once per step and not at all if the cell is never read. A `steps`
view of the same cell computes the value during evaluation, and the
value it computes goes into the memo at commit, so a steps view and a
reader after it still share one call. We considered eager evaluation
at commit, which matches Sodium's call pattern and makes sample a
single load. It is never better than read-through by more than a flag
check, and it is unboundedly worse for the high-rate shape read by a
slow observer, which is one of the benchmark shapes
([RFD 1](./rfd-0001-guiding-principles.md)).

`lift` takes a tuple of cells, arities two to six as Sodium ships them,
and one function over references to all of them:
`(price, quantity).lift(b, |p, q| p * q)`. There is no binary method to
chain, because `a.lift(b, x, f).lift(b, y, g)` composes two functions
rather than lifting three cells, and expressing a three-argument
function through it needs an intermediate cell that clones two inputs
on every read. Sodium's `apply`, a cell of functions applied to a
cell, is `(cf, ca).lift(b, |f, a| f(a))` with the cell holding
`Leaf<Box<dyn Fn(&A) -> B>>`, since cell values are read by reference
and a bare `Box<dyn Fn>` isn't `Trace`. Its
simultaneity rule, the semantics' `knit`, is what marking gives: two
inputs stepping in one instant mark the lifted cell once.

`switch_cell` is read-through on read, `at (SwitchC c) t` is
`at (at c t) t`, two pointer chases and no memo. It has state all the
same: the inner it currently depends on. The semantics'
`steps (SwitchC c t0)` splices in every step of the selected inner, so
the node is a dependent of that inner, relinked at commit whenever the
outer steps, and it is marked at creation and at every switch instant
even when the new inner is quiet
([RFD 5](./rfd-0005-transaction-protocol.md)).

A `switch_cell` built inside `construct` starts from the inner its
outer holds at its creation, as Sodium's Java does. The semantics text
scans the outer from its initial value instead, so a switch built after
its outer stepped gets steps out of time order, from before its
creation, and from the old inner. That breaks the text's own rules, so
Bough follows the rules and the oracle patches the text to agree, as
[RFD 1](./rfd-0001-guiding-principles.md)'s policy says; a test quotes
the text's answer beside Bough's.

The stream views of a cell are `steps` and `steps_with_current`,
Sodium's `updates` and `value`, materializers on `Cell` that carry the
book's warning ([RFD 2](./rfd-0002-strong-io-separation.md)). Both
require `A: Clone`, since a hold keeps its value and the stream needs
one of its own, and both are stream nodes evaluated in order like any
other: a step in the cell's inputs is one event carrying the
post-instant value, computed during evaluation from the inputs'
post-instant values. `steps_with_current` also fires at its creation
instant with the post-instant value, which is the semantics'
`coalesce (flip const) ((t0, a) : sts)`: a creation and a step in one
instant are one event carrying the new value. The listeners
`listen_steps` and `listen_cell` are the I/O side of the same two
views.

## Accumulation

`accumulate(b, init, f)` with `f: Fn(A, &S) -> S` is the semantics'
knot: `let c = hold(init, snapshot(f, s, c))`, a hold whose input
snapshots the hold itself. The cell being snapshotted is the result,
which is what makes an accumulator a legal way to close a loop: it is
already a loop through a hold. Written as a straight line over some
other cell it would be a different operator, one that never reads its
own state, and it would typecheck. On collections it is quadratic:
every event clones the collection to push one element.

`accumulate_mut(b, init, f)` takes `f: FnMut(A, &mut S)`. The `&mut S`
is the asymptotic fix: a `Vec` accumulator is a push. Running `f` at
commit, after every reader in the transaction has seen the
pre-transaction state, is what makes the mutation unobservable: every
reference to the state is scoped to one call, and the mutation happens
when none exists, so observationally it is Sodium's `accum`.

Because the new state does not exist until commit, an in-place
accumulator has no stream view, since the event it would carry has no
value during evaluation. So `accumulate_mut` returns a `State<S>`, a
token of its own that every operation reading a cell accepts through
the `CellRef` trait. A `map_cell` over a `State`, or a `lift` with one
among its cells, gives a `State`, and so does a `switch_cell` over a
cell of states. A `State` has no `steps` and no `steps_with_current`,
so asking for one is a compile error (E0599), and `state_loop` closes a
loop over one ([RFD 2](./rfd-0002-strong-io-separation.md)).
`listen_steps` and `listen_cell` read the committed state after commit
and work as usual. This is the one restriction the in-place form
carries, checked at compile time, by the type. A build-time panic was
the first plan, and it couldn't be complete: a loop closed later, or a
`switch_cell` that selects a state at run time, puts a steps view over
one. Dropping in-place accumulation would leave an asymptotic cliff
against the performance bar for any workload that accumulates, and
persistent collections cost roughly ten times a `Vec` push. Dropping
`accumulate`, the semantics' form, would lose a legal and common stream
view.

`scan(b, init, f)` with `f: Fn(A, &S) -> (B, S)` is Sodium's `collect`:
at each event it emits `B` and holds `S`. It is a node of its own, and
its state is private to it: the state updates when the node runs, at
most once per transaction, so `f` always reads the state from before
the instant. Nothing else reads it, so updating it during evaluation is
indistinguishable from updating it at commit, for the reason `once`'s
flag is. `Iterator::scan` is the nearest Rust name and no more than
that: it takes `(&mut S, A)` and ends the iteration on `None`, while a
stream has no end and every event yields one output.
