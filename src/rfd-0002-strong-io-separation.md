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
to all the core FRP primitives. Creating an input FRP
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

## Two Types: Build and Runtime

The key insight is that we can (and should!) actually represent the
difference between "FRP build time" and "I/O event sending time" in
the API. The denotational semantics already draw this line: `hold`,
`sample`, `value` and `switchC` live in the `Reactive` monad, the pure
operations do not, and `Execute` is the only way to run construction
at event time. We map `Reactive` onto a `Build` context that
every node-creating operation requires and that also carries `sample`,
and we put sending, listening, sampling from outside, and garbage
collection on a `Runtime`, which only exists once the build closure has
returned.

I/O code that can't hold the `Runtime` reaches it through a handle, so
there are three ways in:

- The `Runtime`, which its driver owns. Its calls run now, and only it
  reads.
- An `Io`, for I/O code on the runtime's own thread, such as a GTK
  signal handler or a DOM closure. Only a `Local` runtime has one.
- A `RemoteIo`, for I/O code on any thread.

Every call through a handle waits for the driver's next pump, and
nothing reads through one. [RFD 6](./rfd-0006-io-edge.md) has the
rest.

The invariant this buys is best stated as one sentence: **the graph is
entered from exactly one place at a time.** Graph code, meaning node
functions and `construct` closures, never holds a `Runtime`. During a
transaction the engine holds the only `&mut Runtime`, and `Build` has
no `send` and no `listen`. Every public entry point on `Runtime` also
checks a flag saying whether a transaction is in progress, so even a
`Runtime` smuggled into graph code inside an `Rc<RefCell<_>>` fails
deterministically at the entry, not somewhere downstream.

What this does not, and cannot, prevent is asynchronous effects. A
node function may capture a channel sender and hand a value to another
thread that later sends it into the graph. That send lands in a later
transaction, which makes it I/O by definition rather than a hole in
the wall. Graph code may capture a handle too, since both are
`Clone + 'static`. A call through one from graph code would be I/O
inside FRP logic, so the graph code re-entrancy check refuses it with
`FromGraphCode`. The check is armed only while graph code runs:
evaluation and commit, a `construct` closure, a split's iterator. It
isn't armed in a transaction's closure or in a listener, which are I/O
code, so a call from there queues for the next pump, and that is how
I/O feeds back. The `Io`'s check runs on every target; a `RemoteIo`'s
needs a thread id, so it runs under `std` only
([RFD 7](./rfd-0007-targets.md)). The synchronous guarantee is the one
that matters for correctness, because it is the one that keeps a
transaction a pure function of its inputs.

```rust
use std::{cell::RefCell, rc::Rc};

struct Click;
#[derive(Trace)]
struct Edge { clicks_in: Input<Click>, label: Cell<String> }

let ui = Rc::new(RefCell::new(Ui::new()));

let (mut runtime, edge) = Runtime::build(|b| {
    let (clicks, clicks_in) = b.input::<Click>();
    let count = clicks.accumulate(b, 0u32, |_, n| n + 1);
    let label = count.map_cell(b, |n| n.to_string());
    Edge { clicks_in, label }         // whatever build returns is the edge, anchored
});

let _l = runtime.listen_cell(edge.label, {
    let ui = ui.clone();
    move |s| ui.borrow_mut().set_text(s) // fires now, then on every step
});
runtime.send(edge.clicks_in, Click);                                 // one transaction
runtime.transaction(|tx| { tx.send(edge.clicks_in, Click); });       // several sends, one instant
```

The example runs, given a `Ui`, and the crate's own doc test is the
same program over a tuple. `edge` is an `Anchored<Edge>`: it reads as
the `Edge` through `Deref`, and the nodes it names stay alive while
it's held ([RFD 3](./rfd-0003-memory-model.md)). `runtime` is `mut`
because the operations that drive it take `&mut self`;
`sample` and `try_sample` take `&self`, so two samples compose in one
expression (see Reading a Cell). The listener owns a clone of the
shared UI state because a listener is `'static`.

### Tokens

Streams and cells are inert tokens: an index, a generation, and a
graph id. They have no method that creates a node without a `Build`
context, so I/O code can hold and pass them around but cannot
build with them. `Cell<A>`, `State<A>`, `Input<A>` and `Shared<A>` are
`Copy` for every `A`, through hand-written impls rather than derives,
so `Cell<String>` is `Copy`. `Stream<A>` is move-only, for the reasons
[RFD 4](./rfd-0004-value-model.md) gives. `Input<A>` is `Copy` because
several I/O sources may legitimately drive one input, and because
inputs travel as data (see Inputs below). The graph id is checked
wherever a token meets a graph, which is at materialization for graph
code and at every I/O entry point; a token from one graph used in
another is a build-time panic in graph code and an error from the I/O
API. A handle refuses one when the call is queued, with
`IoError::ForeignGraph`. A queued transaction's closure hides its
tokens until it runs, so a foreign token in one is found at the pump,
as `PumpError::ForeignGraph`. Dropping the graph id would save four
bytes per token and buy undefined behaviour, in the logical sense,
across graphs. Four bytes and one compare is nothing.

### Chains and Nodes

Constructors are methods on the tokens, and they come in two kinds.

Adapters transform events and take no context: `map`, `filter`,
`filter_map`, `map_to`, `snapshot`, `gate` and `once`. They live on
the `Source` trait, and each returns its own type, `Map<S, F>`,
`Filter<S, P>` and so on, which is itself a `Source`. "Adapter" names
both the operation and the type, as it does for `Iterator`. Nothing is
allocated and no node exists yet. `Source` has an associated `Event`
type rather than a type parameter, the way `Iterator` has `Item`, so
`Source<Event = Click>` reads as a source of click events; a generic
`Source<A>` cannot be implemented by an adapter type at all, because
`A` would appear only in the bounds (E0207). `Source` is sealed: a
materializer stores the chain in its node and runs it, so every
adapter is the crate's own. A chain is a linear sequence of adapters
with no materializer, and it is itself linear: using it twice is a
compile error.

Materializers take the build context and create nodes: `hold`,
`accumulate`, `accumulate_mut`, `scan`, `share`, `node`, `unzip`,
`merge`, `or_else`, `split`, `defer`, `construct`, `switch_stream`,
and on cells `map_cell`, `switch_cell`, `steps` and
`steps_with_current`, plus `lift` on a tuple of cells. Most create
exactly one node; `split` and `defer` create two, and `unzip` three,
one for its pairs and one for each half. The adapters between two
nodes fuse into that node's closure;
[RFD 4](./rfd-0004-value-model.md) records the fusion. `Build` itself
has methods only for the things that start from nothing, `input` and
its variants, `constant`, `never`, `cell_loop`, `state_loop` and
`stream_loop`, and for three that aren't nodes: `depends` and `anchor`
([RFD 3](./rfd-0003-memory-model.md)), and `connect` (see Inputs).

```rust
input.map(f).filter(p).snapshot(c, g).hold(b, 0);   // three adapters, one node
(count, other).lift(b, |n, m| n + m);
```

We considered putting every constructor on `Build`,
`b.hold(0, b.filter(b.map(s, f), p))`, which nests inside out, and a
chained builder type borrowing `b` for one expression, which is a
second surface to keep in sync with the first. Methods on the tokens
read like Sodium, the chain runs left to right, and the move of `self`
is the linearity check made visible.

### Inputs

`b.input::<A>()` returns a stream and the `Input<A>` token that drives
it. `b.input_coalescing(f)`, Sodium Java's `StreamSink(f)`, is for
inputs that may be sent more than once in a transaction, with
`f: Fn(A, A) -> A` taking both values by value, first send on the
left. Its event type comes from the first use or from an annotated
closure; a bare `|x, y| x + y` fixes nothing, and the turbofish takes
two parameters, `::<u32, _>`, since the closure type is the second.
`b.input_cell(init)` and `b.input_cell_coalescing(init, f)` return a
cell and its token, a hold over an input. The cell forms are one line
over the stream forms and exist because an input that is state is
common enough to deserve a name.

Two sends to a non-coalescing input in one transaction are an error in
both build modes. This is a rule about one instant, not about who
holds the token, so no token discipline could make it a compile error:
one holder sending twice violates it just as two holders do. Silent
last-wins would make production behave differently from every test
that ever ran.

Inputs may be created anywhere `Build` is available, including inside
`construct`, and the token flows to I/O code as data, in an event a
listener receives. A collection runs after each unit and frees an
input nothing reaches, so the construct sends it out anchored, with
`b.anchor` ([RFD 3](./rfd-0003-memory-model.md)). The alternative,
declaring every input as a parameter of the build closure, cannot
express an input created at run time for a dynamically constructed
component, and multiplexing every dynamic input through one keyed
input such as `Input<(ItemId, Edit)>` pushes routing logic into every
component.

An input may also be fed by an input slot, a `static` the writer owns,
connected with `b.connect(input, &SLOT, priority)` and drained by
`pump`, higher priority first, where the priority is a `u8`. That is
the path from an interrupt handler ([RFD 7](./rfd-0007-targets.md)).

### Listeners and Guards

Listeners are `FnMut(A)` for streams and `FnMut(&A)` for cells, and
the once forms, `listen_once` and `listen_cell_once`, take an
`FnOnce`. A listener has no runtime access: no sample, and no send or
listen that runs now. A listener that captures a handle can call
through it, and the call queues for the next pump like any other, so a
listener it registers misses events until then. State a listener needs
is snapshotted into the graph, where the dependency is visible and
glitch-free. Listeners run after commit, from the finished slots, so a
panicking listener leaves a consistent graph, though it poisons the
runtime, since its transaction never finished
([RFD 5](./rfd-0005-transaction-protocol.md)). No listener is ever
registered mid-transaction, except a once-listener that a
transaction's closure ties to its unit, which is registered before
evaluation begins. Sodium lets listeners sample and delivers to them
during the transaction; removing both removes the
suppress-earlier-firings flag from the engine. The order of listeners
within a transaction is the evaluation order of their streams, ties by
registration order, and is documented as not something to rely on.

`listen`, `listen_cell`, `listen_steps`, `listen_once` and
`listen_cell_once` return a `Listener`. `anchor` takes any `Trace`
value, a single token or a value holding several, and returns it
`Anchored`, with the `Anchor` that roots its tokens. A guard borrows
nothing from the runtime, and dropping one needs no runtime access, on
any thread where the target has pointer atomics, so the runtime can be
driven while guards are held and a guard can be dropped inside a
listener. There is one kind of each, with no mode parameter.
`unlisten()` exists for symmetry with Sodium, and `unanchor()` for
symmetry with it. `keep()` keeps the root without a guard to hold: for
the runtime's life, or for a once-listener until it fires.
[RFD 3](./rfd-0003-memory-model.md) has the rest.

`listen` accepts materialized nodes only, `Stream<A>` or `Shared<A>`,
never a chain, through a `Node` bound that adapter types do not
implement. A listener with a pre-filter would be FRP logic constructed
after build, and `snapshot` and `once` in I/O code would be the first
crack in the wall. A linear stream is moved into `listen`, so it can
be listened to once; a shared stream any number of times; a cell any
number of times through `listen_cell` and `listen_steps`.

Sodium's `updates` and `value` are its operational primitives, filed
under `Operational` because they expose a cell's steps. The book puts
the warning plainly in section 8.4: "To protect the idea of a
continuously varying cell, a true FRP system must ensure that changes
in a cell's value aren't observable." Both exist here, in graph code
and in I/O code. In graph code, `c.steps(b)` is `updates` and
`c.steps_with_current(b)` is `value`, materializers on `Cell` that
return a stream, and their documentation carries that warning: a
stream of a cell's steps observes how the cell was built, not only
what it holds, and belongs in operational code such as sending a cell
over a wire. From I/O code, `listen_steps` is `updates` and
`listen_cell` is `value`, listeners that deliver the value by
reference. We first moved the stream views to `Runtime` alone, so that
no stream view of a cell existed in graph code. That made graph code a
strict subset of the semantics: a read-through cell has no feeding
stream to keep, and the nearest substitute, a snapshot on its inputs'
streams, is one instant stale, because `snapshot` reads a cell as it
was before the instant. Restoring the stream views keeps the semantics
whole and puts the warning where Sodium put it, on the primitives
themselves; what they cost is recorded in
[RFD 4](./rfd-0004-value-model.md).

### Outputs

Any stream or cell token can be listened to from I/O, with the
once-versus-many rule above. The build's return value comes back
`Anchored`, an anchor like any other: `keep` makes it permanent, and
part of it can be kept by anchoring that part and dropping the rest
([RFD 3](./rfd-0003-memory-model.md)). A `construct` names its outputs
the same way, with `b.anchor`. `Anchored` isn't `Trace`, so a hold of
one doesn't compile: a root inside graph state could keep itself alive
through a cycle. One hidden where `Trace` can't see holds its memory
until the runtime drops ([RFD 3](./rfd-0003-memory-model.md)).

We considered a distinct `Output<A>` type that build must produce
explicitly. Dynamic outputs travel inside values, so an `Output`
wrapper would have to be applied inside every `construct` closure that
sends one out, and `b.anchor` is that step already. An `Anchored`
names the edge where its nodes are built, as the build's return value
does, and a second wrapper would say the same thing twice.

There is no queue type in the core. An event loop that wants to pull
events instead of reacting to them writes a listener that pushes into
its own collection. A `RemoteIo` listener can capture a sender of the
executor's own channel type and hand values to a task that way
([RFD 6](./rfd-0006-io-edge.md)). We drafted a core `Mailbox<A>` and
dropped it: it needed a capacity policy, a drain contract and drop
semantics of its own, for something every executor already has.

## Constructing During a Transaction

Nothing can add logic after build except `construct`, which is the
semantics' `Execute`: `s.construct(b, |b, a| ...)` runs the closure at
each event with a fresh `&mut Build`, and its results are ordinary
events. A constructed screen goes into a hold that a `switch_stream`
or `switch_cell` reads, and a token created inside the closure flows
out to I/O code as data, anchored with `b.anchor`, as Inputs
describes. A construct that makes a screen together with its own input
returns the pair, and `unzip` parts it: the screens go into the hold
and the inputs out to I/O code ([RFD 4](./rfd-0004-value-model.md)).
Plugin-style late logic is a cell of plugins and a switch. Tests build
one graph each.

Inside `construct`, `sample` returns the value the cell had at the
start of the transaction, the semantics' `at c t`. That value is fixed
for the whole transaction, so the read imposes no ordering and cannot
glitch, which is also why cell reads are never dependencies in the
evaluation order ([RFD 5](./rfd-0005-transaction-protocol.md)). A
hold created inside `construct` starts at its initial value and picks
up an event in the same transaction if its input has one, as the
semantics' `Hold a s t0` with `t >= t0` requires.

## Loops

FRP allows a limited form of cycles in the constructed graph. Declare
and close are separate, and flat:

```rust
let (block_number, block_number_loop) = b.cell_loop::<BlockNumber>();
let (retry_count, retry_count_loop) = b.cell_loop::<RetryCount>();
let parts = build_transfer(b, block_number, retry_count, ...);   // forward tokens travel anywhere
block_number_loop.close(b, parts.block_number);                  // any `Cell`, subject to the rule below
retry_count_loop.close(b, parts.retry_count);
```

A cell loop closes with any `Cell`, and the forward token becomes that
cell. A state loop, from `state_loop`, is the loop for an in-place
accumulator: its forward is a `State`, with no stream view, and it
closes with a `State` or a `Cell`. A stream loop returns a linear
forward stream and closes with any chain.

The rule is about the dependency graph, not about the closing
expression: the graph stays acyclic. A read of a cell from before the
instant, through `snapshot`, `gate` or `sample`, is not a dependency,
and neither is a `switch_stream`'s selection or a `depends`
declaration. A `split`'s or a `defer`'s output doesn't depend on its
input, since its events come in child instants. Every other use of a
cell is a dependency: `map_cell`, `lift`, the stream views, and a
`switch_cell`'s outer and the inner it selects. Closing a cell loop
with `lift(forward, other, f)` is therefore rejected, since it would
define a value in terms of itself at the same instant, which the
semantics cannot give a meaning to; closing it with a hold whose input
snapshots the forward token is the normal case. A hold doesn't delay
its steps views, so closing with
`hold(merge(ticks, forward.steps(b).map(f)))` is refused too, though
its path passes through a hold. The panic names the cycle's nodes.

The check runs at close, at a switch's first link, and at every move
of a switch to another inner. A `construct`'s nodes are linked into
the graph when they are created, so a new node can close a cycle only
through a close or a switch, and a cycle is found the first time the
code runs. A move that closes a cycle is a run-time error, and it
poisons the runtime ([RFD 5](./rfd-0005-transaction-protocol.md)).
Each move walks everything upstream of its new inner, which took about
9 ns a node on the engine spike, 121 µs for a switch with ten thousand
nodes upstream
([research](./research/2026-09-24-engine-feasibility-spike.md)).

Checking at build instead, over every inner each switch declares it
may select, would take the walk off every move and find every cycle
before the graph runs. It would need every switch to declare its
candidates, and a `construct` makes candidates after build. It was
raised, and not tried.

The closer is consumed by `close`, so a loop cannot close twice. A
loop must close in the scope that declared it, and that is checked
against the loop node, not the closer: the build or `construct` scope
records the loops it declared and panics at scope end for any that is
still open. Moving the closer somewhere else changes nothing. In
particular, smuggling a closer into a `construct` closure through an
`Option` and taking it out on some later event compiles, and the
declaring scope still panics at its end because the loop is open when
the scope closes.

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
shape of a state machine, not a corner case. A single declaration at
the top of the build, forward tokens as a parameter and definitions as
a second return value, cannot express a loop inside a constructed
screen. The flat form is what an application framework needs as well:
declare here, hand tokens to user code, close there.

## The I/O API

`Runtime` has `send`, `transaction`, `listen`, `listen_cell`,
`listen_steps`, `listen_once`, `listen_cell_once`, `anchor`, `sample`,
`collect_garbage`, `set_collection_policy`,
`set_collect_after_every_unit`, `live_nodes`, `stale_operations`,
`set_shuffle_seed`, `statistics` behind its cargo feature,
`set_waker`, `pump`, `io`, `remote_io` and `shutdown`, and `build` and
`build_threaded` make one. `anchor` keeps alive the tokens a value
holds, for I/O code that wants to hold them without listening, and
returns the value `Anchored`, with the `Anchor` that holds the root.
The first name for it was `Pin`, an unrelated concept in `std::pin`;
the second was `Root`, which collided with the concept an anchor is
one kind of. `collect_garbage` runs a collection now, for the manual
policy; `collect` was the obvious name and is exactly the name the
table below retires because it means something else to a Rust reader.

`runtime.transaction(|tx| ...)` hands out a `Transaction`. Its `send`
makes simultaneous inputs one closure, and its `listen_once` and
`listen_cell_once` tie a once-listener to the unit, so I/O code hears
what its own sends caused. A unit queued through a handle runs with an
`IoTransaction` or a `RemoteTransaction`, which have the same three.
The transaction types exist only on the I/O side, which removes the
dual use this RFD complains about. `set_waker`, `pump`, `io`,
`remote_io` and `shutdown`, which ends a runtime on purpose, are the
edge for drivers and handles ([RFD 6](./rfd-0006-io-edge.md)). The
collection policy and the two counters are
[RFD 3](./rfd-0003-memory-model.md)'s, and the settings for tests are
[RFD 1](./rfd-0001-guiding-principles.md)'s.

Every operation that can fail has a `try_` sibling returning a
`Result`, and each family of operations with the same failure modes
has its own error type, with no variant an operation cannot return.
The panicking variants panic on misuse, except for the operations on
collected nodes whose effect the semantics cannot observe, which are a
debug-mode panic and a release-mode no-op. Handle calls are the one
exception: each returns a `Result` and has no panicking form, since a
handler called from C can't unwind.
[RFD 5](./rfd-0005-transaction-protocol.md) lists the families.

We considered a scoped `rt.with_io(|ctx, ...| ...)` context with
pulled outputs. The scope adds nothing structural, since graph code
already cannot reach the `Runtime` during a transaction, and an
application framework needs something that owns the runtime across
event-loop iterations.

## Reading a Cell

`c.sample(b)` in graph code and `runtime.sample(c)` in I/O both take
the context by shared reference and return `&A` borrowed from it.
Shared borrows compose, so `format!("{} {}", c.sample(b), d.sample(b))`
and binding two samples to variables both compile; a caller that wants
to keep a value clones it, and the clone lands where the user decides
to keep the value, which is the whole philosophy of
[RFD 4](./rfd-0004-value-model.md). There is no `Clone` bound and no
closure-taking variant. Reading a read-through cell may compute and
memoize, so its memo is a `OnceCell`, which hands out a reference from
a shared borrow and is cleared at commit through `&mut`
([RFD 4](./rfd-0004-value-model.md)); taking the context by `&mut` was
the first draft, and a stub of the API showed that two samples in one
expression are then a borrow error, which makes `sample` unusable for
its main job.

Only the `Runtime` reads. A handle has no `sample`, since its calls
wait for the next pump; I/O code that holds a handle reads with
`listen_cell_once`, a pump later. We considered an `Io` that reads.
Under the next-pump rule a read sees only what the last pump
committed, so read, change, send loses an update when two clicks land
between pumps.

## Names

Sodium's names are kept where they are good, and the book stays the
manual for those. These change, following the naming policy in
[RFD 1](./rfd-0001-guiding-principles.md):

| Sodium | Bough | Why |
|---|---|---|
| `switchS`, `switchC` | `switch_stream`, `switch_cell` | The suffix letters mean nothing to someone who has not read the book. |
| `updates` | `steps` on `Cell`, `listen_steps` on `Runtime` | An operational primitive: the name says what it exposes, a cell's steps, and it carries the book's warning. Fires on every step, including a step to an equal value. |
| `value` | `steps_with_current` on `Cell`, `listen_cell` on `Runtime` | Long on purpose: it fires once at creation with the current value and then on every step; the listener fires once at registration. |
| `collect` | `scan` | `collect` means something else to every Rust reader, and `scan` is the nearest Rust name; [RFD 4](./rfd-0004-value-model.md) gives the signature, which is not `Iterator::scan`'s. |
| `filterOptional` | `filter_map(\|o\| o)` | `filter_map` takes a function and covers the map-then-filter pair; the identity closure moves the `Option` through by value, so this needs no `Clone`. |
| `apply` on cells | `lift` with `\|f, a\| f(a)` | The oracle's `Apply` applies a cell of functions to a cell. Cell values are read by reference, and a bare `Box<dyn Fn>` isn't `Trace`, so the cell holds `Leaf<Box<dyn Fn(&A) -> B>>` and `(cf, ca).lift(b, \|f, a\| f(a))` is it. An engine test runs it that way; the oracle checks `Apply` as a lift over a cell of addends. |
| `lift` (arities 2 to 6) | `lift` on a tuple of cells, arities 2 to 6 | Rust has no variadics, and a tuple of cells is the one form: `(a, x, y).lift(b, \|a, x, y\| ...)`. Chaining binary lifts composes functions rather than lifting three cells ([RFD 4](./rfd-0004-value-model.md)). |
| `accum` | `accumulate` | The naming policy; `accumulate_mut` is the in-place form ([RFD 4](./rfd-0004-value-model.md)). |
| `map` on a cell | `map_cell` | Distinct from `map` on a stream, and spelled out. |
| `listen` on a cell | `listen_cell` | Cells are read by reference, so the listener signature differs from the stream one. |
| `StreamSink`, `CellSink` | `input`, `input_cell` | Inputs are created from `Build` and drive a stream or a cell. Java's `StreamSink(f)` and `CellSink(init, f)` are `input_coalescing` and `input_cell_coalescing`. |
| `StreamLoop`, `CellLoop` | `cell_loop`, `state_loop`, `stream_loop` with `close` | Same concept, flat declare and close. `state_loop` is a cell loop over a `State`. |
| `Operational` | gone | `defer` and `split` are ordinary methods on `Source`; `updates` and `value` are `steps` and `steps_with_current` on `Cell`, carrying the book's warning, and listeners on `Runtime`. |
| `execute` (the semantics) | `construct` | What it does, in Rust words. |

Kept as is: `never`, `constant`, `map`, `map_to`, `filter`, `merge`,
`or_else`, `snapshot`, `hold`, `gate`, `once`, `sample`, `split`,
`defer`, `listen`, `listen_once`.

New, with no Sodium counterpart: `share` and `Shared`, `node` and
`Node`, `unzip`, `Source` and `Event`, `Trace` and `Leaf`, `State`,
`depends`, `anchor`, `Anchor` and `Anchored`, `Listener`,
`listen_cell_once`, `keep` and `unanchor`, `collect_garbage`,
`set_waker`, `pump`, `io` and `Io`, `remote_io` and `RemoteIo`,
`InputSlot` and `connect`, `Build`, `Runtime`, `Transaction`,
`IoTransaction` and `RemoteTransaction`, `shutdown`, `Local` and
`Threaded`.
