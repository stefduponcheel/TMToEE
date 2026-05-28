// -*- C++ -*-
//
// Package:    TMToEE/GenTrigMatcher
// Class:      GenTrigMatcher
//
// Description: Matches gen electrons from True Muonium (dark photon, PDG 4900022)
//              to HLT trigger objects from the DoubleEle low-mass parking triggers.
//
//              In this sample EVERY eta decays to TM, so there are many TMs per
//              event. Electrons are therefore stored grouped by their parent TM
//              (via genEle_tmIdx), so that downstream one can check whether BOTH
//              legs of the SAME TM matched / fired the trigger.
//
//              This is a reco-independent measurement: it isolates the gen->trigger
//              leg of the efficiency chain.
//

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "TTree.h"

#include <vector>
#include <string>
#include <cmath>
#include <iostream>
#include <functional>

class GenTrigMatcher : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit GenTrigMatcher(const edm::ParameterSet&);
  ~GenTrigMatcher() override = default;

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  // tokens
  const edm::EDGetTokenT<std::vector<reco::GenParticle>> genToken_;
  const edm::EDGetTokenT<edm::TriggerResults> trigBitsToken_;
  const edm::EDGetTokenT<std::vector<pat::TriggerObjectStandAlone>> trigObjToken_;

  // config
  const int tmPdgId_;                    // 4900022
  const double maxDR_;                   // matching cone
  const std::vector<std::string> paths_; // path names without version suffix
  const bool debugFilters_;              // dump DoubleEle/mMax filter labels
  const bool debugChain_;                // dump TM decay chains

  // output
  edm::Service<TFileService> fs_;
  TTree* tree_;

  // event-level
  int  run_, lumi_;
  long event_;
  std::vector<int> evtPathFired_;        // [nPaths] did each path fire this event

  // TM-level (one entry per TM that decays to e+e-)
  int nTM_;
  std::vector<float> tm_pt_, tm_eta_, tm_phi_, tm_mass_;
  std::vector<int>   tm_motherId_;

  // per gen electron
  int nGenEleFromTM_;
  std::vector<float> genEle_pt_;
  std::vector<float> genEle_eta_;
  std::vector<float> genEle_phi_;
  std::vector<int>   genEle_charge_;
  std::vector<int>   genEle_tmIdx_;       // which TM (index into tm_* vectors) this came from
  std::vector<std::vector<int>>   genEle_matchedPath_;  // [ele][path] 1 if matched
  std::vector<std::vector<float>> genEle_matchDR_;      // [ele][path] best dR
  std::vector<std::vector<float>> genEle_matchTrgPt_;   // [ele][path] best obj pt
};

GenTrigMatcher::GenTrigMatcher(const edm::ParameterSet& ps)
    : genToken_(consumes<std::vector<reco::GenParticle>>(ps.getParameter<edm::InputTag>("genParticles"))),
      trigBitsToken_(consumes<edm::TriggerResults>(ps.getParameter<edm::InputTag>("bits"))),
      trigObjToken_(consumes<std::vector<pat::TriggerObjectStandAlone>>(ps.getParameter<edm::InputTag>("objects"))),
      tmPdgId_(ps.getParameter<int>("tmPdgId")),
      maxDR_(ps.getParameter<double>("maxDR")),
      paths_(ps.getParameter<std::vector<std::string>>("paths")),
      debugFilters_(ps.getParameter<bool>("debugFilters")),
      debugChain_(ps.getParameter<bool>("debugChain")) {
  usesResource("TFileService");
}

void GenTrigMatcher::beginJob() {
  tree_ = fs_->make<TTree>("genTrig", "gen-to-trigger-object matching");

  tree_->Branch("run", &run_);
  tree_->Branch("lumi", &lumi_);
  tree_->Branch("event", &event_);

  tree_->Branch("evtPathFired", &evtPathFired_);

  tree_->Branch("nTM", &nTM_);
  tree_->Branch("tm_pt", &tm_pt_);
  tree_->Branch("tm_eta", &tm_eta_);
  tree_->Branch("tm_phi", &tm_phi_);
  tree_->Branch("tm_mass", &tm_mass_);
  tree_->Branch("tm_motherId", &tm_motherId_);

  tree_->Branch("nGenEleFromTM", &nGenEleFromTM_);
  tree_->Branch("genEle_pt", &genEle_pt_);
  tree_->Branch("genEle_eta", &genEle_eta_);
  tree_->Branch("genEle_phi", &genEle_phi_);
  tree_->Branch("genEle_charge", &genEle_charge_);
  tree_->Branch("genEle_tmIdx", &genEle_tmIdx_);
  tree_->Branch("genEle_matchedPath", &genEle_matchedPath_);
  tree_->Branch("genEle_matchDR", &genEle_matchDR_);
  tree_->Branch("genEle_matchTrgPt", &genEle_matchTrgPt_);

  std::cout << "[GenTrigMatcher] Path index mapping:" << std::endl;
  for (size_t i = 0; i < paths_.size(); ++i)
    std::cout << "    [" << i << "] " << paths_[i] << std::endl;
}

void GenTrigMatcher::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
  // clear
  evtPathFired_.assign(paths_.size(), 0);
  tm_pt_.clear(); tm_eta_.clear(); tm_phi_.clear(); tm_mass_.clear();
  tm_motherId_.clear();
  genEle_pt_.clear(); genEle_eta_.clear(); genEle_phi_.clear();
  genEle_charge_.clear(); genEle_tmIdx_.clear();
  genEle_matchedPath_.clear(); genEle_matchDR_.clear(); genEle_matchTrgPt_.clear();
  nTM_ = 0;
  nGenEleFromTM_ = 0;

  run_   = (int)iEvent.id().run();
  lumi_  = (int)iEvent.luminosityBlock();
  event_ = (long)iEvent.id().event();

  edm::Handle<std::vector<reco::GenParticle>> genHandle;
  iEvent.getByToken(genToken_, genHandle);

  edm::Handle<edm::TriggerResults> trigBits;
  iEvent.getByToken(trigBitsToken_, trigBits);

  edm::Handle<std::vector<pat::TriggerObjectStandAlone>> trigObjs;
  iEvent.getByToken(trigObjToken_, trigObjs);

  const edm::TriggerNames& trigNames = iEvent.triggerNames(*trigBits);

  // ---- optional: dump TM decay chains for debugging ----
  if (debugChain_) {
    std::function<void(const reco::Candidate*, int)> printChain =
        [&](const reco::Candidate* p, int depth) {
          std::string indent(2 * depth, ' ');
          std::cout << indent << "pdgId=" << p->pdgId()
                    << " status=" << p->status()
                    << " pt=" << p->pt() << " eta=" << p->eta()
                    << " nDau=" << p->numberOfDaughters() << std::endl;
          if (depth > 6) { std::cout << indent << "  ...(truncated)\n"; return; }
          for (size_t i = 0; i < p->numberOfDaughters(); ++i)
            printChain(p->daughter(i), depth + 1);
        };
    for (const auto& gp : *genHandle) {
      if (gp.pdgId() != tmPdgId_) continue;
      std::cout << "==== TM (event " << iEvent.id().event() << ") ====" << std::endl;
      printChain(&gp, 0);
    }
  }

  // ---- 1. find all TMs and their final-state electron daughters, grouped by TM ----

  // follow an electron down its (single) copy chain to the status==1 version
  auto finalSelf = [](const reco::Candidate* e) -> const reco::Candidate* {
    while (e->status() != 1) {
      const reco::Candidate* next = nullptr;
      for (size_t i = 0; i < e->numberOfDaughters(); ++i) {
        const reco::Candidate* d = e->daughter(i);
        if (d->pdgId() == e->pdgId()) { next = d; break; }
      }
      if (!next) break;
      e = next;
    }
    return e;
  };

  std::vector<const reco::GenParticle*> genEles;  // flat list for matching
  std::vector<int> genEleTM;                      // parallel: parent TM index

  int tmCounter = 0;
  for (const auto& gp : *genHandle) {
    if (gp.pdgId() != tmPdgId_) continue;

    // require it actually decays to electrons (skip any TM->TM copies)
    bool decaysToEle = false;
    for (size_t i = 0; i < gp.numberOfDaughters(); ++i)
      if (std::abs(gp.daughter(i)->pdgId()) == 11) decaysToEle = true;
    if (!decaysToEle) continue;

    int thisTM = tmCounter++;
    tm_pt_.push_back(gp.pt());
    tm_eta_.push_back(gp.eta());
    tm_phi_.push_back(gp.phi());
    tm_mass_.push_back(gp.mass());
    tm_motherId_.push_back(gp.numberOfMothers() > 0 ? gp.mother(0)->pdgId() : 0);

    for (size_t i = 0; i < gp.numberOfDaughters(); ++i) {
      const reco::Candidate* d = gp.daughter(i);
      if (std::abs(d->pdgId()) != 11) continue;
      const reco::Candidate* fe = finalSelf(d);
      genEles.push_back(static_cast<const reco::GenParticle*>(fe));
      genEleTM.push_back(thisTM);
    }
  }

  nTM_ = tmCounter;
  nGenEleFromTM_ = (int)genEles.size();

  // ---- 2. unpack all trigger objects once ----
  std::vector<pat::TriggerObjectStandAlone> unpacked;
  unpacked.reserve(trigObjs->size());
  for (const auto& obj0 : *trigObjs) {
    pat::TriggerObjectStandAlone obj = obj0;
    obj.unpackPathNames(trigNames);
    obj.unpackFilterLabels(iEvent, *trigBits);
    unpacked.push_back(obj);

    if (debugFilters_) {
      for (const auto& fl : obj.filterLabels()) {
        if (fl.find("DoubleEle") != std::string::npos || fl.find("mMax") != std::string::npos) {
          std::cout << "[GenTrigMatcher] TRIGOBJ filter=" << fl
                    << "  pt=" << obj.pt() << " eta=" << obj.eta()
                    << " phi=" << obj.phi() << std::endl;
        }
      }
    }
  }

  // ---- 3. event-level path decisions ----
  for (size_t ip = 0; ip < paths_.size(); ++ip) {
    for (unsigned i = 0; i < trigNames.size(); ++i) {
      const std::string& name = trigNames.triggerName(i);
      if (name.rfind(paths_[ip], 0) == 0) {  // starts with our version-less path
        if (trigBits->accept(i)) evtPathFired_[ip] = 1;
        break;
      }
    }
  }

  // ---- 4. per gen electron matching ----
  for (size_t ie = 0; ie < genEles.size(); ++ie) {
    const auto* ge = genEles[ie];
    genEle_pt_.push_back(ge->pt());
    genEle_eta_.push_back(ge->eta());
    genEle_phi_.push_back(ge->phi());
    genEle_charge_.push_back(ge->charge());
    genEle_tmIdx_.push_back(genEleTM[ie]);

    std::vector<int>   mPath(paths_.size(), 0);
    std::vector<float> mDR(paths_.size(), 999.f);
    std::vector<float> mPt(paths_.size(), -1.f);

    for (size_t ip = 0; ip < paths_.size(); ++ip) {
      const std::string wc = paths_[ip] + "*";  // wildcard for version suffix
      float bestDR = 999.f;
      float bestPt = -1.f;
      for (const auto& obj : unpacked) {
        if (!obj.hasPathName(wc.c_str(), /*pathLastFilterAccepted=*/true,
                             /*pathL3FilterAccepted=*/true))
          continue;
        float dR = reco::deltaR(ge->eta(), ge->phi(), obj.eta(), obj.phi());
        if (dR < bestDR) {
          bestDR = dR;
          bestPt = obj.pt();
        }
      }
      mDR[ip] = bestDR;
      mPt[ip] = bestPt;
      mPath[ip] = (bestDR < maxDR_) ? 1 : 0;
    }

    genEle_matchedPath_.push_back(mPath);
    genEle_matchDR_.push_back(mDR);
    genEle_matchTrgPt_.push_back(mPt);
  }

  tree_->Fill();
}

DEFINE_FWK_MODULE(GenTrigMatcher);
