import datetime

from active.controller.clock_controller import ClockController
from active.controller.decorators import ActiveController

@ActiveController("System Clock")
class SystemClockController(ClockController):
    '''
    ClockController for getting time from the system clock.
    '''
    
    def __init__(self):
        '''
        The default constructor.
        '''
        
        pass
        
    def get_time(self):
        '''
        Get the current time.
        
        Return:
            A datetime object for the current time.
        '''
        
        return datetime.datetime.now()