# API confusions, and a two-part build

2026-10-18. Running commentary from 2026-10-11 to 2026-10-18 on what's confusing in Bough
right now, some of it from walking Tucker through the code. Not a decision. Using "Bough"
until the rename happens.

**Caveat:** Claude wrote this up from my descriptions, without seeing the current code or
API. Names, signatures and details may be wrong, or missing context the code would have
given. Check against the code before acting on any of it.

## "Edge" should probably be "boundary"

"Edge" collides with graph terminology, and Bough's graph is literal. An edge already
means a dependency between two nodes. The notes use it for where the graph meets IO, so
"swappable edges" reads two ways.

"Boundary" fixes that, and it's the word Tucker and I already used for Petty's
architecture. "Our boundary architecture, generalized" becomes literal API vocabulary, not
just pitch framing. It's also the title of Gary Bernhardt's talk, which is the lineage
this sits in.

Alternatives that don't work: "port" (clashes with the framework ports and with
ports-and-adapters, and "adapters" is already taken) and "shell" (functional core /
imperative shell, but it'll get confused with the REPL).

Knock-on: "edge state" becomes "boundary state," which reaches the replay-vs-snapshot
harness. The older notes stay as written.

## `Anchored<T>` shows up too early

It's partly that anchoring is a liveness concept that users read as "this is an output,"
and partly that it conflates keeping things alive with crossing the boundary. But the main
problem is placement: `Anchored<T>` is the return type of `Runtime::build`, so it's one of
the first things a user has to deal with.

The doc example anchors whatever `build` returns, then immediately calls `.keep()`. Read
cold, the wrapper looks like ceremony around a choice with no visible alternative. If
`build` returned `T` directly with anchoring implicit, `Anchored` could move down to
wherever scoped or released lifetimes actually matter, as a power-user type.

Related, from before: an unanchored error stream just gets collected, with no warning. If
boundary outputs became first class, with anchoring derived from them, that's where an
unconsumed-error check could live. Open whether anchor and boundary are two concepts or
one seen from either side.

## The build tuple trap

This is what tripped Tucker up. In the main doc example, `Runtime::build` returns a
2-tuple, and so does the closure passed to it. So `let (mut graph, edge) =
Runtime::build(...)` reads as destructuring the closure's tuple. It's actually the runtime
plus whatever the closure returned.

Cheap fix for the docs: have the example return three things, or a struct. But that only
patches the docs. Anyone writing their own two-element build hits the same trap, so the
real fix is the API.

Smaller cold-reading problems in the same example: the `Rc<RefCell<Vec>>` listener
plumbing is test scaffolding the reader has to decode before they get to Bough, and `edge`
goes with the boundary rename.

## A two-part build, where `build` is just `construct`

Split creation from building:

```rust
let mut rt = Runtime::local(); // or ::remote
let (clicks_in, label) = rt.build(|b| { /* ... */ });
```

No tuple to misread, and `rt.build` is reusable for adding to a running graph. bough-repl
already points that way, since it grows a live graph.

The semantics come for free from what already exists. We already have `construct`, which
builds graph in response to an event firing. A mid-run `rt.build` is an anonymous input
firing whose only job is running `construct` with the closure. So:

- A build runs inside a transaction.
- Samples of current cells see the value from before that transaction.
- Cycle checking and loop resolution already run inside `construct`, so they cover every
  build.

The empty runtime isn't a hazard. `send` and `listen` need a token that only a `build` or
`construct` hands out, so a runtime can't do anything until the first build. That's
obvious from the API but worth saying explicitly in the docs.

## A more relevant example than Petrol Pump

Port Gary Bernhardt's twitter client from the Boundaries talk to Bough, using ATProto and
Bluesky instead of Twitter.

- Possibly a different job from Petrol Pump rather than a replacement. Petrol Pump teaches
  FRP semantics with no IO at all; this would teach the boundary. Maybe Petrol Pump stays
  in the explanation docs and this becomes the "why Bough" example.
- It's close to the edge-cost spike in disguise: HTTP, auth, a live event stream, storage,
  timers. The spike with a recognizable shape to show for it.
- It forces the open HTTP question: which crate has a usable IO-less seam.
- ATProto auth is a lot of incidental complexity. Could stage around it by starting
  read-only from a public event stream (Jetstream, if it's still the easy
  JSON-over-WebSocket option) or recorded JSON through an in-memory boundary. Recorded
  JSON also shows off the swappable boundary and the differential harness. Auth and
  posting come later.

## Open questions

- What does `rt.build` do when called inside `graph.transaction`: join the current
  transaction, the way `construct` would, or get rejected?
- Is `Anchored<T>` still needed in the common path once `build` returns `T`, and what is
  it actually guarding?
- Anchor and boundary: two concepts, or one?
- Does "edge" exist in the API yet, or only in the notes? That decides how costly the
  rename is.
- Bluesky client: replacement for Petrol Pump, or a second example with a different job?
