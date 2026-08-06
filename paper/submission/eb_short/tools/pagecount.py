"""Check the Economics Bulletin prose budget.

The journal's rule is "seven printed pages or less excluding tables, figures,
appendices and references". There is no way to read that off the compiled PDF
directly, so this compiles a second copy with every table, figure and the
reference and data-availability sections stripped out, and counts the pages that
remain. That stripped count is the number the seven-page limit applies to.

Usage:  python tools/pagecount.py
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
MAIN = HERE / 'main.tex'


def pdflatex(texfile, workdir):
    for _ in range(2):                       # twice, for cross-references
        r = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             texfile.name],
            cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        tail = '\n'.join(r.stdout.splitlines()[-25:])
        sys.exit('pdflatex failed:\n' + tail)
    log = (workdir / (texfile.stem + '.log')).read_text(errors='ignore')
    m = re.search(r'Output written on .*?\((\d+) pages', log)
    if not m:
        sys.exit('could not find a page count in the log')
    return int(m.group(1))


def strip_prose_only(text):
    """Remove floats and the back matter, leaving only body prose."""
    text = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '', text, flags=re.S)
    text = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', text, flags=re.S)
    # everything from the data-availability section to the end is back matter
    i = text.find(r'\section*{Data and code availability}')
    if i < 0:
        sys.exit('could not find the back matter marker')
    return text[:i] + '\n\\end{document}\n'


def main():
    src = MAIN.read_text(encoding='utf-8')

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        shutil.copy(MAIN, work / 'main.tex')
        figures = HERE / 'figures'
        if figures.is_dir():          # the full build needs them; the prose one does not
            shutil.copytree(figures, work / 'figures')
        total = pdflatex(work / 'main.tex', work)

        (work / 'prose.tex').write_text(strip_prose_only(src), encoding='utf-8')
        prose = pdflatex(work / 'prose.tex', work)

    print(f'total pages (as submitted): {total}')
    print(f'prose pages (tables, figures and back matter stripped): {prose}')
    print()
    if prose <= 7:
        print(f'WITHIN the seven-page limit, {7 - prose} to spare.')
    else:
        print(f'OVER the seven-page limit by {prose - 7}. Cut prose.')
        sys.exit(1)


if __name__ == '__main__':
    main()
