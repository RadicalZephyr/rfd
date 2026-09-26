# One rule for the I/O edge

_2026-09-26. Where a design session landed. Only the paint probe has
run; the spike comes next._

## The question

The same-thread `Io` on bough's `spike/same-thread-handle` left three
ways into the runtime: the `Runtime` itself, the `Io`, and the
`Remote`. Only the `Remote` couldn't register listeners. The reason
given was that GTK's listeners capture widgets, which aren't `Send`.
That shows a `Remote` can't serve GTK. It doesn't show a `Remote`
shouldn't listen.

A second asymmetry came out of the first. An `Io` call ran at once, or
right after the call in progress. A `Remote` call waited for the next
pump. The `Io` ran sooner only because it could reach the `Runtime`.

## The rule

Every way in can make any call that doesn't need an answer now. Both
handles run their calls at the next pump, the rule the `Remote` already
had. They differ only in whether their closures must be `Send`. Only
the `Runtime` reads.

## Where it landed

- **Two engine modes.** `Local` isn't `Send`, and every callback runs
  on the engine's thread, which is what GTK needs. `Threaded` is
  `Send`, and can be pumped from any thread, even a different one each
  pump.
- **Three ways in.**
  - The `Runtime`, which the driver owns through `&mut`, as in RFD 6.
    Its calls run now, and only it can read.
  - `Io`, a handle for `Local` engines, on every target.
  - `RemoteIo`, today's `Remote`, usable from any thread, on targets
    with atomics and a lock. A `Threaded` engine has only this one.
- **The handles behave the same.** Every call waits for the driver's
  next pump. Both can send, open transactions, listen, `listen_once`
  and anchor, and neither can read. Closures given to a `RemoteIo` must
  be `Send`; closures given to an `Io` needn't be. They share one error
  type, and both refuse calls from graph code with `FromGraphCode`.
  Every app runs a driver, since nothing else runs the queue.
- **A pump.**
  - Input slots run by priority. `connect` takes a `u8`, and every call
    must give one. Higher runs first, as in RTIC and the opposite of
    the NVIC. Equal priorities keep connection order.
  - A pending slot of higher priority pre-empts what's next, but only
    between whole units, children included.
  - Then both handles' calls run in the order they were made, taking
    only what was queued before the pump began. Queued calls rank below
    every slot.
  - A call a listener queues runs at the next pump.
- **Guards.** `Listener` and `Anchor` come in one kind, with no mode
  parameter. They're `Send` where the target has pointer atomics, and
  not `Send` without them, like the engine on a Cortex-M0. A guard
  holds an `Arc`, or an `Rc` without atomics, and the engine holds a
  `Weak`. The guard is live while the count is above zero, and a
  release is counted when the last owner drops.
- **`listen_once`.**
  - It takes an `FnOnce` and returns a guard. `keep` on it means "alive
    until it fires", not "alive forever".
  - On a cell it fires at registration, with the current value. On a
    stream it fires at the next event.
  - It ties to a transaction only through an explicit one,
    `tx.listen_once(...)`, and then it covers the whole unit, children
    included. `send` keeps its signature.
  - One that never fires is a bug in the user's graph. Debug builds
    assert on a tied one whose stream didn't fire in its unit, and on a
    kept one still pending when the engine drops. Release builds drop
    both silently. An `Option` would change every caller's type for
    the sake of a bug.
- **Memory: anchor it at the edge.**
  - Anchoring returns an `Anchored<T: Trace>`, which carries its value.
    `Build`, `construct`, both handles and the `Runtime` can anchor.
    `Build` and `construct` can't listen.
  - `Anchored` is `Clone`. Clones share one root, released when the
    last one drops, so a stream of them can be `share`d.
  - `Anchored` isn't `Trace`, so graph state can't hold one, and a root
    can't keep itself alive through a cycle.
  - `into_parts()` gives `(T, Anchor)`. That's the only place a plain
    `Anchor` comes from.
  - Collection runs after each whole unit. A waiting call roots the
    tokens it names: a registration its node or value, a send its input
    but not the value it carries.
  - An `Anchored` made during the build leaves through a variable the
    build closure captures. The return value stays the permanent root
    set, and must be `Trace`.
  - `Leaf`, `#[trace(skip)]` and hand-written `Trace` impls promise to
    hide no tokens and no guards. Stable Rust can't enforce that, so
    the derive refuses fields whose type names `Anchored`, which covers
    the common path.
- **Words.** Guards are `Listener` and `Anchor`. Handles are `Io` and
  `RemoteIo`. The glossary's entries for handle, guard, `Remote`,
  `Mode` and `Anchor` change, "guard" comes off the avoid list, and
  `Anchored` is new.

## What it changes

- RFD 3's "anchor it or lose it" becomes "anchor it at the edge", and
  RFD 4's "receive, then wire" goes. A token leaves a transaction alive
  only if the graph holds it or it left as an `Anchored`.
- The eager `Io` on `spike/same-thread-handle`
  ([RadicalZephyr/bough#5](https://github.com/RadicalZephyr/bough/pull/5))
  goes: the `Owner`, `with_sample`, `with_graph`, `Io::pump`,
  `NowError`, and running the queue between pump units. The branch is
  still the base for the new work.
- The plan to add subscriptions that hand values back to the caller's
  thread goes too. A `RemoteIo` listener that captures the user's own
  channel already does it, so `RemoteIo`'s docs show that, and the RFD
  promises nothing more:

  ```rust
  // Every value, to this task:
  let (tx, mut totals) = tokio::sync::mpsc::unbounded_channel();
  remote.listen_cell(app.total, move |t| { let _ = tx.send(*t); })?.keep();

  // One value, like a promise:
  let (tx, total) = tokio::sync::oneshot::channel();
  remote.listen_once(app.total, move |t| { let _ = tx.send(*t); })?.keep();
  let total = total.await?;
  ```

## What we considered

- **A send-only `Remote`,** as RFD 6 has it. Its routing table is still
  the pattern the docs recommend for many subscribers. It isn't a
  reason to withhold `listen`.
- **An eager `Io`.** It let a handler read its own sends. It also kept
  two timing rules, needed the `Owner` and weak handles to reach the
  runtime, and ran transactions inside GTK signal handlers.
- **Timing by where a call is made,** so that a listener's call ran
  right after its transaction. Outside a transaction the `Io` would
  still run sooner than the `RemoteIo`, only because it can reach the
  `Runtime`.
- **Running calls at once wherever possible,** Sodium Java's model. The
  driver would stop being the only thread that runs transactions, and
  RFD 7's host would stop owning the schedule.
- **An `Io` that keeps its reads.** Under next pump, a read sees only
  what the last pump committed, so read, change, send loses an update
  when two clicks land between pumps.
- **No collection while anything is queued.** A busy inbox, or an echo
  that never settles, would hold collection off.
- **Two kinds of guard,** such as `LocalListener` beside `Listener`.
  The local kind saves two atomic loads, and costs a second method for
  every registration. It adds no guarantee: every callback runs on the
  engine's thread either way.
- **A `Send` guard on the Cortex-M0,** through `critical-section` and
  `portable-atomic-util`. It adds a dependency for a case nobody has
  asked for.
- **Anchoring through a handle inside the listener.** It works, but
  every listener that receives tokens has to capture a handle and
  anchor before anything else. `Anchored` moves that to one place,
  where the node is built. That's the user naming the edge of their
  graph, as the build closure's return value already does.
- **A receipt from `send` to tie a `listen_once` to.** The `Runtime`'s
  `send` has already finished when it returns, so only the handles
  could offer one.
- **Lower numbers first, as in the NVIC.** Everyone but Cortex-M users
  would read it backwards, and an interrupt's NVIC number usually isn't
  the order the graph wants anyway.

## The costs we took

- A handler doesn't see its own sends before the next pump. A tied
  `listen_once` gets their result later instead. Read, change, send
  becomes send the intent and let the graph do the sum.
- A chain takes one pump per step, and tests pump until nothing is
  queued.
- A reused list row can show its old text for one frame during animated
  scrolling.
- A listener registered from a listener misses events until the next
  pump.
- Two atomic loads each time a listener fires, still to be measured.
- An `Anchored` hidden through `Leaf`, `#[trace(skip)]` or a
  hand-written impl holds memory until the engine drops. That's a leak,
  not unsoundness.

## What the paint probe showed

bough's `bough-gtk/defer-paint-probe/`, on `spike/same-thread-handle`,
emulates the driver in GTK 4.14 and records every painted frame.
Deferring a label's text to the driver gave a wrong frame in one
situation. A list view binds a row inside the frame clock's `update`
phase, as it does in kinetic scrolling and the scroll-to-start and
scroll-to-end animations, and that row is already on screen. That frame
shows the row's old text, and the next one is right. Rows were never
blank. Everywhere else the text landed before the next paint, because
the driver runs at priority 0 and GDK paints at 120. Real touchpad
flings, Wayland and other GTK versions weren't tested.

One frame of wrong data during an animated scroll isn't something a
person will notice, so it doesn't count against the rule.

## Next

- The spike, all of it, so the RFD describes nothing that hasn't run:
  - the `Io` as a queue whose waiting calls root their tokens;
  - registration through a `RemoteIo`;
  - one kind of guard, with bough-bench measuring its cost;
  - one order across both queues;
  - compile tests of which types exist and which are `Send`:
    `Runtime<Local>`, `Runtime<Threaded>`, `Io`, `RemoteIo`,
    `Listener`, `Anchor` and `InputSlot`, on every target and feature
    set CI checks. They live in the library, so a cross `cargo check`
    runs them;
  - `Anchored`, with collection after each unit;
  - slot priority and pre-emption, with RFD 7's fold law run against
    them;
  - `listen_once` and tied listeners;
  - the derive check.
- We agree the interface and the tests first, and each piece lands as a
  small commit.
- Then the RFD revision describes what ran.
