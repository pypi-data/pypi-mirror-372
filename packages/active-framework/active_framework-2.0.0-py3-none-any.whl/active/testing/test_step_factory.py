class TestStepFactory():
    '''
    Singleton factory for creating TestSteps
    '''
    
    # Class level registry from TestStep names to functions
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the TestStep with the given name, if it exists.
        
        Args:
            name String name of the TestStep, as defined by the ActiveTestStep("name") decorator.
        Returns:
            The TestStep callable with the given name if it exists. NoneType if it does not.
        '''
        if name in TestStepFactory.registry:
            return TestStepFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered TestSteps.
        
        Returns:
            A Set of Strings containing the name of every registered TestStep. 
        '''
        return TestStepFactory.registry.keys()
    
    @staticmethod
    def register(callable, name):
        '''
        Register a TestStep callable with the given name.
        
        Args:
            callable The Callable TestStep to register
            name The String name to register callable as. 
        '''
        TestStepFactory.registry[name] = callable
        
# Import our default TestSteps after the class definition so that the factory will be finished importing by the time
# the TestSteps try to automatically register themselves.
import active.testing.clock_controller_value_check
import active.testing.rtu_controller_value_check
    