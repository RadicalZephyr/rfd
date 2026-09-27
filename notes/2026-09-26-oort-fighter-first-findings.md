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
