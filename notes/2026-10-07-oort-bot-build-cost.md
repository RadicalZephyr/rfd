# 2026-10-07 — Oort bot: graph-build cost is a constant factor, not structural

Status: note, not a decision. This came up while we were talking about
benchmarking a construct-heavy Bough for Mema. I'm working from memory of the
agent's findings, not from its notes, so the numbers are approximate.

## What the Oort experiment found

The experiment was a Bough bot for Oort, the Rust programming game where you pilot
a 2D space fighter with zero-gravity physics. Each bot gets about a million WASM
instructions per frame.

The agent's headline finding was that initial graph construction is what limits
how big a Bough bot can be, more than `construct` at runtime. Sending about 20
cells' worth of Oort API data into the graph, with nothing downstream using them,
cost roughly 300,000 instructions. That's about a third of the first frame's
budget. The agent estimated a practical ceiling of around 50 to 60 nodes for a
pre-built graph. You could do a fair amount with that, probably leaning hard on
affine-stream monomorphization and similar transformations, but it's limiting.
We never pushed a bot to the actual instruction limit.

Neither of the two ways around it worked:

- **Amortizing the build across frames.** The agent's simple version of "connect
  this later" added so many nodes that it wasn't viable.
- **Deferred construction.** We put switches in front of specific regions of the
  graph so those regions could be constructed on the next frame. That roughly
  doubled the node count and saved little build budget.

We did *not* test the general every-edge-through-a-switch shape from the Mema
work. That pattern didn't exist yet. My expectation is that it would have the
same problem worse, since each switch is several nodes on its own. That's an
inference, not a measurement.

## Diagnosis: one box per node

I'm fairly confident about the cause, but it still needs to be checked.

The agent benchmarked construction of single node types, using Oort's instruction
counter as the profiler. Per-node cost stayed roughly flat as the graph grew. It
was a little sublinear, with no reported spikes. So the cost is in the node
itself, not in the graph the node is joining.

My first guess was the backing vector reallocating. That doesn't fit, though.
Reallocation should amortize properly, and when it does happen it would cause
spikes, not a steady per-node cost.

What does fit is that current Bough does type erasure by box allocation, so every
node has at least one heap allocation. That's a fixed charge on every construct,
regardless of how big the graph already is. Under this explanation, the ~50-node
ceiling is roughly how many heap allocations fit in a third of a frame.

## Why it isn't alarming

Box-per-node was a known decision that we put off on purpose. In the design
grilling before the engine spike, the agent caught that type erasure becomes a
real problem in no-std, no-alloc environments. We settled on two things:

- **Target no-std-over-alloc first, not pure no-std.** I don't have any boards
  that need pure no-std without an allocator, so this let us punt the problem.
- **Spike the alternative and leave a seam.** We spiked fixed-size nodes:
  type-erased nodes stored inline in the backing vector alongside the node
  bookkeeping. It performed well enough on pure no-std that we'll build it when we
  support a platform that needs it. Bough keeps a seam so the backing storage can
  change without affecting the code built on top of it.

The twist is that Oort sits in the no-std-*over*-alloc bucket, where boxing was
supposed to be fine. WASM has an allocator. But Oort also has a hard per-frame
instruction budget, so it wants fixed-size-node storage for speed under a budget,
not because it lacks an allocator. The deferred design now answers two separate
pressures instead of one. The seam pays for itself sooner and in more places than
the embedded case it was built for.

So the Mema ceiling is around 50 nodes *in the box-per-node build*, and the
storage swap we already planned would lift it. The Oort agent probably overrated
how big a problem this is.

## Open

- Boxing as the cause isn't confirmed end to end. It's worth checking directly:
  compare naked-node construct cost against switch-mediated construct cost, and
  confirm that the allocation is the largest share of the cost.
- That the every-edge-through-a-switch shape carries the same node multiplier is
  inferred, not measured.
