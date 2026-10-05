# What a rollback probe found in the transaction

_2026-10-05. Findings from the rollback probe the handoff of 2026-10-04
asked for: can the engine spike refuse a failing transaction and come
back to where it was, instead of poisoning the runtime? The probe
changes the spike on bough's
[`claude/admiring-pasteur-3n8ryp`](https://github.com/RadicalZephyr/bough/tree/claude/admiring-pasteur-3n8ryp)
branch, a new branch from `claude/probe-crate-implementation-m4utf9` at
`2b72e30`, built and tested with rustc 1.97.0. The note is written as
the probe runs, a section a step; the short answer comes last. The RFDs
are untouched._

RFD 5 chose this on purpose. "Transaction" there means atomicity of
visibility, not abortability, because rollback "needs an undo log for a
case that is a bug by definition". In Mema the users write the edits
and the functions, so a failure isn't a bug in the program; it's
something a live environment does all day. That's the premise this
probe reopens.

## The transaction, mapped

A unit is what one `send`, one `transaction` or one queued unit of a
pump runs: an instant, and the child instants a `split` or a `defer`
queues. Every instant runs the same phases, in `engine/tx.rs`:

```
begin      in_tx = true, the poison; tx += 1; the instant's buffers cleared
sends      each input's slot and stamps; a coalescing input's function
mark       the order of the affected region; watched switches queued
evaluate   the order, backwards; every program node's closures
new nodes  what this instant created, by pull; a construct among them runs
commit     holds take their pending value; accumulate_mut runs; memos
           settle; every queued switch moves; then the cycle check
dispatch   listeners, in evaluation order
children   each child instant, the same phases from mark on
finish     in_tx = false
```

After the unit, and outside it, come the tied cell listeners and a
collection if one is due.

### Listeners run after commit, and graph code runs after listeners

A listener only ever reads committed state: `instant` calls `commit`
and then `dispatch`. But graph code can still fail after some
listeners have run, so a failed transaction's side effects escape.
That happens in two places.

The first is laziness. A `map_cell` or a `lift` is a read-through cell:
its function runs when the cell is read, into a memo, and commit clears
the memo of every one that stepped. A cell listener reads the committed
value:

```rust
fn call_cell<M, A, F>(e: &mut Entry<M>, b: &mut Build<M>, n: u32)
where
    M: Mode,
    A: 'static,
    F: FnMut(&A) + 'static,
{
    let v = b.value::<A>(n);
    part::<M, F>(&mut e.f)(v)
}
```

So the first read of a stepped read-through cell after commit is
usually a listener's, and the cell's function runs there, between two
listeners. Every function in `bough-repl`'s registry is a `map_cell` or
a `lift`. A scratch experiment before the probe started, under 32
shuffle seeds each:

| What it sent | What happened |
|---|---|
| `c = a + 1` and `d = boom(a)`, both watched; 7 to `a` | `c = 8` printed before the panic in 21 of 32 seeds |
| Two redefinitions in one transaction, one of them to a definition that panics on the current value | The other binding's watcher printed in 19 of 32 seeds |
| A redefinition to that definition, with nothing watching it | The edit succeeds and installs it; the panic comes at the next `watch`, outside any transaction, and poisons nothing |

The second is the child instants. They run after their parent's
listeners, so a child that fails does so after its parent committed
and dispatched.

Rolling the graph back can't take back what a listener printed. So
before either rollback mechanism, the probe moves every listened cell's
computation ahead of commit; that step has a section of its own below.

Laziness also blurs the line between an edit and a data event. A bad
definition that nothing reads installs cleanly and fails later, in
whichever transaction first reads it, where it looks exactly like a
data event failing.

Graph code in dispatch also runs unguarded: `instant` disarms the
graph-code guard before `dispatch`, so a read-through function that
calls through a handle there is queued, not refused with
`FromGraphCode`.

### Where the poison is set

The poison is `Build::in_tx`. `begin` sets it, and only `finish` clears
it, after the last child, so a panic anywhere in between leaves it set.
`collect` sets it while `Drop` code runs. Under `std`,
`Runtime::mark_on_panic` wraps every entry that can poison in
`catch_unwind`, marks the poison in both handles and resumes the panic;
there is no drop guard, which is what the abort targets need. A panic outside a transaction
leaves the runtime usable: a `sample` from I/O code, `listen_cell`'s
call at registration, and a tied cell listener. That's where the third
row of the table failed, harmlessly.

### What each phase mutates

| Phase | What it mutates | User code there |
|---|---|---|
| begin | `in_tx`; `tx`; the instant's buffers (`starts`, `order`, `created`, `commits`, `memos`, `relinks`, `dispatch`) | none |
| sends | the input's slot and its `mark`, `pos` and `fired` stamps; `starts`; once-listeners tied to the unit, registered before evaluation | a coalescing input's function |
| mark | `mark` and `pos` stamps; the `ON_STACK` flag, set and cleared; `order`; a watched cell's switches into `relinks` | none |
| evaluate | each program node's parts, taken out of the store while it runs; stream slots; a linear consumer takes its dependency's event; holds' and accumulators' `pending`; `accumulate_mut`'s pending event; `scan`'s state, replaced; `fired` stamps and the `commits`, `memos` and `dispatch` lists; memos filled on read; `post_value` beside a memo, from `prepare`; a new switch's first link, with a linear claim; pull's order entries and stamps; a split's own stack and the child levels | every chain's closures, `accumulate`, `scan`, `construct` closures, read-through functions on read |
| a construct closure | nodes allocated (a slot off the free list or a new one); each new node linked into its dependencies' dependents lists at once; `created`; reach, watchers and `WATCHED`; `anchors`; scopes and open loops; a loop's close | the closure, and whatever it builds that runs at this instant |
| new nodes | as evaluate, by pull | as evaluate |
| commit | each hold's value replaced by its pending one, the old value dropped; `accumulate_mut`'s state; memos promoted or cleared; every queued switch moved (`move_inner`: the old inner's dependents, the new inner's dependents, the switch's dependencies, linear claims); then `check_moved`'s cycle check and linear claim | the `Drop` of replaced values; `accumulate_mut`'s function; a read-through outer's function, read by `move_inner` |
| dispatch | each node's listener list, taken out of the store while it runs; once-listeners spent; dead entries pruned | listeners, and read-through functions on read |
| children | `tx` again for each child; a capture's stack, pushed and popped; the child levels | a split's iterator, and everything above |
| after the unit | tied listeners released; a collection frees nodes | tied cell listeners, `Drop` |

### What a panic leaves half-done

Read from the table, a panic part way through leaves:

- **No program for the node that was running.** `eval_node` takes a
  node's parts out of the store, so its closures can have the whole
  build context, and puts them back after. A panic drops them in the
  unwind, and so for every node whose evaluation was on the stack. The
  node runs no more: a construct that lost its program can never
  rebuild again. Dispatch does the same to a node's listener list, and
  a split's capture to its parts while its iterator runs.
- **Scopes and open loops** a construct closure pushed, which the next
  scope would sit on top of.
- **Child levels and capture stacks**, which the next unit's children
  would run.
- **Pending values.** Collection traces a hold's pending value, so a
  pending definition keeps the nodes it names alive.
- **A post-instant value beside a memo.** Commit promotes it into the
  memo the next time the cell steps, whether or not that instant
  computed a new one. That would be a wrong value an hour later, which
  is RFD 5's argument for poisoning, made concrete.
- **Live orphans.** A construct links each node it makes into its
  dependencies' dependents lists as it makes it, so the next instant's
  marking reaches them, and a construct among them runs its closure on
  later events, until a collection frees them. A rollback has to unlink
  them at once, even if freeing them waits.
- **Once commit has started:** holds overwritten and their old values
  dropped; memos settled; switches moved. A cycle at a switch's move is
  found after all of it. `accumulate_mut` is worse: its function
  mutates the state in place, and with no `Clone` nothing can undo it.
  `bough-repl` never uses it, so no case here exercises it.

What undoes itself is every per-instant stamp: `mark`, `fired`, `pos`,
the pull and prepare stamps, `relink`, a slot's freshness. Each is
compared with `tx`, so a failed instant's stamps are stale as soon as
the next instant begins, provided `tx` is never rolled back with
everything else.

No `RefCell` is held across user code in the engine. Memos are
`OnceCell`s, which stay empty when their initializer panics, and the
edge's locks, the inbox's and each slot's, are never held while a
transaction runs. With no
`unsafe` in the engine, memory is safe after any panic; what isn't
guaranteed is consistency, and the list above is where it breaks.

## Today, every case poisons

Step 2's tests, in `bough-repl/tests/rollback.rs`, drive each case
against the unchanged engine. F3 and F4 go through the REPL itself,
since its checks can't refuse what fails only on a value: `def b boom
a` has the right types and no cycle. F1 and F2 go past the checks,
through the graph API, as `tests/unchecked.rs` already did. F5 is a
graph of its own, because the REPL never builds a construct that runs at
the instant it was built: an outer construct's closure builds an inner
construct over the same stream, which runs at that instant once the
outer closure has returned, and panics on 7. `boom` joins the registry
for the probe: its argument, except that it panics on a multiple of 7
other than 0, so that a tick, which starts at 0, can be watched through
it.

| Case | Where it fails | Test |
|---|---|---|
| F1 | Commit, at the switch's move, after the holds have committed | `f1_a_cycle_closed_by_a_redefinition_is_found_at_the_switch_move_and_poisons` |
| F1, watched | The same: commit comes before the listeners | `f1_watched_the_cycle_is_still_found_at_the_switch_move` |
| F2 | Evaluation, in the binding's construct closure | `f2_a_binding_s_construct_closure_that_panics_poisons` |
| F2, at the root | Evaluation, in the root construct, so no later command reaches the graph | `f2_the_root_construct_panicking_poisons_every_later_command` |
| F3 | Dispatch, at the first watcher's read | `f3_a_definition_that_panics_on_the_current_value_poisons_through_the_repl` |
| F3, beside another redefinition | Dispatch, after the other binding's watcher printed, in 19 of 32 seeds | `f3_the_panic_comes_in_dispatch_after_another_watcher_printed_in_some_orders` |
| F3, unwatched | Nowhere in the edit: at the next `watch`, outside any transaction | `f3_unwatched_the_definition_installs_and_fails_at_the_next_watch` |
| F4 | Dispatch, at the seventh tick | `f4_a_tick_boom_panics_on_poisons_the_runtime` |
| F4, with a watched sibling | Dispatch, after the sibling printed for the failing tick, in 16 of 32 seeds | `f4_a_sibling_watcher_prints_for_the_failing_tick_in_some_orders` |
| F5 | The new-node phase, in the inner closure | `f5_a_construct_built_in_another_s_run_that_panics_at_the_same_instant_poisons` |

Every case but the unwatched F3 poisons the runtime: the next send is
`Err(Poisoned)`, and the REPL's next command panics. The unwatched F3
is the odd one out, and the worse one for Mema: the runtime survives,
but a definition that fails is installed, and nothing has said so.

## Computing before commit

`force` is a cargo feature on bough, which bough-repl forwards. Under
it, `instant` runs one more phase between the new nodes and commit,
which computes every value a cell listener will read in dispatch:

```rust
fn force(&mut self) {
    let mut k = 0;
    while k < self.s.dispatch.len() {
        let n = self.s.dispatch[k];
        k += 1;
        let h = &self.store.hot[n as usize];
        let lazy = matches!(h.kind, Kind::ReadThrough | Kind::Loop | Kind::SwitchCell)
            && h.flags & super::AFTER_COMMIT == 0;
        if lazy
            && self.store.listeners[n as usize]
                .iter()
                .any(|e| e.flag.is_live())
        {
            self.prepare(n);
            self.fill_post(n);
        }
    }
}
```

A cell that stepped has its value after the instant computed by
`prepare`, the path a steps view already takes, and commit promotes it
into the memo. `fill_post` fills the memos that the read would pass
through cells that didn't step, such as a definition built at this
instant that a switch has just moved to. A cell whose listeners are all
dead is skipped, since dispatch wouldn't read it.

What it changed:

- **F3 and F4 fail before any listener runs**, under all 32 seeds:
  `f3_with_force_the_panic_comes_before_any_watcher_prints` and
  `f4_with_force_no_watcher_prints_for_the_failing_tick`. They still
  poison. Force moves the failure ahead of commit; it doesn't recover
  from it.
- **Dispatch runs no graph code.** `bough/tests/dispatch.rs` checks that
  directly: every function asserts that no listener has run yet in its
  instant. The shapes are a lift, a `map_cell`, a switch moved to a cell
  built at the instant, a switch whose outer is a read-through cell, and
  a cell loop. Without force, every one of 16 orders runs a function in
  dispatch; with it, none does, and every order gives the same values.
  Graph code also stops running unguarded, since force runs before the
  guard is disarmed.
- **The semantics hold.** The whole suite, 660 tests, passes with force
  on, the tests that count function calls among them, so each function
  runs as often as before. The one change in how often comes from a
  listener that drops another listener's guard during dispatch: the
  dropped listener's cell used to go unread, and its function now ran
  before commit. No test noticed.
- **A watched F1 is found earlier.** Computing the watched value reads
  around the cycle before any switch has moved, and `prepare`'s
  re-entry check panics with "a same-instant cycle through a read after
  the instant":
  `f1_watched_with_force_the_cycle_is_found_before_commit`. Unwatched,
  F1 is still found at the move, after the holds have committed.

It can't compute a `State`. A `State`'s value after the instant exists
only once commit has run the in-place accumulator under it, which is
why a `State` has no stream view, and the first run of the suite under
force failed exactly there, in `alloc.rs`, with a listened `map_cell`
over an `accumulate_mut`. So the node behind every `State` token is
marked where the token is made, from `accumulate_mut`, `State::map_cell`,
a lift with a `State` among its inputs, a switch over `State`s and a
state loop, and force leaves it lazy. A function over a `State` still
fails in dispatch, after a sibling has printed, in 16 of 32 seeds:
`with_force_a_function_over_a_state_still_fails_in_dispatch`. That's
the second way `accumulate_mut` defeats rollback, after its own
function mutating the state at commit.

Force makes laziness partial. A cell with a live listener is computed
eagerly, at the instant it steps; a cell nobody reads stays lazy, which
is why an unwatched F3 still installs a definition that fails. Step 6
measures what force costs.
