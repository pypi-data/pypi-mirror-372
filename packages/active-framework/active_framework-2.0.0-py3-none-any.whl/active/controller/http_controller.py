from active.controller.decorators import ActiveController
from active.controller.http_controller_base import HTTPControllerBase

@ActiveController("HTTP")
class HTTPController(HTTPControllerBase):
    '''
    Controller for communication with an HTTP based API.
    
    This ActiveController is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the controller to use static
    members, this empty subclass is neccessary purely for the dynamic import.
    '''
