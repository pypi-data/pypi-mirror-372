from active.emulator.decorators import ActiveEmulator
from active.emulator.http_emulator_base import HTTPEmulatorBase
    
@ActiveEmulator("HTTP")
class HTTPEmulator(HTTPEmulatorBase):
    '''
    Emulator for an HTTP API
    
    This ActiveEmulator is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the emulator to use static
    members, this empty subclass is neccesary purely for the dynamic import.
    '''
