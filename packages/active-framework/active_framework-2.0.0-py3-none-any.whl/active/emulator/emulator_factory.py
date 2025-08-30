class EmulatorFactory():
    '''
    Singleton factory for creating Emulators
    '''
    
    # Class level registry from Emulator names to classes
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the Emulator with the given name, if it exists.
        
        Args:
            name String name of the Emulator, as defined by the ActiveEmulator("name") decorator.
        Returns:
            The Emulator class with the given name if it exists. NoneType if it does not.
        '''
        if name in EmulatorFactory.registry:
            return EmulatorFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered Strategies.
        
        Returns:
            A Set of Strings containing the name of every registered Emulator. 
        '''
        return EmulatorFactory.registry.keys()
    
    @staticmethod
    def register(emulator_class, name):
        '''
        Register a Emulator subclass with the given name.
        
        Args:
            emulator_class A Class that inherits from Emulator.
            name The String name to register emulator_class as. 
        '''
        EmulatorFactory.registry[name] = emulator_class


# Import our default Emulators after the class definition so that the factory will be finished importing by the time
# the Emulators try to automatically register themselves.
import active.emulator.bacnet_emulator
import active.emulator.energyplusapi_emulator
import active.emulator.http_emulator
import active.emulator.skycentrics_water_heater_emulator
import active.emulator.volttron_sqlite_historian_emulator
    