import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import uproot
from collections import defaultdict, Counter

hep.style.use("CMS")

OUTDIR = "TrigPtMatchPlotsTMPlusXStatus1"
os.makedirs(OUTDIR, exist_ok=True)

def cms_header(ax):
    hep.cms.label("Internal", year=2022, data=False, lumi=None, com=13.6, ax=ax, loc=0)

def save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print(f"wrote {path}")

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python plot_ptmatch.py <TrigPtMatch.root>")

    t = uproot.open(sys.argv[1])["trigObjPtMatch/trigObjPtMatch"]
    d = t.arrays([
        "run", "lumi", "event",
        "to_pathIdx", "to_pt", "to_eta", "to_phi",
        "match_found",
        "match_dR", "match_dPtRel", "match_pt", "match_eta", "match_phi",
        "match_pdgId", "match_status", "match_motherId", "match_ancestorId",
        "match_fromTM", "match_tmIdx",
        "match_tm_pt", "match_tm_eta", "match_tm_phi",
        "nearDR_dR", "nearDR_dPtRel", "nearDR_pdgId", "nearDR_fromTM",
    ], library="np")

    n = len(d["to_pt"])
    found    = d["match_found"].astype(bool)
    fromTM   = d["match_fromTM"].astype(bool) & found
    notFromTM = found & ~fromTM

    print(f"total trigger objects: {n}")
    print(f"  with gen match in dR<0.3:  {found.sum()} ({found.mean():.3f})")
    print(f"  matched gen from TM:        {fromTM.sum()} ({fromTM.mean():.3f})")

    # ---- 1. dR distribution of pT-matched gen particle ----
    fig, ax = plt.subplots(figsize=(12, 8))
    bins = np.linspace(0, 0.3, 61)
    ax.hist(d["match_dR"][fromTM],   bins=bins, histtype="step", lw=2, color="navy",    label="pT-match from TM")
    ax.hist(d["match_dR"][notFromTM], bins=bins, histtype="step", lw=2, color="crimson", label="pT-match not TM")
    ax.set_xlabel(r"$\Delta R$(trig obj, pT-matched gen)")
    ax.set_ylabel("Trigger objects")
    ax.set_yscale("log")
    cms_header(ax)
    ax.legend()
    save(fig, "ptmatch_dR.png")

    # ---- 2. dPtRel distribution ----
    fig, ax = plt.subplots(figsize=(12, 8))
    bins = np.linspace(-2, 2, 81)
    ax.hist(d["match_dPtRel"][fromTM],    bins=bins, histtype="step", lw=2, color="navy",    label="pT-match from TM")
    ax.hist(d["match_dPtRel"][notFromTM], bins=bins, histtype="step", lw=2, color="crimson", label="pT-match not TM")
    ax.set_xlabel(r"$(p_T^{\rm trig} - p_T^{\rm gen}) / p_T^{\rm trig}$")
    ax.set_ylabel("Trigger objects")
    ax.set_yscale("log")
    cms_header(ax)
    ax.legend()
    save(fig, "ptmatch_dPtRel.png")

    # ---- 3. pT-match vs nearest-dR comparison: dR ----
    fig, ax = plt.subplots(figsize=(12, 8))
    bins = np.linspace(0, 0.3, 61)
    ax.hist(d["match_dR"][found],   bins=bins, histtype="step", lw=2, color="navy",   label="pT-match")
    ax.hist(d["nearDR_dR"][found],  bins=bins, histtype="step", lw=2, color="crimson", label="nearest dR")
    ax.set_xlabel(r"$\Delta R$ of matched gen particle")
    ax.set_ylabel("Trigger objects")
    ax.set_yscale("log")
    cms_header(ax)
    ax.legend()
    save(fig, "compare_dR.png")

    # ---- 4. pT-match vs nearest-dR comparison: dPtRel ----
    fig, ax = plt.subplots(figsize=(12, 8))
    bins = np.linspace(-2, 2, 81)
    ax.hist(d["match_dPtRel"][found],   bins=bins, histtype="step", lw=2, color="navy",    label="pT-match")
    ax.hist(d["nearDR_dPtRel"][found],  bins=bins, histtype="step", lw=2, color="crimson", label="nearest dR")
    ax.set_xlabel(r"$(p_T^{\rm trig} - p_T^{\rm gen}) / p_T^{\rm trig}$")
    ax.set_ylabel("Trigger objects")
    ax.set_yscale("log")
    cms_header(ax)
    ax.legend()
    save(fig, "compare_dPtRel.png")

    # ---- 5. fromTM comparison: pT-match vs nearest-dR ----
    nearDR_fromTM = d["nearDR_fromTM"].astype(bool) & found
    fig, ax = plt.subplots(figsize=(8, 6))
    cats = ["pT-match\nfrom TM", "nearest dR\nfrom TM"]
    vals = [fromTM.sum(), nearDR_fromTM.sum()]
    ax.bar(range(2), vals, color=["navy", "crimson"], edgecolor="black")
    ax.set_xticks(range(2))
    ax.set_xticklabels(cats)
    ax.set_ylabel("Trigger objects matched to TM electron")
    for i, v in enumerate(vals):
        ax.text(i, v, str(v), ha="center", va="bottom")
    cms_header(ax)
    save(fig, "compare_fromTM_counts.png")

    # ---- 6. pdgId of pT-matched gen particle ----
    fig, ax = plt.subplots(figsize=(12, 8))
    pdgids, counts = np.unique(np.abs(d["match_pdgId"][found]), return_counts=True)
    order = np.argsort(counts)[::-1][:15]  # top 15
    ax.bar(range(len(order)), counts[order], color="steelblue", edgecolor="black")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([str(p) for p in pdgids[order]], rotation=45)
    ax.set_xlabel("|pdgId| of pT-matched gen particle")
    ax.set_ylabel("Count")
    ax.set_yscale("log")
    ax.set_ylim(bottom=1)  # log-scale bars autoscale their floor to the smallest
                           # bar otherwise, which visually squashes small counts
    for i, c in zip(range(len(order)), counts[order]):
        ax.text(i, c, str(c), ha="center", va="bottom")
    cms_header(ax)
    save(fig, "ptmatch_pdgId.png")

    # ---- 7. 2D scatter: trig pT vs matched gen pT, split by pdgId category.
    # Categories chosen from the actual observed composition (checked via a
    # quick uproot pass first) rather than guessed: |pdgId| in this sample is
    # dominated by 211 (pion, 34%), 11 (electron, 30%), 22 (photon, 27%),
    # 321 (kaon, 10%) -- no muons at all, so that guessed category is dropped
    # in favor of pion/kaon, which turned out to be the two largest groups. ----
    pdgId = np.abs(d["match_pdgId"])
    is_ele = pdgId == 11
    cat_eleTM  = found & is_ele & fromTM
    cat_eleNot = found & is_ele & ~fromTM
    cat_pion   = found & (pdgId == 211) & ~is_ele
    cat_photon = found & (pdgId == 22) & ~is_ele
    cat_kaon   = found & (pdgId == 321) & ~is_ele
    cat_other  = found & ~cat_eleTM & ~cat_eleNot & ~cat_pion & ~cat_photon & ~cat_kaon

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(d["match_pt"][cat_other],  d["to_pt"][cat_other],  s=8,  alpha=0.3, color="lightgray", label=f"other ({cat_other.sum()})")
    ax.scatter(d["match_pt"][cat_kaon],   d["to_pt"][cat_kaon],   s=10, alpha=0.4, color="seagreen",  label=f"kaon (K$^\\pm$) ({cat_kaon.sum()})")
    ax.scatter(d["match_pt"][cat_photon], d["to_pt"][cat_photon], s=10, alpha=0.4, color="goldenrod", label=f"photon ({cat_photon.sum()})")
    ax.scatter(d["match_pt"][cat_pion],   d["to_pt"][cat_pion],   s=10, alpha=0.4, color="darkorchid", label=f"pion ($\\pi^\\pm$) ({cat_pion.sum()})")
    ax.scatter(d["match_pt"][cat_eleNot], d["to_pt"][cat_eleNot], s=12, alpha=0.5, color="royalblue", label=f"electron, not TM ({cat_eleNot.sum()})")
    ax.scatter(d["match_pt"][cat_eleTM],  d["to_pt"][cat_eleTM],  s=16, alpha=0.8, color="crimson",   label=f"electron, from TM ({cat_eleTM.sum()})")
    lim = np.percentile(d["to_pt"][found], 99) * 1.1 if found.any() else 10
    ax.plot([0, lim], [0, lim], "k--", label=r"$p_T^{\rm trig} = p_T^{\rm gen}$")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel(r"pT-matched gen $p_T$ [GeV]")
    ax.set_ylabel(r"Trigger object $p_T$ [GeV]")
    cms_header(ax)
    ax.legend(fontsize=12)
    save(fig, "ptmatch_pt2d.png")

    # ---- 8. same-TM analysis ----
    CONE = 0.3
    sel = fromTM & (d["match_dR"] < CONE) & (d["match_tmIdx"] >= 0)
    sel_idx = np.nonzero(sel)[0]
    ev_key = list(zip(d["run"][sel], d["lumi"][sel], d["event"][sel]))
    tmidx  = d["match_tmIdx"][sel]

    by_event = defaultdict(list)
    for k, tmi in zip(ev_key, tmidx):
        by_event[k].append(int(tmi))

    # also keep the array index alongside tmIdx, per event, so that once we
    # know which pairs share a TM we can look up their match_eta/match_phi
    # directly (no need to cross-reference the GenStudies ntuple by
    # run/lumi/event, which isn't a safe join key across different
    # production stages -- condor jobs reuse Run=1/Lumi=1/Event=1..N).
    by_event_idx = defaultdict(list)
    for k, tmi, arr_i in zip(ev_key, tmidx, sel_idx):
        by_event_idx[k].append((int(tmi), arr_i))

    n_events_with_match = len(by_event)
    n_single, n_sameTM, n_crossTM = 0, 0, 0
    tm_objcount = Counter()

    for k, tmis in by_event.items():
        c = Counter(tmis)
        for tm, cnt in c.items():
            tm_objcount[cnt] += 1
        if len(tmis) == 1:
            n_single += 1
        elif max(c.values()) >= 2:
            n_sameTM += 1
        else:
            n_crossTM += 1

    print(f"\n{'='*55}")
    print(f"SAME-TM ANALYSIS (pT-matched, dR<{CONE})")
    print(f"{'='*55}")
    print(f"events with >=1 TM-matched object: {n_events_with_match}")
    print(f"  single matched object only:       {n_single}")
    print(f"  >=2 objects -> SAME TM (pair):    {n_sameTM}")
    print(f"  >=2 objects -> all DIFFERENT TMs: {n_crossTM}")
    print("\nper-TM object multiplicity:")
    for cnt in sorted(tm_objcount):
        print(f"  {cnt} object(s): {tm_objcount[cnt]} TMs")

    fig, ax = plt.subplots(figsize=(8, 6))
    cats = ["1 obj", "same-TM\n(pair)", "cross-TM"]
    vals = [n_single, n_sameTM, n_crossTM]
    ax.bar(range(3), vals, color=["lightgray", "navy", "crimson"], edgecolor="black")
    ax.set_xticks(range(3))
    ax.set_xticklabels(cats)
    ax.set_ylabel("Events")
    for i, v in enumerate(vals):
        ax.text(i, v, str(v), ha="center", va="bottom")
    cms_header(ax)
    save(fig, "sameTM_classification.png")

    # ---- 9. dR between the two TM-matched electrons, for same-TM (pair) events.
    # These are the rare cases where >=2 trigger objects matched to the same
    # TM. But slimmedPatTrigger holds one trigger-object entry PER FILTER
    # STAGE of a path (L1 seed, calo filter, track filter, last filter...),
    # so two objects matching the same tmIdx often means two filter-stage
    # objects both landing on the SAME single electron, not the two distinct
    # sibling electrons. Only opposite-sign match_pdgId (11 vs -11) pairs are
    # genuine e+/e- sibling resolutions; same-sign pairs are counted
    # separately as duplicate/redundant matches to one electron. ----
    def dphi_wrap(p1, p2):
        return np.arctan2(np.sin(p1 - p2), np.cos(p1 - p2))

    pair_dR = []      # gen-level, from the matched gen electrons (match_eta/phi)
    pair_dR_reco = []  # trigger-object level (to_eta/phi) -- what actually
                       # determines whether the ECAL/L1 sees one object or two
    n_dup_same_electron = 0
    for k, entries in by_event_idx.items():
        tm_to_idx = defaultdict(list)
        for tmi, arr_i in entries:
            tm_to_idx[tmi].append(arr_i)
        for tmi, idxs in tm_to_idx.items():
            for i in range(len(idxs)):
                for j in range(i + 1, len(idxs)):
                    a, b = idxs[i], idxs[j]
                    if d["match_pdgId"][a] * d["match_pdgId"][b] >= 0:
                        n_dup_same_electron += 1
                        continue
                    deta = d["match_eta"][a] - d["match_eta"][b]
                    dphi = dphi_wrap(d["match_phi"][a], d["match_phi"][b])
                    pair_dR.append(np.hypot(deta, dphi))

                    deta_r = d["to_eta"][a] - d["to_eta"][b]
                    dphi_r = dphi_wrap(d["to_phi"][a], d["to_phi"][b])
                    pair_dR_reco.append(np.hypot(deta_r, dphi_r))
    pair_dR = np.array(pair_dR)
    pair_dR_reco = np.array(pair_dR_reco)

    print(f"\n{'='*55}")
    print(f"SAME-TM PAIR dR (genuine opposite-sign e+/e- sibling pairs)")
    print(f"{'='*55}")
    print(f"same-sign duplicate matches (same electron, multiple filter-stage objects): {n_dup_same_electron}")
    print(f"genuine e+/e- sibling pairs: {len(pair_dR)}")
    if len(pair_dR):
        print(f"  mean:   {pair_dR.mean():.3f}")
        print(f"  median: {np.median(pair_dR):.3f}")
        # 0.05 ~ ECAL supercluster / L1 trigger-tower granularity -- the
        # actual resolving scale, not an arbitrary round number.
        print(f"  frac(dR > 0.05): {(pair_dR > 0.05).mean()*100:.1f}%")

        print("\nper-pair: gen-level dR (production) vs trigger-object dR (ECAL/HLT position)")
        print(f"  {'gen dR':>8}  {'reco dR':>8}")
        for g, r in zip(pair_dR, pair_dR_reco):
            print(f"  {g:8.4f}  {r:8.4f}")

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.hist(pair_dR, bins=np.linspace(0, 0.5, 41), color="navy",
                edgecolor="black", histtype="stepfilled", alpha=0.7)
        ax.axvline(0.05, color="crimson", ls="--", lw=2, label="dR = 0.05 (ECAL/L1 granularity)")
        ax.set_xlabel(r"$\Delta R$ between the two TM-matched electrons")
        ax.set_ylabel("Pairs")
        ax.legend()
        cms_header(ax)
        save(fig, "sameTM_pair_dR.png")

    print("\nDone.")

if __name__ == "__main__":
    main()
