import uproot, numpy as np

t = uproot.open("/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_15_0_5/src/EDAnalyzer/Reconstruction/python/trignearest_skim.root")["trigObjNearest/trigObj"]
d = t.arrays(["run","lumi","event","to_pathIdx","near_fromTM","near_dR"], library="np")

print("total object entries (tree entries):", t.num_entries)

# distinct events
evt = set(zip(d["run"], d["lumi"], d["event"]))
print("distinct events:", len(evt))

# entries per path
import collections
print("entries per path index:")
for p, n in sorted(collections.Counter(d["to_pathIdx"].tolist()).items()):
    print(f"  path {p}: {n}")

# how many objects have nearest e from TM
print("objects with nearest e from TM:", int(d["near_fromTM"].sum()))
    