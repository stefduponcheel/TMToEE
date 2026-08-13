import sys
import re

# Paths that fire unconditionally regardless of physics content (monitoring,
# calibration, random/zero-bias streams) always show up at ~100% efficiency
# in MC -- they aren't real trigger candidates, so we drop anything at
# exactly 100%, not just this explicit list. Kept as an explicit list too
# since it documents which paths that filter is expected to remove.
NON_PHYSICS_PATHS = {
    "HLT_Random_v3", "HLT_ZeroBias_v6", "HLT_ZeroBias_Alignment_v1",
    "HLT_ZeroBias_Beamspot_v4", "HLT_EcalCalibration_v4",
    "HLT_HcalCalibration_v5", "HLT_HcalNZS_v13", "HLT_Physics_v7",
    "HLT_OnlineMonitorGroup_v1", "HLT_EphemeralPhysics_v1",
    "HLT_EphemeralZeroBias_v1",
}

ROW_RE = re.compile(r"^\s*(HLT_\S+)\s+(\d+)\s+(\d+)\s+([\d.]+)%\s*$")


def parse_trigeff(path):
    """Returns a list of (name, fired, total, efficiency_pct) for every
    trigger that fired at least once and isn't trivially unconditional
    (efficiency < 100%), sorted by efficiency descending."""
    rows = []
    in_table = False
    with open(path) as f:
        for line in f:
            if "Trigger Statistics" in line:
                in_table = True
                continue
            if not in_table:
                continue
            if line.strip().startswith("===="):
                if rows:
                    break  # closing separator after we've already collected rows
                continue
            m = ROW_RE.match(line)
            if not m:
                continue
            name, fired, total, eff = m.group(1), int(m.group(2)), int(m.group(3)), float(m.group(4))
            if fired == 0 or eff >= 100.0 or name in NON_PHYSICS_PATHS:
                continue
            rows.append((name, fired, total, eff))

    rows.sort(key=lambda r: r[3], reverse=True)
    return rows


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python parse_trigeff.py <trigeff.log>")

    rows = parse_trigeff(sys.argv[1])
    print(f"{len(rows)} physics-selective triggers fired at least once\n")
    print(f"{'Trigger Name':<70} {'Fired':>8} {'Total':>8} {'Eff':>8}")
    for name, fired, total, eff in rows:
        print(f"{name:<70} {fired:>8} {total:>8} {eff:>7.2f}%")
