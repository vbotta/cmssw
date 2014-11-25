from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
import itertools
import ROOT
class VHbbAnalyzer( Analyzer ):
    '''Analyze VH events
    '''

    def declareHandles(self):
        super(VHbbAnalyzer, self).declareHandles()
#        self.handles['met'] =  AutoHandle( 'slimmedMETs', 'std::vector<pat::MET>' )

    def beginLoop(self):
        super(VHbbAnalyzer,self).beginLoop()
    
       
    def process(self, event):
        self.readCollections( event.input )
#	event.met = self.handles['met'].product()[0]
# 	met = event.met
	
	#assign events to analysis (Vtype)
	#enum CandidateType{Zmumu, Zee, Wmun, Wen, Znn,  Zemu, Ztaumu, Ztaue, Wtaun, Ztautau, Zbb, UNKNOWN};

	if len(event.cleanJets) < 2 :
		return False

	event.Vtype=-1
        nLep=len(event.selectedLeptons)	
	event.vLeptons=[]
	#WH requires exactly one selected lepton
	if nLep == 1: 
		if abs(event.selectedLeptons[0].pdgId())==13 :
			event.Vtype = 2
			event.vLeptons =event.selectedLeptons
		if abs(event.selectedLeptons[0].pdgId())==11 :
			event.Vtype = 3
			event.vLeptons =event.selectedLeptons
	#ZllH check first if a Zmumu can be made, otherwise Zee
	if nLep >= 2: #Z?
		if len(event.selectedMuons) ==  2 :
			if event.selectedMuons[0].charge()*event.selectedMuons[1].charge()<0 :
	                      event.Vtype = 0
			      event.vLeptons =event.selectedMuons
		elif len(event.selectedElectrons) ==  2 : 
			if event.selectedElectrons[0].charge()*event.selectedElectrons[1].charge()<0 :
	                      event.Vtype = 1
			      event.vLeptons =event.selectedElectrons
		else :
			event.Vtype = 123

	if nLep == 0:
		event.Vtype = 5	
		#apply MET cut
		if  event.met.pt() < 50 :
			 return False
	event.V=sum(map(lambda x:x.p4(), event.vLeptons),ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.))
	
	if event.Vtype > 1 :	
		event.V+=met.p4()

	event.aLeptons = [x for x in event.inclusiveLeptons if x not in event.vLeptons]

	#leading csv interpretation
	event.hJetsCSV=sorted(event.cleanJets,key = lambda jet : jet.btag('combinedSecondaryVertexBJetTags'), reverse=True)[0:2]
        event.aJetsCSV = [x for x in event.cleanJets if x not in event.hJetsCSV]
	event.hjidxCSV=[event.cleanJets.index(x) for x in event.hJetsCSV ]
	event.ajidxCSV=[event.cleanJets.index(x) for x in event.aJetsCSV ]
	event.aJetsCSV+=event.cleanJetsFwd

	#highest pair interpretations
	event.hJets=list(max(itertools.combinations(event.cleanJets,2), key = lambda x : (x[0].p4()+x[1].p4()).pt() ))
        event.aJets = [x for x in event.cleanJets if x not in event.hJets]
	event.hjidx=[event.cleanJets.index(x) for x in event.hJets ]
	event.ajidx=[event.cleanJets.index(x) for x in event.aJets ]
	event.aJets+=event.cleanJetsFwd
	
	event.HCSV = event.hJetsCSV[0].p4()+event.hJetsCSV[1].p4()
	event.H = event.hJets[0].p4()+event.hJets[1].p4()

        return True




