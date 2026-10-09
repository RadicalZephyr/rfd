# The I/O Edge: Handles, Drivers, and Threading Modes

**State:** discussion · **Authors:** Zefira Shannon, Claude

The engine is single-threaded and stays so. The requirement is that it
be usable from any threaded or async executor with minimal friction,
from several at once, and without the library choosing a channel
implementation on its users' behalf. Interrupt handlers and DOM
callbacks are two more callers; [RFD 7](./rfd-0007-targets.md) gives
the first an input slot and the second an `Io`, and this RFD keeps the
handles' queues.

## The Driver and the Handles

A single-threaded engine needs a single driver: whoever owns the
`Runtime` runs its transactions, and every app has one, since nothing
else runs the queues. Making users hand-route every I/O source into
that driver through channels of their own is the wrong place to put the
friction. Making each integration crate own the runtime fixes that and
creates a worse problem: two integrations cannot share one runtime. So
the executor-agnostic part of the glue lives in the core.

I/O code that can't hold the `Runtime` holds a handle.
`runtime.io()` gives an `Io`, which is `Clone` and not `Send`, exists
on every target, and exists only for a `Local` runtime: it's for I/O
code on the runtime's own thread, such as a GTK signal handler.
`runtime.remote_io()` gives a `RemoteIo`, which is
`Send + Sync + Clone`, for I/O code on any thread; it exists where the
target has pointer atomics and a lock
([RFD 7](./rfd-0007-targets.md)). One rule covers both: every call
queues for the driver's next pump and returns at once, and nothing
reads through a handle. They differ only in what must be `Send`.

Both handles send, open transactions, listen in all five forms, and
anchor. `send(input, value)` queues a unit of its own.
`transaction(|tx| ...)` queues a closure that runs on the driver at the
pump, so its sends are simultaneous. It gets an `IoTransaction` from an
`Io` and a `RemoteTransaction` from a `RemoteIo`, which differ in one
bound: a listener tied to a remote's unit must be `Send`. A listen or
an anchor returns its guard at once, and its registration waits for the
pump like any call; dropping the guard first cancels it. A waiting
registration keeps the tokens it names alive until the pump runs it,
so a listener handed a row can listen to it or anchor it through a
handle, and the row lasts until the pump registers what keeps it. A
waiting send or transaction keeps nothing alive
([RFD 3](./rfd-0003-memory-model.md)). Once its queue has grown, a
remote unit allocates once, on its sender, and never on the driver.

A `RemoteIo` works with a `Local` runtime too. What crosses threads
must be `Send`, the values it sends and the listeners it registers, and
nothing else: its `anchor` takes any `Trace` value, since the value
stays on the caller's thread and only its tokens wait in the queue.

A call is checked when it's queued, in this order: the runtime has
dropped (`Gone`), it's poisoned (`Poisoned`), the call comes from graph
code (`FromGraphCode`), or a token it names is another graph's
(`ForeignGraph`). A transaction's closure hides its tokens until the
pump runs it, so a handle's `transaction` returns an
`IoTransactionError`, which has the first three, and a foreign token
there is found at the pump
([RFD 5](./rfd-0005-transaction-protocol.md)).

The driver calls `runtime.pump()`, which runs the pending input slots
by priority, then the calls both handles made before the pump began,
in the order they were made, each send or transaction as one
transaction ([RFD 5](./rfd-0005-transaction-protocol.md)). A unit is
the unit of simultaneity: it is never split and two are never merged,
which is what lets a double send inside one be reported at `pump`.

The waker is the standard library's own. A driver that is a future
stores `cx.waker().clone()` on each poll, pumps, and returns pending,
so a tokio, smol or embassy task drives the runtime with no channel in
between; a thread driver builds a waker from an `Arc` through
`alloc::task::Wake` and blocks on whatever that wakes; a bare-metal
main loop that sleeps on the interrupt itself gives `Waker::noop()`.
`core::task::Waker` needs no allocator and no atomics, so `set_waker`
exists on every target. A function pointer in an `Arc` was the first
draft; it was the same thing under a name every executor would have to
learn. A call through a handle wakes the driver unless another call
through the same kind of handle has since the last pump began, since
one wake is enough for every call that pump will run. A new waker
starts that over, and a burst through both kinds of handle wakes the
driver at most twice. Latency is the distance from a send to the next
pump, a property of where the driver sits: a woken thread pumps at
once, a future at its next poll, a frame-based host wherever its
embedder placed the runner, and an adapter states its placement and
the latency it implies.

A driver in the core is a plan, not built: a dedicated
standard-library thread that builds the runtime, hands back the edge
and a `RemoteIo`, and blocks on a condition variable until woken. How
it stops, and what it does with a panic, are open, and they would be
its API. `shutdown` and bough-gtk's `Driver` are the model: the thread
driver in the engine's tests stops when its handle is dropped, and
bough-gtk's ends when it finds the runtime poisoned. An integration
crate is then a few dozen lines: a waker for its executor, and a
driver loop if it wants one. The core has no queue type
([RFD 2](./rfd-0002-strong-io-separation.md)), and it promises no
adapters from `listen` into an executor's channel types, since a
`RemoteIo` listener that captures the user's own channel already does
that:

```rust
// Every value, to this task:
let (tx, mut totals) = tokio::sync::mpsc::unbounded_channel();
remote.listen_cell(app.total, move |t| { let _ = tx.send(*t); })?.keep();

// One value, like a promise:
let (tx, total) = tokio::sync::oneshot::channel();
remote.listen_cell_once(app.total, move |t| { let _ = tx.send(*t); })?.keep();
let total = total.await?;
```

Multiple integrations coexist because none of them owns anything; they
all hold handles. A GUI owning the runtime on its main thread, whose
handlers hold `Io`s, works with tokio network tasks holding `RemoteIo`s
at the same time, and the GUI's non-`Send` state stays in listener
closures on the driver thread. No adapter crate ships with the first
version; `bough-tokio` is the first afterwards, once the performance
bar has been measured.

## The Chat Room

One input takes a username and a line; another takes a username and
the channel that reaches that user's socket. Each per-user tokio task
holds a `RemoteIo` clone, registers its channel when the connection
opens, and sends each line it reads. The routing table is a cell in
the graph, so the one outbound listener captures nothing that changes,
and it is attached before the runtime moves into the task that pumps
it; after the move, a `RemoteIo` could register it instead. The user
writes no channel plumbing for inputs; the only channels in sight are
the per-socket ones tokio needs anyway.

```rust
type User = String;

#[derive(Trace)]
struct Members {
    #[trace(skip)]
    by_user: HashMap<User, mpsc::Sender<String>>,
}

async fn serve(listener: TcpListener) -> std::io::Result<()> {
    let (mut runtime, edge) = Runtime::build_threaded(|b| {
        let (joins, joins_in) = b.input::<(User, mpsc::Sender<String>)>();
        let (messages, messages_in) = b.input::<(User, String)>();
        let members = joins.accumulate_mut(
            b,
            Members { by_user: HashMap::new() },
            |(user, sender), m| {
                m.by_user.insert(user, sender);
            },
        );
        let outbound = messages
            .snapshot(members, |(user, line), m| {
                let recipients: Vec<_> = m.by_user.values().cloned().collect();
                (recipients, format!("{user}: {line}"))
            })
            .node(b);
        (joins_in, messages_in, outbound)
    });
    let (joins, messages, outbound) = edge.keep();

    runtime
        .listen(outbound, |(recipients, text)| {
            for sender in recipients {
                let _ = sender.try_send(text.clone());
            }
        })
        .keep();

    let remote = runtime.remote_io();
    tokio::spawn(std::future::poll_fn(move |cx| {
        runtime.set_waker(cx.waker().clone());
        runtime.pump();
        std::task::Poll::<()>::Pending
    }));

    loop {
        let (socket, address) = listener.accept().await?;
        let remote = remote.clone();
        tokio::spawn(async move {
            let user = address.to_string();
            let (reader, mut writer) = socket.into_split();
            let mut lines = BufReader::new(reader).lines();
            let (sender, mut inbox) = mpsc::channel::<String>(16);
            remote.send(joins, (user.clone(), sender)).unwrap();
            loop {
                tokio::select! {
                    line = lines.next_line() => match line {
                        Ok(Some(line)) => remote.send(messages, (user.clone(), line)).unwrap(),
                        _ => break,
                    },
                    Some(text) = inbox.recv() => {
                        if writer.write_all(text.as_bytes()).await.is_err() {
                            break;
                        }
                    }
                }
            }
        });
    }
}
```

The example compiles against the engine with tokio, which was checked
by hand outside the repository, since the repository has no tokio, and
the engine's tests run it with standard threads and channels in tokio's
place. The
driver is a future: each poll stores the task's waker, pumps, and
returns pending, and a remote's call wakes it by the rule above; there
is no channel and no notifier. An earlier sketch attached the outbound
listener after the spawn and captured the per-user senders in it,
which needs a shared map of senders behind a mutex, the plumbing this
design exists to remove. A routing table that is a cell is the FRP
answer, and it is what "anything a listener needs is snapshotted into
the graph" means in practice. For many subscribers it stays the
pattern we recommend, now that a `RemoteIo` can listen too.

## The New Hole in the Wall, and the Graph Code Re-entrancy Check

Both handles are `Clone + 'static`, so a `map` closure can capture one
and call through it from inside graph code. It is not re-entrant,
since a call only queues, but it is I/O inside FRP logic, so the graph
code re-entrancy check refuses the call with `FromGraphCode` in both
build modes: a logic error with an observable outcome, not an
unobservable one ([RFD 5](./rfd-0005-transaction-protocol.md)). The
check is armed only while graph code runs: evaluation and commit,
`accumulate_mut`'s function included, a `construct` closure and a
split's iterator, in every child instant too. It is disarmed before
the listeners run. A transaction's closure is I/O code, so
`runtime.transaction(|tx| { tx.send(a, 1); io.send(a, 2) })` queues
the second send for the next pump; arming the check for the whole
transaction was the first design, and it refused exactly that. A
listener's call queues too, which is the sanctioned way for I/O to
feed back into the graph: a later transaction, never a nested one. The
check is not the runtime's own flag, which stays set until the
transaction has finished and is the poison
([RFD 5](./rfd-0005-transaction-protocol.md)). It covers its own
runtime only: graph code calling through another runtime's handle
queues there.

The `Io`'s check is a flag its queue shares with the runtime, and it
works on every target. A `RemoteIo`'s has to tell the driver's thread
from any other, so it's a thread id the driver stores in the inbox
while graph code runs, and it exists under `std` only. On bare metal
it is documented and unchecked: interrupts use input slots, and a
`RemoteIo` call from an interrupt handler is documented misuse, since
it allocates ([RFD 7](./rfd-0007-targets.md)). Leaving the check out
and documenting the rule was the alternative; the check costs about
six instructions a transaction.

The handles also learn of the runtime's poison. Where panics unwind,
each entry that can poison marks both handles as the panic leaves it,
and elsewhere the next entry that finds the poison marks them
([RFD 5](./rfd-0005-transaction-protocol.md)). From then on every
call through either handle returns `Err(Poisoned)`, so no thread keeps
filling a queue that no pump will ever run; without the mark,
`try_pump` would fail forever while every handle kept getting `Ok`,
and the queues would grow without bound behind it. A call through a
handle whose runtime has dropped returns `Err(Gone)`, and `io()` and
`remote_io()` never panic.

## Once-Listeners

`listen_once` and `listen_cell_once` take an `FnOnce`. A once-listener
is a root until it fires, and its release counts once, when it fires,
so `keep` on its guard means until it fires, not for good.
`listen_once` fires at the stream's next event. `listen_cell_once` on
the `Runtime` runs its closure at once, with the current value, so the
closure needn't be `'static`, nor `Send` in a `Threaded` runtime.
Through a handle it runs at the pump, and that is how I/O code without
the runtime reads a cell: a pump later.

A once-listener ties to a transaction only through an explicit one,
with `tx.listen_once(...)` or `tx.listen_cell_once(...)` in a
transaction's closure, and then it covers the whole unit
([RFD 5](./rfd-0005-transaction-protocol.md)); `send` keeps its
signature. A handler doesn't see its own sends before the next pump,
and a tied once-listener is how it hears what they caused. There is no
`listen_steps_once`. It would answer "tell me when it next changes"
rather than "what is it now", and `listen_once` on a steps stream the
build made covers that; it can be added if we find a need.

One that never fires is a bug in the user's graph. We considered
returning an `Option` for it, which would change every caller's type
for the sake of a bug, so debug builds check instead: a tied one whose
stream stayed silent in its unit, and a kept one still waiting when
the runtime drops. We also considered a receipt from `send` to tie a
`listen_once` to. The `Runtime`'s `send` has already finished when it
returns, so only the handles could offer one.

The drop check is one rule: no kept once-listener may still be
waiting. A debug build with `std` panics if a runtime drops while a
once-listener whose guard was kept is still registered, or still
waiting in either handle's queue. The kept guard asked for the event
and gave up the means to let it go unheard, so the check catches an
event that never came, even in a test that forgot to assert. A held
guard isn't checked, nor is a runtime dropped while a panic unwinds or
after one poisoned it, nor a build without `std`, which can't tell
whether a panic is unwinding. An app may close with a request still
out, though, and a host that drops its runtime from C, as glib does,
would abort on the panic. So `Runtime::shutdown` ends a runtime on
purpose, without the check, and calls through its handles return
`Err(Gone)` from then on. A runtime that just goes out of scope, as in
a test, is still checked. We considered checking only in tests, but
`cfg(test)` reaches only bough's own tests.

## Only the Runtime Reads

Every read goes through the `Runtime`. Once a driver owns it, as in a
GTK app, app code reads a cell with `listen_cell_once` through a
handle, a pump later. We considered lending the runtime out between
pumps, which would bring back the double borrow, as an error in a
handler that a listener set off, and break the one rule; an `Io` that
reads was rejected too ([RFD 2](./rfd-0002-strong-io-separation.md)).
If late reads prove awkward in real code, bough-gtk can offer a
mirror, a value a listener keeps, read at once and as fresh as the
last pump. That would come later.

## What We Considered, and What It Costs

The one rule, every call at the next pump, came after four other
shapes:

- A send-only `Remote`, as this RFD first had it. Its routing table is
  still the pattern for many subscribers, but that isn't a reason to
  withhold `listen`.
- An eager `Io`, which let a handler read its own sends. It kept two
  timing rules, needed an `Owner` type and weak handles to reach the runtime,
  and ran transactions inside GTK signal handlers.
- Timing by where a call is made, so that a listener's call ran right
  after its transaction. Outside a transaction the `Io` would still
  run sooner than the `RemoteIo`, only because it can reach the
  `Runtime`.
- Running calls at once wherever possible, Sodium Java's model. The
  driver would stop being the only thread that runs transactions, and
  a host would stop owning the schedule
  ([RFD 7](./rfd-0007-targets.md)).

The costs we took:

- A handler doesn't see its own sends before the next pump. Read,
  change, send becomes send the intent and let the graph do the sum,
  and a tied once-listener gets the result.
- A chain of calls takes one pump per step, so tests pump until
  nothing is queued.
- A listener registered from a listener misses events until the next
  pump.

## Threading Modes

The handles remove most of the pressure, but a non-`Send` runtime
still has to be built on the thread that runs it, so a tokio-native
user cannot hold it in a spawned task or behind an `Arc<Mutex>`. The
runtime and the build context take a mode parameter, declared as
`struct Runtime<M: Mode = Local>` and `struct Build<M: Mode = Local>`.
In `Threaded` mode every value and closure the runtime stores must be
`Send`, checked once per materialization and at `listen` through a
per-mode `Accepts<T>` trait, and `Runtime<Threaded>` is `Send` because
every field is: the compiler derives it, with no `unsafe impl`. `Build`
carries the mode because materializers see only `Build`, so the check
has nowhere else to attach: a threaded runtime's build closure receives
a `Build<Threaded>`, and an `Rc` captured in a closure there is a
compile error, which fifty `compile_fail` tests pin across every place
a runtime stores a value. Single-threaded users never see either
parameter, and their `Rc<RefCell<UiState>>` captures keep compiling. A
helper generic over the mode can't write closures of its own, since
the bound it would need names a closure type (E0277); it works with the
caller's closures, with function pointers, or through a per-mode
trait. `Runtime::build` builds a `Local` runtime and
`Runtime::build_threaded` a `Threaded` one, two constructors rather
than one, because a defaulted type parameter takes no part in
inferring an associated function: `Runtime::build(|b| ...)` with a
generic `build` is "type annotations needed", and two inherent
`build`s are ambiguous, as a stub of the API confirmed. Tokens are
plain integers and `Send` in every mode. Neither guards nor handles
carry the mode: a guard is `Send` wherever the target has pointer
atomics, in either mode, an `Io` exists only for a `Local` runtime,
and a `Threaded` runtime has only the `RemoteIo`. `Threaded` itself
exists only where the target has pointer atomics
([RFD 7](./rfd-0007-targets.md)).

Requiring `Send` everywhere would have killed the UI case, where
widgets are not `Send`. A non-`Send`-only runtime would have left
tokio users with the dedicated-thread driver as the sole option, which
is friction on the first line. Retrofitting a type parameter touches
every signature, which is why this is decided now rather than later.
