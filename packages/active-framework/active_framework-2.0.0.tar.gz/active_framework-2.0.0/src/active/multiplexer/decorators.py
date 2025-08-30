def ActiveMultiplexer(name):
    '''
    Decorator for a Multiplexer.
    
    Usage: 
    @ActiveMultiplexer("My Multiplexer Name")
    class MyMultiplexer()
    
    Args:
        name String specifying the unique name that the Multiplexer will be referenced by.
    '''
    
    def ActiveMultiplexerDecorator(multiplexer_class):
        
        # On import, register the new Multiplexer with the factory
        MultiplexerFactory.register(multiplexer_class, name)
    return ActiveMultiplexerDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.multiplexer.multiplexer_factory import MultiplexerFactory