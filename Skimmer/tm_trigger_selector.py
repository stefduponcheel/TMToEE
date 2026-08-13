import sys
import FWCore.ParameterSet.Config as cms
from HLTrigger.HLTfilters.triggerResultsFilter_cfi import triggerResultsFilter

process = cms.Process("SKIM")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

inputFile = sys.argv[1]
outputFile = sys.argv[2]

process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(
        inputFile,  # already a full root:// URL from run_skimming*.sh
    ),
    # Each MiniAOD file is itself a merge of several AODSIM files (see
    # MINIAODSIM's FILES_PER_JOB) that were never renumbered, so even a
    # single file here internally repeats Run=1/Lumi=1/Event=1..N several
    # times over -- without this, only the first chunk's events survive.
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
)

# Trigger filter
process.triggerSelection = triggerResultsFilter.clone(
    triggerConditions = cms.vstring(
        "HLT_DoubleEle4_eta1p22_mMax6*",
        "HLT_DoubleEle4p5_eta1p22_mMax6*",
        "HLT_DoubleEle5_eta1p22_mMax6*",
        "HLT_DoubleEle5p5_eta1p22_mMax6*",
        "HLT_DoubleEle6_eta1p22_mMax6*",
        "HLT_DoubleEle6p5_eta1p22_mMax6*",
        "HLT_DoubleEle7_eta1p22_mMax6*",
        "HLT_DoubleEle7p5_eta1p22_mMax6*",
        "HLT_DoubleEle8_eta1p22_mMax6*",
        "HLT_DoubleEle8p5_eta1p22_mMax6*",
        "HLT_DoubleEle9_eta1p22_mMax6*",
        "HLT_DoubleEle9p5_eta1p22_mMax6*",
        "HLT_DoubleEle10_eta1p22_mMax6*",
    ),
    hltResults = cms.InputTag("TriggerResults", "", "HLT"),
    l1tResults = cms.InputTag(""),
    throw = False
)

process.filter_step = cms.Path(
    process.triggerSelection
)

process.out = cms.OutputModule(
    "PoolOutputModule",
    fileName = cms.untracked.string(outputFile),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring(
            "filter_step"
        )
    ),
    outputCommands = cms.untracked.vstring(
        "keep *"
    )
)

process.end = cms.EndPath(
    process.out
)
