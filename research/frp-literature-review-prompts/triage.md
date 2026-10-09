# Triage for the pre-build design grilling

You are writing a triage: every open design question that stands between
Bough's RFDs and the build, each graded against the evidence, in the
order Zefira should grill them. She grills it question by question next,
and the RFD changes she decides land after that. You triage; she decides.
So you change nothing in this repo and fetch no new sources.

Two paths come from the message that starts you: `<literature>`, the
private literature corpus, and `<out>`, the file you write the triage to.

## What you read

Read these in this order, all of them, in full.

1. **The RFDs**, `src/rfd-000*.md`, and `GLOSSARY.md`. They're the
   baseline every question is asked against.
2. **The review**, `research/2026-09-28-frp-literature-review.md`. It's
   the evidence. Start with its header and the must-read. Then, in each
   of its nine dimension sections: "Questions to grill", "Claude's
   leaning", "Settled decisions the evidence contradicts" and "The Rust
   prior art". Read the rest of a section when a question needs it.
3. **Every note in `notes/`**, the README aside. The notes are
   Zefira's current thinking, and what she wants to build with Bough.
   They're written against the same RFDs as the review.
4. **The findings index**, the table at the end of
   `research/2026-09-24-engine-feasibility-spike.md`. It's where a
   finding's label comes from.

The corpus, `<literature>`, is only for a question the review doesn't
answer. Look in its `synthesis/` files first, then in the reading notes
of the sources they cite, and cite stem and page as the review does.

## The notes play two roles

- **Context, always.** Every note shapes how you frame and rank every
  question. A question one of Zefira's programs depends on ranks above an
  equal one nothing she builds touches.
- **A source of questions, sometimes.** A question that only the notes
  raise gets a full entry when it bears on the core architecture or
  runtime performance, and must be settled before v1. Every other
  question a note raises gets one line in "Raised by the notes, not
  graded here".

## What a question is

An open design choice whose answer changes an RFD, the engine's
architecture or its performance. They come from three places: each
dimension's "Questions to grill", each settled decision the evidence
contradicts, and the notes. When two places raise the same choice, it's
one question with every source listed.

The semantics are largely settled. Weight the triage toward performance
and implementation strategy.

One question is graded whatever the notes' rule above says, the seam
question: does the core need hooks now, so that a future delta-aware
collections crate can attach cleanly, and what would that interface look
like? It comes from `notes/2026-09-29-incremental-collection-propagation.md`,
and the review's RFD 4 section on cells of collections is its evidence.
Grade and place it like any other.

## Each question's entry

```markdown
### Q<n>. <the question, in one plain sentence>

- **Source:** review, notes or both: the review's section headings and
  the notes' filenames.
- **v1:** before v1 or can wait, and why, in one sentence.
- **Stakes:** what each answer changes, and in which RFDs.
- **The literature:** what it recommends, with the review's leaning
  where it gives one. Or "The corpus is silent."
- **The Rust prior art:** what the reactive crates in the review's crate
  table did. Or "Not stated."
- **Where they part:** where the literature, the crates and Bough's
  current design disagree, or leave the choice open.
- **The notes:** what Zefira's notes add, by filename. Leave this out if
  they add nothing.
```

Budget each entry, not the document: about 250 words, up to 400 for a
question that gates the build. Spend the words on the stakes and on
where the evidence parts.

## Order

Before-v1 questions first, then can-wait ones. Within each group, order
by impact on the core architecture and runtime performance: a choice
that must precede the public signatures comes before one that can change
behind them. Number them Q1 onward in that order.

## Citing

- **A finding** is `F<n> (<label>)`, the label copied verbatim from the
  findings index: `F62 (Captures reached through a switch need a
  declaration.)`. Where an argument rests on a finding's detail, quote
  the spike note's sentence. The label and the quote are the finding's
  only words in the triage.
- **The review** by section heading. **A note** by filename. **A
  source** by stem and page.
- **A number** as the review gives it, with its conditions and its
  provenance's caveats. Copy it; don't round it.

## The document

1. **A header:** the date; every note you read, by filename; and counts:
   questions graded, before v1, can wait, and from the review, the notes
   or both.
2. **The before-v1 questions.**
3. **The can-wait questions.**
4. **The semantics cut the literature doesn't back.** The review's RFD 1
   section covers each change Bough makes to the text's semantics, and
   what backs it. Name the one change the literature doesn't directly
   support, quote what the review says about its support, and set out
   the defences open to Zefira. If none fits, or more than one, say so.
5. **Raised by the notes, not graded here:** one line each, with its
   note.
6. **Research seeds:** every question where the corpus is silent, one
   line each, with its number.
7. **Accounting:** each dimension's "Questions to grill", item by item,
   mapped to the Q it became, the Q it merged into, or the reason it was
   dropped; and each note mapped to the Qs it shaped, or "context only".

You're done when the accounting is complete: every question the review
raises and every note is accounted for.
