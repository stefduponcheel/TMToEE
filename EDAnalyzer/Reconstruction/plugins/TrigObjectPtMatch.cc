// -*- C++ -*-
// TrigObjPtMatch: for each trigger object on a fired path,
// find the gen particle with most similar pT within dR < 0.3
// Stores pdgId, mother pdgId, ancestor pdgId for offline classification

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
#include "TMath.h"

#include <vector>
#include <string>
#include <cmath>
#include <map>

class TrigObjPtMatch : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit TrigObjPtMatch(const edm::ParameterSet&);
  ~TrigObjPtMatch() override = default;

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  const reco::Candidate* tmAncestor(const reco::Candidate* p) const;
  const reco::Candidate* tmLastCopy(const reco::Candidate* tm) const;
  const reco::Candidate* firstRealAncestor(const reco::Candidate* p) const;

  const edm::EDGetTokenT<std::vector<reco::GenParticle>> genToken_;
  const edm::EDGetTokenT<edm::TriggerResults> trigBitsToken_;
  const edm::EDGetTokenT<std::vector<pat::TriggerObjectStandAlone>> trigObjToken_;

  const int tmPdgId_;
  const std::vector<std::string> paths_;
  const bool lastFilter_;
  const bool l3Filter_;
  const float coneSize_;  // 0.3

  edm::Service<TFileService> fs_;
  TTree* tree_;

  int  run_, lumi_;
  long event_;

  // trigger object
  int   to_pathIdx_;
  float to_pt_, to_eta_, to_phi_;

  // best pT match within cone
  int   match_found_;       // 1 if any gen particle in cone, 0 otherwise
  float match_dR_;
  float match_dPtRel_;      // (trig_pt - gen_pt) / trig_pt
  float match_pt_;
  float match_eta_;
  float match_phi_;
  int   match_pdgId_;       // for offline classification
  int   match_status_;
  int   match_motherId_;
  int   match_ancestorId_;  // first non-e/gamma ancestor
  int   match_fromTM_;      // 1 if ancestor is TM

  // TM bookkeeping (filled if match_fromTM_==1)
  int   match_tmIdx_;
  float match_tm_pt_;
  float match_tm_eta_;
  float match_tm_phi_;

  // nearest in dR within cone (for comparison)
  float nearDR_dR_;
  float nearDR_dPtRel_;
  int   nearDR_pdgId_;
  int   nearDR_fromTM_;
};

TrigObjPtMatch::TrigObjPtMatch(const edm::ParameterSet& ps)
    : genToken_(consumes<std::vector<reco::GenParticle>>(ps.getParameter<edm::InputTag>("genParticles"))),
      trigBitsToken_(consumes<edm::TriggerResults>(ps.getParameter<edm::InputTag>("bits"))),
      trigObjToken_(consumes<std::vector<pat::TriggerObjectStandAlone>>(ps.getParameter<edm::InputTag>("objects"))),
      tmPdgId_(ps.getParameter<int>("tmPdgId")),
      paths_(ps.getParameter<std::vector<std::string>>("paths")),
      lastFilter_(ps.getParameter<bool>("lastFilter")),
      l3Filter_(ps.getParameter<bool>("l3Filter")),
      coneSize_(ps.getParameter<double>("coneSize")){
  usesResource("TFileService");
}

void TrigObjPtMatch::beginJob() {
  tree_ = fs_->make<TTree>("trigObjPtMatch", "trig object -> best pT-matched gen particle in dR<0.3");

  tree_->Branch("run",   &run_);
  tree_->Branch("lumi",  &lumi_);
  tree_->Branch("event", &event_);

  tree_->Branch("to_pathIdx", &to_pathIdx_);
  tree_->Branch("to_pt",      &to_pt_);
  tree_->Branch("to_eta",     &to_eta_);
  tree_->Branch("to_phi",     &to_phi_);

  tree_->Branch("match_found",      &match_found_);
  tree_->Branch("match_dR",         &match_dR_);
  tree_->Branch("match_dPtRel",     &match_dPtRel_);
  tree_->Branch("match_pt",         &match_pt_);
  tree_->Branch("match_eta",        &match_eta_);
  tree_->Branch("match_phi",        &match_phi_);
  tree_->Branch("match_pdgId",      &match_pdgId_);
  tree_->Branch("match_status",     &match_status_);
  tree_->Branch("match_motherId",   &match_motherId_);
  tree_->Branch("match_ancestorId", &match_ancestorId_);
  tree_->Branch("match_fromTM",     &match_fromTM_);

  tree_->Branch("match_tmIdx",  &match_tmIdx_);
  tree_->Branch("match_tm_pt",  &match_tm_pt_);
  tree_->Branch("match_tm_eta", &match_tm_eta_);
  tree_->Branch("match_tm_phi", &match_tm_phi_);

  // nearest dR for comparison
  tree_->Branch("nearDR_dR",      &nearDR_dR_);
  tree_->Branch("nearDR_dPtRel",  &nearDR_dPtRel_);
  tree_->Branch("nearDR_pdgId",   &nearDR_pdgId_);
  tree_->Branch("nearDR_fromTM",  &nearDR_fromTM_);
}

const reco::Candidate* TrigObjPtMatch::firstRealAncestor(const reco::Candidate* p) const {
  const reco::Candidate* cur = p;
  while (cur && cur->numberOfMothers() > 0) {
    const reco::Candidate* mom = cur->mother(0);
    if (!mom) break;
    int aid = std::abs(mom->pdgId());
    if (aid == 11 || aid == 22) cur = mom;
    else return mom;
  }
  return nullptr;
}

const reco::Candidate* TrigObjPtMatch::tmAncestor(const reco::Candidate* p) const {
  const reco::Candidate* cur = p;
  while (cur && cur->numberOfMothers() > 0) {
    const reco::Candidate* mom = cur->mother(0);
    if (!mom) break;
    if (mom->pdgId() == tmPdgId_) return mom;
    int aid = std::abs(mom->pdgId());
    if (aid == 11 || aid == 22) { cur = mom; continue; }
    return nullptr;
  }
  return nullptr;
}

const reco::Candidate* TrigObjPtMatch::tmLastCopy(const reco::Candidate* tm) const {
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

void TrigObjPtMatch::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
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
      if (trigNames.triggerName(i).rfind(paths_[ip], 0) == 0) {
        if (trigBits->accept(i)) { pathFired[ip] = true; anyFired = true; }
        break;
      }
    }
  }
  if (!anyFired) return;

  // Only match against genuinely final-state particles. A trigger object
  // corresponds to an actual reconstructed detector object, so it can never
  // legitimately match an intermediate particle like TM itself (or its
  // shower-recoil copies) -- TM decays before reaching the detector. Without
  // this, TM can end up as the closest/best-pT gen match purely by kinematic
  // coincidence, and firstRealAncestor() would then walk up to TM's *own*
  // mother (a quark/gluon) instead of TM, silently making match_fromTM_ come
  // out false even when the trigger really was caused by a TM-descended
  // electron. Require both status()==1 (Pythia8's own final-state
  // designation) and numberOfDaughters()==0 (the persisted record has no
  // further decay listed) -- they should normally agree, but combining them
  // guards against edge cases where they might not (e.g. if genTag ever
  // points at a pruned collection instead of our full, unpruned one).
  std::vector<const reco::GenParticle*> genParts;
  for (const auto& gp : *genHandle) {
    if (gp.status() == 1) genParts.push_back(&gp);
  }

  if (genParts.empty()) return;

  // per-event TM index map
  std::map<const reco::Candidate*, int> tmToIdx;
  int nextTM = 0;
  auto getTMInfo = [&](const reco::Candidate* p,
                       int& idx, float& tpt, float& teta, float& tphi) {
    const reco::Candidate* tm = tmAncestor(p);
    if (!tm) { idx = -1; tpt = teta = tphi = -999.f; return; }
    const reco::Candidate* last = tmLastCopy(tm);
    auto it = tmToIdx.find(last);
    idx = (it == tmToIdx.end()) ? (tmToIdx[last] = nextTM++) : it->second;
    tpt = last->pt(); teta = last->eta(); tphi = last->phi();
  };

  // unpack trigger objects
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

      to_pathIdx_ = (int)ip;
      to_pt_  = obj.pt();
      to_eta_ = obj.eta();
      to_phi_ = obj.phi();

      // find all gen particles in cone, pick best pT match
      const reco::GenParticle* bestPt  = nullptr;  // best pT match
      const reco::GenParticle* bestDR  = nullptr;  // nearest dR (for comparison)
      float bestDPtRel = 1e9f;
      float bestDR_val = 1e9f;

      for (const auto* gp : genParts) {
        float dR = reco::deltaR(obj.eta(), obj.phi(), gp->eta(), gp->phi());
        if (dR > coneSize_) continue;

        // nearest dR
        if (dR < bestDR_val) { bestDR_val = dR; bestDR = gp; }

        // best pT match — minimize |dPtRel|
        float dPtRel = (to_pt_ > 0) ? std::abs(to_pt_ - gp->pt()) / to_pt_ : 1e9f;
        if (dPtRel < bestDPtRel) { bestDPtRel = dPtRel; bestPt = gp; }
      }

      // fill pT-match result
      if (bestPt) {
        match_found_   = 1;
        float dR = reco::deltaR(obj.eta(), obj.phi(), bestPt->eta(), bestPt->phi());
        match_dR_      = dR;
        match_dPtRel_  = (to_pt_ > 0) ? (to_pt_ - bestPt->pt()) / to_pt_ : -999.f;
        match_pt_      = bestPt->pt();
        match_eta_     = bestPt->eta();
        match_phi_     = bestPt->phi();
        match_pdgId_   = bestPt->pdgId();
        match_status_  = bestPt->status();
        match_motherId_ = (bestPt->numberOfMothers() > 0) ? bestPt->mother(0)->pdgId() : 0;
        const reco::Candidate* anc = firstRealAncestor(bestPt);
        match_ancestorId_ = anc ? anc->pdgId() : 0;
        match_fromTM_  = (match_ancestorId_ == tmPdgId_) ? 1 : 0;
        getTMInfo(bestPt, match_tmIdx_, match_tm_pt_, match_tm_eta_, match_tm_phi_);
      } else {
        match_found_   = 0;
        match_dR_ = match_dPtRel_ = match_pt_ = match_eta_ = match_phi_ = -999.f;
        match_pdgId_ = match_status_ = match_motherId_ = match_ancestorId_ = 0;
        match_fromTM_ = 0;
        match_tmIdx_ = -1;
        match_tm_pt_ = match_tm_eta_ = match_tm_phi_ = -999.f;
      }

      // fill nearest dR for comparison
      if (bestDR) {
        nearDR_dR_     = bestDR_val;
        nearDR_dPtRel_ = (to_pt_ > 0) ? (to_pt_ - bestDR->pt()) / to_pt_ : -999.f;
        nearDR_pdgId_  = bestDR->pdgId();
        const reco::Candidate* anc = firstRealAncestor(bestDR);
        int ancId = anc ? anc->pdgId() : 0;
        nearDR_fromTM_ = (ancId == tmPdgId_) ? 1 : 0;
      } else {
        nearDR_dR_ = nearDR_dPtRel_ = -999.f;
        nearDR_pdgId_ = nearDR_fromTM_ = 0;
      }

      tree_->Fill();
    }
  }
}

DEFINE_FWK_MODULE(TrigObjPtMatch);
