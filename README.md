# Bough RFDs

A place to document the design decisions of Bough FRP.

## How this repo is filed

Check a file against these rules before you add, move or delete it.

- **RFDs** are `src/rfd-NNNN-*.md`. Each holds its decisions, with their
  trade-offs and rejected alternatives in the sections they belong to,
  as RFD 1's records policy says.
- **Research** is evidence and lives in `research/`. **Notes** are ideas
  and live in `notes/`. Each folder's README says what belongs there. A
  graduated note is deleted, as `notes/README.md` says.
- **Handoffs are transport.** A handoff stays only when a reader of a
  result here needs it to interpret that result, because it set the
  result's scope. So do the prompts that produced a result, in a folder
  named for it, such as `research/frp-literature-review-prompts/`. Every
  other handoff lives outside the repo.
- **Derived views stay out.** A document generated from a source here
  for one job, such as a triage of a review, isn't committed. When the
  method matters, the prompt that produced it is, beside its source.
- **The repo is self-contained.** A document cites a published
  repository at a commit, or a public URL. A private source may be named
  for context, but nothing a reader needs depends on it. In place of a
  local path or a claude.ai session, a placeholder such as `<scratch>`
  stands in, defined where it's used.
