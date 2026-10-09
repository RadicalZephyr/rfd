# Paying the edge cost: shared ports and owned IO edges

2026-10-08. Follow-up to 2026-10-06-edge-complexity-cost.md and
2026-10-06-middleware-and-edge-composition.md, worked through in a chat with Claude. Not a
decision. Using "Bough" until the rename happens.

## Two costs, not one

The edge-cost note says the complexity is concentrated, not eliminated. That lumps two
costs together:

- **Deciding.** Logs exist and they go to stderr. Scales with how many IO concerns the app
  has. That's the honest cost, the one the `Result` analogy is about. A dozen concerns as a
  dozen lines at the edge is fine, it's the app's list of effects.
- **Transport.** Carrying the log stream up through every layer's return type until it
  reaches the edge. Scales with concerns × composition depth. That's the part that would
  make it unusable.

The error splitting from the IO-less note is the same problem. A tar-in-gzip-in-buffer
stack returns `(ok, file_errs, buf_errs, gzip_errs)` and every layer grows the tuple.
Splitting avoided unifying the error types, not carrying them. So one answer has to cover
both.

## Rust's bet was Result plus `?`

Rust didn't just bet on `Result`. It bet on `Result` + `?` + `From`. Without `?` (and
`try!` before it), `Result` really is painful. `?` hides how the error travels and keeps
that it exists and where it ends up.

That gives a test for the open question in the edge-cost note, whether a nicer layer
re-hides what we worked to surface: **the ergonomic layer may hide the transport, never the
existence or the destination.** We can hold designs to that now instead of waiting for it
to take shape.

## Shared IO and owned IO

Two kinds of IO, and Rust practice already treats them differently:

- **Shared:** logs, metrics, reported errors, time, RNG. Many producers, one destination,
  and the user picks it. Libraries don't pick the `tracing` subscriber.
- **Owned:** this client's connections, this database's wire protocol. One producer, and
  the library knows the protocol. Libraries do own their sockets.

They want different mechanisms.

## Owned IO: GraphEdge and IoEdge

A library returns `(GraphEdge, IoEdge)`. `GraphEdge` is output for the rest of the graph,
usually a plain struct of `pub` fields, or just a `Stream` or `Cell`. `IoEdge` is output for
the world, and implements `IoEdgeWiring`, which wires it.

`IoEdge` composes by bundling. A library built from three libraries returns their three
`IoEdge`s as its own, so a parent forwards one value per child instead of one stream per
side-channel per layer. That's what handles depth. `RowView::new` in bough-gtk is already a
hand-written `wire`, so the pattern came out of real work, not just the whiteboard.

What `wire` has to look like, from walking it through:

- **It takes `&Io`, not `&mut Runtime`.** A row built inside `construct` arrives in a
  listener, which holds an `Io`. Dynamic subgraphs are where the hard cases are.
- **It returns a guard.** The listeners it registers have to be kept by something. Keep
  them forever and dynamic rows leak, drop them and the wiring is undone. bough-gtk gets
  away with `tie` because each listener has a widget. A row's log stream doesn't.
- **It takes the integration, it doesn't do IO itself.** If `wire` opens the socket, the
  library is welded to a runtime again and the in-memory edges from the swappable-edges
  note are gone.

Fields are private, but the `IoEdge` can be taken apart. That's what gives power users the
internals, and it makes the escape hatch per port instead of all or nothing.

## Shared IO: ports in the integrations

First version was ports passed down during the build: graph code feeds a port, many
producers per port, the edge claims each port once. reflex's `EventWriterT` and
`RequesterT` are prior art for exactly this. Two shapes, writer (logs, errors) and requester
(HTTP, storage, timers), and the requester shape is the sans-IO shape.

Where it landed instead: ports live in the integrations, and destinations get passed down at
wire time. The library's `IoEdge` holds its log stream and `wire` hands it to a destination
the integration supplies. Two wins over the build-time version:

- The build stays free of port handles. Graph code stays pure.
- Fan-in happens on the IO side, one listener per contributor, so each contributor's
  lifetime follows its guard. The build-time version needed a merge inside the graph, which
  raised a memory-model question: does a port root everything that feeds it, and so leak
  every dynamic subgraph? That question goes away.

It moves the open question rather than answering it though. How does a library's `wire`
find the user's log destination?

1. **A fixed set of well-known ports** in a small facade crate (log, metrics, erased errors,
   time, RNG), the way `log` works. Concrete, no generics, closed set.
2. **Lookup by type** on a wire context. Open, but checked at startup instead of compile
   time, and two HTTP clients both emitting `LogEvent` is ambiguous.
3. **Generic bounds** like `wire<P: Provides<Log>>`. Compile time, and it's trait soup.

I'm leaning toward 1, mostly because of the next section.

## Errors: typed until handled

Errors only go to a port if they're being reported to the user, and reported errors are
type-erased anyway (`anyhow`). Errors that need to stay distinct are errors the graph is
going to handle, so they show up in the `GraphEdge`. It's the thiserror/anyhow split.

That was the main objection to a fixed set of ports, since every library's error type is
different. An erased-error port fits.

This revises the IO-less note, which says errors stay "separate and typed all the way out."
They stay typed until something handles them. Reporting erases.

## GraphBuilder: probably a convention

How it went:

1. A trait with `construct(build, <inputs>) -> (GraphEdge, IoEdge)`. Looked at it and it's
   a convention, not a trait. What a trait buys is a place to hang the docs for the
   pattern, a concrete thing for authors to implement and users to look for, and maybe a
   data-driven middleware list.
2. Sharper: `construct(&self, build)`, and the inputs go into the value however the author
   likes (`new`, `Default`, a builder, a typestate builder). Nice property: the value is a
   recipe you can apply many times, including once per row inside `Source::construct`.

The middleware list still breaks on it. In a chain, each element's input is the previous
element's output, and that doesn't exist yet when you build the list. Captured inputs can
only describe independent components. Middleware needs the input back as a parameter,
fixed by the trait's type parameters. Request-only middleware is the easy case. Anything
that sees responses (timing, retries, auth answering 401) has to wrap the inner service,
tower `Layer` style:

```rust
trait Middleware<Req, Resp> {
    type IoEdge: IoEdgeWiring;

    fn wrap(
        &self,
        b: &mut Build,
        requests: Stream<Req>,
        inner: &mut dyn FnMut(&mut Build, Stream<Req>) -> Stream<Resp>,
    ) -> (Stream<Resp>, Self::IoEdge);
}
```

With `IoEdge = Box<dyn IoEdgeWiring>` that goes in a `Vec` (and `wire` needs
`self: Box<Self>`). A retry layer needs a stream loop for its feedback, which Bough has.

Rejected: a trait that takes a struct apart so the list can handle different `GraphEdge`s
generically. That's the HList/frunk road, and there's nothing generic a list could do with
them except return them.

Worth building? Not now. Tower's trait soup comes from the stacked type recording how it was
built, `Timeout<Auth<Logging<S>>>`. A Bough layer that materializes its output returns
`Stream<Resp>` no matter what built it, so a static stack is just `let` statements in the
build closure. The one choice left is `impl Source` (fused, nested types) or materializing
(one node), which is the `impl Iterator` vs `Box<dyn Iterator>` trade Rust people already
know. That's a pitch line. The `dyn` list is a small add-on for config-driven stacks, and
nothing in the static design blocks it.

Hold off on the trait until after the spike. A trait is an ecosystem commitment: once
authors implement it, changing it breaks them, and a convention can drift freely. The spike
will produce two or three instances of the pattern. If their signatures line up, write the
trait from those.

## The spike, revised

"A realistic app with a dozen IO concerns" only tests breadth, and breadth will look fine.
It needs depth (libraries built from libraries, each with side-channels) and dynamic
subgraphs.

- **Increment 1:** a two-level framing stack over an in-memory transport, each level
  logging. `IoEdgeWiring` taking `&Io` and returning a guard. One log destination. No
  `construct`.
- **Increment 2:** one level built inside `construct`. Check that dropping a row frees its
  nodes.

It should report how many wiring sites it took, and how each level's log stream reaches the
one destination.

On timing: edge ergonomics can't invalidate the FRP core, but they can invalidate the
build/edge API, and that's what's still soft on the io-edge branch. That's the real reason
to do it now.

## Open questions

- Which of the three ways `wire` finds a shared destination. Leaning toward the fixed set.
- The exact shape of the guard `wire` returns, and whether callers `tie` it the way
  bough-gtk does.
- Whether a `GraphBuilder` trait earns its place once there are real instances.
- Whether the requester shape (requests out through the `IoEdge`, responses back as an
  `Input`) is enough for HTTP.
- Whether an enumerable set of ports is what makes the replay-vs-snapshot harness from the
  swappable-edges note close to zero setup.
