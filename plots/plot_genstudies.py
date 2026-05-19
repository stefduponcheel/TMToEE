import argparse
import os

import uproot
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Input ROOT file")
    parser.add_argument("--outdir", default="figures", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # --- read tree ---
    f = uproot.open(args.infile)
    # tree is at genStudies/Events
    tree_path = "genStudies/Events"
    if tree_path not in f:
        # fallback if no subdirectory
        tree_path = "Events"
    t = f[tree_path]

    arrs = t.arrays(library="np")
    n = len(arrs["eta_pt"])
    print(f"Loaded {n} entries from {args.infile}")

    # --- CMS style ---
    plt.style.use(hep.style.CMS)
    def make_hist(values, bins, xlabel, fname,
                logy=False, xlim=None, color="#5790fc"):
        fig, ax = plt.subplots(figsize=(10, 8))
        counts, edges = np.histogram(values, bins=bins)
        hep.histplot(counts, edges, ax=ax, histtype="fill",
                        edgecolor="black", color=color, linewidth=1.0)

        ax.set_xlabel(xlabel)
        ax.set_ylabel("Entries")
        if xlim:
            ax.set_xlim(xlim)
        if logy:
            ax.set_yscale("log")
        hep.cms.label("Internal", data=False, ax=ax,
                        lumi=None, com=13.6)
 

        fig.tight_layout()
        out = os.path.join(args.outdir, fname)
        fig.savefig(out + "_AOD.png", dpi=300)
        plt.close(fig)
        print(f"  wrote {out}_AOD.png")

    # Eta meson kinematics
    make_hist(arrs["eta_pt"], np.linspace(0, 5, 100),
              r"$p_{\mathrm{T}}^{\eta}$ [GeV]", "eta_pt")
    make_hist(arrs["eta_eta"], np.linspace(-5, 5, 25),
              r"$\eta_{\eta}$", "eta_eta")


    # TM kinematics
    make_hist(arrs["tm_pt"], np.linspace(0, 5, 100),
              r"$p_{\mathrm{T}}^{TM}$ [GeV]", "tm_pt")
    make_hist(arrs["tm_eta"], np.linspace(-2.5, 2.5, 25),
              r"$\eta^{TM}$", "tm_eta")

    # Electrons
    make_hist(arrs["ele1_pt"], np.linspace(0, 2, 50),
              r"$p_{\mathrm{T}}^{e^-}$ [GeV]", "ele1_pt")
    make_hist(arrs["ele2_pt"], np.linspace(0, 2, 50),
              r"$p_{\mathrm{T}}^{e^+}$ [GeV]", "ele2_pt")
    make_hist(arrs["ele_dR"], np.linspace(0, 5, 51),
              r"$\Delta R(e^+, e^-)$", "ele_dR_log")

    print(f"\nAll plots in: {args.outdir}/")


if __name__ == "__main__":
    main()
