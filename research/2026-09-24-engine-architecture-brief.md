# Bough engine architecture: the spike's final design

_2026-09-24. Synthesized from three proposals (`arch-safe-first.md`,
`arch-fast-first.md`, `arch-semantics-first.md`) and three judgments
(fidelity, Rust, staging). This is the brief every implementation agent
follows. The load-bearing claims compile and pass in
`design/final-sketch/`; the raw outputs are in `design/final-sketch/results/`._

The spike is throwaway (Q5 a). It builds the engine in `bough` behind the
skeleton's signatures on `spike/engine-feasibility`, stages 1 to 6 fully
oracle-tested and stages 7 and 8 only deep enough to find API problems
(Q1 a). Every commit builds, is fmt and clippy clean, passes the tests and
the `no_std` target checks. A change to a public signature is a finding, and
its commit says why. Two RFD rules are claims under test from the first
commit: no allocation per transaction on a graph that is not growing, and
`no_std` over `alloc`.

---

## 0. The design on one page

- **Base: semantics-first.** One mechanism per clause of `Denotational.hs`.
  A node's data stays in the arena while its program is taken out to run.
  Every marked node is ordered, read-through cells included. Nodes created
  during a transaction, and all of transaction zero, run by memoized pull
  over their dependencies, never in creation order. A cell loop's forward
  token names its own `Loop` node. `split` and `defer` are two nodes with no
  dependency between them. Every steps view calls `prepare`, so no static
  flag can go stale.
- **Storage: safe-first's carriers.** Every stored value, closure and chain
  is erased into `M::Carrier`: `Box<dyn Any>` in `Local`, `Box<dyn Any +
  Send>` in `Threaded`. Only `Accepts<T>::erase` and `Mode::erase_send`
  build a carrier. So the compiler derives `Graph<Threaded>: Send`, a
  missing `Accepts` bound fails to compile inside the engine, and the engine
  is `#![forbid(unsafe_code)]`. The base design's `unsafe impl Send` is
  gone.
- **Performance structure: fast-first's.** A 32-byte hot record per node
  (stamps, position, kind, flags), with its relations and bookkeeping
  elsewhere. The flat loop runs the order blind: a node pulled early has its order entry
  overwritten with node 0. Two relations per node, dependencies and
  dependents. Shape benchmarks and a counting-allocator test from stage 1.
- **switch_stream: fast-first's watcher.** The outer is reach plus a
  watcher that marking follows only to queue a relink. A selector step
  relinks while the old inner is quiet, and a loop through the selection is
  legal.
- **Post-instant values are stored and promoted** (safe-first). `prepare`
  computes a read-through cell's post-instant value through `&mut`; `post`
  returns `&A`; commit promotes that value into the memo. The function
  runs once per step even with a steps view.
- **Fixes:** a same-instant cycle through a switch panics and poisons
  instead of overflowing the stack (R10); switches link their inner at their
  first evaluation, so a switch over a loop cell not yet closed works (R8);
  `accumulate_mut` returns a `State<S>` with no stream view; the oracle gets
  F6 and F7.

The final sketch: 32 tests and 9 `compile_fail` doctests pass on 1.94.1 and
1.85, including every adversarial case the judges ran (R1 to R10) and both
switch_stream probes; it builds for `thumbv7m-none-eabi` and
`thumbv6m-none-eabi` with every node kind instantiated; 20,000
steady-state transactions, 10,000 of them switch relinks, allocate 0 times;
it has no `unsafe`.

---

## 1. How the three proposals and three judgments combine

### 1.1 What comes from where

| Idea | From | Section |
|---|---|---|
| Data stays in the arena, the program runs out of it | semantics-first | 6.a |
| Every marked node ordered; read-through cells settle without user code | semantics-first (F4) | 5.3 |
| New-node phase by pull over dependencies, never creation order | semantics-first | 5.4 |
| `Loop` node for a cell forward; no aliasing | semantics-first | 6.h |
| `split`/`defer` as a capture node and an output node | semantics-first | 6.i |
| Every steps view calls `prepare`; kind dispatch at run time | semantics-first | 5.10 |
| The clause table as the oracle test plan; F6, F7 | semantics-first | 2 |
| Graph-id check around every build closure and construct closure | semantics-first | 6.g |
| Carriers, erasure inside `Accepts`, compiler-derived `Send` | safe-first | 6.a, 6.l |
| Post-instant value computed by `prepare`, promoted into the memo at commit | safe-first | 6.e |
| Counting-allocator test from stage 1; F4 regression test | safe-first | 7 |
| Checked downcasts everywhere; `u64` stamps | safe-first | 4 |
| Collection test shape; per-phase callgrind attribution | safe-first | 7 |
| Hot record separate from relations and stored values | fast-first | 4 |
| Tombstone pull: pulled entry becomes node 0 | fast-first (and base) | 5.9 |
| Watcher for switch_stream's outer | fast-first | 6.h |
| Started nodes are not ordered; the walk starts at their dependents | fast-first | 5.2 |
| Two relations: dependents for marking, dependencies for pull and checks | fast-first | 4 |
| Relink cycle check walks upstream from the new inner | fast-first | 6.h |
| Shuffle affordance as a seeded rotation of each dependents list | fast-first | 5.2 |
| Both send orders and early-evaluation counts in every dynamic test | fast-first, semantics-first | 7 |

### 1.2 Fatal flaws, and what fixes each

| Flaw (judge) | Fix here |
|---|---|
| semantics-first: switch_stream unresolved (fidelity, staging) | Watcher (6.h). Sketch: `switch_stream_relinks_on_a_selector_step_while_the_old_inner_is_quiet` (a, Y, Z) and `switch_stream_loop_through_its_selection` (1, 2, 3, 4). |
| semantics-first: accumulate_mut flag goes stale through close (fidelity) | `State<S>` type split, decided by Zefira before stage 2 (8, item 6). No flag exists. Fallback in 8. |
| semantics-first: `unsafe impl Send` missed `StreamLoop::close` (Rust, staging) | No `unsafe impl`. The closer creates the slot through `Accepts<A>::erase`, so dropping the bound does not compile (sketch: removing it gives E0277 inside the engine). |
| all three: stack overflow on a cycle through a switch (R10) | `prepare` carries entered and finished stamps and panics on re-entry; a switch's initial linking and every relink run the path check. Sketch: `r10_…` and `r10b_…`, both poison. |
| safe-first: creation-order post-pass | Not adopted. Pull over dependencies. Sketch: `r1_…` (label 50, then 50), `r2_…` and `r2b_…` (105). |
| safe-first: split as one node on the marking stack | Not adopted. Two nodes. Sketch: `r7_…` (0, 1, 2, 3), depth-first children. |
| safe-first: switch_stream's outer only reach | Not adopted. Watcher. |
| safe-first: neither F6 nor F7; fast-first: no F7 | Both patches land in `bough-oracle` before stages 4 and 5 are oracle-tested (2.2). |
| fast-first: static `dynamic`/`has_post` flags | Not adopted. `prepare` dispatches on kind; `State<S>` replaces `has_post`. Sketch: `r3_…` (71 in both orders). |
| fast-first: forward payload aliasing | Not adopted. `Loop` node. Sketch: `r9_…` (5). |
| fast-first: use-after-free through `mem::swap` of two `&mut Build` | No `unsafe`, so a swap is a wrong-graph error, caught by the graph-id check after the closure. |
| fast-first: dependents pool leaks on relink | Per-node `Vec` dependents keep their capacity. Sketch: 10,000 relinks allocate 0 times. |

### 1.3 Where the judges disagreed, and the decision

1. **Erasure.** The Rust judge wants safe-first's carriers; the staging
   judge counts the closed set of stored shapes against them. **Decision:
   carriers, with the shape set fixed in stage 1.** Five shapes
   (`Value`, `Slot`, `Cell`, `Memo`, `Stack`) cover every node kind of
   stages 1 to 8; §6.a lists what each kind stores. Soundness by
   construction beats an audit that already missed a bound once. The cost
   measured on one machine is small: the final sketch runs the shallow
   shape in 58 to 60 ns, the semantics-first sketch in 56 to 62 ns.
2. **safe-first's merit.** Rust 8, fidelity 3, staging 5. **Decision:** take
   its Rust mechanisms (carriers, allocation test, post-value promotion, checked
   downcasts, `u64` stamps), none of its protocol.
3. **fast-first's unsafe.** Its speed comes from layout, not from `unsafe`.
   **Decision:** take the layout (hot record, tombstones, two relations,
   upstream relink check, shuffle rotation) and none of the `unsafe`. The
   Miri negative control's lesson, that a node's readable part must stay
   borrowable while its program runs, is kept as the three-part split and
   the test `an accumulator reads itself through a read-through loop`
   (stage 3). Miri is not needed to gate an engine with no `unsafe`.
4. **Relink check direction.** Semantics-first walks downstream; fast-first
   upstream. **Decision:** upstream from the new inner at a switch's first
   link and at relink (a constructed screen is small; downstream of a UI
   switch is the rest of the screen); downstream from the forward at close
   (the forward's dependents are what was built with it).
5. **Split representation.** Fidelity keeps semantics-first's two nodes;
   staging keeps fast-first's "ordered but not walked past". **Decision:
   two nodes.** They give fast-first's rule without a special case in
   marking: the capture node has no dependents, and the output node is a
   started node at each child instant.
6. **Post-instant value.** Semantics-first computes it fresh by
   continuation; safe-first stores it. **Decision: store and promote.**
   `post` returns `&A`, and RFD 4's "a function may run twice for one step"
   tightens to once.
7. **Stamps.** `u64` (safe, semantics) against `u32` with renormalization
   (fast). **Decision: `u64`.** The hot record is 32 bytes either way.
8. **Dependents storage.** Flat pool (fast) against per-node `Vec`
   (semantics). **Decision: per-node `Vec`** for the spike; a pooled
   representation with free runs is a later optimization behind the storage
   seam, measured on the UI shape.

---

## 2. The semantics, clause by clause

### 2.1 The table

"Pre" is the value before the instant, `at c t`. "Post" is the value after
it. A slot is valid when its node's `fired == tx`.

| Clause (`Denotational.hs`) | Engine mechanism | Stage, test |
|---|---|---|
| `T = [Int]`, children `t ++ [n]` | A fresh `Tx` per instant, children included; depth-first child scheduler with an explicit stack | 4: `children_run_depth_first…` |
| `at (a, sts) t` | Committed values change only at commit; every read during a transaction (`snapshot`, `gate`, `sample`, a switch's selection) reads the committed value or the read-through memo | 1: `claim2_chain_fuses…` |
| `MkStream` (inputs) | `Kind::Input`: `send` writes the slot, stamps `fired`, starts the node | 1 |
| `Never` | `Kind::Never`: no dependencies, never marked | 1 |
| `MapS`, `Filter`, and `filter_map`, `map_to`, `once` | Adapters fused into one program through `Source::pull`; `once` keeps its flag in the chain | 1 |
| `Snapshot f s c` | `Snapshot::pull` reads `value(c)`; the cell is reach, not a dependency | 1 |
| `Merge sa sb f` (`knit`, `coalesce f`) | One node pulls both chains; `f(left, right)` when both fire | 1 |
| `Hold a s t0` (`t >= t0`) | `CellValue { value, pending }`; evaluation writes `pending`, commit moves it; a hold created at t is evaluated at t | 1, 6: `claim4_construct…` |
| `Constant` | `Kind::Constant`, never marked | 1 |
| `MapC f c` | Read-through: settles in order (steps iff an input stepped), memo on read | 2: F4 test |
| `Apply` (`knit`) | `lift`: settles once however many inputs stepped | 2 |
| `Updates c` | Steps view: fires when `fired(c) == tx`, emits a clone of `post(c)` | 2 |
| `Value c t0` | The same view, also firing when `created == tx`; one evaluation, so the `coalesce` is vacuous | 2 |
| accum knot | `accumulate` reads its own committed value while its program runs | 2 |
| `SwitchC c t0` | Pre = `value(value(outer))`; steps at creation, at every switch (quiet inner too), at inner steps; post at a switch = `post(post(outer))`, pulling the new inner out of order; relink at commit | 5: `claim5…`, R3–R6, R8, R10 |
| `normalize`, `chopBack` | At a switch instant `post` reads only the new inner | 5 |
| `SwitchS c` (`t <= t1` old) | Reads its current inner's slot; outer is reach plus watcher; relink at commit | 5: both switch_stream probes |
| `Execute s` | `construct` runs the closure with the graph's `&mut Build`; new nodes exist from t | 6 |
| `Split s` (`zipWith [0..]`) | Capture node at t, output node started by the scheduler; child n takes item n from every capture of the parent instant | 4 |
| `coalesce` in `Hold`, `Value`, `SwitchC`, `Split` | By construction: marked once, evaluated once, committed once | all |
| RFD 2 loops | Forward tokens; the dependency graph must stay acyclic except through `split`/`defer` | 3 |

### 2.2 The oracle

- **The harness** follows `design/oracle-spec.md`: GHC as a subprocess, one
  program per line, a pool of processes, programs built on the Rust side
  with the Bough API.
- **Loops by fixed point** (Q2 a, fact 2): the interpreter binds each loop
  to a concrete cell or stream, iterates from a never-stepping start, and
  stops when the iterate repeats. The text is unchanged.
- **F6, before stage 5:** `SwitchC c t0` uses `(a, sts) = chopFront (steps c)
  t0`. Without it a switch created after its outer switched starts from the
  old inner, out of time order. The 20 vendored tests still pass with the
  patch (`design/hs/patched/`).
- **F7, before stage 4:** sort `Split`'s output stably by time. Without it a
  merge of a split fed by its own children gets two events at `[0,0,0]`
  (100 and 10) where the engine gives one (110) (`review-fidelity/hs/SplitSort.hs`).
- **Comparison.** Per observed node and per top-level transaction, the list
  of events or steps in time order. The engine cannot see child indices
  (no affordance exposes them), so they are not compared; values and order
  are (fact 3).
- **Without GHC** every oracle test panics with an install hint unless
  `BOUGH_ORACLE=skip` (Q4 a).
- **Out of the generator:** loops inside construct bodies. R1, R1c, R2 and
  R2b are hand-written tests with GHC-computed expectations.
- **Refused programs:** the generator never emits a same-instant cycle; a
  separate test checks the engine refuses each shape (F3, R10).

---

## 3. Module layout

```
bough/src/
  lib.rs        re-exports, crate docs, compile_fail doctests; #![forbid(unsafe_code)]
  token.rs      Token; Stream, Shared, Cell, Input, State
  mode.rs       Mode (hidden Carrier, Flag, erase_send), Accepts (hidden erase),
                Erase, Carrier, FlagOps, Local, Threaded
  trace.rs      Trace, Tracer, Leaf
  source.rs     Source (sealed; hidden dependency, read_cells, pull), Node (sealed;
                hidden node_token, pull_inner, LINEAR), adapters, stream materializers
  cell.rs       CellRef; Cell and State methods: sample, map_cell, steps,
                steps_with_current, switch_cell, switch_stream
  lift.rs       Lift for arities 2 to 6, one macro, Output by kind join
  build.rs      Build = the core; input*, constant, never, cell_loop, stream_loop,
                state_loop, depends, connect; CellLoop, StreamLoop, StateLoop
  graph.rs      Graph, Transaction, Listener, Anchor, CollectionPolicy; Remote,
                RemoteTransaction (atomics targets)
  slot.rs       InputSlot
  error.rs      unchanged
  engine/       pub(crate); pub items only where a hidden trait method names them
    mod.rs      Tx, NOOP, IN_PROGRESS, START, Kind, flags, Hot, Relations, Cold, Data,
                CellValue, Memo, Ops, NodeOps, Entry, Cx, checked downcasts
    store.rs    Store: the storage seam. alloc, free list, generations, retirement
    sched.rs    Sched: every per-transaction buffer
    tx.rs       begin, fire_start, mark, evaluate, new_nodes, eval_node, commit,
                relink, dispatch, finish
    pull.rs     ensure, prepare, value, post
    loops.rs    scopes, close, path checks
    children.rs the child scheduler
    nodes/      stream.rs (chain, merge, steps), cell.rs (hold, accumulate, in-place,
                scan), read.rs (map_cell, lift), switch.rs, split.rs (split, defer),
                construct.rs
    collect.rs  roots, reach, sweep, prune (stage 7)
    inbox.rs    Remote's inbox, units, pump, slot draining (stage 8)
```

The sketch keeps `tx.rs` and `pull.rs` in one file and `nodes/` in one
file; the split above is for the engine.

---

## 4. Core types

```rust
// ----- mode.rs -----
pub trait Mode: sealed::Sealed + Sized + 'static {
    #[doc(hidden)] type Carrier: Carrier;           // Box<dyn Any> | Box<dyn Any + Send>
    #[doc(hidden)] type Flag: FlagOps;              // Rc<Cell<bool>> | Arc<AtomicBool> (stage 7 adds
                                                    //   a pointer to the graph's released counter)
    #[doc(hidden)] fn erase_send<T: Send + 'static>(value: T) -> Self::Carrier;
}
pub trait Accepts<T: ?Sized>: Mode {
    #[doc(hidden)] fn erase(what: Erase<T>) -> Self::Carrier where T: Sized + 'static;
}
#[doc(hidden)]
pub enum Erase<T> {         // the closed set, fixed in stage 1
    Value(T),               // T itself: a chain, a closure, a state
    Slot,                   // Option<T>, empty: a stream's slot, a pending event
    Cell(T),                // CellValue<T> { value, pending: None }: a stateful cell
    Memo,                   // Memo<T> { value: OnceCell<T>, post_value: None }: a read-through cell
    Stack,                  // Vec<Option<T>>, empty: a split's iterators, a defer's events
}
impl<T: ?Sized> Accepts<T> for Local { .. }             // every shape, as Box<dyn Any>
impl<T: ?Sized + Send> Accepts<T> for Threaded { .. }   // the same match; T: Send known here

// ----- engine/mod.rs -----
pub(crate) type Tx = u64;                  // a serial per instant, children included; never wraps
pub(crate) const NOOP: u32 = 0;            // node 0; a pulled order entry becomes this
pub(crate) const IN_PROGRESS: u32 = u32::MAX;
pub(crate) const START: u32 = u32::MAX;    // pos of a started node: never ordered

pub(crate) enum Kind {
    Noop, Input, Never, Stream, Hold, Constant, InPlace,   // stages 1, 2
    ReadThrough,                                           // stage 2
    Loop,                                                  // stage 3
    SplitCapture, SplitOutput,                             // stage 4
    SwitchCell, SwitchStream,                              // stage 5
}
// flags: LISTENERS, WATCHED, ON_STACK, COMMITS, LINKED, LIVE

pub(crate) struct Hot {        // Vec<Hot>: marking and the evaluation loop. 32 bytes.
    mark: Tx,                  // reached by marking in this transaction
    fired: Tx,                 // fired (stream) or stepped (cell); a slot is valid iff == tx
    created: Tx,               // the creating transaction
    pos: u32,                  // position in `order` when mark == tx; START for a started node
    kind: Kind, flags: u8,
}
pub(crate) struct Relations {  // Vec<Relations>
    deps: Vec<u32>,            // dependencies: settle, pull, cycle checks, reach
    dependents: Vec<u32>,      // marking; capacity kept across relinks
}
pub(crate) struct Cold {       // Vec<Cold>: never read on the fast path
    generation: u32,
    partner: u32,              // split capture <-> output; a switch_stream's outer
    reach: Vec<u32>,           // snapshot/gate cells, depends, a split output's capture,
                               //   a switch_stream's outer: collection only
    watchers: Vec<u32>,        // switch_streams to queue for relink when marking reaches this cell
    done: Tx, pulling: Tx,     // pull of a node created in this transaction
    prep_enter: Tx, prep_done: Tx,   // prepare: cycle detection and once per transaction
    relink: Tx,                // deduplicates the relink list
    visit: u64,                // path checks; collection's mark epoch (stage 7)
    linear_consumer: u32,      // stage 5: the switch_stream taking from this linear stream
}
pub(crate) struct CellValue<A> { value: A, pending: Option<A> }
pub(crate) struct Memo<A> { value: OnceCell<A>, post_value: Option<A> }

pub(crate) enum Data<M: Mode> {   // the data plane: what other nodes read
    Empty,                                            // node 0, never, loop, split capture, switch_cell
    Slot(M::Carrier),                                 // Option<A>: every stream node
    Cell(M::Carrier),                                 // CellValue<A>: hold, accumulate, constant, input_cell
    InPlace { state: M::Carrier, pending: M::Carrier },   // S, Option<E>: accumulate_mut
    ReadThrough { f: M::Carrier, memo: M::Carrier },  // F, Memo<B>: map_cell, lift
}
pub(crate) struct Ops<M: Mode> {  // per node type, monomorphized, promoted to 'static
    eval: fn(&mut [M::Carrier], &mut Build<M>, u32),       // program nodes
    commit: fn(&mut [M::Carrier], &mut Data<M>),           // hold, accumulate, in-place
    value: for<'a> fn(&'a Build<M>, u32) -> &'a dyn Any,   // read-through pre value
    compute_post: fn(&mut Build<M>, u32),                   // read-through post value
    settle_memo: fn(&mut Data<M>),                          // promote post_value or clear
    inner: fn(&Build<M>, u32, bool) -> Token,               // switches: token in outer's pre/post value
    emit_child: fn(&mut [M::Carrier], &mut Build<M>, u32) -> bool,
    end_children: fn(&mut [M::Carrier]),
    coalesce: fn(&mut [M::Carrier], &mut Data<M>, &mut dyn Any),  // coalescing inputs
    trace: fn(&Data<M>, &[M::Carrier], &mut Tracer),        // stage 7: committed values only
    clear_slot: fn(&mut Data<M>),                           // stage 7
}
pub(crate) trait NodeOps<M: Mode> { const OPS: Ops<M>; }   // one zero-sized marker per node type;
                                                             // `&Marker::OPS` is &'static (1.85 ok)
pub(crate) struct Entry<M: Mode> {  // one listener
    flag: M::Flag, f: M::Carrier, call: fn(&mut M::Carrier, &mut Build<M>, u32),
}
pub struct Cx<'a, M: Mode> { pub(crate) b: &'a mut Build<M> }  // pub, unnameable, no constructor

pub(crate) struct Store<M: Mode> {   // THE storage seam
    hot: Vec<Hot>, relations: Vec<Relations>, cold: Vec<Cold>, data: Vec<Data<M>>,
    parts: Vec<Option<Box<[M::Carrier]>>>,   // the program: taken out while it runs
    ops: Vec<&'static Ops<M>>,
    listeners: Vec<Vec<Entry<M>>>,
    free: VecDeque<u32>, live: usize,          // stage 7: FIFO free list
}
#[derive(Default)]
pub(crate) struct Sched {            // cleared by len = 0, never freed
    starts, order, created, commits, memos, relinks, dispatch: Vec<u32>,
    cursor: u32, order_done: bool, stack: Vec<(u32, u32)>,
    levels: Vec<Vec<u32>>, frames: Vec<usize>, depth: usize,   // children
    search: Vec<(u32, u32)>, visit_epoch: u64,                 // path checks
    open_loops: Vec<u32>, scopes: Vec<usize>,                  // loops
    shuffle: Option<u64>,                                      // test affordance
    statistics: Statistics,                                    // `statistics` feature
}

// ----- build.rs, graph.rs -----
pub struct Build<M: Mode = Local> {   // the engine core; no lifetime
    graph_id: u32, store: Store<M>, tx: Tx,
    in_tx: bool,                      // the transaction-in-progress flag = the poison
    s: Sched, mode: PhantomData<M>,
}
pub struct Graph<M: Mode = Local> {
    build: Build<M>,
    roots: Vec<Token>,                // the build's return value, traced once
    anchors: Vec<(u32, M::Flag)>,     // stage 7
    policy: CollectionPolicy, stale_operations: u64,   // stage 7
    inbox: Option<Arc<Inbox>>, slots: Vec<SlotConnection>, waker: Option<Waker>,  // stage 8
}
```

`Graph<Threaded>: Send` holds because every field is `Send` when the
carrier is `Box<dyn Any + Send>`: integers, `Vec`s of them, function
pointers, `&'static Ops` (function pointers are `Sync`), `Arc<AtomicBool>`
flags. `Graph<Local>: !Send` because `Box<dyn Any>` is not. `Graph` is not
`Sync` in either mode (`OnceCell`); RFD 6 asks only for `Send`.

---

## 5. The transaction, step by step

### 5.1 Begin and send

```
begin        assert !in_tx ("poisoned"); in_tx = true; depth = 0; begin_instant()
begin_instant tx += 1; starts, order, created, commits, memos, relinks, dispatch: len = 0;
             order_done = false
send(i, v)   check(token)                       -- graph id, liveness, generation
             if fired[i] == tx: coalescing input -> ops.coalesce(old, v); else DoubleSend
             else write slot; fired = tx; mark = tx; pos = START; starts.push(i);
             dispatch.push(i) if LISTENERS
```

Nothing in the arena is cleared between transactions. A slot is valid only
while `fired == tx`; stale `mark`, `pos` and stamps are ignored by stamp.
A send to a collected input is a debug-mode panic and a counted release-mode
no-op; a foreign token panics; `try_send` returns the error (stage 7).

### 5.2 Mark

An iterative depth-first walk from each started node's dependents, with the
reused `stack`. Started nodes are never ordered.

```
for each start s: push (s, 0)
  top (n, k): if k < dependents(n).len:
                d = dependents(n)[k]; k += 1
                if mark[d] != tx: mark[d] = tx; ON_STACK; push (d, 0)
                     if WATCHED(d): for w in watchers(d): queue_relink(w)   -- no descent
                elif ON_STACK(d): panic "same-instant cycle reached marking"  -- a backstop
              else: pop; if n != s: clear ON_STACK; pos[n] = order.len; order.push(n)
```

The post-order read backwards is a topological order of exactly the affected
region. **Every marked node is ordered**, read-through cells and loop nodes
included: marking reaches more than what steps (a hold behind a filter that
rejects is marked and does not step), so "stepped" must be computed in
dependency order (F4). A split capture has no dependents, and its output has
no dependency on it, so marking never passes from one to the other.

With `set_shuffle_seed(Some(s))`, a separate walk starts each dependents
list at a seeded rotation; any depth-first order is a valid order. With
`None` the plain walk runs, so the affordance costs nothing when off.

### 5.3 Evaluate

```
for i in (0..order.len).rev(): cursor = i; eval_node(order[i])
order_done = true
```

No memo check and no recursion. `eval_node` by kind:

| Kind | Evaluation |
|---|---|
| `Noop`, `Input`, `Never`, `Constant`, `SplitOutput` | nothing |
| `ReadThrough`, `Loop` | settle: stepped iff a dependency fired; no user code |
| `SwitchCell` | first evaluation links the inner (6.h); stepped iff outer fired, inner fired, or `created == tx`; queue relink if outer fired |
| `Stream`, `Hold`, `InPlace`, `SwitchStream`, `SplitCapture` | take `parts[n]` out, call `ops.eval(parts, &mut Build, n)`, put back |

`set_fired(n)`: `fired = tx`; push to `commits` if `COMMITS`, to `memos` if
read-through, to `dispatch` if `LISTENERS`. Dispatch order is therefore
evaluation order, and a pulled node dispatches when it is pulled.

### 5.4 New nodes

```
j = 0; while j < created.len: ensure(created[j]); j += 1   -- the list grows during the walk
```

Nodes created during this transaction exist from this instant. Each runs
once, **after its dependencies, by pull, never in creation order**: a loop's
forward is created before its definition, so creation order is not
topological inside a scope that declares a loop (R1, R2b). Transaction zero
has no started nodes, so this phase evaluates everything the build closure
created: that is how `steps_with_current` and `switch_cell` fire at creation
and how a split fed at build has children before `build` returns.

### 5.5 Commit

```
1. for n in commits: ops.commit(parts[n], data[n])
     hold, accumulate: pending -> value;  in-place: f(pending.take(), &mut state)  (user code)
2. for n in memos:   ops.settle_memo(data[n])   -- only cells that stepped
     post_value present -> memo = OnceCell::from(post_value)  (post at t is pre at t + 1)
     post_value absent  -> memo.take()
3. for n in relinks: relink(n)                   -- reads committed outer values, after 1 and 2
     new = check(ops.inner(outer, pre)); if new != current inner:
       remove n from dependents(old); push n to dependents(new); deps slot = new
       path check upstream from new for n -> panic "switching closes a same-instant cycle"
```

A read-through cell that was marked and did not step keeps its memo (F4).
Commit holds `&mut Build`, and no sampled reference can live across `send`,
which takes `&mut self`, so clearing a `OnceCell` through `&mut` is sound
without `unsafe`.

### 5.6 Dispatch

```
for n in dispatch: list = mem::take(listeners[n])
                   for e in list: if e.flag.is_live(): (e.call)(&mut e.f, self, n)
                   list.retain(live); listeners[n] = list
```

A linear stream's listener takes the finished slot; a shared stream's
clones; a cell listener gets `&` the committed value (for a read-through
cell, the promoted memo or a fresh read). Ties within a node follow
registration order. A handle dropped inside a listener only clears a flag,
checked before each call. Listeners have no graph access.

### 5.7 Children

After the top-level instant's dispatch, if `levels[0]` is not empty:

```
frames = [0]
while let Some(&d) = frames.last():
    begin_instant(); depth = d + 1; levels[d + 1].clear()
    any = false
    for c in levels[d]: any |= ops.emit_child(parts[c], c)   -- next item of c's top iterator
                                                            -- -> fire_start(output(c), item)
    if !any: for c in levels[d]: ops.end_children(parts[c])  -- pop c's top iterator
             levels[d].clear(); frames.pop(); continue
    mark; evaluate; new nodes; commit; dispatch            -- a full instant, t ++ [n]
    if !levels[d + 1].is_empty(): frames.push(d + 1)        -- depth first
```

A capture fired at depth d pushes one iterator and registers in `levels[d]`.
Child n takes item n from every capture of the parent instant, so two splits
share child indices. A split fired inside its own children pushes a second
iterator; frames are last in, first out, so the top iterator always belongs
to the innermost frame. No recursion, so a long defer loop does not grow the
Rust stack.

### 5.8 Finish and poison

`finish` = the instant, then children, then `in_tx = false`. The build
closure is transaction zero: `begin`, push scope, closure, graph-id check,
pop scope (an open loop panics), `finish`, then trace the return value into
`roots`. Any panic, in user code, in a check, or in a listener, leaves
`in_tx` set, and every later entry reports `Poisoned`. There is no drop
guard, which is what RFD 7's abort targets need.

### 5.9 Memoized pull (`ensure`)

```
ensure(x):
  if mark[x] == tx:                                  -- in this transaction's order
      if order_done or pos[x] > cursor: return       -- ran already (START > every cursor)
      assert pos[x] != cursor                        -- "same-instant cycle through a dynamic read"
      match order[pos]: NOOP -> return; IN_PROGRESS -> panic; _ -> {}
      order[pos] = IN_PROGRESS; ensure_deps(x); eval_node(x); order[pos] = NOOP
  elif created[x] == tx:                             -- created during this transaction
      if done == tx: return
      assert pulling != tx                           -- "same-instant cycle among new nodes"
      pulling = tx; ensure_deps(x); eval_node(x); done = tx
  -- else: not affected at t; its slot is stale by stamp
```

Pull is entered from exactly two places: `prepare`, and the new-node phase.
The loop reaches a pulled entry as node 0, so the fast path has no check.

### 5.10 Post-instant values (`prepare`, `post`)

```
prepare(x):                                         -- mutable phase
  if prep_done == tx: return
  assert prep_enter != tx       -- "same-instant cycle through a post-instant read" (R10)
  prep_enter = tx; ensure(x)
  if fired[x] == tx:            -- an unstepped cell's post value is its value: no work
      ReadThrough: prepare each dependency; ops.compute_post(x)  -- post_value = f(post(inputs..))
      Loop:        prepare(target)
      SwitchCell:  prepare(outer); prepare(check(ops.inner(outer, post)))  -- may pull out of order
  prep_done = tx

post::<A>(x) -> &A:                                 -- shared phase, after prepare
  Hold:        fired ? pending : value           Constant: value
  ReadThrough: fired ? post_value : value(x)         Loop:     post(target)
  SwitchCell:  post(check(ops.inner(outer, post)))   -- outer unfired: its post is its value
  InPlace:     unreachable: a State has no stream view
```

`value::<A>` and `post::<A>` recurse at one type only; a switch reads its
outer's token through its monomorphized `inner` function, since
`value::<Cell<A>>` inside `value::<A>` would never finish monomorphizing.

### 5.11 Invariants every stage keeps

1. A node evaluates at most once per instant; a stream fires at most once; a
   cell steps at most once.
2. A committed value changes only at commit, so every read during
   evaluation is the pre-instant value.
3. A node runs only after its dependencies at this instant (order, pull, or
   the new-node phase).
4. The dependency graph is acyclic; watchers, cell reads, `depends` and the
   capture-to-output pair are not dependencies. Close, a switch's initial
   linking and relink check it; marking and pull panic if it is ever violated.
5. Every stored user value entered through `Accepts<T>::erase`.
6. No reference into the arena is held across a call that can allocate.
7. Collection never runs inside a transaction.

---

## 6. Answers

### a. Node representation, type erasure, and reading another node's slot

A node is an index into seven parallel vectors: `hot`, `relations`, `cold`,
`data`, `parts`, `ops`, `listeners`. `data` is what other nodes read: the
slot, the committed value, the memo. `parts` is what only the node's own
evaluation touches: its fused chain, its closures, `once`'s flag, a split's
iterators, `scan`'s state. Evaluating node N moves N's `parts` out (a
fat-pointer move, no allocation), calls `ops.eval(&mut parts, &mut Build,
N)`, and moves them back.

Inside `eval`, N reads input M through `Cx`:

```rust
fn take<A: 'static>(&mut self, m: u32) -> Option<A> {          // linear
    if hot[m].fired != tx { return None }
    slot_mut::<A>(&mut data[m]).take()        // Carrier::get_mut().downcast_mut::<Option<A>>()
}
fn cloned<A: Clone + 'static>(&self, m: u32) -> Option<A> { .. slot::<A>(&data[m]).clone() }
```

The borrow structure needs three things, all shown by the sketch:

1. N's parts are off the arena while N runs, so the closure can be handed
   `&mut Build` (construct needs it; `prepare` needs it to pull).
2. N's data stays in the arena: an accumulator reads its own committed value
   (`eval_accumulate` calls `value::<S>(me)`), and a loop reads a hold
   through a read-through cell. Taking the whole node out fails this case.
3. Borrows are sequential: read inputs (owned values out of a take or a
   clone, `&B` for a snapshot, released after `f`), then write N's own slot.

Every typed access is a checked downcast: a virtual `type_id` call and a
compare. A wrong type is an engine bug that panics; it can never read the
wrong memory. There is no `RefCell`, `Rc` or `unsafe` in the node graph; the
three sanctioned interior-mutability places stay the only ones (the memo's
`OnceCell`, the handle flag, the inbox).

**What each kind stores, and under which bound.** This table is why five
shapes suffice.

| Node | `data` | `parts` |
|---|---|---|
| input | `Slot` (`Accepts<A>`) | coalescing `F`: `Value` (`Accepts<F>`) |
| node, share, stream-loop definition | `Slot` (`Accepts<Event>`) | chain: `Value` (`Accepts<Self>`) |
| merge, or_else | `Slot` (`Accepts<Event>`) | two chains `Value`; `F` `Value`, or an engine `fn` pointer via `erase_send` |
| construct | `Slot` (`Accepts<B>`) | chain, `F`: `Value` |
| steps, steps_with_current | `Slot` (`Accepts<A>`) | none |
| hold, accumulate, constant, input_cell | `Cell` (`Accepts<A>` or `<S>`) | chain (input_cell: a `Stream<A>` token via `erase_send`), `F`: `Value` |
| accumulate_mut | `InPlace`: state `Value` (`Accepts<S>`), pending `Slot` (`Accepts<Event>`) | chain, `F`: `Value` |
| scan | `Slot` (`Accepts<B>`) | chain, `F`, state `S`: `Value` (state updated at evaluation; private, one evaluation per instant) |
| map_cell, lift | `ReadThrough`: `F` `Value`, `Memo` (`Accepts<B>` or `<R>`) | none |
| split | capture: none; output: `Slot` (`Accepts<Item>`) | chain `Value`; iterators `Stack` (`Accepts<IntoIter>`) |
| defer | capture: none; output: `Slot` (`Accepts<Event>`) | chain `Value`; events `Stack` (`Accepts<Event>`) |
| switch_stream | `Slot` (`Accepts<S::Event>`) | none |
| switch_cell, loop, never | none | none |
| listener | – | `Entry.f`: `Value` (`Accepts<F>`) |

### b. A chain compiled into one node's program

```rust
pub trait Source: Sized + 'static + sealed::Sealed {
    type Event;
    #[doc(hidden)] fn dependency(&self) -> Token;                        // the one dependency
    #[doc(hidden)] fn read_cells(&self, visit: &mut dyn FnMut(Token));   // snapshot, gate: reach
    #[doc(hidden)] fn pull<M: Mode>(&mut self, cx: &mut Cx<'_, M>) -> Option<Self::Event>;
    // adapters and materializers as in the skeleton
}
impl<A: 'static> Source for Stream<A>         { fn pull(..) { cx.take::<A>(self.token.index) } }
impl<A: Clone + 'static> Source for Shared<A> { fn pull(..) { cx.cloned::<A>(self.token.index) } }
impl<S: Source, B, F: Fn(S::Event) -> B + 'static> Source for Map<S, F> {
    fn pull(..) { self.source.pull(cx).map(&self.f) }
}
```

A materializer checks the chain's dependency and read cells, erases the
chain value itself (`<M as Accepts<Self>>::erase(Erase::Value(self))`), and
installs the node type's `&'static Ops`. At run time: one indirect call, one
downcast of the chain part, then static calls through every adapter, which
inline. `input.map(f).filter(p).snapshot(c, g).hold(b, 0)` is one node
(`claim2_chain_fuses_into_one_node`: four nodes in the graph, the three
adapters inside one). Linear against shared is a type in the chain, not a
branch. `merge` stores two chains in one node.

**Public change.** `Source` becomes sealed and `'static` with three hidden
required methods; `pull` names `Cx`, which has no public constructor, so
graph code cannot call it (doctest E0433). A downstream `impl Source` could
never have been materialized. `Node` becomes sealed with hidden
`node_token`, `pull_inner` (take or clone, for listeners and
`switch_stream`) and `const LINEAR: bool`.

### c. Stateful cells, read-through cells, and `&A` out of erased nodes

- **Stateful** (hold, accumulator, constant, `input_cell`): `CellValue<A>`;
  `value` is `&cell.value`. An in-place accumulator's value is its state.
- **Read-through** (`map_cell`, `lift`): `value` is
  `memo.value.get_or_init(|| f(value(input)..))`, through the node's
  monomorphized `ops.value`, which knows `A`, `B` and `F`.
- **switch_cell**: `value` is `value(check(ops.inner(outer, pre)))`, two
  chases and no memo. It never reads its own `deps[1]`, which exists only
  for marking.
- **Loop**: `value(target)`.

```rust
impl<M: Mode> Graph<M> {
    pub fn sample<C: CellRef>(&self, cell: C) -> &C::Value {
        let i = self.build.check(cell.cell_token());
        self.build.value::<C::Value>(i)          // &'a Graph -> &'a Build -> &'a Data -> &'a B
    }
}
```

Two samples compose; holding one across `send` is E0502 (doctest). The memo
changes only through `&mut` at commit. `claim3_…` checks the reference is
the same address twice and the function ran once.

### d. The transaction

Section 5. The phases: begin, sends, mark, evaluate, new nodes, commit,
dispatch, children, finish.

### e. The post-instant value of any cell

Two phases, because a post read may need to evaluate nodes: `prepare(x)`
takes `&mut Build`, evaluates what the post value reads, and computes
read-through post values; `post::<A>(x)` takes `&Build` and returns `&A` (5.10).

| Cell | post |
|---|---|
| hold, accumulator, `input_cell` | `fired == tx ? pending : value` |
| constant | value |
| `map_cell`, `lift` | stepped: `post_value`, computed in `prepare` from the inputs' post values and never written to the pre memo; else the memo |
| `switch_cell` | `post(post(outer))`: at a switch, the new inner; otherwise the current one |
| loop | `post(target)` |
| `State` (in-place and read-through over one) | none, and no operation can ask: no stream view exists |

Users of `post`: `steps`, `steps_with_current` (also at creation), and
`prepare` of a switch reading its outer. At commit the post value becomes
the memo (5.5), so `a_steps_view_value_is_promoted_into_the_memo_at_commit`
counts one call per step with a steps view and a cell listener on one cell.

Why no flag: a flag fixed at materialization goes stale when a loop is closed
later with a switch_cell (R3: 3 instead of 71 in one send order). `prepare`
dispatches on the kind at run time, so it follows the loop to the switch.

### f. Memoized pull, with no check on the fast path

5.9. The main loop runs the order blind; `ensure` uses marking's `pos`, the
loop's `cursor`, and the order entry; only nodes created during the
transaction carry `done`/`pulling`. `claim5_…` sends the same transaction in
both orders: one pull when the steps view runs before the new inner, none
otherwise, and the inner's function runs once either way.
`every_dynamic_case_evaluates_each_node_once_in_both_orders` counts the same
evaluations in both orders.

### g. `construct`: a program in the arena, mutating the arena

```rust
fn eval_construct<M, S, F, B>(parts: &mut [M::Carrier], b: &mut Build<M>, me: u32) {
    let [chain, f] = parts else { unreachable!() };
    let Some(a) = part::<S>(chain).pull(&mut Cx { b: &mut *b }) else { return };
    let graph = b.graph_id;
    b.push_scope();
    let out = part::<F>(f)(b, a);                  // may materialize, sample, close loops
    assert_eq!(b.graph_id, graph, "a build context was swapped for another");
    b.pop_scope();                                 // a loop declared here must be closed
    b.put_event(me, out);
}
```

It works without `unsafe` because the program is off the arena while it
runs; `materialize` appends to vectors that may reallocate, and nothing
holds a reference into them across the call (the loop re-reads `order[i]`
by index; parts go back by index); collection never runs inside a
transaction. A new node gets `created = tx`, joins its dependencies'
dependents **at creation**, and goes on `created`. Linking at creation is
harmless: marking is over, and evaluation follows the order and
dependencies. New nodes run after the main loop, by pull, because a node
the closure creates can depend on this construct's own output, which does
not exist until the closure returns. `claim4_…` sends in both orders: the
new hold picks up the other input's event at its creation instant, and
`sample` inside the closure reads the pre value.

`mem::swap` of two `&mut Build` (from a nested `Graph::build`) is safe code.
With no `unsafe` it cannot corrupt memory; the graph-id check turns it into a
panic.

### h. Loops

**Cell forward.** `cell_loop` creates a `Loop` node with no dependencies and
pushes it on the scope's open loops. `value` panics before close ("a cell
loop sampled before it is closed"). `CellLoop::close(b, d)` checks the loop
is open in the current scope, adds the dependency `d -> loop`, and walks
downstream from the loop looking for `d`; a path panics with its node list.
Afterwards the loop settles like a read-through cell and forwards `value`
and `post`. Stamps stay local, so a steps view of the forward works (R9).

**Stream forward.** `stream_loop` creates a `Stream` node whose program
panics if run and whose data is empty. `StreamLoop::close(b, chain)` creates
the slot (`Accepts<A>::erase(Slot)`), installs the chain as the node's own
program, adds the dependency, records read cells, and checks the path.

**The rule.** The dependency graph must be acyclic. A split's capture and
output have no dependency between them, so a cycle through a split or a
defer is never found. `snapshot`, `gate`, `sample`, a switch_stream's
selection and `depends` are not dependencies, so a loop through a hold read
that way has no cycle. A hold's steps view is a dependency, so
`c = hold 0 (merge ticks (map (+1) (steps c)))` is refused at close (F3,
`a_loop_through_a_holds_steps_view_is_refused_at_close`); the text diverges
on it. This replaces RFD 2's "every path passes through a hold, an
accumulator, a split or a defer".

**Scopes.** `open_loops: Vec<u32>` and `scopes: Vec<usize>` of offsets. The
build and every construct run push a scope; `pop_scope` panics if a loop
declared in it is still open.

**Switches.** `switch_cell`'s outer is a dependency: its post value at a
switch instant reads the new inner. `switch_stream`'s outer is not: SwitchS
at t uses the inner selected before t. The outer goes into the switch's
reach (collection) and the switch into the outer's `watchers`; marking that
reaches the outer queues the switch for relink and does not descend. Both
switches link their current inner at their **first evaluation**: the inner
selected before the instant, `ops.inner(outer, pre)`. So creating a switch
reads nothing, and a switch over a loop cell not yet closed works (R8). The
initial linking runs the same path check as a relink. A switch_stream also
queues a relink at creation, since its outer may step at the creation
instant; a switch_cell queues one when its outer fired.

**Relink.** At commit, after holds and memos (5.5). The path check walks
upstream from the new inner over dependencies looking for the switch; a
constructed inner has few nodes above it.

**One consumer of a linear inner** (RFD 4): `Node::LINEAR` marks
`Cell<Stream<A>>`. A second switch_stream on the same outer, or on a loop
forward and its definition, panics at construction or at close. A runtime
backstop covers selection through a switch_cell: linking a linear stream
that already has a switch_stream consumer (`cold.linear_consumer`) panics
and poisons.

### i. Children for `split` and `defer`

Two nodes each. The **capture** node depends on the chain's dependency, is
ordered at t, pulls the chain, pushes `Some(event.into_iter())` on its
`Stack` and registers in `levels[depth]`. The **output** node holds the
slot the user's `Stream<Item>` names; it has no dependencies, is started by
the child scheduler, and keeps its capture in reach. `defer` pushes
`Some(event)` and emits it once (`Option::take`). The scheduler is 5.7.

- **Shared indices:** child n takes item n from every capture of the parent
  instant (probe 4: `a`, `b`, `Z`).
- **Depth first, a split inside its own children:** iterator stack per
  capture, last in, first out (1, 10, 11, 2, 20, 21; R7: 0, 1, 2, 3).
- **No allocation:** `levels`, `frames` and the stacks keep capacity; the
  iterator allocates only what the user's `IntoIter` does.
- **Poison:** `in_tx` stays set across every child.

### j. Collection (stage 7, API depth)

**Roots:** `Graph.roots` (the build's return value, traced once), every
listener entry whose flag is live, every anchor whose flag is live.
**Reach of a node:** `deps`, `cold.reach`, and `ops.trace`, which visits the
committed values that can hold tokens: `CellValue<A: Trace>`, an in-place
state `S: Trace`, `scan`'s state. Memos are derived and not traced.
**Order:** clear every stream slot (`ops.clear_slot`), so an event holding a
token neither roots nor dangles; mark from the roots with the visit epoch,
skipping tokens that fail the graph or generation check; sweep: drop an
unmarked node's data, parts and listeners (user `Drop` runs outside any
transaction), clear `LIVE`, bump the generation, retire the slot at
`u32::MAX`, else push it on the back of the FIFO free list; prune every live
node's `dependents` and `watchers` with `retain`. **Automatic policy:**
after a transaction, collect when nodes allocated plus roots released since
the last collection exceed the live count; a dropped handle bumps a
per-graph counter its flag points to. `live_nodes` counts live nodes minus
node 0; a split is two nodes, documented.

### k. Handles and listeners

`Listener<M> { alive: Option<M::Flag> }`, `Anchor<M>` the same. `Drop`
clears the flag; `keep()` takes the flag out without clearing it (no leak,
no `mem::forget`); `unlisten()` is drop. The node keeps the other clone in
its `Entry`. `listen` stores `call_stream::<M, S, F>`, which reads through
`S::pull_inner` (take or clone); `listen_cell` calls `f(&value)` once at
registration, outside any transaction, then registers like `listen_steps`,
which stores `call_cell::<M, A, F>`. Both accept a `Cell` or a `State`,
since they read after commit.

### l. `Threaded`

No `unsafe`. `Graph<Threaded>: Send` is derived (4). The bounds are forced by
the code: a materializer cannot create a slot, a cell, a memo or a stack for
`T` without calling `<M as Accepts<T>>::erase`, so a missing bound is a
compile error inside the engine. The sketch shows it: removing `Accepts<A>`
from `StreamLoop::close` or `Accepts<Event>` from `node` fails the engine's
own build with E0277. Engine-made values that are `Send` whatever the user
types are (a token inside `input_cell`'s chain, `or_else`'s function
pointer) go through `Mode::erase_send`, whose bound is `T: Send` itself.
`Graph<Local>` is `!Send` (doctest E0277). Belt and braces: stage 8 adds a
`compile_fail` doctest per materializer, closer and `listen` with an `Rc`
event and an `Rc` capture, the staging judge's condition.

The bounds the skeleton lacks are public changes (8, item 5). They are
needed in any design: a slot keeps an event between transactions (a shared
slot, a stream nobody consumes, a deselected inner) and across a poisoning
panic, and a threaded graph can then be dropped on another thread.

### m. Allocation and the storage seam

**Allocates:** materialization (build and `construct`), `listen` and
`anchor`, a reused buffer growing to a new high-water mark, a dependents
list growing to a new length on relink (each list once), and a remote send
(on the sending thread, as RFD 6 sanctions).

**Never allocates:** `send`, `transaction`, marking, evaluation, pull,
prepare, commit, relink into an inner seen before, dispatch, children, and
collection in the steady state. `steady_state_transactions_do_not_allocate`
(counting allocator, its own test binary) runs 20,000 transactions through a
share, a fused chain, a merge, a lift, a cell listener and a switch_cell
toggling between two inners: 0 allocations.

**The seam** is `engine/store.rs` (`Store`) plus `engine/sched.rs`
(`Sched`), and the erasure point `Accepts::erase`. Everything else addresses
nodes by `u32` through their methods. The bounded tier (RFD 7, after the
engine works) replaces `Box` carriers with handles into caller-provided,
size-classed slots. Placing a value in raw bytes needs E2's four `unsafe`
lines, confined to one module; `Send` stays derived because placement still
happens inside `Accepts::erase`, where `T: Send` is known. Miri under Stacked
and Tree Borrows gates that module, with fast-first's negative control kept
as a test that must fail under Miri. `construct` can then run out of slots:
`Exhausted`, a major version.

### n. Where the build context lives

`Build<M>` is the core, and `Graph<M>` owns one. The build closure and every
construct closure receive `&mut Build` borrowed from the graph's own field.
`Build` has no lifetime parameter and no public constructor. `Graph::build`
is 5.8. Two samples in graph code borrow `&Build` and compose.

### o. Stages, so that stage 1 is never rewritten

Section 7. Stage 1 carries four structures that look early: the data/program
split, every marked node ordered, the new-node phase by pull, and the
carriers with all five shapes. Without them stages 2, 3, 5 and 6 each
rewrite the evaluation loop or the erasure.

---

## 7. Stages

Each stage lands in reviewable commits, is oracle-tested against GHC with
random programs in both send orders and under the shuffle affordance
before the next begins (stages 1 to 6), and keeps every earlier test green.
"Files" names what the stage creates or touches in `bough/src`.

| Stage | Adds | Files | Oracle clauses |
|---|---|---|---|
| 1 | first-order core, fusion | mode, token, source, cell (`sample`), build, graph, trace, engine/{mod, store, sched, tx, pull, nodes/stream, nodes/cell} | MkStream, Never, MapS, Filter, Snapshot, Merge, Hold, Constant |
| 2 | cells | cell, lift, token (`State`), source (accumulate, accumulate_mut, scan), engine/{pull, nodes/read, nodes/cell} | MapC, Apply, Updates, Value, accum |
| 3 | loops | build (loops, closers), engine/loops | fixed-point loops |
| 4 | children | source (split, defer), engine/{children, nodes/split} | Split (F7), defer |
| 5 | switches | cell (switch_cell, switch_stream), engine/{nodes/switch, tx relink, pull prepare branch} | SwitchC (F6), SwitchS |
| 6 | construct | source (construct), engine/nodes/construct | Execute |
| 7 | collection, API depth | engine/collect, graph (anchor, policy, try_), trace | – (own property tests) |
| 8 | the I/O edge, API depth | graph (Remote, pump, waker), slot, engine/inbox, error | – (fold law vs oracle) |

### Stage 1: the first-order core and chain fusion

- `mode.rs`: `Carrier`, `Erase` with **all five shapes**, `Accepts::erase`,
  `Mode::erase_send`, `FlagOps`.
- `engine/`: `Hot` (32 bytes, asserted), `Relations`, `Cold` (every field),
  `Data` (every variant), `Ops` (every entry, defaults no-op), `NodeOps`,
  `Entry`, `Cx`, checked downcasts; `Store` with the seven vectors and node
  0; `Sched`.
- The transaction: begin, `fire_start` with double send and coalescing,
  mark (watchers hook present, unused), backwards evaluation, **the
  new-node phase with `ensure`** (transaction zero needs it), commit,
  dispatch, finish, poison.
- `source.rs`: sealed `Source` with `dependency`, `read_cells`, `pull`;
  sealed `Node` with `node_token`, `pull_inner`, `LINEAR`; `map`, `filter`,
  `filter_map`, `map_to`, `snapshot`, `gate`, `once`; `hold`, `node`,
  `share`, `merge`, `or_else`.
- `build.rs`: `input`, `input_coalescing`, `input_cell` (and coalescing),
  `constant`, `never`, graph ids (a load and a store where there is no
  compare-and-swap).
- `graph.rs`: `build`, `build_threaded`, `send`, `transaction`, `listen`,
  `listen_cell`, `listen_steps`, `sample` (on `Cell`; stage 2 widens them to
  `CellRef`), `live_nodes`, `set_shuffle_seed`; the `statistics` feature's counters (evaluations,
  pulls, relinks per phase).
- Tests: `claim1` to `claim3` shapes; the counting-allocator test; the
  compile_fail doctests (chain used twice, `Graph<Local>: !Send`, `Rc`
  capture and `Rc` event in `Threaded`, `Cx` unnameable, sample across
  send); a `Threaded` graph moved to a thread; first-order random programs
  against GHC.
- Benchmarks in `bough-bench`: the shallow shape and its share variant
  (criterion, with a hand-written baseline), the frame shape (1000 inputs,
  10,000 nodes), and `iai-callgrind` per phase.
- CI targets from the first commit (RFD 7): `thumbv7m-none-eabi`,
  `thumbv7em-none-eabihf` and `thumbv6m-none-eabi` without `std`,
  `wasm32-unknown-unknown` with and without it, and the 1.85 toolchain.
- **Exit:** oracle green; 0 allocations; the share shape within the bar with
  a 55 ns payload. The sketch sits at about 2.5 times the baseline there
  (88 ns + 55 against 56). If stage 1 does not improve on that, it adds a
  store-only evaluation path first: chain, hold and merge programs take
  `&mut Store` through a disjoint borrow instead of taking their parts out,
  plus a one-dependent fast path in `mark`. Neither touches the protocol.

### Stage 2: cells

- `ReadThrough` settle in order; `memos`; `Memo` with its post value;
  `settle_memo` promotion; `map_cell`; `lift` 2 to 6 by one macro with the
  `Output` join; `accumulate` (reads itself); `scan` (state in parts);
  `accumulate_mut` returning `State<S>` (**decide before stage 2**, §8 item
  6); `CellRef`; `steps`, `steps_with_current` with `prepare` and `post` for
  holds and read-through cells (the switch branch lands in stage 5 into the
  same `match`).
- Tests: F4 (`a_marked_cell_that_did_not_step_keeps_its_memo_and_stays_quiet`),
  promotion counts, `State` compile_fail doctests (steps on a `State` and on
  a lift over one), the accumulator reading itself, `listen_cell` on a
  `map_cell` (RFD 2's flagship).

### Stage 3: loops

- `Kind::Loop`, `cell_loop`, `CellLoop::close`; `stream_loop`,
  `StreamLoop::close` (slot at close, `Accepts<A>`); `state_loop`; scopes;
  path checks; the `CellLoop` doc comment's rule text.
- Tests: counter through a snapshot, the accumulator reading itself through
  a read-through loop, F3 refused, loop left open, R9, the `sodium-rust#52`
  shape (a cell held through a loop lifted with something upstream of
  itself), random loops through holds against the fixed-point oracle.

### Stage 4: children

- `SplitCapture`, `SplitOutput`, `Stack`, `levels`, `frames`, the iterative
  scheduler, `emit_child`, `end_children`; `defer`.
- The oracle's F7 patch lands first.
- Tests: two splits share indices, depth first with a split inside its own
  children, R7, random programs with splits and defers inside loops.

### Stage 5: switches

- `switch_cell` settle, initial linking, relink, the switch branch of `prepare`;
  `switch_stream` with the watcher, initial linking, creation relink, relink;
  `Node::LINEAR` one-switch check and the runtime backstop; the upstream
  relink check.
- The oracle's F6 patch lands first.
- Tests: `claim5` with pull counts, R3, R4, R5, R8, R10, R10b, both
  switch_stream probes, a switch to a quiet inner, steps at creation.

### Stage 6: construct

- `construct`, scope push and pop around the closure, the graph-id check,
  construct inside construct.
- Tests: `claim4`, R1 and R1c, R2 and R2b, R6, a switch_cell created after its
  outer switched (F6), random programs with construct bodies (loops inside
  bodies stay hand-written).

### Stage 7: collection (API depth, Q1 a)

- Tracer internals, `ops.trace`, `ops.clear_slot`, mark, sweep, prune,
  FIFO free list, generations, retirement, anchors, roots, automatic
  policy, `collect_garbage`, `set_collect_after_every_transaction`,
  `stale_operations`, the `try_` variants for token errors, the debug-dump
  feature.
- Tests: safe-first's collection shape (a hold named only inside a
  constant's value survives; an unrooted hold is collected; its token is
  stale; a later send through the pruned dependents works), build-drive-
  drop-collect-compare with `live_nodes`.
- `#[derive(Trace)]` in `bough-derive` lands here, when the tests need it.
- Enough to answer: does `Trace` on committed values plus `depends` root
  everything real programs need; do the error enums fit.

### Stage 8: the I/O edge (API depth)

- The inbox (standard mutex, or `critical-section`), `Remote::send` and
  `transaction`, units as `(Token, Box<dyn Any + Send>, fn)` so a unit
  needs no mode, `pump` (slots in connection order, then units in arrival
  order), `InputSlot` with its fold, `connect`, `set_waker`, the
  `InsideTransaction` guard under `std`, poison mirroring, every `try_`
  variant and error enum; the per-materializer `Threaded` compile_fail
  doctests.
- The fold law property test: random event sequences and random partitions
  into runs, against the oracle fed the folded runs.

---

## 8. Public API changes (spike findings)

Each is a finding; its commit says why. Code written for `Local` sees none
of 1 to 5; code generic over the mode adds item 5's bounds, as it already
does for `hold`'s.

1. **`Source` is sealed and `'static`, with three hidden required
   methods,** `dependency`, `read_cells`, `pull`. Fusion needs a typed pull
   through every adapter, and a boxed program is `'static`. `pull` takes the
   unnameable `Cx`. A downstream `impl Source` could never be materialized.
2. **`Node` is sealed, with hidden `node_token`, `pull_inner` and `const
   LINEAR: bool`.** Listeners and `switch_stream` read a node the way its
   type says (take or clone); the one-switch rule needs to know linearity.
3. **Impl bounds:** `impl<A: 'static> Source for Stream<A>`, `impl<A: Clone
   + 'static> Source for Shared<A>` (and `Node`), and the snapshot and gate
   cell value `'static`. Checked downcasts need `'static`; every token
   constructor already requires it.
4. **`Mode` gains hidden `Carrier`, `erase_send` and `Flag: FlagOps`;
   `Accepts<T>` gains the supertrait `Mode` and a hidden `erase`;** hidden
   `Erase`, `Carrier` and `FlagOps` types. This makes `Graph<Threaded>:
   Send` a compiler fact and retires `unsafe impl Send`. `Accepts` could
   not be implemented downstream anyway (fact 4).
5. **Added `M: Accepts<…>` bounds:** `input` and `input_coalescing`
   (`A`: the input's slot is created at `input`), `node`, `merge`, `or_else`,
   `defer`, `accumulate_mut` (the event), `scan` and `construct` (`B`),
   `split` (`IntoIter` and `Item`), `switch_stream` (`S::Event`),
   `StreamLoop::close` (`A`). A slot or a pending event outlives a
   transaction, and a poisoned graph drops it wherever it is dropped.
   Against the skeleton, a `Threaded` graph holding `Rc` events type-checks
   today (fast-first's probe). `input` and `input_coalescing` are new
   relative to the other proposals, which created the slot unchecked; an
   input of a non-`Send` type was already unusable in `Threaded`, since
   `send` requires the same bound.
6. **`State<S>`, decided by Zefira before stage 2.** `accumulate_mut`
   returns `State<S>`, a `Copy` token with no stream view, because its new
   state does not exist until commit. A sealed trait `CellRef` (`Cell<A>`
   and `State<A>`, with `type Value`) is what every cell-reading operation
   accepts:
   - `sample` on `State`; `Graph::sample`, `try_sample`, `listen_cell`,
     `listen_steps` and their `try_` forms take `C: CellRef`;
   - `snapshot` and `gate` take `C: CellRef`, so `Snapshot<S, C, F>` and
     `Gate<S, C>` carry the token type;
   - `map_cell` on a `State` returns a `State`;
   - `Lift` gains `type Output`: `Cell<R>` when every input is a `Cell`,
     `State<R>` when any is a `State` (a hidden kind join);
   - `switch_cell` on `Cell<State<A>>` returns `State<A>`;
   - `Build::state_loop` with `StateLoop::close` taking any `CellRef`.
   `steps` and `steps_with_current` stay on `Cell` alone. Why: the
   build-time panic RFD 4 describes cannot be complete. A flag set at
   materialization goes stale when a loop is closed later, and a
   `switch_cell` can select an in-place accumulator at run time; the
   judges found both. RFD 4 already names this split as the answer "if the
   panic bites". The sketch compiles it, `lift` join included, on 1.85
   (`an_in_place_accumulator_is_a_state_that_every_cell_reader_accepts` and
   two E0599 doctests). **Fallback if declined:** a post-less flag set at
   materialization and recomputed downstream of a forward at close, a
   build-time panic on a steps view over a flagged cell, and a poisoning
   run-time panic when a switch_cell selects a flagged cell while a steps
   view reads it.
7. **Invisible:** `Once` gains a private `done` field; `Build`, `Graph`,
   `Listener` (`Option<M::Flag>`), `Anchor`, `Tracer` and
   `RemoteTransaction` get their real private fields.
8. **Additions RFD 1's test affordances need, missing from the skeleton:**
   `Graph::set_shuffle_seed(Option<u64>)` (the seeded order shuffle, a
   runtime setting users' tests can call), a `debug-dump` feature with
   `Graph::dump`, and under the existing `statistics` feature a
   `Graph::statistics()` reader.
9. **Doc text:** `Build::cell_loop`'s and `CellLoop`'s loop rule changes to
   the dependency-graph rule (F3).

## 9. RFD text changes (no signatures)

- **RFD 5:** read-through cells are ordered and settle without user code;
  cell listeners run for every cell that **stepped**, and only stepped
  read-through cells clear or promote their memo (F4); nodes created during
  t are linked at creation and run by pull after the main loop; a switch
  links its inner at its first evaluation; the relink check runs at a
  switch's initial linking and at relink, walking upstream from the new inner;
  a cycle through a post-instant read panics and poisons; dispatch order is
  evaluation order, a pulled node at pull time.
- **RFD 2, glossary "Loop":** the dependency graph must be acyclic except
  through `split` and `defer`; cell reads, a switch_stream's selection and
  `depends` are not dependencies (F3).
- **RFD 4:** switch_stream's outer is reach plus a watcher, not a
  dependency; `State<S>` (if accepted) replaces the build-time panic; with a
  steps view, a read-through function runs once per step, not twice;
  `scan`'s private state updates during evaluation, unobservable for the
  reason `once`'s flag is.
- **RFD 4 or 5:** a switch created at t starts from the outer's committed
  value (F6).

---

## 10. Open risks only the oracle can settle

1. **Switch creation inside construct.** The engine links a switch created
   at t to the outer's pre-instant value and relinks at commit if the outer
   stepped at t. Patched `SwitchC` (F6) and unchopped `SwitchS` agree with
   that on the probes; the combinations (outer stepped before, at, or after
   t; inner created at t; nested switches created together) only random
   construct programs cover.
2. **Post-value promotion.** The engine assumes post at t equals pre at t + 1 for
   every read-through composition. A wrong promotion shows only as a stale
   value one instant later, in a later snapshot or sample.
3. **The loop rule's boundary.** Acyclic dependencies should accept exactly
   the loops the fixed-point oracle answers and refuse the ones the text
   diverges on. Three probes back it (counter, F3, switch_stream selection).
   Loops mixing switch_stream selection, split and construct are untested.
4. **Fixed point equals the semantics** for loops through switch_stream's
   selection and through split. Fact 2 covers holds; `SwitchS.hs` shows one
   more case.
5. **Past events of a switch_stream created at t.** `SwitchS` has no `t0`;
   its events before t exist in the text and never in the engine. The
   engine assumes no consumer created at or after t can observe them.
6. **Settle is exact.** "Stepped iff a dependency fired" must match
   `knit` for `Apply`, `MapC` over a switch that switched to a quiet inner,
   and a loop node over a switch at its creation instant.
7. **Order independence.** Pulls move dispatch and evaluation order; the
   shuffle moves them further. Values must not change. Only property tests
   under the shuffle, compared with the oracle, show it.
8. **Coalescing inputs and double sends** against the oracle's schedule
   folding, and the input-slot fold law (stage 8).
9. **Child indices are not compared** (2.2). A wrong split of events across
   child instants that keeps per-node order and values would pass.

## 11. Other risks

1. **Headroom on the share shape:** about 2.5 times the baseline in the
   sketch. Stage 1's exit criterion and its two internal fixes address it.
   The frame and UI shapes are not measured yet.
2. **One box per stored part.** A merge node owns four carriers. Pointer
   chasing on the frame shape is unmeasured; a size-classed arena for
   carriers is the bounded tier's work anyway.
3. **Relink check cost on the UI shape:** upstream from each new inner at
   every screen switch. Measure in stage 5.
4. **Recursion.** `ensure` and `prepare` recurse over the pulled region;
   `value` and `post` recurse through chains of read-through cells, so a
   10,000-deep `map_cell` chain would overflow. Children, marking and path
   checks are iterative. Make `ensure` iterative if a test bites.
5. **`State<S>` weight.** Error messages through the `lift` join name
   hidden types. Zefira decides before stage 2; the fallback is specified.
6. **The bounded tier needs `unsafe`** for inline erased storage (E2): four
   blocks, one module, a later major version.
7. **Graph ids on a Cortex-M0** use a load and a store; two graphs built
   concurrently from an interrupt handler could share an id.
8. **Two `&mut b` in one call** (`closer.close(b, cell.switch_stream(b))`)
   is E0499; users write a `let`. Documentation, not engine design.

---

## 12. The compile experiment

Crate `design/final-sketch/`: `#![no_std]` over `alloc`,
`#![forbid(unsafe_code)]`, edition 2024, `rust-version = "1.85"`, no
dependencies. About 3,400 lines of library, comments included, and 1,110 of
tests. Raw output: `results/verification.txt`.

| Claim | Test |
|---|---|
| 1. Erased arena, linear take and shared clone | `claim1_erased_arena_linear_take_and_shared_clone`: a non-`Clone` event through a linear accumulator leaves the input slot empty; one shared node feeds a hold and a stream node and keeps its event |
| 2. A fused chain through the hidden `Source` methods | `claim2_chain_fuses_into_one_node`: `map.filter.snapshot.hold` is one node; the snapshot reads the pre value |
| 3. `sample` returns `&A` through a `OnceCell` memo | `claim3_sample_returns_a_reference_from_a_read_through_memo`; doctest E0502 |
| 4. Node creation mid-evaluation | `claim4_construct_creates_nodes_while_a_closure_runs`, both send orders |
| 5. switch_cell post-instant pull | `claim5_switch_cell_post_instant_pull_in_both_send_orders`: 70, one pull or none, the inner runs once |
| Compiler-derived `Send`, no `unsafe` | `a_threaded_graph_is_send_without_unsafe_and_runs_on_another_thread`; doctests: `Graph<Local>: Send` E0277, `Rc` capture E0277, `Rc` event through `node` E0277, `Rc` event through `StreamLoop::close` E0277 |
| Post-value promotion | `a_steps_view_value_is_promoted_into_the_memo_at_commit` |
| F4 | `a_marked_cell_that_did_not_step_keeps_its_memo_and_stays_quiet` |
| `State<S>` | `an_in_place_accumulator_is_a_state_that_every_cell_reader_accepts`; doctests E0599 twice |
| R1 to R10 | `r1_…` (with R1c), `r2_…`, `r2b_…`, `r3_…`, `r4_…`, `r5_…`, `r6_…`, `r7_…`, `r8_…`, `r9_…`, `r10_…`, `r10b_…` |
| switch_stream | `…relinks_on_a_selector_step_while_the_old_inner_is_quiet` (a, Y, Z), `…loop_through_its_selection` (1, 2, 3, 4) |
| Loops, children | F3 refused, loop left open, counter, an accumulator reading itself through a read-through loop, shared child indices, depth first |
| Allocation | `steady_state_transactions_do_not_allocate`: 20,000 transactions, 10,000 relinks, 0 allocations |

```
$ cargo test                      # rustc 1.94.1
claims: 10 passed; dynamic: 20 passed; alloc: 1 passed; doctests: 9 passed (compile_fail)
$ cargo +1.85 test                # the same counts, smoke included
$ cargo test --features smoke --test smoke          # every node kind in one graph: 1 passed
$ cargo clippy --all-targets --features smoke       # no warnings
$ cargo build --release --no-default-features --features smoke --target thumbv7m-none-eabi   # ok
$ cargo build --release --no-default-features --features smoke --target thumbv6m-none-eabi   # ok
$ nm -C …/thumbv6m-none-eabi/release/libfinal_sketch.rlib | grep -cE 'nodes::(eval_|…)'  # 69
$ grep -rn unsafe src | grep -v '//'
src/lib.rs:128:#![forbid(unsafe_code)]
```

Not in the sketch, each with its mechanism above: collection, anchors, the
inbox, `Remote`, `pump`, `InputSlot`, the `try_` variants, coalescing
inputs, `input_cell`, `never`, `gate`, `filter_map`, `map_to`, `scan`,
`defer`, `lift` for three to six, `state_loop`, `switch_cell` over
`Cell<State<A>>`, the one-switch check, the shuffle, the `statistics`
reader, and the store-only evaluation path.

Each `compile_fail` doctest was also built as an example to confirm its
error is the intended one (`results/compile-fail.txt`). Removing
`Accepts<A>` from `StreamLoop::close`, or `Accepts<Event>` from `node`,
fails the engine's own build with E0277.

Rough costs, trivial payloads, release, one x86 machine, six runs over two
sessions with one run under load discarded; information, not the bar
(`cargo test --release --test cost -- --ignored --nocapture`). The
semantics-first sketch ran the same tests on the same machine:

| Shape | final sketch | semantics-first sketch |
|---|---|---|
| shallow, three adapters into a hold | 58 to 61 ns per transaction | 56 to 62 |
| shallow with a share | 85 to 93 | 82 to 88 |
| line of 1000 shared nodes | 31 to 33 ns per node | 31 |
| fan-out to 1000 holds | 33 to 41 ns per node | 32 |
| switch_cell toggle, relink and listener | 141 to 147 ns per transaction | – |

The carriers cost little on the shallow shapes and up to a tenth on the
fan-out, where each hold downcasts its chain and its cell. The Rust judge
measured fast-first at about 33 ns on the shallow shape; that gap is the
target of stage 1's two internal fixes.

---

## Addendum, 2026-09-24, after the engine was built

_Added after the spike. The brief above is kept as every implementation
agent followed it. Where the engine had to leave it, the departure is listed
here with its finding; the findings themselves are in the spike's note,
`2026-09-24-engine-feasibility-spike.md`, beside this one._

- **The scratch files it cites are not kept**: `design/`, the final sketch,
  the three proposals, the three judgments and the reviewers' probes. The
  engine's own tests re-establish each claim they made, and the GHC programs
  behind the engine's fixed tests are in the `bough` repository under
  `bough-oracle/haskell/probes`.
- **5.5, relink.** Checking each switch as it moves refuses a legal program in
  which two switches reverse a dependency between them in one instant (F46).
  The engine moves every queued switch first and checks each on the final
  graph. The one-consumer claims on linear streams are all released before any
  is made (F47). A `switch_stream`'s first link runs its inner at that instant
  (F48).
- **5.7, children.** The sketch kept calling `next()` on an iterator after it
  returned `None` whenever a longer split shared the instant (F41); the engine
  drops an iterator at its first `None`. `frames` is always `[0, 1, …, depth]`,
  so a counter replaced it.
- **5.10, prepare.** The re-entry stamp was not enough. A read of a
  `switch_cell` before its first link, and relink's read of a new selection,
  overflowed the stack on a cycle (F19, F56, F57). Each read now carries
  Brent's cycle detection over the `switch_cell`s it passes and panics, which
  poisons.
- **6.g.** A build context swapped through a nested `Graph::build` is caught
  first by the nested build's own graph-id check (F60).
- **6.j, collection.** The engine collects when the next transaction opens,
  not after one: collecting after one frees an input a `construct` built and a
  listener just delivered, before I/O code can anchor it (F65). The automatic
  trigger compares with the live count the last collection left (F64).
  `anchor` takes any `&T: Trace` (F67). A capture reached only through a
  switch's selection, and `map_to` of a token, need a `depends` declaration
  (F62).
- **6.l and 12.** Without `Accepts<A>` on `StreamLoop::close` the engine fails
  to build with E0271, not E0277.
- **7, stage 1's exit.** The store-only evaluation path made the share shape
  slower under callgrind (384 to 399 instructions per transaction) and was
  reverted; the tighter marking loop was kept. The share shape runs at 2.47
  times its baseline (F24).
- **7, stage 8.** The edge lives in `Build`, since `connect` takes a `Build`;
  both kinds of unit are one boxed closure; `RemoteTransaction` has a lifetime;
  input slots need `std` or `critical-section`, and `Remote` that and pointer
  atomics (F70, F71, F81). The guard is armed around graph code, not for the
  whole transaction (F74).
- **8, item 5.** The `Accepts` bounds landed where listed, and on `split` for
  both its iterator and its item.
- **11, risk 4.** `ensure`, `prepare`, `value` and `post` still recurse; no
  test bit.
