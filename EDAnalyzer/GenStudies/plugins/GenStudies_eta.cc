// -*- C++ -*-
// EDAnalyzer for eta -> TM gamma, TM -> e+e-
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

class GenStudies_eta : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit GenStudies_eta(const edm::ParameterSet&);
  ~GenStudies_eta() override = default;
  static void fillDescriptions(edm::ConfigurationDescriptions&);
private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  const reco::Candidate* findDaughter(const reco::Candidate* mom, int pdgId) const;

  edm::EDGetTokenT<std::vector<reco::GenParticle>> genParticlesToken_;
  TTree* tree_;

  // mother (eta)
  float mom_pt_, mom_eta_, mom_phi_, mom_mass_;
  float mom_vx_, mom_vy_, mom_vz_;
  // partner (photon)
  float partner_pt_, partner_eta_, partner_phi_, partner_mass_;
  // TM
  float tm_pt_, tm_eta_, tm_phi_, tm_mass_;
  float tm_vx_, tm_vy_, tm_vz_;
  float tm_decay_vx_, tm_decay_vy_, tm_decay_vz_;
  float tm_Lxyz_;
  // electrons
  float ele1_pt_, ele1_eta_, ele1_phi_;
  int   ele1_charge_;
  float ele2_pt_, ele2_eta_, ele2_phi_;
  int   ele2_charge_;
  float ele_dR_;
};

GenStudies_eta::GenStudies_eta(const edm::ParameterSet& iConfig)
  : genParticlesToken_(consumes<std::vector<reco::GenParticle>>(
        iConfig.getParameter<edm::InputTag>("genParticles"))) {
  usesResource("TFileService");
}

void GenStudies_eta::beginJob() {
  edm::Service<TFileService> fs;
  tree_ = fs->make<TTree>("Events", "eta -> TM gamma -> ee");
  tree_->Branch("mom_pt",   &mom_pt_,   "mom_pt/F");
  tree_->Branch("mom_eta",  &mom_eta_,  "mom_eta/F");
  tree_->Branch("mom_phi",  &mom_phi_,  "mom_phi/F");
  tree_->Branch("mom_mass", &mom_mass_, "mom_mass/F");
  tree_->Branch("mom_vx",   &mom_vx_,   "mom_vx/F");
  tree_->Branch("mom_vy",   &mom_vy_,   "mom_vy/F");
  tree_->Branch("mom_vz",   &mom_vz_,   "mom_vz/F");

  tree_->Branch("partner_pt",   &partner_pt_,   "partner_pt/F");
  tree_->Branch("partner_eta",  &partner_eta_,  "partner_eta/F");
  tree_->Branch("partner_phi",  &partner_phi_,  "partner_phi/F");
  tree_->Branch("partner_mass", &partner_mass_, "partner_mass/F");

  tree_->Branch("tm_pt",   &tm_pt_,   "tm_pt/F");
  tree_->Branch("tm_eta",  &tm_eta_,  "tm_eta/F");
  tree_->Branch("tm_phi",  &tm_phi_,  "tm_phi/F");
  tree_->Branch("tm_mass", &tm_mass_, "tm_mass/F");
  tree_->Branch("tm_vx",   &tm_vx_,   "tm_vx/F");
  tree_->Branch("tm_vy",   &tm_vy_,   "tm_vy/F");
  tree_->Branch("tm_vz",   &tm_vz_,   "tm_vz/F");
  tree_->Branch("tm_decay_vx", &tm_decay_vx_, "tm_decay_vx/F");
  tree_->Branch("tm_decay_vy", &tm_decay_vy_, "tm_decay_vy/F");
  tree_->Branch("tm_decay_vz", &tm_decay_vz_, "tm_decay_vz/F");
  tree_->Branch("tm_Lxyz", &tm_Lxyz_, "tm_Lxyz/F");

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

const reco::Candidate* GenStudies_eta::findDaughter(const reco::Candidate* mom, int pdgId) const {
  if (!mom) return nullptr;
  for (size_t i = 0; i < mom->numberOfDaughters(); ++i) {
    if (mom->daughter(i) && mom->daughter(i)->pdgId() == pdgId) return mom->daughter(i);
  }
  return nullptr;
}

void GenStudies_eta::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
  edm::Handle<std::vector<reco::GenParticle>> genParticles;
  iEvent.getByToken(genParticlesToken_, genParticles);

  for (const auto& p : *genParticles) {
    if (std::abs(p.pdgId()) != 221) continue;        // eta
    const reco::Candidate* tm = findDaughter(&p, 4900022);
    if (!tm) continue;
    const reco::Candidate* partner = findDaughter(&p, 22);   // photon
    if (!partner) continue;
    const reco::Candidate* ele1 = findDaughter(tm,  11);
    const reco::Candidate* ele2 = findDaughter(tm, -11);
    if (!ele1 || !ele2) continue;

    mom_pt_  = p.pt();  mom_eta_ = p.eta();  mom_phi_ = p.phi();  mom_mass_ = p.mass();
    mom_vx_  = p.vx();  mom_vy_  = p.vy();   mom_vz_  = p.vz();

    partner_pt_   = partner->pt();
    partner_eta_  = partner->eta();
    partner_phi_  = partner->phi();
    partner_mass_ = partner->mass();

    tm_pt_   = tm->pt();   tm_eta_  = tm->eta();   tm_phi_  = tm->phi();   tm_mass_ = tm->mass();
    tm_vx_   = tm->vx();   tm_vy_   = tm->vy();    tm_vz_   = tm->vz();
    tm_decay_vx_ = ele1->vx();
    tm_decay_vy_ = ele1->vy();
    tm_decay_vz_ = ele1->vz();
    float dx = tm_decay_vx_ - tm_vx_, dy = tm_decay_vy_ - tm_vy_, dz = tm_decay_vz_ - tm_vz_;
    tm_Lxyz_ = std::sqrt(dx*dx + dy*dy + dz*dz);

    ele1_pt_     = ele1->pt();
    ele1_eta_    = ele1->eta();
    ele1_phi_    = ele1->phi();
    ele1_charge_ = ele1->charge();
    ele2_pt_     = ele2->pt();
    ele2_eta_    = ele2->eta();
    ele2_phi_    = ele2->phi();
    ele2_charge_ = ele2->charge();
    ele_dR_      = reco::deltaR(*ele1, *ele2);

    tree_->Fill();
  }
}

void GenStudies_eta::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("genParticles", edm::InputTag("genParticles"));
  descriptions.add("genStudies_eta", desc);
}

DEFINE_FWK_MODULE(GenStudies_eta);
