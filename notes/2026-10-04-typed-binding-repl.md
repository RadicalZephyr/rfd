# What a typed binding REPL found in construct

_2026-10-04. Findings from the probe the binding REPL handoff asked for:
`bough-repl`, a sibling crate on bough's
[`claude/probe-crate-implementation-m4utf9`](https://github.com/RadicalZephyr/bough/tree/claude/probe-crate-implementation-m4utf9)
branch, `7c47738..2b72e30`, built and tested with rustc 1.97.0 in debug
and release. Mema's central move is changing a running program without a
rebuild, and this is that move at the smallest size we could make it. The
RFDs are untouched; this note feeds them later._

## What ran

A REPL over one running graph, reading commands from stdin:

```
input x 0        def y add x 3     def y x
set x 5          watch y           graph
tick t 1000
```

A binding is a name with a fixed `Type` and a `Node`. `Type` is a
data-free tag, `Int`, `Bool` and later `Str`, and `Node` has the same
arms, each a concrete `Cell<i64>`, `Cell<bool>` or `Cell<String>`, with
no erasure. The REPL checks a command against the tags and the
namespace, and only then sends it to the graph, where a `construct`
closure matches on the arms to wire the cells. The registry is thirteen
entries under twelve names, each with a hand-written signature.

It's a sibling crate rather than an example, because every completion
criterion is a scripted test that drives the REPL, and those want a
library with integration tests of its own. Twenty-seven tests run each
step to its criterion: the diamond, rebinding, both FizzBuzz demos under
a timer that never restarts, the sentinel demo again under sixteen
shuffle seeds, the real binary against the wall clock, and three that
drive the graph API directly.

## The short answer

`construct` carries live rewiring of a typed graph, and a rebinding is
cheap once the binding exists: one send, one transaction, glitch-free,
with dependents following and the old definition collected. The ceremony
is elsewhere. Getting anything built after `build` takes a command
reified as data, a construct to run it and a listener to bring the
result back. And the engine refuses a bad rewiring only by poisoning the
runtime, so the dynamic layer has to refuse it first.

## (a) The ceremony of one live rebinding

A binding's node is a `switch_cell` over a hold of its current
definition. The hold is fed by a construct of the binding's own, over an
input of definitions:

```rust
fn bind<A: 'static>(
    b: &mut Build,
    first: Cell<A>,
    cell: fn(Node) -> Cell<A>,
) -> (Cell<A>, Input<Def>) {
    let (redefinitions, redefine) = b.input::<Def>();
    let definitions = redefinitions.construct(b, move |b, def| cell(def.build(b)));
    let current = definitions.hold(b, first);
    (current.switch_cell(b), redefine)
}
```

That's four nodes a binding, besides its definition's own, and a test
counts them: `def k 5` is five live nodes, the constant and the four.
With that in place a rebinding is one send on the I/O side, after the
checks:

```rust
pub fn redefine(&mut self, binding: Input<Def>, def: Def) {
    self.runtime.send(binding, def);
}
```

The construct builds the new definition, the hold takes it, and the
switch moves to it at commit, all in the one transaction. Dependents name
the switch and never see the definition behind it.

What a rebinding carries is the part that's work to write, not to run. A
closure only gets a `Build` from an event, so the command travels as
data, a function pointer and the argument tokens:

```rust
pub enum Def {
    Apply(Wire, Vec<Arg>), // Wire = fn(&mut Build, &[Node]) -> Node
    Alias(Arg),
}
```

A new binding pays more, since its tokens have to come back out to the
REPL. The build makes one input of commands and a construct over it, and
a listener leaves what each run made in a slot for the caller to take
once `send` returns:

```rust
pub fn make(&mut self, command: Command) -> Made {
    self.runtime.send(self.commands, command);
    self.made
        .borrow_mut()
        .take()
        .expect("bough-repl: the construct fires once per command")
}
```

The closure anchors what it hands out with `b.anchor`, or the collection
after the unit frees it. All of this is `graph.rs`, 188 lines with its
docs, and it's written once. It's synchronous only because the REPL owns
the `Runtime` and `send` runs its listeners before it returns. A front
end that holds a handle instead gets its tokens a pump later.

## (b) Where the API fought

### Only an event reaches a build context

Everything above follows from it, and RFD 2 means it to: a construct is
the one way to add logic after build. What surprised us is how little
stands between that rule and an `eval`. A construct over a stream of
`Box<dyn FnOnce(&mut Build) -> R>` runs whatever I/O code sends it, and
our `Def` is that closure defunctionalized. We kept the data form, since
the REPL checks a definition before it sends it, but Mema will want the
closure.

### The engine's refusals poison the runtime

Bough refuses both of the bad rewirings that checks 3 and 4 exist for,
and either refusal poisons the runtime. Two tests drive the graph API
past the REPL's checks. A cycle is found when the switch moves, and the
panic names nodes by number:

```
bough: switching closes a same-instant cycle: node 10 (SwitchCell) -> node 12 (ReadThrough)
-> node 16 (SwitchCell) -> node 18 (ReadThrough) -> node 10. The cell a switch selects
may not depend on the switch at the same instant
```

A definition of another type can't even be said to the engine. The hold
is a `Cell<Cell<i64>>`, so the construct recovers the concrete cell from
the `Node`, and the arm it didn't expect is an `unreachable!` in graph
code. After either panic, every send is `Err(Poisoned)`. So the REPL
keeps its own copy of the dependency graph at the level of names, walks
it before every redefinition, and checks types against tags it keeps
beside the cells. It names a cycle in the user's words,
`x -> z -> y -> x`, which the engine can't.

The same goes for the user's functions. A panic in a lift's closure
poisons too, so every registry function is total: arithmetic wraps,
since overflow panics in a debug build, and `mod 0` is 0. A live
environment whose users write the functions can't promise that.

### A redefinition is a step

A switch steps whenever it moves, to an equal value too, and a step to
an equal value is a step. So every watcher downstream of a redefinition
prints at once, at the redefinition's own instant, not at the next tick
as the handoff expected. With `a` at 2, redefining `b` from `add a a` to
`mul a a` prints `c = 8` again. For live coding it's the behaviour we'd
want: you redefine and see the result. It also means a redefinition
notifies everything downstream whether or not anything changed, and a
watch can't tell why it fired.

### Smaller things

- Listeners in one transaction run in an order RFD 2 says not to rely
  on, so the harness compares each step's lines sorted, and the sentinel
  demo runs under sixteen shuffle seeds.
- The handoff's `Node` is also the name of Bough's bound for `listen`,
  and the glossary's word for a graph node. We kept it, but they're
  different things.
- A catch-all arm for the impossible pairs, as `InputToken::send` has,
  hides a missing arm from the compiler. (d) has the case.

### What didn't fight

A construct built inside another construct's run works at the same
instant, so the root construct builds each new binding's own. A hold of
a token, `switch_cell` over it, and `#[derive(Trace)]` on the enums all
just worked. The timer is a thread with a `RemoteIo`, and the driver is
a channel, a `Wake` that sends to it, and a loop that pumps on a wake:
the binary's `main.rs` is 56 lines with its docs. And `depends` was
never needed, for the reason under the open questions below.

## (c) Whether the cell-of-cells shape held

It did, on every count we could test:

- Dependents follow a redefinition without a new `watch`, through
  aliases too.
- Each tick prints one line per watch, the same under sixteen shuffle
  seeds, with no torn or duplicated value, while `out` is redefined
  twice under one running timer.
- A definition left behind is collected. A hundred redefinitions leave
  the live-node count where it started.
- Several bindings' redefinitions can be one transaction, since each
  binding has its own input, and a watcher downstream steps once, to
  what they make together.

We considered two other shapes and didn't build them. Receiving a new
definition's token at the edge and sending it to the binding's own
`input_cell` of cells is "receive, then wire": two units per
redefinition, the token anchored between them, and a window where the
definition exists and nothing uses it. One construct for every
definition, with each binding's hold filtering the shared output for its
own, runs every binding's filter on every definition. A construct per
binding costs four nodes a binding and nothing per definition.

Inputs, ticks included, aren't rebindable, and their node is the input
cell with no switch. An input's identity belongs to the I/O code that
sends to it, a timer thread here, and redefining one would leave that
sender sending to a node nothing reaches.

## (d) What adding `Str` cost

Adding the arms alone, `Str` to `Type`, `StrCell` to `Node` and an arm to
each of the two enums that follow them, `Literal` and `InputToken`, broke
the build at seven matches. Five more places needed the type, and the
compiler didn't say:

| Place | File | Did the compiler flag it? |
|---|---|---|
| `Type`'s `Display` | `ty.rs` | Yes |
| `Literal::ty`, `constant`, `input` and `Display` | `ty.rs` | Yes, all four |
| `bind_node`, the typed dispatch to `bind` | `graph.rs` | Yes |
| `watch`'s listener | `repl.rs` | Yes |
| `InputToken::send` | `ty.rs` | No: its catch-all for impossible pairs took the new pair |
| The literal syntax, `"Fizz"` | `ty.rs` | No |
| The `Node::str` accessor | `ty.rs` | No, until the registry called it |
| `str : Int -> Str` and `if`'s second signature | `registry.rs` | No |

With the four declarations that's sixteen places, and one more that was
a one-off: `check` learned to choose between signatures. The generic
halves needed nothing. `bind<A>`, the `Trace` derive, the checks, the
cycle walk, the namespace and the construct plumbing are the same for
any type.

`if` gained a second signature rather than a new name, so `def` now
picks a function's signature by its arguments' types. That's the start
of overload resolution, and it changed an error message we already had:
a bad `if` now lists both signatures, where before it named the argument
at fault. A `Str` `if` also clones, since a cell's value is read by
reference and the lift returns a value of its own.

For many types, the per-type places are linear and all the same shape,
`Node::XCell(cell) => f::<X>(cell)`, so a macro over a list of tags, arms
and Rust types could generate the enums and every dispatch. Adding a type
would then be a line, its literal syntax and its registry entries. The
registry is what wouldn't shrink. Every polymorphic operation needs a
signature per type, `if` and `eq` alike, and conversions grow with the
square of the types if every pair gets one. And a closed enum can't hold
a type a user defines, which is the case Mema is for. What scales there
is erasure, and Bough already has it underneath: the store keeps each
value erased in the mode's carrier and downcasts it on every read.

## (e) Questions for the RFDs

- **RFD 2: is a closure sent as an event sanctioned?** A construct over
  a stream of build closures lets I/O code post code through the wall.
  Every check still holds, since the closure runs as graph code inside a
  transaction, but RFD 2 says I/O code "can hold and pass them around but
  cannot build with them". Mema needs the closure. If it's sanctioned, a
  `Runtime` method that runs one in a transaction would save the input,
  the construct, the listener and the slot.
- **RFD 5: can a rewiring fail without poisoning?** A cycle at a switch's
  move and a panic in a construct closure both end in poison, since the
  transaction can't finish. A live environment wants a refused rewiring
  to leave the graph as it was. That takes a transaction that can roll
  back the nodes a construct made, or a closure that returns a `Result`
  the engine honours before anything links.
- **RFD 5: errors in the dynamic layer's names.** The cycle panic names
  node numbers. [What an Oort fighter found
  first](./2026-09-26-oort-fighter-first-findings.md) asked for a stale
  token's creation site. A label a construct can attach to a node, shown
  in every engine error, would answer both.
- **RFD 4: an erased cell token.** A token is an index, a generation and
  a graph id, and its type is a `PhantomData`. Since the engine downcasts
  every value on read, an erased `AnyCell` with a checked
  `downcast::<A>()` would be sound without `unsafe`, and would let a
  dynamic layer keep its cells in a map instead of an enum it extends for
  every type.
- **Rebinding as a primitive.** The shape here, an input of definitions,
  a construct, a hold and a switch, is four nodes and five lines, and
  Mema would write it for every binding. Whether Bough should ship it,
  and whether its step at an equal-valued move should stay, is worth
  asking once Mema has used it.

## The handoff's open questions

**Does `construct` compose cleanly once per command, or want batching?**
It composes. Each command is a transaction, and a construct nested in
another's run works at the same instant. Batching matters for one thing,
an edit made of several redefinitions that should show at once, and
per-binding inputs already allow that in one transaction. New bindings
can't join one: their tokens exist only once their own transaction
returns, and the root input isn't coalescing, so two commands in one
transaction are an error.

**What happens to an old subgraph after rebinding?** It's collected at
the next collection that's due, and a hundred redefinitions leave the
live-node count where it started. Until then our definitions cost nothing
to keep: the registry builds only constants and read-through cells, and
a read-through cell nobody reads doesn't run its function. A definition
with a stream node in it would keep running until it's collected, as the
Oort note measured for screens.

**Does `depends` get awkward when dependencies come from runtime names?**
It never came up. A name resolves to a token on the I/O side, the token
travels in the event, and in the closure it becomes a real dependency, an
input of a `lift`. The construct closures capture only a function
pointer. `depends` is for a closure that captures tokens, and we'd have
needed it if `if` had been a switch that selects between its branches
instead of a lift over all three, which reads both branches every time
it's read.

**Is the same-type rule right?** For a binding with dependents, yes. They
were checked against its type, and its hold and switch are typed, so a
change of type is a new binding under the old name, not a rebinding. For
a binding with no dependents it could be relaxed cheaply, by building a
new binding and moving the name, as long as nothing watches it. A watched
one would need its listener moved too, by the REPL, since a listener
belongs to a node. We left the rule as it is.

## Choices made along the way

- A sibling crate, `bough-repl`, for the reason under What ran.
- `watch` uses `listen_cell`, so it prints the current value at once and
  then every step.
- A tick is an `Int` input starting at 0 that its timer sets to 1, 2,
  3 and on. `set` refuses one.
- The tests use a manual clock whose timers are still threads sending
  through a `RemoteIo`, fired when the script says. The scripts are
  deterministic and the cross-thread path is the real one. One test runs
  the binary against the wall clock.
- A string literal is one word in double quotes, with no spaces and no
  escapes.

## Follow-ups we didn't take

- Redefining an input as a new input. The binding's construct would have
  to hand a token out to I/O code, through `unzip` or a second output.
- Pauses in a piped script. The binary ends at end of input, so a piped
  demo ends before its first tick; `(cat demo; cat) | bough-repl` keeps
  it open.
- An edit session, `begin` to `commit`, over one-transaction
  redefinitions.
- Removing a binding, and changing the type of a binding nothing reads.
- The macro over the type list from (d), and an erased cell instead of
  it.
