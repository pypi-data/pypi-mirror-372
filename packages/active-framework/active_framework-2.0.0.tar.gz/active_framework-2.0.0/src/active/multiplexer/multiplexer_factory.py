class MultiplexerFactory():
    '''
    Singleton factory for creating Multiplexers
    '''
    
    # Class level registry from Multiplexer names to classes
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the Multiplexer with the given name, if it exists.
        
        Args:
            name String name of the Multiplexer, as defined by the ActiveMultiplexer("name") decorator.
        Returns:
            The Multiplexer class with the given name if it exists. NoneType if it does not.
        '''
        if name in MultiplexerFactory.registry:
            return MultiplexerFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered Multiplexers.
        
        Returns:
            A Set of Strings containing the name of every registered Multiplexer. 
        '''
        return MultiplexerFactory.registry.keys()
    
    @staticmethod
    def register(multiplexer_class, name):
        '''
        Register a Multiplexer subclass with the given name.
        
        Args:
            multiplexer_class A Class that inherits from Multiplexer.
            name The String name to register multiplexer_class as. 
        '''
        MultiplexerFactory.registry[name] = multiplexer_class


# Import our default Multiplexers after the class definition so that the factory will be finished importing by the time
# the Multiplexers try to automatically register themselves.

    