# 2026-10-09 — Continuous time comes back, through latched inputs

Status: note, not a decision. It reverses decision 2 of the literature
review briefing
([`frp-literature-review-prompts/reading/briefing.md`](../research/frp-literature-review-prompts/reading/briefing.md)),
"Discrete time, no continuous-time module", and the matching line under
"Out of scope" in `2026-09-21-design-requirements.md`. It keeps the
`onStart` cut from that same list, for a different reason than the one
it was cut for. Both go to the v0.1 RFD discussion.

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
A discrete program bakes its step size into what it means.

It fixes the specification, not the numerics. An integral of a behaviour
still gets computed by stepping, and still depends on the step unless
it's done analytically. The game that behaves differently at 30 and
144 fps is mostly an integration-step bug, and a fixed timestep is what
fixes it. What continuous time changes is who owns the step: the
consumer, such as a Bevy adapter picking the fixed timestep, not the
program.

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
the docs warn against them. Bough's `steps`, `steps_with_current`,
`listen_steps` and `listen_cell` are the same advice in the same place,
so they're no worse. The difference I want is that the law becomes a
type.

## `Behavior`, a cell kind without steps

A new token type, `Behavior<A>`, meaning a function of time. It can only
be observed by sampling: `snapshot`, `gate` and `sample` in graph code,
and a sample call from I/O code. It has no stream views, `steps` or
`steps_with_current`, and no listeners, `listen_steps` or `listen_cell`.
The listeners matter as much as the views: `listen_cell` is Sodium's
`value` from I/O code and fires on every step, which on a time-varying
value is every instant, and that exposes the sample rate.

The rest follows from that:

- Every `Cell` is a `Behavior`. Lifting a `Cell` and a `Behavior`
  together gives a `Behavior`. Back to a `Cell` only through a stream:
  snapshot, then `hold`.
- A `Behavior` can't go into `switch_cell`, since the output steps
  whenever its inner does. It needs its own `switch_behavior`.
- Integrals and derivatives stay out of v0.1.

The spike already has the pieces. Its cell kinds combine through a
`CellKind::Join` lattice, which is the shape of "a lift with a
`Behavior` in it is a `Behavior`". `State<A>` is the nearest precedent
for a kind with fewer powers: it has no stream views. It isn't a full
precedent, since it can still be listened to
([RFD 4](../src/rfd-0004-value-model.md)). Read-through cells (RFD 4,
"Cells") compute on read, memoized until an input steps, and not at all
if nobody reads. That's push-pull's lazy evaluation, which is what a
time-varying value needs.

One thing RFD 4 rejected may be right for `Behavior`. RFD 4 puts
read-through cells in the dependents graph, so marking reaches them,
because `listen_cell` needs a step to fire on. Its first draft kept them
outside and compared version counters on read. A `Behavior` has no
listeners, so that reason doesn't apply. Keeping behaviours out of the
marking walk would mean a time-driven region costs nothing on an instant
where nobody samples it. The cost moves to reads: marking is also what
clears memos at commit, so without it every read checks versions up its
inputs. That's the pure pull decision 5 rejected ("a stamp check per
read, recursion as deep as the graph"), limited to behaviours. I haven't
measured which is cheaper.

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
`Behavior`. Child instants share their parent's time. That's how
superdense time reads `T = [Int]`: a child instant is a microstep,
ordered but not timed (the literature review,
[`2026-09-28-frp-literature-review.md`](../research/2026-09-28-frp-literature-review.md),
"`T = [Int]` has neighbours"). An instant's inputs are then its time, its
latched values and its event, so it stays deterministic and the oracle
still applies. `onStart` would have cost a hidden extra transaction on
every pump, a reentrancy rule, and a question about child instants. None
of those come up.

The rule that goes with it: latched inputs are for things that make sense
sampled, such as positions, time and physics state. Things that happen
stay events. A press and release inside one frame would vanish from a
latched boolean, and samples can't even represent a jump unambiguously
(Lee, operational semantics of hybrid systems, §4). The Oort split
already follows this: own-ship state was sampled, the scan was an event.

### Lineage

I worried that an idea this obvious with no lineage meant a problem
neither of us had seen. It has lineage, just not in Sodium:

- Yampa's `reactimate` takes "the next input value along with the amount
  of time elapsed … since the previous sample" on every step (Perez and
  Nilsson, testing and debugging FRP, p. 6; Nilsson et al., FRP
  continued, p. 11). That's both halves of the proposal as one primitive.
- In Lustre, an input is a flow with a value on each tick of its clock
  (Halbwachs et al.). Events are boolean flows there, which is the
  encoding the rule above warns about, so Lustre is lineage for the
  mechanism, not for the rule.
- Fran has `mousePos` as a primitive input behaviour, as FRPNow's
  `snapshot mousePos easter` example shows (van der Ploeg, p. 1).
- FRPNow builds mouse position from async events and `switch` (p. 5),
  the Oort workaround done inside the library.

My reading of why Sodium doesn't have it is threads. Any Sodium thread
can start a transaction, so "which transaction does a latched write land
in" depends on a race, and making every input an event avoids that
question. Bough is single-threaded: the host owns the pump, and handles
queue every call for the next pump (decision 4;
[RFD 6](../src/rfd-0006-io-edge.md)). That doesn't remove the race for a
`RemoteIo` write, which can still land on either side of a pump. It
makes the answer deterministic once the write is stamped. That's an
argument, not a proof.

## The argument for what a sample means

The open question was what `snapshot` of a `Behavior` means at instant
`t`, given that every cell read happens before the instant. The oracle
can't settle it. It's Sodium's App. E with two patches (F6 and F7), and
has no `Behavior`, no latched input and no time, so it could only echo
whatever encoding it was given. It comes down to a short argument
instead.

- A latched `set` lands between instants, so at `t` the value just
  before `t` is already the new one, and `snapshot` reads it. Time is
  continuous, so time just before `t` is `t`: `snapshot time e` gives the
  current time, not the last frame's.
- Discrete cells that step at `t` still read their value from before the
  instant, the old one, as now. A sample of `lift f b c` at `t` is
  `f(B(t), c before t)`.
- It agrees with the Oort workaround. Encode each pump as a latch
  transaction followed by an event transaction. If nothing observes the
  latch except by sampling, the latch transaction steps nothing else, so
  every other cell's value before the event transaction is what it was
  before the latch. The two encodings agree on everything except instant
  numbering.

The precondition, "observed only by sampling", is what `Behavior`'s type
rules have to guarantee. That's why a `Behavior` has no stream views and
no listeners, why a lift with one in it is a `Behavior`, why the only way
back to a `Cell` is `hold` of a sampled stream, and why `switch_cell`
can't take one. Each of those, broken, would break the argument.

## Proposed: a property test for the claim the RFD would make

Not built. The claim the RFD would make is: *a transaction whose only
sends go to inputs read through pre-instant reads is invisible apart from
instant numbering.* The oracle can test that one, since it's a claim
about App. E.

- Generate programs as now, plus latch-only inputs connected only through
  `hold` into `snapshot`, `sample` and `gate`, and through read-through
  cells over those holds whose only consumers sample them. Nothing may
  observe the latch's steps.
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
  creation-time findings live, F89 among them: a `split` built at a
  child instant replays events from before it
  ([`2026-09-24-engine-feasibility-spike.md`](../research/2026-09-24-engine-feasibility-spike.md#f89)).

I don't expect it to fail. It belongs after the RFD fixes `Behavior`'s
rules, because those rules are what it tests, and the generator work is
real: the `bough-oracle` crate's program generator is about 5,000
lines.

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
sampling rate by picking the event, which is Elliott's "discretization
introduced automatically during rendering" (push-pull, p. 1). It keeps
the law, because the stream fires on `frame`, not on `b`'s steps, so
nothing about how `b` was built shows. By the argument above the sample
is current: latched inputs and time read as of this pump, and the
listener runs after that pump's commit, not a pump later. RFD 2's no-read
rule stays as it is.

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
- `Behavior<A>`: no stream views and no listeners, the one conversion
  back to `Cell`, and the `switch_cell` exclusion.
- Latched input behaviours, and a pump that takes a timestamp. Keep the
  `onStart` cut, with this note as its reason.
- How I/O code observes a `Behavior`: a user-sent frame event or a
  built-in per-pump stream, and whether an empty pump with a new
  timestamp is an instant.
- Whether behaviours stay out of the marking walk.
- Whether `steps`, `steps_with_current`, `listen_steps` and `listen_cell`
  move into an `operational` module, as the literature review leans. With
  `Behavior` doing the protecting, that's about how the API reads, not
  what it means.
- The property test above, once the rules exist.
