# Building the I/O edge: one rule, nine steps

_2026-09-27. A research note for the Bough design, answering one question:
can the I/O edge that
[One rule for the I/O edge](../notes/2026-09-26-io-edge-one-rule.md)
settled be built as it says, and what does it cost? The spike that answers
it is on `spike/io-edge` in the `bough` repository, the 33 commits
`e14c2a2..205ac13`, and it is not meant to merge. It followed the
note's plan in nine steps, each step's interface and tests agreed before
its code, and then ported bough-gtk to the result.
[Where the I/O edge spike landed](../notes/2026-09-27-io-edge-spike.md) is
the short version. Nothing here has authority over the RFDs; the questions
at the end are for Zefira._

## The answer first

It can. Both handles queue every call for the next pump and read
nothing, and the `Runtime` is the only reader. One kind of guard serves
both modes. `Anchored` carries a root to the edge, and the build's return
is one like any other. Collection runs after each whole unit, transaction
zero included, and "receive, then wire" is gone. Slots drain by priority
and pre-empt between whole units. `listen_once` works on the `Runtime`,
through both handles, and tied to a transaction. The derive refuses a
field that names `Anchored`. The engine still agrees with GHC: every test
run sends 1,024 random programs and 512 fold-law programs through it.

Seven things moved from the note, each for a reason the code found:

1. A waiting send roots nothing (E8).
2. Guards share an owner count with the engine, not a `Weak` (E1).
3. `Send` is asked for where something crosses threads, so
   `RemoteIo::anchor` takes any `T: Trace` (E12).
4. A queued unit runs with one of two transaction types, which differ in
   one bound (E25).
5. A handle's call checks in a fixed order, and refuses a foreign token
   when it's queued (E10, E11).
6. Each slot keeps its own pending flag, and drains at most once per
   pump (E16, E17).
7. A call wakes the driver unless another has since the last pump began
   (E5).

What it cost:

- A guard's liveness check: two instructions a listener call on x86, and
  none on the Cortex-M3 or aarch64, going by the code it compiles to
  (E2).
- The flag that refuses calls from graph code: about six instructions a
  transaction (E6).
- A waiting remote call: 64 bytes, up from 16 (E14).
- Listener dispatch came out cheaper than it went in. One send to 64
  listeners is 7.7% fewer instructions than when the spike first measured
  it (E22, E24).
- In GTK, the late frame the paint probe predicted, and a catch around the
  runtime's drop (E29, E31).

## What ran

| Piece | Where | What it is |
|---|---|---|
| The engine and the edge | `bough/src` at `205ac13` | The `Runtime`, `Io`, `RemoteIo`, the guards, `Anchored`, the input slots and `listen_once`. |
| The edge's tests | `bough/tests`, mostly `io.rs`, `remote.rs`, `slots.rs`, `listeners.rs`, `collection.rs`, `guard.rs`, `alloc.rs` and `fold_law.rs` | 474 tests in `bough`, doc tests included. |
| The oracle | `bough-oracle` | Unchanged but for its build helper, which calls `keep`. 134 tests, among them 1,024 random programs and 512 fold-law programs a run, each compared with GHC's answer. |
| The derive | `bough-derive` | Two unit tests on its expansion. |
| The benchmarks | `bough-bench/benches/regression.rs` | iai-callgrind instruction counts for the shallow, frame and fan-out shapes. CI fails a change past 5%. Fan-out is the spike's: one send to 64 listeners. Three unit tests check each shape against a baseline without bough. |
| The GTK port | `bough-gtk`, outside the workspace | The helpers a `bough-gtk` crate would offer, a demo, and eleven headless scenarios, each in a process of its own. |

Toolchains: rustc 1.94.1 (e408947bf 2026-03-25), and 1.85.1 for the
minimum supported version; GHC 9.4.7, Ubuntu's package; iai-callgrind
0.14.2 on valgrind 3.22.0; GTK 4.14.5 with gtk4-rs 0.11.5 and glib
0.22.10, under Xvfb 21.1.12. One x86-64 machine with four cores, Ubuntu
24.04.4. Every size below is x86-64's.

Every commit passed this gate before it was pushed:

```sh
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
cargo test --release -p bough --all-features   # or the step's suites
cargo +1.85 check -p bough --all-features
cargo bench -p bough-bench --bench regression
```

and `cargo check -p bough` with `RUSTFLAGS="-D warnings"` in seven
configurations: `thumbv7m-none-eabi` and `thumbv6m-none-eabi`, each without
default features and with `critical-section`; `thumbv7em-none-eabihf`
without default features; and `wasm32-unknown-unknown`, with and without
them. bough-gtk's second commit passed its own `cargo clippy
--all-targets` and `xvfb-run -a cargo test`. Its first passed clippy on the
library and the demo, and left the scenarios to the second.

For each step I broke its mechanisms on purpose, one at a time, and ran
the tests. Where a break got past, I added or fixed a test until it
didn't. A break that can't change behaviour, such as one that makes
pruning run more often, is the benchmark's to catch.

| Step | Commits | Tests after | Breaks, each caught | Also |
|---|---|---|---|---|
| 1. The capability table | `86e1885`, `bbf6697` | | 4, one per kind of row | The rename to `Runtime`, reversed and formatted, gives back the tree byte for byte. |
| 2. One kind of guard | `4674959`, `9d7ffaf`, `dfd77f9` | 552 | 3 | |
| 3. `Anchored` | `d54aa53`, `a62c132`, `db9f137` | 558 | 4 | 335 call sites rewritten by script, then folded back and compared with the old tree. |
| 4. Collection after each unit | `04a3cb8`, `fffb2b7`, `d23a9a0` | 559 | 2 | |
| 5. The `Io` as a queue | `6e1ea5c` to `7e6dd2f`, five | 564 | 18 | |
| 6. `RemoteIo` and one order | `cf3f274`, `b923ef5`, `be450c6`, `4d6f0e5` | 576 | 17 | The threaded suites, 40 runs across both builds. |
| 7. Slot priority and pre-emption | `71d06d7`, `3f7a105`, `96ad035` | 583 | 12 | The threaded and slot suites, 30 runs. |
| 8. `listen_once` and tied listeners | `f830d04` to `1829473`, six, and `6e99419` | 610 | 31 | The threaded suites, 25 runs. |
| 9. The derive's check | `3dd716e` | 613 | 4 | |
| The GTK port | `694e34e`, `205ac13` | 11 scenarios | 4 | All eleven, six runs. |

No threaded run hung or failed. That's evidence against a lost wakeup,
not proof of its absence.

## What moved from the note, and why

**A waiting send roots nothing (E8).** The note had a waiting send root its
input. A send to an input no root reaches can't be observed: anything that
could see its effect would reach the input, and keep it alive. So the root
never kept anything observable alive. All it did was stop the stale-send
signal from firing, the debug panic that points at a missing anchor, and
only for sends, since a transaction's closure hides its tokens (E7). Now a
waiting unit keeps nothing alive, and a waiting registration keeps alive
exactly what it will keep alive once registered. A stale send gets the same
diagnostic whichever way it was queued.

**Guards hold a count (E1).** The note had the engine hold a `Weak`. The
spike made the shared state a count of the guard's owners, held by the
guard and by the engine's entries alike. The guard is live while the count
is above zero. `keep` gives up the guard's share without lowering the
count, so the entry stays live and the state goes when the entry does:
nothing leaks. An `Anchored`'s clones add owners to one count. The last
owner's release counts one released guard for the automatic policy. Loads
and updates are relaxed, since nothing passes through the count between
threads (E2).

**`Send` where something crosses threads (E12).** `RemoteIo::anchor` takes
any `T: Trace`. Only the tokens its `Trace` finds cross to the driver; the
`Anchored` stays with the caller, or goes where `T` can go. The same rule
asks a remote listener for a `Send` closure, since it runs on the driver's
thread.

**Two transaction types (E25).** Step 5 gave both handles one
`IoTransaction`, since the note says the handles behave the same. A queued
unit runs the remote's way: a failed call drops the whole unit, and the
pump reports it. Step 8 split the type again. A listener tied to a queued
unit is stored in the runtime, so its closure must suit the runtime's mode.
An `Io`'s runtime is always `Local`, so its tied closure needn't be `Send`,
which GTK code needs. A `RemoteIo`'s runtime may be `Threaded`, so its tied
closure must be. `IoTransaction` and `RemoteTransaction` share the unit's
state and its end, and differ in that bound.

**A fixed order of checks (E10, E11).** Both handles check a call before
they queue it: the runtime has dropped, is poisoned, is running graph code
on this thread, or a token the call names is another runtime's. So
`IoError` has four variants, and a foreign token is refused where it's
used, not at the pump. A transaction's closure hides its tokens, so its
foreign tokens are found at the pump. After a panic escapes graph code, a
handle's call says `FromGraphCode` until an entry on the runtime finds the
poison, and `Poisoned` from then on (E9). The old `Remote` worked this way
already.

**A pending flag per slot, and once per pump (E16, E17, E18).** The plan had
slot writes set one flag the runtime owns. A Cortex-M0 has no `Arc`, and a
slot is a `static`, which can't hold an `Rc`, so a slot can't reach such a
flag. Each slot keeps its own pending flag beside its lock instead: a write
sets it and a drain clears it, both under the lock, and between units the
pump reads the flags without taking a lock. It's an atomic load and store,
which the M0 has. Each slot drains at most once per pump, marked as the
pump picks it. So a pump ends after one pass over the slots and the calls
queued before it began, whatever its listeners write while it runs.

**The wake rule (E5).** The note didn't state one. Step 5's proposal, wake
when the queue is empty, loses wakeups: during a pump the queue still
holds the calls the pump is about to run, so a listener's call made then
wakes no one. A call now wakes the driver unless another call through the
same kind of handle has since the last pump began. Each handle keeps its
own flag, the `Io`'s a cell and the remote's under the inbox's lock, and a
new waker resets both. A burst through both handles wakes the driver twice
at most.

**`listen_once`, in detail.**

- A once-listener is a root until it fires. When it fires, the root ends,
  and the automatic policy counts the release then, once, however its
  handle ends (E21).
- `Runtime::listen_cell_once` runs its closure at once, so the closure
  needn't be `'static` or `Send`. Through a handle it runs at the pump,
  which is how I/O code with no runtime reads a cell.
- A tied stream listener covers its unit, children included. One that
  heard nothing panics in a debug build once the unit is done, and is
  dropped in a release build (E23). A tied cell listener runs when the
  unit is done, outside the transaction, so a panic in it leaves the graph
  usable. A unit that fails drops its tied listeners with it.
- A debug build with `std` panics if a runtime drops with a kept
  once-listener still waiting (E26). It doesn't see a once-listener that
  a handle asked for and no pump registered.
- There's no `listen_steps_once`. It answers a different question from
  `listen_cell_once`, "tell me when it next changes" rather than "what is
  it now", but `listen_once` on a steps stream the build made covers it.

**The derive refuses `Anchored` only (E28).** `Anchor` and `Listener` are
common words, and a user's own type with one of those names would be
refused.

## What it cost

### Instructions

Each row is `cargo bench -p bough-bench --bench regression` at that
commit.

| Commit | What it measures | Shallow, plain | Shallow, shared | Frame | Fan-out |
|---|---|---|---|---|---|
| `4674959` | before the guard change | 646,243 | 935,006 | 64,327,840 | 7,435,756 |
| `dfd77f9` | one kind of guard | 645,224 | 933,982 | 64,282,800 | 7,566,283 |
| `96ad035` | before `listen_once` | 647,996 | 936,755 | 64,513,917 | 7,567,290 |
| `f830d04` | `listen_once` | 648,348 | 937,107 | 64,514,096 | 7,503,664 |
| `6e99419` | pruning only when one died | 648,347 | 937,106 | 64,514,975 | 6,864,663 |

Steps 3 to 7 lie between `dfd77f9` and `96ad035`. Among them, the flag
that refuses graph code's calls, measured at `65ecbed`, costs about six
instructions a transaction (E6). Two designs were measured on scratch
variants of `96ad035` and not committed:

- a first `listen_once`, whose calls returned whether they'd spent their
  entry, with the call in an `Option`: fan-out 8,081,286 (E22);
- pruning only when an entry died, without `listen_once`: fan-out
  7,061,290 (E24).

Fan-out by wall clock, with criterion, per send: 536 ns before the guard
change and 517 ns after, which criterion calls no change (p = 0.37). The
same 64 closures, boxed and called in a loop, take 158 ns.

### Sizes

Measured with `core::mem::size_of` in a scratch test at `205ac13`.

| What | Bytes |
|---|---|
| A token | 12 |
| A guard, `Listener` or `Anchor` | 8 |
| A listener's entry | 32, and 40 in a debug build with `std` (E26) |
| A remote unit, boxed, which is what the queue held before | 16 |
| A waiting remote call | 64 |
| A waiting `Io` call | 56 |

A waiting remote call is the call (24), the tokens it keeps alive (24), its
guard (8) and its stamp (8). An `Io` call is 8 smaller, since its call is
a plain box.

### Allocation

- A remote unit still allocates once, on its sender, and the driver's
  pumps allocate nothing
  (`a_remote_unit_allocates_once_on_its_sender_and_never_on_the_driver`).
- Keeping a guard leaks nothing once the runtime drops (E1).
- The steady state allocates nothing per transaction, as before.

## Waiting calls and the one-allocation claim

This is the context behind the enum the waiting calls use, which we chose
to keep, with the alternative we may want someday.

**The collision.** In step 6 a waiting remote call had to keep the tokens
it names alive, as an `Io`'s does. Collection can't see inside a boxed
closure, so each call carries its tokens beside the closure. RFD 6 says a
remote send "pushes a unit holding one boxed send", and the first spike
made that a measured claim, which a test pins: once its queue has grown,
a remote unit allocates once, on its sender, and never on the driver.
[The architecture brief](./2026-09-24-engine-architecture-brief.md) lists
it among the few things that allocate: "a remote send (on the sending
thread, as RFD 6 sanctions)". Step 5 kept an `Io` call's tokens in a
`Vec`. Reusing it for remote calls would have given a send's one input
token an allocation of its own: two a send.

**What we did.** The tokens a call names became a small enum: none, for a
transaction; one token held inline, for a send or a listener's node; or a
`Vec`, for an anchor's tokens (E14). The `Io` uses it too.

**What it cost.** A queue entry grew from 16 bytes to 64. The queue holds
its entries inline and reuses its buffer, so that's about 48 bytes more
per waiting call, not another allocation.

**What changed after.** `4d6f0e5` then dropped the send's root (E8), so a
send carries no tokens, and it allocates once with or without the enum.
The enum now only saves a registration that names one token a `Vec`, and
a registration allocates anyway. The 64 bytes remain for every waiting
call.

**The alternative, for later.** Put the tokens inside the one box. Each
kind of call becomes a small struct behind a trait object, with one method
that runs it and one that lists its tokens. An entry shrinks to about 24
bytes, and a call is still one allocation. It costs a trait and a struct
per kind of call, and a virtual call per waiting entry each collection. It
fits where queue memory is tight, such as a Cortex-M3 with
`critical-section`, where `RemoteIo` exists. A third option, two
allocations a send and a changed claim in RFD 6, is moot now that a send
carries no tokens.

## What bough-gtk showed

- **The driver owns the runtime.** `spawn_driver(runtime)` returns a
  `Driver`, a guard. Its future registers its waker and calls `try_pump`
  on each wake. It logs a unit the pump drops, then pumps again for what
  waited behind it, and a poisoned runtime ends it. `tie(&window, driver)`
  ends it with the window.
- **Dropping the `Driver` stops the pumping at once, and the runtime a turn
  later (E29).** glib drops an aborted local future at the main loop's next
  turn, from C, where a panic aborts. A debug build's check as a runtime
  drops can panic, so the `Driver` catches it and logs it. Without the
  catch, the scenario that tests it aborts. A call made during that turn is
  accepted, then lost with the runtime.
- **A panicking listener ends the driver, without an abort (E30).** glib
  catches a panic that escapes a future's poll. That's from glib's source;
  no scenario tests it.
- **The late frame is real (E31).** A list view bound three new rows
  inside the listener that changed its model. Their labels were empty
  after the pump that ran the sends, and right after the next.
- **An app can't read its runtime once the driver has it (E32).**
  `listen_cell_once` through the `Io` is the read, a pump later.
- **Three scenarios changed what they show.** The list view's labels are
  right a pump later. Rows one pump opens survive because a registration
  keeps what it names alive, not because the queue ran between units. And
  dropping the old owner became dropping the `Driver`. Two scenarios are
  new, for the `Driver`'s logging and its catch.

## What the RFDs need

The one-rule note's "What it changes" still holds. The spike adds this.

- **RFD 2.** Two ways in beside the `Runtime`: the `Io` and the
  `RemoteIo`, which replaces `Remote`. Every call through them waits for
  the next pump, and only the `Runtime` reads.
- **RFD 3.** The roots are live guards and waiting registrations, not
  waiting sends (E8). The build's return is an anchor like any other.
  Collection runs after each whole unit, transaction zero included (E4).
  "Anchor it at the edge" replaces "anchor it or lose it". A once-listener
  is a root until it fires (E21). `Leaf`, `#[trace(skip)]` and
  hand-written `Trace` impls promise to hide no tokens and no guards, and
  the derive checks the common case (E28).
- **RFD 4.** "Receive, then wire" goes. A construct anchors what it sends
  to I/O code with `b.anchor`.
- **RFD 5.** A queued unit whose call fails is dropped whole, its tied
  listeners with it (E25). After a panic escapes graph code, the handles
  report `FromGraphCode` until the poison is found (E9).
- **RFD 6.** The handles and their one error type, checked in a fixed
  order (E10, E11). Registration through both. The pump's order: slots,
  then both handles' calls in the order they were made, cut off when the
  pump begins (E15). The wake rule (E5). `listen_once` and tied listeners.
  "`Send` where something crosses threads" (E12). The one-allocation claim
  holds, now without help (E14).
- **RFD 7.** Slot priority as a `u8`, higher first, as in RTIC.
  Pre-emption between whole units, each slot at most once per pump, and a
  pending flag per slot, for the M0 (E16, E17). The fold law holds under
  both (E19). The table of which types exist where, and which are `Send`.
- **The glossary.** As the one-rule note says, plus `RemoteIo`,
  `IoTransaction` and `RemoteTransaction`.

## Questions for Zefira

1. **The drop check at shutdown.** A debug build now panics when a runtime
   drops with a kept once-listener still waiting. In tests that catches
   "the event never came". In an app it also fires at shutdown, for a
   request abandoned on the way out, and any host that drops the runtime
   from C must catch it, as bough-gtk's `Driver` does. Keep it as it is,
   or keep it only for tests?
2. **The queue entry.** Keep the enum's 64 bytes, or build the trait
   version's 24 before the RFD revision names a size?
3. **Reading in a GTK app.** Once the driver owns the runtime, the only
   read is a `listen_cell_once`, a pump later. Is that enough, or should
   the `Driver` let I/O code run against the runtime between pumps? That
   would put reads back outside the one rule.

## What the spike did not settle

- Nothing ran on ARM. That a relaxed load costs nothing there is read
  from the code it compiles to (E2), not measured.
- Nothing tested a real scroll in GTK, nor Wayland, nor touchpad flings.
- glib's catch of a panic at the driver's poll is read from its source,
  not tested.
- The drop check doesn't see a once-listener a handle asked for and no
  pump registered.
- The derive's check goes by name, so an alias or a type parameter gets
  past it.
- `sync_store` in bough-gtk only appends and removes; it doesn't move rows.

## Every finding

E1. **A guard's state is a count of its owners.** The guard and the
engine's entries share it. `keep` leaves the count raised, and the state
goes with the entries, so keeping leaks nothing. The last owner's release
counts one released guard. `9d7ffaf`; tests: keeping a guard leaks nothing
once the runtime drops, counted by the allocation test's allocator; a
listener dropped on another thread counts as released.

E2. **The liveness check costs two instructions a listener call on x86,
and none on the Cortex-M3 or aarch64.** x86 folds a cell's load into its
compare, but not a relaxed atomic load: fan-out went from 7,435,756 to
7,566,283 instructions (+1.76%), and the other shapes ran slightly fewer.
Without `#[inline]` on the state's methods, fan-out ran 10.5% more:
dispatch is generic, so it's compiled in the caller's crate, where a check
that isn't inlined is a call, twice a listener call. `9d7ffaf`, `dfd77f9`.
The ARM half is read from the code, not measured. A scratch library
crate held the three ways to check a count:

```rust
#![no_std]
use core::cell::Cell;
use core::sync::atomic::{AtomicUsize, Ordering};

#[no_mangle]
pub fn cell_live(c: &Cell<usize>) -> bool { c.get() > 0 }
#[no_mangle]
pub fn relaxed_live(a: &AtomicUsize) -> bool { a.load(Ordering::Relaxed) > 0 }
#[no_mangle]
pub fn acquire_live(a: &AtomicUsize) -> bool { a.load(Ordering::Acquire) > 0 }
```

Built with `cargo rustc --release --target <target> -- --emit asm` on
rustc 1.94.1, `cell_live` and `relaxed_live` compile to the same code for
`thumbv7m-none-eabi` and for `aarch64-unknown-linux-gnu`. `acquire_live`,
the old `Threaded` flag's load, adds a `dmb sy` on the Cortex-M3 and loads
with `ldar` on aarch64. On x86, `cell_live` is one `cmp` against memory,
and `relaxed_live` a `mov` and a `test`.

E3. **A `Local` runtime's guards are `Send` wherever the target has
pointer atomics.** Nothing a guard holds depends on the mode, so the mode
parameter went. The capability table says so. `dfd77f9`.

E4. **The build collects too.** Nineteen tests took tokens out of the build
through a side channel, and relied on nothing collecting before the first
send. They return them through the edge now. The build's collection closes
the gap where a token taken out unrooted lived until the first send.
`04a3cb8`.

E5. **"Wake when the queue is empty" loses wakeups.** During a pump the
queue still holds the calls it's about to run. A call now wakes the driver
unless another has since the last pump began. `65ecbed`, `be450c6`;
tests: queuing wakes the driver once per burst, for each handle.

E6. **Refusing calls from graph code costs about six instructions a
transaction:** +1.0% on the shallow shape, +0.1% on fan-out, nothing on
the frame. `Build::arm` and `disarm` set a flag the `Io`'s queue shares.
`65ecbed`.

E7. **A waiting transaction can't keep alive what it sends to.** Its
closure hides its tokens. `7e6dd2f`.

E8. **A waiting send's root keeps nothing observable alive.** A send to an
input no root reaches can't be observed. The root only stopped the
stale-send signal from firing. `4d6f0e5`; the tests that pinned the root
now pin its absence, one per handle.

E9. **After a panic escapes graph code, a handle's call says
`FromGraphCode` until an entry finds the poison.** The flag that marks
graph code stays set, since only a transaction that finishes clears it.
`65ecbed`; test: a call after an entry finds the poison is poisoned.

E10. **Both handles check in one order:** dropped, poisoned, graph code,
foreign token. `remote_io()` never panics; a poisoned runtime's remote
says `Poisoned`. The inbox's closed flag became an atomic, so a remote
call can see `Gone` before it takes the lock. `cf3f274`; two tests pin the
order.

E11. **A foreign token is refused when the call is queued.** Only a
transaction's closure hides its tokens, and those are found at the pump.
`cf3f274`.

E12. **A remote anchor needn't carry a `Send` value.** Only its tokens
cross threads. `b923ef5`.

E13. **A remote registration can't know its runtime's mode.** It carries
code for both, and a hidden `Mode` method picks one at the pump.
`b923ef5`.

E14. **Keeping a waiting call's tokens beside it would have cost a remote
send a second allocation.** An inline enum of the tokens avoided it; a
waiting remote call is 64 bytes, up from 16. See "Waiting calls and the
one-allocation claim". `b923ef5`; test:
`a_remote_unit_allocates_once_on_its_sender_and_never_on_the_driver`.

E15. **One order across both handles.** Every call takes a stamp from one
counter; a remote call takes it under the inbox's lock, so the inbox stays
in stamp order. The pump clears the remote's wake flag and reads the
counter in one critical section, so a remote call is either stamped in
time to run or finds the wake still to make. A remote call made after the
pump began waits for the next pump; the old rule ran whatever had arrived
by the time the pump reached the units. Stamps wrap, and compare by which
half of the range their difference lands in. `be450c6`.

E16. **A Cortex-M0 slot can't reach a flag the runtime owns.** Each slot
keeps a pending flag beside its lock, set by a write and cleared by a
drain under the lock, read by the pump without it. `3f7a105`.

E17. **An index-based drain loop can drain a slot twice.** A slot's
transaction can connect a slot ahead of it, which moves it along the list.
A pump serial, recorded per connection, keeps each slot to one drain per
pump. `71d06d7`.

E18. **Marking a slot drained when the pump picks it bounds the pump.** Two
breaks first showed up as hung tests, not failures. Marking on the pick
bounds the loop by the number of slots, whatever the flags say, and the
tests' listeners that keep writing stop after a cap, so a regression fails
instead of hanging. `3f7a105`.

E19. **The fold law holds under priority and pre-emption.** A property
test drives three slots at random priorities, whose listeners write slots,
their own included, while the pump runs. A model of the pump predicts
every drain, and the engine matches it drain for drain. Breaking
pre-emption, priority, the fold's order or once per pump fails it.
`96ad035`.

E20. **`listen_once` needs no bound that `listen` doesn't.** Its closure is
stored in the empty slot shape, `Option<F>`, which `M: Accepts<F>` already
erases, and then filled. `f830d04`.

E21. **A fired once-listener's release is counted once.** Firing adds an
owner nothing gives up and counts the release, so the handle's later drop
counts nothing more. The entry is spent before the closure runs, so a
closure that drops its own handle counts nothing twice either. `f830d04`;
test: the automatic policy counts a once-listener released when it fires.

E22. **A listener's call takes its whole entry, so a once-listener spends
itself.** The first design had every call return whether it spent its
entry, with the call in an `Option`. It cost about eight instructions a
listener call: fan-out 8,081,286, +6.8% over `96ad035`, or 514,000 more
across the benchmark's 64,000 listener calls. Taking the entry
cost nothing: 7,503,664, −0.8%. `f830d04`.

E23. **A tied listener's silence is read from its owner count.** The unit
holds the guard's only share. Firing adds an owner, so if the unit's
release is the last, the listener never fired. `30a7abf`.

E24. **Pruning a node's entries only when one died saves 8.5% on
fan-out:** 7,503,664 to 6,864,663. The spend marks the dispatch, so a
spent entry still goes at once; an entry whose guard goes after its turn
waits for the node's next dispatch or a collection. On `96ad035` alone it
measured 7,061,290, −6.7%. `6e99419`; a crate-internal test pins both
paths.

E25. **A queued unit needs two transaction types.** A tied listener's
closure must suit the runtime's mode: an `Io`'s runtime is `Local`, a
remote's may be `Threaded`. `IoTransaction` holds its `Runtime<Local>` and
sends typed values; `RemoteTransaction` reaches its runtime through a small
trait. A doc test pins that a remote's tied listener must be `Send`.
`114c12b`, `0c543b4`.

E26. **A kept guard is told from a held one by the state's strong count.**
Telling a once-listener's entry from another's takes a marker, which
exists only in debug builds with `std`, where the check does: 8 bytes an
entry there, none in a release build. `1829473`.

E27. **A panic in a listener drops its node's listener entries.** Dispatch
takes a node's list out of the store while it runs it, and unwinding drops
it. The runtime is poisoned by then, so nothing runs again, but a check
that walks the entries afterwards finds none on that node. Found writing
`1829473`'s test, which poisons through graph code instead.

E28. **The derive's check goes by name.** A derive can't see types. The
alternative, a check by type through autoref, catches aliases and never
refuses the wrong type, but misses `Vec<Anchored<T>>` and type parameters.
`3dd716e`; unit tests on the expansion, and a compile-fail doc test
checked by hand to fail for this reason.

E29. **glib drops an aborted local future at the main loop's next turn,
from C.** A panic there aborts the process, so a runtime whose drop can
panic must be dropped under a catch. `694e34e`; glib 0.22.10,
`main_context_futures.rs`; the scenario
`a_panic_as_the_runtime_drops_does_not_abort` aborts without the catch.

E30. **glib catches a panic that escapes a future's poll.** A local
future's poll runs under `catch_unwind`, and the task ends. glib 0.22.10,
`TaskSource::poll`. Not tested.

E31. **GTK binds a list view's rows inside the listener that changed its
model, and their labels are right a pump later.** Three binds, labels
empty after the pump that ran the sends, right after the next. `205ac13`;
the scenario `a_list_view_binds_rows_inside_a_listener`, which pumps by
hand.

E32. **A GTK app can't read its runtime once the driver owns it.** The two
scenarios that read the runtime, for its live nodes or a cell's value,
drive it themselves instead. `205ac13`.
