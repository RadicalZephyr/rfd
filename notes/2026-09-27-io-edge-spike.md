# Where the I/O edge spike landed

_2026-09-27. The spike that
[One rule for the I/O edge](./2026-09-26-io-edge-one-rule.md) planned
has run, on bough's
[`spike/io-edge`](https://github.com/RadicalZephyr/bough/tree/spike/io-edge),
`e14c2a2..205ac13`. The RFD revision comes next._

## What ran

Nine steps, each with its interface and tests agreed before its code,
and then bough-gtk ported to the result:

1. A compile-time table of which types exist, and which are `Send`, on
   every target CI checks.
2. One kind of guard, `Listener` and `Anchor`, with no mode parameter.
3. `Anchored`, with the build's return anchored like anything else.
4. Collection after each whole unit, transaction zero included.
5. The `Io` as a queue: every call waits for the next pump.
6. `RemoteIo`, which registers as well as sends, with one order and one
   error type across both handles.
7. Slot priority and pre-emption, with RFD 7's fold law run against
   them.
8. `listen_once` and tied listeners.
9. The derive's check for `Anchored`.

Every commit passed the full gate: the workspace tests, 613 at the end,
the seven cross-target checks and MSRV 1.85. Mutation checks broke each
step's mechanisms, and a test caught every break that could change
behaviour. bough-gtk's eleven scenarios pass under Xvfb.

## Where it moved from the plan

- **A waiting send roots nothing.** The plan had it root its input. Its
  only use was to silence the debug panic for a send to a collected
  input, and that panic exists to catch bugs. Only a waiting
  registration keeps what it names alive.
- **Guards hold a count, not a `Weak`.** The engine's entries share the
  guard's state, and the guard is live while its count of owners is
  above zero. Its loads are relaxed, which on x86 and ARM alike is the
  same instruction as a plain load.
- **`Send` where something crosses threads.** `RemoteIo::anchor` takes
  any `T: Trace`, since only its tokens cross to the driver.
- **Two types for a queued unit.** `IoTransaction` runs an `Io`'s unit,
  and `RemoteTransaction` a `RemoteIo`'s. They differ in one bound: a
  listener tied to a remote's unit must be `Send`.
- **Checks in a fixed order.** A handle's call reports `Gone`,
  `Poisoned`, `FromGraphCode`, then `ForeignGraph`, and checks the
  tokens it names when it's queued. A transaction's closure hides its
  tokens, so those are found at the pump. After a panic escapes graph
  code, calls report `FromGraphCode` until an entry on the runtime
  finds the poison.
- **A pending flag per slot.** A slot on a Cortex-M0 is a `static`, and
  can't reach a flag the runtime owns, so each slot keeps its own. The
  pump marks a slot drained when it picks it, and each slot drains at
  most once per pump.
- **`listen_once`, in detail.**
  - One that fires ends its root then, and the automatic policy counts
    the release then.
  - `Runtime::listen_cell_once` runs its closure at once, so the
    closure needn't be `'static` or `Send`.
  - A tied cell listener runs when its unit is done, outside the
    transaction.
  - A unit that fails drops its tied listeners with it.
  - The debug check at drop doesn't see a once-listener that a handle
    asked for and no pump registered.
  - There's no `listen_steps_once`. `listen_once` on a steps stream the
    build made covers it, and we'll add it if we find a need.
- **The derive refuses `Anchored` only.** `Anchor` and `Listener` are
  common words, and a user's own type with one of those names would be
  refused.

## What it cost

- A waiting remote call is 64 bytes, up from 16. An inline enum of the
  tokens it roots keeps a remote send at one allocation, as RFD 6
  claims. A trait object per kind of call would bring it to about 24
  bytes, which we've left for later.
- Listener dispatch got cheaper. One send to 64 listeners is 9.3% fewer
  instructions than before step 8: a listener's call takes its whole
  entry, so a once-listener spends itself, and a node's entries are
  pruned only when one died. A first try at `listen_once` cost 6.3% on
  every listener call, and was replaced.
- The paint probe's late frame shows up in bough-gtk as predicted. A
  list view binds its rows inside the listener that changed its model,
  and their labels are right from the next pump, a turn of the main
  loop later.

## What bough-gtk showed

- **The `Driver` owns the runtime.** `spawn_driver(runtime)` returns a
  guard, and `tie(&window, driver)` ends it with the window.
- **Dropping it stops the pumping at once, and the runtime a turn
  later.** glib drops the future at the main loop's next turn, from C,
  where a panic aborts. The debug check as a runtime drops can panic,
  so the driver catches it.
- **A panicking listener ends the driver without an abort.** glib
  catches a panic that escapes a future's poll. That comes from glib's
  source; no scenario tests it.
- **An app can't read its runtime once the driver has it.**
  `listen_cell_once` through the `Io` is the read, a pump later.

## Next

- The spike's research note: the measurements, and the alternatives
  behind the choices above.
- The RFD revision, describing what ran. RFD 3's roots, RFD 4's
  "receive, then wire", RFD 6's handles and pump, and RFD 7's slots
  change most, and RFDs 2 and 5 name the `Remote` too. The one-rule
  note's "What it changes" still holds, and this note adds to it.
