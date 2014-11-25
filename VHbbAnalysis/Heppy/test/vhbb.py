#! /usr/bin/env python
import ROOT
from DataFormats.FWLite import *
import PhysicsTools.HeppyCore.framework.config as cfg
from VHbbAnalysis.Heppy.vhbbobj import *

from PhysicsTools.Heppy.analyzers.core.AutoFillTreeProducer  import * 
treeProducer= cfg.Analyzer(
	class_object=AutoFillTreeProducer, 
	verbose=False, 
	vectorTree = True,
        globalVariables	= {
		 NTupleVariable("Vtype", lambda ev : ev.Vtype, help="Event classification")
	},
	collections = {
		#standard dumping of objects
   	        "vLeptons" : NTupleCollection("vleptons", leptonTypeVHbb, 8, help="Leptons after the preselection"),
   	        "aLeptons" : NTupleCollection("aLeptons", leptonTypeVHbb, 8, help="Additional leptons, not passing the preselection"),
	        "hJets"       : NTupleCollection("hJets",     jetTypeVHbb, 8, sortDescendingBy = lambda jet : jet.btag('combinedSecondaryVertexBJetTags'),help="Higgs jets"),
	        "aJets"       : NTupleCollection("aJets",     jetTypeVHbb, 8, sortDescendingBy = lambda jet : jet.btag('combinedSecondaryVertexBJetTags'),help="Additional jets"),
# uncomment the following to use indices instead of old-style hJets+aJets
                "hjidx"       : NTupleCollection("hJidx",    objectInt, 2,help="Higgs jet indices"),
#        "ajidx"       : NTupleCollection("aJidx",    objectInt, 2,help="additional jet indices"),
#        "hjidxCSV"       : NTupleCollection("hJCidx",    objectInt, 2,help="Higgs jet indices CSV"),
#        "ajidxCSV"       : NTupleCollection("aJCidx",    objectInt, 2,help="additional jet indices CSV"),
#        "cleanJets"       : NTupleCollection("Jet",     jetTypeVHbb, 8, help="Cental jets after full selection and cleaning, sorted by b-tag"),

                "selectedTaus"    : NTupleCollection("TauGood", tauType, 3, help="Taus after the preselection"),
		#dump of gen objects
                "gentopquarks"    : NTupleCollection("GenTop",     genParticleType, 2, help="Generated top quarks from hard scattering"),
                "genbquarksFromH"      : NTupleCollection("GenBQuarkFromH",  genParticleType, 2, help="Generated bottom quarks from top quark decays"),
                "genwzquarks"     : NTupleCollection("GenWZQuark",   genParticleWithSourceType, 6, help="Generated quarks from W/Z decays"),
                "genleps"         : NTupleCollection("GenLep",     genParticleWithSourceType, 6, help="Generated leptons from W/Z decays"),
                "gentauleps"      : NTupleCollection("GenLepFromTau", genParticleWithSourceType, 6, help="Generated leptons from decays of taus from W/Z/h decays"),

	}
	)

# Lepton Analyzer, take its default config
from PhysicsTools.Heppy.analyzers.objects.LeptonAnalyzer import LeptonAnalyzer
LepAna = LeptonAnalyzer.defaultConfig
#replace one parameter
LepAna.loose_muon_pt = 10

from PhysicsTools.Heppy.analyzers.objects.VertexAnalyzer import VertexAnalyzer
VertexAna = VertexAnalyzer.defaultConfig

from PhysicsTools.Heppy.analyzers.objects.PhotonAnalyzer import PhotonAnalyzer
PhoAna = PhotonAnalyzer.defaultConfig

from PhysicsTools.Heppy.analyzers.objects.TauAnalyzer import TauAnalyzer
TauAna = TauAnalyzer.defaultConfig

from PhysicsTools.Heppy.analyzers.objects.JetAnalyzer import JetAnalyzer
JetAna = JetAnalyzer.defaultConfig

from PhysicsTools.Heppy.analyzers.objects.GeneratorAnalyzer import GeneratorAnalyzer
GenAna = GeneratorAnalyzer.defaultConfig

from VHbbAnalysis.Heppy.VHbbAnalyzer import VHbbAnalyzer
VHbb= cfg.Analyzer(
    verbose=False,
    class_object=VHbbAnalyzer,
    )


sequence = [GenAna,VertexAna,LepAna,TauAna,PhoAna,JetAna,VHbb,treeProducer]


from PhysicsTools.Heppy.utils.miniAodFiles import miniAodFiles
sample = cfg.Component(
    files = ["root://xrootd.ba.infn.it//store/mc/Spring14miniaod/ZH_HToBB_ZToLL_M-125_13TeV_powheg-herwigpp/MINIAODSIM/141029_PU40bx50_PLS170_V6AN2-v1/00000/226BB247-A565-E411-91CF-00266CFF0AF4.root"],
    name="ATEST", isMC=True,isEmbed=False
    )
sample.isMC=True

# the following is declared in case this cfg is used in input to the heppy.py script
selectedComponents = [sample]
from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config( components = selectedComponents,
                     sequence = sequence, 
                     events_class = Events)

# and the following runs the process directly 
if __name__ == '__main__':
    from PhysicsTools.HeppyCore.framework.looper import Looper 
    looper = Looper( 'Loop', sample, sequence, Events, nPrint = 5, nEvents = 300)
    looper.loop()
    looper.write()
