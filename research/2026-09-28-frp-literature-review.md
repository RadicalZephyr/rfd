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

## Switching and dynamic graphs (RFDs 2, 5)

### What the literature says

**Sodium's switch-instant semantics is the combination Reflex
recommends.** Reflex's default `switchHold` uses only the old event at
the switch instant, because that "avoid[s] many potential cyclic
dependency / metastability failures" and is faster. The prompt variants
exist and are discouraged (reflex-reflex-class p. 15). Its `hold` makes a
sample at the switch instant see the old value (p. 7). Yampa offers both
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
  reactive-banana 1.0 shipped that as its `Moment` monad
  (apfelmus-frp-release-of-reactive-banana-version-1-0 p. 1).
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
bound.** Every efficient cycle detector keeps a topological order
(haeupler-incremental-cycle-detection-topological-ordering-and-strong-component
p. 3). Pearce and Kelly keep one integer per node. An edge that already
agrees with the order costs a comparison, and one that doesn't searches
only the affected region between its ends
(pearce-a-dynamic-topological-sort-algorithm-for-directed-acyclic
pp. 3, 5, 8). On random 2,000-node graphs the simple array beats the
asymptotically better algorithms, because ordered lists are expensive
(pp. 15–16, 20; not reproduced). HKMST's limited search is Bough's
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

**F46 needs only an order of operations.** If every deletion of a
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
twice (reactive_graph@v0.8.21 `reactive_graph/src/effect/immediate.rs`:352–354).
Leptos, Sycamore, salsa and Incremental all tie a node's life to the run
that created it: an owner's re-run disposes what the last run made
(reactive_graph@v0.8.21 `reactive_graph/src/owner.rs`:34–46;
sycamore-reactive@0.9.3 `src/signals.rs`:123–143;
salsa@salsa-v0.28.5 `src/tracked_struct.rs`:186–191). carboxyl's stream
`switch` re-registers on each new inner and kills the old callback
through a dropped token (carboxyl@2a80080 `src/stream/mod.rs`:445–475).
`incremental-topo` packages Pearce and Kelly's order over a generational
arena (docs.rs/incremental-topo/0.3.1).

### What the probes found

Six probes built RFD 5's relink check against the alternatives, on a
10,147-node UI-shaped graph with 750 `construct`-style subgraphs. Four
workloads build 0%, 20%, 50% and 100% of their new inners during the
instant: `settled`, `mixed`, `churn` and `lazy`.

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
  F50's ten thousand (`rfd-0005-bounded-relink-check`).
- **A Pearce–Kelly array loses badly when inners are built during the
  instant.** It is 0.018 of the walk's time on `settled`, and 20, 91
  and 250 times worse on `mixed`, `churn` and `lazy`. A new node goes
  at the end of the order, so the first link searches the switch's whole
  downstream (wall-clock). Per-subgraph summaries never beat the walk:
  1.28 to 1.40 of it (wall-clock).
- **An order-maintenance list that places new nodes on the small side
  bounds it on this shape** (`rfd-0005-small-side-order`). Placing the
  new side just before the switch, with a backward search or HKMST's
  two-way search, costs 0.017, 0.10, 0.29 and 0.62 of the walk's time on
  the four workloads, and a node built costs about 14% more than without
  an order (wall-clock).
- **It isn't bounded in general.** On an adversarial shape both searches
  cost 1.7 to 8.8 times the walk unless the switch's downstream is much
  smaller than the new inner's upstream. On a cycle none beats the walk
  by much. The backward search's cost is its search, sort and move, not
  relabelling: with fresh spacing it relabels nothing and still costs
  2.6 to 7.1 times the walk's instructions on the adversary. Dropping
  the sort, moving the set in DFS post-order instead, brings it to 1.7
  to 3.0 times the walk's time (wall-clock), and to 0.73 to 1.13 on
  cycles.
- **Where the list pays.** On a mixed adversary, a new inner reading
  some old nodes before the switch and some new ones after it, the
  no-sort backward search beats the walk once the old upstream is about
  as large as the new side: at 1,000 new nodes it costs 1.24 of the walk
  with 1,000 old ones and 0.23 with 10,000 (wall-clock). The instruction
  counts put that line near twice.

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

- Is the 121 µs of F50 a shape real programs hit, or is a real new
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
  see whether F46's order of operations ever matters in practice.

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
to "in some reachable state, this is undetermined". Scade's users accept
the extra restriction
(pouzet-modular-static-scheduling-of-synchronous-data-flow-networks
p. 18).

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

**F3 isn't a program constructiveness would rescue.** In
`c = hold 0 (merge ticks (map (+1) (steps c)))`, an instant without
`ticks` gives x = x, which is Esterel's `present O then emit O`, whose
least fixpoint is ⊥ (berry-… pp. 31, 41). SC's check, Keating's direct
dependency and DBSP's strictness all refuse it. It needs `steps`, and the
book's ten core primitives "give you no way to convert a cell into a
stream" (blackheath-functional-reactive-programming, ch. 8, §8.4; ch. 2,
Table 2.1). So "every loop passes through a hold" may be the right rule
for the core, and the operational primitives are what break it. That
ties open questions 3 and 10.

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
pp. 5–6); Bough's child instants nest inside the transaction. So F22, a
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
501–512). None of them checks loops through switching, since none has
Sodium's switches.

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
  as mutual defaults, `s0 = i0.or_else(s1)`, `s1 = i1.or_else(s0)`, and
  2 value-dependent. None looks like a program anyone means to write,
  and every one outside (a) breaks when another input fires alone or an
  instant is a child instant.
- Letting gates read holds of the loop, so cells take only reachable
  states, adds 10,491 more under any presence: 10,436 behind a gate
  that's closed in every reachable state, which is dead code refusal
  catches, and 55 from two complementary cells, which is one cell with
  `gate(c)` and `gate(!c)` again. With at least one input firing, 17
  more sit behind constant cells.
- Every program of two to four nodes and every cell binding: of
  3,147,279 refused over two inputs, 13 programs are constructive with a
  cell that changes, in 13 minimal forms, all of four nodes, and all
  break when a third input fires alone. Over three inputs, of 3,468,034,
  none.

**A one-bit marker checks `close`, and can't check switches**
(`rfd-0002-decoupled-marker`). Each stream and cell type carries a mark,
decoupled or not, and `close` requires decoupled.

- It refuses F3 at compile time, with the error "this loop's definition
  depends on a loop's forward reference in the same instant", and builds
  F1's counter. On the first fixture set it refused all 6 illegal loops
  and 3 of 10 legal ones: a helper returning `impl Source`, a helper
  taking a plain `Cell<u32>`, and two loops where one resets the other.
  Helpers generic over the mark fix the first two.
- Extended to `gate`, `sample`, `split`, `defer` and `depends`, it still
  refused every illegal fixture. It can't see sampling a loop cell
  before close, which stays a run-time panic.
- Compile time, on the idle machine: 1.02 to 1.06 of the baseline on the
  hand-written fixtures, and 1.03 to 1.16 on a generated program of 512
  depth-three chains. Cuoq-style rows cost 1.05 to 1.25 there.
- **Every marker design accepts an illegal loop smuggled through a
  switch.** A loop or a construct hands a switch its own consumer's
  steps as a token, and it builds: under the plain marker, under a
  `close` that re-marks its token decoupled, under rows, and inside a
  construct at a child instant. A switch's reach grows after build, so
  neither one bit nor rows can make a switch's moves a compile-time
  check.
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
2. Add the one-bit marker at `close`, which makes F3 and its relatives a
   compile error for a few percent of compile time, and keep the
   run-time check at a switch's first link and moves.
3. Also mark switch outputs `Switched`, which makes the smuggle a compile
   error at the price of refusing a switch inside a switch and an inner
   that reads an open forward.
4. Go constructive: accept cycles through exclusive gates.

For F22: accept it as the user's bug, bound child-instant depth at run
time, or require every `defer` loop to pass a filter or a bound.

### Claude's leaning

Option 1, and say in RFD 2 that the rule is Lustre's and Esterel v4's,
sound and knowingly incomplete, with Keating and Gale's theorem as its
justification for opaque functions. Name the refused class, exclusive
gates, and point to switching as how Bough writes it. Option 2 is cheap
and catches a real mistake at compile time, but it covers `close` only,
costs a mark parameter on every helper signature, and the run-time check
stays whatever happens. I'd hold it until F3-shaped mistakes show up in
real code. Treat F22 as liveness, bounded at run time in the embedded
tier and left to the user elsewhere.

### Questions to grill

- Do you want the loop rule to be exactly the class the semantics gives
  meaning to, or a sound subset that's easy to state? Berry's users and
  Lustre's chose differently.
- Have you wanted a Bough program whose only same-instant cycle runs
  through two exclusive gates that a `switch_stream` couldn't write
  acyclically?
- Is F3 a `steps` problem, so that "every loop passes through a hold"
  holds for the core, and does that go into the case for fencing
  `steps`?
- Would a marker that catches F3 at compile time be worth a mark
  parameter on every helper, given that it can't cover switches?
- Is F22 something to refuse statically, bound at run time, or leave as
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
  dependencies, or by suspending, which is memoized pull
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
the only one that is glitch-free without lossiness or a per-read stamp.
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
cut-off (reactive_graph@v0.8.21 `reactive_graph/src/lib.rs`:67–69,
`src/computed/inner.rs`:69–124). sodium-rust runs changed nodes at the
end of a transaction in DFS order with a visited flag and no ranks
(github.com/SodiumFRP/sodium-rust @3e93021
`src/impl_/sodium_ctx.rs`:233–262, 298–355). incremental-rs keeps
Incremental's design, a queue per height up to a maximum
(github.com/cormacrelf/incremental-rs @5ba8209 `src/recompute_heap.rs`).
DFIR's whole scheduler is a topological order fixed at compile time, one
closure per tick (hydro@dfir_rs-v0.16.0 `dfir_lang/src/graph/meta_graph.rs`:813–816).
salsa is pull only: it validates a memo's inputs in the order they ran
(salsa@salsa-v0.28.5 `src/function/maybe_changed_after.rs`:591–597).

### What the probes found

Four probes set schedulers against RFD 5's mark and flat loop. Two
shapes: RFD 1's UI and frame shapes with static heights, and the
switching section's 10,147-node graph under its four workloads, with
filters whose pass rate sets the quiet share of each marked region. The
wall-clock ratios below are each scheduler's time over the mark's, from
the idle machine. The instruction counts, taken first, put every
crossover lower; wall-clock is what counts here.

- **Static heights with a bucket queue** (`rfd-0005-heap-vs-mark-on-quiet-regions`).
  On the 9,997-node UI shape the bucket queue costs 1.25 of the mark
  when every marked node fires, 1.15 at 10% quiet, 1.02 at 26% quiet,
  0.79 at 50% and 0.21 at 89%. A binary heap costs 2.58 when everything
  fires and breaks even between 45% and 75% quiet. On the frame shape the bucket
  queue costs 1.09 at 64 inputs and 0.94 at 1,024, and the heap 1.50 at
  both. So the log factor is real for a binary heap and small for a
  bucket queue. In instructions the mark was about 100 of every 130
  instructions a marked node costs.
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
  touching at most one node, and never below the cursor, since a switch
  sits after its selector. But one raise touched up to 7,421 nodes, so a
  single link can cost a large pause.
- **The raise finds cycles.** It refused exactly the walk's set of
  moves, at 10 to 28 nodes a refused cycle.
- **Heights grow only when cycles are refused.** Over 3,000 transactions
  the largest height grew from 72 to between 242 and 367, all of it from
  interrupted raises at refused cycles; without them it plateaus at 78.
  Under RFD 5's rule a refused cycle poisons the runtime, so that growth
  never happens.
- **Maintained sparse labels lose the bucket queue**
  (`rfd-0005-maintained-rank-queue`). Ranks from the switching section's
  order-maintenance list, in a binary heap, cost 2.35 to 2.55 of the
  mark when everything fires and break even between 56% and 75% quiet. A
  radix heap does no better. Keeping the labels is cheap: 0.02 to 0.61
  of the walk's upkeep.
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
program's quiet share is known. The UI shape is where Bough is slow
today, a UI's marked regions are plausibly mostly quiet, and heights
would also give the relink check for free. But the flat loop is what
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
p. 8). In Bough those are a forgotten `depends`, F62, which ends in a
stale token, and a `depends` with no inverse, F63, which kept fifty
screens on the engine spike
([research](./2026-09-24-engine-feasibility-spike.md)). No source in
the batch fixes the second one while keeping Sodium's semantics.

**The modal line catches F62 and permits F63.** In the RaTT line a value
is *stable* when it can't reach temporal data, and a closure stored in the
graph, run at later instants, may capture only stable values
(krishnaswami-higher-order-functional-reactive-programming-without-spacetime-leaks
pp. 3–4; bahr-modal-frp-for-all pp. 5–8). Read "temporal data" as "a
Bough token". Then a `construct` builder capturing a cell token is
Rattus's rejected `leakyMap` (bahr-modal-frp-for-all p. 8), and a closure
that captures a delayed location and runs a step later dereferences a
collected one, which is F62 caught by a type rule
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
liveness from the roots, and the one answer to F66 that keeps something
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
can generate a `Collect` impl for a closure or a generator, "nor any
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
expression is declared by hand, the library can't check its own
discipline, and the author's conclusion is to leave the library for a
compiler (acar-self-adjusting-computation pp. 131, 138, 233, 278).

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
`src/impl_/lambda.rs`:5–8, 196). It needs the same declarations and adds
counting on top. Deferred counting still counts writes into the heap
(bacon-… p. 5), which for Bough means every token stored in a value, and
a `Copy` token gives no hook there. So RFD 3's second reason, that
tracing needs no counts and tokens can be `Copy`, is the one that
carries.

**`Trace` is safe for generation-checked indices, and nothing disagrees.**
Every source that makes its trace trait `unsafe` does so because a missed
field frees memory still reachable through a pointer
(goregaokar-… p. 4; kyren-gc-arena p. 2;
jeffrey-josephine-… p. 9). None argues that a missed field is unsafe when
handles are checked indices, which is RFD 3's distinction.

**Every GC-based FRP has F66, and none fixes it but by collecting
sooner.** Garbage is evaluated until it's collected. Elerea calls it its
"biggest problem" (patai-efficient-and-compositional-higher-order-streams
p. 13). FrTime's strong update queue keeps about half the dead signals
alive (cooper-integrating-dataflow-evaluation-into-a-practical-higher-order
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
collection" is Bough's "collection between units, never inside one", and
it is `no_std` over `alloc` (gc-arena@v0.7.0 `src/lib.rs`:1–6,
`src/arena.rs`:209–223). To hold a pointer outside a mutation you stash it
in a `DynamicRootSet` and get a handle whose drop unroots it
(`src/dynamic_roots.rs`:14–53), which is Bough's `Anchored`. Leptos and
Sycamore hold `Copy` handles in a generational slot map, free a node when
the owner scope that made it re-runs or drops, and panic with the place
it was defined when a disposed handle is used
(reactive_graph@v0.8.21 `reactive_graph/src/owner.rs`:34–46,
`src/traits.rs`:66–90; sycamore-reactive@0.9.3 `src/node.rs`:72–121,
`src/signals.rs`:150–194). That makes `depends`'s missing inverse
automatic, at the price Bough refused: a node lives exactly as long as
the scope that made it. carboxyl's derived streams hold their parents
strongly and are held weakly back, "downstream owns upstream", which is
the weak-reference scheme RFD 3 rejects (carboxyl@2a80080
`src/stream/mod.rs`:191–246). sodium-rust has `depends` under the name
`lambda1(f, deps)`.

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
1.0. On F66's shape RFD 3's trigger collects about every second
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
tenth on F66's `nav` shape, where there's little garbage to pace. Its
fast path, a click on a clean arena, is unmeasurable (0.994). A term on
every region node, `total`, collects spuriously when regions are large
beside the live set, and costs 2.2 times on the same click, spurious
collections included.

- Under four inputs firing at uneven rates with live regions that grow,
  `excess` collects about as often as an oracle that paces on true dead
  work, 37 times against 34, for 0.7% more visits. It misses only
  garbage folded into an input's reference, and fires spuriously once
  every 270 to 430 quiet units.
- Garbage on a slow input lags: `excess` misses 500 to 600 units, up
  to 300 in a row, peaking at 1.9 times the survivors. A reference counting only
  region nodes born before the last collection (`marked`) misses none,
  for 0.3% more instructions.
- **No region term sees garbage a dropped guard releases.** A release
  never shrinks a region before the next collection, since released
  nodes stay in dependents lists until pruned. With guards dropped
  through a long quiet stretch and no growth, both terms missed 2,079
  units in a row, peaking at 11.1 times the survivors, and RFD 3's
  release term never fired: 90 releases against about 14,000 survivors.
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

**A lifetime brand makes F62 a compile error on stable**
(`rfd-0003-branded-captures`, `rfd-0003-brand-erasure`). Tokens carry a
fresh `'g` per `Runtime::mutate`, and captures go through `.with(env)`.

- A forgotten capture, one through a helper, one through a switch and
  one through an inner all fail with E0521, "borrowed data escapes
  outside of closure", and every legal fixture builds, including a hold
  of a struct of tokens, a construct capturing three, anchoring, the
  RFD 4 screens example and a switch among captured tokens. `map_to` of a
  token still builds, which is safe since F94 made `map_to` trace its
  value.
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
  borrowed view costs 0.98 to 1.02 everywhere, but changes the API: a
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

Two results disagree with themselves and need a recheck. The incremental
mark's single-unit benches say the barriers' fast path costs 18% to 30%
of a unit, while a whole run with barriers costs 0.7% and the instruction
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

For F62:

1. Keep run-time `depends`, whose failure is a loud stale token.
2. Brand tokens with a lifetime, captures through `.with(env)`, values
   stored through a derived `Rebrand`, and borrowed views where a
   token-bearing collection is read or accumulated.
3. Scope lifetime to creation, as Leptos and Sycamore do. That gives
   `depends` an inverse and changes Sodium's semantics.

For F63: nothing in the literature fixes it without 3. `once()`, which
releases its upstream after one event, is the book's structural answer
to the one case it shows.

For the trigger:

1. Keep RFD 3's trigger.
2. Add the per-input work term, with the born-before-the-last-collection
   reference for lagging inputs, and find a release term that sees
   released garbage, which no probe has.
3. Also slice the mark, prune and sweep with a fixed budget, for hosts
   that care about the pause.

### Claude's leaning

For F62, option 1, and rewrite the reason: the brand is possible and
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
- Is F63 a bug to prevent, or an explicit leak the program asked for,
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
