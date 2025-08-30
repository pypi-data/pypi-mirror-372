def ActiveEmulator(name):
    '''
    Decorator for an Emulator.
    
    Usage: 
    @ActiveEmulator("My Emulator Name")
    class MyEmulator()
    
    Args:
        name String specifying the unique name that the Emulator will be referenced by.
    '''
    
    def ActiveEmulatorDecorator(emulator_class):
        
        # On import, register the new Emulator with the factory
        EmulatorFactory.register(emulator_class, name)
    return ActiveEmulatorDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.emulator.emulator_factory import EmulatorFactory