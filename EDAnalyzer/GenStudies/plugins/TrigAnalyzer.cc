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
#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"

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

	// Prescale lookup. MC events carry no real prescale (the HLT logic
	// itself is evaluated unprescaled); the actual prescale is a real-data
	// -taking-period configuration choice, read here from the HLT menu's
	// own embedded prescale table (HLTConfigProvider), not from the event.
	// Which of the menu's several prescale columns ("sets") corresponds to
	// real conditions of interest (e.g. a specific 2022 era) is an external
	// question (brilcalc / confDB), not something derivable from the menu
	// alone -- prescaleSet_ selects which column to read, defaulting to 0.
	HLTConfigProvider hltConfig_;
	unsigned int prescaleSet_;
	bool hltConfigValid_;
};

TrigAnalyzer::TrigAnalyzer(const edm::ParameterSet &iConfig)
	: prescaleSet_(iConfig.getUntrackedParameter<unsigned int>("prescaleSet", 0)),
	  hltConfigValid_(false)
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

	if (!hltConfig_.inited()) {
		bool changed = true;
		hltConfigValid_ = hltConfig_.init(iEvent.getRun(), iSetup, "HLT", changed);
		if (hltConfigValid_) {
			edm::LogPrint("TrigAnalyzer") << "\nHLT menu table: " << hltConfig_.tableName();
			edm::LogPrint("TrigAnalyzer") << "Available prescale sets (" << hltConfig_.prescaleSize()
				<< " total), using set " << prescaleSet_ << ":";
			const auto &labels = hltConfig_.prescaleLabels();
			for (size_t i = 0; i < labels.size(); i++)
				edm::LogPrint("TrigAnalyzer") << "  [" << i << "] " << labels[i];
		} else {
			edm::LogPrint("TrigAnalyzer") << "\nWARNING: HLTConfigProvider::init failed -- "
				"prescale/predicted columns will be unavailable.";
		}
	}

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
								  << std::setw(15) << "Efficiency"
								  << std::setw(15) << "Prescale"
								  << std::setw(15) << "Predicted";
	edm::LogPrint("TrigAnalyzer") << std::string(135, '-');

	struct Row { TString name; int fired; int total; double efficiency; double prescale; double predicted; bool havePrescale; };
	std::vector<Row> rows;

	for (const auto &entry : triggerCounts_)
	{
		const TString trigName = entry.first;
		int fired = entry.second;
		int total = triggerTotal_[trigName];
		double efficiency = (total > 0) ? (double)fired / total * 100.0 : 0.0;

		double prescale = -1.0;
		double predicted = 0.0;
		bool havePrescale = false;
		if (hltConfigValid_ && prescaleSet_ < hltConfig_.prescaleSize()) {
			// prescaleValue throws if trigName is unknown to the menu (shouldn't
			// happen here, since trigName came from this same event's menu).
			prescale = hltConfig_.prescaleValue<double>(prescaleSet_, trigName.Data());
			havePrescale = true;
			// prescale == 0 means the path is fully masked off in this set --
			// nothing gets recorded no matter how often the logic fires.
			predicted = (prescale > 0) ? fired / prescale : 0.0;
		}

		rows.push_back({trigName, fired, total, efficiency, prescale, predicted, havePrescale});
	}

	// Rank by predicted (realistic) yield, not raw MC efficiency -- a path
	// that fires often but is heavily prescaled records fewer real events
	// than a less-efficient but lightly-prescaled one.
	std::sort(rows.begin(), rows.end(),
			  [](const Row &a, const Row &b) { return a.predicted > b.predicted; });

	for (const auto &r : rows)
	{
		edm::LogPrint("TrigAnalyzer") << std::setw(80) << r.name
									  << std::setw(15) << r.fired
									  << std::setw(15) << r.total
									  << std::setw(14) << std::fixed << std::setprecision(2)
									  << r.efficiency << "%"
									  << std::setw(15) << (r.havePrescale ? std::to_string((long long)r.prescale) : std::string("n/a"))
									  << std::setw(15) << std::fixed << std::setprecision(2) << r.predicted;
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
