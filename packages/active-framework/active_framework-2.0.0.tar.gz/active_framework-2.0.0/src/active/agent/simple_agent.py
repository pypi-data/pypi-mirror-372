import time
import traceback

from datetime import datetime, timedelta

from active.agent.agent import Agent
from active.agent.decorators import ActiveAgent

@ActiveAgent("simple")
class SimpleAgent(Agent):
    '''
    Agent for running a Strategy directly.
    
    ACTIVE configuration file parameters prototype:
    
    {
        "delay": 0,
        "num_episodes": 1
    }
    
    Params:
        num_episodes Integer for the number of times to run the Strategy. A negative number will cause the agent to
            run forever.
    '''
    
    def __init__(self, strategy, internal_active_parameters, delay=0, num_episodes=1):
        '''
        Default constructor
        
        Args:
            strategy: The Strategy to run.
            internal_active_parameters: Dictionary of parameters from the ACTIVE configuration file
            delay: Integer number of seconds to delay between steps
            num_episodes: Integer for the number of times to run the strategy
        '''
        
        super().__init__(strategy, internal_active_parameters)
        self.delay = delay
        self.num_episodes = num_episodes
        
    def start(self):
        '''
        Run Strategy for a number of steps equal to num_episodes, then stop
        '''
        
        # Get the time of the first run
        curr_runtime = datetime.now()
        
        # Time delta equal to the delay between runs
        time_delta = timedelta(seconds = self.delay)
        
        # If number of episodes is negative, loop forever
        if self.num_episodes < 0:
            
            while True:
                try:
                    self.strategy.step(final_episode=False)
                except Exception as e:
                    print(datetime.now())
                    print(e)
                    print(traceback.format_exc())
                
        # If number of episodes is non-negative, half after that many episodes
        else:
        
            for i in range(self.num_episodes):
                
                try:
                    if i == self.num_episodes - 1:
                        self.strategy.step(final_episode=True)
                    else:
                        self.strategy.step(final_episode=False)
                except Exception as e:
                    print(datetime.now())
                    print(e)
                    print(traceback.format_exc())
                    
                # Calculate the next scheduled run time
                curr_runtime = curr_runtime + time_delta
                
                # Wait one second at a time until reaching the scheduled time for the run
                while datetime.now() < curr_runtime:
                    time.sleep(1)
        
        