//Based on: PhysicsTools/PatAlgos/plugins/PATLostTracks.cc

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidate.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/Common/interface/Association.h"

#include <vector>

//
// class declaration
//

class PATTracksToPackedCandidates : public edm::stream::EDProducer<> {
public:
  explicit PATTracksToPackedCandidates(const edm::ParameterSet&);

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

  void addPackedCandidate(std::vector<pat::PackedCandidate>& cands,
                          const reco::Track trk,
                          const reco::VertexRef& pvSlimmed,
                          const reco::VertexRefProd& pvSlimmedColl,
                          bool passPixelTrackSel) const;

private:
  void produce(edm::Event&, const edm::EventSetup&) override;

  // ----------member data ---------------------------
  const edm::EDGetTokenT<reco::TrackCollection> srcTracks_;
  const edm::EDGetTokenT<reco::VertexCollection> srcPrimaryVertices_;
  const double dzSigCut_;
  const double dxySigCut_;
  const double dzSigHP_;
  const double dxySigHP_;
  const double ptMax_;
  const double ptMin_;
  const bool resetHP_;
  const int covarianceVersion_;
  const int covarianceSchema_;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
PATTracksToPackedCandidates::PATTracksToPackedCandidates(const edm::ParameterSet& iConfig)
    : srcTracks_(consumes<reco::TrackCollection>(iConfig.getParameter<edm::InputTag>("srcTracks"))),
      srcPrimaryVertices_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("srcPrimaryVertices"))),
      dzSigCut_(iConfig.getParameter<double>("dzSigCut")),
      dxySigCut_(iConfig.getParameter<double>("dxySigCut")),
      dzSigHP_(iConfig.getParameter<double>("dzSigHP")),
      dxySigHP_(iConfig.getParameter<double>("dxySigHP")),
      ptMax_(iConfig.getParameter<double>("ptMax")),
      ptMin_(iConfig.getParameter<double>("ptMin")),
      resetHP_(iConfig.getParameter<bool>("resetHP")),
      covarianceVersion_(iConfig.getParameter<int>("covarianceVersion")),
      covarianceSchema_(iConfig.getParameter<int>("covarianceSchema")) {
  produces<std::vector<pat::PackedCandidate>>();
  produces<edm::Association<pat::PackedCandidateCollection>>();
}

//
// member functions
//

// ------------ method called to produce the data  ------------
void PATTracksToPackedCandidates::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;

  //track collection
  auto tracks = iEvent.getHandle(srcTracks_);

  auto outPtrTrksAsCands = std::make_unique<std::vector<pat::PackedCandidate>>();

  //vtx collection
  edm::Handle<reco::VertexCollection> pvs;
  iEvent.getByToken(srcPrimaryVertices_, pvs);
  reco::VertexRef pv(pvs.id());
  reco::VertexRefProd pvRefProd(pvs);
  if (!pvs->empty()) {
    pv = reco::VertexRef(pvs, 0);
  }

  //best vertex
  double bestvzError = -999.9, bestvxError = -999.9, bestvyError = -999.9;
  const reco::Vertex& vtx = (*pvs)[0];
  bestvzError = vtx.zError();
  bestvxError = vtx.xError();
  bestvyError = vtx.yError();
  const math::XYZPoint& bestvtx(vtx.position());
  math::Error<3>::type vtx_cov = vtx.covariance();

  std::vector<int> mapping(tracks->size(), -1);
  int savedCandIndx = 0;
  int trkIndx = -1;
  for (auto const& trk : *tracks) {
    trkIndx++;
    double dzvtx = std::abs(trk.dz(bestvtx));
    double dxyvtx = std::abs(trk.dxy(bestvtx));
    double dzerror = std::hypot(trk.dzError(), bestvzError);
    double dxyerror = sqrt(trk.dxyError(bestvtx, vtx_cov) * trk.dxyError(bestvtx, vtx_cov) + bestvxError * bestvyError);

    if (dzvtx >= dzSigCut_ * dzerror)
      continue;
    if (dxyvtx >= dxySigCut_ * dxyerror)
      continue;
    if (trk.pt() >= ptMax_ || trk.pt() <= ptMin_)
      continue;

    bool passSelection = false;
    if (dzvtx < dzSigHP_ * dzerror && dxyvtx < dxySigHP_ * dxyerror)
      passSelection = true;

    addPackedCandidate(*outPtrTrksAsCands, trk, pv, pvRefProd, passSelection);

    //for creating the reco::Track -> pat::PackedCandidate map
    mapping[trkIndx] = savedCandIndx;
    savedCandIndx++;
  }
  edm::OrphanHandle<pat::PackedCandidateCollection> oh = iEvent.put(std::move(outPtrTrksAsCands));
  auto tk2pc = std::make_unique<edm::Association<pat::PackedCandidateCollection>>(oh);
  edm::Association<pat::PackedCandidateCollection>::Filler tk2pcFiller(*tk2pc);
  tk2pcFiller.insert(tracks, mapping.begin(), mapping.end());
  tk2pcFiller.fill();
  iEvent.put(std::move(tk2pc));
}

void PATTracksToPackedCandidates::addPackedCandidate(std::vector<pat::PackedCandidate>& cands,
                                                     const reco::Track trk,
                                                     const reco::VertexRef& pvSlimmed,
                                                     const reco::VertexRefProd& pvSlimmedColl,
                                                     bool passPixelTrackSel) const {
  const float mass = 0.13957018;

  int id = 211 * trk.charge();

  reco::Candidate::PolarLorentzVector p4(trk.pt(), trk.eta(), trk.phi(), mass);
  cands.emplace_back(
      pat::PackedCandidate(p4, trk.vertex(), trk.pt(), trk.eta(), trk.phi(), id, pvSlimmedColl, pvSlimmed.key()));

  if (resetHP_) {
    if (passPixelTrackSel)
      cands.back().setTrackHighPurity(true);
    else
      cands.back().setTrackHighPurity(false);
  } else {
    if (trk.quality(reco::TrackBase::highPurity))
      cands.back().setTrackHighPurity(true);
    else
      cands.back().setTrackHighPurity(false);
  }

  cands.back().setTrackProperties(trk, covarianceSchema_, covarianceVersion_);
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void PATTracksToPackedCandidates::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("srcTracks", {"hiConformalPixelTracks"});
  desc.add<edm::InputTag>("srcPrimaryVertices", {"offlineSlimmedPrimaryVertices"});
  desc.add<double>("dzSigCut", 10.0);
  desc.add<double>("dxySigCut", 25.0);
  desc.add<double>("dzSigHP", 7.0);
  desc.add<double>("dxySigHP", 20.0);
  desc.add<double>("ptMax", 1.0);
  desc.add<double>("ptMin", 0.3);
  desc.add<bool>("resetHP", true);
  desc.add<int>("covarianceVersion", 0);
  desc.add<int>("covarianceSchema", 520);
  descriptions.addWithDefaultLabel(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PATTracksToPackedCandidates);
