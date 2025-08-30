import os

from  active.datastore.data_store import DataStore

class VOLTTRONHistorianDataStoreBase(DataStore):
    '''
    Data Store for saving data to a VOLTTRON historian agent.
    
    Params:
        timeout: Integer time to wait for pubsub before timing out.
        timestamp: Header with user set timestamp to be sent.
        vip: VOLTTRON Interconnect Protocol object for communications with VOLTTRON.
    '''
    
    def __init__(self, timeout=2):
        '''
        The default constructor
        
        Args:
            timeout: Integer time to wait for pubsub before timing out
        '''
        
        self.timeout = timeout
        self.timestamp = {}
        self.vip = None
        
    def copy(self, id, input):
        '''
        Send the data to the Historian under the given topic
        
        Args:
            id: The VOLTTRON topic to publish the message on
            input: The message to publish
        '''
        
        # If VIP isn't set, fail
        if not self._check_vip():
            return
        
        self.vip.pubsub.publish(peer='pubsub',
                                topic=id,
                                message=input,  # [data, {'source': 'publisher3'}],
                                headers=self.timestamp).get(timeout=self.timeout)
        
        
    def copy_file(self, id, input):
        '''
        Send the data in the file to the historian.
        
        Args:
            id: The VOLTTRON topic to publish the message on
            input: The file whose contents will be published.
        '''
        
        # If VIP isn't set, fail
        if not self._check_vip():
            return
        
        message = ""
        
        with open(input, 'r') as target:
            message = target.read()
        
        self.vip.pubsub.publish(peer='pubsub',
                                topic=id,
                                message=message,
                                headers=self.timestamp).get(timeout=self.timeout)  
        
    def load_to_file(self, id, name, path):
        '''
        Not implemented.
        '''
        
        raise NotImplementedError("")
        
    def save(self, id, input):
        '''
        Move the file to a folder named id under own path.
        
        Args:
            id: The name of the category to save the input.
            input: String path to the file to save.
        '''
        
        # If VIP isn't set, fail
        if not self._check_vip():
            return
        
        # Send the file to the historian
        self.copy(id, input)
        
        # Delete the file
        os.remove(input)
        
    def set_timestamp(self):
        '''
        Set the timestamp to save all data with equal to the current instant.
        '''
        
        # Importing here because VOLTTRON is not a dependency of ACTIVE.
        from volttron.platform.messaging.headers import TIMESTAMP
        from volttron.platform.agent.utils import (get_aware_utc_now,
                                           format_timestamp)
        
        # Set the timestamp to the present moment
        self.timestamp = {TIMESTAMP: format_timestamp(get_aware_utc_now())}
        
    def _check_vip(self):
        '''
        Check whether the VIP is set and print an error message if not.
        
        Returns
            True if the VIP is set. False if not.
        '''
        
        if self.vip != None:
            return True
        else:
            print("VOLTTRON Interconnect Protocol not set for VOLTTRON Historian Data Store. Communication with a " +
                  "VOLTTRON message bus this. It is normally provided via using this Data Store in a VOLTTRONAgent and " +
                  'adding it to the "set vip" parameter in the environment configuration file.')
            return False
        