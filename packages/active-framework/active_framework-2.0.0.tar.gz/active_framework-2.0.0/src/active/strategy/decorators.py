def ActiveStrategy(name):
    '''
    Decorator for a Strategy.
    
    Usage: 
    @ActiveStrategy("My Strategy Name")
    class MyStrategy()
    
    Args:
        name String specifying the unique name that the Strategy will be referenced by.
    '''
    
    def ActiveStrategyDecorator(strategy_class):
        
        # On import, register the new Strategy with the factory
        StrategyFactory.register(strategy_class, name)
    return ActiveStrategyDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.strategy.strategy_factory import StrategyFactory
