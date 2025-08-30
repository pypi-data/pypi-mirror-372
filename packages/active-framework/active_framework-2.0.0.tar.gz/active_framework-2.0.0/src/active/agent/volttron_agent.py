import json
import os
import pkgutil

from pathlib import Path
from subprocess import Popen, PIPE

from active.agent.agent import Agent
from active.agent.decorators import ActiveAgent

@ActiveAgent("volttron")
class VolttronAgent(Agent):
    '''
    An Agent for running inside a VOLTTRON agent. Depending on the current environment, either installs and runs the
    ACTIVEBootstrapAgent in VOLTTRON to invoke the strategy, or functions as a no-op when run in VOLTTRON.
    '''
    
    def __init__(self, strategy, internal_active_parameters, set_vip, schedule):
        '''
        Default constructor. 
        
        ACTIVE configuration file prototype:
        
        {
            "schedule": {
                "function1": 10,
                "function2": 60,
                ...
            }
        }
        
        Args:
            strategy: Strategy to be run.
            internal_active_parameters: parameters from the ACTIVE configuration file.
            set_vip: List of Strategy attributes to set the VOLTTRON .vip attribute.
            schedule: Dictionary of strings to integers. Keys are function names. Values are the number of seconds between
                executions of that function by VOLTTRON.
        '''
        
        super().__init__(strategy, internal_active_parameters)
        
    def start(self):
        '''
        Runs the Strategy.
        '''
        
        # If running in VOLTTRON, the ACTIVE Bootstrap Agent will run schedule the function executions after initialization.
        # No further work is required on the part of the Agent
        if self.internal_active_parameters["environment"] == "Volttron":
            pass
            
        else:
            
            # TODO parse for installed agent version and upgrade if neccesary
            # List all currently installed agents.
            list_process = Popen(["volttron-ctl", "list"], stdout=PIPE)
            volttron_agents = list_process.communicate()
            
            # Check for a message about not being able to find volttron-ctl
            if "volttron-ctl" in volttron_agents:
                print("volttron-ctl not found. Make sure you have VOLTTRON installed and volttron-ctl is on your PATH. " + \
                      "You may need to activate the VOLTTRON virtual environment.")
                return
            
            # Check for the error message about VOLTTRON not running.
            if "VOLTTRON is not running. This command requires VOLTTRON platform to be running" in volttron_agents:
                print("No running instance of VOLTTRON detected.")
                return
            
            # The VOLTTRON_HOME standard VOLTTRON environment variable
            volttron_home = os.environ.get("VOLTTRON_HOME", None)
            
            # VOLTTRON_HOME is needed to identify the install location.
            if volttron_home == None:
                
                print("Environment variable VOLTTRON_HOME not set. Aborting.")
                return
            
            # If ACTIVE Bootstrap agent isn't installed, install it
            if not "ACTIVEBootstrap" in volttron_agents:
                print("ACTIVE Bootstrap Agent not installed in VOLTTRON. Attempting to Install...")
            
                
                volttron_home = os.path.expanduser(volttron_home)
                
                if not volttron_home.endswith("/"):
                    volttron_home = volttron_home + "/"
                
                # Create the agent directory and write the VOLTTRON agent files into it
                Path(volttron_home + "ACTIVEBootstrapAgent/bootstrap").mkdir(parents=True, exist_ok=True)
                self._write_files(volttron_home)
                
                print("ACTIVE Bootstrap Agent installed.")
            
            
            # Create a directory to store the VOLTTRON agent config
            Path(volttron_home + "configuration_store/agent_configs/ACTIVEBootstrapAgent").mkdir(parents=True, exist_ok=True)    
            
            # Get the configuration file contents
            active_configuration = self.internal_active_parameters["config"]
            
            # Search the agents block for the agent definition that corresponds to this instance
            for agent_block in active_configuration["agents"]:
                
                if self.internal_active_parameters["name"] == agent_block["name"]:
                    own_block = agent_block
                    break
            
            # Remove all other agents from the configuration, so that the VOLTTRON agent will only run a copy of this one    
            active_configuration["agents"] = [own_block]
            
            # Create a configuration file for the ACTIVE instance to run inside VOLTTRON
            with open(volttron_home + "configuration_store/agent_configs/ACTIVEBootstrapAgent/config.json", "w") as config_file:
                json.dump(active_configuration, config_file, indent=4)
            
            # Start the ACTIVE Bootstrap Agent in VOLTTRON
            Popen(["volttron-ctl", "install", volttron_home + "ACTIVEBootstrapAgent", "--force", "--start", 
                            "--agent-config", volttron_home + "configuration_store/agent_configs/ACTIVEBootstrapAgent/config.json"])
                
    def _write_files(self, volttron_home):
        '''
        Create the Python directory structure and files that define the ACTIVE Bootstrap Agent for VOLTTRON.
        
        Args:
            volttron_home String path to the VOLTTRON_HOME environment variable directory where the agent will be installed
        '''
        
        # From each pacakge data file, write the file into the install location
        with open(volttron_home + "ACTIVEBootstrapAgent/setup.py", "w") as setup:
            source = pkgutil.get_data('active', 'agent/ACTIVEBootstrapAgent/setup.py')
            
            for line in source.decode('utf-8'):
                setup.write(line)
                
        with open(volttron_home + "ACTIVEBootstrapAgent/bootstrap/__init__.py", "w") as init:
            source = pkgutil.get_data('active', 'agent/ACTIVEBootstrapAgent/bootstrap/__init__.py')
            
            for line in source.decode('utf-8'):
                init.write(line)
                
        with open(volttron_home + "ACTIVEBootstrapAgent/bootstrap/agent.py", "w") as agent:
            source = pkgutil.get_data('active', 'agent/ACTIVEBootstrapAgent/bootstrap/agent.py')
            
            for line in source.decode('utf-8'):
                agent.write(line)
                
        with open(volttron_home + "ACTIVEBootstrapAgent/bootstrap/settings.py", "w") as settings:
            source = pkgutil.get_data('active', 'agent/ACTIVEBootstrapAgent/bootstrap/settings.py')
            
            for line in source.decode('utf-8'):
                settings.write(line)
                
                
                
                
                
                
                
            
        
        