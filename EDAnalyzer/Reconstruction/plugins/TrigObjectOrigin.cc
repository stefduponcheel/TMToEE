// -*- C++ -*-
//
// Package:    TMToEE/TrigObjOrigin
// Class:      TrigObjOrigin
//
// Description: Trigger-object-driven matching diagnostic.
//
//   For each event where a DoubleEle low-mass path FIRED:
//     - take the trigger objects on that path,
//     - build a dR < coneDR cone around each object,
//     - find all final-state gen electrons inside the cone,
//     - if exactly one  -> that's the match,
//       if more than one -> take the smallest-dR one (ambiguous flag set),
//       if none          -> no match (still stored, with flags = empty).
//     - store dR, dPt(obj,ele), and the matched gen electron's
//       immediate mother pdgId AND first non-(e/gamma) ancestor pdgId,
//       so we can see WHERE the matched electron actually came from.
//
//   Events where no path fired are skipped entirely.
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

class TrigObjOrigin : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit TrigObjOrigin(const edm::ParameterSet&);
  ~TrigObjOrigin() override = default;

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  // walk up the mother chain past e/gamma copies to the first "real" ancestor
  const reco::Candidate* firstRealAncestor(const reco::Candidate* p) const;

  // tokens
  const edm::EDGetTokenT<std::vector<reco::GenParticle>> genToken_;
  const edm::EDGetTokenT<edm::TriggerResults> trigBitsToken_;
  const edm::EDGetTokenT<std::vector<pat::TriggerObjectStandAlone>> trigObjToken_;

  // config
  const double coneDR_;
  const std::vector<std::string> paths_;
  const bool lastFilter_;   // hasPathName pathLastFilterAccepted arg
  const bool l3Filter_;     // hasPathName pathL3FilterAccepted arg

  // output
  edm::Service<TFileService> fs_;
  TTree* tree_;

  int  run_, lumi_;
  long event_;

  // per trigger object (one tree entry per object on a fired path)
  int   to_pathIdx_;        // which path (index into paths_)
  float to_pt_, to_eta_, to_phi_;
  int   to_nGenInCone_;     // how many gen electrons within coneDR
  // matched gen electron (smallest dR if multiple); -999 if none
  float match_ele_pt_, match_ele_eta_, match_ele_phi_;
  int   match_ele_charge_;
  float match_dR_;          // dR(obj, matched ele)
  float match_dPt_;         // (obj.pt - ele.pt)
  float match_dPtRel_;      // (obj.pt - ele.pt)/obj.pt
  int   match_motherId_;    // immediate mother pdgId of matched ele
  int   match_ancestorId_;  // first non-(e/gamma) ancestor pdgId
  int   match_isAmbiguous_; // 1 if >1 gen ele in cone
};

TrigObjOrigin::TrigObjOrigin(const edm::ParameterSet& ps)
    : genToken_(consumes<std::vector<reco::GenParticle>>(ps.getParameter<edm::InputTag>("genParticles"))),
      trigBitsToken_(consumes<edm::TriggerResults>(ps.getParameter<edm::InputTag>("bits"))),
      trigObjToken_(consumes<std::vector<pat::TriggerObjectStandAlone>>(ps.getParameter<edm::InputTag>("objects"))),
      coneDR_(ps.getParameter<double>("coneDR")),
      paths_(ps.getParameter<std::vector<std::string>>("paths")),
      lastFilter_(ps.getParameter<bool>("lastFilter")),
      l3Filter_(ps.getParameter<bool>("l3Filter")) {
  usesResource("TFileService");
}

void TrigObjOrigin::beginJob() {
  tree_ = fs_->make<TTree>("trigObj", "trigger-object-driven origin matching");

  tree_->Branch("run", &run_);
  tree_->Branch("lumi", &lumi_);
  tree_->Branch("event", &event_);

  tree_->Branch("to_pathIdx", &to_pathIdx_);
  tree_->Branch("to_pt", &to_pt_);
  tree_->Branch("to_eta", &to_eta_);
  tree_->Branch("to_phi", &to_phi_);
  tree_->Branch("to_nGenInCone", &to_nGenInCone_);

  tree_->Branch("match_ele_pt", &match_ele_pt_);
  tree_->Branch("match_ele_eta", &match_ele_eta_);
  tree_->Branch("match_ele_phi", &match_ele_phi_);
  tree_->Branch("match_ele_charge", &match_ele_charge_);
  tree_->Branch("match_dR", &match_dR_);
  tree_->Branch("match_dPt", &match_dPt_);
  tree_->Branch("match_dPtRel", &match_dPtRel_);
  tree_->Branch("match_motherId", &match_motherId_);
  tree_->Branch("match_ancestorId", &match_ancestorId_);
  tree_->Branch("match_isAmbiguous", &match_isAmbiguous_);

  std::cout << "[TrigObjOrigin] Path index mapping:" << std::endl;
  for (size_t i = 0; i < paths_.size(); ++i)
    std::cout << "    [" << i << "] " << paths_[i] << std::endl;
}

const reco::Candidate* TrigObjOrigin::firstRealAncestor(const reco::Candidate* p) const {
  // climb mothers while the mother is an electron or photon (brem/copy chain),
  // return the first ancestor that is neither e nor gamma
  const reco::Candidate* cur = p;
  while (cur != nullptr && cur->numberOfMothers() > 0) {
    const reco::Candidate* mom = cur->mother(0);
    if (mom == nullptr) break;
    int amom = std::abs(mom->pdgId());
    if (amom == 11 || amom == 22) {
      cur = mom;  // keep climbing past e/gamma
    } else {
      return mom; // first non-(e/gamma) ancestor
    }
  }
  return nullptr;
}

void TrigObjOrigin::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
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

  // ---- which of our paths fired this event? ----
  std::vector<bool> pathFired(paths_.size(), false);
  bool anyFired = false;
  for (size_t ip = 0; ip < paths_.size(); ++ip) {
    for (unsigned i = 0; i < trigNames.size(); ++i) {
      const std::string& name = trigNames.triggerName(i);
      if (name.rfind(paths_[ip], 0) == 0) {
        if (trigBits->accept(i)) { pathFired[ip] = true; anyFired = true; }
        break;
      }
    }
  }
  if (!anyFired) return;  // skip events where no path fired

  // ---- collect all final-state gen electrons (any origin) ----
  std::vector<const reco::GenParticle*> genEles;
  for (const auto& gp : *genHandle) {
    if (std::abs(gp.pdgId()) != 11) continue;
    if (gp.status() != 1) continue;
    genEles.push_back(&gp);
  }

  // ---- unpack trigger objects once ----
  std::vector<pat::TriggerObjectStandAlone> unpacked;
  unpacked.reserve(trigObjs->size());
  for (const auto& obj0 : *trigObjs) {
    pat::TriggerObjectStandAlone obj = obj0;
    obj.unpackPathNames(trigNames);
    obj.unpackFilterLabels(iEvent, *trigBits);
    unpacked.push_back(obj);
  }

  // ---- for each fired path, loop objects on that path ----
  for (size_t ip = 0; ip < paths_.size(); ++ip) {
    if (!pathFired[ip]) continue;
    const std::string wc = paths_[ip] + "*";

    for (const auto& obj : unpacked) {
      if (!obj.hasPathName(wc.c_str(), lastFilter_, l3Filter_)) continue;

      // find gen electrons within the cone
      const reco::GenParticle* best = nullptr;
      float bestDR = 999.f;
      int nInCone = 0;
      for (const auto* ge : genEles) {
        float dR = reco::deltaR(obj.eta(), obj.phi(), ge->eta(), ge->phi());
        if (dR < coneDR_) {
          nInCone++;
          if (dR < bestDR) { bestDR = dR; best = ge; }
        }
      }

      // fill one entry per trigger object
      to_pathIdx_    = (int)ip;
      to_pt_         = obj.pt();
      to_eta_        = obj.eta();
      to_phi_        = obj.phi();
      to_nGenInCone_ = nInCone;

      if (best != nullptr) {
        match_ele_pt_     = best->pt();
        match_ele_eta_    = best->eta();
        match_ele_phi_    = best->phi();
        match_ele_charge_ = best->charge();
        match_dR_         = bestDR;
        match_dPt_        = obj.pt() - best->pt();
        match_dPtRel_     = (obj.pt() > 0) ? (obj.pt() - best->pt()) / obj.pt() : -999.f;
        match_motherId_   = (best->numberOfMothers() > 0) ? best->mother(0)->pdgId() : 0;
        const reco::Candidate* anc = firstRealAncestor(best);
        match_ancestorId_ = (anc != nullptr) ? anc->pdgId() : 0;
        match_isAmbiguous_ = (nInCone > 1) ? 1 : 0;
      } else {
        match_ele_pt_ = match_ele_eta_ = match_ele_phi_ = -999.f;
        match_ele_charge_ = 0;
        match_dR_ = match_dPt_ = match_dPtRel_ = -999.f;
        match_motherId_ = match_ancestorId_ = 0;
        match_isAmbiguous_ = 0;
      }

      tree_->Fill();
    }
  }
}

DEFINE_FWK_MODULE(TrigObjOrigin);
