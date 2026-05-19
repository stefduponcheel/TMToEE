import uproot

FILES = {
    "B0": "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/B0ToKstarTM/20260509/Analysis/Ntuples/2022/ntuple_B0_merged.root",
    "Bplus": "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/BplusToKplusTM/20260509/Analysis/Ntuples/2022/ntuple_Bplus_merged.root",
    "omega": "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/omegaToTMPi0/20260509/Analysis/Ntuples/2022/ntuple_Omega_merged.root",
    "eta": "root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/etaToTMGamma/20260508/Analysis/Ntuples/2022/ntuple_eta_merged.root"
}   

for sample, path in FILES.items():

    print("\n" + "=" * 100)
    print(f"{sample}")
    print(path)

    f = uproot.open(path)

    print("\nROOT keys:")
    for k in f.keys():
        print("  ", k)

    tree_path = "genStudies/Events"
    if tree_path not in f:
        tree_path = "Events"

    print(f"\nUsing tree: {tree_path}")

    tree = f[tree_path]

    print("\nBranches:\n")

    for b in sorted(tree.keys()):
        print(b)

    print("\nTotal branches:", len(tree.keys()))
