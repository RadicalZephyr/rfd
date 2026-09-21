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

Stream functions take their occurrence by value and return owned
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
`Source<A>`, so every constructor and `listen` accept either through
one trait, and the edge is compiled into the node at construction: a
linear edge takes the occurrence out of the slot, a shared edge clones
it.

Linearity is what lets `hold` and `merge` drop their `Clone` bounds.
The hold is the sole consumer and moves the occurrence into its
committed value; merge moves whichever input fired through its
function. The `Clone` points that remain are the operations that
genuinely duplicate a value:

- `share`;
- `steps` and `steps_with_current` on a hold, which duplicate the
  hold's input;
- `map_to`, which emits one value repeatedly;
- `steps` of a `switch_cell`, which copies the inner cell's value into
  an occurrence;
- a caller of `sample` who clones; `sample` itself returns a reference
  and has no bound.

We considered a single `Copy` stream token with a build-time panic on
a second consumer. It finds the bug on first run; the move-only token
finds it at compile time, which is the point of the model. The cost is
that a linear stream inside a value is unreachable for derivation,
because cell values are read by reference and a function on
`Cell<Item>` cannot move `item.clicks` out. Any stream that travels
inside a value must be shared, which is the confrontation we want. The
I/O world receives a linear stream only as a by-value occurrence, and
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

Nothing can observe the values between the stages of a linear stream,
so the stages fuse the way iterator adapters do. `map`, `filter`,
`filter_map`, `map_to`, `snapshot`, `gate` and `once` are stages: each
returns an adapter type such as `Map<S, F>`, all of them `Source<A>`,
and none takes a build context. A chain becomes one node with one
monomorphized closure when something materializes it: `hold`,
`accumulate`, `accumulate_mut`, `scan`, `share`, `node`, `merge`,
`or_else`, `split`, `defer`, `construct`, `switch_stream`, and on
cells `steps`, `steps_with_current`, `map_cell`, `lift` and
`switch_cell`. Those take `b`.

```rust
input.map(f).filter(p).snapshot(c, g).hold(b, 0)
```

A chain cannot be stored in a value or returned from build until it is
materialized, like an iterator before `collect`; `node(b)` materializes
a chain as a linear stream with an identity of its own. The marking
walk and the dependents lists see one node per chain, and the
per-stage cost is a direct call, so a chain costs what the imperative
baseline costs. The alternatives were one node per combinator, a
virtual call and a slot per stage, and boxed stages appended to a
chain node, which removes the bookkeeping but keeps a virtual call per
stage. Fusion is the iterator-like API the README promises, and it is
the cheap version of a compiled graph for the one case that dominates
real graphs; the node graph itself stays an interpreter (RFD 5).

`once` carries its state inside the fused closure and updates it
during evaluation. A chain evaluates at most once per transaction, so
this is indistinguishable from updating at commit.

## Cells

A hold is the stateful cell: it moves its occurrence into its
committed value at commit. `map_cell`, `lift` and `switch_cell` are
read-through. They compute from their inputs' current values when
read, memoized against the inputs' version counters, so the function
runs zero times if the cell is never read and at most once per input
change per reader path. A cell read once per frame while its input
steps a thousand times per frame costs one call. Functions must be
pure, and the documented contract is that the engine may call them any
number of times per change, because a stream view of the same cell
computes independently during evaluation. We considered eager
evaluation at commit, which matches Sodium's call pattern and makes
sample a single load. It is never better than lazy by more than a
version compare, and it is unboundedly worse for the high-rate shape
read by a slow observer, which is one of the three workloads.

`switch_cell` is read-through in the semantics' own terms:
`at (SwitchC c) t` is `at (at c t) t`, two pointer chases on sample
and no state of its own.

Stream views of cells are nodes built on demand. `steps` of a hold
clones, because the hold will move that value. `steps` of a derived
cell needs no `Clone`: it reads the post-transaction values of its
inputs by reference, which exist because the pending occurrence sits
in the hold's slot until commit.

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

The cost is the stream view. `steps(accumulate)` at instant t carries
the new state and is simultaneous with the input, and downstream logic
may consume it during t. With in-place mutation the new state does not
exist until commit, so there is nothing to put on the stream at t, and
producing one by cloning during evaluation is `accumulate` again. An
in-place accumulator therefore has no stream view: `steps`,
`steps_with_current`, and `steps` of any cell derived from it are
build-time errors, checked when they are constructed. Everything on
the cell side works, since sample, snapshot, gate and `Build::sample`
read the committed value before t, and `listen_cell` reads it after
commit. This is also why derived cells are read-through: an eager
update stream for `lift(log, filter, f)` would need the
post-transaction state during evaluation.

We considered enforcing the restriction at the type level with a
distinct `State<S>` token accepted by every cell-reading operation
through a trait, and rejected it for now: `lift` over a mix of `Cell`
and `State` has to compute its output type, and the build-time panic
is in the same class as every other construction error. The door stays
open if the panic bites in practice. Dropping in-place accumulation
would leave an asymptotic cliff against the performance bar for any
workload that accumulates, and persistent collections cost roughly ten
times a `Vec` push. Dropping the derived `accumulate` would lose a
legal and common stream view.
