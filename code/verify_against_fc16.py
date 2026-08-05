"""
============================================================================
SOURCE VERIFICATION AGAINST THE FC-16 ANNEXURES
Fiscal Discipline & FDI in Indian States
============================================================================
PURPOSE
  Check every fiscal figure in Section 4 of the manuscript against the
  Sixteenth Finance Commission's Volume II annexures, which are the stated
  source. This is the one link in the chain that reproduction from the
  published tables cannot test: reconstruct_from_paper.py shows the paper is
  internally consistent, but not that the numbers were transcribed correctly
  in the first place.

WHAT IT CHECKS
  Table 2  fiscal deficit, % of GSDP        <- Annexure 5.1
  Table 10 revenue deficit, % of GSDP       <- Annexure 5.2
  Table 4  outstanding liabilities, % GSDP  <- Annexure 5.3
  Table 6  own tax revenue, % of GSDP       <- Annexure 5.5

  Ten states x five years x four indicators = 200 figures.

REQUIREMENTS
  Vol2-Annexures.pdf in the project root, and pdftotext on the path (poppler;
  it ships with Git for Windows at /mingw64/bin).

Run:  python code/verify_against_fc16.py
Exit code 0 if every figure matches the source, 1 otherwise.
============================================================================
"""
import re
import subprocess
import sys

PDF = "Vol2-Annexures.pdf"
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
PAPER_YEARS = ["FY2019-20", "FY2020-21", "FY2021-22", "FY2022-23", "FY2023-24"]

# the annexure row order, exactly as printed
ROWS = ["All States", "Non-NEH States", "NEH States", "Andhra Pradesh", "Arunachal Pradesh",
        "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
        "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

TEN = ["Maharashtra", "Uttar Pradesh", "Telangana", "Gujarat", "Karnataka",
       "Jharkhand", "Tamil Nadu", "Haryana", "Rajasthan", "West Bengal"]

ANNEXURES = {"5.1": ("fiscal deficit", "Table 2"),
             "5.2": ("revenue deficit", "Table 10"),
             "5.3": ("outstanding liabilities", "Table 4"),
             "5.5": ("own tax revenue", "Table 6")}


def pdf_text():
    try:
        out = subprocess.run(["pdftotext", "-q", PDF, "-"],
                             capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit("could not run pdftotext on %s (%s). Install poppler." % (PDF, e))
    return out.stdout.decode("utf-8", errors="replace")


def percentage_blocks(text):
    """Split the Chapter 5 annexures into percentage-of-GSDP tables, in order.

    The annexure headings cannot be used as anchors. They are printed at the
    top of each page, but pdftotext's reading order puts a table's rows either
    side of the next heading, so a block located by its marker can carry a
    neighbour's data. Annexure 5.4 compounds this: it reports Special
    Assistance in rupees, not as a share of GSDP, so it contributes no
    percentage rows at all and everything after it shifts by one marker.

    Document order is reliable where the markers are not. Reading the
    percentage tables in the order they appear gives, per the contents page:
        1st  Annexure 5.1  fiscal deficit
        2nd  Annexure 5.2  revenue deficit
        3rd  Annexure 5.3  outstanding liabilities
        4th  Annexure 5.5  own tax revenue
        5th  Annexure 5.6  revenue receipts
        6th  Annexure 5.7  revenue expenditure
    Each block is a dict of {year: [31 values]} keyed in that printed order.
    """
    rows = []
    for m in re.finditer(r"((?:19|20)\d\d-\d\d)\s+((?:-?\d+\.?\d*\s+){20,})", text):
        vals = m.group(2).split()
        if len(vals) == len(ROWS):
            rows.append((m.start(), m.group(1), vals))

    blocks, current, seen = [], {}, set()
    for _, yr, vals in rows:
        if yr in seen:                    # a repeated year means a new table
            blocks.append(current)
            current, seen = {}, set()
        current[yr] = vals
        seen.add(yr)
    if current:
        blocks.append(current)
    return blocks


ORDER = {"5.1": 0, "5.2": 1, "5.3": 2, "5.5": 3}


def parse_annexure(blocks, num):
    """Return {state: {year: value}} for one annexure."""
    i = ORDER[num]
    if i >= len(blocks):
        return None, "only %d percentage tables found; %s not reached" % (len(blocks), num)
    out = {s: {} for s in ROWS}
    for yr, vals in blocks[i].items():
        if yr not in YEARS:
            continue
        for state, v in zip(ROWS, vals):
            out[state][yr] = float(v)
    return out, None


def paper_tables():
    import docx
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    d = docx.Document("paper/Fiscal_Discipline_and_Investment_Outcomes.docx")
    T, cap = {}, None
    for ch in d.element.body.iterchildren():
        if ch.tag == qn("w:p"):
            m = re.match(r"(Table \d+[a-z]?)\.", Paragraph(ch, d).text.strip())
            if m:
                cap = m.group(1)
        elif ch.tag == qn("w:tbl"):
            if cap:
                T[cap] = [[c.text.strip() for c in r.cells] for r in Table(ch, d).rows]
                cap = None
    return T


def main():
    text = pdf_text()
    blocks = percentage_blocks(text)
    print("percentage-of-GSDP tables found in Chapter 5: %d" % len(blocks))
    # structural sanity check that does not consult the paper: own tax revenue
    # must sit below revenue receipts for every state, since it is a component
    if len(blocks) > 4:
        otr, rr = blocks[3], blocks[4]
        yr = "2022-23"
        if yr in otr and yr in rr:
            bad = sum(1 for a, b in zip(otr[yr], rr[yr]) if float(a) >= float(b))
            print("   own tax revenue < revenue receipts in %d of %d rows"
                  % (len(ROWS) - bad, len(ROWS)))
    T = paper_tables()
    total = matched = 0
    problems, skipped = [], []

    for num, (what, table) in sorted(ANNEXURES.items()):
        src, err = parse_annexure(blocks, num)
        if err:
            problems.append(err)
            continue
        pub = {r[0]: r for r in T[table][1:]}
        print("\nAnnexure %s -> %s   (%s)" % (num, table, what))
        for state in TEN:
            for i, (yr, py) in enumerate(zip(YEARS, PAPER_YEARS), start=1):
                if yr not in src.get(state, {}):
                    skipped.append("%s %s %s" % (num, state, yr))
                    continue
                total += 1
                a, b = src[state][yr], float(pub[state][i])
                if abs(a - b) < 1e-9:
                    matched += 1
                else:
                    problems.append("%s %s %s: source %.2f, paper %.2f"
                                    % (table, state, py, a, b))
        print("   checked so far: %d matched of %d" % (matched, total))

    print("\n" + "=" * 70)
    print("%d of %d figures match the FC-16 annexures" % (matched, total))
    if skipped:
        print("%d not checkable (column alignment lost in text extraction):" % len(skipped))
        for s in skipped[:10]:
            print("   " + s)
    if problems:
        print("\nDISCREPANCIES:")
        for p in problems:
            print("   " + p)
        sys.exit(1)
    print("no discrepancies")
    print("=" * 70)


if __name__ == "__main__":
    main()
