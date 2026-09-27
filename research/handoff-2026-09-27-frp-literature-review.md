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
  `notes/2026-09-27-rfd-revision-landed.md`.
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
