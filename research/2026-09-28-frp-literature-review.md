# What the FRP literature says to Bough

_2026-09-28. A research note for the Bough design, from the literature
review the [handoff](./handoff-2026-09-27-frp-literature-review.md)
planned. It answers two questions for Zefira: what the literature knows
about Bough's open questions, and whether anything in it contradicts a
decision Bough has settled. The must-read below is the answer. The nine
sections after it are the evidence, one per dimension, and they end in
questions to grill, never in RFD text. Nothing here has authority over
the RFDs._

_The sources are in the private `literature` repository, one record per
source with reading notes by page, cited here by stem. `p. N` is the
stored PDF's page index, counted from 1, never the printed page. The
Sodium book is cited by chapter and section. The probes are in
`experiments`, published as `bough-frp/experiments` and cited as
`experiments@COMMIT`, and every number this note establishes carries the
provenance line and command of the result file it comes from, in the
section that quotes it. A paper's number is that paper's claim, marked
"not reproduced". Bough's own numbers are cited to the research note that
measured them._

_Verification, 2026-09-29. Fresh verifiers, given the note,
`literature`, `experiments` and none of the drafting, checked it in
seven slices. They checked about 1,600 claims: each against its page in
the stored PDF, the crate clone at its pinned commit, the Sodium book or
Bough's own notes, and each number against its result file. They found
99 errors: 27 overstated, 14 misread, 12 unsupported, 11 wrong pages, 11
wrong numbers, 10 metadata (8 of them missing years), 9 internal, 3
misattributed and 2 missing provenance lines. Each was fixed and
re-checked by the verifier that found it; the fixes brought in 5 more,
fixed the same way. Two fixes changed a must-read finding, with Zefira's
approval: RFD 6 states no overhead reason, and not every bounded system
compiles a static graph. The 66 result files that don't need wall-clock
were re-run, each at the commit it cites. 62 reproduce, the instruction
counts within 1%. The four `patch-cell-crossover` instruction files
don't, in their `map_*` benchmarks only: the fixture seeds std's
`HashMap` per process, so those counts move by up to 11% from run to
run. The note quotes none of them. The two futex tables depend on
scheduling and tell the same story. Every wall-clock bench was re-run on
the idle machine on a second day, from the same code. For 92 of 168
numbers the re-run's interval overlaps the first run's; the intervals
measure only the noise within one run. Most of the rest move by 1% to
5%, the machine's drift between days, so the ratios here are good to a
few percent. The cycle and adversarial rows and the single-unit benches
move more, up to 45%, and a few other numbers 5% to 6%. Every wall-clock
claim holds in both runs, as worded now; six were reworded, and
single-run tails are marked as such. Compile times and the timed binary
reproduce within about 4%._

## The must-read

Ninety-nine sources were read from stored copies, six crates at
source. Thirteen probes and their follow-ups ran, timed on the idle
machine. Nothing rests on an abstract alone; a leaning resting on a
paper's unreproduced number says so.

Six findings contradict what Bough has settled: four reasons the RFDs
state, the no-std handoff's overhead reason, and RFD 3's collection
trigger. No decision's core is shown wrong. RFDs 3 and 5 gate the build
and come first.

**RFD 5.**

- *The reasons for rejecting rank-ordered push don't hold on their own.*
  Incremental-style heights, raised when a link would point downhill,
  re-rank cheaply, and a bucket queue has no log factor. Heights cost
  about a quarter more when a whole region fires, break even near 30%
  quiet, and win up to eighteenfold on mostly quiet regions; the raise
  finds cycles. Leaning: keep the flat loop, reword the rejection as a
  trade, and measure a real program's quiet share.
- *The per-move walk stays.* A DFS grey mark finds a cycle only when an
  input next reaches it. On a UI-shaped graph a move walks about 535
  nodes. An order-maintenance list that places new nodes before the
  switch costs 0.02 to 0.6 of the walk there, and more than the walk on
  adversarial shapes. Leaning: keep the walk, and Brent's guard.
- [F22](./2026-09-24-engine-feasibility-spike.md#f22) is liveness, outside the loop rule.

**RFD 3.**

- *"An undeclared capture cannot be made a compile error" doesn't hold.*
  A lifetime brand on tokens makes [F62](./2026-09-24-engine-feasibility-spike.md#f62) a compile error on stable, soundly,
  with no `unsafe`, and tokens stay usable as data. It costs a lifetime
  on every token-holding type, I/O inside callbacks, a copy per read of a
  token-bearing collection (1.9 times an event at a thousand tokens)
  unless borrowed views replace `&A`, and a stash route only an `unsafe`
  seal narrows. Leaning: keep `depends` and reword the reason. But a
  brand touches every signature, so it's now or never.
- *The collection trigger needs a work term.* Beside a large live graph
  RFD 3's trigger lets garbage cost about ten times what a trigger paced
  against each input's region growth does, and triples the worst pause.
  The work term costs nothing measurable on a clean unit. No region term
  sees garbage a dropped guard releases, and RFD 3's release term never
  fired. Leaning: add the work term; find a release term.
- *Counting with a backup trace sees cycles.* RFD 3's other reason,
  `Copy` tokens, carries the rejection.
- Modal types catch [F62](./2026-09-24-engine-feasibility-spike.md#f62), not [F63](./2026-09-24-engine-feasibility-spike.md#f63): explicit leaks stay legal. Every
  GC-based FRP has [F66](./2026-09-24-engine-feasibility-spike.md#f66). Safe `Trace` is sound for checked indices.
- A fixed-budget incremental mark cuts the worst pause eightfold for 16%
  more time.

**RFD 1.**

- *[F89](./2026-09-24-engine-feasibility-spike.md#f89) is a semantics change.* The text states its creation rule for
  four primitives, not `Split`. Forgetfulness is the principled reason
  for the cut (FRPNow's Lemmas 1 and 2), and it covers [F6](./2026-09-24-engine-feasibility-spike.md#f6) too. The probe
  finds the text leaking at every [F89](./2026-09-24-engine-feasibility-spike.md#f89)-shaped node and the cut at none; a
  creation time on state-holders and time-movers alone suffices.
  Leaning: restate the exceptions as "the text is leaky; Bough is
  forgetful".
- The oracle reaches the unique fixed point of a guarded system, by
  Banach's theorem, not a least fixpoint. `[Int]` isn't well ordered, so
  arguments range over the instants a run creates, with non-Zeno as the
  side condition.
- `steps` is sound in App. E's model, where a cell is a step sequence.
  Leaning: an `operational` module, not a feature flag.
- The oracle's comparison needs no child indices. Leaning: put
  shrinking, labelled shapes and long engine-only traces in the policy.

**RFD 2.** Acyclicity is Esterel v4's, Lustre's and Keating and Gale's
rule, sound and knowingly incomplete. The census of refused loops finds
nothing a program would want that a switch can't write. [F3](./2026-09-24-engine-feasibility-spike.md#f3) needs `steps`,
which ties questions 3 and 10. A one-bit decoupledness mark refuses [F3](./2026-09-24-engine-feasibility-spike.md#f3)
at compile time for 2% to 16% more compile time, but it and rows accept
a loop smuggled through a switch. Only a `Switched` mark on switch outputs
catches that, at the price of nested switches, so the run-time check
stays. Leaning: keep plain acyclicity; hold the mark.

**RFD 4.** Streams are affine, "at most one consumer", not linear.
Erasing a fused chain at its materializer builds [F36](./2026-09-24-engine-feasibility-spike.md#f36)'s shapes in about
two-fifths of the time for 2% an event. For cells of collections, a
patch-carrying cell wins from small sizes, its data structure matters
most, and Z-set composition fails when two sources upsert one key.
Leaning: erase by default; a patch cell over Cai's change structure in
core, with counted B-trees and fused upserts in a library. The erasure
leaning rests on a generated program.

**RFD 6.** *No source supports "threading costs overhead",* the no-std
handoff's reason; RFD 6's own, that the host owns the schedule, stands.
An uncontended `Mutex` costs 1% to 5% a unit; RFD 6's queue, 11% to 15%.
Contended, the lock loses more. Drechsler et al.'s 20% to 25% for
concurrent propagation is not reproduced, and their negligible
uncontended lock is asserted, not measured. The Sodium book argues *for*
threads. What the sources support: no listeners under a lock, one order
of units the host can see. Leaning: keep the single thread; write its
reasons down.

**RFD 7.** Every bounded system compiles a static graph or bounds
creation up front; the embedded line moved from merging simultaneous
events to ordering them; nobody folds a burst with a user's fold.
Leanings: a slot high-water mark, a child-instant depth cap, fixed queue
capacities with a full-queue `IoError`.

**Unclear, for a recheck.** The height queue's break-even between 1% and
30% quiet is interpolated. The incremental mark's single-unit benches
disagree with its whole-run bench, and the `owned` rebrand's wall-clock
with its instruction counts. Neither changes a leaning. The lock's
mechanism rests on one timed binary.

**What to grill first.** RFD 3's brand, which must precede the
signatures, and its trigger. Then RFD 5's ranks, once a real program's
quiet share is known.

## Semantics and time (RFD 1)

### What the literature says

**Creation time is an old argument, and the literature has a name for
Bough's side of it.** FRP has argued about when a thing starts since the
first higher-order systems. Three lines give the same answer Bough gives:
a thing built at `t` sees nothing from before `t`.

- *Forgetfulness.* FRPNow proves that `whenJust†`, which takes its start
  time from an event argument that may lie in the past, is "inherently
  leaky", and that `whenJust`, which takes it from the behaviour monad's
  "now", is forgetful (vanderploeg-practical-principled-frp p. 5, Lemmas 1
  and 2; the reason is on p. 4). The tool
  is equality up to time observation, a Kripke logical relation over a
  totally ordered time with a least element (pp. 3–5). It names
  Elliott's event join, `accumE` and `accumR` as not forgetful (p. 12,
  fn. 7).
- *Start times.* If a switched-in signal that depends on the triggering
  event started at system start, the implementation would have to
  remember all past input and catch up, which is a space leak and a time
  leak. So most first-class-signal FRP variants start it at the moment
  of switching (sculthorpe-keeping-calm-in-the-face-of-change p. 7).
  CFRP's `runningInEB` keeps an event running across a switch and drops
  its occurrences from before switch-in: "only events that occur after
  it is switched in should be observable" (p. 12).
- *Local time.* A switched-in residual starts at local time zero and
  observes only input after the switch
  (sculthorpe-safe-functional-reactive-programming-through-dependent-types
  p. 4).

All three include the creation instant itself. `runningInEB` drops only
occurrences before switch-in (sculthorpe-keeping-calm-in-the-face-of-change
p. 12), and FRPNow's `snapshot` samples at `max t n`
(vanderploeg-practical-principled-frp p. 4). That matches Bough's "exists
from its creation instant, inclusive".

The counter-position is Elliott's. His `joinE` moves an inner event's
earlier occurrences forward to the time the inner was generated, instead
of dropping them (elliott-push-pull-functional-reactive-programming
p. 3). That is the text's [F89](./2026-09-24-engine-feasibility-spike.md#f89) behaviour in miniature, and FRPNow is the
paper that calls it leaky. Time order doesn't settle the question. The
text's replay moves `[1]`'s event to `[1,1]` and `[1,2]`, after the split
exists, so both answers keep time order (murray-naiad-a-timely-dataflow-system
p. 3 states the "never backwards in time" rule both satisfy). What
separates them is forgetfulness.

**The Sodium text states its creation rule for four primitives only.**
App. E says Value, Hold, SwitchC and Sample take the construction time,
and that their outputs "can never be sampled before the time t they were
constructed" (blackheath-functional-reactive-programming, App. E, §E.4).
`Split` is a pure function on streams with no creation time (App. E,
§E.4, §E.5.10), and App. E has no `Defer` at all. Time order is stated as
an invariant of the domains, "for increasing T values" (App. E, §E.4). So
[F6](./2026-09-24-engine-feasibility-spike.md#f6) and [F7](./2026-09-24-engine-feasibility-spike.md#f7) break a rule the text states: their outputs aren't values of
the domain it declares, and [F6](./2026-09-24-engine-feasibility-spike.md#f6) also contradicts SwitchC's own initial
value (App. E, §E.5.15). [F89](./2026-09-24-engine-feasibility-spike.md#f89) breaks none. In the text, a split built at a
child instant has no "before it existed", and its answer is what its
equation says. Bough's cut is Bough extending the creation rule to
`split` and `defer`.

**`T = [Int]` has neighbours, and none is it.** Superdense time uses the
tag set `T × N`, with finitely many values at one time, well ordered by
the index, and a chattering Zeno condition excluded by definition
(lee-operational-semantics-of-hybrid-systems p. 11). Map `[t]` to `(t, 0)`
and `[t, n]` to `(t, n+1)` and the orders agree at depth two. Its reading
of microsteps as "ordered but not timed" (p. 14) is the right reading of
child instants. Naiad nests counters to any depth and compares them
lexicographically within a loop context, but its egress strips the inner
counter and attributes the result to the outer time, and its order across
epochs is partial (murray-naiad-a-timely-dataflow-system p. 3). A Bough
child instant is a later transaction with its own time, in a total order.
Differential dataflow's theory uses product partial orders and says the
lexicographic order is outside it, since it isn't locally finite, and
that the original construction "appears incorrect for T ≠ N"
(abadi-foundations-of-differential-dataflow p. 14). The closest match
for the order itself is Aguado et al.'s process identifiers: sequences
that alternate naturals with the fork labels l and r, partially ordered
by proper prefix first, then lexicographically, with l and r
incomparable. Within one thread's numbers that is Bough's order. A
forked child runs after its fork and before the parent's next step
(aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of
pp. 8–11). Their children are micro-steps inside one tick, though, and
Bough's are whole transactions.

One caveat follows from these and none of them states it. `[Int]` under
"prefix first, then lexicographic" isn't well ordered:
`[1,1] > [1,0,1] > [1,0,0,1] > …` descends forever above `[1]`. Jeffrey's
fixed-point termination needs a well-ordering on closed intervals, which
is "immediate" in discrete time (jeffrey-ltl-types-frp p. 7). So a Bough
argument by induction or fixed point must range over the instants a run
creates, not over the type. That set is finite per transaction exactly
when no `defer` loop chatters, which is [F22](./2026-09-24-engine-feasibility-spike.md#f22), and Lee's non-Zeno condition
is the side condition to state.

**Clock refinement points the other way.** The model nearest to child
instants in the synchronous languages is Gemünde, Brandt and Schneider's
refined clocks: substeps inside an outer step, hidden from outside, on a
static clock tree (gemunde-clock-refinement-in-imperative-synchronous-languages
pp. 5–7). There, a variable declared on the outer clock keeps one value
for the whole outer step, substeps included (pp. 6, 8, 12), and an event
variable resets only at its own clock's step (p. 13). So an outer-step
event stays present through its substeps, which is what the text does
when a split built at `[1,0]` replays `[1]`'s event. Bough's cut follows
instead from treating every stream as living on the finest clock, where
each event is one point of the total order and `[1] < [1,0]`. Clock
refinement has no node creation inside a substep, so it can't settle
[F89](./2026-09-24-engine-feasibility-spike.md#f89) either way. Berry's incarnations come closer. Re-entering a scope
within one reaction makes a fresh incarnation that doesn't see the old
one's events, and a translation that lets the old emission through is
simply wrong (berry-the-constructive-semantics-of-pure-esterel
pp. 133–134, 140–141). That reads like a node built at `t ++ [n]`, but it
is an analogy, not a proof.

**[F1](./2026-09-24-engine-feasibility-spike.md#f1)'s iteration has a clean status, and it isn't "least fixpoint".** A
guarded definition is a contractive map with a unique fixed point, by
Banach's theorem, and iterating from any start converges, with the first
n instants right after n rounds
(krishnaswami-ultrametric-semantics-of-reactive-programs pp. 2–3).
Differential dataflow says the same for a loop whose feedback shifts the
index (abadi-foundations-of-differential-dataflow p. 8), and Jeffrey for
decoupled functions (jeffrey-ltl-types-frp p. 7). The oracle's
"one round per distinct loop time, plus one" is that convergence,
observed. A Kleene least fixpoint is something else: it starts from the
least-informative environment and climbs an information order
(aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of
pp. 22, 35–36). The oracle starts each loop from "a cell that never
steps", a definite history, not "unknown". The two agree on guarded
loops. The oracle's stopping rule, iterate until the steps repeat, is
differential dataflow's "exit on first repetition", which Abadi et al.
say needs partial streams and domain theory and leave open (p. 15). The
hang itself belongs to the text's whole-history `at`: a co-iterative or
state-machine semantics runs a guarded loop one instant at a time with no
fixpoint at all (cuoq-modular-causality-in-a-synchronous-stream-language
pp. 12–13; caspi-synchronous-kahn-networks p. 7).

**`steps` is sound in the text's own model.** The book hides a cell's
steps to protect continuous time: "To protect the idea of a continuously
varying cell, a true FRP system must ensure that changes in a cell's value
aren't observable" (blackheath-functional-reactive-programming, ch. 8,
§8.4). Bough ruled continuous time out. App. E's cell is a step sequence,
`C a = (a, [(T, a)])`, chosen over Elliott's `T → a` because it "makes
Updates and Value possible" (App. E, §E.4). So `steps` is a projection of
the denotation. What it breaks is equality under `at`: two cells with the
same value at every time and different steps become distinguishable,
which by Elliott's own principle is an abstraction leak for a `T → A`
model (elliott-denotational-design-with-type-class-morphisms pp. 15–16).
Keeping Calm agrees that a step signal "changes" only when it takes a new
value, and at its local time zero
(sculthorpe-keeping-calm-in-the-face-of-change pp. 29, 36), which is
`steps_with_current`'s first event. FRPNow's sound alternative is
`change`, the next time the behaviour differs from now, which needs `Eq`
(vanderploeg-practical-principled-frp p. 4). Monadic FRP goes the other
way and builds its whole semantics on emissions
(vanderploeg-monadic-functional-reactive-programming pp. 1, 3). Reflex
keeps changes out of the plain type: a `Behavior` can't be observed for
change, and only a `Dynamic` carries its update event, under a rule that
it steps if and only if the event fires (reflex-reflex-class pp. 2, 27).

**Simultaneity.** Elliott keeps simultaneous occurrences in a merge,
left-biased, as a design choice against merging them
(elliott-push-pull-functional-reactive-programming pp. 3, 12). Sodium
merges them through a function, one event per stream per instant
(blackheath-functional-reactive-programming, ch. 2, §2.6.1). Nothing in
the batch argues Sodium's choice is wrong.

### The Rust prior art

No Rust crate has Bough's child instants. DFIR's tick is a batch, with
an unfinished loop-iteration counter inside it
(hydro@dfir_rs-v0.16.0 `dfir_lang/src/graph/ops/next_iteration.rs`:9–40),
and its `defer_tick` defers to the next top-level tick
(`dfir_lang/src/graph/ops/defer_tick.rs`:6–11).
carboxyl reads cells before the instant, as Sodium does. Its `merge`
takes no combining function: simultaneous firings pass through
separately, and an opt-in `coalesce` combines them in no defined order
(carboxyl@2a80080 `src/signal.rs`:731–746, `src/stream/mod.rs`:307–334).
salsa iterates a cycle from an initial value to a fixed point, capped at
200 rounds, and refuses to combine that with its equality cut-off, with
a comment that the combination's safety hasn't been proved
(salsa@salsa-v0.28.5 `src/cycle.rs`:9–58,
`src/function/backdate.rs`:33–38). That is the oracle's iteration as a
production pattern, with its known hazard.

### What the probe found

`rfd-0001-forgetful-cut` transcribes App. E over `T = [Int]` and runs
three variants: the text; `cut-all`, a creation time on every constructed
primitive; and `cut-stateful`, a cut on state-holders and time-movers
only, the Sodium drafts' criterion. It tests FRPNow's condition locally:
each node built after `[0]` is rebuilt over its arguments with their past
chopped at its creation, and over three junk pasts.

- On 3,000 random programs with two input histories each, the text leaks
  in 859 of 6,000 runs, at 4,632 nodes. Every [F89](./2026-09-24-engine-feasibility-spike.md#f89)-shaped node leaks,
  2,174 of 2,174, and 2,411 of 3,876 [F6](./2026-09-24-engine-feasibility-spike.md#f6)-shaped ones. The other 47 are
  downstream of an out-of-order argument. Neither cut leaks at any node.
- [F7](./2026-09-24-engine-feasibility-spike.md#f7) is out of time order but forgetful. It's a time-order bug, not a
  leak.
- `cut-all` and `cut-stateful` differ at none of the 121,225 nodes they
  share. The 13,588 nodes only `cut-stateful` has are construct bodies
  run for events from before their construct existed, which nothing can
  observe. So RFD 1 can state one rule, and whether `construct` takes the
  cut makes no observable difference when state-holders and time-movers
  do.
- The probe has no loops, so it doesn't reach RFD 5's worry that a loop
  inside a construct closure fails to settle in the oracle.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0001-forgetful-cut at experiments@c982f4f - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0001-forgetful-cut
```

### Settled decisions the evidence contradicts

One stated reason, not the decision. RFD 1 lists [F89](./2026-09-24-engine-feasibility-spike.md#f89) as a place where
"the text breaks its own rules". For [F6](./2026-09-24-engine-feasibility-spike.md#f6) and [F7](./2026-09-24-engine-feasibility-spike.md#f7) it does. For [F89](./2026-09-24-engine-feasibility-spike.md#f89) the text
states no rule that `Split` breaks. Zefira ruled on 2026-09-28 that the
review treats [F89](./2026-09-24-engine-feasibility-spike.md#f89) as a semantics change under RFD 1's own rule for
changing an inherited corner, with forgetfulness as the reason that
holds. The cut itself isn't questioned: FRPNow's Lemma 1 has [F89](./2026-09-24-engine-feasibility-spike.md#f89)'s shape,
and the probe finds the text leaking exactly there.

Otherwise none found. Discrete time, fidelity to the text, GHC as the
oracle and Sodium's merge all hold against the batch.

### The options for Bough

1. Keep RFD 1's wording and list [F89](./2026-09-24-engine-feasibility-spike.md#f89) among the cases where the text
   breaks its rules.
2. Restate the exceptions: the text's semantics is inherently leaky at [F6](./2026-09-24-engine-feasibility-spike.md#f6)
   and [F89](./2026-09-24-engine-feasibility-spike.md#f89), and Bough picks the forgetful one, with FRPNow's lemmas and
   CFRP's `runningInEB` as precedent and Elliott's `delayOccs` as the
   named alternative. [F7](./2026-09-24-engine-feasibility-spike.md#f7) stays a time-order fix. State one rule, a
   creation time on every state-holder and every time-mover.
3. Do 2 and prove the cut, as FRPNow did for one function, for Bough's
   primitives over `T = [Int]`. FRPNow's relation needs only a total
   order with a least element. `T = [Int]` has one only by App. E's
   posit that `[0]` is the smallest value of `T` (§E.4).
4. Type the cut: an era, a start-time parameter on signals
   (jeffrey-ltl-types-frp p. 5), which in Rust might be a lifetime per
   `construct` scope. That overlaps the memory section's brand.

For [F1](./2026-09-24-engine-feasibility-spike.md#f1), describe the iteration as reaching the unique fixed point of a
guarded system, one loop time per round, or restate the oracle's round
to start from "unknown after time 0" so that it is a real least fixpoint
in the prefix order. For `steps`: keep it public, move it into an
`operational` module with the book's rule in its documentation, or put
it behind a feature flag.

### Claude's leaning

Option 2, now. It turns "the text breaks its own rules" into "the text's
semantics is leaky, and Bough chose the forgetful one", which is a
reason with precedent and a probe behind it. Add to RFD 1's statement of
`T` that arguments range over the instants a run creates, with non-Zeno
as the side condition. Leave 3 unless something comes to rely on the cut
formally, and treat 4 as part of the memory question. Describe [F1](./2026-09-24-engine-feasibility-spike.md#f1) as
reaching the unique fixed point of a guarded system, and cite salsa's
cycle iteration beside it. Keep `steps` public in an `operational`
module: in App. E's model it is sound by definition, and a flag buys
little now that RFD 1 has given up equal-step elision.

### Questions to grill

- Will you accept "the text is leaky at [F6](./2026-09-24-engine-feasibility-spike.md#f6) and [F89](./2026-09-24-engine-feasibility-spike.md#f89), and Bough picks the
  forgetful semantics" as RFD 1's reason, in place of "the text breaks
  its own rules"? Does [F89](./2026-09-24-engine-feasibility-spike.md#f89) then need its own RFD, or a reworded policy?
- Is every Bough stream on the finest clock, so that an event at `t` is
  simply absent at `t ++ [n]`? Would you ever want a value to stay
  constant across a transaction's child instants, as Gemünde's outer
  clock does?
- Does a node created at `t` see `t`'s own events, and does that stay
  true at a child instant `t ++ [n]`? The probe found a `defer` built at
  `[k,0]` over a stream that fired at `[k]` puts the replayed event
  exactly at its own creation time.
- Should RFD 1 say that Bough's semantics ranges over the instants a run
  creates, since `[Int]` isn't well ordered?
- Should [F1](./2026-09-24-engine-feasibility-spike.md#f1) be restated as a fault of the text's whole-history `at`
  rather than of loops, and does that change how RFD 1 describes the
  oracle?
- Is Bough's cell a step sequence, so `steps` is sound by definition, or
  a function of time, which makes it a leak? If the first, is equal-step
  elision the only thing `steps` still costs?
- The book never says why `switch_stream` takes the old stream at the
  switch instant while `switch_cell` takes the new cell's step. Reflex's
  `switchHold` makes the same stream choice "to avoid many potential
  cyclic dependency / metastability failures" (reflex-reflex-class
  p. 15). Does Bough want that reason on record?

### Experiments this proposes for Bough

Never run here; each is for the real build to decide on.

- Give the oracle's `construct` the cut, then let loops into construct
  closures in the random programs, and see whether any fail to settle.
  This is the experiment RFD 5 already names, and the probe says the cut
  itself is unobservable without loops.
- Build a co-iterative reference semantics for the loop-free core in
  Haskell beside the text, and compare it with the oracle on programs
  with guarded loops, to see whether the oracle's rounds ever stop early.

### Reading path

- vanderploeg-practical-principled-frp first. Needs reader and writer
  monads; §3.2's Kripke logical relation is the hard part, and the text
  extraction garbles Definition 1, so read p. 4 of the PDF.
- sculthorpe-keeping-calm-in-the-face-of-change for the start-time
  argument, pp. 7, 12 and 29–37. Needs Yampa's arrows.
- blackheath-functional-reactive-programming App. E, §§E.4, E.5.6,
  E.5.10, E.5.15, with Elliott's push-pull §2 for the `B a` against `C a`
  contrast. Its diagrams draw cells one column late, so read the step
  times in the test code.
- elliott-push-pull-functional-reactive-programming §§2–4 for the
  counter-position. Needs Haskell type classes and laziness.
- lee-operational-semantics-of-hybrid-systems §§5, 7 and 8.3 for
  superdense time. Self-contained.
- krishnaswami-ultrametric-semantics-of-reactive-programs for [F1](./2026-09-24-engine-feasibility-spike.md#f1)'s
  fixed point. Needs complete metric spaces and Banach's theorem.
- aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of
  §2 for the identifier order. Needs lattices at Davey and Priestley's
  level.

## Switching and dynamic graphs (RFDs 2, 5)

### What the literature says

**Sodium's switch-instant semantics is the combination Reflex
recommends.** Reflex's default `switchHold` uses only the old event at
the switch instant, because that "avoid[s] many potential cyclic
dependency / metastability failures" and is faster. The prompt variants
exist and are discouraged (reflex-reflex-class p. 15). Its `hold` makes a
sample at the instant the hold updates, a switch instant included, see
the old value (p. 7). Yampa offers both
timings for every switcher, because the delayed one "is sometimes needed
to break cyclic dependencies" (nilsson-functional-reactive-programming-continued
p. 4). FrTime builds a new branch mid-cycle and forwards its value in the
same cycle (cooper-integrating-dataflow-evaluation-into-a-practical-higher-order
pp. 40–41). The Sodium book gives no reason for `switch_stream` taking
the old stream: it exists only as `t <= t1` in SwitchS's definition
(blackheath-functional-reactive-programming, App. E, §E.5.6).

**Switching is where history leaks, and every line fenced it
differently.**

- Elm banned signals of signals. A fold built late must either keep all
  history or give two identically defined signals different values
  (czaplicki-asynchronous-functional-reactive-programming-for-guis p. 4).
  It later dropped signals entirely, for learnability, not for semantics
  or speed (czaplicki-a-farewell-to-frp p. 5).
- Yampa made signals second class to avoid time and space leaks, and
  `pSwitch` hands running signal functions over as frozen continuations
  with their state (nilsson-functional-reactive-programming-continued
  pp. 2, 5). That's a clean model of "deselected but still stateful".
- Patai made stateful streams *generators* of their start time. Sampling
  before the start is an error, new streams have no past, and `join`
  becomes the diagonal of a skewed stream of streams
  (patai-efficient-and-compositional-higher-order-streams pp. 3–5, 8–9).
  reactive-banana 1.0 moved every history-dependent operation, such as
  `accumE` and `stepper`, into its `Moment` monad
  (apfelmus-frp-release-of-reactive-banana-version-1-0 p. 1), which is
  the same idea.
- Jeltsch's *era* parameter quantifies an inner's era like `ST`, so outer
  behaviours enter only through `switcher`'s arguments, which strip their
  history (apfelmus-frp-dynamic-event-switching pp. 4–5). It's the most
  direct type-level answer in the batch.
- FrTime deletes the signals created in a branch's "extended dynamic
  extent" when the branch is switched out, before any of them can update,
  and doesn't wait for a collector
  (cooper-embedding-dynamic-dataflow-in-a-call-by-value p. 9). That gives
  `depends` an inverse. It also changes the semantics: switched-out state
  is destroyed, which Sodium's isn't.

**A dynamic graph needs its order repaired, and the ranked systems pay
for it.** FrTime runs a height-ordered priority queue. When a new branch
is taller, heights are adjusted and the queue told before any more
updates (cooper-embedding-dynamic-dataflow-in-a-call-by-value pp. 7–8),
and cycles are found by the height reassignment
(cooper-integrating-dataflow-evaluation-into-a-practical-higher-order
p. 46). Scala.React keeps topological levels. When an opaque node reads
a node at or above its own level it throws, is hoisted above that node
with its dependents, and is re-run later in the same turn, which forces
expression signals to be side-effect free
(maier-deprecating-the-observer-pattern-with-scala-react pp. 12–13). The
thesis proves the scheme keeps every edge going upward
(maier-reactive-programming-abstractions-for-complex-event-logic-and
p. 84, Lemma 5.2.5), and its `hoist` walks only dependents below the new
level, with cycle detection a by-product "a debug version" could add
(p. 81). The only claim that repairs are rare is unmeasured
(maier-higher-order-reactive-programming-with-incremental-lists p. 19).
Flapjax doesn't say how it repairs ranks when `switchE` rewires a
taller inner (meyerovich-flapjax-a-programming-language-for-ajax-applications
p. 10). Jane Street's Incremental raises a parent's height and its
ancestors' in increasing order when an edge would point downhill, and
finds a cycle when that walk meets the child (the Incremental source,
`adjust_heights_heap.mli`, read at v0.17.0 in the crate table below).

**Incremental cycle detection is a solved problem with an unhelpful
bound.** Every known efficient cycle detector keeps a topological order
(haeupler-incremental-cycle-detection-topological-ordering-and-strong-component
p. 3). Pearce and Kelly keep one integer per node. An edge that already
agrees with the order costs a comparison, and one that doesn't searches
only the affected region between its ends
(pearce-a-dynamic-topological-sort-algorithm-for-directed-acyclic
pp. 3, 5, 8). On random 2,000-node graphs the simple array beats the
asymptotically better algorithms, because ordered lists are expensive
(pp. 15–17, 20; not reproduced). HKMST's limited search is Bough's
upstream walk with one change: it never visits a node on the wrong side
of the order (haeupler-… p. 4). The amortized bounds assume insertions
only. With deletions the algorithms stay correct and the order stays
valid, but "our time bounds are no longer valid" (haeupler-… p. 2;
bender-a-new-approach-to-incremental-cycle-detection-and p. 18). A
switch move deletes as well as inserts, so for Bough only the
per-insertion, affected-region cost means anything. Batching helps only
for large batches (pearce-a-batch-algorithm-for-maintaining-a-topological-order
pp. 7–8).

Two more ideas bear on the relink check. Pouzet and Raymond summarize a
subgraph by which inputs reach which outputs in the same instant, so a
caller checks feedback against the summary, not the insides
(pouzet-modular-static-scheduling-of-synchronous-data-flow-networks
pp. 5, 9–12). A summary goes stale whenever a switch inside it moves.
Async RaTT's Theorem 4.5 gives a static upper bound on the inputs an
output can depend on, through switching (bahr-asynchronous-modal-frp
p. 19). That's the formal form of RFD 2's untried "check every candidate
at build", and it works only because candidates can't come from anywhere
but the typing context. `construct` makes new ones.

**[F46](./2026-09-24-engine-feasibility-spike.md#f46) needs only an order of operations.** If every deletion of a
transaction is applied before any insertion, each intermediate graph is
a subgraph of the final one. If the final graph is acyclic, so is every
intermediate one, and no legal reversal is refused. That is my reading of
the theory above, not a source's claim. RFD 5 already checks after all
moves, which is the same thing.

### The Rust prior art

Sycamore runs RFD 5's design and folds cycle detection into it: a DFS
over dependents with `Temp` and `Permanent` marks, reverse post-order as
the evaluation order, and a panic, "cyclic reactive dependency", when
the DFS meets a `Temp` node (sycamore-reactive@0.9.3
`packages/sycamore-reactive/src/root.rs`:193–277). Leptos has no cycle
detection; `ImmediateEffect` only warns when a run recurses more than
twice (leptos@v0.8.21 `reactive_graph/src/effect/immediate.rs`:352–354).
Leptos, Sycamore, salsa and Incremental all tie a node's life to the run
that created it: an owner's re-run disposes what the last run made
(leptos@v0.8.21 `reactive_graph/src/owner.rs`:34–46;
sycamore-reactive@0.9.3
`packages/sycamore-reactive/src/signals.rs`:139–143,
`packages/sycamore-reactive/src/root.rs`:160; salsa@salsa-v0.28.5
`src/tracked_struct.rs`:186–191). carboxyl's stream `switch`
re-registers on each new inner and kills the old callback through a
dropped token (carboxyl@2a80080 `src/stream/mod.rs`:445–475).
`incremental-topo` packages Pearce and Kelly's order over a generational
arena (docs.rs/incremental-topo/0.3.1).

### What the probes found

Three probes and their extensions built RFD 5's relink check against the
alternatives, on a 10,147-node UI-shaped graph with 750
`construct`-style subgraphs. Four workloads build 0%, 20%, 50% and 100%
of their new inners during the instant: `settled`, `mixed`, `churn` and
`lazy`.

- **The grey mark can't replace the walk** (`rfd-0005-cycle-in-mark`).
  A DFS mark with a grey state finds a cycle only at the first later
  transaction whose input reaches it. Over 2,000 random `switch_cell`
  cycles it found 781 one transaction late, 882 two to five late, 327
  six to twenty late and 10 not within twenty. Over 2,000
  `switch_stream` cycles it never found 918, 912 of them because no
  input reaches the cycle at all. Of 15 illegal hand-written cases, the
  walk finds 9; Brent's guard finds 6 before either check runs, in both
  designs, and without it they overflow the stack. The mark adds 6.1%
  to a 10,101-node mark in instructions. It found no false positives.
- **The upstream set is small on this shape.** A move to an existing
  view walks about 535 nodes (median upstream 503, most 1,138), not
  [F50](./2026-09-24-engine-feasibility-spike.md#f50)'s ten thousand (`rfd-0005-bounded-relink-check`).
- **A Pearce–Kelly array loses badly when inners are built during the
  instant.** It is 0.018 of the walk's time on `settled`, and 20, 91
  and 250 times worse on `mixed`, `churn` and `lazy`. A new node goes
  at the end of the order, so the first link searches the switch's whole
  downstream (wall-clock). Per-subgraph summaries never beat the walk:
  1.28 to 1.40 of it (wall-clock).
- **An order-maintenance list that places new nodes on the small side
  bounds it on this shape** (`rfd-0005-small-side-order`). Placing the
  new side just before the switch, with a backward search or HKMST's
  two-way search, costs 0.020, 0.11, 0.30 and 0.64 of the walk's time on
  the four workloads with the first, and 0.017, 0.10, 0.29 and 0.62 with
  the second, and a node built costs about 14% more than without
  an order (wall-clock).
- **It isn't bounded in general.** On an adversarial shape the backward
  search costs 2.3 to 8.8 times the walk, and the two-way search 3.2 to
  11 times unless the switch's downstream is much smaller than the new
  inner's upstream. On a cycle the timings are noisy, moving by up to
  45% between days. The backward search's cost is its search, sort and move, not
  relabelling: with fresh spacing it relabels nothing and still costs
  2.6 to 7.1 times the walk's instructions on the adversary. Dropping
  the sort, moving the set in DFS post-order instead, brings it to 1.7
  to 3.0 times the walk's time (wall-clock), and to 0.61 to 1.24 on
  cycles over two days' runs, sometimes beating the walk there.
- **Where the list pays.** On a mixed adversary, a new inner reading
  some old nodes before the switch and some new ones after it, the
  no-sort backward search beats the walk once the old upstream is
  somewhat larger than the new side: at 1,000 new nodes it costs 1.24 of
  the walk with 1,000 old ones and 0.23 with 10,000 (wall-clock). The
  instruction counts put that line near twice.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-small-side-order-counts at experiments@1e7b257 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_small_side_order::tests::mixed_spacing_counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-small-side-order-instructions at experiments@d64e616 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-small-side-order-instructions -- '*::nosort::*'
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-cycle-in-mark at experiments@f16d00b - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0005-cycle-in-mark
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-cycle-in-mark-instructions at experiments@f16d00b - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-cycle-in-mark-instructions
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-bounded-relink-check-counts at experiments@39fd355 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_bounded_relink_check::tests::counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-bounded-relink-check-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-bounded-relink-check-wallclock
python3 scripts/ratios.py moves build
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-small-side-order-counts at experiments@65b0230 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_small_side_order::tests::counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-small-side-order-instructions at experiments@1e7b257 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-small-side-order-instructions
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-small-side-order-counts-nosort at experiments@d64e616 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_small_side_order::tests::nosort_counts -- --nocapture --exact
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-small-side-order-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-small-side-order-wallclock
python3 scripts/ratios.py
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-29 - rfd-0005-small-side-order-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-small-side-order-wallclock
python3 scripts/ratios.py
```

### Settled decisions the evidence contradicts

None found. Every ranked system confirms that a dynamic graph costs a
ranked scheduler repairs, and that is RFD 5's stated worry. What the
scheduling section finds is that the repair is cheap; see there. RFD 5's
per-move walk and Brent's guard on reads both stand: the probe found no
design that makes either redundant.

### The options for Bough

For the relink check:

1. Keep the upstream walk, with every deletion applied before any
   insertion, as RFD 5 has it.
2. Keep an order-maintenance list, place a new inner's new nodes just
   before the switch, and check a move by a backward search in
   post-order. It costs a label per node and about 14% per node built.
3. Get the check from Incremental-style heights, which the scheduling
   section weighs, since raising heights at a link finds cycles on the
   way.
4. Check every candidate at build, Async RaTT-style. It needs every
   switch to declare its candidates, and `construct` defeats it.

For what a switch does to what it deselects: keep Sodium's "deselected
inners keep accumulating", or destroy what a branch built, as FrTime and
the owner-scoped Rust libraries do.

### Claude's leaning

Option 1 now. On the UI shape the walk is about 535 nodes, a few
microseconds, and the probe found nothing that retires it or Brent's
guard. If Oort or bough-gtk shows moves with large upstream sets, option
2 is the one to build, not a Pearce–Kelly array, and option 3 comes free
if the scheduling question goes to heights. Keep "deselected inners keep
accumulating", and write down that it's why Bough can't have the
automatic inverse every owner-scoped library has. Keep Sodium's
switch-instant asymmetry and cite Reflex's reason for it.

### Questions to grill

- Is the 121 µs of [F50](./2026-09-24-engine-feasibility-spike.md#f50) a shape real programs hit, or is a real new
  inner's upstream a few hundred nodes, as the UI-shaped graph has it?
- Would you pay a label per node and 14% per node built so that most
  moves cost a comparison, or only once a real program shows slow moves?
- FrTime and every owner-scoped Rust library destroy what a switched-out
  branch built. Is "a deselected inner keeps accumulating" worth losing
  that automatic inverse for `depends`, and is it written down as the
  reason?
- Would you want Reflex's reason for the old stream at the switch instant
  on record in RFD 1, since the book gives none?
- Does anything besides the cycle check want a global order? If the
  scheduling question goes to heights, the relink check should come from
  them.

### Experiments this proposes for Bough

- Log every move's upstream size, and whether it links a node built in
  the same instant, on Oort's fighter and on bough-gtk's list view, to
  know which of the four workloads real programs look like.
- Count, on those same programs, how often a transaction moves more than
  one switch, and how often two of its moves touch the same region, to
  see whether [F46](./2026-09-24-engine-feasibility-spike.md#f46)'s order of operations ever matters in practice.

### Reading path

- reflex-reflex-class for the switch-instant semantics: the Primitives,
  MonadHold and "Collapsing `Event . Event`" sections. Needs Haskell type
  classes.
- patai-efficient-and-compositional-higher-order-streams for generators.
  Short; needs monads and `mfix`.
- cooper-embedding-dynamic-dataflow-in-a-call-by-value §§1–3 for
  FrTime's heights and deletion; §4 needs reduction semantics with
  evaluation contexts.
- maier-deprecating-the-observer-pattern-with-scala-react §§7.1–7.3 and
  7.6 for hoisting. Needs basic Scala.
- pearce-a-dynamic-topological-sort-algorithm-for-directed-acyclic, then
  haeupler-incremental-cycle-detection-topological-ordering-and-strong-component
  §2. Needs DFS, topological sort and amortized analysis; HKMST's §§4–6
  are heavy theory Bough doesn't need.
- The Incremental source's `incremental_intf.ml`, lines 90–260, is a
  self-contained description of heights and `bind`.

## Loops and causality (RFDs 2, 5)

### What the literature says

**Bough's loop rule is the synchronous languages' rule.** RFD 2 keeps
the same-instant dependency graph acyclic, with a read of a cell from
before the instant and a child instant as the only ways round. That is
Esterel v4's rule, which Berry calls the usual rule for dataflow
languages, and every program it accepts is constructive
(berry-the-constructive-semantics-of-pure-esterel pp. 13, 55). It is
Lustre's rule, that every cycle contains a `pre`, and Lustre refuses
false cycles such as `X = if C then Y else Z; Y = if C then Z else X`
knowingly, since deciding them is undecidable in general
(halbwachs-the-synchronous-data-flow-programming-language-lustre p. 14).
It is Copilot's, where a weighted dependency graph whose every loop
passes a delay is sufficient for a unique meaning and the converse fails
(pike-copilot-a-hard-real-time-runtime-monitor p. 8, Thm. 1). It is
DBSP's, where feedback is well defined when the operator on the cycle is
strict, depending only on inputs before `t`
(budiu-dbsp-automatic-incremental-view-maintenance-for-rich-query p. 3,
Prop. 2.9, Lem. 2.10). A snapshot reads the cell before the instant,
which is DBSP's `z⁻¹`. It is Naiad's and Lee's: every cycle has a
feedback vertex, or a delay or integrator found by dependence analysis
(murray-naiad-a-timely-dataflow-system p. 2;
lee-operational-semantics-of-hybrid-systems p. 17). And it is exactly
right for opaque functions. Keating and Gale prove that a loop with no
direct dependency cycle, delays excluded, can be rewritten to a strict
form with an execution order known at compile time, treating `arr` as a
black box that depends on everything
(keating-this-is-driving-me-loopy pp. 8–11, Thm. 4.5). The theorem gives
that one direction; that a cycle has no such order is the paper's
statement about its implementation (p. 2), not a proved result.

**What the rule refuses that constructiveness accepts.** Berry's users
dismissed acyclicity as too restrictive: "Users ask us to control
feedback, not to restrict it" (berry-… p. 13). Constructive analysis
accepts three more kinds of cycle (pp. 40–41, 50, 55;
shiple-constructive-analysis-of-cyclic-circuits pp. 5–6):

- (a) halves of the cycle in mutually exclusive branches;
- (b) false paths ruled out by facts already known this instant;
- (c) halves separated by a delay, which Bough already accepts.

In Bough terms, (a) is a stream cycle through `gate c` and
`gate (not c)`. Since cells are read before the instant, the conditions
are known when the instant starts, as Esterel's inputs and registers
are (berry-… p. 108). Bough's answer to "only one of these matters at a
time" is switching: a `switch_stream` removes the unselected edge. (b)
needs value-level facts, which a push engine doesn't reason about.
Constructiveness costs reachability over states, which Bough can't do
over unbounded values and a run-time graph
(shiple-constructive-analysis-of-cyclic-circuits p. 4). It makes
acceptance depend on how each primitive treats unknown inputs
(schneider-causality-analysis-of-synchronous-programs-with-delayed-actions
pp. 10–11), and it changes Bough's error from "this graph has a cycle"
to "in some reachable state, this is undetermined". By analogy, Scade's
users accept the extra constraints that modular compilation puts on
feedback loops, since their applications tolerate an inserted delay
(pouzet-modular-static-scheduling-of-synchronous-data-flow-networks p.
18, fn. 9).

Sequential constructiveness accepts more still, but only through program
order between statements (vonhanxleden-sequentially-constructive-concurrency-a-conservative-extension-of-the
pp. 2–3, 21). A Bough instant is a dataflow graph with no statement
order, so SC widens nothing here. It does name Bough's choice. It weighs
"all reads before any writes", under which reads see the previous tick,
and rejects it as less expressive, not as unsound (p. 15). `accumulate_mut`
is its relative write (p. 13), and a cell is Aguado et al.'s registered
variable, supplied at the start of the instant, for which read-safety
holds trivially
(aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of
pp. 19, 37). That is the formal reason a cell read is never an ordering
dependency.

**[F3](./2026-09-24-engine-feasibility-spike.md#f3) isn't a program constructiveness would rescue.** In
`c = hold 0 (merge ticks (map (+1) (steps c)))`, an instant without
`ticks` gives x = x, which is Esterel's `present O then emit O`, whose
least fixpoint is ⊥ (berry-… pp. 31, 41). SC's check, Keating's direct
dependency and DBSP's strictness all refuse it. It needs `steps`, and the
book's ten core primitives "give you no way to convert a cell into a
stream" (blackheath-functional-reactive-programming, ch. 8, §8.4; ch. 2,
§2.14, Table 2.2). So "every loop passes through a hold" may be the
right rule for the core, and the operational primitives are what break
it. That ties open questions 3 and 10.

**A static check exists in two sizes.** Cuoq and Pouzet type each stream
with a row marking which recursion variables it depends on in the same
instant; `pre` gets an unconstrained row and `rec` demands its own
variable absent (cuoq-modular-causality-in-a-synchronous-stream-language
pp. 4–6). It has principal types and handles higher-order code, but
unification wrongly rejects some programs, the authors' "biggest
drawback" (p. 8), and there's no switching at all. Sculthorpe and
Nilsson's is one bit: each signal function is decoupled or not, composite
flags are computed, and `loop` demands a decoupled feedback path
(sculthorpe-safe-functional-reactive-programming-through-dependent-types
pp. 5–6). Keating and Gale point at the same bit
(keating-this-is-driving-me-loopy pp. 12–13). Both say one bit per
function is coarse and a per-input-output matrix more precise
(sculthorpe-… p. 11; jeffrey-ltl-types-frp p. 7). Bough's run-time
graph check is that matrix at node granularity. Keeping Calm names the
higher-order problem: a property survives a switch only if every
possible residual has it, and the residual comes from a host-language
function (sculthorpe-keeping-calm-in-the-face-of-change pp. 33–34).

**The rule doesn't bound a transaction.** A guarded fixed point makes
"may happen" and "must happen" coincide, so it can't promise termination
(bahr-diamonds-are-not-forever p. 3; cave-fair-reactive-programming
p. 3). Esterel forbids a loop body that finishes in the same instant
(berry-… pp. 23–24), and clock refinement warns that the outer step ends
only if the inner loop ends
(gemunde-clock-refinement-in-imperative-synchronous-languages p. 9).
Delayed actions in Quartz go to the next step
(schneider-causality-analysis-of-synchronous-programs-with-delayed-actions
pp. 5–6); Bough's child instants nest inside the transaction. So [F22](./2026-09-24-engine-feasibility-spike.md#f22), a
`defer` loop with no filter, is a liveness problem outside causality, and
nothing in the batch bounds it.

### The Rust prior art

DFIR states Bough's rule for a static graph and checks it at compile
time: "Cyclical dataflow within a tick is not supported. Use
`defer_tick()` or `defer_tick_lazy()` to break the cycle across ticks"
(hydro@dfir_rs-v0.16.0 `dfir_lang/src/graph/flat_to_partitioned.rs`:352–366).
Its docs still describe fixpoint iteration within a tick
(`docs/docs/dfir/concepts/life_and_times.md`:17), so the rule changed
and the docs lag. salsa panics on a cycle unless a query opts into
fixed-point iteration (salsa@salsa-v0.28.5 `src/cycle.rs`:3–58).
Sycamore panics when its DFS meets a node still on the stack
(sycamore-reactive@0.9.3 `packages/sycamore-reactive/src/root.rs`:254–277).
carboxyl's `Signal::cyclic` is a forward declaration that panics if
sampled before it's defined (carboxyl@2a80080 `src/signal.rs`:209–218,
501–512). None of them checks loops through switching: carboxyl has
Sodium's two switches but no cycle check at all, and the others have no
switch of Sodium's kind.

### What the probes found

**The census supports plain acyclicity** (`rfd-0002-ternary-loop-census`).
A ternary evaluator over presence and then value ran 400,000 random
programs that acyclicity refuses, of one to eight nodes over two inputs.

- With any presence of inputs, the quiet instant included, 687 are
  constructive (0.17%), and every one is class (a), exclusive gates. No
  other class can exist there: a quiet instant leaves every open cycle
  at ⊥.
- If at least one input fires every instant, 1,798 are constructive:
  687 (a), 894 with a dead `or_else` branch, 217 with a live cycle such
  as mutual defaults, `s0 = i0.or_else(s1)`, `s1 = i1.or_else(s0)`; 2
  of the 1,111 outside (a) are value-dependent. None looks like a
  program anyone means to write, and every one outside (a) breaks when
  another input fires alone or an instant is a child instant.
- Letting gates read holds of the loop, so cells take only reachable
  states, adds 10,491 more under any presence: 10,436 behind a gate
  that's closed in every reachable state, which is dead code refusal
  catches, and 55 from two complementary cells, which is one cell with
  `gate(c)` and `gate(!c)` again. With at least one input firing, 17
  more sit behind constant cells.
- Every program of two to four nodes and every cell binding: of
  3,147,279 refused over two inputs, 13 programs are constructive with a
  cell that changes when some input fires every instant (none when the
  quiet instant counts), in 13 minimal forms, all of four nodes, and all
  break when a third input fires alone. Over three inputs, of 3,468,034,
  none.

**A one-bit marker checks `close`, and can't check switches**
(`rfd-0002-decoupled-marker`). Each stream and cell type carries a mark,
decoupled or not, and `close` requires decoupled.

- It refuses [F3](./2026-09-24-engine-feasibility-spike.md#f3) at compile time, with the error "this loop's definition
  depends on a loop's forward reference in the same instant", and builds
  [F1](./2026-09-24-engine-feasibility-spike.md#f1)'s counter. On the first fixture set it refused all 6 illegal loops
  and 3 of 10 legal ones: a helper returning `impl Source`, a helper
  taking a plain `Cell<u32>`, and two loops where one resets the other.
  Helpers generic over the mark fix the first two.
- Extended to `gate`, `sample`, `split`, `defer` and `depends`, it still
  refused every illegal fixture. It can't see sampling a loop cell
  before close, which stays a panic when the graph is built.
- Compile time, on the idle machine: 1.02 to 1.06 of the baseline on the
  hand-written fixtures, and 1.03 to 1.16 on a generated program of 512
  depth-three chains. Cuoq-style rows cost 1.05 to 1.25 there.
- **The one-bit marker and rows accept an illegal loop smuggled
  through a switch.** A loop or a construct hands a switch its own
  consumer's steps as a token, and it builds: under the plain marker,
  under a `close` that re-marks its token decoupled, under rows, and
  inside a construct at a child instant. A switch's reach grows after
  build, so neither one bit nor rows can make a switch's moves a
  compile-time check.
- A mark on a switch's output, `Switched`, between decoupled and
  instantaneous, refused all 3 smuggles and kept navigation, and refused
  a switch inside a switch and an inner reading an open forward. A rule
  that re-marks everything once the last loop closes built the switch
  smuggle, and let two builds trade a loop to desynchronise its count.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-ternary-loop-census at experiments@ef7bb53 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-ternary-loop-census
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-ternary-loop-census at experiments@1d2e0d0 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-ternary-loop-census
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-ternary-loop-census at experiments@5a6b1a1 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-ternary-loop-census -- --enumerate
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-decoupled-marker at experiments@81da0b0 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-decoupled-marker
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-decoupled-marker at experiments@4bc4cae - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-decoupled-marker
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-decoupled-marker at experiments@48bdda5 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-decoupled-marker
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-decoupled-marker at experiments@382380f - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-decoupled-marker
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0002-decoupled-marker at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0002-decoupled-marker -- --compile-time
```

### Settled decisions the evidence contradicts

None found. Acyclicity with pre-instant reads and child instants as cuts
is the field's standard rule, sound and knowingly incomplete, and the
census finds nothing it refuses that a program would want and a switch
couldn't express.

### The options for Bough

1. Keep run-time acyclicity alone, as RFD 2 has it.
2. Add the one-bit marker at `close`, which makes [F3](./2026-09-24-engine-feasibility-spike.md#f3) and its relatives a
   compile error for a few percent of compile time, and keep the
   run-time check at a switch's first link and moves.
3. Also mark switch outputs `Switched`, which makes the smuggle a compile
   error at the price of refusing a switch inside a switch and an inner
   that reads an open forward.
4. Go constructive: accept cycles through exclusive gates.

For [F22](./2026-09-24-engine-feasibility-spike.md#f22): accept it as the user's bug, bound child-instant depth at run
time, or require every `defer` loop to pass a filter or a bound.

### Claude's leaning

Option 1, and say in RFD 2 that the rule is Lustre's and Esterel v4's,
sound and knowingly incomplete, with Keating and Gale's theorem as its
justification for opaque functions. Name the refused class, exclusive
gates, and point to switching as how Bough writes it. Option 2 is cheap
and catches a real mistake at compile time, but it covers `close` only,
costs a mark parameter on every helper signature, and the run-time check
stays whatever happens. I'd hold it until [F3](./2026-09-24-engine-feasibility-spike.md#f3)-shaped mistakes show up in
real code. Treat [F22](./2026-09-24-engine-feasibility-spike.md#f22) as liveness, bounded at run time in the embedded
tier and left to the user elsewhere.

### Questions to grill

- Do you want the loop rule to be exactly the class the semantics gives
  meaning to, or a sound subset that's easy to state? Berry's users and
  Lustre's chose differently.
- Have you wanted a Bough program whose only same-instant cycle runs
  through two exclusive gates that a `switch_stream` couldn't write
  acyclically?
- Is [F3](./2026-09-24-engine-feasibility-spike.md#f3) a `steps` problem, so that "every loop passes through a hold"
  holds for the core, and does that go into the case for fencing
  `steps`?
- Would a marker that catches [F3](./2026-09-24-engine-feasibility-spike.md#f3) at compile time be worth a mark
  parameter on every helper, given that it can't cover switches?
- Is [F22](./2026-09-24-engine-feasibility-spike.md#f22) something to refuse statically, bound at run time, or leave as
  the user's bug?

### Experiments this proposes for Bough

- Put the marker on Oort's fighter and on bough-gtk, and count how many
  helper signatures need the mark parameter and how many false refusals
  real code hits.
- Search Oort's and the Sodium book's example programs for any
  same-instant cycle through exclusive gates, the one class a
  constructive rule would add.

### Reading path

- berry-the-constructive-semantics-of-pure-esterel chapters 1–4, which
  are informal and enough for the causality argument. Chapter 10 needs
  Scott domains and least fixpoints.
- keating-this-is-driving-me-loopy after its §2.1 summary of causal
  commutative arrows. §4's proof is readable.
- halbwachs-the-synchronous-data-flow-programming-language-lustre p. 14
  for the rule in one page.
- cuoq-modular-causality-in-a-synchronous-stream-language for rows.
  Needs Hindley–Milner inference and Rémy-style row types; skip §5's
  proof.
- vonhanxleden-sequentially-constructive-concurrency-a-conservative-extension-of-the
  §§1, 4 and 5. Self-contained and operational.
- shiple-constructive-analysis-of-cyclic-circuits after Berry's
  chapter 4. Needs BDDs and symbolic reachability.

## Scheduling and glitch freedom (RFD 5)

### What the literature says

**Everyone gets glitch freedom from an order, a count or a pull.**

- MobX counts pending parents in a first pass and updates a node when
  its count reaches zero in a second
  (milomg-super-charging-fine-grained-reactive-performance pp. 3–4).
  Preact versions its nodes and edges (p. 5).
- Reactively, the TC39 signals proposal and most fine-grained signal
  libraries colour down and then pull: a write marks immediate sinks
  dirty and deeper ones "check", and a read finds the deepest dirty
  source and recomputes from there (milomg-… p. 6;
  tc39-javascript-signals-standard-proposal pp. 11, 13–15). That is
  glitch-free because computeds run only on read and a signal is
  *lossy*: two writes without a read lose the first, "a feature rather
  than a bug" (tc39-… p. 17). FRP streams can't be lossy.
- Adapton dirties eagerly and repairs in demand order. Laziness wins big
  when little output is demanded, and loses 1.5 to 3.5 times to eager
  incremental computation when all of it is
  (hammer-adapton-composable-demand-driven-incremental-computation
  pp. 2, 9; not reproduced).
- Build systems get it from a topological order, which needs static
  dependencies, by restarting, which aborts a task that reads a stale
  key, or by suspending, which is memoized pull
  (mokhov-build-systems-a-la-carte pp. 13–14). Bough is a topological
  scheduler recomputed each transaction for the part of the graph
  that's static within an instant, plus suspending for the two dynamic
  cases. The taxonomy supports that split.
- FrTime, Flapjax and Scala.React rank nodes and run a priority queue
  (cooper-embedding-dynamic-dataflow-in-a-call-by-value p. 7;
  meyerovich-flapjax-a-programming-language-for-ajax-applications p. 12;
  maier-deprecating-the-observer-pattern-with-scala-react p. 9). Jane
  Street's Incremental keeps heights, an over-approximation of the
  longest path to a node, in an array of buckets
  (incremental@v0.17.0 `src/incremental_intf.ml`:111–139).
- Self-adjusting computation runs a priority queue keyed by
  order-maintenance time stamps, O(1) to insert, delete and compare
  (acar-self-adjusting-computation pp. 48, 51, 63). Its order never
  needs repair, because it is the order of one sequential run, and where
  it would need a swap the thesis stops: "likely difficult, if not
  impossible" in constant time (p. 62).

Of all these, RFD 5's DFS reverse post-order over the affected region is
the only one that is glitch-free without lossiness, a per-read stamp, a
per-node count or a maintained rank.
The cost is linear in the region.

**The literature's case against ranks is the repair, and the repair
turns out to be cheap.** RFD 5 rejects rank-ordered push because ranks
"must exceed all dynamically reachable inners", which "forces Sodium to
re-rank and rebuild its queue mid-transaction", and because "a heap
would have added a log factor" for a frame. Every ranked system in the
batch confirms that switching costs a ranked scheduler repairs: FrTime
re-heights and patches the queue (cooper-embedding-dynamic-dataflow-in-a-call-by-value
p. 8), and Scala.React aborts, hoists and re-runs
(maier-deprecating-the-observer-pattern-with-scala-react pp. 12–13). But
Incremental re-heights incrementally, bounded by the ancestors whose
height must rise, and finds cycles on the way
(incremental@v0.17.0 `src/adjust_heights_heap.mli`:3–8, 39–69). And a
bucket queue indexed by small-integer heights has no log factor. Neither
the Incremental blog post nor any paper measures what that costs under
switching (minsky-introducing-incremental pp. 1–9 says nothing about
heights), so the probes did.

**Order maintenance is cheap, and solves a problem Bough doesn't have.**
Order maintenance exists to insert stamps in the middle of a timeline
(acar-self-adjusting-computation p. 137; acar-adaptive-functional-programming
p. 13). Bough's new nodes go at the end, and a relink permutes the
positions an affected region already holds, so a plain array or small
integers suffice. The switching section found one place a list helps:
putting a new inner's nodes just before its switch.

### The Rust prior art

Sycamore ships RFD 5's scheduler: a DFS over dependents, reverse
post-order, a flat loop that runs each node still dirty, and a pull for
a dirty node read during the loop
(sycamore-reactive@0.9.3 `packages/sycamore-reactive/src/root.rs`:193–235,
121–130). It reuses its sort buffer between propagations (lines 26,
198–207). Leptos is Reactively's colour-then-pull with a `PartialEq`
cut-off (leptos@v0.8.21 `reactive_graph/src/lib.rs`:67–69,
`reactive_graph/src/computed/inner.rs`:69–177,
`reactive_graph/src/computed/memo.rs`:173–191). sodium-rust runs changed
nodes at the end of a transaction in DFS order with a visited flag and
no ranks (github.com/SodiumFRP/sodium-rust @3e93021
`src/impl_/sodium_ctx.rs`:233–262, 298–355). incremental-rs keeps
Incremental's design, a queue per height up to a maximum
(github.com/cormacrelf/incremental-rs @5ba8209 `src/recompute_heap.rs`).
DFIR's whole scheduler is a topological order fixed at compile time, one
closure per tick (hydro@dfir_rs-v0.16.0
`dfir_lang/src/graph/meta_graph.rs`:813–816). salsa is pull only: it
validates a memo's inputs in the order they ran (salsa@salsa-v0.28.5
`src/function/maybe_changed_after.rs`:591–597).

### What the probes found

Three probes set schedulers against RFD 5's mark and flat loop. Two
shapes: RFD 1's UI and frame shapes with static heights, and the
switching section's 10,147-node graph under its four workloads, with
filters whose pass rate sets the quiet share of each marked region. The
wall-clock ratios below are each scheduler's time over the mark's, from
the idle machine. The instruction counts, taken first, put the bucket
and height crossovers lower; wall-clock is what counts here.

- **Static heights with a bucket queue** (`rfd-0005-heap-vs-mark-on-quiet-regions`).
  On the 9,997-node UI shape the bucket queue costs 1.25 of the mark
  when every marked node fires, 1.15 at 10% quiet, 1.02 at 26% quiet,
  0.79 at 50% and 0.21 at 89%. A binary heap costs 2.58 when everything
  fires and breaks even between 50% and 74% quiet. On the frame shape,
  where everything fires, the bucket queue costs 1.09 at a width of 64
  entities and 0.94 at 1,024, and the heap 1.50 at both. So the log
  factor is real for a binary heap and small for a bucket queue.
- **Heights raised at link time, Incremental's way, under switching**
  (`rfd-0005-height-queue`). Against RFD 5's mark with an unforced
  construct point:

  | quiet share of the marked region | heights ÷ mark |
  |---|---|
  | about 1% | 1.25 to 1.31 |
  | 30% to 54% | 0.69 to 1.00 |
  | 56% to 75% | 0.41 to 0.68 |
  | 72% to 86% | 0.26 to 0.48 |
  | 95% to 98% | 0.06 to 0.10 |

  Heights lose about a quarter when everything fires, break even near
  30% quiet, and win ten to eighteen times when most of the region stays
  quiet. The instruction counts put break-even near 5% quiet; the
  wall-clock doesn't agree, and nothing was measured between 1% and 30%.
- **The re-ranking RFD 5 names is small.** Over 300 transactions and
  about 1,250 moves per workload, 46 to 145 links needed a raise. In the
  instant, raises mid-evaluation came to 0.13 to 0.37 a transaction,
  touching one node a transaction or fewer on average, and never below
  the cursor, since a switch sits after its selector. But one raise
  touched up to 7,421 nodes, so a single link can cost a large pause.
- **The raise finds cycles.** It refused exactly the walk's set of
  moves, at 4 to 7 nodes a refused cycle (10 to 28 over each
  workload's 2 to 6 refusals).
- **Heights grow far only when cycles are refused.** Over 3,000
  transactions the largest height grew from 72 to between 242 and 367,
  all but a few levels of it from interrupted raises at refused cycles;
  without them it rises from 72 to 74–78 and plateaus there.
  Under RFD 5's rule a refused cycle poisons the runtime, so that growth
  never happens.
- **Maintained sparse labels lose the bucket queue**
  (`rfd-0005-maintained-rank-queue`). Ranks from the switching section's
  order-maintenance list, in a binary heap, cost 2.35 to 2.43 of the
  mark when everything fires and break even between 56% and 75% quiet. A
  radix heap does little better, 2.18 to 2.27 when everything fires.
  Keeping the labels is cheap: 0.02 to 0.61 of the walk's upkeep.
- **Flat adjacency is faster in time, not in instructions.** Rerun over
  flat edge arrays, the mark takes about 13% less time than over nested
  vectors, though it runs more instructions, and the conclusions above
  hold.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-heap-vs-mark-on-quiet-regions-counts at experiments@8006fcf - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_heap_vs_mark_on_quiet_regions::tests::counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-heap-vs-mark-on-quiet-regions-instructions at experiments@8006fcf - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-heap-vs-mark-on-quiet-regions-instructions
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-heap-vs-mark-on-quiet-regions-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-heap-vs-mark-on-quiet-regions-wallclock
python3 scripts/ratios.py ui-small ui-large frame
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-height-queue-counts at experiments@9c8acb5 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_height_queue::tests::counts -- --nocapture --exact
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-height-queue-counts-growth at experiments@9c8acb5 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_height_queue::tests::growth -- --nocapture --exact
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-height-queue-counts-pull at experiments@401293c - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_height_queue::tests::counts_instant -- --nocapture --exact
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-height-queue-counts-unforced at experiments@dd225eb - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_height_queue::tests::counts_unforced -- --nocapture --exact
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-height-queue-instructions at experiments@dd225eb - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-height-queue-instructions -- 'rfd_0005_height_queue_instructions::instant::*'
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-height-queue-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-height-queue-wallclock
python3 scripts/ratios.py
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-maintained-rank-queue-counts at experiments@11c30b1 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0005_maintained_rank_queue::tests::counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-maintained-rank-queue-instructions at experiments@b0701be - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-maintained-rank-queue-instructions
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-maintained-rank-queue-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-maintained-rank-queue-wallclock
python3 scripts/ratios.py settled mixed churn lazy upkeep flat-settled flat-mixed flat-churn flat-lazy
```

### Settled decisions the evidence contradicts

**RFD 5's stated reasons for rejecting rank-ordered push don't hold on
their own.** Both reasons it gives are about cost. Re-ranking under
switching comes to a fraction of a raise a transaction, and Incremental
does it routinely. The log factor belongs to a binary heap; a bucket
queue over small-integer heights doesn't have one. What the wall-clock
leaves is a real trade, not a rejection: heights lose about a quarter
when every marked node fires, and win from about 30% quiet, by up to
eighteen times on mostly quiet regions. Whether Bough should rank depends
on how quiet its marked regions are, which no one has measured on a real
program.

The decision's other parts stand. The DFS mark and flat loop are sound
and ship in Sycamore, memoized pull is still the right fallback for
dynamic dependencies (mokhov-build-systems-a-la-carte pp. 13–14), and
pure pull loses when all output is demanded
(hammer-adapton-composable-demand-driven-incremental-computation p. 2).

### The options for Bough

1. Keep RFD 5 as it is, and restate the reason: the flat loop is simpler
   and wins when most of a marked region fires.
2. Heights raised at link time with a bucket queue, the relink check
   folded into the raise, and memoized pull kept for the two dynamic
   cases or replaced by a raise mid-evaluation.
3. Both, chosen per runtime or per shape. Probably not: two schedulers
   to hold to the oracle.
4. Keep the mark and skip quiet regions some other way, such as a
   pre-filter that stops the mark at a gate or filter known closed.
   Untried.

### Claude's leaning

Keep option 1 for the first build, with the rejection reworded, and
treat option 2 as the first performance change to try once a real
program's quiet share is known. The UI shape is where the relink check
would bite ([F50](./2026-09-24-engine-feasibility-spike.md#f50)), though it is still unmeasured. A UI's marked regions
are plausibly mostly quiet, and heights would also give the relink check
for free. But the flat loop is what
RFD 5, the spike and the oracle work already assume, a height raise can
touch thousands of nodes at one link, and a quarter lost when a region
fires whole is not nothing. This is a leaning on a trade, not on a
contradiction, and it rests on the probes' synthetic graphs.

### Questions to grill

- What share of a marked region stays quiet on Oort's fighter and on
  bough-gtk's list view? Above about 30%, heights win.
- Would you give up a quarter when every marked node fires to win up to
  eighteen times on a mostly quiet UI?
- If heights come in, does the relink check come from the raise, and
  does the upstream walk go?
- Is a single link that raises 7,000 nodes an acceptable pause, or does
  the raise need slicing?
- Should RFD 5's rejection name the real trade, or keep the rejection and
  drop the two reasons the probes don't support?

### Experiments this proposes for Bough

- Instrument the real engine's mark to report, per transaction, the
  marked region's size and how much of it fires, on Oort and bough-gtk.
  That one number decides option 1 against option 2.
- If heights come in, time the largest raise on those programs, and the
  frame benchmark from RFD 1 against the flat loop.

### Reading path

- milomg-super-charging-fine-grained-reactive-performance first, then
  tc39-javascript-signals-standard-proposal. Self-contained.
- mokhov-build-systems-a-la-carte §§2 and 4 for the taxonomy. Needs
  Haskell with Applicative and Monad for the code; the prose reads
  without it.
- The Incremental source's `incremental_intf.ml`, lines 90–260, and
  `adjust_heights_heap.mli`. Some OCaml.
- acar-self-adjusting-computation chapters 4–6 and §8.2, for order
  maintenance and queue overhead. Needs amortized analysis.
- hammer-adapton-composable-demand-driven-incremental-computation §§2,
  5 and 6; call-by-push-value helps for §§3–4.

## Memory and leaks (RFD 3)

### What the literature says

**Two failure modes, and every design picks which one it can see.**
Rooting and tracing that under-approximate give use-after-free; ones that
over-approximate give space leaks (jeffrey-josephine-using-javascript-to-safely-manage-the-lifetimes
p. 8). In Bough those are a forgotten `depends`, [F62](./2026-09-24-engine-feasibility-spike.md#f62), which ends in a
stale token, and a `depends` with no inverse, [F63](./2026-09-24-engine-feasibility-spike.md#f63), which kept fifty
screens on the engine spike
([research](./2026-09-24-engine-feasibility-spike.md)). No source in
the batch fixes the second one while keeping Sodium's semantics.

**The modal line catches [F62](./2026-09-24-engine-feasibility-spike.md#f62) and permits [F63](./2026-09-24-engine-feasibility-spike.md#f63).** In the RaTT line a value
is *stable* when it can't reach temporal data, and a closure stored in the
graph, run at later instants, may capture only stable values
(krishnaswami-higher-order-functional-reactive-programming-without-spacetime-leaks
pp. 3–4; bahr-modal-frp-for-all pp. 5–8). Read "temporal data" as "a
Bough token". Then a `construct` builder capturing a cell token is
Rattus's rejected `leakyMap` (bahr-modal-frp-for-all p. 8), and a closure
that captures a delayed location and runs a step later dereferences a
collected one, which is [F62](./2026-09-24-engine-feasibility-spike.md#f62) caught by a type rule
(bahr-simply-ratt-a-fitch-style-modal-calculus-for pp. 8–9, 15). The
rewrite is to pass the cell in as an argument, so the dependency becomes
an edge. But holding what you asked to hold is an *explicit* leak, and
every calculus in the line permits it (bahr-simply-ratt-… p. 2;
bahr-modal-frp-for-all pp. 27–28). Types make captures visible. They
can't decide which retention was meant. The line gets its strongest
promise, that nothing old is ever evaluated, by giving up persistent
nodes: its machines delete every value more than one tick old, and the
types "merely act as a set of guard rails"
(krishnaswami-…-without-spacetime-leaks pp. 3–4). Async RaTT runs only
computations reachable from an output whose clock contains the input
(bahr-asynchronous-modal-frp pp. 15–17), which is scheduling bounded by
liveness from the roots, and the one answer to [F66](./2026-09-24-engine-feasibility-spike.md#f66) that keeps something
like persistent nodes. Rattus leaves collection to GHC's ordinary tracing
collector once the types guarantee old data is unreferenced
(bahr-modal-frp-for-all pp. 34–35).

**Rust's analogue of "stable" is a lifetime brand.** `'static` fails,
since a `Copy` `u32` token is `'static`. `Copy` and `Trace` describe
representation, not time. `Send` propagates through captures the way
stability must, but Bough already uses it for `Threaded`. A user-defined
auto trait with `impl !Stable` for every token is the exact analogue and
needs nightly. A generative lifetime brand is stable Rust. gc-arena brands
its pointers with an invariant `'gc`, so they "cannot escape the arena
callbacks or be smuggled inside another arena"
(gc-arena@v0.7.0 `src/arena.rs`:98–116), and a closure that captures a
`Gc<'gc, _>` isn't `'static` and has no `Collect` impl, so it can't be
stored at all (`src/gc.rs`:88–90, `src/static_wrapper.rs`:9–21). No one
can generate a `Collect` impl for a generator's state machine, "nor any
planned feature that would enable it" (kyren-gc-arena p. 3). Jeltsch's
eras, an `ST`-style start-time parameter, are the FRP form of the same
idea (apfelmus-frp-dynamic-event-switching pp. 4–5). The costs are in
the sources too: a lifetime parameter on every type that holds a pointer,
gc-arena's `TestRoot<'gc>` and shifgrethor's `Foo<'root>`
(goregaokar-a-tour-of-safe-tracing-gc-designs-in pp. 11–12), and all
access through a callback. gc-sequence passes a traced value into a
closure as an argument instead of letting it capture one (goregaokar-…
p. 12), which is RFD 3's rejected "closure-taking twins". Acar's library
has Bough's `depends` problem outright: every free variable of a memoized
expression is declared by hand, the library checks little of its own
discipline, none of it statically, and the author's conclusion is to
leave the library for a compiler (acar-self-adjusting-computation pp.
131, 138, 233, 278).

**Tracing and counting are duals, and the hybrids see cycles.** Tracing
computes the least fixpoint of the reference-count equation and counting
the greatest; the difference is exactly the cyclic garbage
(bacon-a-unified-theory-of-garbage-collection pp. 4–5). So "counts
cannot see cycles" is right for plain counting. But a counting collector
with a backup trace or with trial deletion does collect cycles (pp. 9,
10). In Bacon's taxonomy Bough is a tracing collector whose roots are
kept by the API rather than found by scanning, the shape he calls
*partial tracing* (p. 6). sodium-rust is the Rust instance of the hybrid:
atomic counts plus Bacon–Rajan cycle collection after each outermost
transaction, with closure captures declared as its trace
(github.com/SodiumFRP/sodium-rust @3e93021 `src/impl_/gc_node.rs`:21–120,
`src/impl_/sodium_ctx.rs`:288–294, `src/impl_/lambda.rs`:5–8, 196). It
needs the same declarations and adds counting on top. Deferred counting
still counts writes into the heap (bacon-… p. 5), which for Bough means
every token stored in a value, and a `Copy` token gives no hook there.
So RFD 3's second reason, that tracing needs no counts and tokens can be
`Copy`, is the one that carries.

**`Trace` is safe for generation-checked indices, and nothing disagrees.**
Every source that makes its trace trait `unsafe` does so because a missed
field frees memory still reachable through a pointer
(goregaokar-… p. 4; kyren-gc-arena p. 2;
jeffrey-josephine-… p. 9). None argues that a missed field is unsafe when
handles are checked indices, which is RFD 3's distinction.

**Every GC-based FRP has [F66](./2026-09-24-engine-feasibility-spike.md#f66), and none fixes it but by collecting
sooner.** Garbage is evaluated until it's collected. Elerea calls it its
"biggest problem" (patai-efficient-and-compositional-higher-order-streams
p. 13). In FrTime a strong update queue would keep about half the dead
signals alive, so its queue holds them weakly too
(cooper-integrating-dataflow-evaluation-into-a-practical-higher-order
pp. 35–36). Scala.React's weak forward references make higher-order drag
collectable, but work grows until the collector runs
(maier-deprecating-the-observer-pattern-with-scala-react pp. 14, 16).
Monadic FRP calls weak references a "non-solution" for exactly that
reason (vanderploeg-monadic-functional-reactive-programming p. 11).
Flapjax stops evaluating a stream once all its sinks are detached, a flag
computed during propagation, which is reference counting by another name
(meyerovich-flapjax-a-programming-language-for-ajax-applications p. 12).
Tracing cost grows as 1/(1 − f) with the live fraction f, and a large,
long-lived, mostly live graph is pessimal for it
(hammer-memory-management-for-self-adjusting-computation pp. 1–2). So a
trigger has to scale with the live graph. gc-arena paces incremental
collection by allocation debt (gc-arena@v0.7.0 `src/arena.rs`:267–279).

**Weak references fail Bough for a reason specific to Bough.** In FrTime,
Scala.React and Elerea the host collector traces closures, so a
deselected inner stays alive whenever anything that could reselect it
holds it, and the weak edge decides only the unreachable case. Bough's
arena can't see closure captures, so a weak edge would be the only edge
(my reading of cooper-integrating-… p. 35 and maier-deprecating-… p. 14).
RFD 3's reason, that weak references collect inners that must keep
accumulating, is true because of that.

**The Sodium book's model is RFD 3's.** Unreferenced logic is garbage,
listeners are the roots, and its one worked leak is a switched-out
object kept alive through a snapshot because it could in principle be
bitten again, fixed by logic that switches itself out or by `once()`
(blackheath-functional-reactive-programming, ch. 7, §7.4.1; ch. 8,
§8.1.1).

### The Rust prior art

gc-arena is the nearest design and in production. Its "mutation xor
collection" (kyren-gc-arena p. 2) is Bough's "collection between units,
never inside one", and it is `no_std` over `alloc` (gc-arena@v0.7.0
`src/lib.rs`:1–6, `src/arena.rs`:209–223). To hold a pointer outside a
mutation you stash it in a `DynamicRootSet` and get a handle whose drop
unroots it (`src/dynamic_roots.rs`:14–53, 134–140), which is Bough's
`Anchored`. Leptos and Sycamore hold `Copy` handles in a generational
slot map, free a node when the owner scope that made it re-runs or
drops, and panic when a disposed handle is used, naming where it was
defined in debug builds (leptos@v0.8.21
`reactive_graph/src/owner.rs`:34–46,
`reactive_graph/src/traits.rs`:66–90; sycamore-reactive@0.9.3
`packages/sycamore-reactive/src/node.rs`:72–121,
`packages/sycamore-reactive/src/signals.rs`:148–149, 190–201). That
makes `depends`'s missing inverse automatic, at the price Bough refused:
a node lives exactly as long as the scope that made it. carboxyl's
derived streams hold their parents strongly and are held weakly back, so
downstream owns upstream, which is the weak-reference scheme RFD 3
rejects (carboxyl@2a80080 `src/stream/mod.rs`:191–246). sodium-rust has
`depends` under the name `lambda1(f, deps)`.

### What the probes found

**A collection's cost, in transactions** (`rfd-0003-sweep-cost`). One
collection of the arena costs as much as this many one-screen
transactions, on the idle machine: 94 and 52 at 1,000 slots with 10% and
90% live, 957 and 563 at 10,000, and about 11,400 and 11,900 at 100,000.
Freeing dominates a mostly dead arena: the sweep is 9,370 of the 11,400
at 10% live.

**Garbage costs far more than collecting it** (`rfd-0005-demand-bounded-push`).
With 9,000 abandoned screens a navigation costs 14,000 times a clean one
until they are collected, and a collection costs 16,000. A mark that
flags dead nodes without sweeping still leaves 377 times; a census that
marks and prunes dependents without sweeping brings a transaction back to
1.0. On [F66](./2026-09-24-engine-feasibility-spike.md#f66)'s shape RFD 3's trigger collects about every second
navigation, so 9,000 screens pile up only under the manual policy.

**RFD 3's trigger needs a work term** (`rfd-0003-work-paced-trigger`).
The trigger collects when nodes allocated plus guards released exceed the
survivors. Beside a large live graph, the `app` shape with 430 screens
kept live, it collects once every 435 navigations, and a click's region
grows to 5,032 nodes against 25.5 clean. A per-input work term, the
growth of each transaction's region past its input's region at the last
collection, set against the survivors (`excess`), collects every 21
navigations. On the idle machine, against collecting after every
navigation:

| shape | RFD 3's trigger | `excess` |
|---|---|---|
| `app`, 3,900 units | 1.23 | 0.12 |
| `app`, worst pause | 2.99 | 1.09 |
| `nav`, 3,900 units | 1.12 | 1.23 |
| uneven inputs, garbage on frequent ones | 1.10 | 0.56 |
| uneven inputs, garbage on rare ones | 0.60 | 0.54 |

So the work term is worth about ten times on `app`, and costs about a
tenth on [F66](./2026-09-24-engine-feasibility-spike.md#f66)'s `nav` shape, where there's little garbage to pace. Its
fast path, a click on a clean arena, is unmeasurable (0.994). A term on
every region node, `total`, collects spuriously when regions are large
beside the live set, and costs 2.2 times on the same click, spurious
collections included.

- Under four inputs firing at uneven rates with live regions that grow,
  `excess` collects about as often as an oracle that paces on true dead
  work, 37 times against 34, for 0.7% more visits. It misses mostly
  garbage folded into an input's reference, and fires spuriously at most
  once every 270 quiet units, and not at all with short quiet stretches.
- Garbage on a slow input lags: `excess` misses 500 to 600 units, up
  to 300 in a row, peaking at about twice the survivors. A reference
  counting only region nodes born before the last collection (`marked`)
  misses none, for 0.3% more instructions.
- **No region term sees garbage a dropped guard releases.** A release
  never shrinks a region before the next collection, since released
  nodes stay in dependents lists until pruned. With guards dropped
  through a long quiet stretch and no growth, both terms missed 2,079
  units in a row, peaking at 11.1 times the survivors, and RFD 3's
  release term never fired: 90 releases against about 10,000 survivors.
  Total cost stayed at the oracle's, because that garbage sat on a slow
  input.

**The pause can be sliced** (`rfd-0003-incremental-mark`). On `app`, an
atomic collection's worst unit marks about 10,000 live nodes. An
incremental mark with Dijkstra insertion barriers, a fixed budget of k
mark-node equivalents a unit, and the prune and sweep sliced too, on the
idle machine against the atomic collection:

| pace | worst pause | total time |
|---|---|---|
| k = 4,000 | 0.27 | 1.007 |
| k = 1,000 | 0.12 | 1.16 |
| k = 500, floating garbage counted | 0.10 | 1.28 |
| k = 250 | 0.18 | 2.05 |
| k = 1,000, prune and sweep atomic | 0.44 | 1.13 |

Every barrier was needed, since switching one off let a reachable node
end white, and the barriers' slow path shaded nothing on this workload.
Pacing by debt lost to a fixed budget: allocation debt ran 2 cycles in
30,000 units, because clicks allocate nothing, and debt on the whole
region gave larger pauses at equal cost. With barriers compiled in and
collection atomic, a whole run costs 1.007 of the unbarriered arena.

**A lifetime brand makes [F62](./2026-09-24-engine-feasibility-spike.md#f62) a compile error on stable**
(`rfd-0003-branded-captures`, `rfd-0003-brand-erasure`). Tokens carry a
fresh `'g` per `Runtime::mutate`, and captures go through `.with(env)`.

- A forgotten capture, one through a helper, one through a switch and
  one through an inner all fail with E0521, "borrowed data escapes
  outside of closure" (outside of function, for the helper), and every
  legal fixture builds, including a hold of a struct of tokens, a
  construct capturing three, anchoring, the RFD 4 screens example and a
  switch among captured tokens. `map_to` of a token still builds, which
  is safe since [F94](./2026-09-24-engine-feasibility-spike.md#f94) made `map_to` trace its value.
- A brand on construct-minted tokens only, an era, catches one of the
  four. A nightly auto trait catches all four with a clear message, and
  refuses a capture of `dyn Fn` and of a generic `T`, so it spreads like
  `Send`.
- The brand is sound with no `unsafe`: values are stored at
  `'static` and restored to the current brand through a derivable
  `Rebrand` trait. A wrong impl can point a token at the wrong live node
  of the right type, silently, but can't forge, retype or carry a token
  across `mutate`. Re-run with lints uncapped so `forbid(unsafe_code)`
  was enforced, 0 of 92 rows changed.
- `RemoteIo` survives: `Anchored` is `Send + Sync + 'static`, and a
  queued transaction is a `for<'g>` closure.
- **It leaves a route out.** Capture an `Anchored` and reopen it inside
  the graph, and it builds and leaks. And a hand-written `Rebrand` or
  borrowed view can stash a `'static` token in a thread-local; the next
  use is a stale-token error, not unsafety. Bounds on the entry points
  refuse 4 of 6 stash routes. An `unsafe` seal on the view traits closes
  one more, and is exactly as strong as `forbid(unsafe_code)` itself.
- **It costs a copy per read and write of a token-bearing collection.**
  On the idle machine, per event through a listener: 1.0 for a scalar or
  a struct of tokens, 1.12 for a nested struct, 1.94 for a `Vec` of
  1,000 tokens. Per `accumulate_mut` event: 1.27 nested and 2.75 for the
  `Vec`, so a growing token-bearing accumulator brings back the
  quadratic cost RFD 4 added `accumulate_mut` to remove. A derived
  borrowed view costs 0.98 to 1.03 per event everywhere, but changes
  the API: a
  closure gets a view type, not `&A`, and gives up indexing, slices and
  most traits.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-sweep-cost-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-sweep-cost-wallclock
python3 scripts/ratios.py live10 live90
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0005-demand-bounded-push-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0005-demand-bounded-push-wallclock
python3 scripts/ratios.py nav app
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-work-paced-trigger-counts at experiments@408a6fe - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0003_work_paced_trigger::tests::counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-work-paced-trigger-counts-uneven at experiments@d881c42 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0003_work_paced_trigger::tests::uneven_counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-work-paced-trigger-counts-spurious-missed at experiments@000e929 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0003_work_paced_trigger::tests::spurious_missed_counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-work-paced-trigger-instructions-spurious-missed at experiments@000e929 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-work-paced-trigger-instructions -- '*::spurious_missed::*'
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-work-paced-trigger-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-work-paced-trigger-wallclock
python3 scripts/ratios.py nav app pause-nav pause-app uneven-spread uneven-sparse pause-uneven-spread pause-uneven-sparse uneven-lagging fast-path
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-incremental-mark-counts at experiments@3d83d68 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0003_incremental_mark::tests::counts -- --nocapture
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-incremental-mark-tests at experiments@3d83d68 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0003_incremental_mark::tests -- --nocapture --test-threads 1 --skip counts
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-incremental-mark-counts-extended at experiments@ac245d5 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo test --release --lib rfd_0003_incremental_mark::tests::extended_counts -- --nocapture --test-threads 1
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-incremental-mark-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-incremental-mark-wallclock
python3 scripts/ratios.py incremental-
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-29 - rfd-0003-incremental-mark-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-incremental-mark-wallclock
python3 scripts/ratios.py incremental-
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-branded-captures at experiments@754b931 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0003-branded-captures
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-brand-erasure at experiments@95010de - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0003-brand-erasure
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-brand-erasure at experiments@c8734b5 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0003-brand-erasure -- borrow
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-brand-erasure at experiments@b924d3f - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0003-brand-erasure -- uncapped
cargo run --release --bin rfd-0003-brand-erasure -- entry
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-rebrand-cost-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-rebrand-cost-wallclock
python3 scripts/ratios.py
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-rebrand-write-cost-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-rebrand-write-cost-wallclock
python3 scripts/ratios.py write_
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-incremental-mark-instructions at experiments@3d83d68 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-incremental-mark-instructions
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0003-rebrand-write-cost-instructions at experiments@2813ee0 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0003-rebrand-write-cost-instructions
```

Two results disagree with themselves and need a recheck. The incremental
mark's single-unit benches say the barriers' fast path costs 18% to 30%
of a unit, and 17% to 53% on a second day, while a whole run with barriers costs 0.7% and the instruction
counts say two instructions a click; a single-unit bench of under a
microsecond may be timing something else. And the `owned` way to write a
token-bearing value, which the instruction counts found constant-time,
costs 62 times a cast per update of a 1,000-element `Vec` on the idle
machine, so whatever made it constant-time under valgrind doesn't hold
there. Neither changes a leaning.

### Settled decisions the evidence contradicts

- **"An undeclared capture cannot be made a compile error without making
  tokens unusable as data."** It can, on stable, soundly and without
  `unsafe`, and tokens stay usable as data inside derived structs. What
  RFD 3 really trades is a lifetime on every token-holding type, I/O
  inside callbacks, a copy per read of token-bearing collections or a
  borrowed-view API in place of RFD 4's `&A`, and a stash route that only
  an `unsafe` seal narrows. The decision to use run-time `depends` may
  still be right. Its stated reason isn't.
- **The collection trigger.** RFD 3 says the trigger means "a graph that
  neither allocates nor drops a guard never pays". True, and beside a
  large live graph it lets garbage run at about ten times the cost of a
  trigger paced against work, and triples the worst pause. Its release
  term never fires when guards are dropped a few at a time.
- **"Counts cannot see cycles."** True of plain counts, incomplete as a
  reason: a counting collector with a backup trace sees them, and
  sodium-rust ships one. RFD 3's other reason, `Copy` tokens with no
  counts, is the one that carries.

Safe `Trace`, tracing from explicit roots, collection between units and
the rejection of weak references all stand.

### The options for Bough

For [F62](./2026-09-24-engine-feasibility-spike.md#f62):

1. Keep run-time `depends`, whose failure is a loud stale token.
2. Brand tokens with a lifetime, captures through `.with(env)`, values
   stored through a derived `Rebrand`, and borrowed views where a
   token-bearing collection is read or accumulated.
3. Scope lifetime to creation, as Leptos and Sycamore do. That gives
   `depends` an inverse and changes Sodium's semantics.

For [F63](./2026-09-24-engine-feasibility-spike.md#f63): nothing in the literature fixes it without 3. `once()`, which
releases its upstream after one event, and logic that switches itself
out are the book's two structural answers to the one case it shows, and
it warns that `once()` may not free anything in practice.

For the trigger:

1. Keep RFD 3's trigger.
2. Add the per-input work term, with the born-before-the-last-collection
   reference for lagging inputs, and find a release term that sees
   released garbage, which no probe has.
3. Also slice the mark, prune and sweep with a fixed budget, for hosts
   that care about the pause.

### Claude's leaning

For [F62](./2026-09-24-engine-feasibility-spike.md#f62), option 1, and rewrite the reason: the brand is possible and
costs more than the error it prevents. But the brand is the kind of
change RFD 6 says must be decided before signatures set, because it puts
a lifetime on every type that holds a token, so it has to be decided
before the real build, not after. For the trigger, option 2: the work
term costs nothing measurable on a clean click and is worth ten times
beside a large live graph. Leave slicing for when a host's frame budget
asks for it, with k near 1,000 to 4,000. Reword the refcount reason to
lead with `Copy` tokens.

### Questions to grill

- Would you put a lifetime on every token-holding type, and move I/O
  inside callbacks, to make a forgotten `depends` a compile error? If
  not now, then never, since retrofitting it touches every signature.
- Is [F63](./2026-09-24-engine-feasibility-spike.md#f63) a bug to prevent, or an explicit leak the program asked for,
  which the library should only make visible?
- Should `once()`-style release, a primitive that lets go of its
  upstream, sit beside `depends` as a way to end a capture?
- Does the work term go into RFD 3's trigger now, and what is the
  release term that sees garbage a dropped guard leaves?
- How often does collection run in real programs, every unit or on a
  trigger, and who chooses the incremental budget?
- Is `Copy` tokens the real reason counting lost, and should RFD 3 lead
  with it?

### Experiments this proposes for Bough

- Port Oort's fighter or bough-gtk's list view to a branded token API on
  a branch, and count the lifetimes, `.with` calls and callback moves it
  takes. That's the cost side of option 2 on real code.
- Log, per collection in those programs, the survivors, the nodes freed,
  and the dead work since the last one, to see how far RFD 3's trigger
  drifts from work in practice.
- Try a release term that counts every region node after a release until
  the next collection, the one fix for released garbage no probe built.

### Reading path

- goregaokar-a-tour-of-safe-tracing-gc-designs-in first; it summarizes
  the Rust designs. Needs lifetimes and a little `Pin`.
- kyren-gc-arena, then gc-arena's `src/collect.rs`, `src/gc.rs`:88–90 and
  `src/static_wrapper.rs`. Needs generativity, invariant lifetime brands.
- bahr-modal-frp-for-all §§1–3 for the capture rule; §4 needs natural
  deduction and big-step semantics, and §5 step-indexed Kripke logical
  relations.
- bahr-simply-ratt-a-fitch-style-modal-calculus-for after
  krishnaswami-higher-order-functional-reactive-programming-without-spacetime-leaks
  §§1–3.
- bacon-a-unified-theory-of-garbage-collection §§1–6. Needs mark-sweep,
  counting and generational collection at textbook level.
- jeffrey-josephine-using-javascript-to-safely-manage-the-lifetimes for
  the two failure modes. Self-contained given Rust lifetimes.

## Values and ownership (RFD 4)

### What the literature says

**"Linear" is the wrong word for Bough's streams.** Linear means consumed
exactly once, affine at most once
(bernardy-linear-haskell-practical-linearity-in-a-higher-order p. 2).
Rust's ownership is a uniqueness system: it sits with Clean among the
uniqueness languages, not the linear ones (p. 23;
marshall-linearity-and-uniqueness pp. 1, 6). The two coincide only when
every value is substructural (p. 4), and Bough has unrestricted values,
`Shared<A>`. Linearity restricts the future: an unrestricted value can
become linear, never the reverse. Uniqueness guarantees the past: a
unique value can become shared, never the reverse (marshall-… pp. 5–8).
Bough's `share` is Marshall's `borrow`, unique to unrestricted and
one-way (p. 11), and what lets `hold` move an event out without `Clone`
is that no one else can read it, the guarantee that licenses in-place
update (p. 6). A `Stream<A>` can be dropped unconsumed, so RFD 4's
"exactly one consumer" is at most one. The industrial case for the rule
is Linear Haskell's: handing one first-class stream to several consumers
is a bug "we have seen … several times" (bernardy-… pp. 26–27). That
needs only no duplication, not an obligation to consume. Kiselyov's
*linear* stream means one element per step of state
(kiselyov-stream-fusion-to-completeness p. 8), a third meaning.

**Fusion works, and its cost is code.** Stream fusion makes every step
non-recursive and lets the optimizer inline the consumer's loop, the
mechanism of RFD 4's chains (coutts-stream-fusion-from-lists-to-streams-to-nothing
pp. 2–4). Its price is duplication: code grew 2.5% on single-module
programs, 11% on multi-module and more than 25% for one program in
twenty (p. 9; not reproduced), and the authors call relying on the
optimizer fragile (p. 9). Staging fuses everything but zipping two nested
streams (kiselyov-… pp. 10–11, Thm. 1), and its critique of trusting a
general-purpose compiler is the risk Bough takes by fusing through
monomorphization (p. 13). Bough's adapters are all per-event functions of
at most one event, the easy fragment; the hard cases, zip and nested
`flat_map`, are materializers in Bough. Causal commutative arrows
normalize any switch-free chain to one loop over one pure function and
one state, for 4.1 to 13.9 times over GHC's arrow translation
(liu-causal-commutative-arrows-and-their-optimization pp. 5–6, 8; not
reproduced). No source measures compile time, which is [F36](./2026-09-24-engine-feasibility-spike.md#f36)'s problem, and
none bounds the number of instantiations. Lustre's modular compilation
keeps generated code "linear in the size of the source program" because a
node compiles once whatever its context
(biernacki-clock-directed-modular-code-generation-for-synchronous-data
p. 9). FrTime's lowering, a source rewrite that collapses lifted
subexpressions into plain calls, gave up to 16,000 times on a
microbenchmark and a slowdown on a program already written for it
(cooper-integrating-dataflow-evaluation-into-a-practical-higher-order
pp. 78–79; not reproduced). Building the graph first and then collapsing
nodes is its proposed extension (p. 81).

**A cell of a collection is the `Replace` change structure.** Cai et al.
give every value a change set, an update ⊕ and a difference ⊖, and allow
the fallback change `Replace v` (cai-a-theory-of-changes-for-higher-order-languages
pp. 2, 9). Bough's `hold` is integration where every change is `Replace`,
and `steps` is differentiation in that structure. DBSP's inversion
theorem, I(D(s)) = D(I(s)) = s
(budiu-dbsp-automatic-incremental-view-maintenance-for-rich-query p. 4),
is `hold(x, steps(c)) = c` and `steps(hold(x, e)) = e`. With `Replace`, a
lifted function's derivative is "recompute", which is exactly why a cell
of a collection propagates *that* it changed and not *what*. Maier and
Odersky's abstract names the same problem
(maier-higher-order-reactive-programming-with-incremental-lists p. 1).

**An incremental collection is the same pair over a richer structure.**

- Over an abelian group, a delta stream integrated gives the collection,
  and the incremental version of any operator Q is D ∘ Q ∘ I, composed by
  the chain rule (budiu-dbsp-… p. 4, Prop. 3.2). Filter, projection and
  grouping are linear, their own incremental versions, and store
  nothing; count and sum are linear only as scalar outputs, and keep a
  per-key total when grouped; join is bilinear and needs both
  integrals; `distinct` needs one; min and max need the whole input
  (pp. 4, 6–7, 10; mcsherry-differential-dataflow pp. 7–8).
- Z-sets, weighted elements with negative weights for removal, make
  keyed data a group (budiu-dbsp-… pp. 4–5).
- The group doesn't fit ordered collections: finding one is "not
  obvious" for sorted or tree-shaped data (budiu-dbsp-… p. 12). Maier's
  reactive sequences carry Ins and Rem atoms under non-commutative
  concatenation, with `map` elementwise, `++` translating indices,
  `foldUndo` for associative, commutative folds with an undo, and
  `aggregate` over a balanced concat tree of cached partials
  (maier-higher-order-reactive-programming-with-incremental-lists
  pp. 6, 8, 11–15). They create one dependent per segment, not per
  element, to keep the graph small (pp. 16–17). On the JVM `foldUndo`
  won from about n = 15, and `map` from about 30 for a cheap function
  and from 3 for an expensive one (pp. 20–21; not reproduced). Pulses
  form a monoid and values a module over it
  (maier-reactive-programming-abstractions-for-complex-event-logic-and
  pp. 78–79).
- A derivative is cheap only if it needs the change and not the base
  value: *self-maintainability* (cai-… p. 8).
- A structure is cheap to update only if its trace barely moves under the
  change. "Any deterministic method for building the tree based on just
  list position is not going to be stable—a single insert can change
  everyone's position" (acar-self-adjusting-computation p. 95). Stable
  structure is keyed by content with fixed randomness (pp. 84, 96–100,
  234).
- Flo's eager-execution law, input in pieces reaches the same state as
  input all at once, is the correctness test for composing patches
  (laddad-flo-a-semantic-foundation-for-progressive-stream-processing
  p. 9).
- A late-built operator starts from the whole current value as one change
  (budiu-dbsp-… p. 7).
- Reflex ships the idea as a type: `Incremental` with a `Patch` class and
  patch-folding accumulators (reflex-reflex-class pp. 2, 4, 22).

The Sodium book sees the problem and has no incremental answer. A naive
merge over N streams is a line of N − 1 nodes, and its fixes are
balanced trees and building "switches into the tree"
(blackheath-functional-reactive-programming, ch. 7, §§7.6–7.7; ch. 8,
§8.6).

### The Rust prior art

futures-signals pairs a latest-value cell, which "might skip changes",
with a `SignalVec` of `VecDiff`s that "will never skip a change"
(docs.rs/futures-signals/0.3.34). That is a cell of a collection plus a
stream of its diffs, `steps` with a richer payload. Sycamore's
`map_keyed` diffs whole collections by key after Solid's algorithm, each
item mapped in its own child scope
(sycamore-reactive@0.9.3 `packages/sycamore-reactive/src/iter.rs`:9–64),
and Leptos's `reactive_stores` tracks nested fields with keyed `Patch`
(docs.rs/reactive_stores/0.4.4). differential-dataflow and DBSP are
Z-set collections in Rust (docs.rs/differential-dataflow/0.25.1;
github.com/feldera/feldera @2ad179e `crates/dbsp`). DFIR claims
"extremely low-latency execution via Rust monomorphization", the same
bet as RFD 4's fusion (hydro-dfir p. 1), and avoids per-node
construction by generating each tick as one function from a macro
(hydro@dfir_rs-v0.16.0 `dfir_lang/src/graph/meta_graph.rs`:813–816).
Sycamore allocates a slot with four `Vec`s, a `SmallVec`, a boxed
callback and a boxed value per node (sycamore-reactive@0.9.3
`packages/sycamore-reactive/src/node.rs`:14–43); no crate publishes a
per-node construction cost to set beside Oort's.

### What the probes found

**Erasing the chain at the materializer removes most of [F36](./2026-09-24-engine-feasibility-spike.md#f36)**
(`rfd-0004-erased-materializer`). The probe generates [F36](./2026-09-24-engine-feasibility-spike.md#f36)'s chain shapes
from data, 182 chain types at depth two and 1,640 at depth three, the
spike's numbers, and builds each crate from clean three times.

| design | release build, depth 2 | depth 3 | per event |
|---|---|---|---|
| boxed `dyn FnMut` at the materializer | 0.41 | 0.37 | 1.022 |
| state struct stepped through a `fn` pointer | 0.33 | 0.29 | 1.028 |
| normalized flat node, CCA-style | 1.04 | 1.04 | 0.981 |

Ratios are to monomorphized materializers, 10.4 s and 100.7 s to build,
35.6 ns an event, on the idle machine. Erasure compiles 7 node evaluation
functions where the baseline compiles 910 and 8,200, and the depth-three
binary shrinks from 18.7 MiB to 11.5 boxed and 7.4 through `fn`
pointers. The flat node removes nothing, since each closure is still its
own type. Erasure doesn't stop growth with the number of chain types:
the adapters are still compiled per chain, and erased builds grow 8.3 to
8.7 times from depth two to three against the baseline's 9.7. The `fn`
pointer design uses a little `unsafe`, and Bough's core is
`forbid(unsafe_code)`, so boxed is the usable one.

**A patch-carrying cell wins from small sizes, and the structure behind
it matters more than the patches** (`rfd-0004-patch-cell-crossover`). The
baseline is RFD 4's cell of the collection, an in-place accumulator with
read-through derived cells. On the idle machine:

- A `Vec` with `map` then `sum`, one insert or remove per instant, read
  every instant: a flat `Vec` carrying positional deltas costs 0.33 to
  0.67 of the baseline at every size, but only because both are linear
  in n. A counted B-tree holding source and mapped values together costs
  0.71 at 3 elements, 0.08 at 1,000 and under 0.001 at a million.
- The same read every 16th instant: the flat delta loses at every size,
  1.03 at 3 elements and 1.6 to 2.3 from 10,000 up, so the large-`Vec`
  rows that looked like valgrind artefacts in the instruction counts are
  real. The shared B-tree wins from 1,000 elements (0.36). A chunked rope
  wins from 1,000 too, but loses to the shared B-tree wherever it wins,
  and to the plain B-tree from 10,000.
- Appends at the end: the flat `Vec` delta is best or tied at every
  size, and the shared B-tree close behind; in one of four runs the
  B-tree edged it at 10 elements.
- A `HashMap` with filter then count, upserts as Z-sets: an eager delta
  whose upsert is one insert on the source, the old value its retraction
  (`fused`), costs 0.53 of the baseline at 3 entries and 0.22 at 10, read
  every instant. Read every 16th instant it crosses between 10 (1.31) and
  30 entries (0.75). A fully lazy map that buffers raw upserts until a
  read wins or ties at every size on rare reads, 0.83 at 3 entries; its
  rows move with the hash seed, by up to 8% at 3 entries. The plain
  eager Z-set delta, built from separate retract and insert steps, costs
  about twice the fused one, so fusion, not laziness, carries the map
  result.
- Consolidating k Z-sets in one instant costs 4.4 times concatenating k
  commands at k = 2 and 75 times at k = 64: it sorts.
- **Z-set composition fails for keyed maps.** Two sources upserting one
  key in one instant, each against the state before it, compose into
  weight −2 on the old value and +1 on each new one, which isn't a map.
  Keyed collections need a combining function again, as `merge` does, and
  positional patches from two sources need index translation.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0004-erased-materializer at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0004-erased-materializer --
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0004-erased-materializer-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0004-erased-materializer-wallclock
python3 scripts/ratios.py
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0004-patch-cell-crossover-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0004-patch-cell-crossover-wallclock
python3 scripts/ratios.py vec- map- compose
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-29 - rfd-0004-patch-cell-crossover-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0004-patch-cell-crossover-wallclock
python3 scripts/ratios.py vec- map- compose
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-29 - rfd-0004-patch-cell-crossover-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0004-patch-cell-crossover-wallclock
python3 scripts/ratios.py vec- map- compose
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-29 - rfd-0004-patch-cell-crossover-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0004-patch-cell-crossover-wallclock
python3 scripts/ratios.py vec- map- compose
```

The three second-day runs are
`results/rfd-0004-patch-cell-crossover-wallclock-run1-2026-09-29.txt` to
`-run3-`, one process each, so each has its own hash seed.

The composition failure is a test in the probe's module, not a result
file; at `experiments@daa6419`:

```
cargo test --release --lib rfd_0004_patch_cell_crossover::tests::same_key_conflict
```

### Settled decisions the evidence contradicts

None found. "Linear" is a naming problem, not a broken reason: what
`hold` and `merge` need is that no second consumer exists, which
uniqueness gives. Fusion by monomorphization is supported, and its known
cost is the one [F36](./2026-09-24-engine-feasibility-spike.md#f36) found. Lazy read-through cells stand: pending deltas
sum, so laziness survives even an incremental cell.

### The options for Bough

On the word: keep "linear", or say "move-only" and "at most one
consumer", with one line in the glossary on why it isn't linear.

On [F36](./2026-09-24-engine-feasibility-spike.md#f36):

1. Keep full monomorphization and bound chain depth where programs build
   chains from data, as RFD 4 has it.
2. Erase at the materializer boundary with a boxed closure, one indirect
   call per chain per event, and keep monomorphization for the chain
   itself.
3. Offer both, erased by default.

On open question 9:

1. Cells of collections only, and the usual advice.
2. A patch-carrying cell in core, `holdPatch(init, Stream<P>)` with
   `P` a change structure: ⊕, a nil change, composition within an instant
   tested by Flo's law. Keyed collections on Z-sets with a combining
   function for same-key conflicts, positional ones on a counted B-tree,
   in a library.
3. Incremental collections in core.
4. Interoperate with DBSP's crate instead of building a library.

### Claude's leaning

Say "move-only, at most one consumer", and keep the word "linear" out of
the docs. For [F36](./2026-09-24-engine-feasibility-spike.md#f36), option 2: about two-fifths of the build time for
about 2% an event, in safe code, and full monomorphization stays
available for programs that don't build chains from data. That leaning
rests on a generated program, not a real one. For question 9, option 2.
The contract should be Cai's change structure, not an abelian group, so
ordered deltas fit and same-key conflicts get a function; the library's
structures should be counted B-trees and content-keyed partitions, since
the probe found the data structure worth more than the patches, and the
eager fused upsert is the map operator to start from.

### Questions to grill

- Do you mean "exactly one consumer" or "at most one"? Should dropping an
  unconsumed `Stream` warn?
- Has any real program, not the data-driven test binary, hit [F36](./2026-09-24-engine-feasibility-spike.md#f36)?
- Would one indirect call per chain per event be acceptable to compile
  every materializer once?
- Should the patch cell's contract require an abelian group, which gives
  commutative merging and DBSP's free operators, or stay at Cai's change
  structure so ordered deltas and keyed conflicts fit?
- Is "`hold` and `steps` are integrate and differentiate over `Replace`"
  a framing you want in RFD 4, given it makes a cell of a collection a
  special case of an incremental one?
- Should an incremental-collection library live in the Bough workspace,
  or should Bough interoperate with DBSP?

### Experiments this proposes for Bough

- Build bough-gtk's list view on a patch-carrying cell over a counted
  B-tree, beside the cell-of-`Vec` version, and time a scroll and an
  insert at the list sizes it really has.
- Measure release build time for Oort's fighter with full
  monomorphization and with boxed materializers, to see whether [F36](./2026-09-24-engine-feasibility-spike.md#f36) bites
  a real program at all.

### Reading path

- marshall-linearity-and-uniqueness §§1–3 for the vocabulary. Needs
  substructural type systems at the level of "linear, affine, unique".
- coutts-stream-fusion-from-lists-to-streams-to-nothing §§2–5, then
  kiselyov-stream-fusion-to-completeness §3. §§4–6 of Kiselyov need
  multi-stage programming.
- budiu-dbsp-automatic-incremental-view-maintenance-for-rich-query
  §§2–4. Self-contained given abelian groups.
- cai-a-theory-of-changes-for-higher-order-languages §§2 and 4 for change
  structures and self-maintainability.
- maier-higher-order-reactive-programming-with-incremental-lists, after
  maier-deprecating-the-observer-pattern-with-scala-react for levels.
  Needs balanced binary trees and monoids.
- acar-self-adjusting-computation Parts II and III for trace stability.
  Needs randomized analysis, skip lists and treaps.

## Concurrency and the I/O edge (RFD 6)

### What the literature says

A word first. Lee's and Drechsler's "transactions" are the database
sense, speculative and abortable (lee-the-problem-with-threads p. 11),
though Drechsler's are abort-free
(drechsler-thread-safe-reactive-programming p. 11). Bough's is one
logical instant, never aborted. Below, "transaction" means Bough's.

**Most glitch-free systems run one propagation at a time.** Scala.React
and Distributed REScala take a global lock
(drechsler-thread-safe-reactive-programming p. 2), and REScala and
Flapjax forbid concurrent propagation. Combining concurrent propagation
with glitch freedom was "an open research problem" in 2018
(margara-on-the-semantics-of-distributed-reactive-programming p. 19).
Céu reacts to an event completely before handling the next, the
environment can't interrupt a reaction, and inputs queue for later
reactions (santanna-structured-synchronous-reactive-programming-with-ceu
p. 2). FrTime's engine thread drains a message queue at the start of each
cycle, which is Bough's pump (cooper-embedding-dynamic-dataflow-in-a-call-by-value
p. 9). Scala.React isolates independent graphs in *domains* that run
concurrently and talk asynchronously
(maier-reactive-programming-abstractions-for-complex-event-logic-and
pp. 33–34), which is Bough's handles between runtimes.

**The cost of making propagation concurrent is measured once.** MV-RP
makes REScala thread-safe with abort-free strict serializability, using
conservative two-phase locking, multiversion reads and retrofitting of
dynamic edges (drechsler-thread-safe-reactive-programming pp. 12–15,
Thm. 1). Single-threaded it costs 20% to 25% against a global lock, and
55% for an STM scheduler (pp. 21–23; not reproduced). Under extreme
contention with updates of about 6.5 µs it never beats the global lock.
Under high contention, once the bottleneck is removed, it beats the lock
from three threads even with cheap updates, and it scales further with
about 160 µs of work per update or low contention (pp. 19, 21–23; not
reproduced). Bough's units are far cheaper than 6.5 µs, so under extreme
contention Bough sits further into the region where concurrent
propagation loses. The same paper says an uncontended global
lock is negligible single-threaded (p. 21), but that's asserted, not
measured: its single-threaded global-lock run is its own baseline. It
also names what goes wrong without care: two threads' changes absorbed
into one reevaluation make an Event skip a value (pp. 8–9). Scala.Rx and
QUARP do that by design and so support only Signals, since "randomly
skipping some values is not usable for Events" (p. 2).

**No source supports "threading costs overhead" for Bough.** Ousterhout's
slides assert it, "Events faster than threads on single CPU: No locking
overheads. No context switching", with no data
(ousterhout-why-threads-are-a-bad-idea-for-most p. 7). Lustre and Quartz
assert that fine-grained concurrency is inefficient and single-threaded
code gets exact WCET, without measuring
(halbwachs-the-synchronous-data-flow-programming-language-lustre p. 32;
schneider-causality-analysis-of-synchronous-programs-with-delayed-actions
pp. 1, 9). Elm's JavaScript backend couldn't use Web Workers because their
overhead was too high, with no numbers
(czaplicki-asynchronous-functional-reactive-programming-for-guis p. 10).
And the Sodium book's Ousterhout passage argues *for* threads. It quotes
"Unless we need true CPU concurrency, events are better", then argues
that in the multicore age "threads are no longer optional" and "shared
mutable state is the real culprit"
(blackheath-functional-reactive-programming, App. B, §B.4). Sodium's
`send()` is "absolutely thread-safe" from any context (ch. 8, §8.1.1).

**What the sources do support.** Determinism by deterministic means:
"deterministic ends should be accomplished with deterministic means",
with nondeterminism explicit and only where it's needed
(lee-the-problem-with-threads p. 17). Lee's model is Kahn networks,
deterministic processes joined by queues, with an explicit
nondeterministic merge where one is wanted (p. 13). In Bough that merge
is the handle queue: which thread's call lands first. And listeners
outside locks: "Callbacks don't work with locks"
(ousterhout-… p. 4), and Lee's observer-pattern example, where locks
around notification deadlock and notification outside the lock reorders
values (lee-… pp. 8–9). The Sodium book's own rules are about listeners:
no `send()` inside a callback, since "we can't maintain correct processing
order", and a worker thread's result goes back as a new transaction
(blackheath-functional-reactive-programming, ch. 8, §8.1.4; ch. 11,
§11.1.2). The book names the cost Bough pays too: a hop through another
thread makes a transition non-atomic, so an intermediate state is
observable (ch. 14, §14.3.1).

**Half of the determinism argument is kept by serializable concurrency
too.** The half is "a transaction is a pure
function of its inputs", which RFD 2 gives for the synchronous
re-entrancy check, not for the single thread. RFD 6 states no
determinism or overhead reason, only that the host owns the schedule.
MV-RP's histories are equivalent to a serial run of the same
transactions (drechsler-thread-safe-reactive-programming pp. 10–11, 15),
so each still computes what it would alone. What concurrency gives up is
that the order of units is fixed in one place before they run. In Bough
the order is the queue's at the pump; under MV-RP it's decided as
transactions race (p. 14).

**Simultaneity at the edge.** In every reactive system in the batch the
caller decides what's simultaneous: Distributed REScala's admitting
thread changes a set of sources in one turn
(drechsler-distributed-rescala-an-update-algorithm-for-distributed-reactive
pp. 3, 7), and REScala's `update(i1 -> v1, i2 -> v2)` is one transaction
while every other call is its own (drechsler-thread-safe-reactive-programming
pp. 7, 16). None merges independent callers, and one calls the merge a
bug. Async RaTT takes one input on one channel per step, and the run
time schedules the order (bahr-asynchronous-modal-frp pp. 3, 15–16).
Rhine says events are simultaneous only on the same clock, a schedule
must choose an order when ticks coincide, and resampling buffers are
"fundamentally asynchronous: input and output never happen
simultaneously" (barenz-rhine-frp-with-type-level-clocks pp. 6–8). In
Rhine's words, an input slot is a resampling buffer from the interrupt
clock to the pump clock, and the pump's order is a schedule. FRPNow goes
the other way, putting every event that completes between rounds into
the next round (vanderploeg-practical-principled-frp pp. 10–11), and
Scala.React coalesces pending edits into one turn, last wins, because a
turn per edit lags when edits outpace propagation
(maier-reactive-programming-abstractions-for-complex-event-logic-and
pp. 35, 42). The book lets several sends to different sinks share an
explicit transaction (blackheath-functional-reactive-programming, ch. 8,
§8.1.2); Bough's "two slots are never simultaneous" narrows that.

**Where Bough sits.** In Margara and Salvaneschi's levels, one runtime
is atomic, the top one: one unit at a time gives complete glitch freedom,
and every read goes through the `Runtime` between units
(margara-… p. 5). Their measured costs of the higher levels, 20.6 ms
against 33.8 ms and 40.4 ms average latency in simulation, are all lock
and message traffic across processes (p. 13; not reproduced), which a
single thread doesn't pay. Across runtimes it's different: connecting
glitch-free networks by observer notifications "would not result in an
overall glitch free system"
(drechsler-distributed-rescala-… p. 4). Two Bough runtimes joined by a
`RemoteIo` give each other FIFO per link and nothing more.

### The Rust prior art

Every Rust design that runs FRP-like propagation keeps one logical
writer per step, and uses threads by serialising, by snapshot and cancel,
or by sharding, never by propagating one transaction on several threads.

- carboxyl takes one global `static` `Mutex` around every transaction,
  and its `send_async` spawns a thread per send and voids ordering
  between sends (carboxyl@2a80080 `src/transaction.rs`:11–77,
  `src/stream/mod.rs`:43–100).
- Leptos makes every node `Send + Sync` behind `RwLock`s, with a
  lock-order rule, a comment that a value write "Can block endlessly if
  the user is has a ReadGuard on the value", and per-thread bookkeeping
  so parallel effect runs don't both subscribe
  (leptos@v0.8.21 `reactive_graph/src/computed/inner.rs`:14–24,
  147–151; `reactive_graph/src/effect/immediate.rs`:208–251).
- salsa runs parallel readers of one revision and a single writer who
  sets a cancellation flag and blocks until the readers finish, which
  "could deadlock if there is a single worker with two handles"
  (salsa@salsa-v0.28.5 `src/storage.rs`:152–165).
- DFIR spawns its tasks local to the thread running the instance
  (hydro@dfir_rs-v0.16.0 `dfir_rs/src/scheduled/context.rs`:407–415).
- timely and DBSP shard data across workers, each running the whole
  circuit (docs.rs/timely/0.31.0; github.com/feldera/feldera @2ad179e
  `crates/dbsp/src/circuit/runtime.rs`:1–2).
- sodium-rust wraps everything in `Arc` and `Mutex`, with `unsafe impl
  Send/Sync` over a `Cell` colour (github.com/SodiumFRP/sodium-rust
  @3e93021 `src/impl_/gc_node.rs`:52–59).

### What the probes found

`rfd-0006-lock-vs-queue-cost` times a unit of about 500 ns, a 50-node
flat propagation, run five ways: on the owner thread; behind an
uncontended `Mutex`; behind one contended by 2, 4 and 8 threads; and
through RFD 6's queue and pump, boxed on the sender with a wake flag. On
the idle machine, against the owner thread:

| | one unit | a burst of 64 |
|---|---|---|
| uncontended `Mutex` | 1.047 | 1.009 |
| RFD 6's queue | 1.145 | 1.115 |

| threads | contended `Mutex` | queue with that many producers |
|---|---|---|
| 2 | 1.73 | 1.31 |
| 4 | 1.92 | 1.45 |
| 8 | 2.07 | 1.60 |

In instructions, the uncontended lock adds 39 and 18 a unit to about
2,200, and the queue 299 and 419.

- The lock's latency is worse than its throughput. At 2 threads the p99
  wait to acquire is 18 to 20 µs and the p99.9 40 to 58 µs; at 8, 40 to
  42 µs and 61 to 65 µs, over two days' runs. The tails are single
  draws: the longest wait was 165 µs in one run and 224 µs in the other,
  and one thread ran 11,087 units in a row in one and 451 in the other,
  since std's mutex is unfair ([F78](./2026-09-24-engine-feasibility-spike.md#f78)). The queue's p99 send is 1.5 to 1.9
  µs at 2 producers and 17 to 18 µs at 8.
- **The contended lock's extra cost is mostly a futex wake per unlock,
  not the graph's state moving between cores.** Grown to 256 KiB of state
  per unit, the lock changes threads in about 1% of units, yet a copy of
  std's mutex still makes about one `futex_wake` call a unit, and std's
  workers sleep about as often. The counts depend on scheduling: 0.73 to
  0.97 wakes and 0.78 to 0.94 sleeps in the recorded run, 0.85 to 0.95
  and 0.70 to 0.97 when verification re-ran it. The queue's extra time stays
  at roughly 60 to 240 ns as the state grows, so its ratio falls to 1.01
  to 1.02 at 256 KiB.
- **A wake across the chip's two core complexes costs more.** Pinned
  within one complex, the lock costs 1.12 at 256 KiB with 2 threads;
  split across both, 1.38. The timed run puts a cross-complex wake at
  about 1.9 µs against 0.9 within one, which accounts for most of the
  gap. Those per-call times come from the timed binary, the best of three
  runs each, on the idle machine; the bench's single run gives 1.65 µs
  against 0.92, and 1.87 against 0.96 on a second day; its "INDICATIVE" label is fixed text from before the
  idle run.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0006-lock-vs-queue-cost-instructions at experiments@d16fe99 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0006-lock-vs-queue-cost-instructions
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0006-lock-vs-queue-cost-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0006-lock-vs-queue-cost-wallclock
python3 scripts/ratios.py single contended footprint-
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-29 - rfd-0006-lock-vs-queue-cost-wallclock at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo bench --bench rfd-0006-lock-vs-queue-cost-wallclock
python3 scripts/ratios.py single contended footprint-
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0006-lock-vs-queue-cost at experiments@44fad84 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0006-lock-vs-queue-cost
```

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0006-lock-vs-queue-cost at experiments@daa6419 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0006-lock-vs-queue-cost -- --timed
```

### Settled decisions the evidence contradicts

**The single thread's overhead reason.** The no-std handoff's claim that
threading costs overhead has no source, and in Rust an uncontended
`Mutex` around the engine costs 1% to 5% a unit, while RFD 6's own queue
costs 11% to 15%. So overhead is no argument against a `Mutex`-wrapped
engine callable from any thread. Under contention the lock does lose
more than the queue, 1.7 to 2.1 against 1.3 to 1.6, and its tail waits
are tens of microseconds, but that's a latency argument, not the
overhead one.

The decision itself stands on other reasons the sources support:
listeners never run under a lock, the order of units is one explicit
sequence the host can see, and the host owns the schedule. RFD 6 already
rejects Sodium Java's run-at-once model on the schedule, not on cost,
which is the right ground. Atomic visibility without aborts is
supported: MV-RP is abort-free for the same reason Bough is, side effects
that can't be undone (drechsler-thread-safe-reactive-programming pp. 2,
9), and Margara rejects optimistic protocols on the same ground (p. 19).

### The options for Bough

1. Keep RFD 6 and give it reasons: simple, one host-visible order of
   units, the host owns the schedule, listeners never under a lock. Drop
   the no-std handoff's overhead reason, and don't lean on RFD 2's "a
   transaction is a pure function of its inputs", which is true but not
   bought by the single thread.
2. Also allow a `Mutex`-wrapped runtime as a third way in, for callers
   who want to run a unit now from another thread and accept listeners
   running on that thread.
3. Also record the order units reach the queue, so a run can be
   replayed.

### Claude's leaning

Option 1. The engine stays single-threaded; the reasons change. Say in
RFD 6 that the order in which units from different threads reach the
queue is the one nondeterministic merge, in Lee's sense, and that
everything after the pump is deterministic. Use Rhine's words for input
slots and the pump if they help. Option 2 is cheap in throughput and
brings back the listener problem the queue exists to avoid. Option 3
belongs to verification; see there.

### Questions to grill

- Is the single thread's determinism argument about the order of units
  being one explicit sequence, rather than RFD 2's transaction being a
  pure function of its inputs, which serializable concurrency also
  keeps?
- Should Bough drop the no-std handoff's overhead argument, given an
  uncontended lock costs less than the queue RFD 6 chose?
- Is losing Sodium's explicit multi-send transaction across several
  slots deliberate, and does RFD 7 say so?
- If two runtimes are ever wired together through handles, do we promise
  only FIFO per link, and say so?
- Should the order units reach the queue be observable or recordable?

### Experiments this proposes for Bough

- Time bough-gtk and the chat room with the real engine behind the queue,
  to see what share of a unit the queue's 11% to 15% is once real
  listeners and payloads run.
- Measure pump latency, send to listener, under a tokio driver at 2, 4
  and 8 producer tasks, the number that matters more to a UI than
  throughput.

### Reading path

- lee-the-problem-with-threads. Self-contained; §6 is easier with a
  picture of Kahn process networks.
- ousterhout-why-threads-are-a-bad-idea-for-most, then
  vonbehren-why-events-are-a-bad-idea-for-high for the rebuttal, which
  concerns independent server requests and matters little to the engine.
- drechsler-thread-safe-reactive-programming. Needs serializability,
  two-phase locking and MVCC at database-textbook level.
- margara-on-the-semantics-of-distributed-reactive-programming for the
  levels. Needs vector clocks and FIFO, causal and sequential
  consistency.
- barenz-rhine-frp-with-type-level-clocks §§3–5 for clocks, schedules and
  resampling buffers. Needs Haskell type families.

## Embedded and bounded (RFD 7)

### What the literature says

**Every system with a proven or stated bound either compiles a static
graph or bounds creation up front.**
E-FRP compiles each event to one interrupt handler of two assignment
phases, with a fixed number of variables, no loops and no allocation, and
gives up switching and higher order entirely, "a core, first-order
subset" (wan-event-driven-frp pp. 2, 5, 9, 16). Emfrp fixes the graph at
compile time, forbids recursive types and functions, has no closures,
and allocates memory statically
(sawada-emfrp-a-functional-reactive-programming-language-for-small
pp. 2–3, 6–7). Copilot reaches constant space by forbidding anonymous
streams, so each history array's length is computed statically
(pike-copilot-a-hard-real-time-runtime-monitor pp. 6, 10). Lustre's
modular compiler gives each node a state struct and `step` and `reset`
methods, with memory "essentially a tree structure" and no dynamic
allocation (biernacki-clock-directed-modular-code-generation-for-synchronous-data
pp. 5, 7–8), and a static engine grows into an optimising compiler, with
allocation by interference-graph colouring and in-place array updates
checked by a type system
(gerard-a-modular-memory-optimization-for-synchronous-data-flow
pp. 3–6). RT-FRP is the one bounded FRP that keeps switching, and its
bound works because `until` *replaces* the running term with a
continuation already counted: the old mode is gone
(wan-real-time-frp pp. 5, 8–9). That's the opposite of Bough's
deselected inners. The one dynamic-graph language, Juniper, uses
reference counts because "a tracing garbage collector has unacceptable
overhead" on 2 KB, leaks cycles, and can't bound memory while it has
references, closures and recursion
(helbling-juniper-a-functional-reactive-programming-language-for-the
p. 7). That sentence about tracing is asserted, not measured.

**Bounding creation.** Four answers appear:

1. RT-FRP's: switch only among templates fixed in the source and discard
   the old mode, so the bound is the largest template
   (wan-real-time-frp pp. 5, 9).
2. Céu's: a lexically scoped pool that spawns name, with an optional
   declared size, `pool Unit[10]`, statically preallocated when sized,
   where "further spawn invocations fail" when it's full. It gets away
   without a collector because every lifetime is lexical
   (santanna-structured-synchronous-reactive-programming-with-ceu pp. 5,
   10–11).
3. Oeyen et al.'s: allow creation from a finite, known set of reactors
   and bound it by flow analysis (oeyen-reactive-programming-without-functions
   p. 14). By their scale, with *strongly*, *eventually* and *weakly*
   reactive, Bough with `construct` running user closures is weakly
   reactive (p. 8).
4. Krishnaswami, Benton and Hoffmann's: an affine permission pays for one
   stream cell per tick, so the graph never holds more cells than the
   permissions passed in
   (krishnaswami-higher-order-functional-reactive-programming-in-bounded-space
   pp. 3, 8, Thm. 4). Their successor paper calls it "too precise to be
   useful in practice", since the graph's size shows up in every
   signature (krishnaswami-higher-order-functional-reactive-programming-without-spacetime-leaks
   p. 2), and it bounds nodes, not what closures hold (…-in-bounded-space
   p. 4).

Even the smallest FRP collects between units: Emfrp runs "a kind of
mark-and-sweep GC that runs each time an iteration finishes" for
non-primitive data (sawada-… p. 6).

**Simultaneity: the embedded line moved from merging to ordering.** E-FRP's
rule is Bough's: "no two events ever occur simultaneously"
(wan-event-driven-frp p. 3). EvEmfrp combined two same-time update
timings with a merge function; its successor runs them "sequentially
according to the total order of the timings"
(yokoyama-switching-mechanism-for-update-timing-of-time-varying pp. 4, 6).
XFRP needed *source unification*, merging inputs into one linear order,
because a node read through `@last` could otherwise have two "last"
values (shibanai-distributed-functional-reactive-programming-on-actor-based-runtime
p. 7). Bough's single pump gives that for free. E-FRP's reason is simpler
handlers and a checkable compile; Bough's, that `merge` would give a
different answer, is semantic and stronger.

**Nobody folds a burst with a user's fold.** The batch has three cruder
collapses: one bit per interrupt, copied and cleared with interrupts off,
so a burst becomes "it happened" (yokoyama-… pp. 9–10); a pending event
not queued twice at the head of a priority queue
(kaiabachev-e-frp-with-priorities p. 5); and sampling once per
iteration, which is keep-latest (sawada-… p. 9; pike-… p. 3). EvEmfrp/S
also drops by declaration: `Interval[T]` masks an interrupt for T after
it fires (yokoyama-… p. 5). Bough's `keep_latest` spelled out is the same
move, and its associative fold is new.

**Priorities.** P-FRP compiles pre-emption: a higher-priority interrupt
aborts a lower handler's work on temporaries, runs, and the lower one
restarts, and the theorem is that the result equals some sequential order
of the two, so "the programmer reasons modulo permutations on the order of
event arrivals" (kaiabachev-e-frp-with-priorities pp. 1, 5, 7, 9,
Thm. 5.3). Pending events queue by priority, ties oldest first (pp. 4–5).
Under the non-pre-emptive model, Bough's, event k can wait for the sum of
the other handlers' times, and no event is lost only if the same one
doesn't recur before it's handled (pp. 9–10). Pre-emption cost the lowest
priority 448 ticks of worst wait against 250 without it (p. 11; not
reproduced). With Bough's drain, the top-priority slot waits at most one
whole unit, children included. On an MCU the interrupt itself pre-empts
and only writes the slot, so the capture is never late; only the reaction
waits.

**Child instants have no bound in the literature.** Clock refinement
warns that the outer step ends only if the substep loop ends
(gemunde-clock-refinement-in-imperative-synchronous-languages p. 9).
EvEmfrp/S runs micro-iterations until none remain, and its compiler
checks that dependencies between timings are acyclic (yokoyama-… p. 6),
which is presumably what makes the chain end, and which Bough can't
check statically for `split` and `defer`. Esterel and Aguado et al.
guarantee finite macro-steps by clock-guarding every recursion
(aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of
p. 7); Bough's child instants nest inside the transaction instead.

**Whole-program evaluation beat active-parts-only for small models.**
SCCharts' data-flow route, evaluating everything each tick as
straight-line code, beat the priority route on speed and jitter for small
and medium models, and the priority route scales better only
asymptotically
(vonhanxleden-sccharts-sequentially-constructive-statecharts-for-safety-critical-applications
pp. 9–11). That bears on a tier that wants WCET more than throughput.

### The Rust prior art

gc-arena is `no_std` over `alloc`, single-threaded, and collects only
between mutations (gc-arena@v0.7.0 `src/lib.rs`:1–6,
`src/arena.rs`:98–116), the nearest thing to Bough's allocator tier. DFIR
generates each tick as one function from a macro, which is what a static
tier looks like in Rust (hydro@dfir_rs-v0.16.0
`dfir_lang/src/graph/meta_graph.rs`:813–816). No reactive crate in the
table targets bare metal with a bounded graph.

### Settled decisions the evidence contradicts

None found. No static engine in core is supported: every bounded system
here gives up `construct`-like creation or bounds it by changing the
semantics, which is RFD 7's reading that a static engine means "either a
subset of the semantics without `construct` or pooled `construct` that
brings a collector back per pool". Tracing between units is
supported: Juniper's counts leak cycles, Emfrp collects between
iterations, and Céu avoids a collector only through lexical lifetimes.
Not aborting is compatible: P-FRP aborts to pre-empt, and Bough never
pre-empts a unit, so it needs no rollback. P-FRP shows that aborting
before commit is the known route if Bough ever wanted pre-emption.

### The options for Bough

For `construct` in the bounded tier:

1. RFD 7's: one arena of N slots, and a full arena panics and poisons.
2. Céu's pools as an opt-in, a declared size per `construct` site with
   creation failing when full.
3. A typed slot capability, an affine token consumed by `construct` and
   freed when the node dies, as an opt-in proof.

For child-instant depth: a fixed maximum set by the caller beside N, or
none. For handle queues in the bounded tier: a fixed capacity per handle
and a full-queue error, or input slots only.

### Claude's leaning

Keep option 1, and add what the literature shows users need: the bounded
tier should report its slot high-water mark, so N comes from running the
program's tests, as Céu's users size pools by hand. Take a maximum
child-instant depth from the caller beside N, with exhaustion handled
like a full arena. Give each handle's queue a fixed capacity and
`IoError` a full-queue case in the bounded tier's major version. That
answers one of RFD 7's open questions: yes, `IoError` needs one. Keep
the associative fold, and cite Yokoyama as evidence that the embedded
FRP line collapses bursts anyway, less explicitly.

### Questions to grill

- RFD 7 says exhaustion never gives a different answer. Would you accept
  Céu's rule, a declared, sized pool that `construct` sites name, with
  creation failing when full, as an opt-in, or is that a different
  semantics you won't ship?
- Does the bounded tier need handle queues at all, or only input slots,
  given every embedded system here keeps one pending occurrence per
  source?
- Is a top-priority slot waiting up to one whole unit acceptable on the
  F303, or does some milestone need P-FRP-style pre-emption?
- Should the bounded tier take a maximum child-instant depth from the
  caller?
- Is Juniper's claim that a tracing collector "has unacceptable overhead"
  on 2 KB of RAM worth testing
  on the Due before the tier is designed around a tracing collector?

### Experiments this proposes for Bough

- Run the button-to-LED milestone on the F303 with a slot high-water mark
  reported, and time the collection between units on the board.
- Measure a unit's worst-case time on the Due with a small graph, whole
  graph evaluated against the marked region only, to see whether
  SCCharts' result about jitter holds for Bough's engine.

### Reading path

- wan-real-time-frp, then wan-event-driven-frp, then
  kaiabachev-e-frp-with-priorities. Needs structural operational
  semantics and typing judgments; the E-FRP text extraction loses
  ligatures, so read the PDF's figures.
- sawada-emfrp-a-functional-reactive-programming-language-for-small and
  yokoyama-switching-mechanism-for-update-timing-of-time-varying.
  Self-contained.
- santanna-structured-synchronous-reactive-programming-with-ceu. Needs
  the synchronous hypothesis, Esterel's `await` and `par`.
- biernacki-clock-directed-modular-code-generation-for-synchronous-data,
  then gerard-a-modular-memory-optimization-for-synchronous-data-flow.
  Needs Lustre's `fby`, `when` and `merge`, and clocks as types.
- pike-copilot-a-hard-real-time-runtime-monitor. Self-contained.

## Verification and testing (RFD 1's policy)

### What the literature says

**RFD 1's policy is QuickCheck's method, with the text as the
specification.** QuickCheck names the oracle problem and lists an
executable specification as one answer (claessen-quickcheck-a-lightweight-tool-for-random-testing-of
p. 9), and its case studies test a fast implementation against a simpler
reference (p. 8). Three of its lessons carry over. Distribution is the
tester's job: the "most serious pitfall" is passing many trivial cases,
fixed by labelling cases and by generators instead of preconditions
(pp. 3, 7). Size grows during a run so small counterexamples come first,
and shrinking arrived as a user's extension (pp. 5, 8). And errors split
about evenly between generators, specification and program (p. 11), which
matches running the text finding four defects in it. QuickCheck has no
coverage criterion and names that as its main limitation (pp. 9, 11).

**Whole-trace equality is stronger than any temporal property over the
same observations.** Property-based testing of asynchronous FRP checks
LTL over several clocked signals on a flattened trace, since
propositional predicates can't say how signals evolve
(nielsen-property-based-testing-for-asynchronous-functional-reactive-programming
pp. 3, 7, 10–13). For what the oracle covers, equal traces satisfy the
same temporal properties. Its lessons matter where the oracle is silent:
liveness can't be tested on a finite trace, so `until` must be weak (pp.
8, 11), generation must be fair so every input fires (pp. 2–3), and
shrinking a signal keeps its clocks (p. 15).

**Trace length finds bugs short traces miss.** Pérez and Nilsson's
bouncing-ball bug appeared only with larger input streams, after 897
tests, where short traces never reached the floor
(perez-testing-and-debugging-functional-reactive-programming p. 14). A
second passed 100 tests and needed 3,443 of a 100,000-test run: more
tests, not longer traces (p. 22).
Their record and replay works because pure arrowized FRP separates
effects and sampling from processing; the trace is the inputs and their
times, and replay is exact "provided that the bug was not in the
Input/Output layer" (pp. 2, 6, 18). QuickCheck can continue a recorded
prefix at random (pp. 14, 19).

**Proof costs years, and a re-encoding is trusted code.** Vélus proves in
Coq that generated assembly is bisimilar to Lustre's dataflow semantics,
for a static graph without switching or dynamic creation. Its semantics
is relational, a specification to prove against rather than an
interpreter to run, and the proof needed an extra semantics that exists
only for the proof (bourke-a-formally-verified-compiler-for-lustre
pp. 2–8, 13). It validates an untrusted scheduler's result rather than
proving the scheduler (p. 4). Copilot's verifier builds a per-program
bisimulation by SMT in "just under one year" and 1,854 lines, and works
only because the generated C is nearly isomorphic to the stream program:
ring buffers, one `step` per tick, no loops, `-O0` only
(scott-trustworthy-runtime-verification-via-bisimulation-experience-report
pp. 3, 5–6, 9, 19, 23). Its most useful admission for Bough: the verifier's
encoding of Copilot's semantics is trusted, and "we do not have a robust
way to test these semantics beyond careful engineering and manual
comparison with the Copilot interpreter" (p. 19). A Rust port of the
text would have been that. Mechanising a small switching-free arrow
language with effects took 2 kLOC of specification and 3 kLOC of proof,
and found proofs that "could not follow the proof sketches given in the
original paper" (ischard-a-mechanized-formalization-of-an-frp-language-with
pp. 3, 8–12).

**Hierarchical time has no testing literature.** Nothing in the batch
tests or mechanises child instants. Vélus keeps absence explicit at every
clock level so a delay slides past gaps (bourke-… p. 6), which is what a
child-index-aware comparison would need.

### The Rust prior art

None of the crates in the table tests against a reference semantics.
carboxyl checks algebraic laws with QuickCheck (carboxyl@2a80080
`src/stream/mod.rs`:690–722), and hydro_lang fuzzes in a simulator
(hydro@dfir_rs-v0.16.0 `hydro_lang/src/sim/flow.rs`:41). salsa is the
one with a fixed-point mechanism of its own, and it refuses to combine
cut-off with cycles without proof (salsa@salsa-v0.28.5
`src/function/backdate.rs`:33–38).

### What the probe found

`rfd-0001-child-index-mutants` asks whether the oracle's comparison, which
checks per-node values per transaction, listener order and cell samples
but not which child instant an event fell in, catches a mutant that puts
an event in the wrong sibling child instant. Over 4,000 random programs
of 8 to 18 nodes with 70,553 mutants, in a toy interpreter of
`T = [Int]` with `hold`, `snapshot`, `split` and `defer`, and no loops or
switches:

- The comparison as it stands caught 17.0%; with every event's full time
  compared, 61.9%. Listener order alone caught 8.9 of the 17.0 points.
- Of the survivors, 20.0% of all mutants are caught once every node is
  observed. 46.4% change nothing any node shows, only which events are
  simultaneous, which a merge or a snapshot added over them would see.
  16.7% are order-isomorphic, and only a new split or defer at the same
  parent could collide with them. With every node observed, the
  comparison with full times missed none.
- Engine-wide bugs are another matter. Every defer at index 1 is caught
  by 15.5% of the programs it affects, indices not shared by 40.3%, and
  every split collapsed, [F2](./2026-09-24-engine-feasibility-spike.md#f2), by 33.4%. A suite of a thousand programs
  catches all three with near certainty.

So the comparison without child indices catches every misplacement a
listener or sample of the program can see once observed. What it misses
is harmless per program, and the risk is a generator that rarely builds
merges or snapshots across sibling child instants.

> rustc 1.98.1 (released 2026-09-01) - measured 2026-09-28 - rfd-0001-child-index-mutants at experiments@f08c179 - Ryzen 7 2700X, Fedora 44 container on Bazzite 44

```
cargo run --release --bin rfd-0001-child-index-mutants
```

### Settled decisions the evidence contradicts

None found. GHC as the oracle gains a second reason: a re-encoding of a
semantics becomes trusted code that can be checked only by hand against
the original (scott-… p. 19), which is what a Rust port would have been.
The per-instant comparison misses no bug class the batch names, except
by trace length, which is the generator's limit, not the comparison's.

### The options for Bough

- Shrinking: already built, twice, in the spike's harness, and not in
  RFD 1's policy.
- Adequacy: have the generator report labelled proportions of the shapes
  the policy promises (loops, diamonds through loops, switches that move,
  constructs at child instants, merges and snapshots across sibling child
  instants), so a later change that starves a shape shows.
- Trace length: accept ten transactions; add long traces for loop-free
  programs against GHC; or add long traces with engine-only properties,
  the live-node count and no stale-token error, without GHC.
- Replay: record handle calls per pump for exact replay, and continue a
  recorded prefix at random.
- A middle path to proof: a debug-mode check that the order the engine
  evaluated was topological for the graph at that moment, validating
  rather than proving, as Vélus does for scheduling.

### Claude's leaning

Put shrinking and labelled proportions into RFD 1's policy, since the
harness already has both and the policy doesn't promise them. Add long
traces with engine-only properties to the scheduled job, since what fails
at length is the engine's bookkeeping, not the semantics. No seventh test
affordance for child indices: label the generator's cross-sibling merges
and snapshots instead, and check the share isn't small. Replay is worth
building as a feature of the handle API, not as a test affordance, and
isn't urgent. Keep GHC running the text; if the semantics is ever
mechanised, do it to prove the creation cuts, not as an oracle.

### Questions to grill

- Is a wrong child index that no program can read a bug, or an
  unobservable detail the comparison is right to ignore?
- Should RFD 1 require the generator to report labelled proportions, and
  keep the spike's seventy deliberate breaks as a suite?
- Which long-run failure worries you most, generation wrap, garbage
  growth or queue growth, and is ten transactions a program a choice or
  an accident?
- Is replay of recorded pump calls a user feature you want, and does it
  count against "six affordances and nothing beyond"?
- Would you ever mechanise the semantics, and if so, is the creation cut
  the reason?

### Experiments this proposes for Bough

- Run the oracle's generator with labelled proportions for a day of
  seeds and see which promised shapes are rare.
- Run the engine alone on loop-free programs for a million transactions
  each, asserting the live-node count and no stale token, to find what
  fails at length.

### Reading path

- claessen-quickcheck-a-lightweight-tool-for-random-testing-of. Needs
  basic Haskell.
- perez-testing-and-debugging-functional-reactive-programming. Needs
  Yampa's arrows, summarised in its §2, and LTL.
- nielsen-property-based-testing-for-asynchronous-functional-reactive-programming
  §§3–5. Needs LTL and QuickCheck.
- scott-trustworthy-runtime-verification-via-bisimulation-experience-report.
  Needs labelled transition systems and bisimulation.
- bourke-a-formally-verified-compiler-for-lustre. Needs Lustre's clocks,
  big-step semantics and simulation proofs.

## The lineage map

Where Bough's ideas come from, by branch, oldest first. An arrow is "led
to", "was answered by" or "was followed, in the same line of work, by";
it doesn't always mean the later source cites the earlier. A dagger
marks a source on the map only, not read. Continuous time is here and
nowhere else: Bough is discrete.

- **Classic FRP, continuous time.** Fran, Elliott and Hudak 1997† →
  first principles, Wan and Hudak 2000† → RT-FRP 2001 → E-FRP 2002 →
  E-FRP with priorities 2007. Push-pull, Elliott 2009, with denotational
  design 2009 → the Sodium book's App. E 2016 → **Bough**.
- **Arrowized FRP.** Arrows, Hughes 2000† → Yampa, FRP continued 2002 →
  arrows and robots 2003† → the arrow space leak 2007 → causal
  commutative arrows 2009 → safe FRP through dependent types 2009 →
  keeping calm 2010 → wormholes 2012† → FRP refactored 2016† → testing
  and debugging 2017 → Rhine 2018 → FRP restated 2019† → runtime
  verification 2020† → loopy 2023.
- **First-class and higher-order FRP.** Elerea, Patai 2011 →
  reactive-banana 2011 and 2015; monadic FRP 2013 → FRPNow 2015, which
  answers Elerea and reactive-banana. Reflex (Hackage) sits beside them.
  Sodium and reactive-banana are "equivalent apart from naming"
  (blackheath-functional-reactive-programming, ch. 1, §1.9).
- **Dynamic dataflow in a host language.** Frappé 2001† → FrTime 2006,
  thesis 2008 → Flapjax 2009 → Scala.React 2012, incremental lists 2013,
  thesis 2013 → REScala 2014† → distributed REScala 2014 → thread-safe
  REScala 2018. DREAM 2014† → Margara and Salvaneschi 2018 →
  Historiographer 2023†. Elm 2013 → farewell to FRP 2016. The survey,
  2013, maps this branch.
- **Modal and guarded types.** Nakano 2000† → guarded domain theory
  2011† → ultrametric semantics 2011 → bounded space 2012 → without
  spacetime leaks 2013 → fair reactive programming 2014 → Simply RaTT
  2019 → diamonds 2021 → Rattus 2022 → asynchronous modal FRP 2023,
  in Haskell 2023† → property-based testing for async FRP 2026. LTL types
  2012 and causality for free 2013† sit beside it; Jeltsch 2012† links it
  to temporal logic.
- **Synchronous languages.** Kahn networks 1974† → Lucid 1985† → Lustre
  1987†, 1991; Esterel 1992†; SIGNAL 1991†; Statecharts 1987†; SDF
  1987† → synchronous Kahn networks 1996 → modular causality 2001.
  Esterel's foundations 2000† → constructive semantics 2002, with cyclic
  circuits 1996 before it and timed ternary simulation 2012† after. The
  survey twelve years later 2003† → delayed actions 2004 →
  clock-directed code 2008 → modular static scheduling 2009 → modular
  memory 2012 → clock refinement 2013 → sequential constructiveness 2014
  → SCCharts 2014 → fixed-point semantics for constructive scheduling
  2015 → Vélus 2017. Copilot 2010 → its verifier 2023, extended 2026.
  Céu 2015. Superdense time, Lee and Zheng 2005.
- **Incremental computation.** Attribute grammars 1981† → computational
  circuits 1990† → the categorized bibliography 1993†. Order in a list,
  Dietz and Sleator 1987† → self-adjusting computation 2005 → adaptive
  functional programming 2006 → its memory management 2008 → traceable
  data types 2010† → Adapton 2014 → a theory of changes 2014 → build
  systems à la carte 2018. Jane Street's Incremental 2015; rustc's
  red-green algorithm and salsa.
- **Dynamic topological order.** Pearce and Kelly 2006 → their batch
  algorithm 2010 → HKMST 2012 → Bender et al. 2016 → Bernstein and
  Chechik 2018† → the dynamic graph survey 2022†.
- **Dataflow at scale.** Naiad 2013 and differential dataflow 2013 →
  its foundations 2015 → shared arrangements 2020† → DBSP 2023 → Flo 2025
  and DFIR. Deterministic dataflow foundations 2020†.
- **Values and fusion.** Stream fusion 2007 → stream fusion to
  completeness 2017. Linear Haskell 2018 → linearity and uniqueness 2022.
- **Fine-grained signals.** MobX and Preact → Reactively 2022 → the TC39
  proposal 2024 → Leptos's `reactive_graph`, Sycamore.
- **Embedded FRP.** Emfrp 2016 → XFRP 2018 → recursive data types 2021†
  → update-timing switching 2024. Juniper 2016. Hailstorm 2020†. The
  bare-metal reactive VM 2022† → reactive programming without functions
  2024. Parallel FRP 1999†.
- **Threads and events.** Ousterhout 1996 → von Behren et al. 2003 → Lee
  2006.
- **Collection in Rust.** Bacon et al. 2004 → Rust for high-performance
  GC 2016† → shifgrethor 2018 → Josephine 2018 → Goregaokar's tour 2021
  → gc-arena.

## The crate table

The six crates read at source, at the pins below, then the rest from
docs.rs, READMEs and single files at a named commit. Read on 2026-09-28.
"Not stated" means the source read was silent.

The pins, shallow clones at the latest stable release tag on 2026-09-27:

| Repo | Tag | Commit | Crate path |
|---|---|---|---|
| github.com/leptos-rs/leptos | v0.8.21 | 584c3a2d884b0e4dba9e3f822a9b6982cff072c7 | reactive_graph/ |
| github.com/sycamore-rs/sycamore | 0.9.3 | 48e55bb7e699ab4975b3d49401ec93cd9dca58b1 | packages/sycamore-reactive/ |
| github.com/kyren/gc-arena | v0.7.0 | d527c45c93794e4788b484a89cca56c9d52e61ec | src/ |
| github.com/salsa-rs/salsa | salsa-v0.28.5 | d434f8805c60ac60dce5f367ca91c5a7cd3e4c86 | src/ |
| github.com/hydro-project/hydro | dfir_rs-v0.16.0 | 118b356447d92e778313d72a351e5a8d2814aa1a | dfir_rs/, dfir_lang/ |
| github.com/milibopp/carboxyl | master (0.2.2, untagged) | 2a80080ee2e9f18e2202c6c57d88bfdc69d1fc23 | src/ |

salsa's `v*` tags stop at 0.16.1 (2021); later releases are tagged
`salsa-v*`. carboxyl moved from aepsil0n to milibopp, and its 0.2.2 on
crates.io has no tag. reactive_graph at leptos v0.8.21 is 0.2.15, the
crates.io latest.

| Crate | Version | Semantics | Glitch freedom | Memory strategy | Threading | Source |
|---|---|---|---|---|---|---|
| `reactive_graph` (Leptos) | 0.2.15, leptos v0.8.21 | Signals, memos, effects; dependencies tracked per run; no instant, no switching | Reactively's: push `Check`/`Dirty` colours, pull to evaluate, `PartialEq` cut-off | `Copy` handles in a process-wide slot map; nodes live as long as their owner scope; stale use panics | Every node `Send + Sync` behind `RwLock`s, with a lock-order rule | leptos-rs/leptos @584c3a2 `reactive_graph/src/` |
| `sycamore-reactive` | 0.9.3 | Signals, memos, effects in one node type; dynamic dependencies; `batch` | DFS reverse post-order, then a flat loop; grey mark panics on a cycle; pull for a dirty read | `Copy` handles into a slot map; ownership by creation scope; explicit recursive dispose | `thread_local!` root, `RefCell` nodes; single-threaded | sycamore-rs/sycamore @48e55bb `packages/sycamore-reactive/src/` |
| `gc-arena` | 0.7.0 | A collector, not a reactive library | n/a | Incremental mark-sweep between `mutate` calls, paced by allocation debt; `'gc`-branded `Copy` pointers; `unsafe trait Collect` with a safe derive | Single-threaded (`Cell`, `Rc`) | kyren/gc-arena @d527c45 `src/` |
| `salsa` | 0.28.5 | Incremental queries over revisions; no events | Demand-driven validation with backdating; opt-in fixed-point cycles, capped at 200 | IDs with a 32-bit generation; tracked structs die with the query run that made them; LRU eviction | Parallel readers, one cancelling writer | salsa-rs/salsa @d434f88 `src/` |
| DFIR (`dfir_rs`, `dfir_lang`) | 0.16.0 | Ticks over batches; static graph from a macro; `defer_tick` to the next tick | Topological order fixed at compile time; cycles within a tick refused | Operator state in a slot vector with a lifespan per tick, loop or forever | One instance per thread; tasks spawned local | hydro-project/hydro @118b356 `dfir_rs/`, `dfir_lang/` |
| `carboxyl` | 0.2.2 (master) | Sodium-like streams and signals; cells read before the instant | Callbacks fire in registration order; a diamond through `merge` fires twice | Downstream holds upstream strongly, upstream holds downstream weakly | One global `Mutex` around each transaction | milibopp/carboxyl @2a80080 `src/` |
| Incremental (OCaml) | v0.17.0 | Vars, `map`, `bind`, observers, `stabilize` | Recompute heap by height; heights raised on link, which finds cycles | Only nodes with a path to an observer are kept; `bind` invalidates what it made | Single-threaded | janestreet/incremental @v0.17.0 `src/incremental_intf.ml`:90–260 |
| sodium-rust | 2.1.3 (source at master 3e93021) | Sodium's streams and cells, explicit transactions | DFS order with a visited flag, no ranks | Atomic counts plus Bacon–Rajan cycle collection; captures declared with `lambda1(f, deps)` | `Arc`/`Mutex` everywhere, `unsafe impl Send/Sync` over a `Cell` | SodiumFRP/sodium-rust @3e93021 `src/impl_/` |
| futures-signals | 0.3.34 | Latest-value signals that may skip; `SignalVec` diffs that never skip | Not stated; lossy polling | `Mutable` like `Arc` + `RwLock` | `Send + Sync` | docs.rs |
| rxrust | 0.15.0 | ReactiveX observables | Not stated | `Rc` or `Arc` context, chosen at compile time | Local or shared; tokio schedulers | README, docs.rs |
| frappe | 0.4.7 | Eager push streams; pulled `Fn() -> T` signals | No transactions in the source read | Derived streams hold their parents | `Send + Sync` closures | wolfiestyle/frappe master |
| dioxus-signals | 0.7.10 | Signals and memos; subscription on render reads | Not stated | `Copy` handles in `generational-box`, dropped with their owner | Unsync by default, sync storage optional | docs.rs |
| adapton | 0.3.31 | Demanded computation graph, nominal memoization | Dirty on write, clean on demand | Not stated | Not stated | docs.rs |
| incremental-rs | 0.2.8 | A port of Incremental | Height-ordered recompute heap, cut-off | `Rc` state; dropping an observer unloads what only it needed | Single-threaded | cormacrelf/incremental-rs @5ba8209 |
| anchors | 0.6.0 | Adapton-style pull, Incremental-style push for observed nodes | Not stated | Not stated | Single-threaded by default | docs.rs (repo archived) |
| differential-dataflow | 0.25.1 | Collections of `(data, time, diff)` updates | Outputs complete for a time once the probe says so | Arrangements of updates | Data-parallel over timely workers | docs.rs |
| timely | 0.31.0 | Dataflow with timestamps and frontiers | Frontiers tell when a time is complete | Not stated | One worker per thread, processes across machines | docs.rs, README |
| dbsp | 0.357.0 | Circuits over Z-set streams; nested circuits to a fixed point | Per step, by circuit order | Storage and a buffer cache for spilling | Multithreaded, data-parallel | feldera/feldera @2ad179e `crates/dbsp` |
| floem_reactive | 0.2.0 | Leptos-style signals, memos, effects, scopes | Not stated | Signals in a runtime map, scoped | `thread_local!` runtime | docs.rs, `src/runtime.rs` |
| i-slint-core (properties) | 1.18.1 | Property bindings with dependency tracking | Not stated | Pinned properties with dependency lists | Not stated | docs.rs |
| comemo | 0.5.1 | Constrained memoization of tracked calls | Validity checked against recorded constraints | Global cache, explicit evict | Not stated | docs.rs |
| incremental-topo | 0.3.1 | Pearce–Kelly incremental topological order | n/a | Nodes in a generational arena | Not stated | docs.rs |
| discro | 0.35.0 | One shared latest value, publisher and subscribers | Not stated | Not stated | On `tokio::sync::watch` | docs.rs |
| reactive_stores | 0.4.4 | Field-level tracking of nested state; keyed `Patch` | A field update notifies parents and children, not siblings | On `reactive_graph` | As `reactive_graph` | docs.rs |

Two crates considered for the table aren't reactive and have no row.
Bevy's change detection records ticks on components for systems to check
when they run, and pushes nothing to dependents
(docs.rs/bevy_ecs/0.19.1). Xilem rebuilds a lightweight view tree,
Elm-style, with no dependency graph (linebender/xilem README).

## Annotated bibliography

Every kept source, by stem, with what it gave Bough. The records in
`literature` hold the reading notes by page, the stored copy's version
and where it came from. Sources on the lineage map only are marked there.

- **abadi-foundations-of-differential-dataflow**. Martín Abadi, Frank McSherry, Gordon D. Plotkin. *Foundations of Differential Dataflow*. FoSSaCS 2015. Core, read in full. Product partial orders for nested loops; expressly excludes the lexicographic order `T = [Int]` is, and gives [F1](./2026-09-24-engine-feasibility-spike.md#f1)'s loop equation a unique solution when feedback shifts the index.
- **acar-adaptive-functional-programming**. Umut A. Acar, Guy E. Blelloch, Robert Harper. *Adaptive Functional Programming*. ACM TOPLAS 2006. Supporting, read in part. The ML library of the thesis's line of work; its one addition for Bough is why time stamps use order maintenance, integer ranks with re-ranking after Dietz and Sleator, rather than real-number tags or list positions.
- **acar-self-adjusting-computation**. Umut A. Acar. *Self-Adjusting Computation*. PhD thesis, CMU 2005. Core, read in full. Change propagation over order-maintenance time stamps, and trace stability: why a cell of a collection is slow and a content-keyed structure isn't.
- **aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of**. Joaquín Aguado, Michael Mendler, Reinhard von Hanxleden, Insa Fuhrmann. *Denotational Fixed-Point Semantics for Constructive Scheduling of Synchronous Concurrency*. Acta Informatica 2015. Core, read in full. The closest formal precedent for the order on `T = [Int]`, and the shape a real least-fixpoint argument needs, which the oracle's rounds don't have.
- **apfelmus-frp-dynamic-event-switching**. Heinrich Apfelmus. *FRP - Dynamic Event Switching*. Blog post 2011. Supporting, read in full. The time-leak argument against unrestricted switching, and three answers, Jeltsch's era types the most direct.
- **apfelmus-frp-release-of-reactive-banana-version-1-0**. Heinrich Apfelmus. *FRP — Release of reactive-banana version 1.0*. Blog post 2015. Supporting, read in full. Start-time generators shipped as reactive-banana's `Moment` monad; no simultaneous occurrences within one event.
- **bacon-a-unified-theory-of-garbage-collection**. David F. Bacon, Perry Cheng, V. T. Rajan. *A unified theory of garbage collection*. OOPSLA 2004. Core, read in full. Tracing and counting as least and greatest fixpoints; counting with a backup trace sees cycles, so RFD 3's first reason is incomplete.
- **bahr-asynchronous-modal-frp**. Patrick Bahr, Rasmus Ejlers Møgelberg. *Asynchronous Modal FRP*. ICFP 2023. Core, read in full. One input on one channel per step, with clocks per delayed value; runs only what an output's clock reaches, and statically bounds dependencies through switching.
- **bahr-diamonds-are-not-forever**. Patrick Bahr, Christian Uldal Graulund, Rasmus Ejlers Møgelberg. *Diamonds are not forever: liveness in reactive programming with guarded recursion*. POPL 2021 (PACMPL 5, POPL). Supporting, read in part. A guarded fixed point can't promise that something happens; the formal form of [F22](./2026-09-24-engine-feasibility-spike.md#f22).
- **bahr-modal-frp-for-all**. Patrick Bahr. *Modal FRP for all: Functional reactive programming without space leaks in Haskell*. JFP 2022. Core, read in full. Rattus: what a type-checked capture rule costs a host language, and the clearest statement that explicit leaks stay legal.
- **bahr-simply-ratt-a-fitch-style-modal-calculus-for**. Patrick Bahr, Christian Uldal Graulund, Rasmus Ejlers Møgelberg. *Simply RaTT: A Fitch-style Modal Calculus for Reactive Programming Without Space Leaks*. ICFP 2019. Core, read in full. A closure that captures a delayed location and runs a step later is [F62](./2026-09-24-engine-feasibility-spike.md#f62), caught by a type rule.
- **bainomugisha-a-survey-on-reactive-programming**. Engineer Bainomugisha, Andoni Lombide Carreton, Tom van Cutsem, Stijn Mostinckx, Wolfgang de Meuter. *A Survey on Reactive Programming*. ACM Computing Surveys 2013. Supporting, read in part. The standard taxonomy; which systems let glitches through.
- **barenz-rhine-frp-with-type-level-clocks**. Manuel Bärenz, Ivan Perez. *Rhine: FRP with Type-Level Clocks*. Haskell Symposium 2018. Supporting, read in part. Simultaneity only on one clock, schedules and resampling buffers: vocabulary for input slots and the pump.
- **bender-a-new-approach-to-incremental-cycle-detection-and**. Michael A. Bender, Jeremy T. Fineman, Seth Gilbert, Robert E. Tarjan. *A New Approach to Incremental Cycle Detection and Related Problems*. ACM TALG 2016. Core, read in full. Weak topological levels paid for by raising them; correct under deletions with no useful bound.
- **bernardy-linear-haskell-practical-linearity-in-a-higher-order**. Jean-Philippe Bernardy, Mathieu Boespflug, Ryan R. Newton, Simon Peyton Jones, Arnaud Spiwack. *Linear Haskell: Practical Linearity in a Higher-Order Polymorphic Language*. POPL 2018. Supporting, read in part. Linear means exactly once, and Rust is a uniqueness language; the industrial case for one consumer per stream.
- **berry-the-constructive-semantics-of-pure-esterel**. Gérard Berry. *The Constructive Semantics of Pure Esterel*. Draft book 2002. Core, read in full. Constructiveness, the class acyclicity undercuts; Bough's rule is Esterel v4's. Incarnations are the nearest model for creation at a child instant.
- **biernacki-clock-directed-modular-code-generation-for-synchronous-data**. Dariusz Biernacki, Jean-Louis Colaço, Grégoire Hamon, Marc Pouzet. *Clock-directed Modular Code Generation for Synchronous Data-flow Languages*. LCTES 2008. Core, read in full. What Bough's rejected static engine would be; modular compilation keeps code linear in the source, unlike [F36](./2026-09-24-engine-feasibility-spike.md#f36).
- **blackheath-functional-reactive-programming**. Stephen Blackheath, Anthony Jones. *Functional Reactive Programming*. Manning 2016. Core, read in part. The semantics Bough is held to. States its creation rule for four primitives only, hides steps for continuous time, and argues for threads.
- **bourke-a-formally-verified-compiler-for-lustre**. Timothy Bourke, Lélio Brun, Pierre-Évariste Dagand, Xavier Leroy, Marc Pouzet, Lionel Rieg. *A Formally Verified Compiler for Lustre*. PLDI 2017. Core, read in full. Vélus: what mechanised fidelity to a dataflow semantics costs, and validation in place of proof for a scheduler.
- **budiu-dbsp-automatic-incremental-view-maintenance-for-rich-query**. Mihai Budiu, Tej Chajed, Frank McSherry, Leonid Ryzhyk, Val Tannen. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages*. VLDB 2023. Core, read in full. Integration and differentiation over an abelian group; which operators are free, and a strictness rule for feedback that is Bough's loop rule.
- **cai-a-theory-of-changes-for-higher-order-languages**. Yufei Cai, Paolo G. Giarrusso, Tillmann Rendel, Klaus Ostermann. *A Theory of Changes for Higher-Order Languages: Incrementalizing λ-Calculi by Static Differentiation*. PLDI 2014. Supporting, read in full. Change structures with a `Replace` fallback: a cell of a collection is the trivial one, and the contract a patch cell should take.
- **caspi-synchronous-kahn-networks**. Paul Caspi, Marc Pouzet. *Synchronous Kahn networks*. ICFP 1996. Supporting, read in full. Guardedness as the whole deadlock check, and dynamic networks under a synchronous semantics losing their memory bound.
- **cave-fair-reactive-programming**. Andrew Cave, Francisco Ferreira, Prakash Panangaden, Brigitte Pientka. *Fair reactive programming*. POPL 2014. Supporting, read in part. The may and must split from the other side; the history of `import` and why it was removed to manage space.
- **claessen-quickcheck-a-lightweight-tool-for-random-testing-of**. Koen Claessen, John Hughes. *QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs*. ICFP 2000. Core, read in full. The method of RFD 1's policy: executable specifications as oracles, distribution as the tester's job.
- **cooper-embedding-dynamic-dataflow-in-a-call-by-value**. Gregory H. Cooper, Shriram Krishnamurthi. *Embedding Dynamic Dataflow in a Call-by-Value Language*. ESOP 2006. Core, read in full. FrTime's height-ordered queue, its repair when a branch is taller, and deletion of what a switched-out branch built.
- **cooper-integrating-dataflow-evaluation-into-a-practical-higher-order**. Gregory H. Cooper. *Integrating Dataflow Evaluation into a Practical Higher-Order Call-by-Value Language*. PhD thesis, Brown University 2008. Supporting, read in part. FrTime in full: a consistency proof with control edges, weak edges that aren't enough, lowering as fusion, lifted collections.
- **coutts-stream-fusion-from-lists-to-streams-to-nothing**. Duncan Coutts, Roman Leshchinskiy, Don Stewart. *Stream Fusion: From Lists to Streams to Nothing at All*. ICFP 2007. Core, read in full. The fusion Bough's chains do, and its price in code size.
- **cuoq-modular-causality-in-a-synchronous-stream-language**. Pascal Cuoq, Marc Pouzet. *Modular Causality in a Synchronous Stream Language*. ESOP 2001. Core, read in full. Rows of recursion variables: the modular static loop check, and its false rejections.
- **czaplicki-a-farewell-to-frp**. Evan Czaplicki. *A Farewell to FRP*. Blog post 2016. Supporting, read in full. Elm dropped signals for learnability, not semantics or speed.
- **czaplicki-asynchronous-functional-reactive-programming-for-guis**. Evan Czaplicki, Stephen Chong. *Asynchronous Functional Reactive Programming for GUIs*. PLDI 2013. Core, read in full. Elm bans signals of signals over history, keeps a total event order, and relaxes it only with `async`.
- **drechsler-distributed-rescala-an-update-algorithm-for-distributed-reactive**. Joscha Drechsler, Guido Salvaneschi, Ragnar Mogk, Mira Mezini. *Distributed REScala: An Update Algorithm for Distributed Reactive Programming*. OOPSLA 2014. Core, read in full. Glitch freedom across hosts needs mutually exclusive turns, and so a coordinator at admission unless the application already serialises them; observer-linked networks aren't glitch-free as a whole.
- **drechsler-thread-safe-reactive-programming**. Joscha Drechsler, Ragnar Mogk, Guido Salvaneschi, Mira Mezini. *Thread-Safe Reactive Programming*. OOPSLA 2018. Core, read in full. The one measurement of making propagation concurrent; its uncontended-lock claim is asserted, not measured.
- **elliott-denotational-design-with-type-class-morphisms**. Conal Elliott. *Denotational design with type class morphisms (extended version)*. LambdaPix technical report 2009-01. Supporting, read in part. The principle behind fidelity: equal meanings must be indistinguishable, which makes `steps` a leak for a `T → A` model.
- **elliott-push-pull-functional-reactive-programming**. Conal Elliott. *Push-Pull Functional Reactive Programming*. Haskell Symposium 2009. Core, read in full. The model App. E is based on; keeps simultaneous occurrences and replays inner events at generation time, the counter-position to [F89](./2026-09-24-engine-feasibility-spike.md#f89)'s cut.
- **gemunde-clock-refinement-in-imperative-synchronous-languages**. Mike Gemünde, Jens Brandt, Klaus Schneider. *Clock refinement in imperative synchronous languages*. EURASIP Journal on Embedded Systems 2013. Core, read in full. Substeps inside a step on a static clock tree; an outer-step event stays present through its substeps, as in the text's [F89](./2026-09-24-engine-feasibility-spike.md#f89) replay, but it has no node creation, so it can't settle [F89](./2026-09-24-engine-feasibility-spike.md#f89).
- **gerard-a-modular-memory-optimization-for-synchronous-data-flow**. Léonard Gérard, Adrien Guatto, Cédric Pasteur, Marc Pouzet. *A Modular Memory Optimization for Synchronous Data-Flow Languages: Application to Arrays in a Lustre Compiler*. LCTES 2012. Core, read in full. Evidence that a static engine grows into an optimising compiler.
- **goregaokar-a-tour-of-safe-tracing-gc-designs-in**. Manish Goregaokar. *A Tour of Safe Tracing GC Designs in Rust*. Blog post 2021. Core, read in full. The Rust GC design space; every `Trace` there is `unsafe` because every design names objects by pointer.
- **haeupler-incremental-cycle-detection-topological-ordering-and-strong-component**. Bernhard Haeupler, Telikepalli Kavitha, Rogers Mathew, Siddhartha Sen, Robert E. Tarjan. *Incremental Cycle Detection, Topological Ordering, and Strong Component Maintenance*. ACM TALG 2012. Core, read in full. Every efficient cycle detector keeps an order; limited search is Bough's walk bounded by it, and deletions void the bounds.
- **halbwachs-the-synchronous-data-flow-programming-language-lustre**. N. Halbwachs, P. Caspi, P. Raymond, D. Pilaud. *The synchronous data flow programming language LUSTRE*. Proceedings of the IEEE 1991. Supporting, read in part. Every cycle through a `pre`, and false cycles refused knowingly: Bough's loop rule in 1991.
- **hammer-adapton-composable-demand-driven-incremental-computation**. Matthew A. Hammer, Khoo Yit Phang, Michael Hicks, Jeffrey S. Foster. *Adapton: Composable, Demand-Driven Incremental Computation*. PLDI 2014. Core, read in full. Demand-driven repair: laziness wins when little is demanded and loses when all of it is.
- **hammer-memory-management-for-self-adjusting-computation**. Matthew A. Hammer, Umut A. Acar. *Memory Management for Self-Adjusting Computation*. ISMM 2008. Core, read in full. Tracing costs 1/(1 − f) and a large live graph is pessimal; owner-based reclamation needs a theorem Bough's semantics lacks.
- **helbling-juniper-a-functional-reactive-programming-language-for-the**. Caleb Helbling, Samuel Z. Guyer. *Juniper: A Functional Reactive Programming Language for the Arduino*. FARM 2016. Core, read in full. The one embedded FRP with a dynamic graph, and no memory bound; its case against tracing is asserted.
- **hydro-dfir**. Hydro Project. *DFIR*. Hydro documentation 2026. Supporting, read in full. DFIR's introduction page only; the crate at source answers the questions it can't.
- **ischard-a-mechanized-formalization-of-an-frp-language-with**. Jordan Ischard, Frédéric Dabrowski, Jules Chouquet, Frédéric Loulergue. *A Mechanized Formalization of an FRP Language with Effects*. SAC 2025. Supporting, read in full. A price point: mechanising a small switching-free arrow language took 5 kLOC and found broken proof sketches.
- **jeffrey-josephine-using-javascript-to-safely-manage-the-lifetimes**. Alan Jeffrey. *Josephine: Using JavaScript to safely manage the lifetimes of Rust data*. arXiv 2018. Supporting, read in full. Under-approximate rooting is use-after-free, over-approximate is a leak: [F62](./2026-09-24-engine-feasibility-spike.md#f62) and [F63](./2026-09-24-engine-feasibility-spike.md#f63).
- **jeffrey-ltl-types-frp**. Alan Jeffrey. *LTL types FRP: Linear-time Temporal Logic Propositions as Types, Proofs as Functional Reactive Programs*. PLPV 2012. Supporting, read in part. Decoupled functions as LTL's constrains; fixed points need a well-ordering, which `[Int]` lacks.
- **kaiabachev-e-frp-with-priorities**. Roumen Kaiabachev, Walid Taha, Angela Zhu, Jun Inoue. *E-FRP With Priorities*. Rice University technical report (extended version of the EMSOFT 2007 paper). Core, read in full. Pre-emption by abort and restart, with a permutation theorem; the latency cost of Bough's non-pre-emptive drain.
- **keating-this-is-driving-me-loopy**. Finnbar Keating, Michael B. Gale. *This Is Driving Me Loopy: Efficient Loops in Arrowized Functional Reactive Programs*. Haskell Symposium 2023. Core, read in full. No direct dependency cycle means a static order exists, with opaque functions: acyclicity is exactly right there.
- **kiselyov-stream-fusion-to-completeness**. Oleg Kiselyov, Aggelos Biboudis, Nick Palladinos, Yannis Smaragdakis. *Stream Fusion, to Completeness*. POPL 2017. Core, read in full. Fusion by staging, what's hard (zip, nesting), and the risk of trusting a general-purpose compiler.
- **krishnaswami-higher-order-functional-reactive-programming-in-bounded-space**. Neelakantan R. Krishnaswami, Nick Benton, Jan Hoffmann. *Higher-order functional reactive programming in bounded space*. POPL 2012. Core, read in full. Affine allocation permissions bound the graph statically; too precise to use, by its authors' own later account.
- **krishnaswami-higher-order-functional-reactive-programming-without-spacetime-leaks**. Neelakantan R. Krishnaswami. *Higher-order functional reactive programming without spacetime leaks*. ICFP 2013. Core, read in full. Stability, and the machine that deletes the past, with types as guard rails; persistent two-way nodes defeat reachability GC.
- **krishnaswami-ultrametric-semantics-of-reactive-programs**. Neelakantan R. Krishnaswami, Nick Benton. *Ultrametric Semantics of Reactive Programs*. LICS 2011. Supporting, read in part. Guarded definitions have unique fixed points by Banach's theorem, which is [F1](./2026-09-24-engine-feasibility-spike.md#f1)'s status.
- **kyren-gc-arena**. kyren. *gc-arena*. Repository README 2026. Supporting, read in full. Mutation xor collection, allocation-debt pacing, and a branded pointer that can't escape the mutation callback.
- **laddad-flo-a-semantic-foundation-for-progressive-stream-processing**. Shadaj Laddad, Alvin Cheung, Joseph M. Hellerstein, Mae Milano. *Flo: a Semantic Foundation for Progressive Stream Processing*. POPL 2025. Core, read in full. Eager execution as the law patch composition must obey; no global instant.
- **lee-operational-semantics-of-hybrid-systems**. Edward A. Lee, Haiyang Zheng. *Operational Semantics of Hybrid Systems*. HSCC 2005. Core, read in full. Superdense time, the depth-two case of `T = [Int]`, and non-Zeno as the side condition [F22](./2026-09-24-engine-feasibility-spike.md#f22) breaks.
- **lee-the-problem-with-threads**. Edward A. Lee. *The Problem with Threads*. IEEE Computer 2006. Core, read in full. Deterministic ends by deterministic means; the handle queue is the one nondeterministic merge.
- **liu-causal-commutative-arrows-and-their-optimization**. Hai Liu, Eric Cheng, Paul Hudak. *Causal commutative arrows and their optimization*. ICFP 2009. Core, read in full. Any switch-free arrow program normalizes to one loop, one function and one state; no compile-time cost reported.
- **liu-plugging-a-space-leak-with-an-arrow**. Hai Liu, Paul Hudak. *Plugging a Space Leak with an Arrow*. ENTCS 2007. Supporting, read in part. A laziness leak Bough's loops through a node can't have: a feedback combinator must reuse its node.
- **maier-deprecating-the-observer-pattern-with-scala-react**. Ingo Maier, Martin Odersky. *Deprecating the Observer Pattern with Scala.React*. EPFL technical report 2012. Core, read in full. Levels with abort and hoist under dynamic dependencies, which forces side-effect-free nodes.
- **maier-higher-order-reactive-programming-with-incremental-lists**. Ingo Maier, Martin Odersky. *Higher-Order Reactive Programming with Incremental Lists*. ECOOP 2013 (LNCS 7920). Core, read in full. Reactive sequences carrying Ins and Rem deltas: the main source for open question 9.
- **maier-reactive-programming-abstractions-for-complex-event-logic-and**. Ingo Maier. *Reactive Programming Abstractions for Complex Event Logic and Dynamic Data Dependencies*. PhD thesis, EPFL, no. 5805, 2013. Supporting, read in part. Scala.React at thesis length: proofs of level-ordered propagation, pulse monoids, coalesced turns and domains.
- **margara-on-the-semantics-of-distributed-reactive-programming**. Alessandro Margara, Guido Salvaneschi. *On the Semantics of Distributed Reactive Programming: the Cost of Consistency*. IEEE TSE 2018. Core, read in full. Consistency levels from FIFO to atomic, and the cost of each, all of it distributed.
- **marshall-linearity-and-uniqueness**. Danielle Marshall, Michael Vollmer, Dominic Orchard. *Linearity and Uniqueness: An Entente Cordiale*. ESOP 2022. Supporting, read in part. Which of the two Bough's streams are: unique, with `share` as a one-way borrow.
- **mcsherry-differential-dataflow**. Frank McSherry, Derek G. Murray, Rebecca Isaacs, Michael Isard. *Differential dataflow*. CIDR 2013. Core, read in full. Collections as multisets over partially ordered versions; which operators keep traces.
- **meyerovich-flapjax-a-programming-language-for-ajax-applications**. Leo A. Meyerovich, Arjun Guha, Jacob Baskin, Gregory H. Cooper, Michael Greenberg, Aleks Bromfield, Shriram Krishnamurthi. *Flapjax: A Programming Language for Ajax Applications*. OOPSLA 2009. Supporting, read in part. Ranks without a stated repair, and a detach flag that stops dropped subgraphs without a collection.
- **milomg-super-charging-fine-grained-reactive-performance**. milomg. *Super Charging Fine-Grained Reactive Performance*. Blog post 2022. Core, read in full. Three glitch-free designs for signals; the colouring is Bough's mark, then pull.
- **minsky-introducing-incremental**. Yaron Minsky. *Introducing Incremental*. Jane Street Tech Blog, 18 July 2015. Core, read in full. Introduces Incremental and says nothing about heights; the source is its code.
- **mokhov-build-systems-a-la-carte**. Andrey Mokhov, Neil Mitchell, Simon Peyton Jones. *Build Systems à la Carte*. ICFP 2018. Core, read in full. Topological, restarting and suspending schedulers: where RFD 5's design sits.
- **murray-naiad-a-timely-dataflow-system**. Derek G. Murray, Frank McSherry, Rebecca Isaacs, Michael Isard, Paul Barham, Martín Abadi. *Naiad: A Timely Dataflow System*. SOSP 2013. Core, read in full. Nested loop-counter timestamps in a working system; a different semantics from `T = [Int]`.
- **nielsen-property-based-testing-for-asynchronous-functional-reactive-programming**. Christian Emil Nielsen, Mathias Faber Kristiansen, Patrick Bahr. *Property-Based Testing for Asynchronous Functional Reactive Programming Using Linear Temporal Logic*. PADL 2026. Core, read in full. LTL properties over clocked traces; only safety can fail on a finite trace.
- **nilsson-functional-reactive-programming-continued**. Henrik Nilsson, Antony Courtney, John Peterson. *Functional Reactive Programming, Continued*. Haskell Workshop 2002. Supporting, read in part. Yampa: second-class signals, both switch timings, and switched-out signal functions as frozen continuations.
- **oeyen-reactive-programming-without-functions**. Bjarno Oeyen, Joeri De Koster, Wolfgang De Meuter. *Reactive Programming without Functions*. Programming 2024. Supporting, read in part. Strongly, eventually and weakly reactive; Bough with `construct` is weakly reactive.
- **ousterhout-why-threads-are-a-bad-idea-for-most**. John Ousterhout. *Why Threads Are A Bad Idea (for most purposes)*. USENIX ATC invited talk 1996. Core, read in full. Asserts events are faster, with no data; its better slide is that callbacks don't work with locks.
- **patai-efficient-and-compositional-higher-order-streams**. Gergely Patai. *Efficient and Compositional Higher-Order Streams*. WFLP 2010 (LNCS 6559, 2011). Core, read in full. Start-time generators, a creation-time semantics, and [F66](./2026-09-24-engine-feasibility-spike.md#f66) as its own biggest problem.
- **pearce-a-batch-algorithm-for-maintaining-a-topological-order**. David J. Pearce, Paul H. J. Kelly. *A Batch Algorithm for Maintaining a Topological Order*. ACSC 2010 (CRPIT Vol. 102). Core, read in full. Batch insertion pays only for large batches.
- **pearce-a-dynamic-topological-sort-algorithm-for-directed-acyclic**. David J. Pearce, Paul H. J. Kelly. *A Dynamic Topological Sort Algorithm for Directed Acyclic Graphs*. ACM Journal of Experimental Algorithmics, Vol. 11, Article No. 1.7, 2006. Core, read in full. One integer per node and a search of the affected region; the probes found it loses when inners are built in the instant.
- **perez-testing-and-debugging-functional-reactive-programming**. Ivan Perez, Henrik Nilsson. *Testing and Debugging Functional Reactive Programming*. ICFP 2017 (Proc. ACM Program. Lang. 1, ICFP). Core, read in full. Record and replay, and bugs that appear only on long traces.
- **pike-copilot-a-hard-real-time-runtime-monitor**. Lee Pike, Alwyn Goodloe, Robin Morisset, Sebastian Niller. *Copilot: A Hard Real-Time Runtime Monitor*. RV 2010. Core, read in full. Constant space by forbidding anonymous streams; a sufficient loop condition.
- **pouzet-modular-static-scheduling-of-synchronous-data-flow-networks**. Marc Pouzet, Pascal Raymond. *Modular Static Scheduling of Synchronous Data-flow Networks: An efficient symbolic representation*. EMSOFT 2009. Core, read in full. Input-to-output summaries of subgraphs; the probes found they never beat the walk on Bough's shape.
- **reflex-reflex-class**. Ryan Trinkle. *Reflex.Class: the Reflex FRP interface*. Hackage documentation 2026. Core, read in full. The richest production switching API; the reason for the old stream at the switch instant, and `Dynamic`'s rule for observing steps.
- **rust-incremental-compilation-in-detail**. The Rust compiler team. *Incremental compilation in detail*. rustc dev guide 2026. Supporting, read in full. rustc's red-green marking: pull with cut-off, and fingerprinting as the main cost.
- **santanna-structured-synchronous-reactive-programming-with-ceu**. Francisco Sant' Anna, Roberto Ierusalimschy, Noemi Rodriguez. *Structured Synchronous Reactive Programming with Céu*. Modularity 2015. Core, read in full. One reaction at a time, and bounded dynamic creation by declared pools with lexical lifetimes.
- **sawada-emfrp-a-functional-reactive-programming-language-for-small**. Kensuke Sawada, Takuo Watanabe. *Emfrp: A Functional Reactive Programming Language for Small-Scale Embedded Systems*. Modularity 2016 companion. Core, read in full. A static embedded FRP that still collects between iterations.
- **schneider-causality-analysis-of-synchronous-programs-with-delayed-actions**. K. Schneider, J. Brandt, T. Schuele. *Causality Analysis of Synchronous Programs with Delayed Actions*. CASES 2004. Core, read in full. A delay moves a cycle into the next step, it doesn't remove it; causality is syntactic.
- **scott-trustworthy-runtime-verification-via-bisimulation-experience-report**. Ryan G. Scott, Ivan Perez, Alwyn E. Goodloe, Mike Dodds, Robert Dockins. *Trustworthy Runtime Verification via Bisimulation (Extended Experience Report)*. arXiv:2607.01363 (extended version of the ICFP 2023 experience report), 2026. Core, read in full. Per-program bisimulation, a year's work, and the admission that a re-encoded semantics is trusted code.
- **sculthorpe-keeping-calm-in-the-face-of-change**. Neil Sculthorpe, Henrik Nilsson. *Keeping Calm in the Face of Change: Towards Optimisation of FRP by Reasoning about Change*. Higher-Order and Symbolic Computation 2010. Supporting, read in part. The start-time argument in full, `runningInEB`'s cut, and when a step signal changes.
- **sculthorpe-safe-functional-reactive-programming-through-dependent-types**. Neil Sculthorpe, Henrik Nilsson. *Safe Functional Reactive Programming through Dependent Types*. ICFP 2009. Core, read in full. Decoupledness in the type, and local time zero for a switched-in residual.
- **shibanai-distributed-functional-reactive-programming-on-actor-based-runtime**. Kazuhiro Shibanai, Takuo Watanabe. *Distributed Functional Reactive Programming on Actor-Based Runtime*. AGERE 2018. Supporting, read in full. Independent sources need one order; source unification is Bough's pump.
- **shiple-constructive-analysis-of-cyclic-circuits**. Thomas R. Shiple, Gérard Berry, Hervé Touati. *Constructive Analysis of Cyclic Circuits*. ED&TC 1996. Core, read in full. The algorithm behind constructiveness, and why it needs reachability over states.
- **tc39-javascript-signals-standard-proposal**. Rob Eisenberg, Daniel Ehrenberg. *JavaScript Signals standard proposal*. TC39 proposal 2024. Core, read in full. Push-then-pull colouring, glitch-free because pull-based, with lossiness the flipside; unsafe features fenced by name.
- **vanderploeg-monadic-functional-reactive-programming**. Atze van der Ploeg. *Monadic Functional Reactive Programming*. Haskell Symposium 2013. Supporting, read in part. Emissions as the semantics, so observing steps is primitive; weak references a non-solution.
- **vanderploeg-practical-principled-frp**. Atze van der Ploeg, Koen Claessen. *Practical Principled FRP: Forget the past, change the future, FRPNow!*. ICFP 2015. Core, read in full. Forgetfulness: a combinator taking its start from the past is inherently leaky. The reason [F89](./2026-09-24-engine-feasibility-spike.md#f89)'s cut holds.
- **vonbehren-why-events-are-a-bad-idea-for-high**. Rob von Behren, Jeremy Condit, Eric Brewer. *Why Events Are A Bad Idea (for high-concurrency servers)*. HotOS 2003. Supporting, read in full. The rebuttal, about independent server requests; it bears on Bough's I/O side, not the engine.
- **vonhanxleden-sccharts-sequentially-constructive-statecharts-for-safety-critical-applications**. Reinhard von Hanxleden, Björn Duderstadt, Christian Motika, Steven Smyth, Michael Mendler, Joaquín Aguado, Stephen Mercer, Owen O'Brien. *SCCharts: sequentially constructive statecharts for safety-critical applications: HW/SW-synthesis for a conservative extension of synchronous statecharts*. PLDI 2014. Supporting, read in part. Whole-program evaluation beat active-parts-only on speed and jitter for small models.
- **vonhanxleden-sequentially-constructive-concurrency-a-conservative-extension-of-the**. Reinhard von Hanxleden, Michael Mendler, Joaquín Aguado, Björn Duderstadt, Insa Fuhrmann, Christian Motika, Stephen Mercer, Owen O'Brien, Partha Roop. *Sequentially Constructive Concurrency—A Conservative Extension of the Synchronous Model of Computation*. ACM TECS 2014. Core, read in full. Program order widens constructiveness, and Bough has none; names "reads before writes" and relative writes.
- **wan-event-driven-frp**. Zhanyong Wan, Walid Taha, Paul Hudak. *Event-Driven FRP*. PADL 2002. Core, read in full. Events compiled to interrupt handlers, never simultaneous: the ancestor of input slots.
- **wan-real-time-frp**. Zhanyong Wan, Walid Taha, Paul Hudak. *Real-Time FRP*. ICFP 2001. Core, read in full. Bounded space and time per step, bought by discarding the old mode at a switch.
- **withoutboats-shifgrethor-i-garbage-collection-as-a-rust-library**. withoutboats. *Shifgrethor I: Garbage collection as a Rust library*. Blog post 2018. Core, read in full. An overview; freedom of reference is what index handles give up.
- **yokoyama-switching-mechanism-for-update-timing-of-time-varying**. Akihiko Yokoyama, Sosuke Moriguchi, Takuo Watanabe. *Switching Mechanism for Update Timing of Time-Varying Values in an FRP Language for Small-Scale Embedded Systems*. ICSCA 2024. Supporting, read in full. The embedded line moved from merging same-time events to ordering them, and collapses bursts to a bit.
