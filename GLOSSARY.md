# Glossary

Bough is a functional reactive programming library that implements the
Sodium denotational semantics with an API that cleanly separates
building FRP logic from driving it with I/O. This glossary is the
project's language; the design behind each term is in the RFDs.

## Language

### Time

**Instant**:
A point in the semantics' time. Everything within one instant is
simultaneous, and a stream has at most one event per instant.
_Avoid_: tick, time step, frame

**Transaction**:
One instant as the engine runs it, from the sends that open it to the
listeners that close it. The initial build is transaction zero, and it can
have children too. A transaction closure gets a `Transaction`; a queued
unit runs with an `IoTransaction` or a `RemoteTransaction`.
_Avoid_: batch, tick

**Child transaction**:
A transaction that `split` or `defer` schedules to run after its parent and
before the next external instant.
_Avoid_: post-transaction, sub-transaction

**Event**:
A source's value at one instant. A stream *fires* events. A toolkit's event
becomes a Bough event when I/O code sends it into an input; "event loop"
and "event-driven" keep their ordinary meanings.
_Avoid_: occurrence (the semantics' `occs`, the same thing), firing (as a noun), message

**Step**:
A change of a cell's value from one instant to the next, including a change
to an equal value.
_Avoid_: update, change

### Streams and cells

**Stream**:
A stream with exactly one consumer, whose events move through by value.
Every constructor takes it by value, so using it twice is a compile error.
_Avoid_: event stream, linear token

**Shared stream**:
A stream with any number of consumers, each of which clones the event. The
only way to give a stream more than one consumer.
_Avoid_: broadcast stream, fan-out stream

**Linear**:
Having exactly one consumer. Streams and chains are linear.
_Avoid_: affine, single-use, unique

**Fan-out**:
Giving a stream more than one consumer, which is always explicit, through
`share`. `unzip` isn't fan-out: it gives each half of a pair a stream of
its own, with one consumer.
_Avoid_: splitting (that is `split`), broadcasting

**Cell**:
A value that exists at every instant. Cell values are read by reference;
the engine clones one only for `steps` and `steps_with_current`, which
need a value of their own.
_Avoid_: behavior, signal, property, variable

**State**:
The cell an in-place accumulator makes, and any read-through cell computed
from one. It's read like a cell, but it has no stream view, since its new
value doesn't exist until commit.
_Avoid_: mutable cell, state cell

**Hold**:
A cell that keeps the latest event of a stream, starting from an initial
value. Holds, accumulators and constants are the stateful cells; a
constant is a hold that never steps.
_Avoid_: register, latch, state cell

**Accumulator**:
A cell whose value is folded from a stream's events, either by returning a
new state or by mutating the state in place. The in-place form makes a
`State`.
_Avoid_: reducer, fold cell

**Read-through cell**:
A cell computed from other cells and memoized until one of them steps:
`map_cell`, `lift`, `switch_cell`. Its function runs when it's read, or
for a steps view during evaluation, at most once per step. Whether it
stepped settles without running user code: it steps when a cell it's
computed from steps. The other kind of cell is stateful, a hold, an
accumulator or a constant, and there is no third kind.
_Avoid_: derived cell, lazy cell, computed cell

**Input**:
A stream or cell driven from outside the graph, and the token I/O code sends
with.
_Avoid_: sink, source, port, event sink

**Source**:
The role of anything that yields events: a stream, a shared stream, or a
chain. An input is a source; a source is not necessarily an input.
_Avoid_: producer, emitter

### Building

**Token**:
The name of a node that the five token types carry: `Stream`, `Shared`,
`Cell`, `State`, `Input`. A token has no method that creates a node
without a build context.
_Avoid_: handle, reference, id

**Node**:
Anything in the graph with an identity of its own, created by a
materializer. `Node` is also the bound `listen` takes, which only
`Stream` and `Shared` satisfy: a chain is not a node.
_Avoid_: vertex, operator

**Adapter**:
An operation that transforms a source's events without creating a node, and
the type it returns: `map` is an adapter, `Map<S, F>` is its type.
_Avoid_: stage, transformer, combinator (for these)

**Chain**:
A linear sequence of adapters with no materializer. The first materializer
consumes it, and its adapters fuse into that node.
_Avoid_: pipeline, builder, lazy stream

**Materializer**:
An operation that takes the build context and creates nodes from a chain
or from a cell. Most create one; `split` and `defer` create two, and
`unzip` three, one for its pairs and one for each half.
_Avoid_: terminal operation, consumer, sink

**Dependency**:
What a node is marked from: a stream node's inputs, and the cells a
read-through cell is computed from, so that a step in one reaches the
other. A cell read inside a stream function is not a dependency, because
a cell is read as it was before the instant; neither is a
`switch_stream`'s selection, nor a `depends` declaration. A `split`'s or
a `defer`'s output doesn't depend on its input: its events come in child
instants.
_Avoid_: edge, link, upstream (as a noun), reach (that is for collection)

**Build context**:
The context every node-creating operation requires. It exists inside the
build closure and inside construct closures, and nowhere else, and it
carries the runtime's mode.
_Avoid_: builder, transaction (Sodium's word for it)

**Graph code**:
Code that runs with a build context or as a node function: the build
closure, construct closures, a split's iterator, and the functions given
to adapters and materializers.
_Avoid_: FRP code, logic, reactive code

**Construct**:
Creating nodes during a transaction, from a construct closure. The only way
logic is added after build.
_Avoid_: dynamic construction, wiring at run time, late binding

**Scope**:
The extent of one build context: the initial build, or one run of a
construct closure. A loop closes in the scope that declared it.
_Avoid_: session, phase

**Loop**:
A cycle in the graph, declared with a forward token and closed later with a
definition. The dependency graph stays acyclic: every path around a loop
crosses a read from before the instant, a `snapshot`, a `gate`, a `sample`
or a `switch_stream`'s selection, or a `split`'s or a `defer`'s child
instant. A hold's steps view doesn't delay. The check runs at close, at a
switch's first link and at every move, and a move that closes a cycle
poisons the runtime.
_Avoid_: cycle (for the construct; a cycle is what a loop makes legal), recursion

**Forward token**:
The token a loop hands out before its definition exists.
_Avoid_: placeholder, forward declaration

**Closer**:
The value that defines a loop, consumed by `close`.

### Driving

**Runtime**:
The value that owns a graph: the only thing that reads it, and what a
driver pumps. In prose, "runtime" means this and nothing else, and "graph"
means its network of nodes.
_Avoid_: engine (for the value), graph (for the value)

**I/O code**:
Code that holds the `Runtime` or a handle. Listeners and transaction
closures are I/O code.
_Avoid_: the I/O world (Sodium's phrase, kept only when quoting it), the outside, the shell

**Handle**:
An `Io` or a `RemoteIo`: how I/O code that can't hold the `Runtime` reaches
it. Every call through one queues for the next pump and returns a `Result`
at once, and nothing reads through one.
_Avoid_: token, subscription, proxy

**Io**:
The handle for I/O code on the runtime's own thread, such as a GTK signal
handler or a DOM closure. `Clone`, not `Send`, on every target, and only
for a `Local` runtime; from `io()`.
_Avoid_: context, session

**RemoteIo**:
The handle for I/O code on any thread: `Send + Sync + Clone`, from
`remote_io()`. What it carries, and the listeners it registers, must be
`Send`. It exists where the target has pointer atomics and a lock, under
`std` or `critical-section`.
_Avoid_: sender, proxy, channel, remote (alone)

**Guard**:
A `Listener` or an `Anchor`: an RAII value whose drop releases its root,
without the runtime. There is one kind, with no mode parameter. A guard is
`Send` where the target has pointer atomics, and not on the Cortex-M0.
"Drop guard" and "mutex guard" keep their Rust senses.
_Avoid_: handle (that is an `Io` or a `RemoteIo`), subscription

**Graph code re-entrancy check**:
The check that refuses a handle's call made from graph code, with
`FromGraphCode`: that's I/O inside FRP logic. The `Io`'s runs on every
target; a `RemoteIo`'s needs a thread id, so it runs under `std` only.
_Avoid_: the guard (a guard is a `Listener` or an `Anchor`)

**Edge**:
The I/O boundary: the tokens I/O code holds. The build's return comes back
`Anchored`, and whatever has flowed out since left as an `Anchored`: a
token leaves a unit alive only if the graph holds it or it left anchored.
_Avoid_: boundary, surface, ports; never a graph edge, which is a dependency

**Driver**:
Whoever owns the `Runtime` and pumps it: a thread, a future, a host's
system, or a bare-metal main loop. Every app has one, since nothing else
runs the queues.
_Avoid_: runtime (that's what it owns), executor, owner

**Listener**:
An I/O callback attached to a node, run after commit with no runtime access,
and the guard that keeps it attached. `listen_cell` and `listen_steps` are
the I/O forms of `steps_with_current` and `steps`, Sodium's `value` and
`updates`. A once-listener, from `listen_once` or `listen_cell_once`,
takes an `FnOnce` and is a root until it fires. A tied listener, from a
transaction's `listen_once` or `listen_cell_once`, belongs to its unit and
ends with it.
_Avoid_: observer, subscriber, callback (for the attachment)

**Anchor**:
The guard that keeps the tokens a value holds alive from I/O code, without
listening to them. It rides in an `Anchored`; a plain `Anchor` comes only
from `Anchored::into_parts`.
_Avoid_: pin, root (that is the concept)

**Anchored**:
A value carried with the anchor that roots the tokens it holds: from
`anchor` on the `Runtime`, a handle or the build context, and the build's
return comes back as one. It derefs to its value. Its clones share one
root, which ends with the last clone. `keep` keeps the root for good and
returns the value, and `into_parts` splits it into the value and its
`Anchor`. It isn't `Trace`.
_Avoid_: owner, wrapper

**Unit**:
A transaction with its children and listeners, however it started: a send
or a transaction on the `Runtime`, a slot's drain, or a queued call. A unit
is the declaration of one external cause, never split and never merged,
and collection runs after each whole one.
_Avoid_: batch, message, job

**IoTransaction** and **RemoteTransaction**:
What a queued unit runs with: an `Io`'s and a `RemoteIo`'s. They differ in
one bound: a listener tied to a remote's unit must be `Send`.
_Avoid_: remote transaction (for an `Io`'s)

**Pump**:
Running what's pending. Pending input slots drain first, by priority,
higher first and equal priorities in connection order, each at most once
per pump, and a slot that becomes pending pre-empts between whole units.
Then both handles' calls run in the order they were made, only those made
before the pump began.
_Avoid_: poll, drain, flush

**Input slot**:
A static mailbox for one input, placed by the code that writes it, folded
in place, and drained by the driver as one transaction per pending slot.
Connected at build to one input of one runtime, with a `u8` priority; the
connection isn't a root. One slot per producer.
_Avoid_: mailbox, buffer, interrupt queue

**Fold**:
A slot's function for combining a pending event with a new one, pending on
the left, associative. Not the input's coalescing function, which combines
two sends inside one transaction.
_Avoid_: coalescer (that is the input's), reducer, accumulator (that is a cell)

**Mode**:
Whether a runtime is `Local` or `Threaded`: whether what it stores must be
`Send`, and whether the runtime itself is. Neither guards nor handles
carry it, and only a `Local` runtime has an `Io`.
_Avoid_: flavor, threading model

**Tier**:
One of the engine's feature levels: the `no_std` core over `alloc`, and
`std`. A bounded storage backend is a later tier, not built.
_Avoid_: profile, mode (that is `Local` or `Threaded`), edition

### Memory

**Root**:
Something that keeps a node alive. There are two kinds: a live guard, which
an `Anchored` holds, and a registration waiting in a handle's queue. A
waiting send or transaction roots nothing. A guard is live until it's
dropped, and `keep` makes it live for the runtime's life; a
once-listener's root ends when it fires.
_Avoid_: anchor (that is one kind), pin, owner

**Reach**:
What a node keeps alive: its dependencies, the tokens its chain holds, such
as the cells `snapshot` and `gate` read and `map_to`'s value, a switch's
current inner, the tokens `Trace` finds in a stateful cell's committed
value, and its `depends` declarations. Reach is wider than dependency: a
`depends` declaration never orders evaluation and can never read as a
cycle.
_Avoid_: reference (a Rust word), liveness edge, retention

**Stale**:
Of a token: its node has been collected.
_Avoid_: dangling, dead, expired

**Foreign**:
Of a token: it belongs to another graph.
_Avoid_: mismatched, alien

**Poisoned**:
Of a runtime: a panic escaped graph code, a listener, a transaction's
closure, or a `Drop` a collection ran, so a transaction or a collection
never finished. The transaction-in-progress flag stays set, and every
later call fails, through both handles too. Where panics unwind, the
handles know at once; where a panic is a trap, they know once an entry
finds the poison.
_Avoid_: broken, corrupted, tainted

**Collection**:
Reclaiming the nodes no root reaches. It runs after each whole unit when
it's due, transaction zero included, and never inside one.
_Avoid_: GC in prose, sweeping, cleanup

### Testing and performance

**The semantics**:
The Sodium denotational semantics, version 1.1, as the executable Haskell in
the Sodium repository. What the engine is held to.
_Avoid_: the spec, the reference implementation

**Oracle**:
The semantics' Haskell, vendored and run under GHC by `bough-oracle` over
lists of time-stamped values, with loops computed by fixed point. The
engine is property-tested against it. It's patched only where the text
breaks its own rules.
_Avoid_: reference model, golden model

**Shape**:
One of the benchmark workloads, each with a hand-written imperative
baseline: shallow, frame and fan-out run in CI, and UI is not built yet.
_Avoid_: scenario, benchmark case

**Bar**:
The performance target: within a factor of three of the baseline on
realistic per-node payloads.
_Avoid_: budget, goal, SLA
