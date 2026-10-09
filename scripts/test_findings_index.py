"""Tests for findings_index.py. Run: python3 -m unittest discover scripts"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from findings_index import FindingsError, index  # noqa: E402

TODAY = "2026-10-09"

DOC = """\
# A spike

## What held

- **F10. A body lead.** More about it.
- **F2.** Only the number is bold.
- **F3, F4. Two findings, one bullet.** Both.

## Every finding

- F2. The second finding.
- F3. The third.
- F4. The fourth.
- F7. Only in the list.
- F10. The tenth.

## Addendum

- **F11. Only in the addendum.** Its lead is its label.
"""


def run(text):
    return index(text, TODAY)


def line_with(text, needle):
    return next(l for l in text.splitlines() if needle in l)


class FindingsIndexTest(unittest.TestCase):
    def test_list_only_finding_is_anchored_on_its_list_entry(self):
        self.assertEqual(line_with(run(DOC), "Only in the list"),
                         '- <a id="f7"></a>F7. Only in the list.')

    def test_body_lead_takes_the_anchor_and_the_list_entry_does_not(self):
        out = run(DOC)
        self.assertEqual(line_with(out, "A body lead"),
                         '- <a id="f10"></a>**F10. A body lead.** More about it.')
        self.assertEqual(line_with(out, "The tenth"), "- F10. The tenth.")
        self.assertEqual(out.count('<a id="f10">'), 1)

    def test_combined_bullet_gets_every_anchor(self):
        self.assertEqual(
            line_with(run(DOC), "Two findings"),
            '- <a id="f3"></a><a id="f4"></a>**F3, F4. Two findings, one bullet.** Both.')

    def test_addendum_only_finding_takes_its_label_from_its_lead(self):
        self.assertIn("| [F11](#f11) | Only in the addendum. |", run(DOC))

    def test_list_label_wins_over_a_body_lead(self):
        self.assertIn("| [F10](#f10) | The tenth. |", run(DOC))

    def test_rows_sort_by_number(self):
        rows = [l for l in run(DOC).splitlines() if l.startswith("| [F")]
        self.assertEqual([r.split("]")[0][3:] for r in rows],
                         ["F2", "F3", "F4", "F7", "F10", "F11"])

    def test_running_twice_changes_nothing(self):
        once = run(DOC)
        self.assertEqual(run(once), once)

    def test_a_reworded_label_updates_the_row_and_keeps_the_anchor(self):
        out = run(run(DOC).replace("F7. Only in the list.", "F7. Reworded."))
        self.assertIn("| [F7](#f7) | Reworded. |", out)
        self.assertNotIn("Only in the list", out)
        self.assertIn('- <a id="f7"></a>F7. Reworded.', out)

    def test_a_finding_with_no_label_is_an_error_naming_it(self):
        with self.assertRaisesRegex(FindingsError, r"\bF5\b"):
            run(DOC + "\n- **F5.** Bold number, no list entry.\n")

    def test_two_body_leads_for_one_finding_is_an_error(self):
        with self.assertRaisesRegex(FindingsError, r"\bF10\b"):
            run(DOC + "\n- **F10. Again.** Twice.\n")

    def test_a_pipe_in_a_label_is_escaped(self):
        out = run(DOC.replace("The third.", "`a | b` splits."))
        self.assertIn(r"| [F3](#f3) | `a \| b` splits. |", out)


class CheckTest(unittest.TestCase):
    SCRIPT = Path(__file__).parent / "findings_index.py"

    def check(self, text):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "note.md"
            path.write_text(text)
            return subprocess.run(
                [sys.executable, self.SCRIPT, "--check", path],
                capture_output=True, text=True).returncode

    def test_check_passes_on_a_current_file(self):
        self.assertEqual(self.check(run(DOC)), 0)

    def test_check_fails_on_a_stale_file(self):
        self.assertEqual(self.check(DOC), 1)


if __name__ == "__main__":
    unittest.main()
