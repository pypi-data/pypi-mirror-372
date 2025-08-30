class ClockController():
    '''
    Abstract base classfor Controllers for time sources.
    '''
    
    def get_time(self):
        '''
        Get the current time.
        
        Return:
            A datetime object for the current time.
        '''
        
        return NotImplemented