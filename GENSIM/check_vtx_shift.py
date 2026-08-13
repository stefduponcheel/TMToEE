import sys
import math
from DataFormats.FWLite import Events, Handle

infile = sys.argv[1]
events = Events(infile)

handle = Handle("std::vector<reco::GenParticle>")
label = ("genParticles")

TM_PDGID = 99033003

n = 0
for event in events:
    event.getByLabel(label, handle)
    genParts = handle.product()

    for gp in genParts:
        if gp.pdgId() != TM_PDGID or gp.numberOfDaughters() == 0:
            continue
        if any(gp.daughter(i).pdgId() == TM_PDGID for i in range(gp.numberOfDaughters())):
            continue

        mu = gp.daughter(0)
        v = mu.vertex()
        r_xy = math.sqrt(v.x()**2 + v.y()**2)

        n += 1
        print(f"TM #{n}: eta={gp.eta():+.3f} phi={gp.phi():+.3f}  "
              f"muon vertex: x={v.x()*10:+7.2f} y={v.y()*10:+7.2f} z={v.z()*10:+7.2f} mm  "
              f"r_xy={r_xy*10:6.2f} mm")

        if n >= 20:
            sys.exit(0)

print(f"\nchecked {n} TM decays")
