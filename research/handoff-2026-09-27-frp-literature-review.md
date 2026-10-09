# An FRP literature review for Bough: the handoff

_2026-09-27. For a Claude Code session in the Fedora container on
Zefira's desktop, from a grilling session in Claude Cowork. The review
runs over several sessions, one per phase. This file is its plan, and
through the dated additions at its end, its state. Read all of it at the
start of every session. Nothing here repeats what the RFDs, the research
notes or the conventions already say; it points at them._

## The goal

One research note, `research/<date>-frp-literature-review.md` on this
branch, dated the day drafting starts. It tells Zefira two things: what
the literature knows about Bough's open questions, and whether anything
in it contradicts a decision Bough has settled. She reads a must-read of
at most 1,000 words. A verification pass makes the rest trustworthy
without her reading it.

The review gates the real build, not RFD publishing. Its findings must
land before code depends on the RFDs, RFD 3 and RFD 5 above all.

## Where things are

- **This branch.** `research/frp-literature-review`, off
  `origin/rfd/revision-after-the-spikes` at `1b30f27`, the unpublished
  revision of RFDs 1 to 7 (RadicalZephyr/rfd#3). This handoff is its
  first commit. No worktree exists yet. Make one before anything else:
  `git worktree add ~/prog/bough/rfd-literature-review
  research/frp-literature-review`, run inside `~/prog/bough/rfd`. Work
  only in the worktree. The main checkout is on
  `spike/engine-feasibility` and stays untouched.
- **What the review audits.** The revised RFDs, `src/rfd-000*.md`, and
  `GLOSSARY.md` on this branch. Where the revision landed:
  `notes/2026-09-27-rfd-revision-landed.md`, at commit
  `1b30f27e58921dec68f34895d5b6ea74b1aa8766`.
- **Bough's evidence.** `research/`, especially the engine spike's
  findings (F1, F3, F36, F46, F62, F89 and the rest) in
  `research/2026-09-24-engine-feasibility-spike.md`, and the open risks in
  §10 of `research/2026-09-24-engine-architecture-brief.md`. A dogfooding
  note on construction cost is on the local branch `notes/oort-fighter`.
- **Scope and goals.** `~/prog/bough/claude-planning/REQUIREMENTS.md` and
  `PLAN.md`. Zefira's own open review notes on the RFDs:
  `~/prog/bough/claude-planning/Changes to Bough RFDs.md`.
- **Sodium.** The Manning book as markdown in
  `~/prog/sodium/frp-mdbook/src/`; cite it by chapter, and never store a
  copy. Its semantics appendix is `src/appendix/denotational-semantics.md`.
  Three bugs in the semantics text: `~/prog/sodium/sodium-denotational-bugs/`.
  The vendored `Denotational.hs` and the oracle:
  `~/prog/bough/bough/bough-oracle/`.
- **literature.** `~/prog/bough/literature`, one commit (`1e3d79c`), a
  README only. It has no remote; if it ever gets one, it must be private,
  because publisher PDFs can't be redistributed.
- **experiments.** `~/prog/bough/experiments`, one commit (`adc7b76`),
  an empty package `bough-experiments`.
- **Conventions.** `~/prog/decisions/docs/decisions/README.md`, its
  Research section and "Dating claims that will not age well", and
  `~/prog/decisions/docs/decisions/experiments/README.md`. Follow them
  for experiments and evidence. Ignore everything about writing decision
  records. This repo's own rules for research and notes are in
  `research/README.md` and `notes/README.md`.

## Rules

- **Never push.** Zefira pushes.
- **Write only in the worktree, `literature` and `experiments`.**
  Everything else is read-only.
- **At most two sub-agents at a time, one by default.** Quota matters
  more than wall time. A run stopped by a usage limit costs more than a
  slow one.
- **Commit as you work, in logical units,** in the style of this repo's
  history: a plain sentence for a subject, a prose body that says why,
  and Claude Code's trailers.
- **A claim is attributed only to a source that was read,** and it is
  checked against the stored copy.
- **Numbers have three homes.** A number the review establishes
  reproduces from `experiments`. A paper's number is quoted as that
  paper's claim, with its page, and marked "not reproduced". Bough's own
  numbers are cited to the research note that measured them.
- **Stop at the stops the phases name, and at any blocker.** A blocker is
  a problem the plan gives no way through: a crate that won't build, a
  source that can't be reached and isn't on the fetch list, an ambiguous
  probe result, a finding that contradicts a settled decision, or
  anything that would change this plan. Choices inside the plan are
  yours; record them in the dated addition.
- **To stop:** write a dated addition, ask the question in the template
  below, commit, and end the session with the same question as your
  final message.
- **Zefira's email is `git config user.email`.** Use it as Unpaywall's
  `email` and OpenAlex's `mailto`, and nowhere else.
- **Each phase starts in a fresh session.** Don't carry a session across
  phases. The state lives in the repos and in the dated additions.

## State

At the end of every phase, at every stop and at every blocker, append a
dated addition to the end of this file, under "Dated additions":

```markdown
### 2026-09-28 14:05 -07:00, after the handoff

What was done, with commits. What's next. Anything open.
```

Date, time and UTC offset, from the container's clock in
`America/Los_Angeles`. Never edit above the additions; the research
README allows a dated addition at the end and nothing else. To find
where you are: the last addition, the `status` field in `literature`'s
source files, the commits in `experiments`, and the note's commits on
this branch.

## The question template

Every stop asks its question this way. The context stands on its own, so
Zefira can answer without scrolling back. Earlier decisions are restated
in words. The recommended answer is (a).

```markdown
#### Context

<standalone context>

### ❓ **<question title>**

<the question>

<question title, restated>:

- **(a)** <answer, and what choosing it commits to>
- **(b)** <answer, and what choosing it commits to>

➡️ **(a)** <the recommendation, and why>
```

A question with no honest set of answers gets the recommendation as its
only lettered answer, and Zefira answers in her own words.

## Before phase 1: the setup

Zefira sets these up. Check each one. Install what's missing with
`sudo dnf` or `cargo install`, and record it in the first addition.
Anything you can't fix is a blocker.

- Rust through rustup (`rustup show`), not Fedora's `rust` package.
- `pdftotext` (poppler-utils), headless Chromium, `valgrind`, and
  `python3` 3.11 or later, for `tomllib`.
- `gungraun-runner` 0.19.4:
  `cargo install gungraun-runner --version 0.19.4 --locked`.
- Git accepts the mounted repos (`git status` in each), and the identity
  is set.
- `date` prints Pacific time.
- WebSearch works.
- A scratch directory outside the repos, for crate clones and `target/`
  directories. It needs several GB.

The permissions Zefira installs for an unattended run. Check the syntax
against the Claude Code version in the container.

```json
{
  "permissions": {
    "allow": [
      "Bash(cargo:*)", "Bash(rustup:*)", "Bash(python3:*)",
      "Bash(git add:*)", "Bash(git commit:*)", "Bash(git worktree:*)",
      "Bash(git status:*)", "Bash(git log:*)", "Bash(git diff:*)",
      "Bash(git show:*)", "Bash(curl:*)", "Bash(sudo dnf:*)",
      "Bash(pdftotext:*)", "Bash(chromium-browser:*)",
      "WebSearch", "WebFetch",
      "Edit(~/prog/bough/literature/**)",
      "Edit(~/prog/bough/experiments/**)",
      "Edit(~/prog/bough/rfd-literature-review/**)"
    ],
    "deny": ["Bash(git push:*)", "Bash(cargo publish:*)"]
  }
}
```

## The phases

### 1. Trace

1. Make the worktree. Rewrite `literature`'s README to the spec below,
   add its script, and commit.
2. Start from the seeds at the end of this file. Each one is unverified
   until you find it; fix its details or drop it.
3. Snowball one hop at a time, per dimension: references backward,
   citations forward, through OpenAlex, Semantic Scholar and DBLP. A
   dimension is saturated when a hop adds no new core source.
4. Rank each dimension's candidates by relevance to Bough's open
   questions and to the audit of settled decisions, then by standing in
   the field. Keep about 15 core sources per dimension, about 100 rows in
   all. That's a soft cap. The rest go in as map-only, with no copy. Never
   choose by the order sources were found.
5. Save legal open copies from arXiv, author pages, institutional
   repositories and Unpaywall. Print web articles to PDF with headless
   Chromium. Books get a row with no file. Commit in batches.
6. **Stop.** In the addition and in your final message, give the fetch
   list: every source without an open copy, theses and reports included.
   For each, give the identifier, title, target filename, and where to
   start looking: author emails where they're published, ORCID, DBLP
   and homepage links.

### 2. Zefira fetches

She saves copies under the listed filenames and tells you when to go
on. Anything she couldn't get stays `abstract-only`, and its claims stay
scoped to the abstract.

### 3. Reading

Read the core sources in full, and supporting sources as far as a claim
needs. Write the reading notes, one claim per line with its page, and
update each source's status. Read the six crates at source (see "The
note") from clones in the scratch directory, pinned to a tag or commit.

**Stop.** In the addition, give two things. First, the probe list: one
line each, naming `rfd-NNNN-<slug>`, the RFD it serves, the claim it
would settle, and whether it measures performance. Second, the
must-read's outline. Zefira cuts probes before any are built.

### 4. Zefira cuts probes

### 5. Probes

Set up `experiments` to the spec below. Build and run every probe that
doesn't need wall-clock timing, and the gungraun instruction counts.
Commit one probe at a time.

**Stop.** Ask Zefira to leave the machine idle. Wall-clock needs it, and
the host also runs her games.

### 6. Wall-clock

Once she says go, a fresh session runs every Criterion bench in one
batch and commits the results.

### 7. Drafting

Write the note to the spec below. Commit it section by section.

### 8. Verification

A fresh sub-agent does this. It gets the note, `literature` and
`experiments`, and none of the drafting reasoning.

- Check every claim against its page in the stored copy, not only
  against the reading note.
- Re-run every probe. Instruction counts must match within 1%. A
  wall-clock ratio reproduces if its interval overlaps the quoted one.
- The drafting agent fixes each error, and the verifier re-checks what
  changed, until the pass is clean.
- **Stop** if a fix would change a finding in the must-read, or if a
  number still doesn't reproduce after one re-run.
- The note's header records what was checked, how, and the errors found
  and fixed, by kind.

From here the note is kept as written, as `research/README.md` says.

### 9. Done

Include the note in the book, with a stub in `src/research/` and a line
in `src/SUMMARY.md` under Research, as this handoff is. Write the final
addition. Your final message points Zefira at the must-read.

## The literature repo

- **Files.** One stem per source:
  `<first-author-last-name>-<title-slug>`, lowercase ASCII, hyphenated.
  An unsigned web source uses the organization, as in
  `janestreet-<title-slug>`. If two stems collide, append the year. Each
  source has `<stem>.pdf` (books have none) and `<stem>.md`.
- **Frontmatter.** TOML between `+++` lines, so the script needs only the
  standard library. The fields:
  - `id`: `doi:`, `arxiv:`, `isbn:`, `hdl:` or `url:`
  - `title`, `authors` (all of them), `year`, `venue`, `abstract_url`
  - `file`
  - `version`: `publisher`, `preprint`, `arxiv-vN`, `thesis`, or
    `web-print YYYY-MM-DD`
  - `source_url`
  - `status`: `not-read`, `abstract-only`, `read-sections` or
    `read-full`
  - `sections_read`, `read_on`
  - `dimensions` and `rfds`
  - `priority` (`core`, `supporting` or `map-only`) and
    `priority_reason`, one line
- **Dimension slugs.** `semantics-time`, `switching`, `loops-causality`,
  `scheduling-glitches`, `memory-leaks`, `values-ownership`,
  `concurrency-io`, `embedded-bounded`, `verification-testing`, and `map`
  for lineage only.
- **The body is reading notes.** One claim per line, with its page:
  `- p. 7, §3.2: <claim>`.
- **The script** regenerates the README's index table (title, year,
  status, dimensions, priority) from the frontmatter, between two marker
  comments. The files are the only source of truth.
- **The README** says all of this and keeps Zefira's opening.

## The experiments repo

- **Layout.** `bough-experiments` stays the root package and gains a
  `[workspace]`. Add a member crate only when the next experiment is
  incompatible with every existing crate:
  - two versions of a crate that Cargo can't both satisfy;
  - a `links` collision;
  - feature unification that would change what a probe measures (check
    `cargo tree -e features` first);
  - another toolchain. That one gets a crate excluded from the
    workspace, with its own pin.
- **Pins.** Pin the toolchain exactly in `rust-toolchain.toml`, at the
  stable version on the day of setup, and commit `Cargo.lock`.
  Criterion 0.8. gungraun 0.19.4, matching its runner.
- **Names.** `rfd-NNNN-<slug>`, after the RFD whose question the probe
  informs.
- **Targets.**
  - A probe that doesn't measure performance is `src/bin/<name>.rs`, run
    with `cargo run --release --bin <name>`.
  - A performance probe is two `[[bench]]` targets with
    `harness = false`: `<name>-wallclock` (Criterion) and
    `<name>-instructions` (gungraun). Each runs with
    `cargo bench --bench <target>`.
  - Check that Cargo resolves both across members. If it doesn't, the
    commands add `-p <crate>`.
- **Wall-clock.** Every wall-clock probe measures its own baseline in the
  same run. The note quotes only the ratio, with its interval.
- **The README** is the decisions experiments template, with its slots
  filled for this repo. An experiment retires when its RFD reaches
  `committed` or `abandoned`, and the note cites the commit that
  produced each number.
- **Provenance.** Every number the note quotes carries a line like this,
  followed by the command that produced it:
  `> rustc VERSION (released DATE) - measured DATE - <target> at experiments@COMMIT - Ryzen 7 2700X, <container OS>`

## The note

- **Shape.**
  1. A header: date, what was verified and how.
  2. The must-read, at most 1,000 words. Its findings are keyed to the
     RFDs, each with its leaning. It flags any leaning that rests on an
     unreproduced paper number or an abstract-only source.
  3. Nine sections, one per dimension:
     - semantics and time (RFD 1)
     - switching and dynamic graphs (RFDs 2, 5)
     - loops and causality (RFDs 2, 5)
     - scheduling and glitch freedom (RFD 5)
     - memory and leaks (RFD 3)
     - values and ownership (RFD 4)
     - concurrency and the I/O edge (RFD 6)
     - embedded and bounded (RFD 7)
     - verification and testing (RFD 1's policy)
  4. A one-page lineage map.
  5. The crate table.
  6. An annotated bibliography by stem.
- **Each dimension section has:**
  - what the literature says;
  - the Rust prior art;
  - settled decisions the evidence contradicts, or the words "none found";
  - the options for Bough;
  - Claude's leaning, labelled as such;
  - questions to grill;
  - the experiments it proposes for Bough itself, which are never run;
  - a reading path that names its prerequisites, for example "needs
    natural deduction and Kripke semantics".
- **Findings end in questions to grill, never in RFD text.** Decisions
  are Zefira's, through her grilling.
- **Scope.**
  - The FRP lineage, and the neighbouring fields where the open
    questions live: incremental computation, synchronous languages,
    modal and guarded FRP types, embedded FRP, and glitch-free
    concurrent reactive programming.
  - Up to 2026.
  - Continuous time gets a place on the lineage map only. Bough is
    discrete, and continuous time is out of scope in REQUIREMENTS.
  - Rx-style libraries appear only where one bears on a Bough question.
- **Rust.**
  - Read six crates at source: Leptos's `reactive_graph`, Sycamore's
    reactive crate, `gc-arena`, `salsa`, DFIR (Hydro) and `carboxyl`.
    Cite them by repo, tag or commit, and path.
  - Everything else is one row in the crate table: semantics, glitch
    freedom, memory strategy, threading.
- **Writing.** In Bough's terms. A formal result is stated as what it
  rules out in a Bough program and what a Rust mechanism for it would
  look like. The formal statement is cited, not needed. The voice is
  Zefira's, as in the RFDs: short declarative sentences, plain words.

## Bough's context

### Settled: check the stated reasons, report only contradictions

- **Fidelity to Sodium's `Denotational.hs` v1.1**, except where the text
  breaks its own rules of time order and creation (F6, F7, F89). RFD 1.
- **Discrete time**, with no continuous-time module. REQUIREMENTS.
- **GHC is the oracle**; the Rust port is shelved. RFD 1.
- **A single-threaded engine.** The `Io` and `RemoteIo` handles queue
  every call for the next pump. RFD 6.
- **Scheduling is a DFS mark followed by a flat evaluation loop.** The
  DFS's reverse post-order is a topological order. Memoized pull is used
  only for a `switch_cell`'s new inner and for nodes created during the
  instant. Rank-ordered push, as in Sodium, and pure pull are rejected.
  RFD 5.
- **Memory is a `u32` generational arena with tracing mark-sweep from
  explicit roots.** `Trace` is safe, with a derive. Refcounts and weak
  refs are rejected. Collection runs after each whole unit. RFD 3.
- **Streams are linear and move by value; cells lend by reference.**
  `share` needs `Clone`. Read-through cells are lazily memoized, and
  eager evaluation is rejected. RFD 4.
- **The dependency graph stays acyclic.** Cell reads before the instant,
  and `split`/`defer` child instants, break cycles. RFDs 2 and 5.
- **A transaction is atomic visibility, not abortable.** A panic poisons.
  RFD 5.
- **The core is `no_std` over `alloc`,** with `std` a default feature.
  There's no static engine in core, and no public backend trait. RFD 7.

### Open: where the effort goes

1. **Capture declarations and space leaks in higher-order graphs.**
   `b.depends` and the move rule are declarations checked at runtime.
   Could types do it? RFD 3.
2. **Incremental ordering and cycle detection under switching.** The
   relink check is linear in upstream nodes, and reads carry Brent's
   cycle detection. RFD 5, and the spike note.
3. **The causality boundary of the loop rule** (F3, and §10 of the
   architecture brief). Could it be checked statically?
4. **The formal status of the creation-time cuts** (F6, F7, F89, and
   `construct`'s cut) and of fixed-point loops (F1), under the
   hierarchical time `T = [Int]`.
5. **The bounded embedded tier:** bounding `construct`, the depth of
   `split` nesting, and queue growth. See RFD 7's open questions.
6. **Construction cost, and fusion's compile-time blow-up** (F36, and the
   `notes/oort-fighter` branch).
7. **Simultaneity at the edge:** the input slot's associative fold, and
   one cause per unit. RFDs 6 and 7.
8. **Concurrency.** Find a source for the single-thread rationale, or
   refute it. The no-std handoff's claim about threading overhead has no
   source.
9. **Cells of collections at scale,** and incremental collections.
10. **Operational primitives** (`steps`, `listen_once`): whether they are
    observationally sound, and whether `steps` should go behind a
    feature. See Zefira's review notes.

## Seeds

Written from memory and unverified. Titles, authors, venues and years
all need checking in phase 1. The first group is where every dimension
starts.

- **Surveys and the map.**
  - Bainomugisha, Carreton, Van Cutsem, Mostinckx, De Meuter, "A Survey
    on Reactive Programming", ACM Computing Surveys, 2013.
  - Elliott and Hudak, "Functional Reactive Animation", ICFP 1997.
  - Wan and Hudak, "Functional Reactive Programming from First
    Principles", PLDI 2000.
  - Nilsson, Courtney and Peterson, "Functional Reactive Programming,
    Continued", Haskell Workshop 2002.
  - Czaplicki and Chong, "Asynchronous Functional Reactive Programming
    for GUIs", PLDI 2013.
  - Perez, Bärenz and Nilsson, "Functional Reactive Programming,
    Refactored", Haskell Symposium 2016.
  - Blackheath and Jones, *Functional Reactive Programming*, Manning,
    2016. A pointer row to `frp-mdbook`.
- **semantics-time.**
  - Elliott, "Push-Pull Functional Reactive Programming", Haskell
    Symposium 2009.
  - van der Ploeg and Claessen, "Practical Principled FRP: Forget the
    Past, Change the Future, FRPNow!", ICFP 2015.
  - Jeltsch, on linear-time temporal logic as a semantics for FRP, MFPS
    2012.
  - Sculthorpe and Nilsson, "Safe Functional Reactive Programming through
    Dependent Types", ICFP 2009.
- **switching.**
  - Krishnaswami, Benton and Hoffmann, "Higher-Order Functional Reactive
    Programming in Bounded Space", POPL 2012.
  - Patai, "Efficient and Compositional Higher-Order Streams", WFLP 2010.
  - Cooper and Krishnamurthi, "Embedding Dynamic Dataflow in a
    Call-by-Value Language", ESOP 2006.
  - Meyerovich et al., "Flapjax", OOPSLA 2009.
  - Reflex's documentation and Trinkle's talks (web).
  - reactive-banana's documentation (web).
- **loops-causality.**
  - Berry, *The Constructive Semantics of Pure Esterel*, a draft book.
  - Halbwachs, Caspi, Raymond and Pilaud, "The Synchronous Data Flow
    Programming Language LUSTRE", Proc. IEEE, 1991.
  - Caspi and Pouzet, "Synchronous Kahn Networks", ICFP 1996.
  - Nakano, "A Modality for Recursion", LICS 2000.
  - Krishnaswami, "Higher-Order Reactive Programming without Spacetime
    Leaks", ICFP 2013.
  - Cave, Ferreira, Panangaden and Pientka, "Fair Reactive Programming",
    POPL 2014.
- **scheduling-glitches.**
  - Acar, *Self-Adjusting Computation*, PhD thesis, CMU, 2005.
  - Hammer, Phang, Hicks and Foster, "Adapton: Composable,
    Demand-Driven Incremental Computation", PLDI 2014.
  - Jane Street's posts and talks on Incremental (web).
  - Pearce and Kelly, "A Dynamic Topological Sort Algorithm for Directed
    Acyclic Graphs", JEA 2006.
  - Haeupler, Kavitha, Mathew, Sen and Tarjan, "Incremental Cycle
    Detection, Topological Ordering, and Strong Component Maintenance",
    TALG 2012.
  - Bender, Fineman, Gilbert and Tarjan, on incremental cycle detection,
    TALG 2016.
  - The TC39 Signals proposal, and writing on push-pull colouring in
    fine-grained signal libraries (web).
- **memory-leaks.**
  - Bahr, Graulund and Møgelberg, "Simply RaTT", ICFP 2019.
  - Bahr, "Modal FRP for All", JFP 2022 (Rattus).
  - Bahr and Møgelberg, "Asynchronous Modal FRP", ICFP 2023.
  - Liu and Hudak, "Plugging a Space Leak with an Arrow", ENTCS 2007.
  - `gc-arena`'s design notes (web).
- **values-ownership.**
  - Coutts, Leshchinskiy and Stewart, "Stream Fusion", ICFP 2007.
  - McSherry, Murray, Isaacs and Isard, "Differential Dataflow", CIDR
    2013.
  - Budiu et al., "DBSP", VLDB 2023.
  - Hydro's papers and DFIR's documentation.
- **concurrency-io.**
  - Drechsler, Salvaneschi, Mogk and Mezini, "Distributed REScala",
    OOPSLA 2014.
  - Margara and Salvaneschi, on the semantics of distributed reactive
    programming and the cost of consistency, TSE 2018.
  - Drechsler et al., "Thread-Safe Reactive Programming", OOPSLA 2018.
  - Ousterhout, "Why Threads Are a Bad Idea", 1996 (talk slides; the
    Sodium book cites it).
- **embedded-bounded.**
  - Wan, Taha and Hudak, "Real-Time FRP", ICFP 2001.
  - Wan, Taha and Hudak, "Event-Driven FRP", PADL 2002.
  - Sawada and Watanabe, "Emfrp", 2016, and the later XFRP work from the
    same group.
  - Helbling and Guyer, "Juniper", FARM 2016.
  - Pike et al., "Copilot", RV 2010.
  - Biernacki, Colaço, Hamon and Pouzet, "Clock-Directed Modular Code
    Generation for Synchronous Data-Flow Languages", LCTES 2008.
- **verification-testing.**
  - Perez and Nilsson, "Testing and Debugging Functional Reactive
    Programming", ICFP 2017.
  - Claessen and Hughes, "QuickCheck", ICFP 2000.
  - The Coq and Agda metatheory behind the RaTT papers and Krishnaswami
    and Benton's "Ultrametric Semantics of Reactive Programs", LICS
    2011.
  - The Copilot verifier, ICFP 2023 or thereabouts.

## Suggested skills

- **`grilling`,** for the question at every stop. Its template is the
  one above.
- **`pdf`,** for extracting text, checking pages and printing web
  sources.
- **Not `handoff`.** State goes into dated additions to this file, not
  into new handoffs.

## Dated additions

### 2026-09-27 09:31 -07:00, the setup, before phase 1

Zefira rebased this branch after the handoff was written. It now sits on
`origin/rfd/revision-after-the-spikes` at `9f96d58`, not `1b30f27`. The
rebase brought in three notes the handoff doesn't name:

- The Oort fighter note is on this branch now, as
  `notes/2026-09-26-oort-fighter-first-findings.md`. The local branch
  `notes/oort-fighter` is no longer where it lives. It's the evidence for
  open question 6.
- `notes/2026-09-27-mode-generic-core.md` is new. It comes from porting
  the Sodium book's petrol pump example to Bough. Read it with the rest
  of Bough's evidence.
- The two commits between `1b30f27` and `9f96d58` only pin mdbook 0.5.4
  and remove the unused admonish setup.

Every item in the setup was checked:

- Rust is rustup's stable 1.98.1 (released 2026-09-01), and Fedora's
  `rust` and `cargo` packages are not installed.
- `pdftotext` is poppler 26.01.0, `valgrind` is 3.27.1, `python3` is
  3.14.7, and `gungraun-runner` is 0.19.4.
- Chromium was missing. It was installed with `sudo dnf install
  chromium`, as 154.0.8037.57. `chromium-browser --headless
  --print-to-pdf` works.
- `date` prints Pacific time.
- WebSearch works.
- OpenAlex, arXiv and DBLP answer. Semantic Scholar answers 429 without
  a key, and there is no key. Back off and retry on it, and lean on
  OpenAlex and DBLP.
- The scratch directory is `~/prog/bough/research-scratch-space`. It is
  outside every repo, and its disk has 1.7 TB free.
- Git's identity is set.

The main `rfd` checkout was on this branch, so the worktree couldn't be
made. It was switched back to `spike/engine-feasibility` at `9afae4c`,
and the worktree is now `~/prog/bough/rfd-literature-review`, as the
handoff says.

Commit signing is off in `rfd`, `literature` and `experiments`. Each has
`commit.gpgsign false` in its own config, which overrides the global
`true`, and the worktree shares `rfd`'s config. A test commit in each of
the three went through unsigned with no passphrase prompt, and was
removed with a soft reset. Nothing else was committed.

The permissions are in `research-scratch-space/.claude/settings.json`,
and phase 1 starts from that directory. They are the handoff's list with
these changes:

- `git clone`, `git fetch` and `git rev-parse` are allowed, and so are
  writes to the scratch directory.
- `bough`, `claude-planning`, `sodium` and `decisions` can be read but
  not written. Neither can the main `rfd` checkout.
- `git -C` is denied. Zefira's rule: never use it. `cd` into the repo
  instead.
- `git checkout` isn't allowed, because it can throw away uncommitted
  work, so it asks first. Pin a crate clone with `git clone --branch
  <tag>` where a tag exists.

Next: phase 1 in a fresh session, from the scratch directory. Nothing is
open.

### 2026-09-27 09:46 -07:00, phase 1 paused: the wrong container

Zefira stopped this session partway through phase 1. It was started on
the host, Bazzite 44 (Silverblue), not in the Fedora container. No PDF
tool has been used and nothing has been fetched.

Done:

- `literature@ad4fa96`: the README is rewritten to the spec, with
  Zefira's opening kept, and `index.py` regenerates and checks the index.
  That commit lacks the `Claude-Session` trailer; later commits carry it.
- The seeds were checked against Crossref. All but three have a DOI and
  their details hold, with these fixes: Patai is WFLP 2010 in LNCS 6559
  (2011); Pearce and Kelly's JEA article is dated 2007 by Crossref;
  Bender, Fineman, Gilbert and Tarjan is TALG 2015/2016, "A New Approach
  to Incremental Cycle Detection and Related Problems"; the Copilot
  verifier is Scott, Dodds et al., "Trustworthy Runtime Verification via
  Bisimulation (Experience Report)", ICFP 2023, doi:10.1145/3607841;
  DBSP's VLDB 2023 paper is doi:10.14778/3587136.3587137. Differential
  Dataflow (CIDR 2013) has no DOI (OpenAlex W3098257205). Acar's thesis
  and Berry's draft book are not in Crossref or OpenAlex and need the
  CMU report and Berry's page.
- Hop 1 of the snowball ran for every dimension. The outputs are in the
  scratch directory, not in any repo: `trace/hops/1-<dim>.tsv`, ranked by
  how many of the dimension's seeds each work links to. Nothing has been
  ranked or kept yet.

The tooling, in `~/prog/bough/research-scratch-space/trace/`:

- `oa.py`: OpenAlex lookups (`get`, `refs`, `cites`, `search`) and a
  Crossref search (`xref`), with a disk cache in `trace/cache/`.
- `snowball.py DIM`: one hop over `seeds.json[DIM]` plus
  `added.json[DIM]`, the file for sources kept after a hop.

Learned about the services, as of this date:

- DBLP's API sits behind an Anubis bot check on all three mirrors and
  can't be used from a script. Crossref replaces it for title search.
- OpenAlex without a key has a free budget of $0.10 a day. A singleton
  lookup (`works/doi:...`) is free, a filtered list costs $0.0001, and a
  `search` costs $0.001. Look up by DOI, and search only when there's no
  DOI.

Next: in the right container, a fresh session resumes phase 1 at step 4,
ranking hop 1's candidates per dimension, then the next hops to
saturation. Hop 1 surfaced gaps the citation graph won't fill from these
seeds, to add by hand: Build Systems à la Carte, Naiad's nested
timestamps and superdense time (for `T = [Int]`), Lee's "The Problem
with Threads" (for the single-thread rationale), Kiselyov et al.'s
"Stream Fusion, to Completeness", Hydro's Flo, Céu, Vélus, and
sequentially constructive concurrency (SCCharts).

#### Context

Phase 1 of the FRP literature review was started on the host instead of
the Fedora container, and was stopped before any PDF work. The literature
repo's README and index script are committed. The seeds are checked, and
the first snowball hop has run, with its output and tooling in the
scratch directory `~/prog/bough/research-scratch-space/trace/`.

### ❓ **Where phase 1 resumes**

Phase 1 is half done. Does the next session pick up from this state, or
start the phase over?

Where phase 1 resumes:

- **(a)** Resume in the Fedora container from step 4, reusing the
  scratch directory's tooling and hop outputs. This needs the scratch
  directory mounted in the container at the same path.
- **(b)** Restart phase 1 from step 2 in the container, re-running the
  seed checks and hop 1. The committed README and script stay.

➡️ **(a)** Nothing done so far depends on the host, and the OpenAlex
cache saves most of today's budget.

### 2026-09-27 09:49 -07:00, where phase 1 resumes

Zefira chose (a). A fresh session in the Fedora container resumes phase
1 at step 4, from the scratch directory's `trace/` tooling and hop 1
outputs. If the scratch directory isn't mounted at
`~/prog/bough/research-scratch-space` in the container, that's a
blocker. Nothing else is open.

Zefira has an OpenAlex account now. Its API key is in
`~/.config/openalex/api_key`, mode 600, one line, outside every repo.
Never print it, log it or commit it. Before any other OpenAlex call, the
next session changes `trace/oa.py` to use it:

- Read `OPENALEX_API_KEY` from the environment, else the file. With
  neither, fall back to the free allowance, as now.
- Send it as the `api_key` query parameter. Check that name against
  OpenAlex's current docs first.
- Leave it out of the cache key, which hashes the request URL, so the
  cached hop 1 responses still hit.
- Confirm the account's budget from the `x-ratelimit-*` headers of one
  free singleton lookup.

Check that `~/.config/openalex/api_key` is visible inside the container.
If it isn't, ask Zefira; don't go on with the free allowance.

### 2026-09-27 10:43 -07:00, phase 1 done: the fetch list

Phase 1 ran in the Fedora container from the scratch directory, resuming
at step 4 as the last addition said. It stops here for the fetch.

`trace/oa.py` now reads the OpenAlex key from `OPENALEX_API_KEY` or
`~/.config/openalex/api_key`, and sends it as `api_key`, the name
OpenAlex's authentication page gives. The key is added after the cache
key is hashed, so hop 1's cached responses still hit, and an error
message shows the URL without it. One free singleton lookup's headers
gave the account's budget: $1 a day, plus $20 prepaid and 200,000
one-time credits, all expiring 2026-12-26. The whole phase used $0.027
of the day's dollar.

The trace:

- Hop 1's candidates were ranked against the open questions, with RFDs 3
  and 5, §10 of the architecture brief and the spike's F-findings read
  for the purpose. Hop 1's link counts favour generic classics (Knuth,
  MapReduce), so the ranking is judgement, recorded one line per source
  in `trace/manifest.py`.
- The gaps the last addition named were added by hand, all but Hydro's
  papers as DOIs: Build Systems à la Carte, Naiad, superdense time (Lee
  and Zheng), Lee's "The Problem with Threads", Stream Fusion to
  Completeness, Flo, Céu, Vélus and sequential constructiveness. So were
  web and Rust sources the citation graph can't reach: Jane Street's
  Incremental, the TC39 signals proposal, the Reactively post,
  Goregaokar's tour of Rust GC designs, shifgrethor, gc-arena's README,
  rustc's red-green algorithm, Reflex's and reactive-banana's docs,
  Elm's "Farewell to FRP", Ousterhout's slides, von Behren et al.'s
  rebuttal, and Elliott's "Denotational Design".
- Saturation: hop 2 added core sources in seven dimensions, so those got
  a hop 3. Hop 3 added core sources only in loops and causality
  (Schneider and Brandt, sequential constructiveness's journal version),
  hop 4 added clock refinement (Gemünde, Brandt and Schneider) there, and
  hop 5 added only map-level work (STATEMATE, SIGNAL). Every dimension is
  saturated. The hop outputs are `trace/hops/<n>-<dim>.tsv`.

What `literature` holds, commits `b81e506` to `17c1b59`:

- 142 records: 66 core, 32 supporting, 44 map-only. The soft cap was
  held by moving 24 supporting rows to map-only, the ones no open
  question turns on (`DEMOTE` in the manifest). Core per dimension runs
  from 5 (verification-testing) to 17 (scheduling-glitches).
- 91 stored copies: 33 publisher, 32 preprint, 12 arXiv, 12 web prints,
  2 theses. Every PDF's first pages carry its title. An arXiv version is
  read from the PDF's own stamp.
- Metadata comes from Crossref for DOIs, since OpenAlex drops subtitles
  ("Flapjax", "Naiad"), and from OpenAlex or by hand otherwise.
  Crossref's casing ("Von Hanxleden", "O'brien") is left for phase 3,
  which checks each record against its copy.

Choices made inside the plan:

- **PDFs are tracked through a repo-local `.gitignore`.** The global
  gitignore drops `*.pdf`, so the first copy commit held only records.
  `literature/.gitignore` says `!*.pdf`.
- **Seven copies are Wayback snapshots of authors' own pages**, now gone:
  FRPNow, Patai, Pérez and Nilsson, Stream Fusion, RT-FRP, E-FRP, and
  Bacon et al. `source_url` names the snapshot.
- **Three copies were the authors' PostScript**, converted with
  `ps2pdf`: Lustre (Proc. IEEE 1991), Synchronous Kahn Networks, and
  QuickCheck. Ghostscript wasn't installed; it was installed with `sudo
  dnf install ghostscript`, 10.06.0. `source_url` names the PostScript.
- **Four copies aren't the venue's text,** and their claims are scoped to
  the stored version. Lee's "Problem with Threads" is the Berkeley tech
  report. Pouzet and Raymond is an extended October 2009 version. Scott
  et al. is the extended arXiv report. E-FRP with priorities is Rice's
  2009 tech report, which adds Jun Inoue as an author.
- **The Reactively post's author is recorded by handle, `milomg`.** The
  post and its GitHub account give only "Milo" and "Milo M"; the surname
  first written came from memory and was removed.
- **Milo's post was printed from its own HTML with overflow unclipped.**
  A plain print kept 154 of its 2,000-odd words.
- **One sub-agent searched author pages** for the 65 sources the indexes
  couldn't place, and found 54. It returned URLs only; every copy was
  downloaded and checked here.

Learned about the services, as of this date:

- ACM's Digital Library refuses scripts and headless Chromium alike with
  a Cloudflare check, even for its open-access PDFs.
- Unpaywall and OpenAlex miss most author pages: they call Krishnaswami's
  ICFP 2013 paper closed, though it's on his Cambridge page.
- HAL and Kiel's repository show an Anubis check to browser user agents
  but serve plain `curl`. CiteSeerX now redirects to the Wayback Machine.
  The Yale Haskell group's site is down.

The tooling is in `~/prog/bough/research-scratch-space/trace/`, outside
every repo, as before: `manifest.py` (the ranking and its reasons),
`build.py` (`records`, `fetch`, `missing`) and `store.py` (stores a
found-URL list with the same checks).

The fetch list. The Sodium book isn't on it: its row has no file by
design, and it's read in `~/prog/sodium/frp-mdbook/src/`. Save each copy
into `~/prog/bough/literature` under the filename given. Phase 3 then
fills in `file`, `version` and `source_url`.

1. **`shiple-constructive-analysis-of-cyclic-circuits.pdf`**, core,
   loops-causality. doi:10.1109/EDTC.1996.494321, Shiple, Berry and
   Touati, "Constructive analysis of cyclic circuits", ED&TC 1996. IEEE
   Xplore only; no author copy found at INRIA's or Berry's Esterel pages,
   live or archived. Berry: DBLP
   https://dblp.org/pers/hd/b/Berry:G=eacute=rard, Collège de France
   https://www.college-de-france.fr/fr/personne/gerard-berry. No
   published email found.
2. **`keating-this-is-driving-me-loopy.pdf`**, core, loops-causality and
   embedded-bounded. doi:10.1145/3609026.3609726, Keating and Gale, "This
   Is Driving Me Loopy: Efficient Loops in Arrowized Functional Reactive
   Programs", Haskell Symposium 2023. OpenAlex says gold open access, so
   https://dl.acm.org/doi/pdf/10.1145/3609026.3609726 in a browser should
   do. Keating: ORCID 0000-0001-6933-3338, DBLP
   https://dblp.org/pid/299/8776.html. Gale: ORCID 0000-0001-7711-6763.
   Keating's 2024 Warwick thesis, "Stricter arrowised functional reactive
   programming", is a separate work:
   https://wrap.warwick.ac.uk/id/eprint/191913/.
3. **`maier-higher-order-reactive-programming-with-incremental-lists.pdf`**,
   core, values-ownership and switching. doi:10.1007/978-3-642-39038-8_29,
   Maier and Odersky, ECOOP 2013 (LNCS 7920). Springer only; not in EPFL
   Infoscience. Odersky: martin.odersky@epfl.ch, published at
   https://people.epfl.ch/martin.odersky, ORCID 0009-0005-3923-8993.
   Maier's EPFL thesis, "Reactive Programming Abstractions for Complex
   Event Logic and Dynamic Data Dependencies", is related but separate.
4. **`sawada-emfrp-a-functional-reactive-programming-language-for-small.pdf`**,
   core, embedded-bounded. doi:10.1145/2892664.2892670, Sawada and
   Watanabe, "Emfrp", Modularity 2016 companion. ACM, not marked open;
   the group's page links an ACM Author-Izer copy:
   https://www.psg.c.titech.ac.jp/acmauthorizer.html. Watanabe: ORCID
   0000-0001-7470-3428, DBLP https://dblp.org/pid/21/2042.html,
   researchmap https://researchmap.jp/takuo.
5. **`yokoyama-switching-mechanism-for-update-timing-of-time-varying.pdf`**,
   supporting, embedded-bounded and switching. doi:10.1145/3651781.3651789,
   Yokoyama, Moriguchi and Watanabe, ICSCA 2024. OpenAlex says gold open
   access: https://dl.acm.org/doi/pdf/10.1145/3651781.3651789 in a browser.
   Yokoyama: ORCID 0000-0002-8352-4082. Moriguchi: ORCID
   0000-0002-4153-4514.
6. **`shibanai-distributed-functional-reactive-programming-on-actor-based-runtime.pdf`**,
   supporting, embedded-bounded and concurrency-io. XFRP.
   doi:10.1145/3281366.3281370, Shibanai and Watanabe, AGERE 2018. ACM,
   not marked open; Author-Izer link on the same group page. Watanabe as
   above.

Nothing outside that list is open. The trace tooling and manifest live
only in the scratch directory; if they should be kept with `literature`,
that's a small commit.

Next: phase 2, Zefira fetches. Then phase 3, reading, in a fresh session.

#### Context

Phase 1 of the FRP literature review is done. The citation trace
saturated in every dimension. `literature` holds 142 records: 98 kept
(66 core, 32 supporting) and 44 map-only. 91 of the 98 kept sources have
a stored legal copy. The Sodium book has no file by design, since it's
read from `frp-mdbook`. That leaves six papers with no open copy found:
four core and two supporting. Two of them, Keating and Gale's loops paper
and Yokoyama et al.'s switching paper, are open access on ACM and only
need a browser; the other four need the publisher or the authors.

### ❓ **Fetching the six missing papers**

Six kept papers have no open copy. Each is listed above with its filename
and where to look. Will you fetch them before phase 3 reads?

Fetching the six missing papers:

- **(a)** Fetch what you can, at least the two open ACM papers, save them
  under the listed filenames, and say go. Whatever you can't get stays
  `abstract-only`, and its claims stay scoped to the abstract.
- **(b)** Skip fetching and go straight to phase 3. All six stay
  `abstract-only`, including four core sources: Shiple et al. on cyclic
  circuits, Keating and Gale on loops, Maier and Odersky on incremental
  lists, and Emfrp.

➡️ **(a)** Four of the six are core, and three bear directly on open
questions: static causality checking, loop cost, and cells of
collections. The two ACM open-access papers take a minute in a browser.

### 2026-09-27 22:39 -07:00, phase 2 done, two requests pending

Zefira chose (a) and fetched five of the six. Four came from the ACM
Digital Library in her browser (Keating and Gale, Emfrp, XFRP, Yokoyama
et al.), and Shiple et al. from IEEE Xplore. All five are the publishers'
versions, each first page carries its title, and their records are
filled in: `literature@661cf51`. 96 of the 98 kept sources now have a
copy. The two without are the Sodium book, by design, and Maier and
Odersky's incremental-lists paper.

Maier and Odersky's ECOOP 2013 paper has no open copy. Zefira emailed
Odersky for one. She supplied its abstract, which neither Crossref nor
OpenAlex carries, and it is in the record, so the record is
`abstract-only`. The abstract confirms why it ranks core: it names the
problem Bough's read-through cells have. A time-varying collection
propagates whether it changed, not what changed.

Maier's 2013 EPFL thesis (no. 5805, doi:10.5075/epfl-thesis-5805)
describes the same reactive sequence, so it is the paper's fallback. It
has a record now, supporting and `abstract-only`: `literature@6f13389`.
Its file is restricted on Infoscience, and Zefira requested access
there.

Next: phase 3, reading, in a fresh session, when Zefira says go. It
doesn't wait on either request. If a copy arrives, it's saved as
`maier-higher-order-reactive-programming-with-incremental-lists.pdf` or
`maier-reactive-programming-abstractions-for-complex-event-logic-and.pdf`,
and whichever session is running fills in the record. If neither
arrives, the note scopes both to their abstracts.

### 2026-09-27 23:08 -07:00, both Maier copies arrived

Zefira bought Maier and Odersky's ECOOP 2013 paper from Springer, and
EPFL granted her request for Maier's thesis. Both are stored and checked
against their titles, in `literature@804a7ed`. The thesis stays
supporting, now as Scala.React at full length to read beside the paper,
not as a stand-in for it. Both are licensed copies, one more reason
`literature` stays private.

Every kept source now has a copy except the Sodium book, which has no
file by design. That's 99 kept rows: 66 core and 33 supporting, with the
thesis added. Nothing is pending. Next: phase 3, reading, in a fresh
session, when Zefira says go.

### 2026-09-28 01:29 -07:00, phase 3 stopped at a blocker: F89's stated reason

Phase 3 read 13 of its 14 batches and stopped on a finding that
contradicts the stated reason for a settled decision. The crates batch,
the probe list and the must-read's outline are still to do.

Done, in `literature`, commits `750ebb5` to `50ebee1`:

- Every kept source but the six crates is read. 98 records carry reading
  notes, one claim per line with its page. Core sources are `read-full`
  except the Sodium book, which is `read-sections` by design. Supporting
  sources are `read-full` or `read-sections`, with the sections listed.
- Each batch left a synthesis file, `synthesis/01-scheduling.md` to
  `synthesis/13-sodium.md`: what the sources mean for Bough, per source,
  with contradictions, options and leanings, candidate probes, questions
  to grill, and reading paths. Drafting starts there.
- Metadata was checked against each copy's first page and corrected where
  it disagreed: casing, author lists, venues and years. Two venues were
  wrong: Diamonds is POPL 2021, not ICFP, and Schneider et al. is CASES
  2004, not EMSOFT. Both were confirmed against Crossref.

How the reading ran, and the choices made inside the plan:

- **Pages are the stored PDF's page index,** counted from 1, never the
  printed page. It's the one numbering a verifier can check without
  ambiguity. The literature README says so (`750ebb5`). The Sodium book
  is cited by chapter and section.
- **Reading notes are the sources' claims only.** What they mean for
  Bough is in `synthesis/`, which the README describes. A line that is
  the reader's inference ends in `(reading)`.
- **One sub-agent per batch, one at a time,** each with the same brief:
  `research-scratch-space/reading/briefing.md`, with the batches in
  `reading/batches.md` and the page-marked text in `reading/text/`. After
  each batch I checked claims against their pages before committing,
  three or four per batch, and fixed the synthesis twice where it said
  more than the page: Keating and Gale's Thm. 4.5 proves one direction
  only, and Acar lays his GC cost on SML/NJ, not on self-adjusting
  computation. Every sampled claim held.
- **Scott et al.'s record describes its stored copy,** the 2026 arXiv
  extension (arXiv:2607.01363), with that copy's title and author order.
  Its `id` is still the ICFP 2023 DOI. The verifier should decide whether
  the `id` follows the copy.
- **The crates are cloned and pinned** in
  `research-scratch-space/crates/PINS.md`. salsa's `v*` tags stop at
  0.16.1 in 2021, so it's pinned at `salsa-v0.28.5`, the crates.io
  latest. carboxyl moved to `milibopp/carboxyl`, and its 0.2.2 has no tag,
  so it's pinned at master, `2a80080`. They haven't been read.

A mistake: one request to the crates.io API sent Zefira's email in its
User-Agent header, against the rule that it goes only to Unpaywall and
OpenAlex. It was sent once, and later requests carried no email.

What the batches found, besides the blocker. No other settled decision is
contradicted. Three stated reasons are weaker than worded, and each is a
question for the grilling, not a blocker:

- RFD 3 rejects refcounts because they can't see cycles. Counting backed
  by a trace does see them (Bacon et al.). The stronger reason, that
  tracing lets tokens be `Copy`, is RFD 3's second one.
- RFD 6's single thread: the one measurement finds an uncontended lock
  costs nothing measurable (Drechsler et al. 2018). The Sodium book's
  Ousterhout passage (App. B §B.4) argues *for* threads. Listeners under
  a lock, and one order of units the host can see, are what the sources
  support.
- RFD 4's "exactly one consumer" is at most one: Rust's moves are affine.

Next: the question below. Then a fresh session finishes phase 3. It runs
batch 14, the six crates at source and the crate table, and then stops
with the probe list and the must-read's outline, as the handoff says.

#### Context

Phase 3 of the FRP literature review read 13 of its 14 batches, every
source but the Rust crates. The last batch was the Sodium book. RFD 1's
policy follows the semantics text except where it breaks its own rules,
"time order, and things existing from their creation". It names three
cases, F6, F7 and F89. F89 is a `split` or `defer` built at a child
instant, which in the text replays an event from before it existed. Bough
gives nothing there, as Sodium's Java does.

The book's Appendix E states time order as an invariant ("for increasing
T values", §E.4), which covers F6 and F7. It states creation only through
the `t0` of four primitives in the `Reactive` monad: Hold, Value, SwitchC
and Sample. `Split` is a pure function on streams, `Stream [a] → Stream
a`, with no creation time (§E.5.10). The text has no `Defer`; RFD 5 makes
a `defer` a split of one element. So in
the text, a split has no "before it existed", and its answer at a child
instant is what its equation says. Bough's F89 cut is not the text
breaking a rule. It's Bough extending the creation rule to `split` and
`defer`.

Other sources back the cut on its merits. FRPNow proves that a
combinator which may take its start from the past is "inherently leaky",
and one tied to now is "forgetful" (van der Ploeg and Claessen, Lemmas 1
and 2, p. 5). Sculthorpe's CFRP makes occurrences before switch-in
unobservable. Nothing found argues for the text's replay.

### ❓ **What F89's deviation rests on**

RFD 1 lists F89 as the text breaking its own rule, and the text states
no such rule for `split`. What should the review treat F89 as?

What F89's deviation rests on:

- **(a)** A semantics change under RFD 1's own rule for changing the
  semantics. The review reports that RFD 1's stated reason doesn't hold
  for F89, and that forgetfulness is a principled reason that does. The
  cut itself isn't questioned. Whether it needs its own RFD, or a
  reworded policy, is for the grilling.
- **(b)** Within the policy as written, reading "things existing from
  their creation" as a rule the whole text implies, which `split`
  breaks. The review records a qualification, not a contradiction, and
  phase 3 goes on.

➡️ **(a)** RFD 1 says changing an inherited corner "is a semantics
change and needs its own RFD, not an implementation choice", and the
text is explicit that `Split` is pure. Calling it (b) would rest a
settled policy on a rule the text doesn't state. (a) costs nothing
now: the finding goes in the must-read, and phase 3 finishes as planned.

### 2026-09-28 01:32 -07:00, F89 is a semantics change

Zefira chose (a). The review treats F89's cut as a semantics change
under RFD 1's own rule. It reports that RFD 1's stated reason, the text
breaking its own rule, doesn't hold for F89, and that forgetfulness
(FRPNow's Lemmas 1 and 2) is a principled reason that does. The finding
goes in the must-read, keyed to RFD 1. Whether it needs its own RFD or a
reworded policy is for the grilling.

She asked for phase 3 to go on in this session rather than a fresh one.
Next: batch 14, the six crates at source and the crate table, then the
phase 3 stop with the probe list and the must-read's outline.

### 2026-09-28 01:49 -07:00, phase 3 done: the probes and the outline

Batch 14 read the six crates at source, at the tags and commits in
`literature/synthesis/14-crates-pins.md`, and tabled seventeen others:
`literature@4ff07e4`. Every kept source is now read, and every batch has
a synthesis file. Checked by hand: Sycamore already runs RFD 5's design,
a DFS whose reverse post-order is the evaluation order, and it panics on
the DFS's grey mark as a cycle (`sycamore-reactive@0.9.3 src/root.rs`).
Jane Street's Incremental does order by heights, and re-heights
incrementally, which fills the gap batch 01 found.

No settled decision is contradicted beyond F89's stated reason, answered
above.

#### The probe list

Fourteen batches proposed 23 probes. Overlaps are merged, so thirteen
remain. Each line: the name, the RFD it serves, the claim it would settle,
and whether it measures performance.

1. `rfd-0005-cycle-in-mark`, RFD 5: whether the DFS mark's grey state
   catches every same-instant cycle the per-move upstream walk does (F46,
   F50, F19 and F56), so the walk and its 121 µs can go. Not performance;
   an instruction count beside.
2. `rfd-0005-bounded-relink-check`, RFD 5: whether a maintained `u32`
   topological order, with deletions applied first, bounds a switch move
   well below the upstream walk on a 10,000-node UI-shaped graph, with
   per-subgraph dependency summaries as a variant. Performance. Moot if
   1 succeeds.
3. `rfd-0005-heap-vs-mark-on-quiet-regions`, RFD 5: whether a heap that
   visits only firing nodes beats the mark plus flat loop when most
   marked nodes stay quiet, and at what quiet fraction. Performance.
4. `rfd-0005-demand-bounded-push`, RFDs 3 and 5: whether skipping nodes
   no root reaches, flagged at collection, costs less than evaluating
   garbage until it's collected (F66). Performance.
5. `rfd-0003-sweep-cost`, RFD 3: how long a mark-sweep of the arena
   takes at 1k, 10k and 100k slots with 10% and 90% live, to size the
   collection trigger. Performance.
6. `rfd-0003-branded-captures`, RFD 3: whether a lifetime brand on tokens,
   as gc-arena brands its pointers, or a nightly auto trait, makes a
   forgotten capture (F62) a compile error while `hold`, `construct` and
   `anchor` stay writable. Not performance.
7. `rfd-0004-erased-materializer`, RFD 4: whether erasing a fused chain at
   its materializer, as a boxed closure, a state struct stepped through a
   function pointer, or a normalized flat node, removes F36's per-chain
   compile blow-up at depths two and three, within a few ns per event.
   Performance, compile time and run time.
8. `rfd-0004-patch-cell-crossover`, RFD 4 and question 9: the collection
   size at which a cell carrying deltas beats a cell of the collection,
   for a `Vec` and for a keyed map with Z-set deltas, two delta sources
   in one instant, and a reader that reads rarely. Performance.
9. `rfd-0002-decoupled-marker`, RFD 2: whether a one-bit decoupledness
   marker type makes F3 a compile error while the counter that stops at
   ten compiles, and at what compile time and error text. Row types are
   the fallback. Not performance; compile time only.
10. `rfd-0002-ternary-loop-census`, RFD 2: how many same-instant cycles
    acyclicity refuses are constructive, and whether any fall outside
    the exclusive gates switching already expresses. Not performance.
11. `rfd-0001-forgetful-cut`, RFD 1: in a model over `T = [Int]`, whether
    the creation cut always satisfies FRPNow's forgetfulness while the
    text's replay fails exactly on F6 and F89 shapes, and whether a cut
    on every constructed primitive ever differs from one on state-holders
    and time-movers only. Not performance.
12. `rfd-0001-child-index-mutants`, RFD 1: what fraction of mutants that
    misplace an event among sibling child instants the oracle's
    comparison catches, with and without child indices. Not performance.
13. `rfd-0006-lock-vs-queue-cost`, RFD 6: the per-unit cost of a 500 ns
    propagation run on the owner thread, behind an uncontended `Mutex`,
    behind one contended by 2, 4 and 8 threads, and through a queue and
    pump. Performance.

#### The must-read's outline

At most 1,000 words, findings keyed to the RFDs, each with a leaning.

- **Header.** What was read and how, what was verified, and the flags:
  which leanings rest on a paper's unreproduced number, and which on a
  probe not yet run. No source is still abstract-only.
- **RFD 1.**
  - F89 is a semantics change. The text's `Split` is pure, and
    forgetfulness is the principled reason for the cut, for F6 too.
  - The oracle reaches the unique fixed point of a guarded system (F1).
    `[Int]` isn't well-ordered, so arguments range over the instants a
    run creates.
  - GHC as the oracle gains a second reason.
  - The harness's gap is trace length. Shrinking and shape coverage,
    already built, belong in the policy.
  - `steps` is sound in App. E's own model of a cell.
- **RFD 2.**
  - Acyclicity is Esterel v4's and Lustre's rule.
  - Constructiveness wouldn't rescue F3.
  - F3 needs `steps`, which ties questions 3 and 10.
  - The cheapest static check is a decoupledness bit (probe 9).
- **RFD 3.**
  - Types in the modal line catch a forgotten capture (F62), not an
    over-declaration (F63).
  - Lifetime brands may make F62 a compile error, which challenges RFD
    3's "cannot be made a compile error" (probe 6).
  - Counting with a backup trace does see cycles, so RFD 3's first reason
    is incomplete and its second carries it.
  - A safe `Trace` is sound for generation-checked indices.
  - Every GC-based FRP has F66.
- **RFD 4.**
  - "Linear" means affine; "exactly one consumer" is "at most one".
  - Fusion is supported, and F36 has no answer in the literature (probe 7).
  - Question 9: a cell that carries a change structure (Cai), Z-sets for
    keyed data, and keyed partitions for stable traces (probe 8).
- **RFD 5.**
  - Every ranked system confirms the cost of ranks. Incremental pays it
    incrementally.
  - Sycamore ships the DFS mark. Its grey mark may replace the relink
    walk (probes 1 and 2).
  - F46 needs only deletions before insertions.
  - F22 is a liveness gap, outside causality.
- **RFD 6.**
  - No source supports "threading costs overhead". An uncontended lock is
    free (Drechsler et al., unreproduced; probe 13), and the Sodium book
    argues for threads.
  - What the sources do support: no listeners under a lock, and one order
    of units the host can see.
  - No system merges independent callers.
- **RFD 7.**
  - The Emfrp line moved from merging simultaneous events to ordering
    them.
  - No source folds a burst with a user fold.
  - Every bounded system is static.
  - Leanings for the bounded tier: a high-water mark, a depth cap for
    child instants, fixed queue capacities.
- **What to grill first.** RFD 3 and RFD 5, since they gate the build.

Next: Zefira cuts probes (phase 4). Then phase 5 sets up `experiments`
and builds what's left.

#### Context

Phase 3 of the FRP literature review is done. Every kept source is read,
with reading notes by page, and each of fourteen batches has a synthesis
file in `literature/synthesis/`. The batches proposed thirteen probes
once overlaps were merged, listed above. The review gates the real
build, and RFDs 3 and 5 most of all, so probes that could change a
leaning there matter most. Phase 5 builds the probes that survive,
commits one at a time, and runs every performance probe's instruction
counts. Wall-clock runs wait for the machine to be idle.

### ❓ **Which probes to build**

Thirteen probes are listed above. Which survive to phase 5?

Which probes to build:

- **(a)** Build eight: 1, 2, 6, 7, 8, 9, 11 and 13. These are the ones
  whose answer could change a leaning on RFDs 3, 4 and 5, plus the
  cheapest checks on RFDs 1, 2 and 6's stated reasons. Cut 3 and 4,
  whose leanings the literature already settles; 5, which the trigger
  doesn't need yet; and 10 and 12, which would refine leanings that
  don't turn on them.
- **(b)** Build all thirteen. Phase 5 takes about twice as long, and the
  wall-clock batch grows from five performance probes to eight.

➡️ **(a)** Each cut probe either confirms a leaning the literature
already supports or informs a choice that nothing costly depends on yet.

### 2026-09-28 01:58 -07:00, phase 4: all thirteen probes stay

Zefira chose (b). Every probe in the list above is built in phase 5. The
performance probes, whose Criterion benches wait for the idle machine in
phase 6, are 2, 3, 4, 5, 7, 8 and 13, with an instruction count beside
probe 1.

Next: phase 5 in a fresh session. It sets up `experiments` to the spec
above, builds the thirteen probes one commit at a time, runs every probe
that doesn't need wall-clock timing and every gungraun instruction
count, and stops to ask for the idle machine.

### 2026-09-28 02:15 -07:00, phase 5 starts, with phase 6's go given

Zefira goes to bed and leaves the machine for about eight hours. Phase 5
doesn't need an idle machine: its probes check behaviour or count
instructions under valgrind. So she gave phase 6's go in advance, on one
condition. If phase 5 ends clean, with every probe built and no stop,
phase 6 runs in the same night. A fresh sub-agent runs it, given only
this handoff and the repos, which keeps the point of the fresh-session
rule. If phase 5 stops, phase 6 waits for her.

The machine was checked before the start, from inside the container:

- Closed on the host: Steam, a second Claude Code session, an editor's
  rust-analyzer, and a distrobox GUI.
- `uupd.timer`, the OS updater due at 04:06, is stopped for the night.
  It restarts at the next boot. Its container upgrade is off in
  `/etc/uupd/config.json` anyway, so the toolchain and valgrind can't
  change under the run.
- CPU boost is off (`/sys/devices/system/cpu/cpufreq/boost` reads 0),
  the governor is `performance`, and the tuned profile is
  `throughput-performance-bazzite`. Boost off trades speed for less
  thermal variance; the note quotes only ratios.
- The screen blanks after one minute, and idle suspend is `nothing`.
- Load average 0.00 at the start. Still running and left alone:
  gnome-shell, DisplayLink's manager, tailscaled, and a user timer that
  curls crates.io every two hours.

### 2026-09-28 02:41 -07:00, contradictions are findings, not stops

Zefira, during phase 5: a finding that contradicts a settled decision is
not a blocker. It is the finding to report, and it doesn't stop the
probes. This replaces that case in the Rules' list of blockers from here
on, for phases 5 and 6 and the verification pass. Crates that won't
build, unreachable sources and ambiguous probe results still stop.

### 2026-09-28 02:44 -07:00, unclear results are findings too

Zefira, a few minutes later: an ambiguous probe result doesn't stop a
phase either. It is reported as a finding, with what would settle it,
and she rechecks unclear results once the whole job is done. Of the
Rules' blockers, a crate that won't build and a source that can't be
reached still stop a phase.

### 2026-09-28 03:40 -07:00, the probes' own follow-ups join phase 5

Zefira: the follow-up probes the sub-agents suggest are built in phase 5
too. Those suggested so far, numbered after the thirteen:

14. `rfd-0005-small-side-order`, RFD 5, performance. Probe 2 found a
    Pearce-Kelly order 20 to 230 times worse than the walk when inners
    are built during the instant, because a new node goes at the end of
    the order and the search covers the switch's whole downstream. An
    order-maintenance list, or HKMST's two-way search, that places new
    nodes just before the switch, on probe 2's workloads.
15. `rfd-0003-work-paced-trigger`, RFD 3, performance. Probe 4 found
    that RFD 3's trigger lets hundreds of dead screens pile up beside a
    large live graph, and that pacing collection against garbage work
    is worth about ten times; that was arithmetic, not measured. End to
    end, RFD 3's trigger against a trigger on a work proxy, such as the
    marked region's size against the live count.
16. `rfd-0003-brand-erasure`, RFD 3, not performance. Probe 6's brand
    design left its rebranding as `todo!()`, where gc-arena uses
    `unsafe`. Whether a derived field-wise rebrand is sound with no
    `unsafe`, whether RFD 6's cross-thread handles survive the brand,
    and the leak route through capturing an `Anchored` and reopening
    it.
17. Probe 8, extended: a rope or concatenation tree for positional
    deltas, whose `memmove` made the large-`Vec` rows unreadable, and
    a lazy delta that buffers Z-sets until a read.
18. Probe 13, extended: where a contended lock's extra 300 to 400 ns a
    unit goes, by varying the graph's footprint.
19. Probe 9, extended: `gate`, `sample`, `split`, `defer` and
    `depends` in the marker's DSL.

Extensions are new commits to the same probe. Phase 6 still waits for
every probe, these included.

### 2026-09-28 03:57 -07:00, one more follow-up

20. Probe 10, extended: gates that read holds of the loop, so cells
    take only reachable states rather than every valuation. It settles
    whether state invariants add constructive loops outside the
    exclusive gates a switch expresses. Not performance.

### 2026-09-28 04:01 -07:00, two more follow-ups, and a cutoff

From probe 14, which found an order-maintenance list keeps the relink
check below the walk on every workload of probe 2's graph:

21. Probe 14, extended: an adversarial shape where both the new inner's
    upstream after the switch and the switch's downstream are large, to
    see whether the two-way search's bound matters against the backward
    one. Performance.
22. `rfd-0005-maintained-rank-queue`, RFD 5, performance. Probe 3's
    bucket queue with ranks from probe 14's maintained order instead of
    static heights, its upkeep counted. It settles whether the switch
    cost still justifies rejecting rank-ordered push.

A choice inside the plan: follow-ups can breed follow-ups, and the night
is finite. Phase 6's benches need about two hours on the idle machine.
So a follow-up suggested after 06:30 is recorded in the last addition
and not built, and phase 5 stops taking new work then.

### 2026-09-28 04:07 -07:00, the cutoff moves to 11:00

Zefira: mistral, this machine, is free until at least 14:00. So a
follow-up suggested before 11:00 is built. Phase 5 stops taking new
work then, and phase 6 starts by 11:30 at the latest, which leaves its
benches about two hours and some slack before 14:00. One suggested
later is recorded in the last addition and not built.

### 2026-09-28 04:09 -07:00, two more follow-ups

From probe 15, which found RFD 3's trigger needs a work term:

23. Probe 15, extended: its per-input work term under several inputs
    firing at uneven rates, some rarely, and live regions that grow, to
    see whether it collects spuriously or misses. Performance.
24. `rfd-0003-incremental-mark`, RFD 3, performance. The pause that no
    trigger removes, marking ten thousand live nodes, split across
    units, with the write barrier that needs counted.

### 2026-09-28 04:17 -07:00, two more follow-ups

From probe 17, which put the positional delta on a rope and found a lazy
map no help:

25. Probe 8, extended again: a counted B-tree against the chunked rope,
    at a million elements and on appends. Performance.
26. Probe 8, extended again: a fully lazy map that buffers raw upserts
    and brings the source up to date only on read. Performance.

A note for verification: probe 17's re-run moved the earlier
variants' counts by up to 6.6%, most likely from code layout. Every
instruction count reproduces only at the commit its result file cites.

### 2026-09-28 04:26 -07:00, two more follow-ups

From probe 16, which made the brand sound with no `unsafe` on stable:

27. `rfd-0003-rebrand-cost`, RFD 3, performance. The copy a safe rebrand
    makes on every read of a held value that contains tokens, against
    an unchecked cast, on held values and snapshots.
28. Probe 16, extended: a real `#[derive(Rebrand)]` proc macro, whether
    it can give brand-free types a copy-free read, and what the orphan
    rules force for foreign event types. Not performance.

### 2026-09-28 04:28 -07:00, two more follow-ups

From probe 18, which found a contended lock's extra cost is mostly not
the state migrating:

29. Probe 13, extended again: futex system calls counted per unit in
    the contended mutex, to confirm a wake on every unlock. A count.
30. Probe 13, extended again: threads pinned to one core complex
    against split across both, to see whether the migration cost per
    line is a cross-complex cost. Performance.

### 2026-09-28 04:33 -07:00, two more follow-ups

From probe 19, which extended the marker to gate, sample, split, defer
and depends:

31. Probe 9, extended again: `close` returns the definition's token
    re-marked decoupled, to see whether the one bit plus sequencing
    removes both false refusals without rows. Not performance.
32. Probe 9, extended again: a split inside a `construct` that runs at a
    child instant, to see whether any path there escapes the
    per-instant rule. Not performance.

### 2026-09-28 04:39 -07:00, one more follow-up

33. Probe 10, extended again: every cell binding enumerated for
    programs of two to four nodes, instead of one sampled, to see
    whether a constructive loop outside the exclusive gates exists with
    a changing cell and two or more inputs. Not performance.

### 2026-09-28 04:47 -07:00, two more follow-ups

From probe 21, which found the small-side orders bounded only on
acyclic moves, and costly to reorder:

34. Probe 14, extended again: a mixed adversary, a large old upstream
    before the switch plus a new side of size k, to find where the walk
    and the backward search cost the same. Performance.
35. Probe 14, extended again: a moved set inserted with fresh spacing,
    so repeated inserts into one gap stop relabelling. Performance.

### 2026-09-28 05:10 -07:00, two more follow-ups

From probe 22, which found maintained labels cost a queue its O(1)
buckets rather than costing upkeep:

36. `rfd-0005-height-queue`, RFD 5, performance. Incremental's way:
    small-integer heights raised on link, with a bucket queue, the
    height raises at moves counted, to see whether it wins back the 16%
    crossover under switching.
37. Probe 22, extended: the schedulers rerun over flat adjacency, to
    check the ratios aren't an artefact of a vector-of-vectors graph.
    Performance.

### 2026-09-28 05:12 -07:00, two more follow-ups

From probe 23, which found the per-input work term sound under uneven
inputs:

38. Probe 15, extended again: the rate of spurious collections against
    the length of quiet stretches and the growth rate, with an input
    that grows and then shrinks by releasing a guard. Performance.
39. Probe 15, extended again: garbage on a medium-rate input whose
    first transaction after a collection lags many navigations, to
    bound the work term's worst misses. Performance.

### 2026-09-28 05:23 -07:00, two more follow-ups

From probes 25 and 26, which found a counted B-tree beats the rope from
ten thousand elements, and a fully lazy map wins by fusing its insert:

40. Probe 8, extended again: an eager delta for the map with the
    lookup, removal and insertion fused into one insert, to separate
    fusion from laziness. Performance.
41. Probe 8, extended again: a B-tree whose leaves share one index
    lookup for the source and the mapped collection, as a fused map
    node would. Performance.

### 2026-09-28 05:33 -07:00, three more follow-ups

From probe 24, which split the collection across units with insertion
barriers:

42. Probe 24, extended: garbage skipped by the region during the mark,
    or the next cycle started sooner, to lower the floor that small
    budgets hit. Performance.
43. Probe 24, extended: a work debt keyed to the total region, to see
    whether any debt pacing beats a fixed budget. Performance.
44. Probe 24, extended: probe 23's uneven workload under a budget of
    a thousand, where barriers and floating garbage would fire.
    Performance.

### 2026-09-28 05:34 -07:00, two more follow-ups

From probe 27, which found a safe rebrand costs a read little for
scalars and a copy per read for collections:

45. `rfd-0003-rebrand-write-cost`, RFD 3, performance. The same on the
    write side: storing token-bearing state into `hold` and
    `accumulate_mut`, safe against the cast.
46. Probe 27, extended: whether a derive can produce a borrowed view
    for generic structs and enums, and whether `sample` can return it
    from a `OnceCell` with no `unsafe`, keeping RFD 4's `&A`. Not
    performance.

### 2026-09-28 05:43 -07:00, two more follow-ups

From probe 28, which derived `Rebrand` and found the orphan rules leave
`Leaf` or Bough-side impls:

47. Probe 16, extended again: derive `Trace` beside `Rebrand`, and test
    that a skipped field and `Trace` agree. Not performance.
48. Probe 16, extended again: a copy-free read for generic types
    instantiated brand-free, such as `Tagged<u32>`. Not performance.

### 2026-09-28 05:47 -07:00, one more follow-up, and strace

Probes 29 and 30 installed `strace` in the container with `sudo dnf
install strace`, to cross-check the futex counts. It turned out to
disturb the run too much to use, and the counts come from a counting
copy of std's mutex instead.

49. Probe 13, extended again: the counting mutex pinned within one core
    complex and across both, with the time per wake, to see whether a
    wake across complexes explains the gap between placements.
    Performance.

### 2026-09-28 06:00 -07:00, two more follow-ups

From probes 31 and 32. They found the decoupledness mark, in every
design tried, accepts an illegal loop that hands a switch its own
consumer's steps as a token, so a compile-time check can cover `close`
only, and the run-time check at a switch's moves stays.

50. Probe 9, extended again: when a close leaves no loop open, re-mark
    everything, with type-state on `Build`. Not performance.
51. Probe 9, extended again: switches that require decoupled inners at
    the type level, to see whether that closes the hole and keeps the
    navigation loop. Not performance.

### 2026-09-28 06:18 -07:00, one more follow-up

52. Probe 14, extended again: the backward search's cost split into
    search, sort, unlink and relink, and a move that keeps the search's
    own order when it is already topological, the one lever left that
    could move where the list beats the walk. Performance.

### 2026-09-28 06:25 -07:00, two more follow-ups

From probe 36, which found Incremental's small-integer heights with a
bucket queue cost about 3% more than RFD 5's mark when everything
fires and win from about 5% quiet, under switching. That contradicts
the reason RFD 5 gives for rejecting rank-ordered push; it is reported
as a finding.

53. Probe 36, extended: nodes built during the instant and evaluated
    in it, which needs a height raise mid-evaluation with the cursor
    already past. It is the case RFD 5's rejection names, and it
    wasn't tested. Performance.
54. Probe 36, extended: a local height repair after a refused move, to
    see whether the height growth that refusals cause goes away
    cheaply. It matters only if Bough carries on after a refusal
    instead of poisoning. Performance.

### 2026-09-28 06:34 -07:00, two more follow-ups

From probes 38 and 39, which found no region term sees garbage that a
dropped guard releases, and RFD 3's release term too small to fire:

55. Probe 15, extended again: a release term that sees garbage, such
    as counting every region node after a release until the next
    collection. Performance.
56. Probe 15, extended again: released screens on the input that fires
    every unit, with no growth, to bound the worst cost rather than
    the peak ratio. Performance.

### 2026-09-28 06:45 -07:00, two more follow-ups

From probes 40 and 41, which found fusion, not deferral, carries the map
result, and one shared B-tree cuts its cost by about 40%:

57. Probe 8, extended again: the fused delta handing its filter a real
    Z-set, as separate nodes would, to price the node boundary for an
    engine that doesn't fuse. Performance.
58. Probe 8, extended again: the shared B-tree with leaves of 32 pairs,
    the same bytes as the two-tree leaves, to see whether the gain is
    one descent or fewer bytes moved. Performance.

### 2026-09-28 07:02 -07:00, two more follow-ups

From probe 53, which found heights still beat RFD 5's mark once nodes
built during the instant run in it, with the re-ranking RFD 5 names
coming to a fraction of a raise a transaction:

59. Probe 36, extended again: a navigation whose selector sits high, so
    raises reach below the cursor, to test re-seating against
    evaluating out of order. Performance.
60. Probe 36, extended again: a mark that doesn't start from the root
    event stream at every navigation, to separate how much of the
    heights' lead is the larger marked region. Performance.

### 2026-09-28 07:04 -07:00, two more follow-ups

From probes 42 to 44, which found a fixed budget beats every debt pace
and the barriers' slow path never fires:

61. Probe 24, extended again: units that insert edges to old nodes,
    such as navigating back to a kept screen or I/O re-anchoring an old
    token, to exercise the barriers' slow path. Partly performance.
62. Probe 24, extended again: the born-before-the-cycle reference on the
    uneven workload's per-input references. Performance.

### 2026-09-28 07:16 -07:00, three more follow-ups

From probe 45, which found a safe rebrand makes `accumulate_mut` cost in
proportion to its state, and two safe ways around it:

63. Probe 45, extended: whether rebranding by value stays constant-time
    at lower optimisation levels, and what the nested shape's extra is.
    Performance.
64. Probe 45, extended: an accumulator that pushes a token every event
    out to ten thousand events, to confirm or refute the quadratic cost
    directly. Performance.
65. With 46: derive the mutable borrowed view for generics and enums,
    and see whether a list view can offer `retain` and `sort_by` with
    no `&mut Vec` at the writer's brand. Not performance.

### 2026-09-28 07:36 -07:00, two more follow-ups

From probe 37, which found the scheduler ratios hold over flat
adjacency, the crossovers moving 3 to 5 points of quiet share:

66. Probe 22, extended again: flat slices without bounds checks, or true
    compressed rows, timed by wall-clock, to see whether the layout's
    cache gain moves the crossovers in time. Performance.
67. Probe 22, extended again: built nodes' slices given room from the
    start, to see whether building during the instant makes the flat
    layout's upkeep matter. Performance.

### 2026-09-28 07:39 -07:00, two more follow-ups

From probes 46 and 65, which derived borrowed views with no `unsafe`,
and found a hand-written view impl can stash a static token, as the
committed `view` can:

68. Probe 16, extended again: whether a trait only the derive can
    implement, sealed or `unsafe` with the derive writing the impl,
    closes that route without breaking `forbid(unsafe_code)` in user
    crates. Not performance.
69. Probe 16, extended again: `accumulate_mut` at commit through the
    mutable view, in a toy whose commit owns its values. Not
    performance.

### 2026-09-28 07:41 -07:00, two more follow-ups, one of them limited

From probe 49, which found, indicatively, that a wake across core
complexes explains about 70% of the mutex's gap between placements:

70. Probe 13, extended again: whether wake cost and wake-to-run latency
    are idle-state exit, tested only with a busy-spinning thread on the
    sleeper's core. Capping idle states with `cpupower` would change
    the host's power settings, which is Zefira's call, so it isn't
    done. Performance.
71. Probe 13, extended again: a trace of the wake through the kernel, to
    see whether the cross-complex cost is the remote wake path. Tried
    only if `perf` works in the container as it stands; nothing on the
    host is changed for it. Performance.

### 2026-09-28 07:58 -07:00, two more follow-ups

From probes 50 and 51, which found a mark on a switch's output refuses
every smuggle and keeps navigation, at the price of a switch nested in
a switch, and a last-open-loop rule with holes of its own:

72. Probe 9, extended again: a generative brand per switch, to accept a
    switch nested in a switch without reopening the smuggles. Not
    performance.
73. Probe 9, extended again: the last-open-loop rule with a generative
    brand and an explicit epoch bump, to remove the hole where two
    builds trade a loop, and the refusals of a loop in a `for` or an
    `if`. Not performance.

### 2026-09-28 08:00 -07:00, a caveat and three more follow-ups

Probes 47, 48 and 68 found that the brand-erasure harness compiled its
fixtures with `--cap-lints allow`, which caps `forbid` too. So no
committed run of probes 16, 28 or 46 enforced `forbid(unsafe_code)`,
and their "sound with no `unsafe`" rests on inspection: no fixture has
the `unsafe` keyword. Follow-up 75 checks it.

74. Probe 16, extended again: entry points such as `anchor` that require
    `T: Rebrand<Of<'g> = T>`, so a stashed static token can't get back
    into a `mutate`, which could make the stash harmless with no seal.
    Not performance.
75. Probe 16, extended again: every committed mode re-run with lints
    uncapped, to confirm `forbid(unsafe_code)` holds. Not performance.
76. Probe 16, extended again: the bare `unsafe` seal on the borrowed
    views, to see whether it closes the stash through `Borrow`. Not
    performance.

### 2026-09-28 08:07 -07:00, phase 5 stops taking follow-ups

Zefira chose to stop the follow-up chain. The later follow-ups had
turned from checking findings to designing APIs Bough hasn't chosen, and
would refine answers that no longer move a leaning. What finishes:

- The two agents running: 52 (the backward search profiled), and 74 to
  76, whose re-check of `forbid(unsafe_code)` with lints uncapped is a
  validity check on committed claims.
- 60 is built: it separates how much of the height queue's lead over
  RFD 5's mark comes from a larger marked region, a confound in a
  finding that contradicts a settled decision.

Dropped, not built, each recorded above with what it would settle: 54,
55, 56, 57, 58, 59, 61, 62, 63, 64, 66, 67, 69, 70, 71, 72, 73. The
reason, in short: the brand and marker chains design options the
grilling hasn't picked, and the rest tune constants inside findings
already clear. 66 and 67 are partly answered by phase 6's wall-clock.

Phase 6 starts once those three are committed, around 09:00 rather
than 11:30, which leaves slack before 14:00.

### 2026-09-28 08:36 -07:00, phase 5 done: the probes, and phase 6's commands

Phase 5 is done. Every probe the stop left in is built, run where it
doesn't need timing, and committed: `experiments@e7ad1a9` (the setup)
to `experiments@8c9ed83`, one probe or extension at a time, each code
commit followed by its results with the provenance line filled in.
Zefira is awake and starts phase 6 in a session of her own; this one
stops here.

What's there:

- The thirteen probes from phase 3, and the follow-ups built before the
  stop: 14 to 53, 60, 65, 68 and 74 to 76, many as extensions of an
  earlier probe. 29 bench targets, 14 of them wall-clock; binaries for
  the rest; fixtures for code that must fail to compile; one workspace
  member, the `Rebrand` derive.
- `results/` holds every binary's output and every gungraun run, each
  file named for its target and run. Timings taken during phase 5 are
  in the scratch directory only, marked indicative.
- The orchestrator's log of every report, with its numbers, is
  `research-scratch-space/probes/reports.md`. Drafting can start there;
  every number in it is in a committed result file.
- `cargo fmt` and clippy with warnings as errors are clean across the
  workspace. `cargo test --release --workspace` passes but for one
  flaky assertion: `rfd_0006_lock_vs_queue_cost::tests::footprints_agree`
  checks the ticket lock hands off in over half the units, which failed
  once in a full parallel run and passed three times alone. It depends
  on scheduling, not on the probe's numbers.

Findings the review must report, with the probes behind them. The
numbers are instruction counts unless marked; wall-clock is phase 6's.

- **RFD 5's reasons for rejecting rank-ordered push don't hold on
  their own** (contradicts a settled decision's stated reason). With
  static heights a bucket queue beats the mark from about 16% quiet
  (3). Under switching, Incremental's small-integer heights cost about
  3% more than the mark when everything fires and win from about 5%
  quiet, the re-ranking RFD 5 names coming to a fraction of a raise a
  transaction (36, 53). With the confound removed that probe 53's
  model had, the crossover stays near 5% quiet and the wins shrink
  (60). Labels from an order-maintenance list lose to heights (22).
- **RFD 5's per-move walk stays.** The DFS mark's grey state can't
  replace it: it finds a cycle only when an input next reaches it, and
  never if none does (1). Kept orders beat the walk on UI-shaped graphs
  but not in general; with the sort removed, only once the old upstream
  is about twice the new side (2, 14, 21, 34, 35, 52).
- **RFD 3's collection trigger needs a work term** (contradicts the
  settled trigger's sufficiency). Beside a large live graph it let
  garbage pile up at about 8 times the cost of a work-paced trigger
  (4, 15), and a per-input reference stays sound under uneven inputs
  (23, 38, 39). No region term sees garbage a dropped guard releases.
  An incremental mark with insertion barriers splits the pause about
  ten times for about 9% (24, 42 to 44).
- **RFD 3's "cannot be made a compile error" doesn't hold.** A lifetime
  brand makes F62 a compile error on stable, soundly with no `unsafe`,
  confirmed with lints uncapped (6, 16, 75). It costs a lifetime on
  every type and helper that holds tokens and I/O inside callbacks, a
  copy per read and write unless borrowed views replace `&A` (27, 45,
  46), and a stash route through hand-written impls that entry bounds
  narrow but don't close (47, 48, 68, 74, 76).
- **RFD 2: the decoupledness mark can check `close`, not switches.**
  One bit refuses F3 and costs little to compile (9, 19), but every
  marker design accepts a loop smuggled through a switch (31, 32); a
  mark on a switch's output closes that at the price of switches nested
  in switches (50, 51). The census of refused loops supports plain
  acyclicity (10, 20, 33).
- **RFD 1: the creation cut is forgetful, and one rule covers it.** A
  cut on state-holders and time-movers only never differs from a cut
  on every primitive; the text leaks exactly on F6 and F89 shapes (11).
  Child indices would catch more mutants, and what the oracle misses
  is invisible to its programs (12).
- **RFD 4: erasing the chain at the materializer** cuts F36's build
  times to about a third for 3 instructions an event (7, wall-clock
  pending). **Question 9**: a patch-carrying cell wins from small
  sizes; a counted B-tree for positions and a fused upsert for maps
  (8, 17, 25, 26, 40, 41); Z-set composition fails for two sources
  upserting one key.
- **RFD 6: an uncontended lock costs about 1%, RFD 6's queue 10 to 20%**
  (contradicts the single-thread rationale's stated reason). Contended,
  the lock loses more than the queue, mostly to a futex wake per unlock
  and a wake across core complexes, per the counts and indicative
  timings (13, 18, 29, 30, 49).

Unclear results for Zefira to recheck: the height-queue crossover
between 2% and 30% quiet is interpolated (60); the lock's mechanism
rests on indicative timings (18, 29, 30, 49); probe 8's large-`Vec`
rows are memmove artefacts under valgrind until wall-clock (8, 25).

Choices made inside the plan:

- Probes that must fail to compile are fixtures a binary compiles, not
  targets. Compile time is measured by binaries that build generated
  crates, run with the wall-clock benches.
- A counts run that needs no timing is sometimes a library test, not a
  binary, where the probe had no binary stub; its result file gives the
  exact command.
- The two sub-agents at once shared one repository; targets were
  declared as stubs ahead of time so they never edited the manifest
  together. Once, briefly, a third was started by mistake and stopped
  before it wrote anything.
- `strace` was installed with `sudo dnf` (probes 29 and 30), and
  `libc` joined the dependencies for thread affinity.
- Extensions changed some earlier probes' shared code, and a few
  earlier counts moved by up to 6.6% from code layout. Every count
  reproduces only at the commit its result file cites. Verification
  must check out that commit.

#### Phase 6: the commands

Run from `~/prog/bough/experiments` on the idle machine: boost off,
governor `performance`, nothing else running, as this night's first
addition describes. Save each command's full output as
`results/<target>-<date>.txt` with the provenance line, and commit.

**Run `scripts/ratios.py` straight after each bench, before the next
one.** Several benches share Criterion group names (`moves` and `build`
in two, `nav` and `app` in two), so a later bench overwrites an earlier
one's samples under `target/criterion`. Save the ratios with the bench.
`ratios.py` compares each variant with its group's `baseline` only;
the reports name the comparisons to read by hand.

In order, RFDs 3 and 5 first, since they gate the build. Durations
are the agents' estimates, not timed; the whole run is likely two to
three hours.

1. `cargo bench --bench rfd-0005-height-queue-wallclock` (about 9 min),
   then `python3 scripts/ratios.py`.
2. `cargo bench --bench rfd-0005-maintained-rank-queue-wallclock`, then
   `python3 scripts/ratios.py settled mixed churn lazy upkeep flat-settled flat-mixed flat-churn flat-lazy`.
3. `cargo bench --bench rfd-0005-heap-vs-mark-on-quiet-regions-wallclock`,
   then `python3 scripts/ratios.py ui-small ui-large frame`.
4. `cargo bench --bench rfd-0005-small-side-order-wallclock` (about 10
   min), then `python3 scripts/ratios.py`.
5. `cargo bench --bench rfd-0005-bounded-relink-check-wallclock`, then
   `python3 scripts/ratios.py moves build`.
6. `cargo bench --bench rfd-0005-demand-bounded-push-wallclock`, then
   `python3 scripts/ratios.py nav app`.
7. `cargo bench --bench rfd-0003-work-paced-trigger-wallclock` (about 8
   min), then `python3 scripts/ratios.py nav app pause-nav pause-app uneven-spread uneven-sparse pause-uneven-spread pause-uneven-sparse uneven-lagging fast-path`.
8. `cargo bench --bench rfd-0003-incremental-mark-wallclock`, then
   `python3 scripts/ratios.py incremental-`.
9. `cargo bench --bench rfd-0003-sweep-cost-wallclock` (about 5 min),
   then `python3 scripts/ratios.py live10 live90`.
10. `cargo bench --bench rfd-0003-rebrand-cost-wallclock` (about 4 min),
    then `python3 scripts/ratios.py`.
11. `cargo bench --bench rfd-0003-rebrand-write-cost-wallclock` (about 5
    min), then `python3 scripts/ratios.py write_`.
12. `cargo bench --bench rfd-0004-erased-materializer-wallclock`, then
    `python3 scripts/ratios.py`; and
    `cargo run --release --bin rfd-0004-erased-materializer` (compile
    times, about 14 min).
13. `cargo bench --bench rfd-0004-patch-cell-crossover-wallclock` (about
    9 min), then `python3 scripts/ratios.py vec- map- compose`.
14. `cargo run --release --bin rfd-0002-decoupled-marker -- --compile-time`
    (about 7 min).
15. `cargo bench --bench rfd-0006-lock-vs-queue-cost-wallclock` (about 7
    min; the spreads and hand-off tables print after Criterion's
    report), then `python3 scripts/ratios.py single contended footprint-`;
    and `cargo run --release --bin rfd-0006-lock-vs-queue-cost -- --timed`.

Next: phase 6, in Zefira's session. Then phase 7, drafting.

#### Context

Phase 5 of the FRP literature review is done. The thirteen probes and
the follow-ups built before the stop are committed in `experiments`,
with every instruction count and non-timing result in `results/`.
Several findings contradict the stated reasons of settled decisions in
RFDs 3, 5 and 6, and are reported as findings, as Zefira ruled. What's
left is the wall-clock run, which needs the idle machine: fourteen
Criterion benches and two compile-time binaries, listed above in order,
RFDs 3 and 5 first.

### ❓ **Running phase 6**

Phase 6 runs the wall-clock benches in one batch on an idle machine.
Zefira starts it in a session of her own. When?

Running phase 6:

- **(a)** When the machine can sit idle for about three hours: boost
  off, the governor at `performance`, nothing else running. The session
  runs the fifteen steps above in order and commits the results.

➡️ **(a)** The instruction counts are in; only the wall-clock ratios
wait, and they need the machine to themselves.

### 2026-09-28 08:55 -07:00, phase 6 goes

Zefira chose (a) and starts phase 6 now, in a session of her own. It
runs the fifteen steps in the last addition, in order, taking the
ratios after each bench.

### 2026-09-28 11:35 -07:00, phase 6 done: the wall-clock run

Every step of phase 6 ran in one batch, 09:54 to 11:34, with no failure.
The results are `experiments@ce14249` to `experiments@1241138`, one
commit per probe. Every result file cites `experiments@daa6419`, the
commit that was checked out for the run and holds the script that ran
it. That differs from phase 5, whose files cite each probe's own code
commit.

The machine, checked before the start:

- Boost off and the governor at `performance`, logged before every step
  and unchanged throughout.
- Zefira stopped and masked GNOME's file indexer, `localsearch`, which
  was using about 10% of a core on the host, and stopped
  `bough-name-watch.timer`, the crates.io curl.
- She set the tuned profile to `latency-performance` instead of the
  night's `throughput-performance-bazzite`, to keep deep sleep states'
  wake-up jitter out of the timings. The container can't read the
  profile; the run's log records it as set on the host.

How the run went, and the choices made inside the plan:

- **One script ran it all:** `experiments/scripts/phase6.sh`
  (`daa6419`). It builds every target first, so nothing compiles between
  benches. Then, in the fifteen steps' order, it runs each bench, runs
  `ratios.py` with that step's prefixes, and appends the ratios to the
  same result file. The binaries' output goes to
  `results/<name>-compile-time-<date>.txt` and
  `results/<name>-timed-<date>.txt`.
- **Each bench starts from an empty `target/criterion`,** and its
  samples are moved to
  `research-scratch-space/phase6-criterion/<target>/` straight after.
  So no bench's ratios can pick up another's samples, whatever the group
  names, and the raw samples are kept for verification. Phase 5's
  indicative samples, left in `target/criterion`, are in
  `phase6-criterion/pre-phase6/`, not in any ratio. The log is
  `phase6-criterion/run.log`.
- **A smoke run came first,** with `PHASE6_SMOKE=1`: Criterion's
  `--quick`, the materializer's `--quick`, and the two long binaries
  skipped, everything written to `research-scratch-space/phase6-smoke/`.
  Its numbers aren't results.
- **The load average reads 2 to 5 during the run.** That's Criterion's
  analysis, which bootstraps its statistics across all cores with rayon
  after each benchmark's measurement, not during it. The measurement is
  single-threaded, so the samples don't see it. The machine went back to
  idle when the smoke run ended.
- **Criterion warned 51 times that it couldn't finish its samples in the
  target time.** It extends the time instead, so every benchmark has its
  full sample count.
- **The lock probe's `--timed` table still prints "INDICATIVE ... not on
  an idle machine".** The label is fixed text from phase 5. This run was
  on the idle machine, pinned, so drafting can read these as measured.

Next: phase 7, drafting, in a fresh session. The wall-clock ratios are
in the result files beside the instruction counts. Drafting checks them
against phase 5's findings, the ones marked "wall-clock pending" above
all, starting with probe 7's erasure and probe 8's large-`Vec` rows.

### 2026-09-28 17:54 -07:00, phase 7 done: the note is drafted

The note is `research/2026-09-28-frp-literature-review.md`, "What the FRP
literature says to Bough", committed section by section in `95e85c4` to
`16e32d9`: the header, the must-read at 998 words, the nine dimension
sections, the lineage map, the crate table and the annotated
bibliography of the 99 kept sources. It isn't in the book yet; that's
phase 9. Its header says it is unverified.

The wall-clock run moved some of phase 5's findings. Drafting quotes
wall-clock where the two disagree, and says so where it matters:

- **RFD 5's heights.** Phase 5's counts had Incremental-style heights
  2% to 3% dearer than RFD 5's mark when everything fires and winning
  from about 5% quiet. On the idle machine they cost 25% to 31% more when
  everything fires and break even near 30% quiet, still winning up to
  eighteen times on mostly quiet regions. The contradiction of RFD 5's
  stated reasons stands; what's left is a trade. The static-height bucket
  queue's break-even moved from about 16% to about 26% quiet.
- **RFD 3's work term** costs about a tenth on the `nav` shape, not 2%
  to 7%, and is still worth about ten times on `app`. The incremental
  mark at k = 1,000 costs 16% more time, not 9.5%.
- **Probe 8's large-`Vec` rows are real.** The flat delta loses on rare
  reads at every size from 10,000 up in wall-clock too, so they weren't
  valgrind artefacts. The leaning moves to counted B-trees.
- **Two results disagree with themselves**, reported as unclear in the
  note: the incremental mark's single-unit benches put the barriers'
  fast path at 18% to 30% of a unit while a whole run with barriers costs
  0.7%; and the `owned` rebrand, constant-time in instructions, costs 62
  times a cast per update of a 1,000-element `Vec` in wall-clock.
- The work-paced probe's `total` policy costs 2.2 times on a clean click
  because that bench times its spurious collections, as the bench says.
  That one is explained, not unclear.

Choices made inside the plan:

- **Where provenance goes.** Each dimension section has a "What the
  probes found" subsection, which the handoff's list doesn't name, and
  every result file it quotes follows it: the file's provenance line and
  the command that made it, plus the `ratios.py` call for wall-clock. The
  must-read quotes a few numbers and relies on the sections for their
  provenance.
- **The bibliography's citation lines are generated** from the records'
  frontmatter by a script in the scratchpad, so they can't drift from
  `literature`; the annotations are written by hand from the reading.
- **The Z-set composition failure** is cited to a test in the probe's
  module, `rfd_0004_patch_cell_crossover::tests::same_key_conflict`, run
  at `experiments@daa6419`, since no result file records it.
- **"Transaction" means Bough's** in the concurrency section, which says
  so, since Lee's and Drechsler's are the database sense.

For the verifier:

- `rfd-0001-forgetful-cut`'s verdict line says 5,012 leaking nodes, and
  its table 4,632. The verdict counts the whole-rerun check's nodes too.
  The note quotes the table.
- Phase 5's reports log summarized some probes from earlier runs; every
  number in the note was taken from a committed result file, not from the
  log, except where the section says it comes from instruction counts.
- The Incremental (OCaml) rows cite tag v0.17.0 with no commit, as batch
  14 read it; `PINS.md` doesn't list it.
- Two corrections were made during drafting and are commits of their
  own: three ratios in the scheduling section read from the wrong pass
  rate or the wrong side, and the lagging input's misses.

Next: phase 8, verification, by a fresh sub-agent in a fresh session. It
gets the note, `literature` and `experiments`, and none of this session's
reasoning. Nothing is open.

#### Context

Phase 7 of the FRP literature review is done. The note is drafted and
committed, unverified. Phase 8 hands it to a fresh sub-agent that checks
every claim against its page in the stored copy and re-runs every probe,
instruction counts within 1% and wall-clock ratios by overlapping
intervals, with the drafting session fixing what it finds. It stops if a
fix would change a must-read finding, or if a number fails to reproduce
twice. The wall-clock re-runs need the idle machine again: boost off, the
governor at `performance`, nothing else running.

### ❓ **Starting phase 8**

Verification re-runs every probe, wall-clock included. When does it
start?

Starting phase 8:

- **(a)** In a fresh session, when the machine can sit idle for the
  wall-clock re-runs, about two hours on the last run's evidence. The
  claim checks and instruction counts don't need it and can go first.

➡️ **(a)** Checking claims against pages needs no idle machine, so the
session can start with those and ask for the machine only when it reaches
the wall-clock benches.

### 2026-09-28 18:15 -07:00, phase 8 waits for a fresh session

Zefira chose (a). She starts phase 8 in a fresh session once her weekly
usage resets, in a few hours. It checks claims against pages and re-runs
the instruction counts first, and asks for the idle machine only when it
reaches the wall-clock benches. Nothing else is open.

### 2026-09-29 06:05 -07:00, phase 8 stopped: two must-read fixes and the idle machine

Phase 8 ran from 03:28. The claims check and the instruction-count
re-runs are done; the wall-clock re-runs aren't started. It stops on
three things: two fixes that would change a must-read finding, the
handoff's stop, and the idle machine the wall-clock needs. The note's
header says where verification stands.

How it ran. The brief every verifier got is
`research-scratch-space/verify/brief.md`, with `claims-task.md` and
`probes-task.md` beside it. Each verifier was a fresh sub-agent given the
note, `literature`, `experiments`, Bough's notes and the crate clones,
and none of the drafting. At most two ran at once: the probe verifier
throughout, and the claims verifiers one at a time.

- **Claims, in seven slices:** semantics with verification and testing;
  switching with loops; scheduling; memory; values with concurrency;
  embedded with the lineage map and crate table; and last the
  bibliography, with the must-read checked against the corrected
  sections. About 1,600 claims, 99 errors: 27 overstated, 14 misread, 12
  unsupported, 11 wrong pages, 11 wrong numbers, 10 metadata (8 missing
  years), 9 internal, 3 misattributed, 2 missing provenance lines. Two
  of the must-read's numbers were wrong, both listed below. I fixed each
  slice's
  errors, and the verifier that found them re-checked what changed until
  it was clean. The fixes brought in five more errors, all caught that
  way. Commits `3c0be00` to `a89bb57` on this branch.
- **Probes:** all 66 result files that don't need wall-clock, re-run
  from a scratch clone, each at the commit it cites. 62 reproduce, every
  instruction count within 1%; `same_key_conflict` passes at `daa6419`.
  The re-runs and scripts are in `research-scratch-space/verify/probes/`.

What the probe re-runs found besides:

- **The four `rfd-0004-patch-cell-crossover` instruction files don't
  reproduce in their `map_*` benchmarks,** after a clean second run. The
  fixture builds std `HashMap`s with the default per-process seed, so
  those counts move by up to 11% between runs. Every `vec_*` and
  `compose_*` benchmark matches exactly. The note quotes no `map_*`
  instruction count; its map numbers are wall-clock, which is one seed
  too.
- **The futex tables depend on scheduling.** The story holds, about one
  wake per unlock at 256 KiB, but the ranges moved, so the note now gives
  both runs'. The pinned table's cross-complex wakes came out lower than
  within-complex in the original run and higher in the re-run; the note
  claims no direction for them.
- **Three phase 5 runs came from working trees with two or three
  uncommitted tests**
  (`small-side-order-counts-adversarial`,
  `maintained-rank-queue-counts`, `height-queue-counts-pull`). Their
  tables reproduce byte for byte at the cited commits; only libtest's
  "filtered out" count differs.
- **A trap for any later re-run:** a shared `CARGO_TARGET_DIR` across
  `git archive` trees silently links a stale `bough-experiments`,
  because the archive's file times are older than the artifact. Touch
  each tree before building. The first pass hit this and was thrown
  away.

Choices made inside the plan:

- **The verifiers couldn't write files;** the harness refuses sub-agent
  writes. Their reports came back as messages, and the slice summaries
  in `verify/` are mine.
- **Wording-only must-read fixes were made,** and listed here so Zefira
  can reverse them: garbage costs ten times as much, not runs ten times
  longer; a `Switched` mark does catch a smuggled loop, at the price of
  nested switches; erasure builds in about two-fifths of the time, not a
  third; Drechsler et al. call an uncontended lock negligible, not free;
  F3 ties questions 3 and 10. Each keeps its finding and leaning. The
  must-read was 1,008 words by `wc -w` at phase 7; it's trimmed to 1,000.
- **Crate citations name the repository's tag** (`leptos@v0.8.21`, not
  `reactive_graph@`), with paths from the repository root.
- **Paragraphs the fixes left over-long were refilled** in a commit of
  their own, whitespace only, checked by comparing normalized text.

Next: Zefira's answers below. Then the wall-clock re-runs on the idle
machine: the fifteen steps of phase 6 through `scripts/phase6.sh` at
`daa6419`, each ratio compared by overlapping intervals with the one the
note quotes. Then the header's last line, and phase 9.

#### Context

Phase 8 of the FRP literature review verified the note's claims and
re-ran its instruction counts. Every error found is fixed except two,
where the fix would change what a must-read finding says, so they wait.
Both sections behind them are already corrected.

The first is RFD 6. The must-read says six findings contradict what a
settled decision says, "five stated reasons, and RFD 3's collection
trigger", and one of the five is the single thread's overhead reason.
But RFD 6 states no overhead or determinism reason. Its one reason is
that a host owns the schedule, which the evidence supports. The overhead
claim is the no-std handoff's, and "a transaction is a pure function of
its inputs" is RFD 2's, given for the re-entrancy check.

The second is RFD 7. The must-read says "Every bounded system compiles
a static graph". The embedded section's own sources disagree:
Krishnaswami, Benton and Hoffmann prove a bound for a language with
switching, Céu preallocates declared pools of dynamic instances, and
Oeyen et al. bound conditional signals and dynamic deployments. What
holds is that every bounded system either compiles a static graph or
bounds creation up front.

### ❓ **The RFD 6 finding in the must-read**

RFD 6 states no overhead reason for the single thread. How should the
must-read put the finding that no source supports "threading costs
overhead"?

The RFD 6 finding in the must-read:

- **(a)** Say whose reason it is. The must-read counts four stated
  reasons of RFDs, plus the no-std handoff's overhead claim, which the
  single thread was built on and no source supports. RFD 6's own reason,
  the host owns the schedule, stands. The leaning is unchanged: keep the
  single thread and write its reasons down.
- **(b)** Keep the count at five stated reasons, treating the no-std
  handoff's rationale as the settled decision's. The header records that
  RFD 6 itself doesn't state it.

➡️ **(a)** The must-read is what you'll read, and it shouldn't say an RFD
argues something it doesn't. It costs a few words, trimmed elsewhere.

### ❓ **The RFD 7 finding in the must-read**

"Every bounded system compiles a static graph" is too strong. What should
the must-read say?

The RFD 7 finding in the must-read:

- **(a)** "Every bounded system compiles a static graph or bounds
  creation up front", as the section now says. It keeps "no static engine
  in core" supported, and it puts a pooled `construct` on the table,
  which RFD 7's own text already names as the other option.
- **(b)** Keep the sentence, and let the section carry the
  qualification.

➡️ **(a)** The pools are the most useful thing the embedded line offers
the bounded tier, and the must-read shouldn't hide them.

### ❓ **The wall-clock re-runs**

The wall-clock re-runs need the machine idle for about two hours: boost
off, the governor at `performance`, nothing else running, as for phase
6. When, and do the patch-cell map benches get extra runs?

The wall-clock re-runs:

- **(a)** When the machine can sit idle, a fresh session runs the fifteen
  steps at `daa6419` and compares each ratio with the note's. The
  patch-cell bench runs three times, so the map rows show their spread
  across hash seeds. A map result the note quotes stands only if all
  three agree with it.
- **(b)** The same, but the patch-cell bench runs once, like the rest.

➡️ **(a)** The map rows are the only ones known to vary with the seed,
and three runs of one bench add about twenty minutes.

### 2026-09-29 08:37 -07:00, phase 8 stopped again: the wall-clock rule

Zefira answered (a) to all three questions at 06:30, and said the
machine was idle. Done since:

- **The must-read's two findings are fixed** (`fb30418`, `5b45917`): the
  overhead reason is the no-std handoff's, and RFD 6's own, the host
  owns the schedule, stands; every bounded system compiles a static graph
  or bounds creation up front. Other wording was trimmed to keep 1,000
  words, and the verifier found both fixes clean.
- **The wall-clock re-run ran** 06:32 to 08:27, every step without
  failure: a copy of `scripts/phase6.sh` from a scratch worktree at
  `daa6419`, so `experiments` is untouched, with the patch-cell bench
  three times. Boost stayed off and the governor `performance`
  throughout; the container can't read the tuned profile, so the log
  doesn't claim one. Nothing else ran but one read-only verifier for a
  few minutes. The script, results, log and Criterion samples are in
  `research-scratch-space/verify/wallclock/`.
- **A fresh verifier compared** every wall-clock number the note quotes
  with the re-run, 168 numbers and derived claims. Its report is
  `verify/wallclock/report.md`.

What the comparison found:

- **92 reproduce by the handoff's rule, overlapping intervals. 76
  don't.** Criterion's intervals are 0.2% to 0.5% wide, and this machine
  moves 1% to 5% from one day to the next, so an interval rarely
  overlaps across days. For 69 of the 76 the note's claim still holds,
  and for about 20 its rounded figure doesn't change.
- **Six claims don't hold as worded:** no-sort's "0.73 to 1.13" on
  cycles is 0.61 to 1.24 now, beating the walk by 40% on two cycle
  shapes, whose rows swing by up to 40% between runs; the flat `Vec`
  delta isn't best for appends at every size in one of three runs; the
  fully lazy map loses at 10 entries in one of three runs, a
  hash-seed row; the barriers' fast path is 17% to 53% of a unit, not
  18% to 30%, already flagged for a recheck; the lock changes threads in
  1.2% of units, not under 1%; and the bench's cross-complex wake is
  1.87 µs, not 1.65.
- **The lock's tail figures are single draws:** the longest wait moved
  from 165 µs at 2 threads to 224 µs at 8, and the longest run by one
  thread from 11,087 units to 451. The median and p99 story holds.
- **Compile times and the timed binary reproduce,** within 4%.
- **No must-read finding changes.** Every number it quotes holds as
  worded, the rounding included.

Nothing in the note is changed by this yet. The handoff says to stop if
a number still doesn't reproduce after one re-run, and the question is
whether a third run would tell anything.

#### Context

Phase 8 re-ran every wall-clock bench of the FRP literature review on
the idle machine, from the same code as phase 6, and compared it with
the numbers the note quotes. The handoff's rule is that a wall-clock
ratio reproduces if its interval overlaps the quoted one. 92 of 168
numbers do. The other 76 miss by 1% to 5%, because Criterion's
intervals, a few tenths of a percent wide, only measure the noise within
one run, not the drift between days. 69 of the 76 still support what
the note says. Six claims fail as worded, and one bench's tail figures
don't repeat. None of it changes the must-read. The handoff says to
stop when a number still doesn't reproduce after one re-run.

### ❓ **What "reproduces" means for wall-clock**

Overlapping intervals fail across days on this machine even when
nothing has changed. What should the rule be?

What "reproduces" means for wall-clock:

- **(a)** A ratio reproduces if the re-run is within 5% of it and
  supports the claim the note makes with it. The note's header says
  its wall-clock ratios are good to a few percent, measured on two days.
  The six failing claims are reworded to what both runs support, the
  noisy cycle rows and single-run tail figures are marked as such, and
  there's no third run. Verification then finishes in this session.
- **(b)** Keep the handoff's rule. The benches behind the 76 misses run
  once more, about two hours on the idle machine, and whatever still
  misses stops the phase again.

➡️ **(a)** A third run measures the drift again and will miss the same
way. What Zefira needs to trust is the claims, and the drift is small
next to every margin a leaning turns on.

### 2026-09-29 08:47 -07:00, phase 8 done: the note is verified

Zefira chose (a): a wall-clock ratio reproduces if a second day's run is
within a few percent and supports the note's claim, since the
machine's drift between days defeats overlapping intervals. Done since:

- **The six failing claims are reworded** to what both days support,
  and the lock's tail figures are marked as single draws (`9fbbaea`).
  The wall-clock verifier re-checked them, twice, and found the header
  undersold how far the adversarial rows move; fixed in `ad7ae7e` and
  `05401c7`. Clean.
- **The second day's result files are in `experiments`**
  (`experiments@8f7eb89`), with the script as it ran,
  `scripts/phase8-wallclock.sh`, since the note now quotes some of their
  figures. Each quoted one has its provenance line.
- **The note's header** now records the whole verification: what was
  checked and how, the errors by kind, the two must-read fixes Zefira
  approved, the count re-runs, and the wall-clock comparison.

One thing is unconfirmed: the tuned profile on the second day. Phase 6
had `latency-performance` set on the host; the container can't read it,
so the re-run's log doesn't say.

From here the note is kept as written, as `research/README.md` says.

Next: phase 9 in a fresh session. Put the note in the book, with a stub
in `src/research/` and a line in `src/SUMMARY.md` under Research, write
the final addition, and point Zefira at the must-read. Nothing is open.

### 2026-09-29 09:05 -07:00, the second day's tuned profile

Zefira set the host's tuned profile to `latency-performance` before
phase 8's wall-clock run, as for phase 6. Read from the container with
`distrobox-host-exec tuned-adm active`, which needs no sudo, the host
reports "Current active profile: latency-performance". So both days ran
with the same settings, and nothing is unconfirmed. Later runs can log
the profile this way.

### 2026-09-29 09:08 -07:00, phase 9 done: the review is done

The note is in the book (`ad15eaf`). Its stub is
`src/research/2026-09-28-frp-literature-review.md`, an include of the
note like this handoff's, and `src/SUMMARY.md` lists it under Research,
after this handoff, as "What the FRP literature says to Bough". The note
itself is unchanged.

The book builds with mdbook 0.5.4, the version the deploy workflow pins,
and `mdbook-linkcheck2` 0.13.0 finds no broken link. mdbook wasn't
installed in the container; the release binary was downloaded into the
session's scratchpad for the build, and nothing was installed on the
path. The build's warnings are the ones other notes already had, plus
one linkcheck warning in the note, a quotation's "avoid[s]" read as a
possible link. It isn't one.

The review is done. The must-read is the note's "## The must-read":
`research/2026-09-28-frp-literature-review.md`. What to grill first, it
says, is RFD 3 and RFD 5, since they gate the build. Nothing is open.
