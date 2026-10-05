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

## Mechanism A: an undo log

`undo` is a cargo feature that implies `force`, and rollback is a switch
on the runtime, `Runtime::set_rollback`, off by default, so a runtime
that doesn't ask still poisons. The whole suite passes with the feature
compiled in. With the switch on, a panic in graph code is caught, the
instant is undone, and the transaction is refused. `try_send` and
`try_pump` return the refusal as an error. `send`, `transaction` and
`pump` panic with it, and leave the runtime usable. The REPL has the
same switch, and prints the refusal:

```
> def b boom a
error: refused a transaction: node 16 failed: boom on 7; dropped its events at node 7
```

The log lives in a new engine module, `probe`, whose hooks are empty
without the feature. Each item on the half-done list above has an
answer:

- **The program.** A node's evaluation is caught where it runs, so its
  parts go back into the store before the panic goes on:

  ```rust
  if self.s.probe.on {
      let running = self.s.probe.running.replace(n);
      let ran = std::panic::catch_unwind(core::panic::AssertUnwindSafe(|| {
          (ops.eval)(&mut parts, self, n)
      }));
      self.store.parts[n as usize] = Some(parts);
      match ran {
          Ok(()) => self.s.probe.running.set(running),
          Err(payload) => std::panic::resume_unwind(payload),
      }
      return;
  }
  ```

  `running` names the node whose code was running when the panic came,
  which is what the refusal reports. A split's iterator gets the same
  catch.
- **Commit.** Each hold parks the value it replaces in its pending slot,
  which is empty after a commit, instead of dropping it, until relink has
  checked the moves; then the parked values drop. Relink records each
  move: the switch, its old inner, and its place among that inner's
  dependents, since marking follows that order. A failure at a switch's
  move, F1's, can then put everything back.
- **The roll back** runs in one order, whatever phase the instant
  stopped in:

  ```rust
  self.undo_commits();      // parked values back, pending ones dropped
  self.undo_memos();        // memos and values after the instant forgotten
  self.undo_moves();        // switches back, in their old place
  self.undo_listeners();    // listeners the unit tied to itself removed
  self.end_levels();        // child levels ended, capture stacks popped
  self.discard_created();   // new nodes unlinked and freed
  self.anchors.truncate(self.s.probe.anchors);
  self.s.scopes.clear();
  self.s.open_loops.clear();
  ```

  and then closes the unit, dropping its sends' events. `tx` isn't rolled
  back, so every stamp the instant left is stale.
- **What it can't undo.** An `accumulate_mut`'s function mutates its
  state in place at commit, and the `Drop` of a parked value is user code
  with nothing to put back. From either on, a failure still poisons:
  `a_panic_in_accumulate_mut_still_poisons`. So does a listener's panic,
  as before.

What it did, in `bough-repl/tests/rollback_undo.rs`. Each test checks the
handoff's criteria: the runtime isn't poisoned; the live count and every
live node's structure, switches and the order of every dependents list
included, are as they were, with no collection between; the bindings'
values are unchanged; no watcher printed; and a later redefinition of
the same binding works. Structure is compared by a hidden
`Runtime::topology`, which records every live node's dependencies,
dependents, reach, watchers, claims and flags.

| Case | Where it failed | Test |
|---|---|---|
| F1 | At the switch's move, after commit, so the whole log is read | `f1_a_cycle_found_at_the_switch_move_is_undone_after_commit` |
| F1, watched | In force, before commit | `f1_watched_a_cycle_found_before_commit_is_undone` |
| F2 | The binding's construct; its program is kept, so it redefines again | `f2_a_construct_closure_that_panics_is_undone_and_its_program_kept` |
| F2, at the root | The root construct, which makes the next binding | `f2_the_root_construct_is_undone_and_makes_the_next_binding` |
| F3 | In force, beside another redefinition, under 32 seeds; both are taken back | `f3_a_definition_that_fails_on_the_current_value_is_undone_before_any_watcher_prints` |
| F3, through the REPL | The refusal is an error line, and the old definition stays | `f3_through_the_repl_the_refusal_is_an_error_and_the_old_definition_stays` |
| F5 | The inner construct, built at the instant; the outer one's nodes go with it | `f5_a_nested_construct_that_fails_takes_the_outer_construct_s_nodes_with_it` |

To check that the tests can tell, each step of the roll back was taken
out in turn. Without the move undo, F1 fails; without the commit undo,
F1 fails; without the discard, six tests fail; without the catch, four
fail, F2's later redefinition first, on a construct with no program.
Forgetting memos, ending child levels, removing tied listeners and
truncating anchors weren't covered at first, so tests were added that
fail without each:
`a_value_computed_for_after_a_refused_instant_is_forgotten`, and, in
`bough/tests/rollback.rs`,
`a_split_s_children_queued_before_the_failure_go_with_it` and
`a_listener_tied_to_a_refused_transaction_goes_with_it`. F5's test now
covers the anchors. Clearing scopes and open loops is the one step no
test can see: a scope left behind sits under the next ones, and is
never consulted.

That check also caught a mistake in F5's test. The first version sent 2
before 7, and the inner construct that 2 built was still alive, so it
ran on 7 and panicked before the outer construct had built anything.
The roll back was given nothing to discard, and passed. Now the inner
construct fails only at the instant that built it.

Smaller findings:

- **What a refused construct made is freed at once.** The roll back
  unlinks every node the instant made and frees it, so the live count is
  back at its baseline with no collection, and the next allocation reuses
  the slots. Unlinking can't wait, as the map says; freeing could, at the
  cost of the live count. Freeing at once runs their `Drop`, user code,
  inside the roll back with the flag still set, so a panic there poisons.
- **A transaction is all or nothing.** F3 beside a good redefinition
  takes both back, since they were one transaction.
- **A closure's own state is outside the log.** A construct closure that
  counted its run before it panicked keeps the count:
  `a_closure_s_own_state_is_outside_the_log`. `AssertUnwindSafe` asserts
  exactly this, and nothing checks it.
- **A child instant is rolled back alone.** It has its own commit and
  listeners, so its parent and the children before it stand, the ones
  after it are dropped, and the unit comes back refused though not all
  of it was undone: `a_failing_child_instant_is_rolled_back_alone`.
- **A can't refuse what never ran.** An unwatched F3 still installs a
  definition that fails, and the failure comes at the next read:
  `f3_unwatched_the_definition_still_installs_and_fails_at_the_next_watch`.
- **The panic hook still prints.** A caught panic has already run the
  hook, so each refusal also puts a panic message on stderr. A host that
  refuses would install its own hook.

## Mechanism B: staging

`stage` is a cargo feature that implies `force` and needs no `std`,
under the same `set_rollback` switch. Its idea is the reverse of A's:
rather than undoing what commit did, it moves everything that can refuse
an edit ahead of commit, and keeps what the instant makes from touching
anything older until commit, so a refusal throws the instant's work away
and has nothing committed to undo. It catches no panic. Three changes
make it:

- **`try_construct`**: a construct whose closure returns a `Result`. An
  `Err` refuses the instant, naming the construct and carrying the
  error's text; the closure's scope is dropped, open loops and all:

  ```rust
  match out {
      Ok(v) => {
          b.pop_scope();
          b.put_event(me, v);
      }
      Err(e) => {
          b.drop_scope();
          b.refuse(me, e.to_string());
      }
  }
  ```

  With rollback off, an `Err` poisons, as a panic in the closure would:
  `with_rollback_off_a_closure_s_error_poisons`. Under `stage` the REPL's
  constructs are `try_construct`s, and its wiring returns a `Mismatch`
  rather than reaching the `unreachable!` arm, which the panicking paths
  still do, with the same message.
- **Staged links.** A node made at the instant that depends on an older
  one waits in a list to join that node's dependents until commit.
  Evaluation, pull and the cycle checks follow dependencies, which link
  at once, so nothing in the instant notices. A debug assertion checks
  that a refused instant's nodes never joined an older node's dependents,
  and with staging taken out it fires in four tests.
- **The switches move before commit.** After the last new node, and
  before force, every queued switch moves to the inner its outer holds
  after the instant, and the cycle check runs without panicking:

  ```rust
  while k < self.s.relinks.len() {
      let n = self.s.relinks[k];
      if let Some(cycle) = self.check_moved_or_refuse(n) {
          self.roll_back(None, cycle);
          return true;
      }
      k += 1;
  }
  ```

  Commit then doesn't relink. Taking the check out fails both F1 tests.

What it did, in `bough-repl/tests/rollback_stage.rs`, against the same
criteria as A:

| Case | How B refuses it | Test |
|---|---|---|
| F1 | The early check, before commit | `f1_a_cycle_is_refused_before_commit` |
| F1, watched | The same: the check runs before force, so the watch changes nothing | `f1_watched_a_cycle_is_refused_before_commit_the_same_way` |
| F2 | The binding's closure returns the mismatch; its new node, over `a`, never joined `a`'s dependents | `f2_a_construct_closure_s_error_is_refused` |
| F2, at the root | The wiring's mismatch is the root closure's error | `f2_the_root_construct_s_error_is_refused_and_it_makes_the_next_binding` |
| F5 | The inner `try_construct`'s error takes the outer one's nodes with it | `f5_a_nested_construct_s_error_takes_the_outer_construct_s_nodes_with_it` |
| F3 | Not refused: `boom` panics in a value, and still poisons | `f3_a_panic_in_a_value_still_poisons` |
| F4 | Not refused, for the same reason | |

So B covers every edit whose failure is a check or a closure that says
so, and nothing that panics. F3 and F4 fail once values flow, as the
handoff expected; the section on user functions below says what it
would take for B to reach them.

**Does B need most of A anyway?** It needs half. The roll back is
shared: dropping pending values, forgetting values computed for after
the instant, ending child levels, removing tied listeners, truncating
anchors and scopes, freeing what the instant made, and moving switches
back, since the early relink moves them before the check. What B never
needs is the other half: parking committed values, undoing commit, and
the catch around each node that keeps its program through an unwind.
That half exists only because A lets checks run during commit and
panics run anywhere. Moving the checks ahead of commit is what makes it
unnecessary, and with both features on, A's parking has nothing left to
protect: after B's reordering the only failures left in commit are an
`accumulate_mut`'s function and a `Drop`, which neither can undo.

**Rollback on by default.** The probe's tests turn rollback on; the
suite's 660 don't, so they say nothing about B's reordering on a graph
where nothing fails. To find out, the switch was made on by default and
the whole suite run under each mechanism, without committing that. Under
`stage`, four tests whose semantics have nothing to do with failure
broke: a switch built at an instant at which its outer steps links its
first inner, an older cell, so the link waits for commit, and the early
relink then moved the switch and looked for it among the old inner's
dependents, where it wasn't yet. A move now takes a waiting link from
the staged list, and makes its new one by the same rule:
`a_switch_built_and_moved_at_one_instant_finds_its_waiting_link`, in
`bough/tests/staging.rs`. With the fix, every test that still fails with
rollback on by default, 12 under `stage` and 41 under `undo`, asserts a
poisoning, or a panic out of `send`, for a failure the mechanism now
refuses. Two were read in full to be sure, and a third turned up a gap:

- **A cycle found by a read still panics under B.** The early relink
  reads each outer's value after the instant, and if that read goes
  around a cycle, `prepare`'s re-entry check panics before the cycle
  check can return it. B catches nothing, so that one poisons:
  `a_read_in_relink_around_a_cycle_its_check_would_refuse_panics_and_poisons`
  fails on the message, not on the poisoning. Refusing it would take a
  read that returns the cycle instead of panicking.

Smaller findings:

- **Staging reorders a dependents list.** When a switch moves to an
  older cell at the same instant that a construct links a new node to
  that cell, the switch now joins the cell's dependents before the new
  node does. Marking follows that order, so the plain evaluation order
  can change; RFD 2 says not to rely on it, and the shuffle tests pass.
- **`has_linear_switch` reads dependents**, so within an instant it
  can't see a loop closed with an older definition while that link
  waits. No test reaches it; it's a hole in the one-consumer check, not
  in rollback.
- **B builds where A can't.** `cargo check -p bough --no-default-features
  --features stage` passes for `thumbv7m-none-eabi` and for
  `wasm32-unknown-unknown`; `undo` needs `std` and doesn't build for the
  first. It does build for wasm32, where a panic is a trap, so its catch
  would never run; step 6 tries that.
