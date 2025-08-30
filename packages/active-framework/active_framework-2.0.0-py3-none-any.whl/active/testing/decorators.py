def ActiveTestStep(name):
    '''
    Decorator for a TestStep
    
    Usage: 
    @ActiveTestStep("My Test Step Name")
    def my_test_step()
    
    Args:
        name String specifying the unique name that the TestStep will be referenced by.
    '''
    
    def ActiveTestStepDecorator(callable):
        
        # On import, register the new TestStep with the factory
        TestStepFactory.register(callable, name)
    return ActiveTestStepDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.testing.test_step_factory import TestStepFactory