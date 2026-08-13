# TM here is true muonium (mu+mu- bound state, PDG 99033003, m0 = 0.21132 GeV = 2*m_mu),
# produced via p p > mumu(1|3S1) j in an external LHE file (model: sm_onia-lepton_masses).
# Pythia8 does not know this PDG code, so it is declared from scratch and forced to decay
# to e+ e- only, with the same displaced decay-length convention (tau0 = 0.53 mm) used for
# the dark-photon stand-in TM (PDG 4900022) elsewhere in TMToEE.

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
            # ROOT CAUSE (found by reading Pythia8's own source docs, LHEF.xml):
            # our LHE file sets VTIMUP=0 (decay time) for TM in every event. By
            # default (LesHouches:setLifetime=1), Pythia8 takes decay times for any
            # non-tau particle directly from the LHE record, silently overriding
            # whatever tau0/mWidth we set in the particle database below -- which is
            # exactly why every previous attempt (tau0 alone, width alone, both
            # together) still showed prompt decay. Setting it to 2 makes Pythia8
            # generate the decay time itself from the particle data instead.
            'LesHouches:setLifetime = 2',
            # TEST: does tau0 alone (mWidth=0) suffice now that setLifetime=2 is set,
            # matching the working PDG 4900022 precedent (tau0 only, no mWidth)? Every
            # earlier attempt was invalidated by the LHE override above, so this is the
            # first real test of whether mWidth was ever actually needed.
            # id:new = name antiName spinType chargeType colType m0 mWidth mMin mMax tau0
            #   name/antiName = TM twice -> TM is its own antiparticle (neutral bound state)
            #   spinType = 3 -> vector (J=1), matching the onium's JPC = 1-- (3S1)
            #   chargeType = 0 -> electrically neutral
            #   colType   = 0 -> colour singlet (colourless, as in the LHE record)
            #   m0 = 0.213 GeV, bumped ~1.7 MeV above 2*m_mu (0.211317 GeV, PDG) --
            #   at the physical mass (0.21132, same as the LHE record), Pythia8
            #   fails with "failed to find workable decay channel" on every event:
            #   TM->mu+mu- sits right at threshold, and even with mWidth=0, the
            #   ResonanceWidths:minWidth=1e-30 floor still lets Pythia8's internal
            #   mass generation dip below 2*m_mu often enough to kill the channel.
            #   This is expected -- true muonium can't actually decay to two
            #   on-shell free muons in vacuum, which is exactly why the real
            #   physical process is dissociation via material interaction, not a
            #   decay. Since this fragment is already an approximate stand-in for
            #   that process, giving Pythia8 a small safe margin above threshold
            #   is the practical fix rather than chasing the exact physical mass.
            #   mWidth/mMin/mMax = 0 -> lifetime set directly via tau0, matching PDG 4900022
            #   tau0 = 0.53 mm -> proper decay length c*tau (same convention as PDG 4900022)
            'ParticleDecays:limitTau0 = off',
            'ResonanceWidths:minWidth = 1e-30',
            '99033003:new = TM TM 3 0 0 0.213 0.0 0.0 0.0 0.53',
            '99033003:addChannel = on 1 0 -13 13', # force TM -> mu+ mu-, only channel
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                     'pythia8CP5Settings',
                                     'processParameters',
                                     )
    )
)

ProductionFilterSequence = cms.Sequence(generator)
