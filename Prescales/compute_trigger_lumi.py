import sys
import subprocess
import re

from run_ranges import RUN_RANGES
from parse_trigeff import parse_trigeff

SUM_RE = re.compile(r"#Sum (delivered|recorded)\s*:\s*([\d.]+)")
VERSION_SUFFIX_RE = re.compile(r"_v\d+$")
UB_TO_FBINV = 1e-9  # 1 fb^-1 = 1e9 ub^-1


def version_wildcard(name):
    """Our MC's trigeff.log reports one specific frozen-menu version suffix
    (e.g. _v1), but real HLT paths bump version numbers through the year
    even when functionally unchanged. Querying brilcalc for the exact
    versioned name would only capture whichever slice of the year that one
    version happened to be active, undercounting paths that got
    reconfigured. Wildcard the version suffix so brilcalc sums across all
    versions of the same path instead."""
    return VERSION_SUFFIX_RE.sub("_v*", name)


def brilcalc_lumi(hltpath_pattern, begin, end):
    """Returns (delivered_fb, recorded_fb), or (None, None) if brilcalc
    returned no data for this path over this run range."""
    cmd = [
        "brilcalc", "lumi", "-c", "web",
        "--begin", str(begin), "--end", str(end),
        "--hltpath", hltpath_pattern,
        "--output-style", "csv",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    delivered_ub = recorded_ub = None
    for line in result.stdout.splitlines():
        m = SUM_RE.search(line)
        if not m:
            continue
        val = float(m.group(2))
        if m.group(1) == "delivered":
            delivered_ub = val
        else:
            recorded_ub = val

    if delivered_ub is None or recorded_ub is None:
        return None, None
    return delivered_ub * UB_TO_FBINV, recorded_ub * UB_TO_FBINV


def main():
    args = sys.argv[1:]
    limit = None
    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])
        del args[idx:idx + 2]

    if len(args) < 2:
        raise SystemExit("usage: python compute_trigger_lumi.py <trigeff.log> <year> [outfile.csv] [--limit N]")

    trigeff_log = args[0]
    year = args[1]
    outfile = args[2] if len(args) > 2 else f"trigger_lumi_{year}.csv"

    if year not in RUN_RANGES:
        raise SystemExit(f"Unknown year {year!r}. Known: {list(RUN_RANGES)}")
    begin, end = RUN_RANGES[year]

    triggers = parse_trigeff(trigeff_log)
    if limit is not None:
        triggers = triggers[:limit]
    print(f"{len(triggers)} triggers to query over runs {begin}-{end}\n")

    # Written incrementally in discovery order, as a progress/safety net in
    # case the run gets interrupted -- not the final deliverable.
    progress_file = outfile + ".progress"
    results = []
    with open(progress_file, "w") as f:
        f.write("year,name,fired,total,mc_efficiency_pct,recorded_fb,delivered_fb,recorded_x_efficiency_fb\n")
        for i, (name, fired, total, eff) in enumerate(triggers, 1):
            delivered_fb, recorded_fb = brilcalc_lumi(version_wildcard(name), begin, end)
            if recorded_fb is None:
                print(f"[{i}/{len(triggers)}] {name}: no brilcalc data over this run range, skipping")
                continue

            metric = recorded_fb * (eff / 100.0)
            results.append((name, fired, total, eff, recorded_fb, delivered_fb, metric))
            f.write(f"{year},{name},{fired},{total},{eff},{recorded_fb},{delivered_fb},{metric}\n")
            f.flush()
            print(f"[{i}/{len(triggers)}] {name}: recorded={recorded_fb:.4f} fb^-1, "
                  f"eff={eff:.2f}%, recorded*eff={metric:.4f} fb^-1")

    # Final deliverable: same rows, sorted by recorded*efficiency descending.
    results.sort(key=lambda r: r[6], reverse=True)
    with open(outfile, "w") as f:
        f.write("year,name,fired,total,mc_efficiency_pct,recorded_fb,delivered_fb,recorded_x_efficiency_fb\n")
        for row in results:
            f.write(f"{year}," + ",".join(str(v) for v in row) + "\n")

    print(f"\n{'='*100}")
    print(f"{'Trigger Name':<55} {'Eff':>7} {'Recorded[fb-1]':>15} {'Recorded*Eff[fb-1]':>20}")
    print("-" * 100)
    for name, fired, total, eff, recorded_fb, delivered_fb, metric in results:
        print(f"{name:<55} {eff:>6.2f}% {recorded_fb:>15.4f} {metric:>20.4f}")

    print(f"\nWrote {outfile}")


if __name__ == "__main__":
    main()
