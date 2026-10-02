# Incremental propagation for collection-valued signals

The literature review supported bough's core design, but it was scoped to
the open questions already in the RFDs. Following one of the five surveyed
Rust libraries (a distributed dataflow system with a reactive intermediate
form) led out into the incremental-computation world: Salsa, then Adapton,
then a newer system built on Adapton's semantics. That raised a worry the
review doesn't answer: is a Sodium-semantics engine a Model T next to what
that world can do?

Mostly no. The two lineages aim at different targets. Incremental
computation is about memoised, demand-driven recomputation (Salsa,
Adapton) or streaming over large collections. Classic FRP is about
composable event and signal networks with a clean denotational meaning.
They overlap, but they're different courses, not faster and slower cars on
the same one.

The worry is real in one narrow place: signals whose values are
collections. When one element changes, a naive FRP engine recomputes
everything downstream over the whole collection. The incremental approach
propagates only the delta. This is the most likely place for bough to fall
down in practice.

## What we might build

Delta-aware collection types, structures that emit changes rather than
only new values, as a sibling crate alongside the core rather than inside
it. The core keeps its small, literature-backed semantics, and incremental
collections plug into it from outside. On this reading the gap is a future
crate on the roadmap, not a flaw in the core.

## Why it might matter

Whole-collection recomputation costs scale with the size of the
collection, not the size of the change. Any application built on
collection-valued signals (lists, keyed maps, sets of entities) pays that
cost on every update.

## What it would take to find out

A dedicated research pass on incremental collection propagation, wider
than the RFD-scoped review. The entry point is Ingo Maier's thesis and his
follow-up conference paper on incremental lists in Scala.React, which is
already in the corpus. The extracted plaintext corpus and the verified
review are the starting material.

One part can't wait for that pass: the seam. Does the core need hooks now
so a delta-aware crate can attach cleanly later, and what does the
interface between core and collections look like? That interface is the
one thing here that would be costly to retrofit, so it goes into the
upcoming grilling rather than waiting for the research.
