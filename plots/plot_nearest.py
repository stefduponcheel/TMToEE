#!/usr/bin/env python3
"""
 All plots are written to ./TrigObjectMatching/ in CMS style (mplhep).

Usage:
  python plot_nearest.py trignearest_merged.root
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import uproot
from collections import defaultdict, Counter

# CMS style
hep.style.use("CMS")

OUTDIR = "TrigObjectMatching"
os.makedirs(OUTDIR, exist_ok=True)

# header used on every plot
def cms_header(ax, lumi_text="2022 (13.6 TeV)"):
    hep.cms.label("Internal",year = 2022, data=False, lumi=None,
                  com=13.6, ax=ax, loc=0)

def save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print(f"wrote {path}")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python plot_nearest.py <trignearest.root>")

    t = uproot.open(sys.argv[1])["trigObjNearest/trigObj"]
    d = t.arrays(["run","lumi","event","to_pathIdx","to_pt","to_eta",
                  "near_dR","near_ele_pt","near_dPtRel",
                  "near_fromTM","near_ancestorId","near_tmIdx",
                  "near_tm_pt","near_tm_eta"], library="np")

    n = len(d["to_pt"])
    fromTM = d["near_fromTM"].astype(bool)
    print(f"total trigger objects (fired paths): {n}")
    print(f"  nearest electron from TM: {fromTM.sum()} ({fromTM.mean():.3f})")

    # ---- 1. dR distribution, TM vs not ----
    fig, ax = plt.subplots(figsize=(12, 8))
    bins = np.linspace(0, 1.0, 51)
    ax.hist(d["near_dR"][fromTM],  bins=bins, histtype="step", lw=2, color="navy",   label="nearest e from TM")
    ax.hist(d["near_dR"][~fromTM], bins=bins, histtype="step", lw=2, color="crimson", label="nearest e NOT from TM")
    ax.axvline(0.1,  color="gray",  ls="--", label="0.1")
    ax.axvline(0.03, color="green", ls=":",  label="0.03")
    ax.set_xlabel(r"$\Delta R$(trig obj, nearest gen $e$)  [no cone]")
    ax.set_ylabel("Trigger objects")
    ax.set_yscale("log")
    cms_header(ax)
    ax.legend()
    save(fig, "nearest_dR.png")

    # ---- 2. dR zoom ----
    fig, ax = plt.subplots(figsize=(12, 8))
    bins = np.linspace(0, 0.2, 41)
    ax.hist(d["near_dR"][fromTM],  bins=bins, histtype="step", lw=2, color="navy",   label="from TM")
    ax.hist(d["near_dR"][~fromTM], bins=bins, histtype="step", lw=2, color="crimson", label="not TM")
    ax.axvline(0.1,  color="gray",  ls="--", label="0.1")
    ax.axvline(0.03, color="green", ls=":",  label="0.03")
    ax.set_xlabel(r"$\Delta R$ (zoom)")
    ax.set_ylabel("Trigger objects")
    cms_header(ax)
    ax.legend()
    save(fig, "nearest_dR_zoom.png")

    # ---- 3. object pt vs nearest-electron pt (colored by TM origin) ----
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(d["near_ele_pt"][~fromTM], d["to_pt"][~fromTM], s=10, alpha=0.35, color="crimson", label="not TM")
    ax.scatter(d["near_ele_pt"][fromTM],  d["to_pt"][fromTM],  s=14, alpha=0.7,  color="navy",   label="from TM")
    lim = np.percentile(d["to_pt"], 99) * 1.1
    ax.plot([0, lim], [0, lim], "k--", label=r"obj $p_T$ = ele $p_T$")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel(r"Nearest gen electron $p_{T}$ [GeV]")
    ax.set_ylabel(r"Trigger object $p_{T}$ [GeV]")
    cms_header(ax)
    ax.legend()
    save(fig, "nearest_pt2d.png")

    # ---- 4. cut-scan table ----
    tm_dR = d["near_dR"][fromTM]
    print("\nTM-origin nearest electrons, dR cut efficiency:")
    for c in (0.01, 0.02, 0.03, 0.05, 0.1, 0.2):
        print(f"  dR<{c:<5}: {(tm_dR < c).sum():>5} ({(tm_dR < c).mean():.3f})")

    # ================= SAME-TM ANALYSIS =================
    CONE = 0.1
    sel = fromTM & (d["near_dR"] < CONE) & (d["near_tmIdx"] >= 0)

    ev_key = list(zip(d["run"][sel], d["lumi"][sel], d["event"][sel]))
    tmidx  = d["near_tmIdx"][sel]
    by_event = defaultdict(list)
    for k, tmi in zip(ev_key, tmidx):
        by_event[k].append(int(tmi))

    n_events_with_match = len(by_event)
    n_events_sameTM    = 0
    n_events_crossTM   = 0
    n_events_singleobj = 0
    tm_objcount_hist   = Counter()

    for k, tmis in by_event.items():
        c = Counter(tmis)
        for tm, cnt in c.items():
            tm_objcount_hist[cnt] += 1
        max_per_tm = max(c.values())
        n_distinct_tm = len(c)
        if len(tmis) == 1:
            n_events_singleobj += 1
        elif max_per_tm >= 2:
            n_events_sameTM += 1
        elif n_distinct_tm >= 2:
            n_events_crossTM += 1

    print("\n" + "=" * 55)
    print(f"SAME-TM ANALYSIS (objects with TM-origin e, dR<{CONE})")
    print("=" * 55)
    print(f"events with >=1 TM-matched object: {n_events_with_match}")
    print(f"  single matched object only:       {n_events_singleobj}")
    print(f"  >=2 objects -> SAME TM (pair):     {n_events_sameTM}")
    print(f"  >=2 objects -> all DIFFERENT TMs:  {n_events_crossTM}")
    print("\nper-TM object multiplicity (how many trig objects point to one TM):")
    for cnt in sorted(tm_objcount_hist):
        print(f"  {cnt} object(s): {tm_objcount_hist[cnt]} TMs")

    # bar chart of the event classification
    fig, ax = plt.subplots(figsize=(8, 6))
    cats = ["1 obj", "same-TM\n(pair)", "cross-TM"]
    vals = [n_events_singleobj, n_events_sameTM, n_events_crossTM]
    ax.bar(range(3), vals, color=["lightgray", "navy", "crimson"], edgecolor="black")
    ax.set_xticks(range(3))
    ax.set_xticklabels(cats)
    ax.set_ylabel("Events")
    cms_header(ax)
    ax.set_title(f"Fired-event classification (TM-matched objects, $\\Delta R<{CONE}$)", pad=20)
    for i, v in enumerate(vals):
        ax.text(i, v, str(v), ha="center", va="bottom")
    save(fig, "sameTM_classification.png")

    # ---- ALL-objects pt2d (plain, single color) ----
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(d["near_ele_pt"], d["to_pt"], s=10, alpha=0.4, color="navy")
    lim = max(d["to_pt"].max(), d["near_ele_pt"].max()) * 1.05 if n else 10
    ax.plot([0, lim], [0, lim], "r--", label=r"obj $p_T$ = ele $p_T$")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel(r"Nearest gen electron $p_{T}$ [GeV]")
    ax.set_ylabel(r"Trigger object $p_{T}$ [GeV]")
    cms_header(ax)
    ax.legend()
    save(fig, "pt2d_all.png")

    print("\nDone.")


if __name__ == "__main__":
    main()
