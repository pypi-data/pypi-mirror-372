from active.controller.cr1000x_rtu_controller_base import CR1000XRTUControllerBase
from active.controller.decorators import ActiveController

@ActiveController("CR1000X RTU")
class CR1000XRTUController(CR1000XRTUControllerBase):
    '''
    An RTU which is communicated with over HTTP through a CR1000X data logger.
    
    This ActiveController is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the controller to use static
    members, this empty subclass is necessary purely for the dynamic import.
    '''