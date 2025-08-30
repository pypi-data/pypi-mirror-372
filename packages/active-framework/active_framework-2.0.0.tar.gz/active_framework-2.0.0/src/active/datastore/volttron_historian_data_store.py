from active.datastore.decorators import ActiveDataStore
from active.datastore.volttron_historian_data_store_base import VOLTTRONHistorianDataStoreBase

@ActiveDataStore("VOLTTRON Historian")
class VOLTTRONHistorianDataStore(VOLTTRONHistorianDataStoreBase):
    '''
    A DataStore for saving data to a VOLTTRON historian agent.
    
    This class is only a wrapper with all business logic delegated to the base class per ACTIVE conventions.
    '''

    