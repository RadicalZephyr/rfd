# What an Oort fighter found first

_2026-09-26. Observations from the first real program built on bough's
[`spike/io-edge`](https://github.com/RadicalZephyr/bough/tree/spike/io-edge)
at `7e6dd2f`, and what they might mean for Bough. The experiments ran in
the bot's repository. Nothing here has been tried on Bough's side._

## Where these come from

We're dogfooding Bough on a bot for Oort, a game where each ship runs a
wasm program every simulated tick with a million instructions of gas.
The bot is a graph with two modes, Search and Engage. Engage is built by
`construct` from the scan that acquires a target and switched in over
Search. Each tick the driver sends its own ship's state to an input cell,
sends the radar scan as a stream event in its own transaction, then
samples the orders cell and writes it to the game. The whole design is
in the bot's `docs/notes.md`, on `RadicalZephyr/oort-rz`'s
`bough-fighter` branch.

Everything below behaves as documented. The question each one raises is
whether it's documented where a consumer will look.

## Snapshots and sampling read different sides of the instant

A snapshot sees a cell as it was before its transaction, and a sample
taken after the transaction sees it after. The bot has to use both
sides. Its track is an `accumulate` over scans, and a scan has to match
the track's prediction from before that scan, so fire decisions snapshot
the track. But the orders have to steer at a hit that arrived this
tick, so they're a `lift` over the track, sampled after the send
returns. Building the orders as a snapshot instead steers every hit at
the last tick's guess. Five of our six Engage tests passed that way. On
the acquiring tick the track's seed is the contact anyway, and on a miss
nothing updates. Only a second hit that had moved caught it.

We first ran into the rule sending own-ship state and the scan in one
transaction, where every snapshot of own-ship state saw the tick before.
Splitting them into two transactions fixed it, and agrees with RFD 7's
one cause per transaction.

The `snapshot` doc states the rule in a sentence. What a consumer needs
is the pattern: snapshot for what the event is judged against, and a
lift sampled after the transaction for what the event should produce. A
worked example of that pair might save the next consumer the same bug.

## A switch looks different from the edge

`construct`'s doc says a switch "starts at t from the inner its outer
held before t, moving after t if the outer steps at t". From the driver,
that looks like two behaviours. When the scan at t constructs Engage,
the sampled orders after t are already Engage's, and its own `hold` saw
the event that built it. The switched fire stream still delivers
Search's event at t and Engage's from t+1. We read that as an asymmetry
between `switch_cell` and `switch_stream` until we found the sentence.
It sits in `construct`'s docs, not in either switch's.

## Construction costs more than a tick

Gas is close to wasm instructions, so these are comparable counts.

| | Gas |
|---|---|
| Search tick, before the acquisition chain | 14,458 |
| Search tick, with it | 33,079 |
| A tick that constructs Engage | 122,162 |
| An engaged tick | about 56k to 58k |
| Tick 1, Search alone | 113,035 |
| Tick 1, with the acquisition chain | 302,830 |

Constructing Engage costs about 89k, for two lifts, an accumulate and a
shared fire chain. The acquisition chain (a `share`, `filter_map`,
`snapshot`, `once`, a counter and the `construct`) added 190k to tick 1,
and it more than doubles a tick in which nothing is acquired. These are in the budget for this bot, and they're
measured through a crate boundary that stops inlining. But a program
that builds per entity, one subgraph per contact say, would find
construction its limit well before propagation.

What might be worth finding out: where construction's instructions go,
per node kind, measured with something like `bough-bench`, and whether
an idle fused chain costs something per event that it wouldn't need to.

## Construction costs the same for every node

_Added 2026-09-27, from probe bots that each add one kind of node and
measure Oort's tick 1._

| What's built | Gas |
|---|---|
| An empty `Runtime::build` | 21k |
| The first input | about 25k more |
| A `hold`, `lift`, `switch_cell` or `construct` | 13k to 19k each |
| A `cell_loop` and its close | about 12k on top of the hold that closes it |
| A fused `map` and `filter` in front of a hold | about 145 |

A `construct` that never fires costs as much as a hold. The marginal
cost falls from about 18k to 13k as the graph grows, with a bump from
one hold to two that looks like a table growing. We found nothing
quadratic. Fusion does its job, so what costs is materializing, and
about 15k wasm instructions a node means a million-instruction tick
builds 60 or 70 nodes. The fighter's 460k tick 1 is 21k plus about 28
of them. We haven't profiled where a node's instructions go.

## Building the graph in stages didn't pay

_Added 2026-09-27._

We tried spreading the fighter's construction over several ticks, as a
dogfood of staged building. The graph booted itself: tick 1 built the
inputs and outputs that start idle, the first scan built Search through
`once().construct(...)`, and the second built the modes from Search's
bundle, which it received through a held cell. Each stage took over the
outputs with `hold` and a switch.

It works. Every test passed, and the fighter won the same ticks as
before. It also costs more than it saves:

| Tick | What it builds | Gas |
|---|---|---|
| 1 | The edge alone | 368k |
| 2 | Search | 81k |
| 3 | The modes | 330k |
| After | A Search tick | 71k, up from 44k |

Making outputs switchable from tick 1 took about 22 nodes: two
constants, a `never` and its `share`, two stage constructs and their
shares, the hold that hands Search on, an `or_else` and its `share`,
three holds and three switches, and a `booted` hold. At 15k a node the
plumbing costs about what the graph it spreads does. Oort's tick 1 is
also the ship's constructor plus its first tick, so the first stage
lands on top of the edge anyway. And when the second scan was a hit,
the modes and an Engage built in the same tick, for 506k.

Two things here are for Bough. At this per-node cost, staging only pays
for a graph much larger than its plumbing, so it's a pattern for big
programs, not a way to trim a small one. And "receive, then wire" at
the edge would have been cheaper than switches: each stage anchors its
outputs and the driver keeps the tokens, which drops the switches,
constants and holds. We didn't try it.

## Two smaller things from staging

A `construct` nested in another at the same instant works. The second
scan built the modes, the modes' acquisition saw that same scan, and it
constructed an Engage from inside the stage's own construct run. A test
pins that down, and it happened in the simulator too.

The rule that a closure's captures need `depends` bit us once. Each
stage's closure captured the input cell for our own state, and at tick
1 nothing else reached it, so the build's collection freed it. The
panic said only "a stale token: its node was collected", two ticks
later, when a stage first used it. It didn't say which token or where
it had been captured. Naming the token's creation site, even in debug
builds only, would have saved a guess.
