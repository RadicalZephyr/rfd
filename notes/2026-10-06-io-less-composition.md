# Bough as the composition layer for IO-less protocols

2026-10-06. Brain dump from a voice chat, not a decision. Using "Bough" until the rename
happens.

## The pitch

We'd talked about framing Bough as familiar to Rust devs by comparing it to IO-less
(sans-IO) libraries. I think we can push that further. Bough isn't just *an* IO-less
library, it could be the infrastructure for composing IO-less protocol libraries and
connecting them to your app. Bring whatever IO you need, compose any protocol on top,
build your app at a higher level.

The bet is that protocol logic (parsers, framing, wire-protocol state machines) can be
written as reusable, mostly pure pieces with no opinion about where the bytes come from,
and Bough wires them to a runtime. The protocol layer ends up living at the edge of the
functional core, right where it meets the imperative shell.

Open worry: plenty of existing protocol crates probably smuggle in buffering or assume
they own the socket, so not everything will re-wire cleanly. That doesn't sink it
though. Bough gives authors a reason to separate protocol logic from IO, and could pull
the ecosystem toward that.

## Two sides, and why the split is healthy

- **Integrations** (bough-tokio, bough-smol, bough-std). Calling these "integrations"
  because "adapters" already means the iterator-style chains. This is a closed set. New
  runtimes basically never happen and the ecosystem has settled on Tokio (full featured)
  and smol (small). It's fiddly, bespoke work, but bounded, so we can actually write all
  of them and be done.
- **Protocol libraries.** The open, unbounded set. Ideally they ship their own `bough`
  feature composing their building blocks into a layer. We want that to be cheap for
  authors, and we pay for that by nailing the integrations ourselves.

Both sides have to come together. Clean integrations without protocols is pointless, and
protocols without integrations can't run.

## Bootstrapping protocols

Have to prove it ourselves first, then go upstream with "hey, this is a cool thing we
built," hopefully once there are some users.

- Start small. Port the framing pattern from Tokio's codecs (line-based, length-delimited,
  etc.). Those codecs are a big part of why I picked Tokio over std in the first place,
  but they're coupled to Tokio streams. A Bough version against a Bough protocol trait
  makes that pattern available on any runtime, and gives people a model to write their own
  IO-less protocols against. Could be its own crate.
- These small examples double as tutorials / how-to guides in the Diátaxis docs.
- HTTP is required for traction, since it unlocks all the REST APIs. reqwest is probably
  the wrong shape (batteries included, owns its runtime glue), though I don't know whether
  it has an IO-less layer underneath now. Lower level candidates to look at: `httparse`,
  `http`, `h2`. Haven't checked any of these yet.

Small examples teach, HTTP recruits.

## The java.io model

The thing I'm really picturing is java.io's layered streams. Open a file stream, wrap it
in a buffered reader, wrap that in gzip, wrap that in a tar reader, and you can read a
gzipped tar by composing layers in the right order. Each layer doesn't know or care what's
above or below it.

Rust doesn't really have that uniform layering. You get it ad hoc per crate, coupled to
whatever IO that crate chose. java.io's version is pull-based and blocking. In Bough the
composition lives in the FRP graph and the IO gets swapped in underneath through
integrations, so the same stack runs on Tokio, smol, or std.

## Errors split instead of unify

This is the consequence I hadn't said out loud. I'd been assuming this kind of code had to
live in the imperative shell, using normal libraries. The blocker for java.io-style
layering in Rust is `Result`: stacking decorators means unifying every layer's error enum,
which you only really want to do in an end-user crate, because it risks hiding things from
the user.

If the byte reading lives inside the graph (like I did for the TFTP implementation on
Sodium Rust), the natural move is to split off a stream every time there's a
`Result`. Bough provides one universal operation for splitting a stream of results into an
ok stream and an error stream. To wrap another layer, split, then wrap only the ok side,
since that's the only side you can process. Errors stay separate and typed all the way
out, and the user deals with all the error sources at the end. Compositions can still be
shipped as libraries, because errors compose by being split, not unified.

Known weakness: it's much easier to drop errors on the floor this way. `#[must_use]`
doesn't reach into the graph the way it does for a `Result`. Worth thinking later about
whether Bough can lint or flag an unconsumed error source. I think the arbitrary
composability is worth it.

## Open questions

- Which side to prime first in practice, given both have to land together.
- Which HTTP crate has a usable IO-less seam.
- How to catch unconsumed error sources.
- How this relates to the framework-ports question of where effects go. These protocol
  layers sit right at that seam too.
