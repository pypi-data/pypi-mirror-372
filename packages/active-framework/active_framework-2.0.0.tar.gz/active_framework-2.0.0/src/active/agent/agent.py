class Agent():
    '''
    Base class for all ACTIVE agents.
    
    Params:
        internal_active_parameters: Dictionary of ACTIVE parameters from the configuration file.
        strategy: ACTIVE Strategy that this Agent is to execute.
    '''
    
    def __init__(self, strategy, internal_active_parameters):
        '''
        The default constructor.
        
        Args:
            strategy: ACTIVE Strategy to execute
            internal_active_parameters: Dictionary of values from the ACTIVE configuration file.
        '''
        
        self.internal_active_parameters = internal_active_parameters
        self.strategy = strategy
        
    def start(self):
        '''
        Begin the Agent's execution.
        '''        
        
        pass