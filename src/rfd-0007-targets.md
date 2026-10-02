# Targets: No-std Tiers, Input Slots, and Host Embedding

**State:** discussion · **Authors:** Zefira Shannon, Claude

Three targets became first class after the first six RFDs were written:
bare metal, meaning Cortex-M3 and M4 boards and later a Cortex-M0; the
Bevy game engine as a host; and the web through `wasm32-unknown-unknown`
and wasm-bindgen. Each was checked against the design as it stood, with
the research in [`research/`](./research/2026-09-22-no-std-handoff.md)
carrying the evidence, and each changed something. This RFD records the
decisions that are costly to undo: the tiers the engine ships in, the
input slot, what a target without atomics keeps, and the rules a host
must follow. The smaller consequences are edited into the RFDs they
belong to.

## Two Tiers, and a Third Later

The core is `no_std` over `alloc`, and `std` is a feature, on by
default, that adds the `RemoteIo`'s graph code re-entrancy check,
`Trace` for the standard collections and `Instant`, and the standard
mutex under input slots and the `RemoteIo`'s inbox. Two more things
need `std`, since they need code to run as a panic unwinds, or to know
whether one is: marking the poison in the handles on a panic's way out
([RFD 5](./rfd-0005-transaction-protocol.md)), and the debug check as
a runtime drops ([RFD 6](./rfd-0006-io-edge.md)). The memory-model
principle that a graph pays for allocation only while it grows
([RFD 3](./rfd-0003-memory-model.md)) becomes a rule: the engine
allocates at build and inside `construct`, and when I/O code registers
a listener or an anchor or calls through a handle, and nowhere else.
Every per-transaction structure is reused, and the arena and those
structures sit behind a `pub(crate)` storage seam. The child scheduler
is iterative: a recursive one overflowed a 256 KiB stack on a
countdown 100,000 levels deep, and the iterative one keeps one buffer
per depth ever reached. Both boards we own have allocators, so this
tier is meant to run the button-to-LED milestone on the F303 Discovery
and on the Due. That is a plan, not built: nothing has run on ARM yet.

A third tier would follow once the engine works: a bounded storage
backend behind that seam, with a fixed number of slots the caller
provides, so a graph that never grows never allocates at all. It is a
plan, not built. It brings one new failure, `construct` finding no free
slot, which would be a panic that poisons the runtime. Its open
questions:

- Every handle call allocates, and the handles' queues grow.
- Which error types get an `Exhausted` variant.
- Whether `IoError` needs a case for a full queue.
- Whether a waiting call needs to fit in 24 bytes, as the
  [research](./research/2026-09-27-io-edge-spike.md) sketches.

Under the rule that no error type carries a variant an operation cannot
return, an `Exhausted` variant doesn't exist until then, and adding one
is a breaking change; the bounded tier is a major version, and we
accept that rather than mark every error type `#[non_exhaustive]` today
or route exhaustion through a second call. Exhaustion is not a
semantics deviation: a program that exhausts the arena gets no answer,
loudly, the way a `std` program aborts on allocation failure, never a
different answer.

A static engine, the graph fixed at compile time in the types with no
node table and no allocation, was explored and rejected for the core.
The exploration in
[`research/`](./research/2026-09-23-static-engine-exploration.md)
compiled the alternatives for all three Cortex-M targets. The static
engine is smaller by a wide margin, about nine kilobytes of code and 1.4
kilobytes of RAM for a three-hundred-node program against seventy-six
and 7.6 for the bounded dynamic engine, and it pays for that with a
second front end, since a hand-written type-level builder stops being
checkable somewhere between a hundred and three hundred nodes and a
proc-macro front end sees syntax rather than types; a second testing
harness, because a type-level program cannot be generated at run time
for the oracle; and either a subset of the semantics without
`construct` or pooled `construct` that brings a collector back per
pool. It is a separate product with the same semantics, worth building
someday as its own project, and not this one.

The dependency policy in [RFD 1](./rfd-0001-guiding-principles.md)
allows a feature to add a crate when that crate is the seam an
ecosystem already implements, and this is the case it was written for:
the engine crate depends on no other crate in its default feature set,
and a `critical-section` feature adds the crate of that name, which is
the seam every embedded HAL implements, to guard input slots and the
`RemoteIo`'s inbox on bare metal. A `Lock` trait the embedder
implements would have kept the count at zero and made every embedded
user write glue the ecosystem already wrote once; in-tree inline
assembly per architecture would have been a port of the same crate.

## What a Target Has

Everything the I/O surface shares between threads is an `Arc`, and an
`Arc` needs compare-and-swap. A Cortex-M3 or M4 has it; a Cortex-M0 has
32-bit loads and stores and no read-modify-write, and `alloc::sync` does
not exist there. A lock is the other need: `core` and `alloc` have no
safe lock to share between threads, and a spin lock needs `unsafe` and
deadlocks against an interrupt, so a lock is `std` or
`critical-section`. So `Threaded` exists where the target has pointer
atomics, the way `std::sync::Arc` itself does; input slots exist where
there is a lock; and the `RemoteIo` needs both. The `Io`, `IoError` and
`PumpError` exist everywhere, since the `Io`'s queue is the runtime's
own and needs no lock, and `core::task::Waker` is in `core` and needs
no atomics, so `set_waker` exists everywhere too. A thumbv7m build with
neither `std` nor `critical-section` keeps `pump`, `set_waker` and the
`Io`. A Cortex-M0 gets `Local`, the `Io`, and input slots with
`critical-section`, which is what an interrupt-driven main loop needs,
and its guards aren't `Send`. The M0 is not a board we own; it is the
floor the design reaches without a `portable-atomic` dependency,
verified by CI's cross checks, by the table below, and on the engine
spike by release builds for thumbv6m and thumbv7m that instantiate
every node kind.

| Type | Exists | `Send` |
|---|---|---|
| `Runtime<Local>` | everywhere | no |
| `Io` | everywhere | no |
| the tokens | everywhere | yes, whatever they carry |
| `Listener`, `Anchor` | everywhere | with pointer atomics |
| `Anchored<T>` | everywhere | where `T` is, with pointer atomics |
| `Runtime<Threaded>` | with pointer atomics | yes |
| `InputSlot` | with a lock | `Sync`, since it lives in a `static` |
| `RemoteIo` | with pointer atomics and a lock | yes, and `Sync` |

The engine checks the table at compile time on every target CI checks:
a type missing where its row says it exists breaks the build there, and
so does a type that is `Send` where its row says it isn't, or the
reverse. Absence isn't checked, so a type that exists where its row
says it doesn't would compile unnoticed; today the code can't compile
there anyway, since there's no `Arc` without pointer atomics and no
inbox without a lock.

On `wasm32-unknown-unknown` the gate is true, so `Threaded` exists, and
with `std` the `RemoteIo`, with no threads to use them, and `Local` is
the web mode: a stable build cannot share a runtime across web
workers, and a worker feeds the runtime by posting a message to the
main thread. On a non-atomics wasm build `JsValue` and every `web_sys`
object are `Send`, so `Threaded` would accept them, while a `Closure`
is not; nothing to decide, one sentence in the mode documentation.

There is one kind of guard, with no mode parameter: a guard is `Send`
wherever the target has pointer atomics, in either mode, and not on the
M0. Checking whether a guard is live costs two instructions a listener
call on x86, and none on the Cortex-M3 or aarch64, where a relaxed
load compiles to the same code as a plain one; the ARM half is read
from the compiled code, not measured
([research](./research/2026-09-27-io-edge-spike.md)). We considered two
kinds of guard, a `LocalListener` beside `Listener`, which saves those
instructions, costs a second method for every registration, and adds
no guarantee, since every callback runs on the runtime's thread either
way; and a `Send` guard on the M0, through `critical-section` and
`portable-atomic-util`, which adds a dependency for a case nobody has
asked for.

## Input Slots

Interrupt handlers, GTK callbacks and tokio tasks all hand input to a
single-threaded core without racing a transaction. GTK callbacks hold
an `Io`, and tokio tasks a `RemoteIo`
([RFD 6](./rfd-0006-io-edge.md)). An interrupt handler needs something
else: it has no allocator, no lifetime and no `Arc`, it fires in
bursts, and a queue that grows during a burst is a fault on a
microcontroller.

An input slot is a value the writer owns, which for an interrupt handler
means a `static`:

```rust
static PRESSES: InputSlot<u32> = InputSlot::new(|a, b| a + b);
```

It holds one pending event. A write when one is pending folds the two
with the slot's fold, pending on the left, so a burst between two pumps
becomes one event and the slot never grows. The fold is a `fn` pointer so
that the type can be named in a `static`; a closure that captures nothing
converts to one. Every slot has a fold, and dropping the older event is
spelled `keep_latest`, so the drop is declared rather than silent, the
way the first design refused silent last-wins for a double send. An
overflow counter was the alternative, and a counter is a decision nobody
made.

Build connects a slot to an input, `b.connect(input, &PRESSES, priority)`,
callable more than once for one input with one slot per producer; a
second producer gets a second slot. A slot feeds one input of one
runtime: `connect` panics on a slot that is connected already, and a
runtime that drops disconnects its slots. A connection is not a root:
the input lives while something else reaches it
([RFD 3](./rfd-0003-memory-model.md)). The slot's fold and the input's
coalescing function are independent declarations with different jobs:
the fold combines a burst between two pumps, the coalescing function
combines two sends inside one transaction, and slots never cause the
second, since `pump` runs each pending slot as a transaction of its
own. A constructor per combination would have doubled the four input
constructors to six.

The priority is a `u8`, and higher drains first, as in RTIC and the
opposite of the NVIC's numbers; equal priorities drain in connection
order. After each whole unit, children included, the highest-priority
pending slot runs next, and the handles' calls rank below every slot.
Each slot drains at most once per pump, marked as the pump picks it,
so a pump is bounded however often listeners and interrupts write slots
while it runs. Each slot keeps its own pending flag, set and cleared
under its lock and read by the pump without it, because a `static`
slot on the M0 can't reach anything the runtime owns. We considered
lower numbers first, as the NVIC has it: everyone but Cortex-M users
would read it backwards, and an interrupt's NVIC number usually isn't
the order the graph wants anyway.

Two slots are never simultaneous, and that is a rule about the semantics
rather than a convenience. Simultaneity means caused by the same external
event, and `merge` combines simultaneous events through its function, so
two unrelated inputs made simultaneous by the timing of a drain would be
combined into one event, a different answer rather than a coarser one.
The Bevy port's research reached the same conclusion for frame batching
([`research/`](./research/2026-09-23-frp-host-embedding-requirements.md)).
A genuinely simultaneous multi-input event is a tuple input, or a queued
unit. The per-transaction cost is a counter and reused buffers, so five
sensor slots at a kilohertz are five transactions a millisecond.

The law the fold obeys: a slot's external sequence is cut into runs by
when the driver pumps, which is timing the semantics do not see, and each
run folds left to right in arrival order into one event. So the fold must
be associative, and it need not be commutative because a slot has one
producer. That is documented and property-tested: for random event
sequences and random partitions into runs, the engine's output equals
GHC's fed the folded runs, and under random priorities and pre-emption
a model of the pump predicts every drain, which the engine matches
drain for drain. Requiring commutativity would have allowed several
producers on one slot and forbidden `keep_latest`, the commonest fold.

The slot is guarded by a critical section on bare metal, through the
`critical-section` feature, and by the standard mutex under `std`. The
standard mutex is unfair: on the engine spike, a writer hammering a
slot held off the driver's drain for a whole 20,000-write burst. The
slot never grows, so only latency suffers. A web build keeps `std`; the
crate ships no critical section for wasm, so a `no_std` web build
registers a single-core no-op itself. The waker a slot write wakes is a
`core::task::Waker`, so an embedded async executor that builds wakers
without an allocator drives the runtime the same way a desktop executor
does. The first sketch had a per-input slot inside the runtime's own
inbox; that puts the slot behind the runtime's ownership, and reaching
it from an interrupt needs an `Arc` the M0 lacks or a `&'static` an
owned runtime cannot give without a leak.

## The Graph Code Re-entrancy Check, and Retirement

A `RemoteIo` call from graph code is refused, and the check needs a
thread id, which `std` has and bare metal does not, so the `RemoteIo`'s
check exists under `std` only; the `Io`'s exists everywhere
([RFD 6](./rfd-0006-io-edge.md)). On bare metal the legitimate other
context is an interrupt handler, which this RFD serves with slots, so a
`RemoteIo` call from one is documented misuse, since it allocates. A
Cortex-M port that reads the IPSR register to tell a handler from the
main thread is untried, and a later addition if the misuse bites, not a
maintenance surface for a hypothetical.

A slot's generation is a `u32` bumped on every free. A device that runs
for months could wrap it, and a stale token from before the wrap would
then validate. A slot whose generation reaches its maximum is retired
and never reused, one compare on free; with a first-in first-out free
list the churn spreads across every slot, so retirement is astronomically
rare in practice and the stale-token guarantee stays true without a
footnote. Widening to `u64` would make a token sixteen bytes and cost an
atomic the M3 and M4 cannot update. A harness that estimates a program's
uptime from its measured churn is an idea in
[`notes/`](./notes/2026-09-23-slot-churn-simulation.md).

## Hosts

A host owns the schedule: a game engine's frame loop, a browser's event
loop, a GUI toolkit's main loop. Bough's answer to each is the same
shape. The runtime is library-owned; a driver the host schedules pumps
what the handles and slots queued, inside the host's own critical
section; each external cause is one unit and one transaction; latency
is the distance from a send to the next pump, a property of where the
embedder placed the driver, which an adapter states.

Bevy gets a `bough-bevy` adapter after the performance bar is measured,
on the same terms as `bough-tokio`: the runtime a resource, an
exclusive system as the runner, every host message its own unit, never
a frame batched into one transaction. The health-and-shield slice from
the Bevy port's research is the adapter's example, and the engine
already gives GHC's values on it, long before the adapter exists. A
fully ECS-native port, nodes as entities and edges as the host's
relationships, stays a separate project; it is that project's
experiment, and the fan-in wall it hit is a property of that bet. The
research also asked for the graph representation to be a public backend
interface, so an embedder could choose library-owned or host-owned
storage. Rejected: the trait would be the whole of
[RFD 5](./rfd-0005-transaction-protocol.md) guessed before any of it
exists, and chain fusion is only possible when the library owns
storage. The internal storage seam is the narrower thing both new
targets need, and a public trait, if ever, is extracted from a working
engine.

GTK is the host that has run. bough-gtk, a prototype beside the
engine, gives the runtime to a driver: `spawn_driver(runtime)` returns
a `Driver`, whose future registers its waker and calls `try_pump` on
each wake, and dropping the `Driver` stops the pumping. Signal handlers
hold an `Io`, and app code reads with `listen_cell_once`, a pump later,
since the driver owns the runtime. Two lessons came out of it. A host
that drops its runtime from C calls `shutdown`: glib drops an aborted
local future at the main loop's next turn, from C, where a panic
aborts, and the debug check as a runtime drops can panic
([RFD 6](./rfd-0006-io-edge.md)). And a list view's rows are right a
pump later: GTK binds new rows inside the listener that changed the
list's model, and their labels fill in at the next pump, so a reused
row can show its old text for a frame during animated scrolling, a cost
we accept. A panic in a GTK signal handler aborts the process, which is
why a handle's calls return a `Result` rather than panic. Untested: a
real scroll, Wayland, touchpad flings, and glib's catch of a panic that
escapes a future's poll, which is read from glib's source.

The web fits closely, and the research in
[`research/`](./research/2026-09-23-wasm-target-research.md) verified
each of its claims by compiling or running it, with the `Remote` of the
time. `Local` is the web mode. A DOM callback calls through an `Io`,
never through the runtime directly, because `dispatchEvent` runs
listeners synchronously and nested: a closure holding the runtime in
`Rc<RefCell<_>>` that sends directly traps on a double borrow the
moment a Bough listener dispatches a DOM event whose closure sends
again, and on that target a trap leaves the module callable but
damaged. The driver is a future spawned with `spawn_local` that stores
its waker, pumps and returns pending; the pump runs as a microtask,
before the next task and before the next paint. `bough-web`, which
comes after the bar like the others and isn't built, is to give the
runtime only to the driver and route every DOM closure through an
`Io`; direct sends stay possible with the hazard stated. Nothing has run on the web with an `Io` yet. The trap to
avoid is pumping on `requestAnimationFrame`, which delays every
transaction to the next frame and stops in a hidden tab.

That target has no unwinding: a panic is a trap, no drop guard runs,
and `catch_unwind` compiles but catches nothing. This is why the poison
is the transaction-in-progress flag itself, which needs nothing to run
([RFD 5](./rfd-0005-transaction-protocol.md)). Where panics unwind, the
handles are marked on the panic's way out; on the web they aren't, so
until an entry on the runtime finds the poison, a handle's call says
`FromGraphCode` after a panic in graph code, and is accepted and lost
after one anywhere else. A web adapter would tear the runtime down at
the first `Poisoned` its driver sees; none is built yet.

## Testing and CI

Continuous integration checks the core on seven configurations:
`thumbv7m-none-eabi` and `thumbv6m-none-eabi`, each without default
features and with `critical-section`; `thumbv7em-none-eabihf` without
default features; and `wasm32-unknown-unknown` with and without them,
so a standard-library use that creeps into the core fails the build the
day it lands. The capability table rides on these checks. CI also
checks the minimum supported Rust version, 1.85. A
`wasm32-wasip1` leg under wasmtime is to run the engine's own tests on
a 32-bit abort target, with proptest's default features off, which do
not build for wasm, and the build-time panic tests explicitly ignored
there, where libtest would otherwise skip them in silence. GHC can't
run there, so the oracle stays on the host
([RFD 1](./rfd-0001-guiding-principles.md)). That leg isn't built. A
Node leg under `wasm-bindgen-test` would be for `bough-web` alone, and
neither is built. Wasm code size is to be reported as information
beside trivial-payload overhead, with no analogue of the
instruction-count gate, and nothing reports it yet; the research
measured about two hundred and seventy bytes per monomorphized node
type after `wasm-opt`.

The first embedded milestone is a button press through a small graph to
an LED on the F303 Discovery, bare metal. It is to live under
`examples/` in the `bough` repository as a crate of its own,
cross-compiled in continuous integration for its target and never run
there. It is a plan, not built.
