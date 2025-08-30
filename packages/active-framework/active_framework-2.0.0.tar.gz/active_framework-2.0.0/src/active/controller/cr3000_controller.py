from active.controller.cr3000_controller_base import CR3000ControllerBase
from active.controller.decorators import ActiveController

@ActiveController("CR3000")
class CR3000Controller(CR3000ControllerBase):
    '''
    Controller for an CR3000 data logger, communicated with over HTTP.
    
    This ActiveController is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the controller to use static
    members, this empty subclass is necessary purely for the dynamic import.
    '''