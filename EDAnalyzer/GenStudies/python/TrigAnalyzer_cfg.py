import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing("analysis")
options.register(
    "mode", "etaToTMGamma",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Signal mode (subdir under /store/user/sduponch/PhD/TMToEE/)",
)
options.register(
    "version", "20260508",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Production version (date tag)",
)
options.register(
    "year", "2022",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Year",
)
options.register(
    "nFiles", 1,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Number of files to read",
)
options.register(
    "storage", "iihe",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Where AODSIM lives: 'iihe' (default, CRAB-produced, 1-indexed) or "
    "'eos' (condor-produced, 0-indexed, worker nodes have unreliable "
    "connectivity to maite.iihe.ac.be this session)",
)
options.register(
    "prescaleSet", 0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "HLT menu prescale column/set index to read prescales from (see "
    "TrigAnalyzer's printed prescale-set labels to pick the right one "
    "for a given real data-taking period)",
)
options.parseArguments()

if options.storage == "eos":
    base = f"/eos/user/s/sduponch/PhD/{options.mode}/AODSIM/{options.year}"
    INFILE = [f"root://eosuser.cern.ch/{base}/output_{i}.root" for i in range(options.nFiles)]
else:
    base = (
        f"root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/"
        f"{options.mode}/{options.version}/Simulation/AODSIM/{options.year}"
    )
    INFILE = [f"{base}/output_{i}.root" for i in range(1, options.nFiles + 1)]

process = cms.Process("TrigEff")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 50000
process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.MessageLogger.cerr.TrigAnalyzer = cms.untracked.PSet(
    limit=cms.untracked.int32(-1)
)

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(INFILE),
    skipBadFiles=cms.untracked.bool(True),
    # Default (checkAllFilesOpened) drops events whose (Run,Lumi,Event) triple
    # repeats across files. Condor-produced samples (not CRAB) don't get unique
    # per-job run/lumi numbers, so every file legitimately reuses Run=1/Lumi=1/
    # Event=1..N -- without this, only the first file's events survive.
    duplicateCheckMode=cms.untracked.string("noDuplicateCheck"),
)

process.TrigAnalyzer = cms.EDAnalyzer(
    "TrigAnalyzer",
    prescaleSet=cms.untracked.uint32(options.prescaleSet),
)
process.p = cms.Path(process.TrigAnalyzer)
