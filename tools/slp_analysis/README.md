# SLP analysis

Generates the comparison document "SLP-Analyse (Original vs Advanced Ep4).md"
(spell learning points of the magic party members, spell costs per school, what can be
learned at which level) for the german 1.20 original vs. the current Advanced data.

```
python slp_report.py "C:\Users\Robert\docs\AmbermoonAdvanced\4\SLP-Analyse (Original vs Advanced Ep4).md"
```

Options: `--work <dir>` (temp dir for extracted data, default `%TEMP%\slp_analysis`),
`--original-zip <zip>` (german 1.20 release).

- `SlpAnalysis` (C#) dumps party members, spells and scrolls via Ambermoon.Data.Legacy.
  Ambermoon.net must be checked out next to this repo.
- Advanced SP/SLP costs come from `DAT_SpellInfos` in `code_changes/AM2_CPU.s`
  (the remake values are listed too, so mismatches show up).
- `section7.md` is the hand-written assessment appended as the last section.
