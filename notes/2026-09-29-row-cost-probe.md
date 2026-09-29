# What a thousand rows cost

_2026-09-29. An experiment to run, from a conversation about where
Bough fits after the
[literature review](../research/2026-09-28-frp-literature-review.md).
Nothing here has run._

## Why

Bough is to prove itself as a foundation for app frameworks, and we
plan to build the first one on it, most likely for the web. The public
yardstick there is js-framework-benchmark, a table of rows under six
buttons, with keyed entries for Leptos, Sycamore and Dioxus. Five of its
nine tests build, replace or clear rows, so building and tearing down
rows is most of what it measures, and that is what we know least about.
The one per-node number we have is the Oort fighter's, about 15k wasm
instructions a node, through a crate boundary that stops inlining
([What an Oort fighter found first](./2026-09-26-oort-fighter-first-findings.md)).

Its select test shows a second cost. Selecting a row changes two rows
in a thousand, but a step to an equal value is still a step, so a
derivation per row from one selection cell steps in every row and
reaches every row's listener. The signals engines stop the other 998 at
a `PartialEq` check, and `reactive_graph`'s `Selector` doesn't reach
them at all.

## The experiment

One row, built the same way in three engines, at the versions the
review read at source:

- bough, `spike/io-edge` at `b752520`: a label cell from a `hold`, so
  it can change; a `map_cell` from one shared selection cell that says
  whether the row is selected; and a `listen_cell` on each, standing in
  for the DOM writes. The listeners register through the `Io` at the
  next pump, as bough-gtk's rows do, so a row's build counts the
  transaction that constructs it and the pump that registers its
  listeners. In `Local`, the web mode, and in `Threaded`, since
  `reactive_graph` pays for `Send + Sync` and `sycamore-reactive`
  doesn't.
- `sycamore-reactive` 0.9.3: a signal, a `create_selector` (its
  `create_memo` doesn't cut off) and two effects, in a child scope per
  row.
- `reactive_graph` 0.2.15, with its `effects` feature: an `RwSignal`,
  a `Memo` and two `RenderEffect`s under an `Owner` per row, then again
  with a `Selector` in place of the memos. Its docs promise only that a
  render effect's first run is synchronous, so a select drives the
  executor to idle before the clock stops.

Each engine builds the rows after one event, as a framework would, and
tears them down its own way: bough by dropping the listeners, switching
the rows out and collecting; Sycamore by disposing the scope;
`reactive_graph` by dropping the render effects and the owner. For
1,000 and 10,000 rows, measure:

- building them, with every listener's and effect's first run;
- selecting one row, and how many listeners or effects ran;
- tearing them down;
- bytes allocated per row, and bough's live nodes per row.

Native first, timed with criterion and counted with gungraun, as
`bough-bench` does. Then `wasm32-wasip1` under wasmtime, whose fuel
costs about one unit a wasm instruction, so it can sit beside Oort's
gas. The code goes in `experiments`, with the review's probes.

## What it decides

- Whether construction comes first in the real build. Close to the
  signals engines, the build starts where the review said, with RFD 3
  and RFD 5. An order of magnitude off, the framework has nothing to
  show on the benchmark until construction is fixed. What counts as
  close is set before the run, so the result can't move the bar.
- Whether the core needs a keyed dispatch, like `Selector` or Solid's
  `createSelector`, so a selection reaches only the rows it changes.
  That's a question for RFD 4, and RFD 5 wants the answer too: with a
  dispatch, a select is almost all quiet, which is where the review
  found heights win.

## What it won't tell us

It measures the spike, not the real build, so it gives orders of
magnitude. It leaves out the DOM, which each framework reaches through
its own renderer, and server rendering, which is still an open
question.
