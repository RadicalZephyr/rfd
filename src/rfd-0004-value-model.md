# Value Model: Linear Streams, Explicit Sharing, and Where Clone Happens

**State:** discussion · **Authors:** Zefira Shannon, Claude

Sodium hands values around by reference in garbage-collected
languages, and `sodium-rust` requires `Clone` on everything and clones
at every fan-out. Bough puts `Clone` only where a value is genuinely
duplicated, lets non-`Clone` values flow through streams, and makes
the user confront the point where duplication happens. This RFD is
also where the distinction between shared nodes and intermediate
combinators from the README becomes concrete.

## By Value Through Streams, By Reference From Cells

Stream functions take their event by value and return owned
values: `map` takes `A` and returns `B`, `snapshot` takes `A` and
`&B`, `merge` takes `A, A`, and `filter` takes `&A` since it does not
consume. The identity function is `|a| a`, not `|a| a.clone()`. Cell
functions take references: `map_cell` and `lift` take `&A`, and
`accumulate` takes `A, &S`. Stream listeners take `A`; cell listeners
take `&A`.

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
has `Item`, so every constructor and `listen` accept either through
one trait, and the dependency is compiled into the node at
construction: a linear dependency takes the event out of the slot, a
shared one clones it.

Linearity is what lets `hold` and `merge` drop their `Clone` bounds.
The hold is the sole consumer and moves the event into its
committed value; merge moves whichever input fired through its
function. The `Clone` points that remain are the operations that
genuinely duplicate a value:

- `share`;
- `map_to`, which emits one value repeatedly;
- a caller of `sample` who clones; `sample` itself returns a reference
  and has no bound.

Cells have no stream view in graph code. Sodium's `updates` and
`value` are operational primitives and become the listeners
`listen_steps` and `listen_cell` ([RFD 2](./rfd-0002-strong-io-separation.md)),
which read the committed value after commit by reference and need no
`Clone` either.

We considered a single `Copy` stream token with a build-time panic on
a second consumer. It finds the bug on first run; the move-only token
finds it at compile time, which is the point of the model. The cost is
that a linear stream inside a value is unreachable for derivation,
because cell values are read by reference and a function on
`Cell<Item>` cannot move `item.clicks` out. Any stream that travels
inside a value must be shared, which is the confrontation we want. I/O code receives a linear stream only as a by-value event, and
since listeners have no graph access, it attaches a listener only
after `send` returns: dynamic wiring from I/O is collect, then wire.

A cell can hold linear tokens directly, `hold(b, init)` over a stream
of streams, and `switch_stream` may switch over such a cell, exactly
one switch per such cell, checked when a second is constructed. This
is the `Clone`-free path for the main dynamic pattern: `construct`
builds a screen, a hold keeps the current one, one switch reads its
events. Requiring `Shared` for every switched stream would put a
`Clone` bound on every dynamically constructed event type, which undoes
half the benefit.

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
`accumulate`, `accumulate_mut`, `scan`, `share`, `node`, `merge`,
`or_else`, `split`, `defer`, `construct`, `switch_stream`, and on
cells `map_cell`, `lift` and `switch_cell`. Those take `b`.

```rust
input.map(f).filter(p).snapshot(c, g).hold(b, 0)
```

A chain cannot be stored in a value or returned from build until it is
materialized, like an iterator before `collect`; `node(b)` materializes
a chain as a linear stream with an identity of its own. The marking
walk and the dependents lists see one node per chain, and the
per-adapter cost is a direct call, so a chain costs what the imperative
baseline costs. The alternatives were one node per combinator, a
virtual call and a slot per adapter, and boxed adapters appended to a
chain node, which removes the bookkeeping but keeps a virtual call per
adapter. Fusion is the iterator-like API the README promises, and it is
the cheap version of a compiled graph for the one case that dominates
real graphs; the node graph itself stays an interpreter ([RFD 5](./rfd-0005-transaction-protocol.md)).

`once` carries its state inside the fused closure and updates it
during evaluation. A chain evaluates at most once per transaction, so
this is indistinguishable from updating at commit.

## Cells

A hold is the stateful cell: it moves its event into its
committed value at commit. `map_cell`, `lift` and `switch_cell` are
read-through. They compute from their inputs' current values when
read, memoized against the inputs' version counters, so the function
runs zero times if the cell is never read and at most once per input
change per reader path. A cell read once per frame while its input
steps a thousand times per frame costs one call. The memo sits behind
interior mutability, because `sample` takes its context by shared
reference so that two samples can appear in one expression: a
`Cell`-style slot in `Local` mode and a mutex in `Threaded` mode
([RFD 6](./rfd-0006-io-edge.md)). Functions must be
pure. The engine calls them at most once per version of their inputs,
and not at all if the cell is never read. We considered eager
evaluation at commit, which matches Sodium's call pattern and makes
sample a single load. It is never better than read-through by more than a
version compare, and it is unboundedly worse for the high-rate shape
read by a slow observer, which is one of the three workloads.

`lift` is binary and composes by chaining, since the intermediate
cells are read-through and cost nothing; Sodium's `apply`, a cell of
functions applied to a cell, is `lift` with `|f, a| f(a)`.

`switch_cell` is read-through in the semantics' own terms:
`at (SwitchC c) t` is `at (at c t) t`, two pointer chases on sample
and no state of its own.

There is no stream view of a cell in graph code. The listeners
`listen_steps` and `listen_cell` are the only way to turn steps into
events, and they belong to I/O code.

## In-Place Accumulation

`accumulate(b, init, f)` is the semantics' `hold init (snapshot f s c)`
with `f: Fn(A, &S) -> S`, and on collections it is quadratic: every
event clones the collection to push one element. `accumulate_mut(b,
init, f)` takes `f: FnMut(A, &mut S)` and runs it at commit, after
every reader in the transaction has seen the pre-transaction state, so
a `Vec` accumulator is a push. Observationally it is Sodium's `accum`,
because the function cannot read the graph, and no observer can see
the mutation: every reference is scoped to one call and the mutation
happens when none exists.

Because a cell has no stream view in graph code, in-place accumulation
needs no restriction at all. Everything that reads the cell reads it
either during evaluation, as it was before the instant, or after
commit, from a listener, and the mutation happens between the two. An
earlier draft gave cells a stream view and had to forbid it on the
in-place form, since the new state does not exist until commit; moving
the stream views to I/O code dissolved the problem. Dropping in-place accumulation
would leave an asymptotic cliff against the performance bar for any
workload that accumulates, and persistent collections cost roughly ten
times a `Vec` push. Dropping `accumulate`, the semantics' form, would lose a
legal and common stream view.
