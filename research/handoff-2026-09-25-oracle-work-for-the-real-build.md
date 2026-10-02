# Oracle work for the real build: the handoff

_2026-09-25. For a fresh agent, from the session that ran the engine
feasibility spike. The spike is finished; this is the oracle work that
comes next. What the spike found is in
[its note](./2026-09-24-engine-feasibility-spike.md), and the oracle's
design is in [its specification](./2026-09-24-ghc-oracle-spec.md). This
handoff does not repeat them._

## The goal

Three pieces of work, in `bough-oracle` and bough's CI:

1. Patch the oracle's `split` to take a creation time (finding F89).
2. Run GHC in CI with a fixed seed, and add a scheduled job with fresh
   seeds.
3. Try the same creation-time cut on `construct`, as an experiment
   (finding O4).

## Settled; do not reopen

- **GHC is the oracle.** Bough's oracle is the vendored `Denotational.hs`
  under GHC, and `bough-oracle` is kept. Porting the semantics to Rust is
  shelved entirely. RFD 1 still says the oracle is a Rust port and that
  GHC does not run in CI; that text changes in the RFD revision, not in
  this work.
- **The fidelity policy.** The semantics text is the authority, except
  where it breaks its own rules: time order, and things existing from
  their creation. There Bough follows the rule, names the difference, and
  a test pins the text's answer beside Bough's. Patches live in
  `bough-oracle/haskell/Oracle/Derived.hs`, and the vendored file stays
  untouched, as the patches for F6 and F7 do.
- **Question 8: patch `split`.** It is one case of the policy. `defer` is
  a split of one element, so it follows.
- **Question 9: seeds.** CI runs a fixed seed. A scheduled job runs fresh
  seeds and reports each failure with its seed.
- **The `construct` cut is an experiment, not a decision.** Try it,
  measure it, and let Zefira decide.

## Where things are

- **bough.** `spike/engine-feasibility` at `4dc2ff4`, in draft PR
  RadicalZephyr/bough#4 into `claude/workspace-skeleton`. The spike's
  engine is throwaway; its oracle is not. How to run the oracle is in
  `bough-oracle/haskell/README.md`.
- **rfd.** `spike/engine-feasibility` at `90021d7`, in PR
  RadicalZephyr/rfd#2, stacked on RadicalZephyr/rfd#1.
- **F89.** The reproduction in the text's own constructors, and a fix
  checked against the twenty vectors, are the third section of
  [the issue drafts](./2026-09-25-sodium-issue-drafts.md).

## Ask Zefira first: where the work lands

Two facts make this a real question.

- **CI only runs from `main`.** bough's CI runs on pushes to `main` and
  on pull requests into `main`, and GitHub runs a `schedule` workflow only
  from the default branch, which is `main`. `main` is 8 commits behind
  `claude/workspace-skeleton`, and the spike is 84 ahead of that.
- **The oracle's tests need the spike's engine.** The builder in
  `bough-oracle/src/build.rs` writes every program with the spike's
  engine API, so the oracle's engine tests need that engine until the
  real one exists.

Recommendation: a new branch off `spike/engine-feasibility`, with commits
that touch only `bough-oracle/` and `.github/`, so they carry to the real
build intact. Check the CI steps locally; the scheduled job starts
running once it reaches `main`.

## The work

### 1. The `split` patch (F89)

- **Where.** `split` in `Oracle/Derived.hs` is a plain function. It
  needs the creation time, so it moves into `Reactive`, as `switchCell`
  did for F6. `switchCell`'s patch is the pattern: cut the input at
  `t0`, keeping events with `t >= t0`. `defer` is `split` of a
  one-element list. The interpreter's callers in `Oracle/Interpret.hs`
  pass the build time.
- **Keep the text beside it.** `splitText` stays, as `switchCellText`
  does.
- **Haskell tests.** Add cases to the `patches` group of
  `OracleTests.hs`. `bough-oracle/tests/oracle.rs` asserts every group's
  count in `HASKELL_GROUPS`, 181 cases in all, so update the table.
- **The fixed test.** `a_split_built_at_a_child_instant_splits_nothing_from_before_it_unlike_the_text`
  in `bough-oracle/tests/engine.rs` pins both answers today. Make it pin
  the patched answer against the text's, as the tests for F6 and F7 do.
- **The generator.** Lift its restriction: a body whose construct may
  run at a child instant builds no split or defer. It is in
  `bough-oracle/src/generate.rs`, in the module doc and at the field that
  tracks what may fire in a child instant. The random programs then cover
  splits and defers in bodies at child instants.
- **The probes.** They import the vendored text directly, not
  `Oracle.Derived`, so their outputs do not change. `tests/probes.rs`
  must still pass.

### 2. GHC and fixed seeds in CI

- **The test job.** In `.github/workflows/ci.yml` the test job sets
  `BOUGH_ORACLE: skip`, in a debug and a release matrix. Install GHC and
  HUnit (`apt-get install ghc libghc-hunit-dev`, the install hint in
  `bough-oracle/src/ghc.rs`), drop the skip, and fix the seed with
  `PROPTEST_RNG_SEED`.
- **The scheduled job.** Add a workflow on a schedule that runs fresh
  seeds with more programs (`PROPTEST_CASES`). A failing random test
  already prints its `PROPTEST_RNG_SEED`; the job must surface it.
- **Time.** The full suite runs in about 26 s once built. The first run
  also compiles the oracle with GHC; measure that.

### 3. The `construct` experiment (O4)

- **The problem.** The text's `Execute` has no creation time either, so
  a construct built inside a body runs its body for events from before
  it existed. Nothing observes those runs (F44), but a loop inside one can
  fail to settle (O4). So `well_founded` in `bough-oracle/src/generate.rs`
  refuses a loop in any body.
- **Try.** Give `construct` in `Oracle/Derived.hs` the same cut, only
  source events from its creation on. Then let the generator put loops in
  bodies.
- **Measure.** Do random programs with loops in bodies agree with the
  engine? That would also cover the engine's pull of new nodes out of
  creation order inside a body, which only a loop closed at build
  exercised in the spike.
- **Report** the result. Keeping the cut is Zefira's decision.

## Gotchas

- **Count floors.** Some random tests assert how many programs had
  something to test, and use fresh seeds. A generator change once moved
  one of those counts to its floor; the spike's commit "Generate
  constructs, RFD 4's screens and RFD 2's navigation loop" tells it. After
  changing the generator, sample
  `same_instant_cycles_through_a_switch_are_refused_or_poison_the_graph`
  and `same_instant_cycles_are_refused_at_close` over twenty seeds, and
  keep each floor well below what they give.
- **Skip mode.** `BOUGH_ORACLE=skip` must keep passing: without GHC, the
  oracle's tests return early.
- **Disk.** The cloud container's disk allowance is tight. Delete target
  directories you no longer need.
- **Per-commit checks.** The spike ran these on every commit:

  ```sh
  cargo fmt --all --check
  RUSTFLAGS="-D warnings" cargo clippy --workspace --all-targets --all-features
  cargo test --workspace --all-features
  BOUGH_ORACLE=skip cargo test -p bough-oracle --all-features
  cargo check -p bough --target thumbv6m-none-eabi --no-default-features
  cargo +1.85 check --workspace --all-features
  ```

  At the last commit of a batch it also ran the release tests and the
  other targets CI checks, and a long run:
  `PROPTEST_CASES=16384 PROPTEST_RNG_SEED=20260924 cargo test -p bough-oracle --release --test engine`.
- **Toolchains.** rustc 1.94.1, with 1.85.1 as the minimum, and GHC
  9.4.7 with HUnit 1.6.2.0.

## Working with Zefira

- **Her profile preferences apply.** Conversation comes first. Agree on
  the interface and the tests before non-trivial code. Keep increments
  small. Documents and commit messages are in her voice: short
  sentences, plain words.
- **Every commit builds and passes on its own.**
- **ADHD mode.** She turned it on in this session: lead with the next
  action, number the steps, and end with one next action.

## Suggested skills

- `anthropic-skills:i-have-adhd`: call it first, since she turned it on
  in this session.
- `code-review`: run it on each increment before pushing.
- `session-start-hook`: only if the new environment lacks GHC. A
  SessionStart hook can install `ghc` and `libghc-hunit-dev`, so the
  oracle's tests run in web sessions.
