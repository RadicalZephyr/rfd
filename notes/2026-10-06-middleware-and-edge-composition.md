# Middleware is just a pattern; edge composition is the real gap

2026-10-06. Fourth thread from the same voice chat as 2026-10-06-io-less-composition.md,
2026-10-06-swappable-edges.md and 2026-10-06-edge-complexity-cost.md. Not a
decision. Using "Bough" until the rename happens.

## Middleware as the thing to build

The logging middleware example quietly points at something worth building with Bough:
tower-style composable middleware that lets you stack layers like other languages do,
without tower's trait soup and unergonomic problems.

It doesn't depend on the sans-IO protocol story at all. It's I/O agnostic. tower is welded
to async and the request/response seam. In Bough, middleware is a transform you can splice
in at any point in the graph where a stream flows. It still makes the most sense at the
edge, but nothing constrains it there the way a framework built on a specific runtime is
constrained.

## But it's not really a framework

What do we even need for this? Sources, cells, the split operation, dependency
wiring. That's all existing Bough. Middleware is an implementation pattern, not a new
abstraction or engine machinery.

That makes it a cheaper flagship than it first sounded, and maybe a stronger one: "look
how little it takes to get tower's ergonomics out of plain Bough."

## The actual open problem: composing at the edge

What isn't solved is how to compose the forked side-channels (log streams, error streams,
whatever middleware hands back) at the edge.

My original vision for the Bough API was returning a type that describes your IO edge,
probably with a derive macro. We went a different direction: you get a build context
passed in, and you pass out everything that needs to be anchored. That's more Rust shaped,
but it's only concerned with anchoring the parts of the graph you want to keep around. It
doesn't address IO ergonomics the way the original design was aiming to.

The original design didn't account for any of this either, so we didn't really lose
anything. They were answering different questions. The anchoring design doesn't foreclose
an edge-composition layer, and my hope is that it's something we can layer on top of
Bough.

Possibility: the derive-macro idea comes back, aimed at assembling and wiring the forked
side-channels rather than describing the whole IO edge. That might be what the
plug-and-play tier from the edge-cost note actually is.

## Open questions

- Is middleware purely a pattern, or are there one or two small helpers missing (e.g. for
  splice-and-fork) so users aren't rewriting it by hand? The edge spike should tell us.
- What does an edge-composition layer on top of build context/anchoring look like, and is
  a derive macro the right tool?
- Where does the middleware example sit relative to the framework ports: ahead of them, or
  the thing they're built through?
