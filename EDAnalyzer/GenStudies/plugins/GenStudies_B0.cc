// -*- C++ -*-
//
// Package:    EDAnalyzer/GenStudies
// Class:      GenStudies_B0
//
// EDAnalyzer for B0 -> K*0 TM, K*0 -> K+ pi-, TM -> e+ e-
// (and charge-conjugate B0-bar -> K*0-bar TM, K*0-bar -> K- pi+)
//
// PDG IDs:
//   B0:    511   (B0-bar: -511)
//   K*0:   313   (K*0-bar: -313)
//   K+:    321
//   pi+:   211
//   TM:    4900022
//   e-/e+: 11 / -11
//

#include <memory>
#include <vector>
#include <cmath>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"

class GenStudies_B0 : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit GenStudies_B0(const edm::ParameterSet&);
  ~GenStudies_B0() override = default;
  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  const reco::Candidate* findDaughter(const reco::Candidate* mom, int pdgId) const;
  const reco::Candidate* findDaughterAbs(const reco::Candidate* mom, int absPdgId) const;

  edm::EDGetTokenT<std::vector<reco::GenParticle>> genParticlesToken_;
  TTree* tree_;

  // mother (B0/B0-bar)
  float mom_pt_, mom_eta_, mom_phi_, mom_mass_;
  float mom_vx_, mom_vy_, mom_vz_;
  int   mom_pdgId_;

  // K*0 (partner)
  float kstar_pt_, kstar_eta_, kstar_phi_, kstar_mass_;
  int   kstar_pdgId_;

  // K from K*0 decay (charged kaon)
  float kaon_pt_, kaon_eta_, kaon_phi_;
  int   kaon_charge_;

  // pi from K*0 decay (charged pion)
  float pion_pt_, pion_eta_, pion_phi_;
  int   pion_charge_;

  // TM
  float tm_pt_, tm_eta_, tm_phi_, tm_mass_;
  float tm_vx_, tm_vy_, tm_vz_;
  float tm_decay_vx_, tm_decay_vy_, tm_decay_vz_;
  float tm_Lxyz_;

  // Electrons
  float ele1_pt_, ele1_eta_, ele1_phi_;
  int   ele1_charge_;
  float ele2_pt_, ele2_eta_, ele2_phi_;
  int   ele2_charge_;
  float ele_dR_;
};

GenStudies_B0::GenStudies_B0(const edm::ParameterSet& iConfig)
  : genParticlesToken_(consumes<std::vector<reco::GenParticle>>(
        iConfig.getParameter<edm::InputTag>("genParticles"))) {
  usesResource("TFileService");
}

void GenStudies_B0::beginJob() {
  edm::Service<TFileService> fs;
  tree_ = fs->make<TTree>("Events", "B0 -> K*0 TM, K*0 -> K+pi-, TM -> e+e-");

  // mother
  tree_->Branch("mom_pt",    &mom_pt_,    "mom_pt/F");
  tree_->Branch("mom_eta",   &mom_eta_,   "mom_eta/F");
  tree_->Branch("mom_phi",   &mom_phi_,   "mom_phi/F");
  tree_->Branch("mom_mass",  &mom_mass_,  "mom_mass/F");
  tree_->Branch("mom_vx",    &mom_vx_,    "mom_vx/F");
  tree_->Branch("mom_vy",    &mom_vy_,    "mom_vy/F");
  tree_->Branch("mom_vz",    &mom_vz_,    "mom_vz/F");
  tree_->Branch("mom_pdgId", &mom_pdgId_, "mom_pdgId/I");

  // K*0
  tree_->Branch("kstar_pt",    &kstar_pt_,    "kstar_pt/F");
  tree_->Branch("kstar_eta",   &kstar_eta_,   "kstar_eta/F");
  tree_->Branch("kstar_phi",   &kstar_phi_,   "kstar_phi/F");
  tree_->Branch("kstar_mass",  &kstar_mass_,  "kstar_mass/F");
  tree_->Branch("kstar_pdgId", &kstar_pdgId_, "kstar_pdgId/I");

  // K from K*0
  tree_->Branch("kaon_pt",     &kaon_pt_,     "kaon_pt/F");
  tree_->Branch("kaon_eta",    &kaon_eta_,    "kaon_eta/F");
  tree_->Branch("kaon_phi",    &kaon_phi_,    "kaon_phi/F");
  tree_->Branch("kaon_charge", &kaon_charge_, "kaon_charge/I");

  // pi from K*0
  tree_->Branch("pion_pt",     &pion_pt_,     "pion_pt/F");
  tree_->Branch("pion_eta",    &pion_eta_,    "pion_eta/F");
  tree_->Branch("pion_phi",    &pion_phi_,    "pion_phi/F");
  tree_->Branch("pion_charge", &pion_charge_, "pion_charge/I");

  // TM
  tree_->Branch("tm_pt",         &tm_pt_,         "tm_pt/F");
  tree_->Branch("tm_eta",        &tm_eta_,        "tm_eta/F");
  tree_->Branch("tm_phi",        &tm_phi_,        "tm_phi/F");
  tree_->Branch("tm_mass",       &tm_mass_,       "tm_mass/F");
  tree_->Branch("tm_vx",         &tm_vx_,         "tm_vx/F");
  tree_->Branch("tm_vy",         &tm_vy_,         "tm_vy/F");
  tree_->Branch("tm_vz",         &tm_vz_,         "tm_vz/F");
  tree_->Branch("tm_decay_vx",   &tm_decay_vx_,   "tm_decay_vx/F");
  tree_->Branch("tm_decay_vy",   &tm_decay_vy_,   "tm_decay_vy/F");
  tree_->Branch("tm_decay_vz",   &tm_decay_vz_,   "tm_decay_vz/F");
  tree_->Branch("tm_Lxyz",       &tm_Lxyz_,       "tm_Lxyz/F");

  // electrons
  tree_->Branch("ele1_pt",     &ele1_pt_,     "ele1_pt/F");
  tree_->Branch("ele1_eta",    &ele1_eta_,    "ele1_eta/F");
  tree_->Branch("ele1_phi",    &ele1_phi_,    "ele1_phi/F");
  tree_->Branch("ele1_charge", &ele1_charge_, "ele1_charge/I");
  tree_->Branch("ele2_pt",     &ele2_pt_,     "ele2_pt/F");
  tree_->Branch("ele2_eta",    &ele2_eta_,    "ele2_eta/F");
  tree_->Branch("ele2_phi",    &ele2_phi_,    "ele2_phi/F");
  tree_->Branch("ele2_charge", &ele2_charge_, "ele2_charge/I");
  tree_->Branch("ele_dR",      &ele_dR_,      "ele_dR/F");
}

const reco::Candidate* GenStudies_B0::findDaughter(const reco::Candidate* mom, int pdgId) const {
  if (!mom) return nullptr;
  for (size_t i = 0; i < mom->numberOfDaughters(); ++i) {
    const reco::Candidate* d = mom->daughter(i);
    if (d && d->pdgId() == pdgId) return d;
  }
  return nullptr;
}

const reco::Candidate* GenStudies_B0::findDaughterAbs(const reco::Candidate* mom, int absPdgId) const {
  if (!mom) return nullptr;
  for (size_t i = 0; i < mom->numberOfDaughters(); ++i) {
    const reco::Candidate* d = mom->daughter(i);
    if (d && std::abs(d->pdgId()) == absPdgId) return d;
  }
  return nullptr;
}

void GenStudies_B0::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
  edm::Handle<std::vector<reco::GenParticle>> genParticles;
  iEvent.getByToken(genParticlesToken_, genParticles);

  for (const auto& p : *genParticles) {
    if (std::abs(p.pdgId()) != 511) continue;          // B0 or B0-bar

    // Find K*0 daughter (313 for B0, -313 for B0-bar)
    const reco::Candidate* kstar = findDaughterAbs(&p, 313);
    if (!kstar) continue;

    const reco::Candidate* tm = findDaughter(&p, 4900022);
    if (!tm) continue;

    // K*0 -> K+ pi- (or K- pi+ for K*0-bar)
    const reco::Candidate* kaon = findDaughterAbs(kstar, 321);
    const reco::Candidate* pion = findDaughterAbs(kstar, 211);
    if (!kaon || !pion) continue;

    // TM -> e+ e-
    const reco::Candidate* ele_minus = findDaughter(tm,  11);
    const reco::Candidate* ele_plus  = findDaughter(tm, -11);
    if (!ele_minus || !ele_plus) continue;

    // Mother
    mom_pt_    = p.pt();
    mom_eta_   = p.eta();
    mom_phi_   = p.phi();
    mom_mass_  = p.mass();
    mom_vx_    = p.vx();
    mom_vy_    = p.vy();
    mom_vz_    = p.vz();
    mom_pdgId_ = p.pdgId();

    // K*0
    kstar_pt_    = kstar->pt();
    kstar_eta_   = kstar->eta();
    kstar_phi_   = kstar->phi();
    kstar_mass_  = kstar->mass();
    kstar_pdgId_ = kstar->pdgId();

    // K
    kaon_pt_     = kaon->pt();
    kaon_eta_    = kaon->eta();
    kaon_phi_    = kaon->phi();
    kaon_charge_ = kaon->charge();

    // pion
    pion_pt_     = pion->pt();
    pion_eta_    = pion->eta();
    pion_phi_    = pion->phi();
    pion_charge_ = pion->charge();

    // TM
    tm_pt_   = tm->pt();
    tm_eta_  = tm->eta();
    tm_phi_  = tm->phi();
    tm_mass_ = tm->mass();
    tm_vx_   = tm->vx();
    tm_vy_   = tm->vy();
    tm_vz_   = tm->vz();
    tm_decay_vx_ = ele_minus->vx();
    tm_decay_vy_ = ele_minus->vy();
    tm_decay_vz_ = ele_minus->vz();
    const float dx = tm_decay_vx_ - tm_vx_;
    const float dy = tm_decay_vy_ - tm_vy_;
    const float dz = tm_decay_vz_ - tm_vz_;
    tm_Lxyz_ = std::sqrt(dx*dx + dy*dy + dz*dz);

    ele1_pt_     = ele_minus->pt();
    ele1_eta_    = ele_minus->eta();
    ele1_phi_    = ele_minus->phi();
    ele1_charge_ = ele_minus->charge();
    ele2_pt_     = ele_plus->pt();
    ele2_eta_    = ele_plus->eta();
    ele2_phi_    = ele_plus->phi();
    ele2_charge_ = ele_plus->charge();
    ele_dR_      = reco::deltaR(*ele_minus, *ele_plus);

    tree_->Fill();
  }
}

void GenStudies_B0::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("genParticles", edm::InputTag("genParticles"));
  descriptions.add("genStudies_B0", desc);
}

DEFINE_FWK_MODULE(GenStudies_B0);
