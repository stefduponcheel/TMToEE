// -*- C++ -*-
//
// Package:    TMToEE/TrigObjNearest
// Class:      TrigObjNearest
//
// Description: Trigger-object-driven, NO CONE CUT, with parent-TM bookkeeping.
//
//
//   For each event where a DoubleEle low-mass path FIRED:
//     - take the trigger objects on that path,
//     - find the GLOBALLY NEAREST final-state gen electron (any origin), NO dR cut,
//     - store its dR, pt, dPt(rel), immediate mother, first non-(e/gamma) ancestor,
//       whether it is from a TM, AND a stable per-event index of WHICH TM it came
//       from (near_tmIdx) plus that TM's kinematics.
//
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
#include <map>
#include <iostream>

class TrigObjNearest : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit TrigObjNearest(const edm::ParameterSet&);
  ~TrigObjNearest() override = default;

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  const reco::Candidate* firstRealAncestor(const reco::Candidate* p) const;
  const reco::Candidate* tmAncestor(const reco::Candidate* ele) const;
  const reco::Candidate* tmLastCopy(const reco::Candidate* tm) const;

  const edm::EDGetTokenT<std::vector<reco::GenParticle>> genToken_;
  const edm::EDGetTokenT<edm::TriggerResults> trigBitsToken_;
  const edm::EDGetTokenT<std::vector<pat::TriggerObjectStandAlone>> trigObjToken_;

  const int tmPdgId_;
  const std::vector<std::string> paths_;
  const bool lastFilter_;
  const bool l3Filter_;

  edm::Service<TFileService> fs_;
  TTree* tree_;

  int  run_, lumi_;
  long event_;

  // per trigger object (one entry per object on a fired path)
  int   to_pathIdx_;
  float to_pt_, to_eta_, to_phi_;

  // NEAREST gen electron (no cone cut)
  float near_dR_;
  float near_ele_pt_;
  float near_ele_eta_;
  float near_ele_phi_;
  int   near_ele_charge_;
  float near_dPt_;
  float near_dPtRel_;
  int   near_motherId_;
  int   near_ancestorId_;
  int   near_fromTM_;       // 1 if ancestor is 4900022

  // parent-TM bookkeeping
  int   near_tmIdx_;        // stable per-event TM index, -1 if not from a TM
  float near_tm_pt_;
  float near_tm_eta_;
  float near_tm_phi_;
};

TrigObjNearest::TrigObjNearest(const edm::ParameterSet& ps)
    : genToken_(consumes<std::vector<reco::GenParticle>>(ps.getParameter<edm::InputTag>("genParticles"))),
      trigBitsToken_(consumes<edm::TriggerResults>(ps.getParameter<edm::InputTag>("bits"))),
      trigObjToken_(consumes<std::vector<pat::TriggerObjectStandAlone>>(ps.getParameter<edm::InputTag>("objects"))),
      tmPdgId_(ps.getParameter<int>("tmPdgId")),
      paths_(ps.getParameter<std::vector<std::string>>("paths")),
      lastFilter_(ps.getParameter<bool>("lastFilter")),
      l3Filter_(ps.getParameter<bool>("l3Filter")) {
  usesResource("TFileService");
}

void TrigObjNearest::beginJob() {
  tree_ = fs_->make<TTree>("trigObj", "trig object -> nearest gen electron, no cone, with parent TM");

  tree_->Branch("run", &run_);
  tree_->Branch("lumi", &lumi_);
  tree_->Branch("event", &event_);

  tree_->Branch("to_pathIdx", &to_pathIdx_);
  tree_->Branch("to_pt", &to_pt_);
  tree_->Branch("to_eta", &to_eta_);
  tree_->Branch("to_phi", &to_phi_);

  tree_->Branch("near_dR", &near_dR_);
  tree_->Branch("near_ele_pt", &near_ele_pt_);
  tree_->Branch("near_ele_eta", &near_ele_eta_);
  tree_->Branch("near_ele_phi", &near_ele_phi_);
  tree_->Branch("near_ele_charge", &near_ele_charge_);
  tree_->Branch("near_dPt", &near_dPt_);
  tree_->Branch("near_dPtRel", &near_dPtRel_);
  tree_->Branch("near_motherId", &near_motherId_);
  tree_->Branch("near_ancestorId", &near_ancestorId_);
  tree_->Branch("near_fromTM", &near_fromTM_);

  tree_->Branch("near_tmIdx", &near_tmIdx_);
  tree_->Branch("near_tm_pt", &near_tm_pt_);
  tree_->Branch("near_tm_eta", &near_tm_eta_);
  tree_->Branch("near_tm_phi", &near_tm_phi_);

  std::cout << "[TrigObjNearest] Path index mapping:" << std::endl;
  for (size_t i = 0; i < paths_.size(); ++i)
    std::cout << "    [" << i << "] " << paths_[i] << std::endl;
}

const reco::Candidate* TrigObjNearest::firstRealAncestor(const reco::Candidate* p) const {
  const reco::Candidate* cur = p;
  while (cur != nullptr && cur->numberOfMothers() > 0) {
    const reco::Candidate* mom = cur->mother(0);
    if (mom == nullptr) break;
    int amom = std::abs(mom->pdgId());
    if (amom == 11 || amom == 22) cur = mom;
    else return mom;
  }
  return nullptr;
}

// climb past e/gamma copies; return the TM (4900022) if that's the first real ancestor
const reco::Candidate* TrigObjNearest::tmAncestor(const reco::Candidate* ele) const {
  const reco::Candidate* cur = ele;
  while (cur != nullptr && cur->numberOfMothers() > 0) {
    const reco::Candidate* mom = cur->mother(0);
    if (mom == nullptr) break;
    if (mom->pdgId() == tmPdgId_) return mom;
    int amom = std::abs(mom->pdgId());
    if (amom == 11 || amom == 22) { cur = mom; continue; }
    return nullptr;  // first real ancestor is not a TM
  }
  return nullptr;
}

// collapse TM copies: walk down TM->TM until the last copy (whose daughters are the electrons).
// Since ALL TMs decay to e+e-, the last copy is unambiguous.
const reco::Candidate* TrigObjNearest::tmLastCopy(const reco::Candidate* tm) const {
  const reco::Candidate* cur = tm;
  bool advanced = true;
  while (advanced) {
    advanced = false;
    for (size_t i = 0; i < cur->numberOfDaughters(); ++i) {
      if (cur->daughter(i)->pdgId() == tmPdgId_) {
        cur = cur->daughter(i);
        advanced = true;
        break;
      }
    }
  }
  return cur;
}

void TrigObjNearest::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
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

  // which paths fired
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
  // temporary debug, right after computing pathFired/anyFired:
    int nNameMatched = 0;
    for (size_t ip = 0; ip < paths_.size(); ++ip) {
    for (unsigned i = 0; i < trigNames.size(); ++i) {
        if (trigNames.triggerName(i).rfind(paths_[ip],0)==0) { nNameMatched++; break; }
    }
    }
    std::cout << "event " << iEvent.id().event()
            << " nNameMatched=" << nNameMatched
            << " anyFired=" << anyFired << std::endl;
  if (!anyFired) return;

  // all final-state gen electrons (any origin)
  std::vector<const reco::GenParticle*> genEles;
  for (const auto& gp : *genHandle) {
    if (std::abs(gp.pdgId()) != 11) continue;
    if (gp.status() != 1) continue;
    genEles.push_back(&gp);
  }
  if (genEles.empty()) return;

  // per-event stable TM index map (keyed on the TM's last copy pointer)
  std::map<const reco::Candidate*, int> tmToIdx;
  int nextTM = 0;
  auto getTMInfo = [&](const reco::Candidate* ele,
                       int& idx, float& tpt, float& teta, float& tphi) {
    const reco::Candidate* tm = tmAncestor(ele);
    if (!tm) { idx = -1; tpt = teta = tphi = -999.f; return; }
    const reco::Candidate* last = tmLastCopy(tm);
    auto it = tmToIdx.find(last);
    if (it == tmToIdx.end()) {
      idx = nextTM++;
      tmToIdx[last] = idx;
    } else {
      idx = it->second;
    }
    tpt  = last->pt();
    teta = last->eta();
    tphi = last->phi();
  };

  // unpack objects
  std::vector<pat::TriggerObjectStandAlone> unpacked;
  unpacked.reserve(trigObjs->size());
  for (const auto& obj0 : *trigObjs) {
    pat::TriggerObjectStandAlone obj = obj0;
    obj.unpackPathNames(trigNames);
    obj.unpackFilterLabels(iEvent, *trigBits);
    unpacked.push_back(obj);
  }

  for (size_t ip = 0; ip < paths_.size(); ++ip) {
    if (!pathFired[ip]) continue;
    const std::string wc = paths_[ip] + "*";

    for (const auto& obj : unpacked) {
      if (!obj.hasPathName(wc.c_str(), lastFilter_, l3Filter_)) continue;

      // global nearest gen electron, no cone
      const reco::GenParticle* best = nullptr;
      float bestDR = 1e9f;
      for (const auto* ge : genEles) {
        float dR = reco::deltaR(obj.eta(), obj.phi(), ge->eta(), ge->phi());
        if (dR < bestDR) { bestDR = dR; best = ge; }
      }

      to_pathIdx_ = (int)ip;
      to_pt_  = obj.pt();
      to_eta_ = obj.eta();
      to_phi_ = obj.phi();

      near_dR_         = bestDR;
      near_ele_pt_     = best->pt();
      near_ele_eta_    = best->eta();
      near_ele_phi_    = best->phi();
      near_ele_charge_ = best->charge();
      near_dPt_        = obj.pt() - best->pt();
      near_dPtRel_     = (obj.pt() > 0) ? (obj.pt() - best->pt()) / obj.pt() : -999.f;
      near_motherId_   = (best->numberOfMothers() > 0) ? best->mother(0)->pdgId() : 0;
      const reco::Candidate* anc = firstRealAncestor(best);
      near_ancestorId_ = (anc != nullptr) ? anc->pdgId() : 0;
      near_fromTM_     = (near_ancestorId_ == tmPdgId_) ? 1 : 0;

      // which TM
      getTMInfo(best, near_tmIdx_, near_tm_pt_, near_tm_eta_, near_tm_phi_);

      tree_->Fill();
    }
  }
}

DEFINE_FWK_MODULE(TrigObjNearest);
