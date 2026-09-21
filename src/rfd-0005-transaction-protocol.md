# Transaction Protocol and Failure Modes

**State:** discussion · **Authors:** Zefira Shannon, Claude

Sodium's implementations schedule with node ranks and a priority
queue, re-rank nodes mid-transaction when a switch happens, coalesce
double deliveries, and apply holds in a "last" phase. Most of that
machinery exists to recover, at runtime, invariants the denotational
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

Only stream-to-stream edges need ordering. A merge needs both inputs'
occurrences at t, a filter needs one, a snapshot needs its stream plus
a pre-t cell read. `SwitchS` uses the stream selected before t for t
itself, so the topology in effect during t is fixed before t starts,
and all relinking happens at commit together with the holds.

Each stream has at most one occurrence per instant; `Merge` and `Hold`
both coalesce. Per-transaction stream state is one `Option<A>`, and
with correct ordering there is never a second delivery, so the
internal coalescing and last-firing-only machinery disappears.

`SwitchC` is the one forward-looking primitive. At a switch instant it
drops the old inner's step and emits the new inner's post-instant
value, and it emits a step at every switch instant, and at creation,
even when the new inner is quiet. The post-instant value of a hold is
its input's occurrence at t if there is one, else its current value,
so this update needs the new inner's input evaluated at t, a
dependency only discoverable mid-transaction. This single primitive is
why Sodium re-ranks nodes and rebuilds its queue during a transaction.

Things created at an instant exist from that instant inclusive. A hold
keeps occurrences with `t >= t0`, `Value` fires at t0 with the
post-t0 value, and `Execute` lets an occurrence at t build graph at t.
A node built inside a `construct` closure must be able to read
occurrences already computed in this transaction.

Time is a list of integers. `Split` produces children `t ++ [n]`,
which run after t and before t's successor, depth first, and two
splits in the same t share child indices. That is the complete
specification of the post-transaction queue.

And the Haskell knot-tying for accumulators works only because an
occurrence's time is known before its value. Operationally: every
cycle must pass through a hold, an accumulator or a split. A
stream-only cycle has no meaning, and the engine refuses it. The Java
implementation does not; its rank code terminates on a cycle and
carries on with inconsistent ranks.

## The Transaction

```
begin      sends write into input slots for t
mark       depth-first walk over dependents from the fired inputs;
           its reverse post-order is a topological order of exactly
           the affected region; the on-stack flag turns a stream-only
           cycle into a build-time panic
evaluate   a flat loop over that order; each node reads its inputs'
           slots; memoized pull is the fallback for two dynamic cases
           only: switch_cell reading a newly selected inner at the
           switch instant, and nodes created during t
commit     holds move their slot into current; accumulate_mut runs
           its function; switches relink dependents; version counters
           bump
dispatch   listeners run from the finished slots, in the evaluation
           order of their streams, ties by registration order
children   t ++ [0], t ++ [1], ... each a full transaction, depth
           first, all inside send before it returns
```

One pass yields the order, so evaluation has no recursion, no priority
queue, no maintained ranks, and no memoization checks on the fast
path. Cost is linear in the affected region with small constants,
which is what all three workload shapes want. For UI the region is
small. For a frame simulation the region is most of the graph, and a
heap would have added a log factor there. For shallow high-rate
events the fixed cost is a counter bump and two reused vectors.
Slots are stamped with the transaction id, so nothing needs clearing
between transactions, and a linear consumer takes its value out of
the slot, so nothing lingers. The build closure runs as transaction
zero, which is how `steps_with_current` created at build fires at
zero.

We considered rank-ordered push, Sodium's design, and pure memoized
pull. Ranks must exceed all dynamically reachable inners for a switch
node, which is unknowable in advance and is exactly what forces Sodium
to re-rank and rebuild its queue mid-transaction. Pull handles a
dynamic dependency by following the pointer it just read, and it
matches the semantics' `occs` clauses almost line for line, but it
pays a stamp check per read and recurses as deep as the graph. It
survives only as the fallback for the two dynamic cases, where the
recursion is bounded by the nesting depth of switches.

## Listeners After Commit

Listeners have no graph access ([RFD 2](./rfd-0002-strong-io-separation.md)), so whether they run before or
after commit is unobservable except through panics. After commit, a
panicking listener leaves a consistent graph, and dispatch is a tight
loop over a collected list. Sodium delivers during the transaction so
that a listener may sample the pre-instant value; we removed sampling
from listeners instead. Cell listeners receive a reference to the
committed value, which is the post-instant value, matching the
semantics' `Value`.

## Misuse

Construction errors panic. A stream-only cycle, a second consumer of a
cell holding linear streams, `steps` on in-place state, a loop
declared and never closed, a stale or foreign token in graph code, and
a double send to a non-coalescing input are all deterministic and are
found the first time the code runs.

I/O operations that can fail have a `try_` sibling returning a
`Result`. Each family of operations with the same failure modes has
its own error enum, and no enum carries a variant that one of its
operations cannot return:

| Operations | Failure modes |
|---|---|
| `Graph::try_send` | `Stale`, `ForeignGraph`, `DoubleSend`, `Poisoned` |
| `Transaction::try_send` | `Stale`, `ForeignGraph`, `DoubleSend`; poisoning is checked once, when the transaction is opened |
| `Graph::try_transaction`, `try_collect_garbage`, `try_pump`, `try_remote` | `Poisoned` |
| `Graph::try_listen`, `try_listen_cell`, `try_pin`, `try_sample` | `Stale`, `ForeignGraph`, `Poisoned` |
| `Remote::try_send` | `ForeignGraph`, `InsideTransaction` |
| `Remote::try_transaction` | `InsideTransaction` |

The panicking variants panic on misuse in both build modes, with one
class excepted. An operation on a collected node whose effect is
unobservable by the semantics, meaning sending to a collected input,
listening to a collected stream, or pinning a collected node, is a
debug-mode panic and a release-mode no-op in the panicking variant,
following the integer-overflow precedent, and is counted on the graph
so a release build can report that it is dropping sends. A remote send
whose input was collected before the driver pumps is discovered at
`pump` and follows the same rule. Sampling a collected cell must
return something, so `sample` panics and `try_sample` returns `Err`. A
double send is a violation with an observable outcome either way, so
it is an error in both modes; last-wins in release would mean
production behaves differently from every test that ever ran. A
`Remote::send` from graph code is in the same class ([RFD 6](./rfd-0006-io-edge.md)).

## Panics

Any panic that escapes `send` poisons the graph, and every later call
fails with `Poisoned`. A user function panicking during evaluation or
commit leaves the graph mid-transaction. A listener panicking during
dispatch leaves the graph committed but with the rest of that
transaction's listeners unrun and its child transactions still queued,
so the semantic timeline is incomplete. One rule covers both, at one
flag check per entry. A user who wants a listener to survive its own
panic wraps it in `catch_unwind`, where the consequence is visible.
Rollback needs an undo log for a case that is a bug by definition, and
leaving the state undefined is how you get a wrong answer an hour
later.
