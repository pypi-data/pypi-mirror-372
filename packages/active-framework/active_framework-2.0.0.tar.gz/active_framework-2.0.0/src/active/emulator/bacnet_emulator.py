from active.emulator.bacnet_emulator_base import BACnetEmulatorBase
from active.emulator.decorators import ActiveEmulator

@ActiveEmulator("BACnet Emulator")
class BACnetEmulator(BACnetEmulatorBase):
    '''
    Emulator for a BACnet device.
    
    This ActiveEmulator is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the emulator to use static
    members, this empty subclass is neccesary purely for the dynamic import.
    '''
