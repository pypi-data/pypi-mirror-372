import json
import os

from pathlib import Path
from subprocess import Popen

from active.emulator.decorators import ActiveEmulator

@ActiveEmulator("VOLTTRON SQLite Historian")
class VOLTTRONSQLiteHistorianEmulator():
    '''
    Emulator for the VOLTTRON SQLite Historian VOLTTRON Agent. Does not actually emulate a VOLTTRON Agent, but instead
    launches the real thing.
    
    Requires a running instance of VOLTTRON.
    
    Params
        config: Dictionary of values equivalent to the content of the VOLTTRON configuration file for the agent.
        tag: String defining the custom name the VOLTTRON Agent will be known by. Should be unique.
        volttron_path: String to the VOLTTRON installation directory.
    '''
    
    def __init__(self, database_path, parameters, tag, volttron_path):
        '''
        Default constructor.
        
        Args
            database_path: String for the path to the .sqlite file to store the database
            parameters: Dictionary from String keys to arbitrary values to be added to the VOLTTRON configuration file. See
                https://volttron.readthedocs.io/en/develop/agent-framework/historian-agents/historian-framework.html for
                details on valid parameters.
            tag: String defining the custom name the VOLTTRON Agent will be known by. Should be unique.
            volttron_path: String path to the base VOLTTRON installation directory. If the VOLTTRON executable is located at
                /home/admin/volttron/env/bin/volttron, then this must be "/home/admin/volttron"
        '''
        
        self.config = parameters
        
        # Add the definitions for the default parameters to the custom ones defined by the user.
        self.config.update({
            "agentid": "sqlhistorian-sqlite",
            "connection": {
                "type": "sqlite",
                "params": {
                    "database": database_path
                }
            }
        })
        
        self.tag = tag

        self.volttron_path = volttron_path
        if not self.volttron_path.endswith("/"):
            self.volttron_path = self.volttron_path + "/"
        
    def start(self):
        '''
        Start the Historian Agent in VOLTTRON
        '''
        
        # The VOLTTRON_HOME standard VOLTTRON environment variable
        volttron_home = os.environ.get("VOLTTRON_HOME", None)
        
        # VOLTTRON_HOME is needed to identify the install location.
        if volttron_home == None:
            
            print("Environment variable VOLTTRON_HOME not set. Aborting.")
            return
        
        # Ensure the home path ends with /
        if not volttron_home.endswith("/"):
            volttron_home = volttron_home + "/"
        
        # Create a directory to store the VOLTTRON agent config
        Path(volttron_home + "configuration_store/agent_configs/SQLiteHistorianAgent").mkdir(parents=True, exist_ok=True)   
        
        # Create a configuration file for the ACTIVE instance to run inside VOLTTRON
        with open(volttron_home + "configuration_store/agent_configs/SQLiteHistorianAgent/config.sqlite", "w") as config_file:
            json.dump(self.config, config_file, indent=4)
            
        print("volttron-ctl install "+ self.volttron_path + "services/core/SQLHistorian --force --start --agent-config " +
                        volttron_home + "configuration_store/agent_configs/SQLiteHistorianAgent/config.sqlite --tag ACTIVE-SQLiteHistorian-" + self.tag)
        
        # Start the SQLiteHistorian Agent in VOLTTRON
        Popen(["volttron-ctl", "install", self.volttron_path + "services/core/SQLHistorian", "--force", "--start", 
                        "--agent-config",
                        volttron_home + "configuration_store/agent_configs/SQLiteHistorianAgent/config.sqlite",
                        "--tag",
                        "ACTIVE-SQLiteHistorian-" + self.tag])

    def stop(self):
        '''
        Stop the Historian Agent in VOLTTRON
        '''
        
        # Stop the SQLiteHistorian Agent in VOLTTRON
        Popen(["volttron-ctl", "stop", "ACTIVE-SQLiteHistorian-" + self.tag])
        
if __name__ == "__main__":
    test =  VOLTTRONSQLiteHistorianEmulator(database_path="/home/volttron/volttron/platform.historian.sqlite",
                                            parameters={
                                                "capture_device_data": True,
                                                "capture_analysis_data": False,
                                                "capture_log_data": False,
                                                "capture_record_data": False,
                                                "custom_topics": {
                                                    "other_topic": ["tnc"]
                                                }
                                            },
                                            tag="g36",
                                            volttron_path="/home/volttron/volttron/")       
    test.start()
