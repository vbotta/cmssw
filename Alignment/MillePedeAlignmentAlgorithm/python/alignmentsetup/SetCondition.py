import FWCore.ParameterSet.Config as cms
from CondCore.DBCommon.CondDBSetup_cfi import *
import CalibTracker.Configuration.Common.PoolDBESSource_cfi

def setCondition(process, connect, record, tag, label = None):
    '''
    Overwrites a condition in startgeometry from globaltag.
    Creates a cms.ESPrefer object as a new attribute of process.
    The new attribute is called prefer_conditionsIn<record>
    '''
    
    if label != None:
        # create a new attribute of process that is named <record>condition (with label)
        setattr(process, record+'condition',
                CalibTracker.Configuration.Common.PoolDBESSource_cfi.poolDBESSource.clone(
                    connect = cms.string(connect),
                    toGet = cms.VPSet(
                        cms.PSet(
                            record = cms.string(record),
                            tag = cms.string(tag),
                            label = cms.untracked.string(label)
                        )
                    )
                ))
    else:
        # create a new attribute of process that is named <record>condition (without label)
        setattr(process, record+'condition',
                CalibTracker.Configuration.Common.PoolDBESSource_cfi.poolDBESSource.clone(
                    connect = cms.string(connect),
                    toGet = cms.VPSet(
                        cms.PSet(
                            record = cms.string(record),
                            tag = cms.string(tag),
                        )
                    )
                ))
    # create an ESPrefer statement as attribute of process
    # that is called prefer_conditionsIn<record>
    setattr(process, 'prefer_conditionsIn'+record, cms.ESPrefer("PoolDBESSource",record+'condition'))
