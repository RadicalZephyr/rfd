# 2026-10-10 — Adding continuous Behavior to the oracle

Late-night thread, written up so I can bring it into the Bough design discussion.

## The problem

I want Bough to support continuous-time Behaviors directly, not as Sodium's library pattern. The oracle (Blackheath's denotational semantics, in Haskell) is how I check Bough is semantically correct. If continuous Behaviors have no denotation in the oracle, I can't check that part of Bough at all. So the semantics has to be extended before the feature can be verified.

## What I thought the blocker was, and what it actually is

I'd been thinking continuous time was research-level and that was why Sodium kept it out of the core. That conflated three things:

- **Denotation on paper:** easy and well-trodden. Elliott & Hudak (Fran) gave Behaviors a clean meaning, functions from time to values, decades ago. Extending Blackheath's semantics is adding to existing work, not inventing it.
- **Mechanising it in Rocq:** painful, because of the reals. Not needed for the oracle, which is executable.
- **Implementing it:** the classic problems are sampling, space/time leaks, and keeping events and time consistent with each other.

So the denotation isn't the hard part. The hard part is the *check*.

## The extension

- `Behavior a` denotes a function `Time -> a`, alongside the existing discrete model.
- `sample` evaluates it at a transaction's time.
- `type Time = Rational` rather than `Double`, so the oracle never disagrees with itself because of rounding.

## What "correct" means

Functions can't be compared for equality, so "Bough matches the oracle" has to mean **they agree at every time Bough actually observes**. That fits property testing directly: generate event streams, sample both the oracle and Bough at the transaction times, compare.

## The design lever

Anything not closed-form in time breaks exact agreement. `integral` is the classic case: the denotation is exact, any implementation approximates it, so the oracle could only check "within tolerance".

- **Closed-form Behaviors only** (no integration over Behaviors): the oracle stays exact and fully usable.
- **Allow `integral` and friends:** more expressive, but the price is giving up exact verification for that part of the API.

This is a cleaner framing of core-vs-library than "is it too deep": what does putting continuous time in the core buy, and what does it cost the oracle and the runtime?

## Open

- **Why Sodium actually keeps continuous time as a library pattern.** My guess is implementation simplicity (small discrete core), but that's a guess. Check Blackheath's book / the Sodium discussions before it becomes a premise in a decision.
- Where exactly `Time` comes from in a transaction, and whether Bough's single global transaction step gives a clean answer.
- Is there a middle ground for integration (e.g. an exact integral of piecewise-polynomial Behaviors) that keeps the oracle exact?

## Experiment

Copy the oracle, add `Behavior` over rational time and `sample`, write one QuickCheck property comparing it against a trivial implementation, and see what resists. Expectation: the denotation goes in cleanly, and the first real friction shows up when trying to write `integral`.
