from active.controller.clock_controller import ClockController
from active.controller.decorators import ActiveController

@ActiveController("EnergyPlus API Clock")
class EnergyPlusAPIClockController(ClockController):
    '''
    ClockController which gets the timestamp from an EnergyPlus simulation.
    
    Parameters:
        emulator: EnergyPlusAPIEmulator for the simulation to get the timestamp from.
    '''
    
    def __init__(self, emulator=None):
        '''
        The default constructor.
        
        Args:
            emulator: EnergyPlusAPIEmulator to get the timestamp from.
        '''
        
        self.emulator = emulator
        
    def get_time(self):
        '''
        Get the timestamp from the emulator.
        
        Returns:
            datetime object representing the current time within the simulation.
        '''
        
        return self.emulator.timestamp()