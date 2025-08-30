class StrategyFactory():
    '''
    Singleton factory for creating Strategies.
    '''
    
    # Class level registry from Stragey names to classes
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the Strategy with the given name, if it exists.
        
        Args:
            name String name of the Strategy, as defined by the ActiveStrategy("name") decorator.
        Returns:
            The Strategy class with the given name if it exists. NoneType if it does not.
        '''
        if name in StrategyFactory.registry:
            return StrategyFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered Strategies.
        
        Returns:
            A Set of Strings containing the name of every registered Strategy. 
        '''
        
        return StrategyFactory.registry.keys()
    
    @staticmethod
    def register(strategy_class, name):
        '''
        Register a Strategy subclass with the given name.
        
        Args:
            strategy_class A Class that inherits from Strategy.
            name The String name to register strategy_class as. 
        '''
        StrategyFactory.registry[name] = strategy_class
        
    