class ControllerFactory():
    '''
    Singleton factory for creating Controllers
    '''
    
    # Class level registry from Controller names to classes
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the Controller with the given name, if it exists.
        
        Args:
            name String name of the Controller, as defined by the ActiveController("name") decorator.
        Returns:
            The Controller class with the given name if it exists. NoneType if it does not.
        '''
        if name in ControllerFactory.registry:
            return ControllerFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered Controllers.
        
        Returns:
            A Set of Strings containing the name of every registered Controller. 
        '''
        return ControllerFactory.registry.keys()
    
    @staticmethod
    def register(controller_class, name):
        '''
        Register a Controller subclass with the given name.
        
        Args:
            controller_class A Class that inherits from Controller.
            name The String name to register controller_class as. 
        '''
        ControllerFactory.registry[name] = controller_class


# Import our default Controllers after the class definition so that the factory will be finished importing by the time
# the Controllers try to automatically register themselves.
import active.controller.bacnet_controller
import active.controller.bacnet_rtu_controller
import active.controller.cr1000x_rtu_controller
import active.controller.cr3000_controller
import active.controller.delta_solar_inverter_controller
import active.controller.energyplus_controller
import active.controller.energyplusapi_clock_controller
import active.controller.energyplusapi_rtu_controller
import active.controller.http_controller
import active.controller.intersect_controller
import active.controller.system_clock_controller
import active.controller.skycentrics_controller
import active.controller.skycentrics_water_heater_controller
    