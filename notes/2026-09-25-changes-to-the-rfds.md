# Changes to Bough RFDs

_2026-09-25. Zefira's notes from reading the RFDs, kept as written.
The FRP literature review took them as open review notes._

One share by Copy is limiting

should have "share by copy", "share by clone" could provide "share by Rc" and "share by Arc" as convenience fns.

snapshot needs to take tuples of cells like lift does. Maybe reuse the Tuples trait?

> takes a tuple of cells, arities two to six as Sodium ships them, and one function over references to all of them

needs a rework for ease of reading

maybe ` steps ` etc as a public API should be being a feature flag. internal use still available.

Does accumulate_mut actually need FnMut? it should still be Fn I think.

Sending from a Remote shouldn't treat "in transaction" as an error, it's a normal thing that will happen often. we need some mechanism to help remote clients wait until a sense is ok for these cases, blocking for threads, parking for async. edit: I forgot what this error was for and the error name doesn't clarify. improve error name. "illegal send inside graph" something like that.

We should probably rename Graph to Runtime



> The check is the one every entry already makes against a smuggled Graph.

what does this mean?

## RFD 6

> Latency is the distance from a send to the next pump, a property of where the driver sits: a woken thread pumps at once, a future at its next poll, a frame-based host wherever its embedder placed the runner, and an adapter states its placement and the latency it implies.

runtime integration library referred to as an adapter, overloaded with chain adapter, prefer integration

So Remote doesn't carry the Mode, so it cannot create new listeners or anchors, seems problematic potentially.

## RFD 7

> An overflow counter was the alternative, and a counter is a decision nobody made.

what does this mean? is it saying "we're didn't decide to add a counter" or "a counter represents a decision on how to handle multiple interrupts firing between pumps that should have been made but wasn't"?

we state that slots are only usable by one producer but there's no mechanism to enforce this. The embedded Rust ecosystem has already developed a pattern for this because it's a common design need in embedded, we should use it.


If the wasm target for bough can run under Node and on the web it should probably be called `bough-wasm` instead of `bough-web`.

Can we run embedded targets through QEMU in CI? is it performant, would it tell us something meaningful?
