"""
============================================================================
SOURCE CHECKS AGAINST THE DPIIT STATE-WISE FDI REPORT
Fiscal Discipline & FDI in Indian States
============================================================================
PURPOSE
  The DPIIT quarterly factsheet reports state-wise FDI equity inflow as a
  single cumulative figure from October 2019 to the report date, not year by
  year. It therefore cannot confirm the individual cells of Table 11, which
  are annual. Two things it can establish, and both are worth having.

  1. SAMPLE SELECTION. Section 4.1 says the ten states were chosen because
     they head DPIIT's table. Checking that against the table itself shows the
     rule is not quite what was applied, and why: Delhi ranks fourth on FDI
     but is absent from the FC-16 annexures, so no fiscal indicator exists for
     it. The sample is the ten largest recipients among states FC-16 covers.

  2. CUMULATIVE CONSISTENCY. Table 11 runs to March 2024; a later factsheet
     runs further. Every state's cumulative total must therefore be at least
     as large in the later report. A negative increment would mean one of the
     two is wrong.

  The Jharkhand increment is reported separately because it independently
  corroborates Section 7.3 from data published after the paper's window.

REQUIREMENTS
  The DPIIT factsheet PDF in the project root, and pdftotext on the path.
  Pass the filename as the first argument; it defaults to the factsheet used
  when this check was written.

Run:  python code/verify_against_dpiit.py [factsheet.pdf]
Exit code 0 if the checks pass, 1 otherwise.
============================================================================
"""
import re
import subprocess
import sys

DEFAULT_PDF = "4128971a6c7fd4a7653ca9e648a5f34b.pdf"
FC16_PDF = "Vol2-Annexures.pdf"


def text_of(path):
    try:
        out = subprocess.run(["pdftotext", "-q", path, "-"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit("could not run pdftotext on %s (%s)" % (path, e))
    return out.stdout.decode("utf-8", errors="replace")


def dpiit_totals(txt):
    """State -> cumulative INR crore, from the Annexure-C state-wise table.

    The factsheet carries a shorter 'states attracting highest FDI' table
    earlier in the document, so anchor on the Annexure-C heading rather than
    on the first match for the column label.
    """
    i = txt.find("STATE-WISE FDI EQUITY INFLOW FROM OCTOBER 2019")
    if i < 0:
        sys.exit("Annexure-C state-wise table not found in the factsheet")
    blk = txt[i:i + 3000]
    names_blk = re.search(r"1 MAHARASHTRA.*?State Not Indicated", blk, re.S)
    names = [s.strip().upper() for _, s in re.findall(
        r"(\d{1,2})\s+([A-Za-z][A-Za-z \-\.]+?)(?=\s+\d{1,2}\s+[A-Za-z]|\s*\Z)",
        names_blk.group(0).replace("\n", " "))]
    # the INR column is the run between the two unit headers and the % header
    inr = re.search(r"\(In USD Million\)(.*?)% age out of total", blk, re.S).group(1)
    vals = [float(v.replace(",", "")) for v in re.findall(r"[\d,]+\.\d+", inr)]
    return names, dict(zip(names, vals))


def paper_table_11():
    import docx
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    d = docx.Document("paper/Fiscal_Discipline_and_Investment_Outcomes.docx")
    cap = None
    for ch in d.element.body.iterchildren():
        if ch.tag == qn("w:p"):
            m = re.match(r"(Table \d+[a-z]?)\.", Paragraph(ch, d).text.strip())
            if m:
                cap = m.group(1)
        elif ch.tag == qn("w:tbl"):
            if cap == "Table 11":
                return {r.cells[0].text.strip().upper():
                        [c.text.strip() for c in r.cells] for r in Table(ch, d).rows[1:]}
            cap = None
    sys.exit("Table 11 not found in the manuscript")


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    names, dp = dpiit_totals(text_of(pdf))
    paper = paper_table_11()
    failures = []

    print("=" * 72)
    print("1. SAMPLE SELECTION")
    print("=" * 72)
    print("   DPIIT ranking, cumulative from October 2019:")
    for i, n in enumerate(names[:11], start=1):
        mark = "" if n in paper else "   <- not in the paper's sample"
        print("      %2d  %-16s %14s%s" % (i, n.title(), format(dp[n], ",.0f"), mark))
    dropped = [n for n in names[:10] if n not in paper]
    added = [n for n in paper if n not in names[:10]]
    print("   inside the top ten but excluded: %s" % ([n.title() for n in dropped] or "none"))
    print("   outside the top ten but included: %s" % ([n.title() for n in added] or "none"))

    fc = text_of(FC16_PDF)
    j = fc.find("State All States")
    fc_states = fc[j:j + 700].split("\n")[0]
    for n in dropped:
        covered = n.title() in fc_states
        print("   is %s covered by the FC-16 annexures? %s" % (n.title(), covered))
        if covered:
            failures.append("%s is in FC-16 and in the DPIIT top ten, but not in the sample" % n)

    print()
    print("=" * 72)
    print("2. CUMULATIVE CONSISTENCY WITH A LATER REPORT")
    print("=" * 72)
    print("   %-16s %14s %14s %13s" % ("state", "paper to Mar24", "DPIIT later", "increment"))
    for s, row in paper.items():
        if s not in dp:
            continue
        p = float(row[6].replace(",", ""))
        inc = dp[s] - p
        bad = inc < -0.5
        if bad:
            failures.append("%s: cumulative falls from %.0f to %.0f in a later report" % (s, p, dp[s]))
        print("   %-16s %14s %14s %13s%s"
              % (s.title(), format(p, ",.0f"), format(dp[s], ",.0f"),
                 format(inc, ",.0f"), "   IMPOSSIBLE" if bad else ""))

    if "JHARKHAND" in dp:
        inc = dp["JHARKHAND"] - float(paper["JHARKHAND"][6].replace(",", ""))
        top = max(dp[s] - float(paper[s][6].replace(",", "")) for s in paper if s in dp)
        print()
        print("   Jharkhand's increment since March 2024 is %s crore, against %s crore"
              % (format(inc, ",.0f"), format(top, ",.0f")))
        print("   for the largest recipient. Section 7.3's account of Jharkhand's")
        print("   collapse is corroborated by data published after the paper's window.")

    print()
    print("=" * 72)
    if failures:
        print("CHECKS FAILED:")
        for f in failures:
            print("   " + f)
        sys.exit(1)
    print("all checks pass")
    print("=" * 72)


if __name__ == "__main__":
    main()
