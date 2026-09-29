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
`experiments`, and every number this note establishes carries the
provenance line and command of the result file it comes from, in the
section that quotes it. A paper's number is that paper's claim, marked
"not reproduced". Bough's own numbers are cited to the research note that
measured them._

_Verification: not yet done. Phase 8 of the handoff checks every claim
against its page in the stored copy, re-runs every probe, and records
here what it checked, how, and the errors it found and fixed._

## Semantics and time (RFD 1)

### What the literature says

**Creation time is an old argument, and the literature has a name for
Bough's side of it.** FRP has argued about when a thing starts since the
first higher-order systems. Three lines give the same answer Bough gives:
a thing built at `t` sees nothing from before `t`.

- *Forgetfulness.* FRPNow proves that a combinator which takes its start
  time from an argument that may lie in the past is "inherently leaky",
  and that one which takes it from the monad's "now" is forgetful
  (vanderploeg-practical-principled-frp p. 5, Lemmas 1 and 2). The tool
  is equality up to time observation, a Kripke logical relation over a
  totally ordered time with a least element (pp. 3–5). It names
  Elliott's event join, `accumE` and `accumR` as not forgetful (p. 12,
  fn. 7).
- *Start times.* If a switched-in signal started at system start, the
  implementation would have to remember all past input and catch up,
  which is a space leak and a time leak. So first-class-signal FRP
  starts it at the moment of switching (sculthorpe-keeping-calm-in-the-face-of-change
  p. 7). CFRP's `runningInEB` keeps an event running across a switch and
  drops its occurrences from before switch-in: "only events that occur
  after it is switched in should be observable" (p. 12).
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
p. 3). That is the text's F89 behaviour in miniature, and FRPNow is the
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
F6 and F7 break a rule the text states: their outputs aren't values of
the domain it declares, and F6 also contradicts SwitchC's own initial
value (App. E, §E.5.15). F89 breaks none. In the text, a split built at a
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
for the order itself is Aguado et al.'s process identifiers: sequences of
naturals ordered by proper prefix first, then lexicographically, where a
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
when no `defer` loop chatters, which is F22, and Lee's non-Zeno condition
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
F89 either way. Berry's incarnations come closer. Re-entering a scope
within one reaction makes a fresh incarnation that doesn't see the old
one's events, and a translation that lets the old emission through is
simply wrong (berry-the-constructive-semantics-of-pure-esterel
pp. 133–134, 140–141). That reads like a node built at `t ++ [n]`, but it
is an analogy, not a proof.

**F1's iteration has a clean status, and it isn't "least fixpoint".** A
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

No Rust crate has hierarchical time. DFIR's tick is a batch, and its
`defer_tick` defers to the next top-level tick
(hydro@dfir_rs-v0.16.0 `dfir_lang/src/graph/ops/defer_tick.rs`:6–11).
carboxyl reads cells before the instant, as Sodium does, and has no
simultaneity combine (carboxyl@2a80080 `src/signal.rs`:731–746,
`src/stream/mod.rs`:307–323). salsa iterates a cycle from an initial
value to a fixed point, capped at 200 rounds, and refuses to combine that
with its equality cut-off, with a comment that the combination's safety
hasn't been proved (salsa@salsa-v0.28.5 `src/cycle.rs`:9–58,
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
  in 859 of 6,000 runs, at 4,632 nodes. Every F89-shaped node leaks,
  2,174 of 2,174, and 2,411 of 3,876 F6-shaped ones. The other 47 are
  downstream of an out-of-order argument. Neither cut leaks at any node.
- F7 is out of time order but forgetful. It's a time-order bug, not a
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

One stated reason, not the decision. RFD 1 lists F89 as a place where
"the text breaks its own rules". For F6 and F7 it does. For F89 the text
states no rule that `Split` breaks. Zefira ruled on 2026-09-28 that the
review treats F89 as a semantics change under RFD 1's own rule for
changing an inherited corner, with forgetfulness as the reason that
holds. The cut itself isn't questioned: FRPNow's Lemma 1 has F89's shape,
and the probe finds the text leaking exactly there.

Otherwise none found. Discrete time, fidelity to the text, GHC as the
oracle and Sodium's merge all hold against the batch.

### The options for Bough

1. Keep RFD 1's wording and list F89 among the cases where the text
   breaks its rules.
2. Restate the exceptions: the text's semantics is inherently leaky at F6
   and F89, and Bough picks the forgetful one, with FRPNow's lemmas and
   CFRP's `runningInEB` as precedent and Elliott's `delayOccs` as the
   named alternative. F7 stays a time-order fix. State one rule, a
   creation time on every state-holder and every time-mover.
3. Do 2 and prove the cut, as FRPNow did for one function, for Bough's
   primitives over `T = [Int]`. FRPNow's relation needs only a total
   order with a least element, which `T = [Int]` has.
4. Type the cut: an era, a start-time parameter on signals
   (jeffrey-ltl-types-frp p. 5), which in Rust might be a lifetime per
   `construct` scope. That overlaps the memory section's brand.

For F1, describe the iteration as reaching the unique fixed point of a
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
formally, and treat 4 as part of the memory question. Describe F1 as
reaching the unique fixed point of a guarded system, and cite salsa's
cycle iteration beside it. Keep `steps` public in an `operational`
module: in App. E's model it is sound by definition, and a flag buys
little now that RFD 1 has given up equal-step elision.

### Questions to grill

- Will you accept "the text is leaky at F6 and F89, and Bough picks the
  forgetful semantics" as RFD 1's reason, in place of "the text breaks
  its own rules"? Does F89 then need its own RFD, or a reworded policy?
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
- Should F1 be restated as a fault of the text's whole-history `at`
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
- krishnaswami-ultrametric-semantics-of-reactive-programs for F1's
  fixed point. Needs complete metric spaces and Banach's theorem.
- aguado-denotational-fixed-point-semantics-for-constructive-scheduling-of
  §2 for the identifier order. Needs lattices at Davey and Priestley's
  level.
