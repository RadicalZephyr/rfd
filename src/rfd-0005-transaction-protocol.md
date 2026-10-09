# Transaction Protocol and Failure Modes

**State:** discussion · **Authors:** Zefira Shannon, Claude

Sodium's implementations schedule with node ranks and a priority
queue, re-rank nodes mid-transaction when a switch happens, coalesce
double deliveries, and apply holds in a "last" phase. Most of that
machinery exists to recover, at run time, invariants the denotational
semantics state directly. This RFD derives the transaction from those
invariants and then records what the semantics leave open: listeners,
panics, and misuse.

## What the Semantics Fix

Cells are read strictly before the instant. The semantics' `at` keeps
steps with `tt < t`, so every snapshot, sample and switch selection
inside transaction t sees the pre-t value. Holds therefore commit at
the end of a transaction, and cell reads impose no ordering inside
one. Half of the Java implementation's priority machinery exists to
get this right by scheduling; we get it by construction, with a
committed value that only changes at commit.

Only dependencies need ordering, and a read of a cell is never one. A
merge needs both inputs' events at t, a filter needs one, a snapshot
needs its stream plus a pre-t cell read. A read-through cell is
ordered too, since whether it stepped is settled in dependency order,
but settling it runs no user code: it stepped if and only if one of its
dependencies stepped ([RFD 4](./rfd-0004-value-model.md)). `SwitchS`
uses the stream selected before t for t itself, so the topology in
effect during t is fixed before t starts. A `switch_stream`'s outer is
not its dependency, since that would refuse the legal navigation loop
through its selection; it only tells the switch to move, so a selector
step moves the switch even while the old inner is quiet. Every switch
moves at commit, together with the holds, and the graph is checked for
a same-instant cycle once they all have: two switches may reverse a
dependency between them in one instant, which one move at a time would
read as a cycle. For the same reason, every linear stream a switch lets
go is released before any switch takes one, so two switches may trade
linear streams in one instant. A `switch_stream` built during t links
its first inner at t, and runs it then, so the switch sees the inner's
event at t.

Each stream has at most one event per instant, and each cell at most
one step. The semantics enforce this with `coalesce` in five places,
and two of them do work: `Value` and `SwitchC` collapse a creation and
a step, or a switch and a step, at one instant into one step carrying
the later value. Here that holds by construction: a node is marked
once per transaction and evaluated once, a cell's value is committed
once, and a `steps_with_current` or `switch_cell` created or switched
at t emits the post-t value it reads, so there is never a second
delivery to collapse. `Merge`'s `coalesce` is the user's combining
function rather than engine policy, and `Hold`'s and `Split`'s are
vacuous under the one-event-per-instant invariant. Sodium's
last-firing-only machinery exists to recover this at run time and has
nothing to do here.

`SwitchC` is the one forward-looking primitive. At a switch instant it
drops the old inner's step and emits the new inner's post-instant
value, and it emits a step at every switch instant, and at creation,
even when the new inner is quiet. The post-instant value of a hold is
its input's event at t if there is one, else its current value,
so this step needs the new inner's input evaluated at t, a
dependency only discoverable mid-transaction. This single primitive is
why Sodium re-ranks nodes and rebuilds its queue during a transaction.

Things created at an instant exist from that instant inclusive. A hold
keeps events with `t >= t0`, `Value` fires at t0 with the
post-t0 value, and `Execute` lets an event at t build graph at t.
A node built inside a `construct` closure must be able to read
events already computed in this transaction. The nodes a closure built
are linked into the graph as they are built, and they run at t once
the closure has returned, each after what it depends on, by pull, not
in creation order, since a loop's forward token is created before its
definition.

A construct built at t0 runs its closure for its source's events from
t0 on, t0 included. The text's `Execute` has no creation time, so in
the text a construct built inside a closure also runs its own closure
for events from before it existed. Nothing built at t0 can see those
runs, so the difference isn't observable, but a loop inside such a
closure can fail to settle in the oracle, so its random programs keep
loops out of construct closures. Giving the oracle's `construct` the
engine's cut, and then letting loops in, is an experiment still open
([bough-frp/bough#13](https://github.com/bough-frp/bough/issues/13)).

Time is a list of integers. `Split` produces children `t ++ [n]`,
which run after t and before t's successor, depth first, and every
`split` and `defer` at t shares t's children, so two splits in the
same t share child indices, and a `defer` is a split of one element,
at index 0. Transaction zero has children too: a `defer` that fires
during the build runs at `[0, 0]`, before `build` returns. That is the
complete specification of the post-transaction queue, except where the
text breaks its own rules, where Bough follows the rules, as
[RFD 1](./rfd-0001-guiding-principles.md)'s policy says:

- A `split` fed by its own children gives its events in time order.
  The text's `concatMap` puts them out of order, and a merge downstream
  then sees two events at one instant. The oracle sorts the text's
  events by time, stably.
- A `split` or a `defer` built at a child instant gives nothing from
  before it existed, as Sodium's Java does. The text turns the event of
  the instant it was built at into children that come after it exists,
  so they're observable. A fixed test pins both answers. The oracle's
  patch isn't built, so its random programs keep splits and defers out
  of closures that may run at a child instant.

And the Haskell knot-tying for accumulators works only because an
event's time is known before its value. Operationally, the dependency
graph stays acyclic: every path around a loop crosses a read of a cell
from before the instant, or a `split`'s or a `defer`'s child instant
([RFD 2](./rfd-0002-strong-io-separation.md)). A same-instant cycle
has no meaning, and the engine refuses it: at close, at a switch's
first link, or at a switch's move, where it is a run-time error that
poisons. The Java implementation does not; its rank code terminates on
a cycle and carries on with inconsistent ranks. The rule does not bound
a transaction: a loop through `defer` with no filter never ends, in the
text and in the engine, and `send` never returns.

## The Transaction

```
begin      sends write into input slots for t
mark       depth-first walk over dependents from the fired inputs;
           its reverse post-order is a topological order of exactly
           the affected region, read-through cells included
evaluate   a flat loop over that order; each node reads its inputs'
           slots, and a read-through cell settles whether it stepped
           from its dependencies without running user code; memoized
           pull is the fallback for two dynamic cases only:
           switch_cell reading a newly selected inner at the switch
           instant, and nodes created during t
commit     holds move their slot into current; accumulate_mut runs
           its function; the memos of read-through cells that
           stepped are cleared; every switch moves, and then the
           graph is checked for a same-instant cycle; nodes created
           during t were linked as they were built
dispatch   stream listeners run from the finished slots in the
           evaluation order of their streams; cell listeners run for
           every cell that stepped and read the committed value; ties
           by registration order
children   t ++ [0], t ++ [1], ... each a full transaction, depth
           first, all inside the call that ran the unit
collect    after the whole unit, a collection if one is due
           (RFD 3)
```

One pass yields the order, so evaluation has no recursion, no priority
queue, no maintained ranks, and no memoization checks on the fast
path. Cost is linear in the affected region with small constants,
which is what every workload shape wants. For UI the region is small.
For a frame simulation the region is most of the graph, and a heap
would have added a log factor there. For shallow high-rate events the
fixed cost is a counter bump and two reused vectors. Slots are stamped
with the transaction id, so nothing needs clearing between
transactions, and a linear consumer takes its value out of the slot, so
nothing lingers. The build closure runs as transaction zero.

A `steps` or `steps_with_current` node over a read-through cell is a
stream node in that order like any other. It computes from its
inputs' post-t values, a hold's slot if the hold fired at t and its
current value otherwise, which is the same forward-looking read
`switch_cell` makes at a switch instant
([RFD 4](./rfd-0004-value-model.md)).

A read of a cell's value follows a `switch_cell` to the inner its
outer selects, and a selection is checked for cycles only when the
switch links it. So a read can go around a same-instant cycle the check
hasn't seen yet, through a switch built at t and not yet linked, or
through a move not yet checked, and without a check it would overflow
the stack. Instead the read panics, which poisons the runtime. Each
read carries Brent's cycle detection over the `switch_cell`s it
passes, at about 2 ns per `switch_cell`
([research](./research/2026-09-24-engine-feasibility-spike.md)).

A `pump` runs each pending input slot as a transaction of its own,
higher priority first and equal priorities in connection order, each
at most once per pump, and after each whole unit, children included, a
slot that has become pending pre-empts what's next. Then it runs the
calls both handles made before the pump began, in the order they were
made: a send or a transaction as a unit of its own, and a
registration. Calls rank below every slot, and a call made during the
pump waits for the next one, so a listener that always sends can't keep
a pump from returning ([RFD 6](./rfd-0006-io-edge.md),
[RFD 7](./rfd-0007-targets.md)). Simultaneity comes only from a unit,
which is one external cause declared as such, and never from the timing
of a drain.

We considered rank-ordered push, Sodium's design, and pure memoized
pull. Ranks must exceed all dynamically reachable inners for a switch
node, which is unknowable in advance and is exactly what forces Sodium
to re-rank and rebuild its queue mid-transaction. Pull handles a
dynamic dependency by following the pointer it just read, and it
matches the semantics' `occs` clauses almost line for line, but it
pays a stamp check per read and recurses as deep as the graph. It
survives only as the fallback for the two dynamic cases, where the
recursion is bounded by the depth of the region it pulls: the inners
under a switch, or the nodes a `construct` closure built.

## Listeners After Commit

A listener runs on the thread that called `send`, `transaction` or
`pump`, after commit. Listeners have no runtime access
([RFD 2](./rfd-0002-strong-io-separation.md)), so whether they run
before or after commit is unobservable except through panics. After
commit, a panicking listener leaves a consistent graph, and dispatch
is a tight loop over a collected list. Sodium delivers during the
transaction so that a listener may sample the pre-instant value; we
removed sampling from listeners instead. Cell listeners receive a
reference to the committed value, which is the post-instant value,
matching the semantics' `Value`; they fire for every cell that stepped
in the transaction, read-through cells included, and for a
read-through cell that read is the first computation after its memo
was cleared.

A once-listener that a transaction's closure ties to its unit, through
`listen_once` or `listen_cell_once` on a `Transaction`, an
`IoTransaction` or a `RemoteTransaction`, belongs to the unit and ends
with it. A tied stream listener hears the first event its stream
fires anywhere in the unit, children included, and runs as a listener
does, after that instant's commit. One that heard nothing is a panic in
a debug build once the unit is done, and is dropped in a release build.
A tied cell listener runs once the unit is done, outside it, with the
cell's value then. A queued unit that fails is dropped whole, and its
tied listeners with it.

## Misuse

Construction errors panic. A same-instant cycle found at close or at a
switch's first link, a second consumer of a cell holding linear
streams, a loop declared and never closed, and a stale or foreign
token in graph code are all deterministic and are found the first time
the code runs. Three are found only at run time, and each is a panic
that poisons: a switch's move that closes a same-instant cycle, a
`switch_cell` that selects a cell whose linear streams another switch
already takes from, and a read that goes around a same-instant cycle
through `switch_cell` selections. A double send to a non-coalescing
input is a run-time failure, listed below.

I/O operations that can fail have a `try_` sibling returning a
`Result`, except a handle's calls, which return a `Result` and have no
panicking form ([RFD 2](./rfd-0002-strong-io-separation.md)). Each
family of operations with the same failure modes has its own error
type, and no type carries a variant that one of its operations cannot
return:

| Operations | Error type and failure modes |
|---|---|
| `Runtime::try_send` | `SendError`: `Stale`, `ForeignGraph`, `Poisoned`; one send opens one transaction, so no double send can occur |
| `Transaction::try_send` | `TransactionSendError`: `Stale`, `ForeignGraph`, `DoubleSend`; poisoning is checked once, when the transaction is opened |
| `Transaction::try_listen_once`, `try_listen_cell_once` | `TransactionListenError`: `Stale`, `ForeignGraph`; a transaction only opens on a runtime that isn't poisoned |
| `Runtime::try_transaction`, `try_collect_garbage` | `PoisonedError` |
| `Runtime::try_pump` | `PumpError`: `Poisoned`, `Stale`, `DoubleSend`, `ForeignGraph`; whether an input is collected or coalesces is graph knowledge, and a queued transaction's closure hides its tokens, so a stale send, a double send or a foreign token inside a queued unit, or a slot connected to an input since collected, is only discoverable when the driver pumps; the failing call or slot is dropped whole and the rest stay pending, and a stale slot is disconnected |
| `Runtime::try_listen`, `try_listen_cell`, `try_listen_steps`, `try_listen_once`, `try_listen_cell_once`, `try_anchor`, `try_sample` | `TokenError`: `Stale`, `ForeignGraph`, `Poisoned` |
| a handle's `send`, `listen`, `listen_cell`, `listen_steps`, `listen_once`, `listen_cell_once` and `anchor` | `IoError`: `Gone`, `Poisoned`, `FromGraphCode`, `ForeignGraph`, checked in that order |
| a handle's `transaction` | `IoTransactionError`: `Gone`, `Poisoned`, `FromGraphCode`; it converts into an `IoError`, so `?` takes one into the other |

The panicking variants panic on misuse in both build modes, with one
class excepted. An operation on a collected node whose effect is
unobservable by the semantics, meaning sending to a collected input,
listening to a collected stream, or anchoring a collected node, is a
debug-mode panic and a release-mode no-op in the panicking variant,
following the integer-overflow precedent, and is counted on the
runtime so a release build can report that it is dropping sends. A
send queued through a handle whose input was collected before the
driver pumps is discovered at `pump` and follows the same rule: a
release `pump` skips it, counts it and runs the unit's other sends,
while `try_pump` drops the unit whole and returns `Stale`. Sampling a
collected cell must return something, so `sample` panics and
`try_sample` returns `Err`. A double send is a violation with an
observable outcome either way, so it is an error in both modes;
last-wins in release would mean production behaves differently from
every test that ever ran. A foreign token in `Runtime::send`, or a
stale one in a debug build, panics before the send's transaction
opens, which leaves the runtime usable; inside `Transaction::send` the
same panic escapes a transaction, so it poisons. A handle's call from
graph code returns `FromGraphCode` in both build modes
([RFD 6](./rfd-0006-io-edge.md)).

## Panics

Any panic that escapes a transaction poisons the runtime, whether it
leaves through `send`, `transaction` or `pump` or through a child
transaction they run, and so does a panic in a `Drop` that a
collection runs. Every later call fails with `Poisoned`. A user
function panicking during evaluation or commit leaves the graph
mid-transaction. A listener panicking during dispatch leaves the graph
committed but with the rest of that transaction's listeners unrun and
its child transactions still queued, so the semantic timeline is
incomplete. One rule covers both. A panic outside a transaction leaves
the runtime usable: a tied cell listener's, which runs after its unit,
and a cell listener's call at registration, which `listen_cell` and the
runtime's `listen_cell_once` make.

The poison is the transaction-in-progress flag itself. Begin sets it,
and only a transaction that finishes, children and listeners included,
clears it, so an entry that finds it set outside a transaction knows a
transaction never finished and reports `Poisoned`. There is no separate
bit, which matters on the targets where a panic is a trap rather than
an unwind: on `wasm32-unknown-unknown` no Rust code runs after the
panic hook, while a flag that was already set needs nothing to run
([RFD 7](./rfd-0007-targets.md)). The check is the one every entry
already makes against a smuggled `Runtime`. A transaction never runs
under the inbox lock, so a panic leaves the lock free.

The handles can't see the flag, since they reach the runtime only
through their queues. Where panics unwind, under `std`, each entry that
can poison catches the panic on its way out with `catch_unwind`, marks
the poison in both handles, and resumes it with `resume_unwind`, so
every handle call says `Poisoned` at once, from any thread. That costs
two instructions a send. Where a panic is a trap, as on wasm, nothing
runs after it, and without `std` there is no `catch_unwind` to run, so
the handles learn of the panic only when an entry on the runtime finds
the flag. Until then, after a
panic in graph code a handle's call says `FromGraphCode`, since the
graph code re-entrancy check is still armed, and after one anywhere
else the call is accepted and lost. One way to close that window is
untried: on wasm, `std::thread::panicking()` stays true after a trap,
as the wasm research found in Node, so a handle could check it
([research](./research/2026-09-23-wasm-target-research.md)).

A user who wants a listener to survive its own panic wraps it in
`catch_unwind`, where the consequence is visible; that exists only
where panics unwind, and on an abort target the module is damaged
after any panic, so a web adapter would tear the runtime down at the
first `Poisoned` its driver sees; none is built yet. Rollback needs an undo log for a case that
is a bug by definition, and leaving the state undefined is how you get
a wrong answer an hour later. "Transaction" here means atomicity of
visibility, holds commit together at the end and listeners see only
committed state, not abortability.
