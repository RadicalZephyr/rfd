# Swappable edges: client/server as two graphs, migration, and a free differential test

2026-10-06. Second thread from the same voice chat as
2026-10-06-io-less-composition.md. Not a decision. Using "Bough" until the rename happens.

## In-memory edges

Because Bough is sans-IO at the core and real IO only shows up at the edge through
integrations, the ends of any pipeline are swappable. An in-memory version isn't a special
mode, it's the same graph with a different edge: feed it a buffer instead of a socket,
collect into a `Vec` instead of a file.

Obvious win is testing. Codec and protocol stacks are miserable to test when they're
welded to real IO. Here the whole stack runs in memory with no fixtures, and production is
the identical composition pointed at a runtime.

Less obvious: "in-memory" is a class of edges, not one. A buffer, a channel, another
graph's output. So graphs can feed each other through the same seam they'd use for a
socket.

## Client and server as two graphs

Minecraft's move was making single player into multiplayer with a local server. This is
that, but tighter. Write the client and server as two separate Bough graphs that always
talk through the same protocol composition. Single player connects them with an in-memory
edge, multiplayer swaps in a network edge.

- No separate single-player code path that drifts from the multiplayer one. It's one
  composition with a swapped end.
- Where the client/server boundary physically lands (same process, loopback, remote) stops
  being an architectural commitment and becomes a deployment choice.
- Security side effect: in single player there's no socket, no listener, no parser
  touching untrusted bytes. Network attack surface is zero until you actually invite
  someone.

## Local to hosted migration

Ties into orthogonal persistence, which is its own idea. You start playing single player,
a friend wants to join. Instead of NAT traversal and port forwarding (which wouldn't even
work, since the local server isn't on a network stack), you both connect to a server
running elsewhere, running the same program. Catching it up is one of:

1. **Replay** the events the client sent locally. Needs determinism.
2. **Ship a snapshot** of the edge state, which the rest of the server state can be
   reconstructed from, because it's the same code. Leans much less on determinism.

The player never has to choose between single player and multiplayer up front.

## Entropy belongs at the edge too

The graph is deterministic given its inputs. So the fix for non-determinism is pulling the
hidden entropy into edge state where the graph can see it. E.g. the PRNG seed lives in
edge state instead of being ambient randomness the program grabs. The question stops being
"is my program deterministic" and becomes "is all my entropy accounted for in edge state."

Same move as IO at the edge, applied to a different kind of impurity. re-frame's
co-effects already mapped this territory: RNG, browser history, local storage, anything
impure and stateful gets injected so handlers stay pure and replayable. Good vocabulary to
borrow.

## The two migration strategies are a differential test

Take the same program, reconstruct it twice: one graph by event replay, one by edge-state
snapshot. Run both through a harness and compare. If they agree, all your non-determinism
is pushed to the edge. If they diverge, there's a hidden source of entropy that the
snapshot carried and replay couldn't reproduce.

- You don't have to know where the leak is to detect it.
- You don't have to name expected outputs. The oracle is agreement between the two
  reconstructions.
- You don't have to name specific inputs either. If your input types can be generated
  programmatically (`proptest` `Arbitrary`, a fuzz corpus), this is fuzz testing whether
  your graph has pushed all coeffects to the edge.

Same shape as the engine's differential tests against the Haskell oracle, pointed at a
different property: not "does the engine match the semantics" but "did the app author push
all their coeffects to the edge." Could be something Bough ships as a harness.

## Open questions

- What exactly counts as "edge state" in Bough terms, and can the runtime capture/restore
  it generically?
- How this relates to orthogonal persistence, which I want to think about separately.
- Whether a shipped harness can make the replay-vs-snapshot test close to zero setup for
  users.
