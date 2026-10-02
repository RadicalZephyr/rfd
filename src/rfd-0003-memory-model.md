# Memory Model

**State:** discussion · **Authors:** Zefira Shannon, Claude

Sodium's Java, C# and TypeScript implementations lean on a host garbage
collector. `sodium-rust` built its own: reference counts on every node
plus a tracing pass that needs every closure to declare the Sodium
objects it captures. That declaration tax is paid on every closure,
and a cycle through values, a cell whose value holds a token for a
node that depends on the cell, still leaks. Bough's requirement is
stricter on both counts: a leak is unacceptable, and whatever the user
has to tell us must be checked. There is one exception, a guard hidden
in graph state, which can hold its memory until the runtime drops;
What the User Declares names it.

## Nodes Live in an Arena, Tokens Name Them

Every node lives in one arena owned by the `Runtime`, indexed by `u32`.
Nodes name each other by index, never through an `Rc`, and there is no
`RefCell` in the node graph. Inside the runtime, interior mutability
appears in four places, each with one job: the memo of a read-through
cell, a `OnceCell` that hands out a reference from a shared borrow and
is cleared only through `&mut` at commit
([RFD 4](./rfd-0004-value-model.md)); the state a guard shares with the
runtime's entries for it, so that dropping the guard needs no runtime
access; the `Io`'s queue, which an `Io` pushes to without the runtime;
and the `RemoteIo`'s inbox ([RFD 6](./rfd-0006-io-edge.md)). An input
slot, a `static` the writer owns, has a lock of its own
([RFD 7](./rfd-0007-targets.md)). A token is an index, a generation and
a graph id. A freed slot bumps its generation, so a stale token fails
the check on its next use instead of addressing a recycled node. A slot
whose generation reaches its maximum is retired and never reused, one
compare on free, so a stale token from before a wrap can never
validate; with a first-in first-out free list the churn spreads across
every slot, and retirement is astronomically rare
([RFD 7](./rfd-0007-targets.md)). This is what makes a wrong `Trace`
implementation a loud error rather than memory unsafety, and it is why
`Trace` is a safe trait.

`Cell<A>`, `State<A>`, `Input<A>` and `Shared<A>` are `Copy`.
`Stream<A>` is move-only because it is linear
([RFD 4](./rfd-0004-value-model.md)); it is still the same twelve
bytes. The phantom in every token is `PhantomData<fn() -> A>`, so a
token is `Send` whatever `A` is, which
[RFD 6](./rfd-0006-io-edge.md) relies on.

The arena and every per-transaction structure sit behind a
`pub(crate)` storage seam. The engine allocates when the graph grows,
at build and inside `construct`, and when I/O code registers a listener
or an anchor or calls through a handle. A handle's call allocates on
the caller's side: once its queue has grown, a remote unit allocates
once, on its sender, and never on the driver. A transaction allocates
nothing once the graph
has stopped growing: mark and order buffers are reused, dispatch lists
are reused, and a child transaction pulls from the split's iterator
rather than queueing items. That is what lets the same engine run on a
microcontroller with an allocator it never calls once setup is done,
and what would let a bounded storage backend with a fixed number of
slots land behind the seam without touching the protocol. That backend
is a plan, not built, and every handle call allocating and the queues
growing are among its open questions ([RFD 7](./rfd-0007-targets.md)).

## Liveness Is Reachability From Explicit Roots

A node is alive when it is reachable from a root. There are two kinds
of root:

1. every live guard, a `Listener` or an `Anchor`;
2. every registration waiting in a handle's queue, a listener or an
   anchor, which keeps the tokens it names alive until the pump runs
   it.

A waiting send or transaction roots nothing: a send to an input no root
reaches can't be observed, so the pump reports it as stale. A
once-listener is a root until it fires.

I/O code takes an anchor with `anchor(value)`, on the `Runtime`, on
either handle, or on `Build`, for a value holding tokens it wants to
hold without listening to them. The value comes back `Anchored`, which
reads as the value through `Deref` and holds the `Anchor` that roots
its tokens. Its clones share one root, which ends with the last clone.
`keep` keeps the root for the runtime's life and returns the value, and
`into_parts` splits it into the value and its `Anchor`, which is the
only way to get a plain `Anchor`. `Anchored` isn't `Trace`, so a hold
of one doesn't compile. The build's return value is anchored like any
other, which is why its type must implement `Trace`: `build` returns it
`Anchored`.

A connected input slot doesn't root its input. Keep the build's return,
or the part that holds the input, while its slots are connected; on
bare metal that means `keep`.

A node's reach, what it keeps alive, is its dependencies, the tokens
its chain holds (the cells `snapshot` and `gate` read, and `map_to`'s
value), the tokens a `Trace` walk finds inside a stateful cell's
committed value, a switch's currently selected inner (which is such a
value), and the explicit `depends` declarations below. Reach is wider
than dependency: the marking walk of a transaction follows dependents
lists only, so a `depends` declaration never orders evaluation and can
never read as a cycle ([RFD 5](./rfd-0005-transaction-protocol.md)).

Collection is mark from the roots, sweep the arena, bump the
generation of every freed slot, and prune dead nodes out of their
inputs' dependents lists. No node carries a count, so a cycle through
values is collected like anything else. A node reachable only from a
token I/O code holds but neither anchored nor listened to is
collected, and the next use of that token is an error. So a token
leaves a unit alive only if the graph holds it or it left as an
`Anchored`: anchor it at the edge. This is semantically right. A
deselected inner cell that something still names keeps accumulating,
because it is reachable; one that nothing names can never be observed
again.

Why not reference counts. Counted tokens would root what I/O code
holds and what values hold, but counts cannot see cycles; `sodium-rust`'s
answer was declared dependencies per closure, and it still leaks
through user structs. Weak references, the C++ implementation's
answer, collect nodes that must keep accumulating while deselected.
Tracing from roots is the only model in which "unreachable" means
"unobservable forever", and it needs no counts, so tokens can be
`Copy`.

We considered three other ways to root. A permanent root set, where
the build's return stayed a root for the runtime's life: anything to be
freed later would have been anchored during the build and passed out
through a variable the closure captures, so nothing the build returned
could ever be freed, and the captured variable is a C out-param with
extra steps. A connection that roots its input: a slot is a `static`
that never disconnects, so its input would be a permanent root again.
And anchoring through a handle inside the listener that receives a
token: it works, but every listener that receives tokens has to capture
a handle and anchor before anything else. `Anchored` moves that to one
place, where the node is built, and that's the user naming the edge of
their graph, as the build's return value already does.

## What the User Declares

Two things, both checked.

Every type held in a cell implements `Trace`, derived with
`#[derive(Trace)]` next to the `Clone` most such types already derive,
with `#[trace(skip)]` for fields that cannot hold tokens. A value of a
foreign type that holds no tokens goes in a `Leaf<T>` wrapper, which
traces nothing and derefs to `T`; the orphan rules forbid implementing
`Trace` for another crate's type, so a macro declaring one a leaf could
only ever run inside this crate. Implementations ship for the
standard library's types; those for `HashMap`, `HashSet` and `Instant`
need `std`, and the one for `Arc` needs pointer atomics. The bound sits
on `hold`, `map_to` and the other operations that persist a value, so a
stream of non-`Trace` values can be mapped, filtered and merged freely
and fails only where it would persist. Stream event types need nothing
beyond what their adapters need, because slots are cleared before a
collection and only holds persist.

`Leaf`, `#[trace(skip)]` and a hand-written impl each promise to hide
no tokens and no guards. A hidden token keeps nothing alive, so its
node can be collected, and its next use is then a stale token. A hidden
guard is the one exception to the requirement: it roots
what it holds from inside graph state, and if what it roots reaches the
state that holds it, nothing can collect either until the runtime
drops. That is a leak, not unsoundness. The derive refuses a field
whose type names `Anchored`, which catches the common case. It goes by
name, since a derive can't see types, so an alias or a type parameter
gets past it.

`Trace` is a safe trait. The obligation is real, but the consequence
of getting it wrong is a stale-token error, and `unsafe` should mean
memory safety and nothing else. `Ord` and `Hash` carry
compiler-unverifiable invariants and are safe traits for the same
reason. The `gc` crate marks its `Trace` unsafe because its collector
frees memory on the strength of it; ours does not, no memory is ever
touched through a stale token. Making hand-written implementations
`unsafe` would also lock a crate with `forbid(unsafe_code)` out of
writing one.

A closure is the one thing the collector can't look inside, so every value
a `move` closure captures that holds a token is declared, with
`depends`, on the node the closure belongs to. For an adapter, that is
the node its chain becomes. `b.depends(&node, &[&clicks, &total])`
states that a node keeps those values' tokens alive. It takes any
`Trace` values, so a struct or a `Vec` of tokens is one declaration,
and it takes references, so it does not consume a linear stream; it is
callable after any construction. The rule finds every capture: graph
closures are `'static`, so a closure can hold a token only by owning
it, and without `move` the compiler refuses the borrow (E0373). It
never asks whether a capture is upstream, which a switch can change at
run time. Declaring a token the node reaches anyway costs one reach
entry.

We considered a deps-list parameter on every closure-taking
constructor, `sodium-rust`'s shape, which doubles that part of the
API, and a deps parameter on `construct` alone, which misses a `map`
that emits a captured token after the node it came from has become
unreachable. Closure-taking twins that take their captures as an
argument double the API too, and are another way to write `depends`.
A switch constructor that takes its candidates isn't needed once every
capture is declared.

The rule has costs we know. `depends` has no inverse: on the engine
spike, a declaration made on a long-lived node from inside a
`construct` kept fifty screens instead of one. And the burden is heavy
where code selects among tokens: the ordinary switch idiom, a closure
choosing among tokens, needs every candidate declared, and a missing
one fails at the first move rather than at build
([research](./research/2026-09-24-engine-feasibility-spike.md)).

An undeclared capture cannot be made a compile error without making
tokens unusable as data, and we want the data. Its failure mode is a
stale token: a loud error at the point of use, never a leak and never
a read of a recycled node. A value is traced when it is declared, and
a chain when its node is built, so a token added later through
interior mutability isn't seen; the I/O code that adds it anchors it.
A setting on the runtime, `set_collect_after_every_unit`, makes that
error deterministic in tests, and the public live-node count,
`live_nodes`, is how the no-leak requirement is asserted: build, drive,
drop, collect, compare.

## When Collection Runs

Never inside a unit. Automatic by default and amortized: after each
whole unit, transaction zero included, collect when the nodes allocated
plus the guards released since the last collection exceed the number
of nodes that collection left alive. A once-listener's release counts
when it fires. Garbage is made by unrooting as much as by allocating,
and a graph built once that then drops listeners allocates nothing, so
a trigger on allocation alone would never fire for it; a graph that
neither allocates nor drops a guard never pays. A guard dropped
between units leaves its garbage until a collection runs after the
next unit, or until `collect_garbage`. A manual policy is available,
set with `set_collection_policy` and run with `collect_garbage`, for a
frame loop that wants to collect at frame end or a high-rate loop that
wants to choose when it pays. Manual-only was rejected because UI code
should never think about it; automatic-only because the shallow
high-rate shape wants to choose.

Garbage costs time as well as memory, since it runs whenever its inputs
fire until it is collected: on the engine spike, after 9,000 screens a
navigation took 596 µs a transaction without collection and 528 ns with
it. The trigger counts a dropped guard as one release however much it
unrooted, so a drop that unroots a large part of the graph waits for
the trigger like any other.

We considered holding collection off while anything is queued. A busy
inbox, or an echo that never settles, would hold it off for good.

## Guards

A guard borrows nothing from the runtime, so the runtime can be driven
while guards are held. `Listener` and `Anchor` are RAII: dropping one
unlistens or unanchors with no runtime access, on any thread where the
target has pointer atomics, so dropping one inside a listener callback
is fine. A guard is live until it is dropped, and a live guard is a
root. `keep()` consumes the guard and leaves its listener or anchor
live without a guard to hold, for the runtime's life, or for a
once-listener until it fires, because every real application has
process-lifetime listeners and a field called `_listeners` that exists
to be ignored is the alternative. `unlisten()` exists for symmetry with
Sodium, and `unanchor()` for symmetry with it. A linear stream is
consumed by `listen`, so once that listener is dropped the stream can
never be observed again and is collected unless something else roots
it. Rust-level reference cycles between a listener closure and the I/O
state that owns its guard are the user's problem and get a
documentation note, not machinery.

Checking whether a guard is live costs two instructions a listener call
on x86 ([research](./research/2026-09-27-io-edge-spike.md)).

## Operations on Collected Nodes

Sending to a collected input, listening to a collected stream, or
anchoring a collected node has no effect the semantics can observe. In
the panicking variants these are a debug-mode panic and a release-mode
no-op, counted on the runtime so a release build can still report that
it is dropping sends; the `try_` variants return `Err(Stale)` in both
modes ([RFD 5](./rfd-0005-transaction-protocol.md)). Through a handle,
a stale token is found at the pump: `pump` panics in a debug build and
counts it in a release build, and `try_pump` returns
`PumpError::Stale`, so a stale send gets the same diagnostic whichever
handle queued it. Sampling a collected cell must return something, so
it always fails.
