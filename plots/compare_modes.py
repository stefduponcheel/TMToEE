import os
import uproot
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

plt.style.use(hep.style.CMS)

FILES = {
    r"$\eta \to TM\gamma$":     "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/etaToTMGamma/20260508/Analysis/Ntuples/2022/ntuple_eta_merged.root",
    # r"$B^{0} \to K^{*} TM$":    "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/B0ToKstarTM/20260509/Analysis/Ntuples/2022/ntuple_B0_merged.root",
    # r"$B^{+} \to K^{+} TM$":    "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Analysis/Ntuples/2022/ntuple_Bplus_merged.root",
    # r"$\omega \to TM\pi^{0}$":  "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/omegaToTMPi0/20260509/Analysis/Ntuples/2022/ntuple_Omega_merged.root",
    # r"$D^{+} \to \pi^{+} TM$":  "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/DplusToPiplusTM/20260515/Analysis/Ntuples/2022/ntuple_Dplus_merged.root",
}

OUTDIR = "figures_compareV3"
os.makedirs(OUTDIR, exist_ok=True)


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


def clean(x):
    x = np.asarray(x)
    return x[np.isfinite(x)]


def save(fig, fname):
    out = os.path.join(OUTDIR, fname)
    fig.savefig(out + ".png", dpi=300)
    plt.close(fig)


def plot_overlay(data, branch, bins, xlabel, fname, logy=False, xlim=None):
    fig, ax = plt.subplots(figsize=(12, 10))

    for label, arrs in data.items():
        if branch not in arrs:
            continue

        vals = clean(arrs[branch])
        counts, edges = np.histogram(vals, bins=bins)

            # if counts.sum() > 0:
            #     counts = counts / counts.sum()

        hep.histplot(counts, edges, ax=ax, histtype="step",
                     linewidth=3, label=label)

    ax.set_xlabel(xlabel)
    # ax.set_ylabel("Normalized entries")
    if xlim:
        ax.set_xlim(*xlim)
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(bottom=1,top= 1e6)

    ax.legend(frameon=False)
    hep.cms.label("Internal", data=False, year=2022, ax=ax, lumi=None, com=13.6)
    fig.tight_layout()
    save(fig, fname)


def plot_single_channel_particles(data, label, particles):
    for branch, bins, xlabel, fname in particles:
        if branch not in data[label]:
            continue
        fig, ax = plt.subplots(figsize=(12, 10))

        vals = clean(data[label][branch])
        counts, edges = np.histogram(vals, bins=bins)

        hep.histplot(counts, edges, ax=ax, histtype="fill",
                     edgecolor="black", linewidth=2.0, label=label)

        ax.set_xlabel(xlabel)
        ax.set_ylabel("Entries")
        ax.legend(frameon=False)
        hep.cms.label("Internal", data=False, year=2022, ax=ax, lumi=None, com=13.6)
        fig.tight_layout()
        save(fig, fname.replace("/", "_"))

def plot_overlay_logx(data, branch, bins, xlabel, fname, logy=True, xlim=None):
    """Like plot_overlay, but with log-scaled x-axis. `bins` must be log-spaced."""
    fig, ax = plt.subplots(figsize=(12, 10))

    for label, arrs in data.items():
        if branch not in arrs:
            continue

        vals = clean(arrs[branch])
        # log binning is undefined at 0 — drop those entries
        vals = vals[vals > 0]
        counts, edges = np.histogram(vals, bins=bins)

        # if counts.sum() > 0:
        #     counts = counts / counts.sum()

        hep.histplot(counts, edges, ax=ax, histtype="step",
                     linewidth=3, label=label)

    ax.set_xlabel(xlabel)
    # ax.set_ylabel("Normalized entries")
    ax.set_xscale("log")
    if xlim:
        ax.set_xlim(*xlim)
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(bottom=1e-5)

    ax.legend(frameon=False)
    hep.cms.label("Internal", data=False, year=2022, ax=ax, lumi=None, com=13.6)
    fig.tight_layout()
    save(fig, fname)

def main():
    data = load()

    # Tuple format: (branch, bins, xlabel, fname [, logy [, xlim]])
    common_plots = [
        # mother kinematics
        # ("mom_pt",  np.linspace(0, 25, 200),     r"Mother $p_{\mathrm{T}}$ [GeV]", "common_mother_pt"),
        # ("mom_pt",  np.linspace(0, 25, 200),     r"Mother $p_{\mathrm{T}}$ [GeV]", "common_mother_pt_log", True),
        # ("mom_eta", np.linspace(-4, 4, 81),     r"Mother $\eta$", "common_mother_eta"),
        # ("mom_phi", np.linspace(-3.2, 3.2, 65), r"Mother $\phi$", "common_mother_phi"),

        # # TM kinematics
        # ("tm_pt",   np.linspace(0, 25, 200),     r"TM $p_{\mathrm{T}}$ [GeV]", "common_tm_pt"),
        # ("tm_pt",   np.linspace(0, 25, 200),     r"TM $p_{\mathrm{T}}$ [GeV]", "common_tm_pt_log", True),
        # ("tm_pt",   np.linspace(0, 1, 201),     r"TM $p_{\mathrm{T}}$ [GeV]", "common_tm_pt_zoom", False, (0, 1)),
        # ("tm_eta",  np.linspace(-4, 4, 81),     r"TM $\eta$", "common_tm_eta"),
        # ("tm_phi",  np.linspace(-3.2, 3.2, 65), r"TM $\phi$", "common_tm_phi"),
        # ("tm_Lxyz", np.linspace(0, 100, 401),   r"TM $L_{xyz}$ [cm]", "common_tm_Lxyz", True),

        # # electron kinematics
        ("ele1_pt",  np.linspace(0, 25, 200),    r"$e_{1}$ $p_{\mathrm{T}}$ [GeV]", "common_ele1_pt", True),
        # ("ele1_pt",  np.linspace(0, 25, 200),    r"$e_{1}$ $p_{\mathrm{T}}$ [GeV]", "common_ele1_pt_log", True),
        ("ele2_pt",  np.linspace(0, 25, 200),    r"$e_{2}$ $p_{\mathrm{T}}$ [GeV]", "common_ele2_pt", True),
    #     ("ele2_pt",  np.linspace(0, 25, 200),    r"$e_{2}$ $p_{\mathrm{T}}$ [GeV]", "common_ele2_pt_log", True),
    #     ("ele1_pt",  np.linspace(0, 1, 201),    r"$e_{1}$ $p_{\mathrm{T}}$ [GeV]", "common_ele1_pt_zoom", False, (0, 1)),
    #     ("ele2_pt",  np.linspace(0, 1, 201),    r"$e_{2}$ $p_{\mathrm{T}}$ [GeV]", "common_ele2_pt_zoom", False, (0, 1)),
    #     ("ele1_eta", np.linspace(-4, 4, 81),    r"$e_{1}$ $\eta$", "common_ele1_eta"),
    #     ("ele2_eta", np.linspace(-4, 4, 81),    r"$e_{2}$ $\eta$", "common_ele2_eta"),
    #     ("ele_dR",   np.linspace(0, 5, 101),    r"$\Delta R(e^{+}, e^{-})$", "common_ele_dR"),
    #     ("ele_dR",   np.linspace(0, 5, 101),    r"$\Delta R(e^{+}, e^{-})$", "common_ele_dR_log", True),
     ]

    for item in common_plots:
        plot_overlay(data, *item)

    # particle_plots = {
    #     r"$B^{0} \to K^{*} TM$": [
    #         ("kaon_pt",   np.linspace(0, 5, 201),  r"$K$ $p_{\mathrm{T}}$ [GeV]", "B0_kaon_pt"),
    #         ("kaon_eta",  np.linspace(-4, 4, 81),  r"$K$ $\eta$", "B0_kaon_eta"),
    #         ("pion_pt",   np.linspace(0, 5, 201),  r"$\pi$ $p_{\mathrm{T}}$ [GeV]", "B0_pion_pt"),
    #         ("pion_eta",  np.linspace(-4, 4, 81),  r"$\pi$ $\eta$", "B0_pion_eta"),
    #         ("kstar_pt",  np.linspace(0, 5, 201),  r"$K^{*}$ $p_{\mathrm{T}}$ [GeV]", "B0_kstar_pt"),
    #         ("kstar_eta", np.linspace(-4, 4, 81),  r"$K^{*}$ $\eta$", "B0_kstar_eta"),
    #         ("kstar_mass",np.linspace(0.6, 1.2, 121), r"$K^{*}$ mass [GeV]", "B0_kstar_mass"),
    #     ],
    #     r"$B^{+} \to K^{+} TM$": [
    #         ("kaon_pt",  np.linspace(0, 5, 201), r"$K$ $p_{\mathrm{T}}$ [GeV]", "Bplus_kaon_pt"),
    #         ("kaon_eta", np.linspace(-4, 4, 81), r"$K$ $\eta$", "Bplus_kaon_eta"),
    #     ],
    #     r"$\omega \to TM\pi^{0}$": [
    #         ("pi0_pt",  np.linspace(0, 5, 201), r"$\pi^{0}$ $p_{\mathrm{T}}$ [GeV]", "omega_pi0_pt"),
    #         ("pi0_eta", np.linspace(-4, 4, 81), r"$\pi^{0}$ $\eta$", "omega_pi0_eta"),
    #     ],
    #     r"$\eta \to TM\gamma$": [
    #         ("partner_pt",  np.linspace(0, 2, 101), r"$\gamma$ $p_{\mathrm{T}}$ [GeV]", "eta_gamma_pt"),
    #         ("partner_eta", np.linspace(-4, 4, 81), r"$\gamma$ $\eta$", "eta_gamma_eta"),
    #     ],
    #     r"$D^{+} \to \pi^{+} TM$": [
    #         ("pion_pt",  np.linspace(0, 5, 201), r"$\pi$ $p_{\mathrm{T}}$ [GeV]", "Dplus_pion_pt"),
    #         ("pion_eta", np.linspace(-4, 4, 81), r"$\pi$ $\eta$", "Dplus_pion_eta"),
    #     ],
    # }

    # for label, plots in particle_plots.items():
    #     plot_single_channel_particles(data, label, plots)
        
    # logx_pt_plots = [
    #     ("mom_pt",  np.logspace(-2.5, 2.3, 120), r"Mother $p_{\mathrm{T}}$ [GeV]", "common_mother_pt_logx"),
    #     ("tm_pt",   np.logspace(-2.5, 2.3, 120), r"TM $p_{\mathrm{T}}$ [GeV]",     "common_tm_pt_logx"),
    #     ("ele1_pt", np.logspace(-3, 2.3, 120), r"$e_{1}$ $p_{\mathrm{T}}$ [GeV]", "common_ele1_pt_logx"),
    #     ("ele2_pt", np.logspace(-3, 2.3, 120), r"$e_{2}$ $p_{\mathrm{T}}$ [GeV]", "common_ele2_pt_logx"),
    # ]
    # for item in logx_pt_plots:
    #     plot_overlay_logx(data, *item)
    print(f"\nPlots written to {OUTDIR}/")
    

if __name__ == "__main__":
    main()
