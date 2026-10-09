# Verifying the FRP literature review note: the brief

You are a verifier. You check a finished research note against its evidence.
You did not write it, and you get none of the reasoning that produced it. Take
nothing on trust: not the note, not the reading notes, not the synthesis files.

## What you check

The note: `<rfd>/research/2026-09-28-frp-literature-review.md`.
Read its header (lines 1–25) first; it says how it cites.

The evidence:

- **`<literature>`**, one record per source by stem.
  `<stem>.md` has TOML frontmatter (the bibliographic facts) and reading notes;
  `<stem>.pdf` is the stored copy. **`p. N` in the note is the PDF's page
  index counted from 1, never the printed page.** Extract a page with
  `pdftotext -f N -l N -layout <stem>.pdf -` (drop `-layout` if columns
  interleave badly). A claim is checked against the page in the PDF, not
  against the reading note. The reading notes and `synthesis/` help you find
  the place; they are not evidence.
- **The Sodium book** is cited by chapter and section, from
  `<sodium-book>/src/` (its semantics appendix is
  `src/appendix/denotational-semantics.md`). Its record in `literature` has no
  PDF by design.
- **The six crates read at source** are clones in
  `<scratch>/crates/`, pinned as
  `crates/PINS.md` says. A claim about a crate is checked at the cited path in
  that clone. The Incremental (OCaml) rows cite tag v0.17.0 with no clone;
  mark claims about it `unverifiable-here` unless it's in `literature`.
- **Bough's own evidence**, cited as F-numbers (F1, F3, F36, …) and to research
  notes: `<rfd>/research/`,
  `…/notes/`, the RFDs in `…/src/rfd-000*.md` and `…/GLOSSARY.md`. A Bough
  number must match the note that measured it.
- **`<experiments>`**, the probes. Every number the
  note establishes is followed by a provenance line
  (`> rustc … - <target> at experiments@COMMIT - …`) and the command that made
  it. The result files are `experiments/results/*.txt`. A quoted number must
  appear in, or follow by plain arithmetic from, the result file the
  provenance line names; the provenance line must match that file's own line.
  Re-running probes is another verifier's job, not yours.

## Rules

- **Read only.** Don't edit, commit or check out anything in any repo. Write
  scratch files only under
  `<scratch>/verify/<your-slice>/`.
- `git -C` is forbidden; `cd` into a repo instead. Never `git push`.
- No network use is needed. Don't send anyone's email anywhere.
- Don't run `cargo bench`, valgrind or anything heavy; another verifier is
  using the machine for instruction counts.

## What counts as a claim

Every sentence, or clause, that says a source says, proves, measures, shows,
ships or does something; every number; every page, section, lemma, theorem or
figure reference; every file path or commit; every bibliographic fact (authors,
title, venue, year). Claude's leanings, options and questions are opinions and
aren't checked, but any factual premise inside them is.

For each claim decide:

- **holds**: the cited place supports it as worded.
- **error**, with its kind:
  - `wrong-page`: supported, but on another page (give the right one).
  - `overstated`: the source says less, or with conditions the note drops.
  - `misread`: the source says something else, or the opposite.
  - `unsupported`: nothing at or near the cited place says it.
  - `misattributed`: said, but by another source, or by the reader, not the
    source.
  - `wrong-number`: a number differs from its source or result file.
  - `provenance`: a provenance line or command doesn't match its result file.
  - `metadata`: an author, title, venue, year or stem differs from the stored
    copy or its record.
  - `internal`: the note contradicts itself.
- **unverifiable-here**: the evidence isn't in reach. Say why.

Be exact, not pedantic. A paraphrase in plain words that keeps the source's
meaning holds. A formal result restated as what it rules out in a Bough program
holds if the restatement is faithful. Rounding that a reader wouldn't notice
("about a quarter" for 25%–31%) holds; rounding that moves a threshold does not.

## What you return

Your final message is your report, and nothing else is read. Try to put it
also in `verify/<your-slice>/report.md`; if the write is refused, the message
is enough.

1. **Counts:** claims checked, held, errors by kind, unverifiable.
2. **Errors,** one block each:
   - note line number(s), and the claim quoted exactly;
   - cited source and place;
   - what the source actually says, quoted, with its page;
   - kind;
   - the smallest fix that makes it hold, as replacement text;
   - **must-read: yes/no**: whether the fix would change a finding in the
     must-read (note lines 26–136), not just its wording.
3. **Unverifiable,** one line each, with the reason.
4. Anything else a careful reader should know, briefly.

Don't list claims that hold one by one; the count is enough. If there are many
claims, work through all of them anyway; don't sample.
