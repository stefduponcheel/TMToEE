import sys
import math
from DataFormats.FWLite import Events, Handle

infile = sys.argv[1]
events = Events(infile)

handle = Handle("std::vector<reco::GenParticle>")
label = ("genParticles")

TM_PDGID = 99033003

n = 0
n_events = 0
n_genparts = 0
n_tm_any = 0
for event in events:
    n_events += 1
    event.getByLabel(label, handle)
    genParts = handle.product()
    n_genparts += len(genParts)
    n_tm_any += sum(1 for gp in genParts if gp.pdgId() == TM_PDGID)

    for gp in genParts:
        if gp.pdgId() != TM_PDGID:
            continue
        if gp.numberOfDaughters() == 0:
            continue
        # skip non-last copies (TM->TM shower/recoil bookkeeping)
        if any(gp.daughter(i).pdgId() == TM_PDGID for i in range(gp.numberOfDaughters())):
            continue

        daughters = [gp.daughter(i) for i in range(gp.numberOfDaughters())]
        dpids = sorted(d.pdgId() for d in daughters)

        prod = gp.vertex()
        decay = daughters[0].vertex()
        Lxyz = math.sqrt((decay.x() - prod.x())**2 +
                          (decay.y() - prod.y())**2 +
                          (decay.z() - prod.z())**2)

        n += 1
        print(f"TM #{n}: pt={gp.pt():.3f} eta={gp.eta():.3f}  "
              f"daughters={dpids}  flight_dist={Lxyz*10:.4f} mm")

        if n >= 20:
            sys.exit(0)

print(f"\nchecked {n} TM decays")
