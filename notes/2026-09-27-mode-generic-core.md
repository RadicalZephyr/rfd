# A core that doesn't know its mode

_2026-09-27. Where a conversation about the petrol pump port landed.
One fix compiled in a scratch copy; nothing else has run._

## The question

The petrol pump repository is meant to show one application core, from
Blackheath and Jones' example, written once in bough and used unchanged
under GTK, ratatui, egui, and as a networked service on threads or
async. That means the core is generic over `Mode`. GTK needs `Local`,
because its listeners capture widgets, which aren't `Send`. Tokio needs
`Threaded`, unless its runtime is single-threaded.

Porting `LifeCycle` failed at the first `or_else`:

```text
error[E0277]: the trait bound `M: bough::Accepts<impl bough::Source<Event = Fuel>>` is not satisfied
```

## What we found

- A materializer needs `M: Accepts<T>` for the chain it stores. A
  helper that returns `impl Source` hides that type, and a closure's
  type has no name, so no bound can mention either one. The `Accepts`
  docs already say so: generic code can't make a closure of its own and
  store it.
- A chained `or_else` also needs `M: Accepts<Stream<Fuel>>`, since the
  second call's receiver is the first call's node. That one can be
  named.
- The workaround compiles under both modes. The closures become function
  pointers, constants move into `map_to`, and each chain gets an alias:

  ```rust
  type IsUp = fn(&UpDown) -> bool;
  type Lifted = MapTo<Filter<Stream<UpDown>, IsUp>, Fuel>;

  where
      M: Mode + Accepts<Lifted> + Accepts<Stream<Fuel>> + Accepts<Fuel>,
  ```

  Every chain the core stores needs one, and every closure that captures
  something has to be rewritten so it doesn't. A reader would take the
  showcase as an argument against bough.

## Where it landed

- **The claim.** The core commits to a `Send` vocabulary, and the shell
  chooses the mode and everything that follows from it. "The core
  doesn't know about threads" is too strong. Running under both modes
  commits it to `Send`, and that has a cost: a core that shares large
  immutable data pays for `Arc` even in a GTK build.
- **The friction is a leak, not only an ergonomics problem.** Today the
  core has to list, type by type, what the shell's mode will accept.
  That's the shell's question asked inside the core. What the core
  actually depends on is that its values are `Send`.
- **Only the shell needs `Local`'s "accept anything".** Listeners, input
  wiring and anything that touches a widget live in the shell. A
  portable core that only builds graph only needs `Send`.
- **Sequencing.** The port pauses. The next step is designing bough, so
  that the core isn't ported the hard way and then rewritten.

## A lead

`Send` is an auto trait, so it leaks through `impl Trait` and through
closures. Generic code can prove a chain is `Send` without naming it.
Both modes accept every `Send` type, and `Mode::erase_send` already
exists for the engine's own values. What's missing is a public way to
say "this mode accepts anything `Send`": a portable bound for building
graphs, with `Accepts` kept for the operations the shell uses.

The open problem is that Rust can't give one method two alternative
bounds, `M: Accepts<Self>` or `Self: Send`. A blanket impl for `Send`
types would overlap `Local`'s blanket impl, and that needs
specialization. So it's parallel methods, or a bound shaped some other
way.

## What we considered

- **A concrete `Threaded` core.** The pump's types are all `Send`, and
  every shell we named has atomics. The UI shells would drive it through
  `RemoteIo` even though they're single-threaded, and their listeners
  couldn't capture widgets. That's a weaker showcase, since the
  difference between the modes is exactly what should stay in the shell.
- **A concrete `Local` core.** It would port the book directly with
  closures, but it gives up the claim.
- **Keeping the function pointer workaround and porting on.** It works,
  and it buries the showcase under type aliases, which the bough change
  would then make us rewrite.

## Next

- An experiment: the smallest portable bound that lets a `Mode`-generic
  function store an unnamed `Send` chain, tried on `when_lifted` and
  `when_set_down`.
- Then the interface and its tests, agreed before any code in bough.
