"""Figure 1 of the Economics Bulletin note: debt and region are the same ordering.

Plots each state's five-year mean debt-to-GSDP against its five-year mean log
FDI, with the marker showing the state's region. The point of the figure is that
the four regional groups separate cleanly along the debt axis, which is what
makes the fiscal reading and the regional reading observationally similar in a
ten-state panel.

Self-check: reproduces the regional mean debt figures published in the paper
(20.6, 26.2, 33.1, 34.5) before drawing anything.
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / 'data' / 'processed' / 'MASTER_PANEL_DATASET.csv'
OUT = ROOT / 'paper' / 'submission' / 'eb_short' / 'figures' / 'fig01_region.pdf'

REGION = {
    'Maharashtra': 'West', 'Gujarat': 'West',
    'Karnataka': 'South', 'Tamil Nadu': 'South', 'Telangana': 'South',
    'Haryana': 'North', 'Rajasthan': 'North', 'Uttar Pradesh': 'North',
    'Jharkhand': 'East', 'West Bengal': 'East',
}
# published in the paper, computed on all fifty state-year cells
PUBLISHED_MEAN_DEBT = {'West': 20.6, 'South': 26.2, 'North': 33.1, 'East': 34.5}

STYLE = {
    'West':  ('o', '#1b6ca8'),
    'South': ('s', '#2e8b57'),
    'North': ('^', '#c65d21'),
    'East':  ('D', '#8b2e5f'),
}
DEBT = 'debt (% of GSDP)'
LOGFDI = 'log_fdi (natural log, unitless)'


def load():
    d = pd.read_csv(PANEL)
    d['region'] = d['state'].map(REGION)
    if d['region'].isna().any():
        raise SystemExit('unmapped states: %s'
                         % sorted(d.loc[d['region'].isna(), 'state'].unique()))
    return d


def check_regional_means(d):
    """The figure is only worth drawing if it is the same data the text quotes."""
    got = d.groupby('region')[DEBT].mean().round(1)
    for region, published in PUBLISHED_MEAN_DEBT.items():
        assert abs(got[region] - published) < 0.05, (
            f'{region}: computed {got[region]}, paper reports {published}')
    return got


def main():
    d = load()
    means = check_regional_means(d)
    print('regional mean debt (%% GSDP), matches the paper:\n%s\n' % means)

    # log FDI is averaged over the years a state actually has, so Uttar Pradesh
    # contributes its three observed years rather than a total dragged down by
    # two censored ones.
    per_state = (d.groupby(['state', 'region'])
                   .agg(debt=(DEBT, 'mean'), log_fdi=(LOGFDI, 'mean'))
                   .reset_index())

    fig, ax = plt.subplots(figsize=(6.0, 3.9))
    for region, (marker, colour) in STYLE.items():
        g = per_state[per_state['region'] == region]
        ax.scatter(g['debt'], g['log_fdi'], marker=marker, c=colour, s=70,
                   edgecolors='white', linewidths=0.8, label=region, zorder=3)
        for _, r in g.iterrows():
            ax.annotate(r['state'], (r['debt'], r['log_fdi']),
                        textcoords='offset points', xytext=(6, -3),
                        fontsize=7.5, color='#333333')

    ax.set_xlabel('Five-year mean debt (% of GSDP)', fontsize=9)
    ax.set_ylabel('Five-year mean log FDI', fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.25, linewidth=0.5, zorder=0)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc='upper right', title='Region',
              title_fontsize=8)
    ax.set_xlim(15, 45)
    fig.tight_layout()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches='tight')
    fig.savefig(OUT.with_suffix('.png'), dpi=200, bbox_inches='tight')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
