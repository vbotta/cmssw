from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle


class VHbbAnalyzer( Analyzer ):
    '''Analyze VH events
    '''

    def declareHandles(self):
        super(VHbbAnalyzer, self).declareHandles()
#       self.handles['met'] =  AutoHandle( self.cfg_ana.metCol, self.cfg_ana.metType )


    def beginLoop(self):
        super(VHbbAnalyzer,self).beginLoop()
    
    def selectHiggsJetPair(self,event) :
        #silly jet assigment, just for test
        return event.cleanJets[0:2]


       
    def process(self, event):
        self.readCollections( event.input )
 #      event.met = self.handles['met'].product()[0]
 #      met = event.met
	
	#assign events to analysis (Vtype)
	#enum CandidateType{Zmumu, Zee, Wmun, Wen, Znn,  Zemu, Ztaumu, Ztaue, Wtaun, Ztautau, Zbb, UNKNOWN};

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
		pass

	event.aLeptons = [x for x in event.inclusiveLeptons if x not in event.vLeptons]

	#silly jet assigment, just for test
	event.hJets=self.selectHiggsJetPair(event)
	event.aJets=event.cleanJets[2:]+event.cleanJetsFwd


        return True




