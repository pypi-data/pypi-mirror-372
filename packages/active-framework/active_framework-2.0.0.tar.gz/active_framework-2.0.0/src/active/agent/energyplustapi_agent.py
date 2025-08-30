from active.agent.agent import Agent
from active.agent.decorators import ActiveAgent

@ActiveAgent("EnergyPlus API")
class EnergyPlusAPIAgent(Agent):
    '''
    An Agent for running code inside an EnergyPlus simulation using the EnergyPlusAPI plugin through an EnergyPlusEmulator.
    
    Parameters:
        begin_system_timestep_before_predictor_handler: Callable from the Strategy to register with EnergyPlus for the
            begin_system_timestep_before_predictor
        emulator: An EnergyPlusAPIEmulator which is running an EnergyPlus simulation in which code will be injected
        episodes: Integer number of episodes to run. It is the Strategy's responsibility to determine which episodes, if any,
            will be trainnig episodes.
        inside_system_iteration_loop_handler: Callable from the Strategy to register with EnergyPlus for the 
            inside_system_iteration_loop_handler
        internal_active_parameters: Dictionary of values from the ACTIVE configuration file.
        strategy: ACTIVEStrategy to run
    '''
    
    def __init__(self, strategy, internal_active_parameters, begin_system_timestep_before_predictor_handler=None, 
                 emulator=None, episodes=1, inside_system_iteration_loop_handler=None):
        '''
        The default constructor.
        
        Args:
            strategy: ACTIVE Strategy to execute
            internal_active_parameters: Dictionary of values from the ACTIVE configuration file.
            begin_system_timestep_before_predictor_handler: String name of strategy function to register as a handler for the
                EnergyPlus begin_system_timestep_before_predictor
            emulator: EnergyPlusAPIEmulator to run the simulation
            episodes: Integer number of episodes to run
            inside_system_iteration_loop_handler: String name of strategy function to register as a handler for the 
                EnergyPlus inside_system_iteration_loop
        '''
        
        super().__init__(strategy, internal_active_parameters)
        
        # Initialize parameters
        self.emulator = emulator
        self.episodes = episodes
        
        # Grab Strategy functions by name as handlers
        if begin_system_timestep_before_predictor_handler:
            self.begin_system_timestep_before_predictor_handler = getattr(type(strategy), 
                                                                          begin_system_timestep_before_predictor_handler)
        else:
            self.begin_system_timestep_before_predictor_handler = None
            
        if inside_system_iteration_loop_handler:
            self.inside_system_iteration_loop_handler = getattr(type(strategy), inside_system_iteration_loop_handler)
        else:
            self.inside_system_iteration_loop_handler = None
        
    def start(self):
        '''
        Begin the Agent's execution.
        '''    
        
        # Register EnergyPlus handler functions 
        self._register_handlers()

        # Whether this is the final episode
        final_episode = False
        
        # Run Strategy to setup then launch EnergyPlus simulation once for each episode
        for i in range(self.episodes):
            
            # Check if this is the last episode
            if i == self.episodes - 1:
                final_episode = True
            
            # Have stragy perform all calculations
            self.strategy.step(final_episode=final_episode)
        
            # Launch the simulation
            self.emulator.launch()
            
            self._register_handlers()
            
            # Create any outputs
            self.strategy.output()
        
    def _register_handlers(self):
        '''
        Register all defined handlers from the Strategy to the EnergyPlus simulation.
        '''
        
        # Set the handlers
        if self.begin_system_timestep_before_predictor_handler:
            self.emulator.set_begin_system_timestep_before_predictor_handler(
                self.begin_system_timestep_before_predictor_handler)
        
        if self.inside_system_iteration_loop_handler:
            self.emulator.set_inside_system_iteration_loop_handler(
                self.inside_system_iteration_loop_handler)
        
        