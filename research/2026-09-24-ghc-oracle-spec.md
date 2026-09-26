# The GHC oracle: specification for the spike

This is the brief for the `bough-oracle` harness. It is the only oracle the
spike uses: the vendored `Denotational.hs`, run by GHC, never edited.

## Shape

```
bough-oracle/
  haskell/Reactive/Sodium/Denotational.hs   vendored, unchanged (already committed)
  haskell/sodium.hs, LICENSE, README.md     vendored, unchanged (already committed)
  haskell/Oracle.hs                         Main: read programs from stdin, answer on stdout
  haskell/Oracle/Program.hs                 the program description (derives Read, Show)
  haskell/Oracle/Derived.hs                 derived operations over Denotational's constructors
  haskell/Oracle/Interpret.hs               program -> Denotational terms, loops by fixed point
  haskell/OracleTests.hs                    HUnit: vectors and derived operations through the interpreter
  src/lib.rs                                re-exports
  src/program.rs                            the same description in Rust, printed as Haskell `Read` syntax
  src/ghc.rs                                builds the GHC binary once, runs a pool of processes
  src/answer.rs                             parses answers
  tests/oracle.rs                           one integration-test binary for everything that needs GHC
```

Later stages add `src/build.rs` (the program built with the Bough API),
`src/generate.rs` (proptest strategies) and `src/compare.rs`.

## The protocol

The Rust side writes one program per line to the process's stdin, in the
syntax of Haskell's derived `Read` for `Oracle.Program.Program`. The Haskell
side answers one line per program:

- `OK <answer>`, where `<answer>` is a JSON array of integers and arrays, one
  element per observed node, in the order `observe` lists them:
  - a stream: `[0, [[t, v], ...]]`, every event with time `t >= [1]`;
  - a cell: `[1, v0, [[t, v], ...]]`, where `v0` is `at (steps c) [1]`, the
    value after transaction zero and its children, and the steps are every
    step with time `t >= [1]`.
  A time `t` is an array of integers. A value `v` is an integer, a boolean as
  `0` or `1`, or a list as an array of integers.
- `ERR <message>` when evaluation throws, for example a loop that does not
  converge.
- `TIMEOUT` when one program takes longer than five seconds. Compile with
  `-threaded` so `System.Timeout` interrupts pure code reliably.

The process stays up across programs. The Rust side keeps a pool of processes
behind a mutex so parallel test threads do not share one.

Building: the Rust side runs `ghc -O1 -threaded -i<haskell dir> -outputdir
<dir> -o <dir>/bough-oracle Oracle.hs` once per test binary, under a lock
file, into a directory under `CARGO_TARGET_TMPDIR` (or `target/`). GHC's own
recompilation check makes a second build fast.

Without GHC: every test that needs it panics with an install hint (`apt-get
install ghc libghc-hunit-dev`, or ghcup) unless `BOUGH_ORACLE=skip` is set, in
which case it prints that it skipped and returns. No `#[ignore]`.

## The program description

Values are integers, booleans and lists of integers, plus stream and cell
tokens as values for the higher-order operations. Closures cannot cross a
process boundary, so every function is an expression `E` both sides evaluate
identically: 64-bit wrapping arithmetic (`Int` in GHC wraps; Rust uses
`wrapping_*`), `Mod` with a positive divisor only (Haskell `mod`, Rust
`rem_euclid`), booleans as `0` and `1`, and anything nonzero is true.

```haskell
data V = I Int | B Bool | L [Int]

data E
  = Arg | Arg2 | ArgN Int           -- the function's arguments (see each Def)
  | CArg                            -- inside a construct body: the construct's event
  | Sample Ref                      -- inside a construct body: sample a cell at the body's instant
  | Lit Int
  | Add E E | Sub E E | Mul E E | Mod E Int
  | Max E E | Min E E | Eq E E | Lt E E | Not E | If E E E

data Ty = TInt | TBool | TList | TStreamOf Ty | TCellOf Ty

data Ref = N Int                    -- node i of the enclosing program (top level)
         | Local Int                -- node j of the enclosing construct body

data Program = Program [Input] [Def] [Int] [[(Int, V)]]
--                     inputs  nodes observe schedule
-- Node i is the i-th Def. The schedule has one entry per external
-- transaction k = 1, 2, ..., each a list of sends (input index, value) in
-- send order. Transaction k is at time [k]; the build is time [0].

data Input = Input Ty (Maybe E)     -- the coalescing function: Arg first send, Arg2 second
```

`Def` covers every operation the engine exposes. Adapters are separate
`Def`s; the Rust side fuses a linear run of them into the materializer that
consumes it.

```haskell
data Def
  -- sources
  = SInput Int                      -- the stream of input i
  | CInput Int E                    -- input_cell: a hold over input i, initial E
  | SNever Ty
  | CConstant E
  | SLit Ty [([Int], V)]            -- MkStream; oracle-only, the engine cannot build it
  -- adapters (Int events unless stated)
  | SMap E Ref                      -- Arg: event
  | SFilter E Ref                   -- keep when E /= 0
  | SFilterMap E E Ref              -- keep when the first /= 0, emit the second
  | SMapTo V Ref
  | SSnapshot E Ref Ref             -- stream, Int cell; Arg: event, Arg2: cell value before the instant
  | SGate Ref Ref                   -- stream, Bool cell
  | SOnce Ref
  | SMapList E E Ref                -- Int -> list: length (first `mod` 4), element i is the second with Arg2 = i
  | SPickStream E [Ref] Ref         -- Int -> one of the listed shared Int streams, index E `mod` n
  | SPickCell E [Ref] Ref           -- Int -> one of the listed Int cells
  -- stream materializers
  | SNode Ref | SShare Ref          -- identities in the semantics; linearity and fusion in Rust
  | SMerge E Ref Ref                -- Arg: left event, Arg2: right event
  | SOrElse Ref Ref
  | SSplit Ref                      -- stream of lists
  | SDefer Ref
  | SScan E E E Ref                 -- initial state; output E and new-state E, Arg: event, Arg2: state
  | SSteps Ref | SStepsWithCurrent Ref
  | SSwitch Ref                     -- cell of streams
  | SConstruct Body Ref
  -- cells
  | CHold E Ref
  | CHoldStream Ref Ref             -- initial stream, stream of streams
  | CHoldCell Ref Ref               -- initial cell, stream of cells
  | CConstantStream Ref | CConstantCell Ref
  | CAccum E E Ref                  -- initial; new state E with Arg: event, Arg2: state
  | CAccumMut E E Ref               -- the same denotation; Rust uses accumulate_mut
  | CMapCell E Ref                  -- Int -> Int
  | CToBool Ref                     -- Int -> Bool, nonzero
  | CMapPickCell E [Ref] Ref        -- Int cell -> cell of cells
  | CLift E [Ref]                   -- two to six Int cells, ArgN i is cell i
  | CSwitch Ref                     -- cell of cells
  -- loops
  | CLoop Ty                        -- a forward cell
  | SLoop Ty                        -- a forward stream
  | Close Int Ref                   -- closes loop node i with a definition; defines no usable node

data Body = Body [Def] Result       -- local nodes; Refs inside may be N (outer) or Local
data Result = RValue E | RNode Ref  -- emit an Int, or emit a token (stream or cell)
```

Creation time: top-level nodes are created at `[0]`. Nodes inside a construct
body are created at the instant the construct's event occurs, which is the
`t` its `Reactive` runs at, and `Hold`, `Value` and `SwitchC` take it as `t0`.

## Denotation of each Def

The table in `research-derived-ops/derived-ops.md` (and its verification)
fixes the derived ones. The direct ones: `SInput` is `MkStream` over the
schedule, one event per transaction that sends to it, folded with the
coalescing function in send order when there are several; `CInput` is `Hold`
over it at `[0]`; `SMap` is `MapS`; `SFilter` is `Filter`; `SSnapshot` is
`Snapshot`; `SMerge` is `Merge l r f` (left event first); `SOrElse` is
`Merge l r const`; `SSplit` is `Split`; `SSteps` is `Updates`;
`SStepsWithCurrent` is `Value c t0`; `SSwitch` is `SwitchS`; `CSwitch` is
`SwitchC c t0`; `SConstruct` is `Execute (MapS (\a -> Reactive (runBody a)) s)`;
`CHold` is `Hold`; `CMapCell` is `MapC`; `CLift` is `Apply` over `MapC`.

## Loops

Loops are computed by explicit fixed-point iteration, never by lazy
knot-tying, because the text as written does not terminate on a loop whose
spine depends on values (`Filter` inside a loop through a `Hold`).

- Interpret the program with every loop node bound to a concrete term: a
  cell loop to `Hold v0 (MkStream sts) []`, a stream loop to `MkStream occs`.
- Start from a cell that never steps (initial value the type's zero) and a
  stream that never fires.
- Each round, re-interpret the whole program and take the steps or events of
  each loop's definition as its next iterate. Stop when every loop's iterate
  equals the previous one; after 200 rounds, answer `ERR`.
- Loop types are first-order only. A loop inside a construct body is out of
  scope for the spike's random programs.

This is the same denotation: every legal loop passes through a hold, an
accumulator, a `split` or a `defer`, so each round fixes at least one more
instant, and the fixed point of a well-founded definition is unique. Where
lazy knot-tying terminates, the two agree; a test checks that on programs
without value-dependent spines.

Well-founded loops only. The fixed point from a never-stepping start is the
semantics only when the loop's back edge is a read before the instant
(`snapshot`, `gate`, `sample`, the selection of `switch_stream`) or a child
instant (`split`, `defer`). A back edge through a steps view (`steps`,
`steps_with_current`, `switch_cell`'s post-instant read) is a same-instant
dependency cycle even when the path passes through a hold, because a hold does
not delay its steps view: `c = hold 0 (merge ticks (map (+1) (steps c)) const)`
diverges in the lazy text, while iteration happily finds a fixed point. The
generator never produces such loops for the oracle comparison; the engine
must reject them at construction, and a separate test checks that it does.
(RFD 2's rule, "every path back to the forward token passes through a hold,
an accumulator, a split or a defer", accepts this program. That is a finding.)

Operations whose own definition is a knot (the accumulators, `scan`, `once`
if defined with a loop) use lazy knot-tying where the spine is
value-independent and the fixed point where it is not.

## Tests in the first oracle commit

1. The twenty vectors of `sodium.hs` restated as `SLit` programs through the
   interpreter, compared with the vectors, with GHC as a subprocess from Rust.
2. The derived operations' tests from the research, through the interpreter.
3. The capped counter (filter inside a loop through a hold) answers the
   expected steps; the uncapped counter by fixed point equals the lazy knot.
4. Protocol: `ERR` on a non-converging loop, `TIMEOUT` on a program that
   never finishes, many programs through one process, a pool under parallel
   test threads.
5. `BOUGH_ORACLE=skip` skips; without it and without GHC, a clear panic.

## Amendments after the research round (these override the text above)

1. **Observation window.** `Program` gains a first field, `Window`:
   `data Window = FromFirstTransaction | Everything`. `FromFirstTransaction`
   is what the engine comparison uses (cells: `at (steps c) [1]` and steps
   with `t >= [1]`; streams: events with `t >= [1]`). `Everything` answers
   `steps c` and `occs s` whole, for the cross-check vectors, whose events
   sit at `[0]`.
2. **Derived definitions** come from
   `scratchpad/research-derived-ops/Derived.hs` as corrected by
   `scratchpad/research-derived-ops-verify/verification.md`. Port them into
   `Oracle/Derived.hs`; keep their tests (DerivedTests.hs, VerifyTests.hs) as
   Haskell unit tests of the oracle. In particular `once` and `scan` take the
   creation time t0, and the tests must exercise them away from `[0]`.
3. **Two patches to defects in the text, in the derived layer only; the
   vendored file stays untouched:**
   - F6, `switchCell c t0 = SwitchC (concrete (chopFront (steps c) t0)) t0`
     with `concrete (a, sts) = Hold a (MkStream sts) []`. The text's `SwitchC`
     starts from the outer's initial value and gives steps out of time order
     when the outer stepped before t0 (research verification point 1; Java
     `Cell.java` switchC starts from the chopped outer too).
   - F7, `split s = MkStream (sortOn fst (occs (Split s)))`, a stable sort by
     time. The text's `concatMap` leaves children out of order when a split
     is fed by its own children, and a merge downstream then sees two events
     at one instant (`scratchpad/review-fidelity/hs/SplitSort.hs`).
   Each patch has a Haskell test showing the text's answer and the patched
   answer on the case, and a test showing they agree on the twenty vectors.
4. **Resource limits.** Link with `-with-rtsopts=-M1g` and answer `ERR heap`
   on heap overflow; a lazy knot can eat a gigabyte in seconds. If the
   process dies anyway, the Rust side reports the program and respawns.
5. **Stream loops** iterate over events the same way cell loops iterate over
   steps (the lazy knot through `defer` runs out of memory).
6. **Negative numbers** in the Haskell `Read` syntax need parentheses:
   `I (-5)`, `Lit (-5)`. The Rust printer emits them that way, and a test
   round-trips extreme values (`i64::MIN`, `i64::MAX`).

---

## Addendum, 2026-09-24, after the oracle was built

_Added after the spike. The specification above is kept as the harness's
agents followed it; the harness itself is `bough-oracle` in the `bough`
repository, and its README is the current description. Departures and
review findings, with their numbers in the spike's note,
`2026-09-24-engine-feasibility-spike.md`:_

- **Loops.** A fixed cap of 200 rounds refused well-founded loops that chain
  through more instants, and a construct body's loops solved inside every round
  of the enclosing scope could fail on the outer loops' zero start. Every loop,
  at the top level and in each body run, now iterates in the same rounds, and
  the rounds allowed are 200 plus two per distinct loop time any round's state
  has held; a well-founded loop needs at most that plus one (O1). The first
  iteration kept unforced thunks across rounds and reached 583 MB on a long
  counter; each state is now forced whole (O2).
- **A loop through `defer` with no filter** answers `TIMEOUT`, since it never
  converges (F22).
- **Build.** `-rtsopts` so a test can lower the heap limit; each binary its
  own `-outputdir`, since every program is module `Main`; `GHCRTS` removed from
  the processes' environment; a watchdog kills a process that stops answering.
- **Negative numbers.** GHC 9.4.7's derived `Read` accepts bare negative
  numbers in argument position, against the Haskell Report (O3). The printer
  keeps the parentheses.
- **Protocol.** The answers carry no node types, so the Rust builder repeats
  the checker for the subset it builds.
- **Known and not fixed** (O4 to O6): the interpreter builds a construct body's
  runs for events before the construct's creation, which the text defines and
  nothing can observe (F44), and a loop in such a run can make a hand-written
  program answer `TIMEOUT`; the Haskell unit tests run without a time limit; a
  GHC build orphaned by killing the test binary with SIGKILL leaks the process.
