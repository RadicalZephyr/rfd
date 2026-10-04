# Frameworks in bough, as a curriculum

2026-10-02

## The idea

An earlier note said I wanted to build a web framework on top of bough to show it's a
language for building frameworks. The actual ambition is bigger: rebuild a bunch of the
popular app frameworks (TEA, re-frame, Redux, etc.) on bough.

The pure core of most of these looks tiny in FRP terms. Fold events into state, derive the
view from state. In bough that's an accum over merged events plus a map. Where they really
differ is effects (Elm's Cmd/Sub, re-frame's effect and coeffect maps, Redux middleware
and sagas), plus where state lives and how components nest.

## Why bother, if bough is supposed to replace frameworks

Part of the appeal of bough for me is that it (ideally) replaces the need for a
framework. But post-Rails web dev is so dominated by app frameworks that people expect
one, and a library that says you don't need a framework leaves them no easy way in, at
least as a mental model. In Rust, most of the popular reactive projects are frameworks
that built their own reactive core, and futures-signals, the outlier, mostly gets used by
people building frameworks on top of it.

The other way to say it: if bough is more expressive than most frameworks, app developers
land in a design space that only framework designers used to navigate. Before, they just
picked the framework whose decisions (or branding) they liked.

So the ports are an on-ramp, not the goal.

## Curriculum, not platonic ideal

I'd floated a research job on popular frameworks to build the "platonic ideal" of each
pattern. Going with the curriculum framing instead. An on-ramp has to be recognizable, so
a TEA that's cleaner than Elm but shaped differently loses the point. The ports stay
faithful and the idealizing goes in the commentary.

Each port is a page of combinators, and then it points at the few lines where it made a
choice another framework made differently. Work through three or four and you've learned
the design space without getting dropped into it cold.

## Form

One crate with all the ports in it. `cargo add` is the on-ramp, and having them side by
side says there are options. Alternatives I passed on: a crate per framework (a lot of
maintenance surface for one person, and it quietly argues you should stay inside a
framework), and a docs-only cookbook (no `cargo add` way in).

The off-ramp is copying the source of the port you use into your own codebase, documented
in lots of places. shadcn/ui is a precedent. Probably worth a standing rule for the crate
that each port uses only bough's public API and lives in one self-contained file. That
keeps copy-out trivial, and it makes the crate a test of the public API: if a port needs
engine internals, the gap is in bough.

Copying has a cost: copies diverge and fixes don't flow back. What survives is vocabulary
(update, msg), so naming in the ports deserves real care.

## The Lisp curse

The worry is that bough just becomes a new way to write spaghetti with reactive updates,
and that's almost certainly what most people will do at first. What makes me hopeful is
that if popular frameworks are really such small patterns, and the pieces compose, then
writing reusable patterns becomes an ecosystem project. Maybe the pitch is "frameworks
become conventions you can see through and step off" rather than "you don't need a
framework."

The caveat is load-bearing though: patterns compose as long as their code doesn't break
the FRP rules. If bough can't stop I/O inside a map, that's a convention, not a
guarantee. Eventually patterns need a way to earn trust. Types where possible, maybe a
replay test (same inputs twice, outputs must match) to catch hidden side effects.

## Open: where do effects go?

This is the big question to answer when I pick this back up.

I'd been thinking of two mostly orthogonal axes off bough: I/O integrations, and
abstractions built only on pure FRP. They aren't fully orthogonal, they meet at
effects. Composing a framework crate with an I/O crate needs a shared effect vocabulary,
or else an adapter for every pair. And the curriculum needs runnable examples, so every
port has to pair with some I/O anyway.

Candidate answer: the vocabulary is just bough. I/O crates expose sources and sinks as
streams and cells, and each framework shrinks to combinators. That's basically Cycle.js (a
pure main from source streams to sink streams, with drivers doing the I/O). Worth studying
as prior art and as a caution, since it was elegant and never caught on.

Unverified guess, related: Rust frameworks own their reactive core because they need to
own scheduling and how updates reach the renderer. If that's right, the I/O crates have to
match that coupling, which is a harder bar than the framework layer.

## Sequencing

Not now. This comes after folding in the literature review, the open RFD PRs, 0.1.0 and
the rename. Maybe pull one TEA-in-bough example forward for the 0.x announcement, to give
people a way in.

Experiment for later: tic-tac-toe as TEA-on-bough and re-frame-on-bough, with one I/O
backend. If each is a page of combinators, frameworks really are idioms. If I end up
inventing an effect protocol, that protocol is the real design surface.
