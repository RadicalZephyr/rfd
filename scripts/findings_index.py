#!/usr/bin/env python3
"""Index a research note's findings by number.

Each finding F<n> gets one anchor, <a id="f<n>"></a>, at its fullest
discussion: its bold lead in the body (`- **F<n>. ...**`) where it has
one, otherwise its entry in the "## Every finding" list (`- F<n>. ...`).
Its label is the list entry's text, or the bold lead's where the list
has none. The table of every finding, sorted by number, goes between
two marker comments in a dated addendum at the end of the note.

    findings_index.py NOTE        rewrite NOTE in place
    findings_index.py --check NOTE  exit 1 if NOTE would change
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

ANCHOR = re.compile(r'<a id="f\d+"></a>')
LIST_ENTRY = re.compile(r"^- F(\d+)\. (.+)$")
BODY_LEAD = re.compile(r"^(\s*- )\*\*(F\d+(?:, F\d+)*)\.")
LEAD_LABEL = re.compile(r"\*\*F\d+(?:, F\d+)*\.\s*(.+?)\*\*", re.DOTALL)
START = "<!-- findings-index:start -->"
END = "<!-- findings-index:end -->"


class FindingsError(Exception):
    pass


def index(text, today):
    """Return the note with its anchors and index brought up to date."""
    text = ANCHOR.sub("", text)
    if START in text:
        head, rest = text.split(START, 1)
        tail = rest.split(END, 1)[1]
    else:
        head = text.rstrip("\n") + f"""

## Addendum, {today}: findings by number

_Every finding, in order. Each link goes to the finding's fullest
discussion above. `scripts/findings_index.py` writes this table and the
anchors; run it after adding a finding._

"""
        tail = "\n"

    lines = head.split("\n")
    labels, list_line, lead_line = {}, {}, {}
    in_list = False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            in_list = line == "## Every finding"
        if in_list and (m := LIST_ENTRY.match(line)):
            n = int(m.group(1))
            if n in list_line:
                raise FindingsError(f"F{n} is in the list twice")
            labels[n], list_line[n] = m.group(2), i
        elif not in_list and (m := BODY_LEAD.match(line)):
            for n in (int(f[1:]) for f in m.group(2).split(", ")):
                if n in lead_line:
                    raise FindingsError(f"F{n} has two bold leads")
                lead_line[n] = i
                if n not in labels:
                    lead = LEAD_LABEL.search("\n".join(lines[i:i + 5]))
                    if lead and lead.group(1).strip():
                        labels[n] = " ".join(lead.group(1).split())

    numbers = sorted(set(list_line) | set(lead_line))
    unlabelled = [f"F{n}" for n in numbers if n not in labels]
    if unlabelled:
        raise FindingsError("no label for " + ", ".join(unlabelled))

    anchors = {}
    for n in numbers:
        anchors.setdefault(lead_line.get(n, list_line.get(n)), []).append(n)
    for i, ns in anchors.items():
        tags = "".join(f'<a id="f{n}"></a>' for n in ns)
        lines[i] = re.sub(r"^(\s*- )", lambda m: m.group(1) + tags,
                          lines[i], count=1)

    rows = "".join(
        f"| [F{n}](#f{n}) | {labels[n].replace('|', chr(92) + '|')} |\n"
        for n in numbers)
    table = f"\n| Finding | Label |\n|---|---|\n{rows}"
    return "\n".join(lines) + START + table + END + tail


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the note would change; write nothing")
    parser.add_argument("note", type=Path)
    args = parser.parse_args()

    text = args.note.read_text()
    try:
        new = index(text, datetime.date.today().isoformat())
    except FindingsError as e:
        sys.exit(f"{args.note}: {e}")
    if args.check:
        if new != text:
            print(f"{args.note}: the findings index is out of date",
                  file=sys.stderr)
            sys.exit(1)
    elif new != text:
        args.note.write_text(new)


if __name__ == "__main__":
    main()
