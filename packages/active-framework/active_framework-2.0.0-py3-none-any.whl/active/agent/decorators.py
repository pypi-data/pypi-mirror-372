def ActiveAgent(name):
    '''
    Decorator for a Agent.
    
    Usage: 
    @ActiveAgent("My Agent Name")
    class MyAgent()
    
    Args:
        name String specifying the unique name that the Agent will be referenced by.
    '''
    
    def ActiveAgentDecorator(agent_class):
        
        # On import, register the new Agent with the factory
        AgentFactory.register(agent_class, name)
    return ActiveAgentDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.agent.agent_factory import AgentFactory