import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('genTag', 'genParticles',
                 VarParsing.multiplicity.singleton, VarParsing.varType.string,
                 "Gen particle collection")
options.register('tmPdgId', 4900022,
                 VarParsing.multiplicity.singleton, VarParsing.varType.int,
                 "PDG id of TM (4900022 for the dark-photon stand-in channels, "
                 "99033003 for ppToTMeeX's true-muonium state)")
options.parseArguments()

process = cms.Process("TRIGPTMATCH")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 500
process.MessageLogger.cerr.threshold = "WARNING"

nev = options.maxEvents if options.maxEvents else -1
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(int(nev)))
process.source = cms.Source("PoolSource",
    fileNames=cms.untracked.vstring(*options.inputFiles),
    skipBadFiles=cms.untracked.bool(True),
    # Skimmed files are downstream of the MINIAODSIM merge (FILES_PER_JOB AODSIM
    # files combined per job, never renumbered), so even reading just one of
    # them internally repeats Run=1/Lumi=1/Event=1..N several times over --
    # without this, only the first chunk's events would survive.
    duplicateCheckMode=cms.untracked.string("noDuplicateCheck"))
process.TFileService = cms.Service("TFileService",
    fileName=cms.string(options.outputFile if options.outputFile else "TrigPtMatch.root"))

double_ele_paths = [
    "HLT_DoubleEle4_eta1p22_mMax6",
    # "HLT_DoubleEle4p5_eta1p22_mMax6",
    # "HLT_DoubleEle5_eta1p22_mMax6", "HLT_DoubleEle5p5_eta1p22_mMax6",
    # "HLT_DoubleEle6_eta1p22_mMax6", "HLT_DoubleEle6p5_eta1p22_mMax6",
    # "HLT_DoubleEle7_eta1p22_mMax6", "HLT_DoubleEle7p5_eta1p22_mMax6",
    # "HLT_DoubleEle8_eta1p22_mMax6", "HLT_DoubleEle8p5_eta1p22_mMax6",
    # "HLT_DoubleEle9_eta1p22_mMax6", "HLT_DoubleEle9p5_eta1p22_mMax6",
    # "HLT_DoubleEle10_eta1p22_mMax6",
]

process.trigObjPtMatch = cms.EDAnalyzer(
    "TrigObjPtMatch",
    genParticles = cms.InputTag(options.genTag),
    bits         = cms.InputTag("TriggerResults", "", "HLT"),
    objects      = cms.InputTag("slimmedPatTrigger"),
    tmPdgId      = cms.int32(options.tmPdgId),
    paths        = cms.vstring(*double_ele_paths),
    lastFilter   = cms.bool(False),
    l3Filter     = cms.bool(False),
    coneSize     = cms.double(0.3),
)

process.p = cms.Path(process.trigObjPtMatch)
