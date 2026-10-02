## 2026-09-28: Renaming Bough

`bough` is taken on crates.io, and I'd rather rename than keep chasing the owner. The
name's crowded anyway: a Rust mutation tester, a Go worktree tool and a coding agent all
use it. Keeping Bough as the brand with a `bough-frp` package and `[lib] name = "bough"`
would work mechanically, but it doesn't fix the crowding.

What I want from the name, in order: short, memorable, unique-ish, easy to spell. It
doesn't have to describe FRP, it just can't mislead. The tree imagery was always a bit off
since FRP graphs aren't hierarchies; what I actually liked was the branching. Graph words
are out because they'd read as a graph data-structure crate.

Elements after Sodium didn't work. Cesium and natrium are too obscure for the reactivity
pun to land, and potassium (the actual next alkali metal) is taken. River and
branch-and-merge words are nearly all taken: braid, rill, weir, tributary, confluence,
eddy and the rest. anabranch and thalweg are free, but I don't like how they sound. river
looked free, but it's held by two yanked versions; `cargo info` 404s on fully yanked
crates, while the crates.io API doesn't. From the literary angle, clacks, whorl, lethe and
acheron are taken, and fuligin is free but I can't imagine typing it.

Leaning toward `portia`, after the jumping spider in Tchaikovsky's Children of Time. It's
free on crates.io with zero search hits there, easy to spell, and comes with a built-in
mascot. The other Portias I found are Shakespeare, Portia de Rossi, My Time at Portia, and
a dormant Python scraper.
