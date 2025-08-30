class AgentFactory():
    '''
    Singleton factory for creating Agents
    '''
    
    # Class level registry from Agent names to classes
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the Agent with the given name, if it exists.
        
        Args:
            name String name of the Agent, as defined by the ActiveAgent("name") decorator.
        Returns:
            The Agent class with the given name if it exists. NoneType if it does not.
        '''
        if name in AgentFactory.registry:
            return AgentFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered Strategies.
        
        Returns:
            A Set of Strings containing the name of every registered Agent. 
        '''
        return AgentFactory.registry.keys()
    
    @staticmethod
    def register(agent_class, name):
        '''
        Register a Agent subclass with the given name.
        
        Args:
            agent_class A Class that inherits from Agent.
            name The String name to register agent_class as. 
        '''
        AgentFactory.registry[name] = agent_class


# Import our default Agents after the class definition so that the factory will be finished importing by the time
# the Agents try to automatically register themselves.
import active.agent.energyplustapi_agent
import active.agent.intersect_agent
import active.agent.simple_agent
import active.agent.volttron_agent
    