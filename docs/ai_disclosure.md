# AI-assistance disclosure (draft — the group must check it against the course policy)

**Tool:** Claude (Anthropic), used on 13 November 2026.

**What the assistant produced:** the Python package and scripts, the test suite, the demonstration
notebook, the figures and result tables (by running that code), the LaTeX report and viva notes,
the slide deck and speaker notes, the proposal text, this disclosure and the other files in `docs/`.

**What was actually executed:** all code was run in a Linux environment (Python 3.13, NumPy 2.5.3,
SciPy 1.18.1, pandas 3.0.5, Matplotlib 3.11.2). All 22 validation checks and the pytest suite (23
tests) passed. Quick and full experiment modes completed. The notebook was executed top to bottom.
The report and viva notes were compiled with pdfLaTeX. The deck was converted to PDF with LibreOffice.
Every number in the report and slides was taken from the generated CSV files.

**Not done by the assistant / limits:**
* No instructor approval is claimed. No group details were invented (names and IDs are placeholders).
* Market-data websites were not reachable from the build environment. The real-data part therefore
  uses two small **secondary-source** datasets (see `data/SOURCES.md`). No option quotes were used.
* Citations were checked against publisher or index pages where possible. The Kamal & Derman (1999)
  reference has no volume or page numbers because none were verified. Please confirm it in your library.
* The proposal was written on 13 November 2026, after the 31 October deadline. It is not backdated.

**What the group should do:** verify the derivations, run the code yourselves, and edit the text into
your own words where needed. Then state the AI use in whatever form your course requires. Replace this
draft with your final statement.
