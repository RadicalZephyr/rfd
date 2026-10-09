# Reading brief: phase 3 of Bough's FRP literature review

You are reading a batch of papers for a literature review. The review
serves Bough, a Rust FRP library that implements Sodium's denotational
semantics. The review answers two questions: what the literature knows
about Bough's open questions, and whether anything in it contradicts a
decision Bough has settled. Your batch is one slice of that. Other agents
read other slices, one after another.

## What you produce

1. **Reading notes in each source's record**, `<literature>/<stem>.md`.
2. **One synthesis file for your batch**, `<literature>/synthesis/<batch>.md`.
3. **A short final message** (under 400 words): what you read, what's
   worth the lead reviewer's attention, and anything you couldn't do.

Don't commit. The lead reviewer checks your work and commits it.

Write only in `<literature>/` and in
`<scratch>/`. Everything else is read-only.
Never use `git -C`, and don't run git commands that change anything.

## How to read

- Each stored copy is extracted to
  `<scratch>/reading/text/<stem>.txt`, with
  lines `=== page N of M ===` between pages. **N is the page you cite**:
  the PDF's own page index, counted from 1, as a viewer shows it. Never
  cite the printed page number of a journal or proceedings.
- Where the extraction garbles something that matters, such as a
  formula, a figure or a table, read that page of the PDF itself with the
  Read tool's `pages` parameter: `<literature>/<stem>.pdf`.
- A **core** source is read in full, every page, appendices included.
  A **supporting** source is read as far as a claim needs: its
  introduction and conclusion, then the sections that bear on Bough.
  The batch list says which is which. If a core source is too long to
  read in full in your context, stop and say so in your final message
  rather than skimming and calling it read.
- Read with Bough's questions in mind (below), but record what the source
  says, not what it means for Bough. The bearing goes in the synthesis.

## The reading notes

The record is TOML frontmatter between `+++` lines, then the body. Leave
every frontmatter field alone except these:

- `status`: `read-full` if you read every page, `read-sections` if not.
- `sections_read`: for `read-sections`, the sections you read, as the
  source numbers or names them, such as `["1", "2", "4.3", "7"]` or
  `["Introduction", "Conclusion"]`. For `read-full`, `["all"]`.
- `read_on`: today's date from `date +%F`.
- `title`, `authors`, `year`, `venue`: fix them if the stored copy
  disagrees, from its first page. Crossref's casing is often wrong
  ("Von Hanxleden", "O'brien"); use the copy's. List every author in the
  copy's order. Don't change `id`, `file`, `version` or `source_url`.

Then write the body. It is the reading notes, one claim per line:

```markdown
- p. 7, §3.2: <claim>
```

- `p. N` is the extraction's page index. Add the section where the source
  numbers or names one: `§3.2`, `§Evaluation`, `App. B`, `Fig. 4`,
  `Thm. 2`. A claim spanning pages: `pp. 7–8`.
- One claim per line, in plain words, a sentence or two. State what the
  source claims, proves, defines, measures or builds. Keep its own terms
  and name them when they matter: "a *stable* value (□A) is one that…".
- **Numbers exactly as printed**, with units and conditions: "p. 9, §6:
  on the 64-core machine, 1.8× speed-up over …". Never round or convert.
- A theorem gets its statement in words and its conditions. A negative
  result or a limitation the authors state gets a line of its own; those
  are often the most useful claims.
- Quote directly, in quotation marks, only for a definition or a sentence
  whose exact wording matters. Keep quotes short.
- Mark your own inference, when a claim isn't stated outright, with
  `(reading)` at the end of the line. Use it rarely.
- How many lines: as many as the source has claims that the review could
  use, typically 15 to 40 for a core paper, more for a thesis or book,
  5 to 15 for a supporting source. Cover the whole source, not only
  the parts that bear on Bough: the drafting agent needs to know what the
  source is about, its method, its results and its limits.
- Group by section in page order. No headings inside the body, no prose
  paragraphs, no commentary on Bough.

Every line you write must be checkable against the stored copy's page by
a verifier who reads only that page. Get the page right. If you aren't
sure of a claim, check the page again or leave the claim out.

## The synthesis file

`<literature>/synthesis/<batch>.md`. This is your reading of
what the batch means for Bough, and it is marked as that. It's where the
drafting agent will start for your dimensions. Its shape:

```markdown
# <Batch title>: what the sources mean for Bough

_Claude's reading, phase 3, <date>. The claims are in the records; this
file cites them by stem and page. Nothing here is a source's claim unless
it cites one._

## Per source

### <stem>
2 to 6 lines: what in it bears on which of Bough's open questions or
settled decisions, with page citations, and how. Say plainly when a
source turns out to matter little.

## Settled decisions the evidence contradicts
Each with the decision, the source and page, and why it contradicts.
Or "None found." Be strict: a contradiction means the evidence says the
decision's stated reason is wrong, or that it breaks something Bough
requires. A different design choice made elsewhere is not a
contradiction; it goes under options.

## Open questions: what the batch says
For each of Bough's open questions (numbered as below) that the batch
touches: what the literature knows, the options it gives Bough, and a
leaning, labelled "Leaning:". Cite stem and page for every claim.

## Candidate probes
Experiments in Rust that would settle a claim for Bough, small enough to
build in an afternoon in a scratch crate, with no dependency on Bough's
engine (it's not published). One line each:
`rfd-NNNN-<slug>` — the RFD it serves — the claim it would settle —
performance or not.
Only propose probes whose answer would change a leaning. Fewer is better.

## Questions to grill
Questions for Zefira that the batch raises. Each one sentence.

## Reading paths
For each core source: what a reader needs first. For example "needs
natural deduction and Kripke semantics" or "self-contained".
```

## Bough in brief

Bough is a Rust library for discrete-time, push-based FRP. Its semantics
are Sodium's (Blackheath and Jones, *Functional Reactive Programming*,
Manning 2016), whose executable denotational semantics,
`Denotational.hs` v1.1, is Bough's test oracle, run under GHC. The
engine is designed in seven RFDs, and a throwaway spike built all of it
and matched GHC on about 72,000 random programs.

### The vocabulary

- **Stream**: discrete events, at most one per instant. **Cell**: a value
  that steps at instants; Sodium's "behavior". Read-through cells
  (`map_cell`, `lift`, `switch_cell`) compute on read and memoize;
  stateful cells are `hold` and the accumulators.
- **Instant / transaction**: one logical time step. Time is a list of
  integers, `T = [Int]`: child instants `t ++ [n]` run after `t` and
  before its successor, depth first. `split` (one event per item of a
  collection, each in its own child instant) and `defer` (the event, one
  child instant later) create them.
- **Cells are read strictly before the instant.** `snapshot`, `gate` and
  `sample` see the value before transaction t, so a cell read is never an
  ordering dependency inside t.
- **Switching**: `switch_stream` and `switch_cell` over a cell of streams
  or cells; the higher-order, dynamic-graph part. `construct` (Sodium's
  `execute`) builds new graph at an event, inside a transaction.
- **Loops**: `cell_loop`, `stream_loop`, declare then close. Legal loops
  go through a cell read from before the instant, or a child instant.
- **Operational primitives**: `steps` and `steps_with_current` (Sodium's
  `updates` and `value`) expose a cell's steps, which the book says a true
  FRP system should hide.
- **Listeners** run after commit and can't read or send into the graph
  synchronously. I/O code reaches the engine through handles whose calls
  queue for the next `pump`.

### Settled decisions (check their stated reasons; report only contradictions)

1. **Fidelity to Sodium's `Denotational.hs` v1.1**, except where the text
   breaks its own rules of time order and creation (findings F6, F7, F89:
   a `switch_cell` created late, a `split` fed by its own children, a
   `split`/`defer` built at a child instant). RFD 1.
2. **Discrete time**, no continuous-time module.
3. **GHC is the oracle**; porting the semantics to Rust is shelved,
   because the text hangs on legal loops (F1) and a port would need
   the same fixed-point machinery.
4. **A single-threaded engine.** Handles (`Io`, `RemoteIo`) queue every
   call for the next pump. The stated reasons: the engine stays simple
   and deterministic, the host owns the schedule, and a transaction is a
   pure function of its inputs. RFD 6.
5. **Scheduling is a depth-first mark then a flat evaluation loop.** The
   DFS's reverse post-order over the affected region is a topological
   order. No ranks, no priority queue, no memo checks on the fast path.
   Memoized pull only for a `switch_cell`'s new inner at the switch
   instant and for nodes created during the instant. Rejected:
   rank-ordered push (Sodium's; ranks must exceed every dynamically
   reachable inner, which forces re-ranking mid-transaction) and pure
   pull (a stamp check per read, recursion as deep as the graph). RFD 5.
6. **Memory: a `u32` generational arena, tracing mark-sweep from explicit
   roots** (live listeners, anchors). `Trace` is a safe trait with a
   derive; a stale token is a loud error, never unsafety. Rejected:
   reference counts (can't see cycles through values) and weak refs
   (collect deselected inners that must keep accumulating). Collection
   runs between units, never inside one. Closures can't be traced, so a
   closure's token captures are declared with `depends`, checked only
   at run time. RFD 3.
7. **Streams are linear and move by value; cells lend by reference.**
   `share` makes a stream multi-consumer and needs `Clone`. Adapters
   (`map`, `filter`, `snapshot`…) fuse into one node like iterator
   adapters. Read-through cells are lazily memoized; eager evaluation at
   commit was rejected as unboundedly worse for a high-rate cell read by
   a slow observer. RFD 4.
8. **The dependency graph stays acyclic.** Cell reads before the instant,
   and `split`/`defer` child instants, break cycles. Checked at loop
   close, at a switch's first link, and at every switch move (a move that
   closes a cycle panics and poisons). RFDs 2 and 5.
9. **A transaction is atomic visibility, not abortable.** Holds commit
   together; listeners see only committed state. A panic poisons the
   runtime; there is no rollback. RFD 5.
10. **The core is `no_std` over `alloc`**, `std` a default feature. No
    static (compile-time graph) engine in core; no public backend trait.
    A graph that isn't growing allocates nothing per transaction. RFD 7.

### Open questions (where the effort goes)

1. **Capture declarations and space leaks in higher-order graphs.**
   `depends` and the linear-move rule are checked at run time. Could
   types do it (modal types, lifetimes, linearity)? A forgotten
   declaration is a stale-token error at use (F62). `depends` has no
   inverse: a declaration inside a `construct` on a long-lived node kept
   fifty screens (F63). Garbage is evaluated until collected: after 9,000
   screens a navigation took 596 µs per transaction uncollected, 528 ns
   collected (F66). RFD 3.
2. **Incremental ordering and cycle detection under switching.** Each
   switch move re-checks acyclicity by walking everything upstream of the
   new inner: about 9 ns a node, 121 µs for 10,000 upstream nodes (F50).
   Moves are batched and checked on the final graph, since checking one
   move at a time refuses a legal program where two switches reverse a
   dependency (F46). Reads through `switch_cell` carry Brent's cycle
   detection (about 2 ns per switch passed) because a read can go round a
   cycle not yet checked (F19, F56). Would incremental topological order
   or incremental cycle detection do better? Checking every declared
   candidate at build was raised and not tried. RFD 5.
3. **The causality boundary of the loop rule.** The rule: the dependency
   graph (excluding pre-instant cell reads and child instants) stays
   acyclic. F3: an earlier rule ("every loop passes through a hold")
   accepted `c = hold 0 (merge ticks (map (+1) (steps c)))`, which has no
   evaluation order. Does acyclicity accept exactly the loops the
   semantics give meaning to? Loops mixing `switch_stream` selection,
   `split` and `construct` are untested. Could it be checked statically,
   at compile time?
4. **The formal status of the creation-time cuts** (F6, F7, F89, and the
   same cut applied to `construct`) and of fixed-point loops (F1: the
   text's `at` hangs on a counter that stops at ten; the oracle iterates
   to a fixed point), under hierarchical time `T = [Int]`. Is there a
   semantics in which the cuts are the right answer, not a patch?
5. **The bounded embedded tier**: a fixed number of arena slots, bounding
   `construct`, the depth of `split` nesting, and queue growth. RFD 7.
6. **Construction cost, and fusion's compile-time blow-up.** Building a
   node costs about 15k wasm instructions (Oort dogfooding). Fusion
   compiles every materializer again per nested chain type: 182 chain
   types and a 36 s release build at depth two, 1,640 and 367 s at depth
   three (F36).
7. **Simultaneity at the edge.** An input slot (for interrupt handlers)
   folds a burst between two pumps with an associative fold. Each
   external cause is one unit and one transaction; two slots are never
   simultaneous. RFDs 6 and 7.
8. **Concurrency.** Find a source for the single-thread rationale, or
   refute it. An earlier design note claimed threading costs overhead,
   with no source.
9. **Cells of collections at scale, and incremental collections.** The
   usual FRP advice is cells of collections rather than collections of
   cells, but a cell of a collection propagates *that* it changed, not
   *what* changed.
10. **Operational primitives** (`steps`, `listen_once`): are they
    observationally sound, and should `steps` go behind a feature flag?

### Where to look in Bough, if you need more

Read-only. The RFDs: `<rfd>/src/rfd-000N-*.md`
(1 principles, 2 build/IO split and loops, 3 memory, 4 values, 5
transaction, 6 I/O edge, 7 targets). The glossary:
`<rfd>/GLOSSARY.md`. The spike's findings
F1 to F95: `<rfd>/research/2026-09-24-engine-feasibility-spike.md`.
You shouldn't need them for most papers; the brief above is enough.

## Your tools and limits

- `pdftotext`, `pdfinfo` and Python 3.14 are installed. The Read tool
  reads PDF pages as images when the text isn't enough.
- No web access is needed. Don't fetch anything.
- Don't start sub-agents.
