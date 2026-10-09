# Which handoffs stay in the repo

_2026-10-09. Where a cleanup conversation landed before it turned to the
graduated notes. Nothing has moved yet; this parks the findings so the
handoff work can pick up from here._

## The test

A handoff stays only if a future reader of a result needs it to interpret
that result: it defines the result's scope, so it's methodology. Any other
handoff is transport and leaves the repo. Handoffs that leave go to the
`claude-handoffs` repository, under a `bough/` subdirectory.

## Where each handoff stands

- `research/handoff-2026-09-27-frp-literature-review.md` **stays.** It
  scopes the literature review. It has 36 references to paths outside this
  repo, which have to be inlined or removed first. Two of them,
  `REQUIREMENTS.md` and `Changes to Bough RFDs.md` in `claude-planning`,
  are the review's scope, so the test says to bring them in, not to cut
  the reference.
- `research/2026-09-23-static-engine-handoff.md` and its addendum
  **probably stay.** The exploration answers their numbered questions by
  number (Q1, Q10, Q21), so it can't be read without them.
- `research/2026-09-22-no-std-handoff.md` **probably goes.** It's notes
  from a claude.ai chat, candidate constraints for a design session, and
  doesn't scope any one result. RFD-0007 links to it as the way into the
  target research, so that link needs a new target, and RFD-0007 needs
  checking for anything it only carries by reference.
- `research/handoff-2026-09-25-oracle-work-for-the-real-build.md` **goes.**
  It's future work, not the scope of a result. RFD-0005 cites it for an
  experiment still open; that experiment becomes an issue and the RFD links
  the issue.
- `notes/2026-10-09-handoff-bough-frp-lit-review-grilling.md`, untracked,
  **goes.**

## Other references outside the repo

- The literature review itself, at line 3090, cites
  `literature/synthesis/14-crates-pins.md`.
- The static engine exploration points at `bough-static/experiments/` for
  its experiments.

## Outside the repo

- `claude-planning` holds five files that are already in `research/`,
  byte for byte or nearly: the no-std handoff, the host embedding
  requirements, both static engine handoffs, and the wasm research. Those
  copies can go. The rest is planning from before the RFDs: `REQUIREMENTS.md`,
  `PLAN.md`, `HANDOFF.md`, `GRILLING-TRANSCRIPT.md`,
  `Changes to Bough RFDs.md` and a tarball of RFD patches.
- `claude-handoffs` has one handoff squarely about Bough,
  `handoff-2026-10-04-bough-rollback-probe.md`, and three that mention it:
  the FRP open research questions, the research skills, and the game design
  thread.

## Also settled

Notes that graduate straight to an RFD are deleted too, the same as notes
that graduate to research. Their trade-offs and alternatives move into the
RFD, so an RFD never leans on a document that isn't research.
