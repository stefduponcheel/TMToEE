# Inspired by:
# - eta -> TM gamma fragment
# - https://inspirehep.net/literature/1663979

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
            # Hard QCD with b-bbar pair production
            'HardQCD:hardbbbar = on',

            'HiddenValley:Ngauge = 1',
            '4900022:m0 = 0.210',
            '4900022:onMode = off',
            '4900022:onIfMatch = 11 -11', 
            '4900022:tau0 = 0.53',          
            'HiddenValley:doKinMix = on',
            'HiddenValley:kinMix = 0.1',    

            # Force B+ -> K+ TM (and equivalently B- -> K- TM)
            '521:onMode = off',
            '521:addChannel = on 1 0 321 4900022',
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    )
    )
)

bMesonFilter = cms.EDFilter("MCSingleParticleFilter",
    ParticleID = cms.untracked.vint32(521, -521),
    MinPt = cms.untracked.vdouble(1.0, 1.0),      
    MinEta = cms.untracked.vdouble(-2.5, -2.5),
    MaxEta = cms.untracked.vdouble( 2.5,  2.5),
)

ProductionFilterSequence = cms.Sequence(generator * bMesonFilter)
