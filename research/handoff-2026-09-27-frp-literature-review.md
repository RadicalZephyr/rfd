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
