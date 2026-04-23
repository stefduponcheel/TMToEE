# Inspired by: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_fragment/BPH-RunIII2024Summer24GS-00174/0 

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
            'SoftQCD:nonDiffractive = on', # minbias, https://pythia.org/latest-manual/QCDSoftProcesses.html
            #Add new particle with ID 4900022, mass 0.210 GeV, and tau 0.53 mm
            'HiddenValley:Ngauge = 1',
            '4900022:m0 = 0.210', 
            '4900022:onMode = off', 
            '4900022:onIfMatch = 11 -11', # force decay TM -> e+ e-
            '4900022:tau0 = 0.53', #0.53 mm corresponds to a width of 3.7e-13 GeV, which is the value for the dark photon with kinetic mixing of 2.7e-5 and mass of 0.210 GeV
            'HiddenValley:doKinMix  = on',
            'HiddenValley:kinMix = 0.1', # Actual value is 2.7e-5 but this is too small for the generator to produce any events, so we use a larger value and will reweight the events later
            '221:onMode = off',
            '221:addChannel = on 1 0 4900022 22'
        ),
	parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    )
    )
)

etaFilter = cms.EDFilter("MCSingleParticleFilter",
    ParticleID = cms.untracked.vint32(221),
    MinPt = cms.untracked.vdouble(1.0),
    MinEta = cms.untracked.vdouble(-2.5),
    MaxEta = cms.untracked.vdouble( 2.5),
)

ProductionFilterSequence = cms.Sequence(generator* etaFilter)
