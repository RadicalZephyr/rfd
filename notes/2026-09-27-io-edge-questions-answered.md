# The I/O edge spike's three questions, answered

_2026-09-27. The questions at the end of
[Building the I/O edge](../research/2026-09-27-io-edge-spike.md), and
where each landed. The first changed the spike, in `d3bae74` and
`1a2fe9d` on bough's
[`spike/io-edge`](https://github.com/RadicalZephyr/bough/tree/spike/io-edge),
so the RFD revision describes `e14c2a2..1a2fe9d`._

## The drop check stays, and `shutdown` skips it

A debug build still panics when a runtime drops with a kept
once-listener still waiting. That catches an event that never came,
even in a test that forgot to assert. But an app may close with a
request still out, and a host that drops its runtime from C, as glib
does, would abort on the panic.

`Runtime::shutdown` ends a runtime on purpose, without the check. A
runtime that just goes out of scope, as in a test, is still checked.
Checking only in tests had no clean switch, since `cfg(test)` reaches
only bough's own tests.

bough-gtk's driver ends its runtime with `shutdown`. The catch around
its drop went, since it was there only for this panic, so an app's
value that panics as it drops now aborts, as it would anywhere in GTK.

## The waiting calls keep the enum, and the RFDs don't name its size

No RFD names the size of a waiting call, and RFD 6's one allocation a
send holds either way. The trait version, about 24 bytes, is the real
build's to take if a target's memory budget asks for it. Nothing
outside the queue would change.

## Only the `Runtime` reads, in a GTK app too

Once the driver owns the runtime, app code reads a cell with
`listen_cell_once`, a pump later. Lending the runtime out between pumps
would bring back the double borrow, as an error in a handler that a
listener set off, and break the one rule. If late reads prove awkward in
real code, bough-gtk can offer a mirror: a value a listener keeps,
read at once and as fresh as the last pump.

## For the RFD revision

- RFD 6 gains the drop check and `shutdown`, with `listen_once`.
- RFD 6's one-allocation claim stands, without a size.
- "Only the `Runtime` reads" stands, as the one-rule note has it.
