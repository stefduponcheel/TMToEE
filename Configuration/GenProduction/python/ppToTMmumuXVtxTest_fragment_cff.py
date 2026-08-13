import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8HadronizerFilter",
    pythiaPylistVerbosity = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    maxEventsToPrint = cms.untracked.int32(0),
    filterEfficiency = cms.untracked.double(1.0),
    comEnergy = cms.double(13600.0),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'LesHouches:setLifetime = 2',
            'ParticleDecays:limitTau0 = off',
            'ResonanceWidths:minWidth = 1e-30',
            '99033003:new = TM TM 3 0 0 0.213 0.0 0.0 0.0 0.0001',  # ~prompt: tiny tau0
            '99033003:addChannel = on 1 0 -13 13',
            # Placeholder 21mm offset -- purely to test the MECHANISM, not
            # the real beampipe radius (still unconfirmed).
            'Beams:allowVertexSpread = on',
            'Beams:offsetVertexX = 21.',
            'Beams:offsetVertexY = 0.',
            'Beams:offsetVertexZ = 0.',
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                     'pythia8CP5Settings',
                                     'processParameters',
                                     )
    )
)

ProductionFilterSequence = cms.Sequence(generator)
