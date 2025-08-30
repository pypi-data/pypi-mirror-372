from active.controller.bacnet_rtu_controller_base import BACnetRTUControllerBase
from active.controller.decorators import ActiveController

@ActiveController("BACNet RTU")
class BACnetRTUController(BACnetRTUControllerBase):
    '''
    Controller for an RTU device via BACnet protocol communication.
    
    This ActiveController is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the controller to use static
    members, this empty subclass is necessary purely for the dynamic import.
    '''