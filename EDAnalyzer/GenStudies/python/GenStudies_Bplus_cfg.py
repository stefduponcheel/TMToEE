import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing("analysis")
options.outputFile = "ntuple_Bplus.root"
options.maxEvents = -1
options.parseArguments()

process = cms.Process("GenStudiesBplus")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(options.inputFiles),
    skipBadFiles=cms.untracked.bool(True),
)

process.TFileService = cms.Service(
    "TFileService",
    fileName=cms.string(options.outputFile),
    closeFileFast=cms.untracked.bool(True),
)

process.genStudies = cms.EDAnalyzer(
    "GenStudies_Bplus",
    genParticles=cms.InputTag("genParticles"),  
)

process.p = cms.Path(process.genStudies)
