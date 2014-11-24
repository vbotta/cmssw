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

       
    def process(self, event):
        self.readCollections( event.input )
 #      event.met = self.handles['met'].product()[0]
 #      met = event.met
	
	#assign events to analysis (VType)
	event.VType=-1
        nLep=len(event.selectedLeptons)	
	if nLep == 1: 
		if abs(event.selectedLeptons[0].pdgId())==13 :
			event.Vtype = 2
		if abs(event.selectedLeptons[0].pdgId())==11 :
			event.Vtype = 3
	if nLep == 2: #Z?
		#check SF OS
		if event.selectedLeptons[0].charge()*event.selectedLeptons[1].charge()<0 and
		   abs(event.selectedLeptons[0].pdgId()) == abs(event.selectedLeptons[1].pdgId()) :
			if abs(event.selectedLeptons[0].pdgId()) == 13:
	                      event.Vtype = 0
			if abs(event.selectedLeptons[0].pdgId()) == 11:
	                      event.Vtype = 1
			event.Vtype = 123 #?? SS or OF

	if nLep == 0:
		event.Vtype = 5	
		#apply MET cut
		pass

        print nLep

        return True




