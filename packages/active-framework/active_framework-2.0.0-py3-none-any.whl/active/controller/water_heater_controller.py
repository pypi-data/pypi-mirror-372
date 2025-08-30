class WaterHeaterController():
    '''
    Controller for a water heater
    '''
        
    def get_available_capacity(self):
        '''
        Get the available capacaity
        
        Returns:
            The capacity as a float.
        '''
            
        return NotImplemented
    
    def get_override(self):
        '''
        Get the override.
        
        Return:
            The override as an int, 0 for no override or 1 for overriding
        '''
        
        return NotImplemented
    
    def get_power(self):
        '''
        Get the power
        
        Return:
            The power as a float
        '''
            
        return NotImplemented
    
    def get_state(self):
        '''
        Get the state
        
        Return:
            The state
        '''
        
        return NotImplemented
    
    def get_total_capacity(self):
        '''
        Get the total capacaity
        
        Returns:
            The capacity as a float.
        '''
            
        return NotImplemented
