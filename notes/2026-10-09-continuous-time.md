# 2026-10-09 — Continuous time comes back, through latched inputs

Status: note, not a decision. It reverses decision 2 of the literature
review briefing ("Discrete time, no continuous-time module") and the
matching line under "Out of scope" in `2026-09-21-design-requirements.md`.
It keeps the `onStart` cut from that same list, for a different reason
than the one it was cut for. Both go to the v0.1 RFD discussion.

## Why decision 2 goes

Decision 2 came out of the first design conversation, before Bough was
Bough. I took the suggestion because I didn't understand the question,
not because I'd reasoned about it. Nothing has depended on it since, so
now is the cheap time to undo it.

The case for keeping continuous time doesn't rest on Bough's main domain.
Event-driven GUI and business logic barely notice it. It rests on Bevy,
where animation and physics values are things I'd want in the graph, and
on Bough being a general-purpose engine. I won't rule out a use case
without a measured cost, and there isn't one. The machinery it needs is
already in the spike (below).

## What continuous time buys, and what it doesn't

Elliott's argument is the vector-graphics one (push-pull, p. 1; the
Sodium book, ch. 9 §9.1). A program over continuous time has no sample
rate in its meaning. Time transforms compose exactly, the sample rate is
the consumer's choice, and approximations converge as the rate goes up.
A discrete program bakes its step size into what it means. That's the
class of bug where a game behaves differently at 30 and 144 fps.

It fixes the specification, not the numerics. An integral of a behaviour
still gets computed by stepping, and still depends on the step unless
it's done analytically. What changes is that the step belongs to the
consumer: a Bevy adapter picking the fixed timestep, not the program.

## What Sodium actually does

Sodium has no continuous time in its core. Two things stand in for it:

- **A law.** "To protect the idea of a continuously varying cell, a true
  FRP system must ensure that changes in a cell's value aren't
  observable" (ch. 8 §8.4). FRPNow says why that's enough: there's "no
  way to distinguish, through observation, a continuously changing
  behavior from a discretely changing behavior" (van der Ploeg, practical
  principled FRP, p. 3). Hide the steps and a continuous cell can sit
  behind the same type as a stepwise one.
- **A library pattern.** "The mechanism of continuous time is to update a
  cell representing time before passing external events into the FRP
  system" (ch. 9 §9.5). It runs on `Transaction.onStart`, whose "main use
  case is the implementation of a time/alarm system" (App. A).

The law is advice in Sodium, not a rule: `updates` and `value` exist and
the docs warn against them. Bough's `steps`, `listen_steps` and
`listen_cell` are the same advice in the same place, so they're no worse.
The difference I want is that the law becomes a type.

## `Behavior`, a cell kind without steps

A new token type, `Behavior<A>`, meaning a function of time. It can only
be observed by sampling: `snapshot`, `gate` and `sample` in graph code,
and a sample call from I/O code. It has no `steps`, no `listen_steps` and
no `listen_cell`. That last one matters as much as the first two:
`listen_cell` is Sodium's `value` and fires on every step, which on a
time-varying value is every instant, and that exposes the sample rate.

The rest follows from that:

- Every `Cell` is a `Behavior`. Lifting a `Cell` and a `Behavior`
  together gives a `Behavior`. Back to a `Cell` only through a stream:
  snapshot, then `hold`.
- A `Behavior` can't go into `switch_cell`, since the output steps
  whenever its inner does. It needs its own `switch_behavior`.
- Integrals and derivatives stay out of v0.1.

The spike already has both halves. `State<A>` is a cell kind with no
`steps`, so a kind without steps isn't new. Read-through cells
([RFD 4](../src/rfd-0004-value-model.md), "Cells") compute on read,
memoized until an input steps, and not at all if nobody reads. That's
push-pull's lazy evaluation, which is what a time-varying value needs.

One thing RFD 4 rejected may be right for `Behavior`. RFD 4 puts
read-through cells in the dependents graph, so marking reaches them,
because `listen_cell` needs a step to fire on. Its first draft kept them
outside and compared version counters on read. A `Behavior` has no
listeners, so that reason doesn't apply. Keeping behaviours out of the
marking walk would mean a time-driven region costs nothing on an instant
where nobody samples it. I haven't measured whether that matters.

## Latched inputs instead of `onStart`

The Oort bot already ran into this without naming it. Sending own-ship
state and the scan in one transaction meant "every snapshot of own-ship
state saw the tick before" (`2026-09-26-oort-fighter-first-findings.md`),
and the fix was to split them into two transactions. My first thought was
to reverse the `onStart` cut. I don't think that's the fix.

In Bough every transaction starts in host code, so anything `onStart`
could do, the host can already do on the line before `pump`. The Oort bot
did exactly that, and it still felt like a hack. The hack is that
own-ship state went in as an **event**, so it needed its own instant:
listeners fire, the instant counter moves, one game tick becomes two
Bough instants. `onStart` would keep that shape, because Sodium's hook
runs its own transaction before yours. It would only hide the extra
instant.

What was missing is a write that isn't an event: an **input
`Behavior`** whose `set` starts no instant and is latched, so it becomes
the value before the next instant. The pump takes a timestamp,
non-decreasing (ch. 9 §9.4), and time is just the built-in input
`Behavior`. Child instants share their parent's time, which is the
superdense reading of `T = [Int]` from the literature synthesis. An
instant's inputs are then its time, its latched values and its event,
so it stays deterministic and the oracle still applies. `onStart` would
have cost a hidden extra transaction on every pump (against RFD 7's one
cause per transaction), a reentrancy rule, and a question about child
instants. None of those come up.

The rule that goes with it: latched inputs are for things that make sense
sampled, such as positions, time and physics state. Things that happen
stay events. A sampled input can't carry a discontinuity between samples
(Lee, operational semantics of hybrid systems, p. 10); a press and
release inside one frame would vanish from a latched boolean. The Oort
split already follows this: own-ship state was sampled, the scan was an
event.

### Lineage

I worried that an idea this obvious with no lineage meant a problem
neither of us had seen. It has lineage, just not in Sodium:

- Yampa's `reactimate` takes "the next input value along with the amount
  of time elapsed … since the previous sample" on every step (Perez and
  Nilsson, testing and debugging FRP, p. 6; Nilsson et al., FRP
  continued, p. 11). That's both halves of the proposal as one primitive.
- Lustre and the other synchronous languages give every input a value on
  every tick (Halbwachs et al.; Caspi and Pouzet).
- Fran has `mousePos` as a primitive input behaviour.
- FRPNow builds mouse position from async events and `switch` (p. 4),
  the Oort workaround done inside the library.

My reading of why Sodium doesn't have it is threads. Any Sodium thread
can start a transaction, so "which transaction does a latched write land
in" depends on a race, and making every input an event avoids that
question. Decision 4 (single-threaded, the host owns the pump, handles
queue for the next pump) answers it: the next pump. That's an argument,
not a proof.

## The argument for what a sample means

The open question was what `snapshot` of a `Behavior` means at instant
`t`, given that every cell read happens before the instant. The oracle
can't settle it: it's Sodium's App. E, unchanged, and has no `Behavior`,
no latched input and no time, so it could only echo whatever encoding it
was given. It comes down to a short argument instead.

- A latched value is defined as the value for instant `t`, so `snapshot`
  reads it at `t`. Time is continuous, so time just before `t` is `t`:
  `snapshot time e` gives the current time, not the last frame's.
- Discrete cells that step at `t` still read as before the instant, as
  now. A sample of `lift f b c` at `t` is `f(B(t), c before t)`. That's
  the left-limit reading, with each input piecewise constant between
  samples, as in Yampa.
- It agrees with the Oort workaround. Encode each pump as a latch
  transaction followed by an event transaction. If nothing observes the
  latch except by sampling, the latch transaction steps nothing else, so
  every other cell's value before the event transaction is what it was
  before the latch. The two encodings agree on everything except instant
  numbering.

The precondition, "observed only by sampling", is what `Behavior`'s type
rules have to guarantee. That's why `switch_cell` and `hold` of a
behaviour's steps are on the list above: either one would break the
argument.

## Proposed: a property test for the claim the RFD would make

Not built. The claim the RFD would make is: *a transaction whose only
sends go to inputs read through pre-instant reads is invisible apart from
instant numbering.* The oracle can test that one, since it's a claim
about App. E.

- Generate programs as now, plus latch-only inputs connected only through
  `hold` into `snapshot`, `sample` and `gate`. Nothing may observe the
  latch's steps.
- Encode each schedule twice. The workaround encoding gives pump `k` two
  transactions, the latch sends and then the event sends. The latched
  encoding gives it one, and puts pump `k`'s latch sends in pump
  `k - 1`'s transaction, beside its events. A read before the instant at
  `k` sees them, and one at `k - 1` doesn't, which is what latching
  means, with no extra instant. Pump 1's latch values are the holds'
  initial values. Compare the observed nodes after renumbering the
  workaround's instants.
- What it could catch: a creation-time cut that sees the extra instant.
  Constructs created at the event transaction, `split` and `defer` child
  instants, and switches are where to look, since that's where the
  F89 family lives.

I don't expect it to fail. It belongs after the RFD fixes `Behavior`'s
rules, because those rules are what it tests, and the generator work is
real (`generate.rs` is about 5,000 lines).

## How I/O code sees a `Behavior`

This is where Bough feels the cost. Handles don't read: `Io` and
`RemoteIo` have no `sample`, and I/O code observes a cell by listening,
with `listen_cell` or `listen_cell_once`
([RFD 2](../src/rfd-0002-strong-io-separation.md)). RFD 2 turned down an
`Io` that reads because "read, change, send loses an update when two
clicks land between pumps." Only code that owns the `Runtime` samples.
Most runtime integrations give most code a handle, not the runtime, and
`Behavior` takes away the listener too. On the spike as it stands, a
handle has no way at all to see a `Behavior`.

The fix doesn't need a read path: I/O code listens to a snapshot. Graph
code writes `frame.snapshot(b)`, and a handle listens to that stream like
any other. That's the right FRP shape anyway. The observer picks the
sampling rate by picking the event, which is Elliott's "the renderer
decides how often to look." It keeps the law, because the stream fires on
`frame`, not on `b`'s steps, so nothing about how `b` was built shows.
By the argument above the sample is current: latched inputs and time read
as of this pump, and the listener runs after that pump's commit, not a
pump later. RFD 2's no-read rule stays as it is.

The open question is where `frame` comes from:

- **The user sends one.** The Bevy adapter sends a frame event each tick.
  No new primitive, but every app has to wire it up, and wiring it up
  wrong is the Oort bug again.
- **A built-in per-pump stream**, `runtime.pumps()` or similar, firing
  once per pump with its time. Then `pumps().snapshot(b)` is the usual way
  to observe a `Behavior` from I/O. That changes the pump's contract: a
  pump with nothing queued but a new timestamp has to become an instant
  whenever something depends on `pumps()`.

So the cost lands on the pump contract and on the docs, not on the
handles. How I/O code sees a `Behavior` needs a documented pattern, and
probably a built-in stream.

## For the v0.1 discussion

- Reverse decision 2, and strike continuous time from the out-of-scope
  list.
- `Behavior<A>`: the observation surface, the conversions, and the
  `switch_cell` and `hold` exclusions.
- Latched input behaviours, and a pump that takes a timestamp. Keep the
  `onStart` cut, with this note as its reason.
- How I/O code observes a `Behavior`: a user-sent frame event or a
  built-in per-pump stream, and whether an empty pump with a new
  timestamp is an instant.
- Whether behaviours stay out of the marking walk.
- Whether `steps`, `listen_steps` and `listen_cell` move into an
  `operational` module, as the literature synthesis leans. With
  `Behavior` doing the protecting, that's about how the API reads, not
  what it means.
- The property test above, once the rules exist.
