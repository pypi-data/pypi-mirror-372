import json

from active.controller.skycentrics_controller_base import SkycentricsControllerBase
from active.controller.water_heater_controller import WaterHeaterController

class SkycentricsWaterHeaterControllerBase(SkycentricsControllerBase, WaterHeaterController):
    '''
    Business logic for controlling a Skycentrics water heater.
    
    ACTIVE environment file prototype:
    
    {
        "client_id": "abcdefg", 
        "client_secret": "hijklm", 
        "device_mac": "0a0a0a0a0a", 
        "password": "password1", 
        "url": "https://api.skycentrics.com", 
        "username": "myname@company.com"
    }
    
    Parameters:
        client_id: String Skycentrics client id
        client_secret: String Skycentrics client secret
        device_mac: String name for this device in Skycentrics
        url: URL for the Skycentrics API
    '''
    
    def __init__(self, client_id="", client_secret="", device_mac="", password="", url="https://api.skycentrics.com", username=""):
        '''
        Default constructor
        
        Args:
            client_id: String Skycentrics client id
            client_secret: String Skycentrics client secret
            device_mac: String name for this device in Skycentrics
            password: String password for the Skycentrics account
            url: URL for the Skycentrics API
            username: String username for the Skycentrics account
        '''
        super().__init__(client_id=client_id, client_secret=client_secret, device_mac=device_mac, password=password, url=url, username=username)
        
    def get_available_capacity(self):
        '''
        Get the available capacaity
        
        Returns:
            The capacity as a float.
        '''
        
        commodities = self._get_with_cache('commodities')
        
        for commodity in commodities:
            if commodity['code'] == 7:
                return commodity['cumulative']
            
        return None
    
    def get_override(self):
        '''
        Get the override.
        
        Return:
            The override as an int, 0 for no override or 1 for overriding
        '''
        
        return self._get_with_cache('override')
    
    def get_power(self):
        '''
        Get the power
        
        Return:
            The power as a float
        '''
        
        commodities = self._get_with_cache('commodities')
        
        for commodity in commodities:
            if commodity['code'] == 0:
                return commodity['instantaneous']
            
        return None
    
    def get_state(self):
        '''
        Get the state
        
        Return:
            The state
        '''
        return self._get_with_cache('state')
    
    def get_total_capacity(self):
        '''
        Get the total capacaity
        
        Returns:
            The capacity as a float.
        '''
        
        commodities = self._get_with_cache('commodities')
        
        for commodity in commodities:
            if commodity['code'] == 6:
                return commodity['cumulative']
            
        return None
    
    def set_state(self, value, duration):
        '''
        Set the new state.
        
        Args:
            value The new state as a String. Should be one of "load", "shed", or "normal"
            duration Integer number of seconds for the new state to last
        '''
        
        if value == "load":
            self.set_device_parameter("event", json.dumps({"event": "LU", "duration": duration}))
        elif value == "normal":
            self.set_device_parameter("load_shed", json.dumps({"s": 0, "duration": 0}))
        elif value == "shed":
            self.set_device_parameter("load_shed", json.dumps({"s": 1, "duration": duration}))
    
    def _get_with_cache(self, key):
        '''
        Get the requested device data key's data from the cache if it exists and if not by querying the API.
        
        Args:
            key: The string key whose data is to be loaded
        '''
        
        if self._cache is not None:
            return self._cache[key]
        
        return self.get_device_data()[key]
