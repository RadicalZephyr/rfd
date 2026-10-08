# The cost: edge complexity gets concentrated

2026-10-06. Third thread from the same voice chat as 2026-10-06-io-less-composition.md and
2026-10-06-swappable-edges.md. Not a decision. Using "Bough" until the rename happens.

## Middleware doesn't break the model

Servlet-style middleware chaining is really awkward in Rust (tower and its trait soup). In
Bough it gets cleaner. Take logging middleware on an HTTP request stack: it doesn't write
a file mid-chain, it forks a stream of log events off to the side, and that stream gets
its own output edge like any other IO. Same move as splitting off error streams. The
middleware stays pure composition.

## But it moves the cost

Working through that example is what made the cost click. The middleware gives you back a
log stream, and now you have to receive it at the runtime build step and wire it to an
output correctly. Every piece of statefulness that a framework or a quietly-stateful
library would normally hide gets hoisted up to the edge, and the user has to deal with
each one.

So all the nice properties (pure middle, IO and entropy at the edge, replayable, testable)
aren't free. The complexity isn't eliminated, it's concentrated and made visible. And it
scales with how much IO the app touches, all in one place.

## Why that's still the right trade for Rust

This is the Rust pitch, one level up. Rust's bet is `Result` over exceptions. The happy
path isn't actually harder to write, Rust just shows you every place it can go wrong,
where Python or C++ or Java let you blissfully ignore exceptions and your code is quietly
worse and more breakable.

Bough does the same thing with IO and state. The wiring was always there, frameworks just
let you pretend it wasn't. "The difficulty of what you're doing becomes visible" is a
sentence Rust people have already bought once.

Visible wiring is reviewable, testable, and can't drift silently. That's better up to a
point.

## Tiered ergonomics

Past that point we want a nicer layer so the average user can plug and play, while full
manual control of the edge stays available for power users doing something truly
complex. Ergonomic surface with an escape hatch underneath, which is also very Rust.

Open question: can Bough give real help at the edge (bundling, conventions for assembling
edges) without re-hiding the thing we worked to surface? I don't know, and I don't think
we can know until this starts taking shape.

## Spike it early

This needs a spike sooner rather than later, possibly before the main build. It's the
question that could invalidate the ergonomics of everything else. If the edge is unusably
heavy at realistic app scale, I want to find out while the core is still malleable, not
after the framework ports and integrations are built on top of it.

## Open questions

- What does the edge look like for a realistic app with a dozen IO concerns (HTTP,
  logging, storage, RNG, timers)? That's probably the spike.
- What would the plug-and-play layer be: bundled edge sets, a builder, conventions per
  integration crate?
- How does this interact with the framework ports and the "where do effects go" question?
  Probably the same seam again.
