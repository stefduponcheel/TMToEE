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
options.parseArguments()

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
)

process.TrigAnalyzer = cms.EDAnalyzer("TrigAnalyzer")
process.p = cms.Path(process.TrigAnalyzer)
