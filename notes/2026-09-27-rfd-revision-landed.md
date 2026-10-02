# Where the RFD revision landed

_2026-09-27. The revision
[What the RFD revision will do](./2026-09-27-rfd-revision-grilling.md)
planned is drafted, as
[RadicalZephyr/rfd#3](https://github.com/RadicalZephyr/rfd/pull/3),
stacked on the research PR. Nothing is published yet._

## What it is

- One commit per document: the glossary, then RFDs 1 to 7. Each can be
  read and published on its own.
- It describes bough's
  [`spike/io-edge`](https://github.com/RadicalZephyr/bough/tree/spike/io-edge),
  `e14c2a2..ad262cd`, which includes the grilling's five steps.
- Every State line is still `discussion`. Zefira publishes each RFD
  once she has read it.

## How it was checked

- RFD 2's example runs against `ad262cd`, given a stub `Ui`.
- RFD 6's chat room compiles with tokio in a scratch crate, since the
  repository has no tokio. Its subscription snippet runs.
- One claim the map left open ran first, as an experiment: a guard
  dropped between units keeps its garbage until a collection after the
  next unit, or `collect_garbage`. RFD 3 says so now.
- A second reader checked every claim against the code, the cited
  notes and the other documents. Its findings held up but one: it
  couldn't see the chat room compile, so RFD 6 now says how it was
  checked.

## What the map missed

The passages to change were mapped against the code before drafting.
Drafting found six things the map got wrong or left out:

- Sodium Java's `Stream` has `listenOnce`, so `listen_once` isn't new.
- The oracle checks `Apply` as a lift over a cell of addends. It's an
  engine test that runs the `Leaf<Box<dyn Fn>>` form.
- `scan`'s state updates during evaluation, not at commit.
- The 5% gate fails only on a rise.
- `std::thread::panicking()` stays true after a wasm trap. The wasm
  research ran it in Node.
- Nothing reports wasm code size yet, and `bough-web` and its Node leg
  aren't built.

## Waiting on Zefira

- The nine choices the PR lists, where the grilling didn't settle
  things. Two are the likeliest to be rejected:
  - Examples name the runtime `runtime`, while the crate's doc tests
    still say `graph`. The glossary saves "graph" for the network, so a
    `Runtime` called `graph` teaches the wrong word.
  - RFD 2's new argument against `Output<A>`: a construct's outputs
    need wrapping anyway, and `b.anchor` is that wrapping.
- Reading each document, and publishing it or sending it back.

## Still open

- bough's `error.rs` says the bounded engine adds `Exhausted` to three
  error types. The grilling left open which ones, so the comment claims
  more than was decided.
- The plans the RFDs mark as not built: GHC in CI, the core driver, the
  bounded tier, the debug dump, the UI benchmark shape, the wasip1 leg,
  the web pieces, and the button-to-LED milestone.
- The oracle experiment on `construct`'s creation-time cut, which the
  [oracle handoff](../research/handoff-2026-09-25-oracle-work-for-the-real-build.md)
  carries.
