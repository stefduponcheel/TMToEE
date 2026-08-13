import sys
import math

# Rewrites the TM (99033003) particle line in every LHE event, bumping its
# mass from 0.21132 GeV (right at the mu+mu- threshold, causing Pythia8's
# "failed to find workable decay channel" for ppToTMmumuX) up to a target
# value, while keeping px/py/pz unchanged and recomputing E to stay
# consistent with the new mass. This is the physical kinematic mass Pythia8
# actually uses -- unlike the particle-database m0 in the fragment, which
# has no effect on an already-on-shell LHE-sourced particle.

infile, outfile = sys.argv[1], sys.argv[2]
new_mass = float(sys.argv[3]) if len(sys.argv) > 3 else 0.213

TM_PDGID = "99033003"
n_fixed = 0

with open(infile) as fin, open(outfile, "w") as fout:
    for line in fin:
        tok = line.split()
        if len(tok) == 13 and tok[0] == TM_PDGID:
            px, py, pz = float(tok[6]), float(tok[7]), float(tok[8])
            e_new = math.sqrt(px**2 + py**2 + pz**2 + new_mass**2)
            tok[9] = f"{e_new:.10e}"
            tok[10] = f"{new_mass:.10e}"
            # preserve original leading-column width/alignment as best effort
            line = " " + " ".join(tok) + "\n"
            n_fixed += 1
        fout.write(line)

print(f"rewrote {n_fixed} TM lines, mass -> {new_mass} GeV")
print(f"wrote {outfile}")
