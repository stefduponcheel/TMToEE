import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing("analysis")
options.inputFiles = "file:root://maite.iihe.ac.be//store/user/sduponch/PhD/TMToEE/DplusToPiplusTM/20260515/Simulation/AODSIM/2022/output_100.root"
options.outputFile = "ntuple_Dplus.root"
options.maxEvents = -1
options.parseArguments()

process = cms.Process("GenStudiesDplus")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100000
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
    "GenStudies_Dplus",
    genParticles=cms.InputTag("genParticles"),  
)

process.p = cms.Path(process.genStudies)
