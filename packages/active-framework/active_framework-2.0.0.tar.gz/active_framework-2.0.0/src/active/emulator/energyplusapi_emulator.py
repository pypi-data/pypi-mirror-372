from active.emulator.energyplusapi_emulator_base import EnergyPlusAPIEmulatorBase

from active.emulator.decorators import ActiveEmulator

@ActiveEmulator("EnergyPlus API")
class EnergyPlusAPIEmulator(EnergyPlusAPIEmulatorBase):
    '''
    An Emulator for running an EnergyPlus simulation and communicating with it through the EnergyPlusAPI.
    
    All business logic is delegated to EnergyPlusAPIEmulatorBase to avoid dynamic loading of class variables that are used
    inside the C++ bindings for EnergyPlus.
    '''