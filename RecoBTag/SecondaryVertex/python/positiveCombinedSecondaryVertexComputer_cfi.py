import FWCore.ParameterSet.Config as cms

from RecoBTag.SecondaryVertex.combinedSecondaryVertexComputer_cfi import *

positiveCombinedSecondaryVertexComputer = combinedSecondaryVertexComputer.clone()
positiveCombinedSecondaryVertexComputer.trackSelection.sip3dSigMin = 0
positiveCombinedSecondaryVertexComputer.trackPseudoSelection.sip3dSigMin = 0
