# 2026-10-08 — What the expressibility port has to express

Status: note, not a decision. Picks up from
`2026-10-07-mema-expressibility-in-haskell.md` and replaces two things in it:
the claim that compiling in the pure fragment is the proof, and the plan to
port the Bough REPL as it stands.

## Compiling isn't the proof

The 10-07 note said that if the REPL compiles as pure Haskell over the real
primitives, that's the expressibility proof. It claims too much. Every
interactive program can be written as one hold over a pure interpreter, a Mealy
machine: keep `Int`s in the side table instead of cells, compute the arithmetic
in the step function, never call `execute`. That's pure, Safe, built only from
real primitives, and it passes every transcript. It proves nothing about
construct.

A second version is harder to spot. A REPL that builds a whole fresh graph on
every command calls `execute` honestly, carries values across with `sample`, and
also passes everything. So "it exercises `execute`" isn't the criterion either.

The 10-07 note already says why tests can't catch either one: behaviour can't
see structure. So structure has to be shown some other way. The proof is a
correspondence. Every node the program builds maps to the matching primitive,
and every place where it doesn't is named and argued. I can check that without
Haskell fluency, because it comes down to matching primitive names. The tests
confirm behaviour; the correspondence is the proof.

## Porting the REPL as it stands proves little

The Bough REPL only builds cells, over `Int`, `Bool` and `Str`, through
registry functions. That's trivial to express in Safe Haskell, so a faithful
port is a weak proof of the thing I actually want: that the Sodium semantics can
express arbitrary graph construction from pure data.

Making the Haskell do more than the REPL leaves no Rust to compare it against.
That's fine, because there were always two questions:

- Can the semantics express arbitrary construct from pure data? Haskell alone
  answers that.
- Does the Bough REPL lean on something outside the semantics? That one needs
  the Rust.

The first comes first. The correspondence changes sides: it no longer maps Rust
to Haskell, but the port's command language to the constructors of the
semantics. One `build` function, one case per constructor. That table is nearly
the identity and needs no Rust. The second question comes back later, the other
way round: the Haskell becomes the spec for the next Rust REPL, and the table
gets built then.

What keeps the Haskell honest:

- Definitions are pure data.
- `build` turns each data constructor into its matching primitive, one case
  each.
- The side table holds cells, never values.

## What purity actually enforces

I ran the experiment rather than trust the 10-07 argument. With GHC 9.4.7:

- `{-# LANGUAGE Safe #-}` refuses `unsafePerformIO` and `Debug.Trace`, so "no
  `IO` in the type" really means none.
- The vendored text is safe-inferred, but only under `-XHaskell2010`. GHC 9.4's
  default language turns on an extension Safe forbids. That's a compiler flag,
  not an edit to the file.
- A shim of about twenty lines in front of the text exports `Stream`, `Cell` and
  `Reactive` abstract, and each primitive as `mapS = MapS` and so on. A module
  behind it can't write a lookalike primitive: `MkStream` isn't in scope, so
  there's no occurrence list to fake.

Two audits remain. Safe doesn't stop a module importing
`Reactive.Sodium.Denotational` directly and calling `occs`, so the REPL module's
import list is one. The shim is the other. Every line of it is a renaming except
a three-line `MonadFix` instance for `Reactive`, the standard reader-monad fix,
which `mdo` needs to tie the knot at the root. That's the one thing not in the
text.

## The probe

A throwaway Int-only REPL of about a hundred lines, with input, def, redefinition,
set and watch. The side table is a `Cell (Map String Binding)`, held over
`execute (snapshot step lines env)`. Rebinding follows `graph.rs`'s `bind`
line for line: `hold first (execute …)`, then `switchC`.

It ran under the text's own lazy knot-tying, with no fixed-point iteration, and
reproduced the first transcript in `rebinding.rs` exactly: `c = 2, 1, 27, 30,
40`. F6 never came up, because every switch is created at the same instant as
the hold it switches over. So the port sits on the raw text, not on
`Oracle/Derived.hs`. That's less to trust than the oracle.

The text memoizes nothing, and it shows. 24 lines took 0.06s, 44 lines 0.7s, 84
lines 21s, and 164 lines didn't answer in a minute. The obvious fix, sharing or
memoizing, changes how the semantics is computed, which is exactly the kind of
change that bit me in the oracle. Standing rule: a transcript that's too slow
gets split. The semantics never gets sped up.

## Inputs and listeners don't reduce to bindings

The token conjecture split in two.

Cell tokens behave as conjectured. In Rust, a listener drops the token into a
`RefCell` slot, the REPL stores it, and a later `Command` carries it back in. In
Haskell, the side table cell holds it, a step samples it, and `execute` gets it.
A token is a binding.

Input tokens aren't. They're addresses of sources created at runtime, and the
semantics only has inputs that exist from the start. A runtime input becomes a
filter on the one root stream, keyed by something. A runtime listener is the
mirror image: a `switchS` over a growing merge into one root output. Runtime
inputs are a demux of the root input, and runtime listeners are a mux into the
root output.

The key can't be the user's name. Remove a binding and add one with the same
name, and the old switch picks up the new binding's routes. Rename breaks the
routing outright. So the key has to be identity as a runtime value: exactly
where the 10-07 note said the conjecture would break.

It doesn't break, because Mema already has that key. A `VertexId` is pure data
in the flat vertex table (ADR-007). ADR-009's `Map<VertexId, Map<InstanceId,
LiveNode>>` *is* the token side table, and the port shows it can be a cell.
Identity is a runtime value, but it lives in the AST, not in the runtime. A
token is a binding, and an address is a key in the data.

## The edit set is ADR-042's vocabulary

I thought the set of edits was too big to enumerate. It isn't. Completeness is
trivial and is the trap: one batch that removes everything and adds the new
program reaches any program from any other. That's the rebuild-the-world REPL
again. The hard part is what survives each edit. That's the question the 10-07
note parked, about which equivalence an edit preserves, and it's a column
beside the list, not the list.

ADR-042 already has a closed vocabulary. I'm treating it as a starting list,
not an authority. The port's root input stream is ADR-031's log, and its command
type is ADR-042's operations. The theorem gets a closed statement: every ADR-042
operation is expressible in the semantics.

Where I landed on each:

- **`add-vertex`, `remove-vertex`, `rename-port`.** All needed. `add-vertex`
  creates its default sources in the same instant (ADR-013). `rename-port`
  changes only the side table, never the graph.
- **Freeze is `demote-to-constant`, not remove.** Replacing a removed vertex
  with its current value is a different operation from ADR-013's remove, which
  points the consumers at fresh defaults. ADR-042's rule 3 says both exist. The
  freeze is a hold seeded with `sample`, not a `Constant`, because
  `set-constant` has to be able to change it later.
- **Same-type redefinition only.** Cell to stream, and stream to cell, aren't
  needed. Reset is `remove-vertex` + `add-vertex`; keeping state is
  `replace-vertex`, which already carries the hold value where the types agree.
  Both, and reset first.
- **No `retype-port` for now.** A type change can be done as a dance across
  several transactions. The cost is that listeners and downstream holds see
  every intermediate state, and those states go into the log. ADR-042 keeps
  `retype-port` as one operation for that reason. It's out of the proof for now,
  not out of Mema.
- **Loops are valid under Sodium's rules.** A loop with nothing to delay it is a
  rejected edit that does nothing. That's ADR-014's "every cycle contains a hold"
  check, run before anything reaches the graph. In Bough, a switch move that
  closes a cycle within one instant poisons the runtime, so the check is
  mandatory there too.
- **Edits at the edge**, inputs and listeners both. Needed.
- **Batches are needed, but not as a feature.** Single operations move several
  switches at once: `remove-vertex` with N consumers, `replace-vertex`,
  `promote-constant`, `add-vertex` with its defaults. ADR-013 wants one user
  action to be one commit. In the semantics that's one root event carrying a
  list of routes, at one instant, so it's cheap.
- **Construct closure edits: needed, and last.** The live-view draft rejects a
  row subgraph per item, so dynamic collections don't need them. ADR-009's
  instances do: an edit to a specification has to reach every live instance.
  A route keyed by `VertexId` reaches every instance's switch, and each instance
  builds its own nodes. But the route has to carry the definition with its
  `VertexId`s unresolved, because each instance resolves them against its own
  nodes. The REPL's `Def` carries resolved tokens.

## Switch per wire, not per binding

ADR-008 puts a switch on every input wire. The Rust REPL puts one on every
binding's output, and so did the probe. With a switch per binding, changing what
a consumer reads means rebuilding the consumer, and a stateful consumer loses
its state. `rewire` promises the consumer stays the same consumer, and only a
switch per wire gives that. The port follows ADR-008 and departs from the Rust
REPL on purpose.

That also takes the risk off loops. I'd expected a loop built from data to need
a knot tied inside a construct, which would lean on the `MonadFix` line.
ADR-014 says otherwise: every vertex is built with default sources, and a loop
closes later by moving a switch. The only knot left is the one at the root,
which the probe already ties.

## Order

By risk, one per increment:

1. `add-vertex` with defaults, and `wire`, `unwire` and `rewire`, over a switch
   per wire. The new base.
2. Loops through `rewire`, with the guardedness check.
3. `remove-vertex`, `demote-to-constant`, `promote-constant` and `set-constant`:
   the instants that move several switches.
4. `replace-vertex`, carrying the hold value.
5. `rename-port`.
6. Instances of one specification.
7. `retype-port`, `split-vertex` and `merge-vertices`, later or never for the
   proof.

## Open / parked

- Whether the semantics sanctions a loop inside `execute`. ADR-014 means
  user loops don't need one, but the root knot still uses `MonadFix`. A question
  for the literature review, not the code.
- A valid loop whose events depend on values, such as a filter inside the loop,
  doesn't terminate under the text. It's expressible, but it can't be tested
  without the oracle's fixed-point iteration, the part that held the one change
  the literature review didn't validate.
- Edit timing is asymmetric in the text. A cell switch moves at the edit's
  instant and shows the new definition's value then. A stream switch still
  takes the old stream's events at that instant. So a cell edit takes effect at
  its instant and a stream edit after it. Mema has to say which one an edit
  means.
- Where the port lives, maybe `bough-oracle/haskell/expressibility/`, and
  whether cargo builds it the way `tests/probes.rs` does.
- Instances wait on `drafts/compound-instances.md` settling what an
  `InstanceId` is inside a specification.
- Whether the Bough REPL leans on anything outside the semantics. Deferred until
  the Haskell is the spec.
- Words. Bough's glossary reserves "edge" for the I/O boundary, and Mema's ADRs
  use it for a wire; I say "wire" for Mema. "Shape" is a benchmark workload in
  Bough's glossary and a widget's port record in Mema's `CONCEPTS.md`; neither
  means a program's structure. And "driver" means the `Runtime`'s owner, not the
  oracle's code around the text.
