# Where Bough fits

_2026-09-29. Where a conversation after the
[literature review](../research/2026-09-28-frp-literature-review.md)
landed. The review asks whether Bough's design is sound; this asks
whether Bough is worth building, and for whom. The experiment it
proposed is [What a thousand rows cost](./2026-09-29-row-cost-probe.md)._

## The question

Is Bough building something that already exists, with users who would
be hard to win over? No.

## What we found

From crates.io, downloads in the 90 days to 2026-09-29:

- The Sodium-style crates are nearly unused. sodium-rust has 165 and
  nothing depends on it; carboxyl has 508 and no release since 2023;
  frappe has 195 and none since 2020.
- The reactive crates with big numbers ship inside a UI framework:
  `reactive_graph` and `dioxus-signals` have about 1.2M each. They're a
  different model; the review's crate table gives Leptos's graph no
  instant and no switching.
- A framework's core is used almost only by its framework.
  `reactive_graph` has 26 reverse dependencies, nearly all Leptos's own
  crates or add-ons for Leptos. The exception is `futures-signals`,
  built to be general, which four frameworks by other authors build on:
  hirola, pinwheel, mika and haalka, three of them dormant. haalka's
  author has also written jonmo, a Bevy-native core.

## Where it landed

- Bough succeeds as a foundation that app frameworks build on, not as
  raw FRP for app authors. Frameworks are what draw people in, and raw
  FRP is too flexible to be the product.
- We build the first framework, for the web. GTK is the hardest host to
  build for and not the most compelling; web apps are what most
  developers know. js-framework-benchmark, with keyed entries for
  Leptos, Sycamore and Dioxus, is the yardstick, and its app is a good
  first milestone.
- The pitch is the Boundaries architecture, a functional core in an
  imperative shell, with FRP as the core's substrate. It can be made
  without teaching FRP as a whole. What beats the Sodium ports is
  completeness, correctness, and documentation that doesn't assume the
  book.
- Embedded stays. `no_std` has to be designed in from the start, with
  `std` on top, because retrofitting it is very hard. RFD 7 and CI
  already do this: the core is `no_std` over `alloc`, CI checks
  thumbv6m, thumbv7m and thumbv7em, and the bounded tier waits behind a
  storage seam. The board milestone and the bounded tier can follow the
  framework. Embedded also keeps Bough general: with Oort, it's a
  consumer whose needs differ from the framework's, and the web wants
  what embedded wants of the core anyway, `Local`, no threads,
  allocation only when building, and small code.

## What we considered

- Claude read "frameworks write their own core" as a preference that a
  good general core wouldn't overcome. Zefira's reading fits the data as
  well: no suitable general core existed, and a framework's core gets
  welded to it because its author cares about the framework, not the
  core. The data can't tell the two apart, and whether other authors
  adopt Bough can only be tested once Bough and a framework both exist.
  jonmo says "suitable" depends on the host, as R3 in the
  [Bevy research](../research/2026-09-23-frp-host-embedding-requirements.md)
  has it. Zefira's reading applies to us too: we're about to be the
  framework author with our own core.
- Claude proposed cutting Cortex-M as a first-class target to make room
  for the framework. That mixed up the constraint with the work: the
  constraint is cheap and CI enforces it, and the expensive parts were
  already deferred.
- Claude leaned toward GTK as the first host, since bough-gtk exists
  and has found real boundary problems. The web won for the reasons
  above.

## What follows

- RFD 1's first sentence, "the go-to Functional Reactive Programming
  library in Rust", no longer says what Bough is for. The aim is nearer
  its "Easy to Build More Tooling On".
- Framework authors know signals and will ask why FRP. A candidate
  answer, not yet agreed: with signals, what an event does lives in a
  callback that writes signals, which is shell code; with Bough, events
  are streams in the graph, so the state changes they cause are in the
  core. If every input crosses the I/O edge, a framework can record a
  session and replay it exactly.
- Boundaries is implemented all the time as a reducer: Elm's
  architecture, Redux, iced, relm4, sans-IO. What's rare is a core that
  composes. The pitch depends on the baseline: order against callbacks,
  events in the core against signals, composition against reducers.
- RFD 3's brand gets harder to justify. Sycamore 0.8 tracked whether a
  signal was alive with lifetimes, and 0.9 removed them to pass signals
  around "without infecting everything with lifetimes". A brand would
  reach every framework's component types. That supports the review's
  leaning, `depends`, with a stale token's panic naming where the token
  was made, as Leptos and Sycamore do and the Oort fighter asked.
- The docs' reader is a framework author, who knows signals. "Coming
  from signals" reaches more of them than "Coming from Sodium".
- For framework authors, how Bough is driven and embedded matters more
  than its semantics, and the benchmark judges construction, equal
  steps, keyed lists and wasm size. RFD 1's benchmark shapes all
  measure propagation. The probe takes the first two.

## Still open

- Client-only first, or server rendering from the start. If components
  run under `Threaded` on a server and `Local` in the browser, the
  [Mode friction](./2026-09-27-mode-generic-core.md) comes back.
- Whether the framework drives the real build's API or follows it.
- What counts as close enough in the probe, set before it runs.
- Whether record and replay is what a signals framework can't match,
  tried on the framework.
