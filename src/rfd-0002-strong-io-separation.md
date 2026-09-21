# Strong Separation of Constructing FRP and I/O

**State:** discussion · **Authors:** Zefira Shannon, Claude

One flaw in the Sodium API is that it is possible to use I/O bridge
APIs inside of FRP logic and doing this seriously compromises the
correctness of the FRP engine.

We can do better than this in Rust.

## Flaws in Sodium's API Design

The first problem with the Sodium API is that it is so minimal that
some methods that should only be used for interfacing with the I/O
edge ("World of I/O" in Sodium parlance) are directly on the `Stream`
and `Cell` structs and so they show up in the documentation right next
to all the core FRP combinator primitives. Creating an input FRP
struct requires first creating the input edge struct (an I/O API!), so
from the very jump the Sodium API is _requiring_ the user to mix the
usage of I/O and FRP code.

The second major problem is that the `Transaction` concept is used for
both constructing FRP and in the I/O edge. From an implementation
perspective this makes sense because a transaction is needed. From an
API perspective it again muddles the distinction between the FRP and
I/O. This dual-usage of `Transaction` also doesn't help guide the user
towards the standard pattern of building all FRP up-front and then
"turning the crank" and just sending events to the constructed graph.

Because of these flaws and because Sodium in Rust is a port of the C++
implementation, there is no attempt to leverage unique Rust features
like lifetimes to prevent the use of I/O edge APIs inside FRP because
the design is fundamentally unsuited to doing so.

## Two Worlds, Two Types

The key insight is that we can (and should!) actually represent the
difference between "FRP build time" and "I/O event sending time" in
the API, and leverage this to make it impossible to use I/O
constructs inside of FRP core code because the I/O structs don't exist
until _after_ the FRP has been constructed.

The denotational semantics already draw this line. `hold`, `sample`,
`value` and `switchC` live in the `Reactive` monad, the pure
combinators do not, and `Execute` is the only way to run construction
at occurrence time. We map `Reactive` onto a `Build` context that
holds every constructor and `sample`, and we put sending, listening,
sampling from outside, and collection on a `Graph` that only exists
once the build closure has returned.

```rust
let (graph, ports) = Graph::build(|b| {
    let (clicks, clicks_in) = b.input::<Click>();
    let count = clicks.accumulate(b, 0u32, |_, n| n + 1);
    let label = count.map_cell(b, |n| n.to_string());
    Ports { clicks_in, label }        // Ports: Trace. Whatever build returns is the edge.
});

let _l = graph.listen_cell(ports.label, |s| ui.set_text(s));      // fires now, then on updates
graph.send(ports.clicks_in, Click);                               // one transaction
graph.transaction(|tx| { tx.send(a_in, 1); tx.send(b_in, 2); });  // simultaneous inputs
```

Inside the build closure the user holds `&mut Build`, which has no
`send` and no `listen`. During a transaction the engine holds
`&mut Graph`, so no node function can reach the I/O API. The only
bypass is wrapping the graph in a `RefCell` yourself, and that panics
deterministically because the borrow is already taken for the whole of
`send`. The borrow checker does the work an earlier version of this
RFD asked of explicit lifetimes, without a scoped context.

### Tokens

Streams and cells are inert tokens: an index, a generation, and a
graph id. They have no method that touches the graph without a `Build`
context, so the I/O world can hold and pass them around but cannot
build with them. `Cell<A>`, `Input<A>` and `Shared<A>` are `Copy`;
`Stream<A>` is move-only, for the reasons RFD 4 gives. The graph id is
checked on every use, so a token from one graph used in another is a
build-time panic in graph code and an error from the I/O API. Dropping
the graph id would save four bytes per token and buy undefined
behaviour, in the logical sense, across graphs; four bytes and one
compare is nothing.

### Construction Is Method-Chained on the Tokens

Constructors are methods on the tokens, taking the build context as
their first argument where they need one:

```rust
input.map(f).filter(p).snapshot(c, g).hold(b, 0);
count.lift(b, other, |n, m| n + m);
```

Stages such as `map` need no context at all (RFD 4); only operations
that create a node name `b`. We considered putting every constructor
on `Build`, `b.hold(0, b.filter(b.map(s, f), p))`, which nests inside
out, and a chained builder type borrowing `b` for one expression,
which is a second surface to keep in sync with the first. Methods on
the tokens read like Sodium, the chain runs left to right, and the
move of `self` is the linearity check made visible.

### Inputs

`b.input::<A>()` returns a stream and the `Input<A>` token that drives
it. `b.input_coalescing(f)` is for inputs that may be sent more than
once in a transaction, with `f: Fn(A, A) -> A` taking both values by
value, first send on the left. `b.input_cell(init)` and
`b.input_cell_coalescing(init, f)` are the same for cells, a hold over
an input. Two sends to a non-coalescing input in one transaction are
an error in both build modes; silent last-wins would make production
behave differently from every test that ever ran.

Inputs may be created anywhere `Build` is available, including inside
`construct`, and the token flows to the I/O world as data, through a
listener on the value that carries it. An earlier version of this RFD
declared inputs as parameters of the build closure. That cannot
express an input created at runtime for a dynamically constructed
component, and the alternative, multiplexing every dynamic input
through a keyed input such as `Input<(ItemId, Edit)>`, pushes routing
logic into every component.

### Listeners Have No Graph Access

Listeners are `FnMut(A)` for streams and `FnMut(&A)` for cells and
nothing else: no sample, no send, no listen from inside a listener.
State a listener needs is snapshotted into the graph, where the
dependency is visible and glitch-free. Listeners run after commit,
from the finished slots, so a panicking listener leaves a consistent
graph, and no listener is ever registered mid-transaction. Sodium lets
listeners sample and delivers to them during the transaction; removing
both deletes the suppress-earlier-firings flag and the `value`
coalescing dance from the engine. The order of listeners within a
transaction is the evaluation order of their streams, ties by
registration order, and is documented as not something to rely on.

`listen` and `mailbox` accept materialized nodes only, `Stream<A>` or
`Shared<A>`, never a chain. A listener with a pre-filter would be FRP
logic constructed after build, and `snapshot` and `once` in I/O code
would be the first crack in the wall.

### Outputs

Any stream or cell token can be listened to from I/O, and whatever the
build closure returns is the permanent root set (RFD 3). We considered
a distinct `Output<A>` type that build must produce explicitly, making
it impossible to listen to a node that was not exported. Dynamic
outputs travel inside values, and an `Output` wrapper would have to be
applied inside every `construct` closure; the build return value
already says "these are the edges". `Mailbox<A>` is a helper over
`listen` that queues occurrences for a loop to drain. It gives the
pull style of the earlier sketch, `ctx.recv(output)`, without a second
mechanism, because a queue is a listener with a `Vec`.

### Runtime Construction

Nothing can add logic after build. Runtime construction goes through
`construct`, which is the semantics' `Execute`:
`s.construct(b, |b, a| ...)` runs the closure at each occurrence with
a fresh `&mut Build`, and its results reach the world only through
`switch_stream` and `switch_cell`. Plugin-style late logic is a cell
of plugins and a switch. Tests build one graph each.

### Loops

FRP allows a limited form of cycles in the constructed graph, and
every cycle must pass through a hold, an accumulator or a `split`.
Declare and close are separate, and flat:

```rust
let (block_number, block_number_loop) = b.cell_loop::<BlockNum>();
let (retry_count, retry_count_loop) = b.cell_loop::<RetryCount>();
let parts = build_transfer(b, block_number, retry_count, ...);   // forward tokens travel anywhere
block_number_loop.close(b, parts.block_number);                  // any Cell<A>: hold, accumulate, lift, switch
retry_count_loop.close(b, parts.retry_count);
```

A cell loop closes with any cell and the forward token becomes that
cell. A stream loop returns a linear forward stream and closes with
any chain. The closer is move-only, so a loop cannot close twice and
cannot be moved into a `construct` closure, which means a loop cannot
span the scope it was declared in. A loop declared and never closed is
a build-time panic at the end of the build or `construct` scope, the
same class as every other construction error. The cycle check runs at
close, and again in the transaction's marking walk for cycles a
`construct` creates (RFD 5).

Sampling a loop cell before it is closed is a build-time panic, since
there is no value to return. Sodium's `Lazy` family is out of the
first version; a `Lazy<A>` for the initial-value case can be added
later, forced at the end of the scope after every loop has closed,
which is exactly what Sodium's `sampleLazy` does.

We tried closure-scoped loops first, `b.cell_loop(init, |b, c| ...)`,
which cannot be left open but nest one level per loop. Three entwined
loops in a protocol state machine, a block number, a retry counter and
a terminal error that each read themselves and each other, nest three
deep with the whole body in the innermost closure. That is the normal
shape of a state machine, not a corner case. The `build_with_cycles`
sketch from the earlier version of this RFD, one declaration at the
top of the build with the definitions as a second return value, cannot
express a loop inside a constructed screen. The flat form is what an
application framework needs as well: declare here, hand tokens to
user code, close there.

### The I/O API

`Graph` has `send`, `transaction`, `listen`, `listen_cell`, `mailbox`,
`sample`, `pin`, `collect` and `remote`, each with a `try_` variant
(RFD 5). `graph.transaction(|tx| ...)` hands out a `Transaction` that
has only `send`, so simultaneous inputs are one closure. `Transaction`
exists only on the I/O side, which removes the dual use this RFD
complains about. We considered the scoped `rt.with_io(|ctx, ...| ...)`
from the earlier sketch. The scope adds nothing structural, since
graph code already cannot reach `Graph` during a transaction, and an
application framework needs something that owns the graph across
event-loop iterations. Threaded and async I/O reach the graph through
`Remote` (RFD 6).

### Reading a Cell

`c.sample(b)` in graph code and `graph.sample(c)` in I/O both return
`&A` borrowed from the context, so the borrow ends at the semicolon
and a caller that wants to keep the value clones it. Both take the
context by `&mut`, because reading a lazy derived cell may compute and
memoize. There is no `Clone` bound and no closure-taking variant; the
clone lands where the user decides to keep the value, which is the
whole philosophy of RFD 4.

## Names

Sodium's names are kept where they are good, and the book stays the
manual for those. These change, following the naming policy in
RFD 1:

| Sodium | Bough | Why |
|---|---|---|
| `switchS`, `switchC` | `switch_stream`, `switch_cell` | The suffix letters mean nothing to someone who has not read the book. |
| `updates` | `steps` | It fires on every step including unchanged values, and `steps` is the semantics' own word for that list. |
| `value` | `steps_with_current` | Long on purpose: it fires once now with the current value and then on every step. |
| `collect` | `scan` | It is exactly `Iterator::scan`, and `collect` means something else to every Rust reader. |
| `filterOptional` | `filter_map` | Takes a function and replaces the map-then-filter pair. |
| `accum` | `accumulate` | The naming policy; `accumulate_mut` is the in-place form (RFD 4). |
| `map` on a cell | `map_cell` | Distinct from `map` on a stream, and spelled out. |
| `StreamSink`, `CellSink` | `input`, `input_cell` | Inputs are created from `Build` and drive a stream or a cell. |
| `StreamLoop`, `CellLoop` | `stream_loop`, `cell_loop` | Same concept, flat declare and close. |
| `Operational` | gone | Its four operations are ordinary methods. |
| `execute` (the semantics) | `construct` | What it does, in Rust words. |

Kept as is: `never`, `constant`, `map`, `map_to`, `filter`, `merge`,
`or_else`, `snapshot`, `hold`, `gate`, `once`, `lift`, `sample`,
`split`, `defer`, `listen`.
