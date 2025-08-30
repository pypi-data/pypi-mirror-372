from active.controller.delta_solar_inverter_controller_base import DeltaSolarInverterControllerBase
from active.controller.decorators import ActiveController

@ActiveController("Delta Solar Inverter")
class DeltaSolarInverterController(DeltaSolarInverterControllerBase):
    '''
    Controller for a solar inverter, communicated with over the Delta API.
    
    This ActiveController is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the controller to use static
    members, this empty subclass is necessary purely for the dynamic import.
    '''