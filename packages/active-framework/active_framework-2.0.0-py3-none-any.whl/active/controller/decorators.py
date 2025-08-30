def ActiveController(name):
    '''
    Decorator for a Controller.
    
    Usage: 
    @ActiveController("My Controller Name")
    class MyController()
    
    Args:
        name String specifying the unique name that the Controller will be referenced by.
    '''
    
    def ActiveControllerDecorator(controller_class):
        
        # On import, register the new Controller with the factory
        ControllerFactory.register(controller_class, name)
    return ActiveControllerDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.controller.controller_factory import ControllerFactory