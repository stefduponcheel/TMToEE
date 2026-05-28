import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('genTag', 'genParticles',
                 VarParsing.multiplicity.singleton, VarParsing.varType.string,
                 "Gen particle collection")
options.register('coneDR', 0.1,
                 VarParsing.multiplicity.singleton, VarParsing.varType.float,
                 "Cone dR around trigger object")
options.parseArguments()

process = cms.Process("TRIGORIG")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 500
process.MessageLogger.cerr.threshold = "WARNING"

# guard maxEvents: VarParsing default is -1 in analysis mode, but be explicit
nev = options.maxEvents if options.maxEvents else -1
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(int(nev)))

process.source = cms.Source("PoolSource",
    fileNames=cms.untracked.vstring(*options.inputFiles),
    skipBadFiles=cms.untracked.bool(True),
)

outname = options.outputFile if options.outputFile else "trigorig.root"
process.TFileService = cms.Service("TFileService",
    fileName=cms.string(outname))

double_ele_paths = [
    "HLT_DoubleEle4_eta1p22_mMax6",
    # "HLT_DoubleEle4p5_eta1p22_mMax6",
    # "HLT_DoubleEle5_eta1p22_mMax6",
    # "HLT_DoubleEle5p5_eta1p22_mMax6",
    # "HLT_DoubleEle6_eta1p22_mMax6",
    # "HLT_DoubleEle6p5_eta1p22_mMax6",
    # "HLT_DoubleEle7_eta1p22_mMax6",
    # "HLT_DoubleEle7p5_eta1p22_mMax6",
    # "HLT_DoubleEle8_eta1p22_mMax6",
    # "HLT_DoubleEle8p5_eta1p22_mMax6",
    # "HLT_DoubleEle9_eta1p22_mMax6",
    # "HLT_DoubleEle9p5_eta1p22_mMax6",
    # "HLT_DoubleEle10_eta1p22_mMax6",
]

process.trigObjOrigin = cms.EDAnalyzer(
    "TrigObjOrigin",
    genParticles = cms.InputTag(options.genTag),
    bits         = cms.InputTag("TriggerResults", "", "HLT"),
    objects      = cms.InputTag("slimmedPatTrigger"),
    coneDR       = cms.double(float(options.coneDR)),
    paths        = cms.vstring(*double_ele_paths),
    lastFilter   = cms.bool(True),
    l3Filter     = cms.bool(True),
)

process.p = cms.Path(process.trigObjOrigin)
