import FWCore.ParameterSet.Config as cms

process = cms.Process("ANA")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(10))

# process.source = cms.Source("PoolSource", fileNames=cms.untracked.vstring("file:/afs/cern.ch/work/k/kakang/H2DW/CMSSW_12_4_14_patch3/src/Simulation/AODSIM/output.root"))
process.source = cms.Source("PoolSource", fileNames=cms.untracked.vstring("file:/afs/cern.ch/user/s/sduponch/private/PhD/TM/TMToEE/CMSSW_12_4_14_patch3/src/test/GENSIM/etatoTMgamma_GENSIM.root"))

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")

process.printTree = cms.EDAnalyzer("ParticleTreeDrawer",
                                   src = cms.InputTag("genParticles"),                                                                 
                                   printP4 = cms.untracked.bool(False),
                                   printPtEtaPhi = cms.untracked.bool(False),
                                   printVertex = cms.untracked.bool(False),
                                   printStatus = cms.untracked.bool(False),
                                   printIndex = cms.untracked.bool(False),
                                   )
process.p = cms.Path(process.printTree)
