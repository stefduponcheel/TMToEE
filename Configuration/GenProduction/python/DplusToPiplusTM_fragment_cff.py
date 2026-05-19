# D+ -> pi+ TM, TM -> e+e-
# Adapted from B+ -> K+ TM fragment

import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
    pythiaPylistVerbosity = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    maxEventsToPrint = cms.untracked.int32(0),
    addHepMCProduct = cms.bool(True),
    comEnergy = cms.double(13600.0),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            # Hard QCD with c-cbar pair production
            'HardQCD:hardccbar = on',

            # True Muonium as Hidden Valley dark photon
            'HiddenValley:Ngauge = 1',
            '4900022:m0 = 0.210',
            '4900022:onMode = off',
            '4900022:onIfMatch = 11 -11',
            '4900022:tau0 = 0.53',
            'HiddenValley:doKinMix = on',
            'HiddenValley:kinMix = 0.1',

            # Force D+ -> pi+ TM (and equivalently D- -> pi- TM)
            '411:onMode = off',
            '411:addChannel = on 1 0 211 4900022',
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    )
    )
)

dMesonFilter = cms.EDFilter("MCSingleParticleFilter",
    ParticleID = cms.untracked.vint32(411, -411),
    MinPt = cms.untracked.vdouble(1.0, 1.0),
    MinEta = cms.untracked.vdouble(-2.5, -2.5),
    MaxEta = cms.untracked.vdouble( 2.5,  2.5),
)

ProductionFilterSequence = cms.Sequence(generator * dMesonFilter)
