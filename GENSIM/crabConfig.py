from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.requestName = "MC_etaToTMGamma_2022_20260423"
config.General.transferLogs = True

config.section_("JobType")
config.JobType.psetName = "GENSIM_etaToTMGamma_cfg.py"
config.JobType.pluginName = "PrivateMC"

config.section_("Data")
config.Data.outputPrimaryDataset = "SIM"
config.Data.splitting="EventBased"
config.Data.unitsPerJob = 500
config.Data.totalUnits = 50000
config.Data.publication = False
config.Data.outputDatasetTag = "2022"
config.Data.outLFNDirBase = "/store/user/sduponch/PhD/TMToEE/etaToTMGamma/20260423/Simulation"

config.section_("User")
config.User.voGroup = "becms"

config.section_("Site")
config.Site.storageSite = "T2_BE_IIHE"
