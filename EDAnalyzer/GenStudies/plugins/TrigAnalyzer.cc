#include <memory>
#include <vector>
#include <algorithm>
#include <iostream>
#include <limits>
#include <cmath>
#include <string>
#include <optional>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/Utilities/interface/EDMException.h"

#include <CommonTools/UtilAlgos/interface/TFileService.h>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "TTree.h"
class TrigAnalyzer : public edm::one::EDAnalyzer<>
{
public:
	explicit TrigAnalyzer(const edm::ParameterSet &);
	~TrigAnalyzer() override {};

	static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);

private:

	void beginJob() override;
	void analyze(const edm::Event &, const edm::EventSetup &) override;
	void endJob() override;

    edm::EDGetTokenT<reco::GenParticleCollection> GenPartToken_;
	edm::EDGetTokenT<edm::TriggerResults> triggerToken_;

    unsigned long nEventsProcessed_;
    unsigned long nEventsTriggered_;

	std::map<TString, int> triggerCounts_;
	std::map<TString, int> triggerTotal_;
};

TrigAnalyzer::TrigAnalyzer(const edm::ParameterSet &iConfig)
{
	edm::InputTag TriggerBitsTag_("TriggerResults", "", "HLT");
	triggerToken_ = consumes<edm::TriggerResults>(TriggerBitsTag_);
}

void TrigAnalyzer::beginJob()
{
	nEventsProcessed_ = 0;
}
void TrigAnalyzer::analyze(const edm::Event &iEvent, const edm::EventSetup &iSetup)
{
    nEventsProcessed_++;
	edm::Handle<edm::TriggerResults> triggerHandle;
	iEvent.getByToken(triggerToken_, triggerHandle);
    
    const edm::TriggerNames &names = iEvent.triggerNames(*triggerHandle);
	for (Size_t i = 0; i < names.size(); i++)
	{
		TString trigName = names.triggerName(i);
		if (!trigName.BeginsWith("HLT_"))
			continue;
		Bool_t pass = triggerHandle->accept(i);
		triggerTotal_[trigName]++;
		if (pass)
			triggerCounts_[trigName]++;
	}
}
void TrigAnalyzer::endJob()
{
	edm::LogPrint("TrigAnalyzer") << "\n========== Trigger Statistics ==========";
	edm::LogPrint("TrigAnalyzer") << std::setw(60) << "Trigger Name"
								  << std::setw(15) << "Fired"
								  << std::setw(15) << "Total"
								  << std::setw(15) << "Efficiency";
	edm::LogPrint("TrigAnalyzer") << std::string(105, '-');

	std::vector<std::pair<TString, double>> triggerEfficiencies;

	for (const auto &entry : triggerCounts_)
	{
		const TString trigName = entry.first;
		int fired = entry.second;
		int total = triggerTotal_[trigName];
		double efficiency = (total > 0) ? (double)fired / total * 100.0 : 0.0;

		triggerEfficiencies.push_back({trigName, efficiency});
	}

	std::sort(triggerEfficiencies.begin(), triggerEfficiencies.end(),
			  [](const auto &a, const auto &b)
			  { return a.second > b.second; });

	for (const auto &item : triggerEfficiencies)
	{
		const TString &trigName = item.first;
		int fired = triggerCounts_[trigName];
		int total = triggerTotal_[trigName];
		double efficiency = item.second;

		edm::LogPrint("TrigAnalyzer") << std::setw(80) << trigName
									  << std::setw(15) << fired
									  << std::setw(15) << total
									  << std::setw(14) << std::fixed << std::setprecision(2)
									  << efficiency << "%";
	}

	edm::LogPrint("TrigAnalyzer") << "========================================\n";
}
void TrigAnalyzer::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
	edm::ParameterSetDescription desc;
	desc.setUnknown();
	descriptions.addDefault(desc);
}

DEFINE_FWK_MODULE(TrigAnalyzer);
