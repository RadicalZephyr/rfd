# Your slice: re-run the probes (no wall-clock)

Read `verify/brief.md` first. Its rules hold, except that you are the one
verifier who may run `cargo bench`, `cargo run`, `cargo test` and valgrind.
Your scratch directory is `<scratch>/verify/probes/`.

## The job

Re-run every result file in `<experiments>/results/`
that doesn't need wall-clock timing, and say whether it reproduces.

- **Skip for now** the files whose names contain `-wallclock-`, `-timed-` or
  `-compile-time-`. They need an idle machine and run later.
- **Each result file names its commit** in its provenance line(s)
  (`… at experiments@COMMIT …`) and the command under it. Some files hold
  more than one run; take each one. **A count reproduces only at the commit
  its file cites**, since later commits changed shared code. So build each
  file's code at that commit, never at `HEAD`.
- **How to get a commit's code without touching `experiments`:** clone it once
  into your scratch directory (`git clone <experiments>
  verify/probes/experiments`), then export each commit you need with
  `git archive <commit> | tar -x -C verify/probes/src/<commit>`. Don't
  `git checkout` and don't use `git -C`. Use one shared
  `CARGO_TARGET_DIR=verify/probes/target` and go commit by commit, so
  dependencies build once. Each commit's `rust-toolchain.toml` pins rustc.
- **Run the command exactly as the file gives it,** from that commit's tree,
  and save the full output as `verify/probes/runs/<result-file-name>`.

## What reproduces

- **Instruction counts** (gungraun's `Instructions:` lines): each benchmark
  within 1% of the file. Compare every benchmark, not a sample.
- **Other output of a binary or test:** counts, tables, verdicts and pass/fail
  that are deterministic must match exactly. Output that depends on thread
  scheduling (lock hand-offs, futex wakes and the like) can't match exactly:
  say which lines those are, and whether the rerun tells the same story
  (same order of magnitude, same ranking of variants). Timings printed by a
  non-wall-clock run are indicative and aren't compared.
- **A mismatch gets exactly one more re-run,** from a clean build of that
  commit. If it still doesn't reproduce, record it and go on.
- One known flaky assertion, per experiments' own history:
  `rfd_0006_lock_vs_queue_cost::tests::footprints_agree` depends on
  scheduling. If it fails, run it once alone before calling it a failure.
- Also run the test
  `rfd_0004_patch_cell_crossover::tests::same_key_conflict` at
  `experiments@daa6419`, which the note cites with no result file, and say
  whether it passes.

The machine must stay usable for a claims verifier running beside you; that's
fine, since instruction counts don't depend on load. Don't change host power
settings.

## What you return

In place of the brief's report format:

1. A table, one row per result file (and per run where a file has several):
   file, commit, command, what was compared (e.g. "41 benchmarks"), largest
   deviation, verdict (`reproduces`, `reproduces-after-rerun`,
   `does-not-reproduce`, `scheduling-dependent: same story` or
   `…: different story`, `could-not-build`).
2. For every row that isn't `reproduces`: the benchmarks or lines that
   differ, original against rerun, both runs.
3. The files you skipped as wall-clock, listed.
4. The toolchain and valgrind versions you ran with, and anything odd.

Put it in `verify/probes/report.md` too.
