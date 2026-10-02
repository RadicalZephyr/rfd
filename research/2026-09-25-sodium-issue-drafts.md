# Three issues for Sodium's semantics text, drafted

_2026-09-25. Drafts of three issues for SodiumFRP/sodium, one for each
wrong answer [the engine spike](./2026-09-24-engine-feasibility-spike.md)
found in `Denotational.hs`: F6, F7 and F89. None is posted yet. Each
section below is one issue, its heading the issue's title._

_Every reproduction ran under GHC 9.4.7 against the vendored text at
`a6f5b3186389e86d949a2965b8d1ed3f522fb2e0`, and printed what each section
says the text prints. Each fix ran against a patched copy of the text:
the reproduction printed what the section says it should, and the twenty
vectors in `sodium.hs` still passed. The programs are in the sections
themselves._

## Denotational semantics: a SwitchC created after its outer stepped starts from the wrong inner and steps out of time order

### Summary

In `denotational/Reactive/Sodium/Denotational.hs` (revision 1.1), `SwitchC c t0` scans the outer cell `c` from its initial value. It should scan from `c`'s value at the creation time `t0`. When a switch cell is created after its outer has stepped, the result goes wrong in three ways:

- It starts from an inner the outer no longer selects.
- It has steps from before it existed.
- Its steps are out of time order.

`sample` and `Value` at the creation instant read the wrong value too.

### Reproduction

```haskell
import Reactive.Sodium.Denotational

main :: IO ()
main = do
  let c1 = Constant 'a'
      c2 = Hold 'x' (MkStream [([3], 'y')]) [0]
      outer = Hold c1 (MkStream [([1], c2)]) [0] -- selects c2 at [1]
      sw = SwitchC outer [3]                     -- created at [3]
  print (steps sw)
  print (run (sample sw) [3])
  print (occs (run (value sw) [3]))
```

The text prints:

```
('x',[([3],'a'),([1],'y')])
'y'
[([3],'a')]
```

It should print:

```
('x',[([3],'y')])
'x'
[([3],'y')]
```

The outer has selected `c2` since `[1]`. The switch cell exists from `[3]`, so it should start from `c2`'s value before `[3]`, which is `'x'`. It should step to `'y'` at `[3]`, when `c2` does. Instead, the text's switch cell:

- steps to `'a'` at `[3]`. That is `c1`'s value, and the outer deselected `c1` at `[1]`.
- steps at `[1]`, before the switch cell existed.
- lists its steps out of time order, `[3]` before `[1]`. The text documents `C a` as "for increasing T values".
- reads `'y'` for `sample` at `[3]`. That value comes from the step at `[1]`; `c2`'s value before `[3]` is `'x'`.
- fires `'a'` for `Value` at `[3]`, the deselected inner again.

### Cause

The initial value of `steps (SwitchC c t0)` reads the outer at `t0`, but the scan does not. Its `where` clause takes `(a, sts) = steps c`, which is the outer's whole history, from its initial value.

### Fix

```diff
 steps (SwitchC c t0) = (at (steps (at (steps c) t0)) t0,
         coalesce (flip const) (scan t0 a sts))
-    where (a, sts) = steps c
+    where (a, sts) = chopFront (steps c) t0
```

With this change, the reproduction prints the expected output. The twenty vectors in `sodium.hs` pass unchanged, because every `SwitchC` there is created at `[0]`, before its outer steps.

The Java implementation behaves like the fix. `Cell.switchC` starts from the outer's value at creation and follows its updates from then on.

### Context

We found this while using the executable semantics as the test oracle for Bough, a Rust FRP library that follows Sodium's semantics. Checked with GHC 9.4.7 against `Denotational.hs` at `a6f5b3186389e86d949a2965b8d1ed3f522fb2e0`.

## Denotational semantics: Split emits out of time order when its input fires in a child transaction of an earlier event

### Summary

In `denotational/Reactive/Sodium/Denotational.hs` (revision 1.1), `occs (Split s)` lists each input event's children in the order of the input events. That is only time order when no input event falls in a child transaction of an earlier one.

Take an input that fires at `[0]` and again at `[0,0]`:

- The children of `[0,0]` are `[0,0,0]` and `[0,0,1]`.
- Both come before `[0,1]`, the second child of `[0]`.
- `Split` emits them after `[0,1]`.

The text documents `S a` as "for increasing T values", and `Merge` and `coalesce` depend on it. So a merge downstream sees two separate events at one instant.

### Reproduction

```haskell
import Reactive.Sodium.Denotational

main :: IO ()
main = do
  -- Lists at [0], and again in [0]'s first child transaction, [0,0].
  let parents = MkStream [([0], [1, 2]), ([0,0], [10, 11])]
      items = Split parents
  print (occs items)
  print (occs (Merge items (MkStream [([0,0,0], 100)]) (+)))
  -- The same without a literal: a stream merged with its own defer.
  let lists = MkStream [([0], [1, 2])]
      deferred = Split (MapS (\l -> [l]) lists)
  print (occs (Split (Merge lists deferred (++))))
```

The text prints:

```
[([0,0],1),([0,1],2),([0,0,0],10),([0,0,1],11)]
[([0,0],1),([0,0,0],100),([0,1],2),([0,0,0],10),([0,0,1],11)]
[([0,0],1),([0,1],2),([0,0,0],1),([0,0,1],2)]
```

It should print:

```
[([0,0],1),([0,0,0],10),([0,0,1],11),([0,1],2)]
[([0,0],1),([0,0,0],110),([0,0,1],11),([0,1],2)]
[([0,0],1),([0,0,0],1),([0,0,1],2),([0,1],2)]
```

The merge in the second line has two events at `[0,0,0]`, 100 and 10. A merge with `(+)` should give one event there, 110.

The third line shows that the input needs no literal. A stream merged with its own defer fires at `[0]` and at `[0,0]`; this uses defer as the Java implementation defines it, a split of one element. A split fed by its own children, which is how a tree walk is written, gives the same shape of input.

### Cause

`concatMap split` walks the input events in their time order. It emits all of one event's children before the next event's children, even when the next event is a descendant of the first and its children come earlier.

### Fix

```diff
+import Data.List (sortOn)
+
 ...
-occs (Split s) = concatMap split (coalesce (++) (occs s))
+occs (Split s) = sortOn fst (concatMap split (coalesce (++) (occs s)))
```

`sortOn` is stable, so events at one time keep their order. With this change, the reproduction prints the expected output, and the twenty vectors in `sodium.hs` pass unchanged.

The sort needs the whole stream. That is fine for the finite streams the executable text evaluates. A lazy version would only need to merge each event's children with the children of its descendants: an event's children always come before any later event that is not its descendant.

### Context

We found this while using the executable semantics as the test oracle for Bough, a Rust FRP library that follows Sodium's semantics. Checked with GHC 9.4.7 against `Denotational.hs` at `a6f5b3186389e86d949a2965b8d1ed3f522fb2e0`.

## Denotational semantics: Split has no creation time, so a split created in a child transaction splits an event from before it existed

### Summary

In `denotational/Reactive/Sodium/Denotational.hs` (revision 1.1), `Hold`, `SwitchC` and `Value` take a creation time and ignore what happened before it. `Split` does not.

Usually that cannot be observed:

- The children of an event at `t` fall at `t ++ [n]`.
- Those are all before any later top-level time.
- So nothing created after `t` sees them.

A split created in one of `t`'s own child transactions is different. Say it is created at `[1,0]`:

- It splits its input's event from `[1]` into children at `[1,0]`, `[1,1]` and `[1,2]`.
- Those are at and after the split's creation.
- So anything created along with the split sees them.

### Reproduction

```haskell
import Reactive.Sodium.Denotational

main :: IO ()
main = do
  let x = MkStream [([1], 1 :: Int)]
      deferred = Split (MapS (\a -> [a]) x) -- Sodium's defer: x's event again at [1,0]
      -- Runs at [1,0]: splits x, and totals the parts from -1.
      body _ = Reactive $ \t0 ->
        let parts = Split (MapS (\v -> [v * 10, v * 10 + 1, v * 10 + 2]) x)
            total = Hold (-1) (Snapshot (+) parts total) t0
        in total
      shown = SwitchC (Hold (Constant 0) (Execute (MapS body deferred)) [0]) [0]
  print (steps shown)
```

The text prints:

```
(0,[([0],0),([1,0],9),([1,1],20),([1,2],32)])
```

It should print:

```
(0,[([0],0),([1,0],-1)])
```

Step by step:

1. `x` fires 1 at `[1]`.
2. The defer fires the same event at `[1,0]`, where `Execute` runs `body`.
3. The body creates a split of `x` and a total over its parts.
4. The split did not exist at `[1]`, so it should have nothing to split, and the total should stay at -1.
5. The text splits the event from `[1]` into 10, 11 and 12 at `[1,0]`, `[1,1]` and `[1,2]`, and the total takes all three.

The Java implementation gives -1. There, a stream forgets its firings in the transaction's `last` actions. `Transaction.close` runs those before the child transactions queued in `post`, so a split listened to in a child transaction never sees the parent's firing.

Defer is a split of one element, so in the text a defer created in a child transaction has the same problem. A hold created at `[1,0]` over it takes `x`'s event from `[1]`, at `[1,0]`.

### Cause

`Split` has no creation time.

`Execute` and `SwitchS` have none either, but they keep each event's time. What they carry from before a node's creation stays before anything created later, where nothing can observe it. `Split` moves an event to later times, and that is why the missing creation time shows up here.

### Fix

Give `Split` a creation time, as `Hold` and `SwitchC` have:

```diff
-    Split    :: Stream [a] -> Stream a
+    Split    :: Stream [a] -> T -> Stream a
 ...
-occs (Split s) = concatMap split (coalesce (++) (occs s))
+occs (Split s t0) = concatMap split (coalesce (++) (filter (\(t, _) -> t >= t0) (occs s)))
```

A split created at `[0]` keeps everything, so the twenty vectors in `sodium.hs` pass unchanged. The one `Split` vector only needs its creation time: `Split s1 [0]`.

With the fix, the reproduction prints the expected output once it passes the creation times: `[0]` for the defer, and `t0` for the split in the body. This fix composes with the sort that the issue on `Split`'s time order proposes.

### Context

We found this while using the executable semantics as the test oracle for Bough, a Rust FRP library that follows Sodium's semantics. Checked with GHC 9.4.7 against `Denotational.hs` at `a6f5b3186389e86d949a2965b8d1ed3f522fb2e0`.
