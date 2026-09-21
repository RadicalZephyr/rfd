# The I/O Edge: Remotes, Drivers, and Threading Modes

**State:** discussion · **Authors:** Zefira Shannon, Claude

The engine is single-threaded and stays so. The requirement is that it
be usable from any threaded or async runtime with minimal friction,
from several at once, and without the library choosing a channel
implementation on its users' behalf.

## The Driver and the Remote

A single-threaded engine needs a single driver: whoever owns the
`Graph` runs its transactions. Making users hand-route every I/O
source into that driver through channels of their own is the wrong
place to put the friction. Making each integration crate own the graph
fixes that and creates a worse problem: two integrations cannot share
one graph. So the runtime-agnostic part of the glue lives in the core.

`graph.remote()` returns a `Remote`, which is `Send + Clone`, backed
by an inbox behind a standard-library mutex and a pluggable waker, an
`Arc<dyn Fn() + Send + Sync>` registered by the driver.
`remote.send(input, value)` locks, pushes a boxed pending send,
unlocks, and wakes. It is synchronous and never blocks on the graph.
`remote.transaction(|tx| ...)` batches simultaneous sends the same
way, with a `Send + 'static` closure that runs on the driver. The
driver calls `graph.pump()`, which runs each pending item as its own
transaction in arrival order, and arrival order is the total order
the semantics need. Transported values must be `Send`; nothing else
changes, and a `Remote` works with a `Graph<Local>`.

The core ships one driver: a dedicated standard-library thread that
builds the graph, hands back the ports and a `Remote`, and blocks on a
condition variable until woken. An integration crate is then a few
dozen lines: a waker for its runtime, a driver loop if it wants one,
and adapters from `listen` into its channel types, which is where
queues live; the core has no queue type ([RFD 2](./rfd-0002-strong-io-separation.md)). Multiple
integrations coexist because none of them owns anything; they all
hold `Remote`s. A GUI owning the graph on its main thread works with
tokio network tasks holding `Remote`s at the same time, and the GUI's
non-`Send` state stays in listener closures on the driver thread. No
adapter crate ships with the first version; `bough-tokio` is the first
afterwards, once the performance bar has been measured.

## The Chat Room

One input takes a username and a message. Each per-user tokio task
holds a `Remote` clone and, on each line read from its socket, calls
`remote.send(messages, (user, line))`. The driver pumps. A listener on
the outbound stream captures the per-user `tokio::sync::mpsc::Sender`s,
which are `Send`, and forwards. The user writes no channel plumbing
for inputs.

```rust
let (mut graph, ports) = Graph::build_threaded(|b| { ... });
let remote = graph.remote();
let notify = Arc::new(Notify::new());
graph.set_waker({ let n = notify.clone(); Arc::new(move || n.notify_one()) });
tokio::spawn(async move {
    loop { notify.notified().await; graph.pump(); }
});

// per connection
let remote = remote.clone();
tokio::spawn(async move {
    while let Some(line) = lines.next_line().await? {
        remote.send(ports.messages, (user.clone(), line));
    }
});
```

## The New Hole in the Wall, and Its Guard

`Remote` is `Send + Clone + 'static`, so a `map` closure can capture
one and send from inside graph code. It is not reentrant, since a
send only enqueues, but it is I/O inside FRP logic. The inbox records
the driver's thread id and an evaluating flag. A `Remote::send` from
that thread while a transaction is evaluating is an error in both
build modes, `InsideTransaction` from `try_send`, since it is a logic
error with an observable outcome and not an unobservable one ([RFD 5](./rfd-0005-transaction-protocol.md)).
A remote send whose input was collected before the driver pumps is
discovered at `pump` and follows the debug/release rule for
unobservable operations. From another
thread it enqueues. From a listener it enqueues too, which is the
sanctioned way for I/O to feed back into the graph: a later
transaction, never a nested one. Leaving it unguarded and documented
was the alternative; a check on a path that is already a bug costs
nothing.

## Threading Modes

`Remote` removes most of the pressure, but a non-`Send` graph still
has to be built on the thread that runs it, so a tokio-native user
cannot hold it in a spawned task or behind an `Arc<Mutex>`. The graph
takes a mode parameter, `Graph<Mode = Local>`. In `Threaded` mode
every value and closure the graph stores must be `Send`, checked once
per materialization and at `listen` through a per-mode `Accepts<T>`
trait, and `Graph<Threaded>` is `Send`. Single-threaded users never
see the parameter, and their `Rc<RefCell<UiState>>` captures keep
compiling. `Graph::build` builds a `Local` graph and
`Graph::build_threaded` a `Threaded` one, two constructors rather than
one, because a defaulted type parameter takes no part in inferring an
associated function: `Graph::build(|b| ...)` with a generic `build` is
"type annotations needed", and two inherent `build`s are ambiguous,
as a stub of the API confirmed. Tokens are plain integers and `Send` in every mode;
`Remote`, `Listener` and `Pin` do not carry the mode.

Requiring `Send` everywhere would have killed the UI case, where
toolkit handles are not `Send`. A non-`Send`-only graph would have
left tokio users with the dedicated-thread driver as the sole option,
which is friction on the first line. Retrofitting a type parameter
touches every signature, which is why this is decided now rather than
later.
