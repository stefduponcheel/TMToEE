import os
import numpy as np
import uproot
import matplotlib.pyplot as plt
import mplhep as hep

plt.style.use(hep.style.CMS)

FILES = {
    r"$\eta \to TM\gamma$":     "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/etaToTMGamma/20260508/Analysis/Ntuples/2022/ntuple_eta_merged.root",
    r"$B^{0} \to K^{*} TM$":    "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/B0ToKstarTM/20260509/Analysis/Ntuples/2022/ntuple_B0_merged.root",
    r"$B^{+} \to K^{+} TM$":    "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Analysis/Ntuples/2022/ntuple_Bplus_merged.root",
    r"$\omega \to TM\pi^{0}$":  "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/omegaToTMPi0/20260509/Analysis/Ntuples/2022/ntuple_Omega_merged.root",
    r"$D^{+} \to \pi^{+} TM$":  "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/DplusToPiplusTM/20260515/Analysis/Ntuples/2022/ntuple_Dplus_merged.root",
}

OUTDIR = "figures_efficiency"
os.makedirs(OUTDIR, exist_ok=True)

ELE_PT_CUT = 1.0  # GeV


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def get_tree(path):
    f = uproot.open(path)
    return f["genStudies/Events"]


def load():
    data = {}
    for label, path in FILES.items():
        t = get_tree(path)
        data[label] = t.arrays(library="np")
        print(f"{label}: {len(data[label]['tm_pt'])} entries")
    return data


def save(fig, fname):
    out = os.path.join(OUTDIR, fname)
    fig.savefig(out + ".png", dpi=300)
    fig.savefig(out + ".pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Efficiency calculation
# ---------------------------------------------------------------------------

def binom_err(p, n):
    return float(np.sqrt(p * (1 - p) / n)) if n > 0 else 0.0


def compute_electron_efficiency(data, ele_cut=ELE_PT_CUT):
    """For each process, fraction with ele1, ele2, or both above ele_cut."""
    results = {}
    for label, arrs in data.items():
        ele1 = np.asarray(arrs["ele1_pt"])
        ele2 = np.asarray(arrs["ele2_pt"])

        mask1 = np.isfinite(ele1)
        mask2 = np.isfinite(ele2)
        mask_both = mask1 & mask2

        n1 = int(mask1.sum())
        n2 = int(mask2.sum())
        n_both = int(mask_both.sum())

        f1 = float((ele1[mask1] > ele_cut).sum() / n1) if n1 > 0 else 0.0
        f2 = float((ele2[mask2] > ele_cut).sum() / n2) if n2 > 0 else 0.0
        f_both = (float(((ele1[mask_both] > ele_cut) & (ele2[mask_both] > ele_cut)).sum() / n_both)
                  if n_both > 0 else 0.0)

        results[label] = {
            "n_total": len(arrs["ele1_pt"]),
            "ele1": f1, "ele1_err": binom_err(f1, n1), "n1": n1,
            "ele2": f2, "ele2_err": binom_err(f2, n2), "n2": n2,
            "both": f_both, "both_err": binom_err(f_both, n_both), "n_both": n_both,
        }
    return results


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

def _plain(label):
    """Strip LaTeX for terminal printing."""
    return (label.replace("$", "")
                 .replace("\\to", "->")
                 .replace("\\gamma", "gamma")
                 .replace("\\omega", "omega")
                 .replace("\\pi", "pi")
                 .replace("\\eta", "eta")
                 .replace("\\", "")
                 .replace("{", "").replace("}", "")
                 .replace("^", ""))


def print_efficiency_table(eff, ele_cut=ELE_PT_CUT):
    print()
    print("=" * 100)
    print(f"Fraction of events with electron pT > {ele_cut:g} GeV (all entries)")
    print("=" * 100)
    print(f"{'Process':<28} {'N':>10}  {'ele1 [%]':>17} {'ele2 [%]':>17} {'both [%]':>17}")
    print("-" * 100)
    for label, r in eff.items():
        print(f"{_plain(label):<28} {r['n_total']:>10d}  "
              f"{100*r['ele1']:>7.2f} +/- {100*r['ele1_err']:<5.2f}  "
              f"{100*r['ele2']:>7.2f} +/- {100*r['ele2_err']:<5.2f}  "
              f"{100*r['both']:>7.2f} +/- {100*r['both_err']:<5.2f}")
    print("=" * 100)


def print_ratio_table(eff, key="both", ele_cut=ELE_PT_CUT):
    labels = list(eff.keys())
    print()
    print("=" * 110)
    print(f"Pairwise ratios of '{key}' fraction (pT > {ele_cut:g} GeV) :  row / column")
    print("=" * 110)
    # header
    header = f"{'':<28}" + "".join(f"{_plain(l):>18}" for l in labels)
    print(header)
    print("-" * 110)
    for ri in labels:
        row = f"{_plain(ri):<28}"
        for cj in labels:
            num = eff[ri][key]
            den = eff[cj][key]
            if den > 0 and num > 0:
                ratio = num / den
                rel = np.sqrt((eff[ri][key + "_err"] / num) ** 2
                              + (eff[cj][key + "_err"] / den) ** 2)
                err = ratio * rel
                row += f"{ratio:>9.3f}+/-{err:<6.3f}"
            else:
                row += f"{'--':>18}"
        print(row)
    print("=" * 110)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_efficiency_bar(eff, ele_cut=ELE_PT_CUT, fname="electron_pt_fraction"):
    labels = list(eff.keys())
    x = np.arange(len(labels))
    width = 0.27

    f1 = np.array([eff[l]["ele1"] for l in labels]) * 100
    e1 = np.array([eff[l]["ele1_err"] for l in labels]) * 100
    f2 = np.array([eff[l]["ele2"] for l in labels]) * 100
    e2 = np.array([eff[l]["ele2_err"] for l in labels]) * 100
    fb = np.array([eff[l]["both"] for l in labels]) * 100
    eb = np.array([eff[l]["both_err"] for l in labels]) * 100

    fig, ax = plt.subplots(figsize=(15, 9))
    ax.bar(x - width, f1, width, yerr=e1, capsize=4, label=r"$e_{1}$", edgecolor="black")
    ax.bar(x,         f2, width, yerr=e2, capsize=4, label=r"$e_{2}$", edgecolor="black")
    ax.bar(x + width, fb, width, yerr=eb, capsize=4, label=r"both $e$", edgecolor="black")

    for xi, val, err in zip(x - width, f1, e1):
        ax.text(xi, val + err + 1.0, f"{val:.1f}%", ha="center", fontsize=16)
    for xi, val, err in zip(x, f2, e2):
        ax.text(xi, val + err + 1.0, f"{val:.1f}%", ha="center", fontsize=16)
    for xi, val, err in zip(x + width, fb, eb):
        ax.text(xi, val + err + 1.0, f"{val:.1f}%", ha="center", fontsize=16)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel(rf"Fraction with $p_{{\mathrm{{T}}}} > {ele_cut:g}$ GeV [%]")

    top = max((f1 + e1).max(), (f2 + e2).max(), (fb + eb).max())
    ax.set_ylim(0, max(100, top * 1.18))
    ax.legend(frameon=False, loc="upper right")
    hep.cms.label("Internal", data=False, year=2022, ax=ax, lumi=None, com=13.6)
    fig.tight_layout()
    save(fig, fname)


def plot_efficiency_vs_cut(data, cuts=np.linspace(0.0, 15.0, 201),
                           fname="electron_pt_fraction_vs_cut",
                           key="both", logy=False):
    """Fraction of events passing varying ele pT cuts (turn-on curve)."""
    fig, ax = plt.subplots(figsize=(12, 9))
    for label, arrs in data.items():
        e1 = np.asarray(arrs["ele1_pt"])
        e2 = np.asarray(arrs["ele2_pt"])
        m = np.isfinite(e1) & np.isfinite(e2)
        e1, e2 = e1[m], e2[m]
        n = len(e1)
        if n == 0:
            continue
        if key == "both":
            frac = np.array([((e1 > c) & (e2 > c)).sum() / n for c in cuts])
        elif key == "ele1":
            frac = np.array([(e1 > c).sum() / n for c in cuts])
        elif key == "ele2":
            frac = np.array([(e2 > c).sum() / n for c in cuts])
        ax.plot(cuts, frac * 100, linewidth=3, label=label)

    ax.set_xlabel(r"Electron $p_{\mathrm{T}}$ threshold [GeV]")
    nice_key = {"both": r"both $e$", "ele1": r"$e_{1}$", "ele2": r"$e_{2}$"}[key]
    ax.set_ylabel(f"Fraction with {nice_key} above threshold [%]")
    ax.set_xlim(cuts[0], cuts[-1])
    step = cuts[1] - cuts[0]
    ax.text(0.98, 0.02, f"Sampled every {step:.2g} GeV",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=14, color="gray",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="lightgray", alpha=0.8))
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(1e-4, 200) 
    else:
        ax.set_ylim(0, 105)
        ax.set_xlim(0, 10)  # 



    ax.grid(True, which="both", alpha=0.3)
    ax.legend(frameon=False)
    hep.cms.label("Internal", data=False, year=2022, ax=ax, lumi=None, com=13.6)
    fig.tight_layout()
    save(fig, fname)

def print_both_gain_vs_eta(eff, ele_cut=ELE_PT_CUT):
    """Gain in 'both electrons > cut' fraction relative to eta -> TM gamma."""
    reference_label = r"$\eta \to TM\gamma$"
    if reference_label not in eff:
        print(f"Reference {reference_label!r} not found.")
        return

    ref = eff[reference_label]["both"]

    print()
    print("=" * 60)
    print(f"Gain in 'both e' (pT > {ele_cut:g} GeV) relative to "
          f"{_plain(reference_label)}")
    print("=" * 60)
    print(f"{'Process':<32}{'gain':>20}")
    print("-" * 60)
    for label, r in eff.items():
        g = r["both"] / ref if ref > 0 else 0.0
        marker = "  (ref)" if label == reference_label else ""
        print(f"{_plain(label):<32}{g:>15.2f}{marker}")
    print("=" * 60)
# ---------------------------------------------------------------------------

def main():
    data = load()

    eff = compute_electron_efficiency(data)
    print_efficiency_table(eff)
    print_ratio_table(eff, key="both")
    print_ratio_table(eff, key="ele2")

    plot_efficiency_bar(eff, fname=f"electron_pt_gt_{ELE_PT_CUT:g}GeV_fraction")
    for k in ("both", "ele2"):
        plot_efficiency_vs_cut(data, key=k, logy=False,
                               fname=f"electron_pt_fraction_vs_cut_{k}_lin")
        plot_efficiency_vs_cut(data, key=k, logy=True,
                               fname=f"electron_pt_fraction_vs_cut_{k}_log")
    print_both_gain_vs_eta(eff)
    print(f"\nResults in {OUTDIR}/")


if __name__ == "__main__":
    main()
