import argparse
import copy
import importlib
import importlib.util
import json
import os
import sys
import threading
import time

from active.agent.agent_factory import AgentFactory
from active.controller.controller_factory import ControllerFactory
from active.datastore.data_store_factory import DataStoreFactory
from active.emulator.emulator_factory import EmulatorFactory
from active.gui import ACTIVE_Workbench
from active.multiplexer.multiplexer_factory import MultiplexerFactory
from active.strategy.strategy_factory import StrategyFactory
from active.testing.test_step_factory import TestStepFactory
from builtins import list


    
# Dictionary from the name of each Component that started a thread to the thread it started
emulator_threads = {}
agent_threads = {}

# Stack of Components currently under construction
reference_construction_stack = []

def execute(command, config, environment="Python"):
    '''
    Execute the provided command, given the user specified configuration file and environment.
    
    Args:
        command: String specifying the ACTIVE command. Must be one of:
            "start"- Start the environment.
        config: Dictionary of contents of an environment configuration file.
        environment: The context in which this instance is being run. Must be one of:
            "Python"- ACTIVE is being run directly in Python, as from the command line.
            "Volttron"- ACTIVE is being run from within a VOLTTRON agent.
    Return:
        A List of Agents which were started. Or None, if command was not recognized.
    '''
    
    # Parse any extensions listed in the configuration.
    if "extension directories" in config:
    
        for extension_path in config["extension directories"]:
    
            # List of all files in the extension package
            package_files = [] 
            
            # Get all the *.py files in the extension package
            for root, dirs, files in os.walk(extension_path):
                for file in files:
                    if file.endswith(".py"):
                        package_files.append(os.path.join(root, file))
                        
            # Import each file in the extension package
            for source_file in package_files:
                
                module_name = str(os.path.basename(source_file))[:-3]
                spec = importlib.util.spec_from_file_location(module_name, source_file)
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
    
    # List of all user specified agents
    agents = {}
             
    # List of all user specified controllers   
    controllers = {}        
    
    # List of all user specified controllers   
    data_stores = {}     
    
    # Dictionary of multiplexer names to user specified multiplexers
    multiplexers = {}
    
    # Dictionary of emulator names to emulators
    emulators = {}
    
    # ACTIVE's internal variables should include the environment and a full copy of the config
    internal_variables = { "environment": environment }
    internal_variables["config"] = copy.deepcopy(config)
            
    # Switch on command name
    if command == "start":
        
        # Start the environment
        _setup_environment(config, controllers, data_stores, emulators, multiplexers, agents, internal_variables, environment, emulator_threads, agent_threads)
               
        for name, agent in agents.items():
            print("Starting agent " + name)
            _start_agent(agent, name, agent_threads)
            
        # Wait for agents to resolve if this is the base instance
        if environment == "Python":
            if "keep alive" in config and config["keep alive"]:
              for thread in emulator_threads:
                  emulator_threads[thread].join()  
            
        return list(agents.values())
    
    elif command == "test":
        
        if not "tests" in config.keys():
            print("No tests defined in environment file.")
            return
            
        # Number of current test
        test_index = 0
            
        # Run each test in succession
        for test in config["tests"]:
            
            test_index += 1
            
            # Start the environment
            _setup_environment(config, controllers, data_stores, emulators, multiplexers, agents, internal_variables, environment, emulator_threads, agent_threads)
            
            # Number of steps elapsed in this test
            step_index = 0
            
            # Run each step of the current test
            for step in test:
                
                step_index += 1
                
                # action == function means execute a user defined test step
                if step["action"] == "function":
                            
                    # Run the test and get the list of errors
                    errors = _run_test_step(step, controllers, data_stores, emulators, multiplexers, agents, config)
                    
                    # If there are any errors, print them and halt
                    if len(errors) > 0:
                        
                        print("ACTIVE Test: Failure in Test " + str(test_index) + " on Step " + 
                              str(step_index) + " function " + step["type"] + 
                              ". Error message(s) were:")
                        
                        for error in errors:
                            print("ACTIVE Test:" + error)
                            
                        return
                        
                # action == start means to start an emulator or agent
                elif step["action"] == "start":
                    
                    # Check each emulator to see if any match the requested component
                    for emulator_block in config["emulators"]:
                        
                        if emulator_block["name"] == step["component"]:
                            
                            # Start the emulator
                            _start_emulator(emulators[step["component"]], emulator_threads, emulator_block)
                            continue
                        
                    # if the component wasn't an emulator, check if there is an Agent of that name and start it
                    if step["component"] in agents.keys():
                        
                        _start_agent(agents[step["component"]], step["component"], agent_threads)
                    
                    # Print error for unknown Component    
                    else:
                        print("Attempted to start unrecognized Component " + step["component"])
                        return
                            
                elif step["action"] == "stop":
                    
                    # Check each emulator to see if any match the requested component
                    for emulator_block in config["emulators"]:
                        
                        if emulator_block["name"] == step["component"]:
                            
                            # Stop the emulator
                            _stop_emulator(emulators[step["component"]], emulator_block, emulator_threads)
                            continue
                    
                    # Print error for unknown Component
                    print("Attempted to stop unrecognized Component " + step["component"])
                    return
                            
                # Action == wait means allow time to elapse
                elif step["action"] == "wait":
                    
                    time.sleep(step["seconds"])
            
        # All agents are stopped in last test, so there are none running to return
        return []
        
    else:
        print('Unrecognized command "' + command + '".')
        return []

def run():
    '''
    Main entry point into ACTIVE.
    
    '''
    
    # Add argument parsing for the command and the configuration file
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("config")
    args = parser.parse_args()

    # Load the configuration file's contents, then execute the command.
    with open(args.config) as config_file:
        config = json.load(config_file)
        
        if "log" in config and config["log"]:
            sys.stderr = open(config["log"], "w")
            sys.stdout = open(config["log"], "w")
        
        agents = execute(args.command, config, "Python")
            
        if "GUI" in config and config["GUI"]:
            ACTIVE_Workbench.run(args.config)

        for thread in agent_threads:
            agent_threads[thread].join()  
        
        if "GUI" in config and config["GUI"]:
            
            # Loop forever to keep the GUI up
            while True:
                time.sleep(10)
        
def _create_controller(controller_block, controllers, data_stores, emulators, multiplexers, config):
    '''
    Initialize a controller according to the configuration file definition.
    
    Args:
        controller_block: Dictionary of contents of the "controllers" section block from the environment configuration file,
            defining the controller to be created.
        controllers: Dictionary of controller names to Controllers.
        data_stores: Dictionary of data_store names to DataStores.
        emulators: Dictionary of emulator names to Emulators.
        mutliplexers: Dictionary of multiplexer names to Multiplexers.
        config: Dictionary of the contents of the configuration file.
    Return:
        The new Controller
    '''
    
    # Check if this controller is already being instantiated higher up on the stack
    if controller_block["name"] in reference_construction_stack:
        reference_construction_stack.append(controller_block["name"])
        print("Circular reference detected in Environment file: " + str(reference_construction_stack))
        exit()
        
    # Add this component to the stack of Components under construction
    reference_construction_stack.append(controller_block["name"])
    
    # Get the Controller subclass from 'type'
    controller_class = ControllerFactory.get(controller_block["type"])
    
    # If the Controller type was not found, print an error messsage
    if controller_class == None:
        print('Unknown Controller type "' + controller_block["type"] + '". If you were attempting to add a ' +
            "Controller from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded Controllers are:")
        print(list(ControllerFactory.names()))
        return
    
    # Parse all references to other ACTIVE components.
    _replace_active_references(controller_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Initialize the controller and save it by name.
    controller = controller_class(**controller_block["parameters"])
    controllers[controller_block["name"]] = controller
    
    # Construction complete, remove the new component from the construction stack
    reference_construction_stack.pop()
    
    return controller
    
def _create_data_store(data_store_block, controllers, data_stores, emulators, multiplexers, config):
    '''
    Initialize a data store according to the configuration file definition.
    
    Args:
        data_store_block: Dictionary of contents of the "data stores" section block from the environment configuration file,
            defining the data store to be created.
        controllers: Dictionary of controller names to Controllers.
        data_stores: Dictionary of data_store names to DataStores.
        emulators: Dictionary of emulator names to Emulators.
        multiplexers: Dictionary of multiplexer names to Multiplexers.
        config: Dictionary of the contents of the configuration file.
    Return:
        The new DataStore
    '''
    
    # Check if this data storer is already being instantiated higher up on the stack
    if data_store_block["name"] in reference_construction_stack:
        reference_construction_stack.append(data_store_block["name"])
        print("Circular reference detected in Environment file: " + str(reference_construction_stack))
        exit()
        
    # Add this component to the stack of Components under construction
    reference_construction_stack.append(data_store_block["name"])
    
    # Get the DataStore subclass from 'type'
    data_store_class = DataStoreFactory.get(data_store_block["type"])
    
    # If the Data Store type was not found, print an error messsage
    if data_store_class == None:
        print('Unknown Data Store type "' + data_store_block["type"] + '". If you were attempting to add a ' +
            "Data Store from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded Data Stores are:")
        print(list(DataStoreFactory.names()))
        return
    
    # Parse all references to other ACTIVE components.
    _replace_active_references(data_store_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Initialize the data store and save it by name.
    data_store = data_store_class(**data_store_block["parameters"])
    data_stores[data_store_block["name"]] = data_store
    
    # Construction complete, remove the new component from the construction stack
    reference_construction_stack.pop()
    
    return data_store
    
def _create_emulator(emulator_block, controllers, data_stores, emulators, multiplexers, config):
    '''
    Initialize an Emulator according to the configuration file definition.
    
    Args:
        emulator_block: Dictionary of contents of the "emulators" section block from the environment configuration file,
            defining the emulator to be created.
        controllers: Dictionary of controller names to Controllers.
        data_stores: Dictionary of data_store names to DataStores.
        emulators: Dictionary of emulator names to Emulators.
        multiplexers: Dictionary of multiplexer names to Multiplexers.
        config: Dictionary of the contents of the configuration file.
    Return:
        The new Emulator
    '''
    
    # Check if this controller is already being instantiated higher up on the stack
    if emulator_block["name"] in reference_construction_stack:
        reference_construction_stack.append(emulator_block["name"])
        print("Circular reference detected in Environment file: " + str(reference_construction_stack))
        exit()
        
    # Add this component to the stack of Components under construction
    reference_construction_stack.append(emulator_block["name"])
    
    # Get the Emulator subclass from 'type'
    emulator_class = EmulatorFactory.get(emulator_block["type"])
    
    # If the Emulator type was not found, print an error messsage
    if emulator_class == None:
        print('Unknown Emulator type "' + emulator_block["type"] + '". If you were attempting to add an ' +
            "Emulator from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded Emulators are:")
        print(list(EmulatorFactory.names()))
        return
    
    # Parse all references to other ACTIVE components
    _replace_active_references(emulator_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Initialize the emulator and save it by name.
    emulator = emulator_class(**emulator_block["parameters"])
    emulators[emulator_block["name"]] = emulator
    
    # Construction complete, remove the new component from the construction stack
    reference_construction_stack.pop()
    
    return emulator

def _create_multiplexer(multiplexer_block, controllers, data_stores, emulators, multiplexers, config):
    '''
    Initialize a controller according to the configuration file definition.
    
    Args:
        multiplexer_block: Dictionary of contents of the "multiplexers" section block from the environment configuration 
            file, defining the multiplexer to be created.
        controllers: Dictionary of controller names to Controllers.
        data_stores: Dictionary of data_store names to DataStores.
        emulators: Dictionary of emulator names to Emulators.
        multiplexers: Dictionary of multiplexer names to Multiplexers
        config: Dictionary of the contents of the configuration file.
    Return:
        The new Controller
    '''
    
    # Check if this multiplexer is already being instantiated higher up on the stack
    if multiplexer_block["name"] in reference_construction_stack:
        reference_construction_stack.append(multiplexer_block["name"])
        print("Circular reference detected in Environment file: " + str(reference_construction_stack))
        exit()
        
    # Add this component to the stack of Components under construction
    reference_construction_stack.append(multiplexer_block["name"])
    
    # Get the Multiplexer subclass from 'type'
    multiplexer_class = MultiplexerFactory.get(multiplexer_block["type"])
    
    # If the Multiplexer type was not found, print an error messsage
    if multiplexer_class == None:
        print('Unknown Multiplexer type "' + multiplexer_block["type"] + '". If you were attempting to add a ' +
            "Multiplexer from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded Multiplexers are:")
        print(list(MultiplexerFactory.names()))
        return
    
    # Parse all references to other ACTIVE components.
    _replace_active_references(multiplexer_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Initialize the multiplexer and save it by name.
    multiplexer = multiplexer_class(**multiplexer_block["parameters"])
    multiplexers[multiplexer_block["name"]] = multiplexer
    
    # Construction complete, remove the new component from the construction stack
    reference_construction_stack.pop()
    
    return multiplexer

def _create_agent(agent_block, internal_variables, agents, controllers, data_stores, emulators, multiplexers, config):
    '''
    Initialize an Emulator according to the configuration file definition.
    
    Args:
        emulator_block: Dictionary of contents of the "emulators" section block from the environment configuration file,
            defining the emulator to be created.
        controllers: Dictionary of controller names to Controllers.
        data_stores: Dictionary of data_store names to DataStores.
        emulators: Dictionary of emulator names to Emulators.
        multiplexers: Dictionary of multiplexer names to Multiplexers.
        config: Dictionary of the contents of the configuration file.
    Return:
        The new Emulator
    '''
    
    # Get the Agent subclass from the type
    agent_class = AgentFactory.get(agent_block["type"])

    # If the Agent type was not found, print an error messsage
    if agent_class == None:
        print('Unknown Agent type "' + agent_block["type"] + '". If you were attempting to add an ' +
            "Agent from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded Agents are:")
        print(list(AgentFactory.names()))
        return        
    
    # Parse all references to other ACTIVE components.
    _replace_active_references(agent_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Get the block containing the Agent's Strategy's definition
    strategy_block = agent_block["strategy"]
    
    # Get the Strategy subclass from the type
    strategy_class = StrategyFactory.get(strategy_block["type"])

    # If the Strategy type was not found, print an error messsage
    if strategy_class == None:
        print('Unknown Strategy type "' + strategy_block["type"] + '". If you were attempting to add a ' +
            "Strategy from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded Strategies are:")
        print(list(StrategyFactory.names()))
        return                    
    
    # Parse all references to other ACTIVE components.
    _replace_active_references(strategy_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Create a copy of the agent's internal variables
    agent_variables = copy.deepcopy(internal_variables)
    agent_variables["agent_name"] = agent_block["name"]
    
    agents[agent_block["name"]] = agent_class(strategy_class(**strategy_block["parameters"]), 
                                               agent_variables, **agent_block["parameters"])
    
def _initialize_base_components(controllers, data_stores, emulators, multiplexers, config):
    '''
    Initialize the components which do not have associated code execution (eg no start()): the controllers, data stores,
    and multiplexers.
    
    Args:
        controllers The dictionary of controller names to defined controllers.
        data_stores The dictionary of data stores names to defined data stores.
        emulators The dictionary of emulator names to defined emulators.
        multiplexers: The dictionary of multiplexer names to defined multiplexers.
        config: Dictionary of contents of the configuration file.
    '''
    
    # Initialzie all controllers in configuration
    if "controllers" in config:
        
        for controller_block in config["controllers"]:
            
            _create_controller(controller_block, controllers, data_stores, emulators, multiplexers, config)
                    
    # Initialzie all data stores in configuration
    if "data stores" in config:
        
        for data_store_block in config["data stores"]:
            
            _create_data_store(data_store_block, controllers, data_stores, emulators, multiplexers, config)
            
    if "multiplexers" in config:
        
        for multiplexer_block in config["multiplexers"]:
            
            _create_multiplexer(multiplexer_block, controllers, data_stores, emulators, multiplexers, config)
        
def _interpret_active_reference(target, controllers, data_stores, emulators, multiplexers, config):
    '''
    Create the full version of the input string, replacing any ACTIVE references. A string is an ACTIVE reference if and 
    only if it is of the form "!ACTIVE:foo" where foo is the reference to be interpreted. References will be interpreted by 
    the first match in sequence of:
    
    "!FILE-foo:bar": A file of format foo at location bar. Valid formats are: json
    "foo": A Controller with "name": "foo" in its own parameters.
    "foo": A Data Store with "name": "foo" in its own parameters.
    
    Args:
        target The String to be interpreted.
        controllers The dictionary of controller names to defined controllers.
        data_stores The dictionary of data stores names to defined data stores.
        emulators The dictionary of emulator names to defined emulators.
        multiplexers: The dictionary of multiplexer names to defined multiplexers.
    Return:
        The target if it was not an ACTIVE reference, or the dictionary or component it represented if it was.
    '''
    
    # Only strings can specify ACTIVE references
    if not isinstance(target, str):
        return target
    
    # References begin with !ACTIVE:
    if target.startswith("!ACTIVE:"):
        
        # Remove the prefix
        target = target[8:]
        
        # Check for a sub-reference
        if target.startswith("!"):
            
            # !FILE specifies a file to load
            if target.startswith("!FILE"):
                
                # The contents of the loaded file
                contents = {}
                
                # !FILE-json specifies a json format file to load
                if target.startswith("!FILE-json:"):
                    target = target[11:]
                    
                    with open(target) as param_file:
                        contents = json.load(param_file)
                
                # !FILE reference did not use a known file type. 
                else:
                    print('Directive "' + target + '" references unknown file type.')
                    exit(1)
                
                return contents
                    
                    
        else:
            
            # If it was a simple reference, get the Controller/DataStore of that name
            if target in controllers:
                return controllers[target]
            elif target in data_stores:
                return data_stores[target]
            elif target in emulators:
                return emulators[target]
            elif target in multiplexers:
                return multiplexers[target]
            
            # If the references wasn't found, but it did exist in the controllers/data stores/emulator blocks, instantiate 
            # and save that Controller/DataStore
            if "controllers" in config:
                for controller_block in config["controllers"]:
                    if controller_block["name"] == target:
                        controller = _create_controller(controller_block, controllers, data_stores, emulators, multiplexers,
                                                        config)
                        return controller
                    
            if "data stores" in config:
                for data_store_block in config["data stores"]:
                    if data_store_block["name"] == target:
                        data_store = _create_data_store(data_store_block, controllers, data_stores, emulators, multiplexers,
                                                        config)
                        return data_store
                    
            if "emulators" in config:
                for emulator_block in config["emulators"]:
                    if emulator_block["name"] == target:
                        emulator = _create_emulator(emulator_block, controllers, data_stores, emulators, multiplexers, 
                                                    config)
                        return emulator
                    
            if "multiplexers" in config:
                for multiplexer_block in config["multiplexers"]:
                    if multiplexer_block["name"] == target:
                        multiplexer = _create_multiplexer(emulator_block, controllers, data_stores, emulators, multiplexers,
                                                       config)
            

            print('Config file contained unresolvable reference "!ACTIVE:' + target + '". No controller, ' +
                  "or data store named " + target + " defined.")
            exit(1)
    
    # The string wasn't a reference, so return it as is.    
    else:
        return target
        
def _replace_active_references(parameters, controllers, data_stores, emulators, multiplexers, config):        
    '''
    Replace all ACTIVE references in parameters. A parameter is an ACTIVE reference if and only if it is of the form 
    "!ACTIVE:foo" where foo is the reference to be interpreted. References will be interpreted by the first match in 
    sequence of:
    
    "foo": A Controller with "name": "foo" in its own parameters.
    "foo": A Data Store with "name": "foo" in its own parameters.
    
    Args:
        parameters A dictionary or list or parameters, or a string (which will be ignored.
        controllers The dictionary of controller names to defined controllers.
        data_stores The dictionary of data stores names to defined data stores.
        emulators The dictionary of emulator names to defined emulators.
        multiplexers: Dictionary of multiplexer names to defined Multiplexers
    '''
    
    # If the parameters are a list, check each item for references
    if isinstance(parameters, list):

        for i, item in enumerate(parameters):
            
            # If the item is a dictionary or list, recurse on it
            if isinstance(item, dict) or isinstance(item, list):
                _replace_active_references(item, controllers, data_stores, emulators, multiplexers, config)
                
            # If it is a string, attempt to interpret it
            else:
                parameters[i] = _interpret_active_reference(item, controllers, data_stores, emulators, multiplexers, config)
    
    # If the parameters are a dictionary, try to look for any references
    elif isinstance(parameters, dict):

        for key, value in parameters.items():
            
            # If the value is a dictionary or list, recurse on it
            if isinstance(value, dict) or isinstance(value, list):
                _replace_active_references(value, controllers, data_stores, emulators, multiplexers, config)
                
            # If the value is a string, attempt to interpret it
            elif isinstance(value, str):
                parameters[key] = _interpret_active_reference(value, controllers, data_stores, emulators, multiplexers,
                                                            config)
                
def _run_test_step(test_step_block, controllers, data_stores, emulators, multiplexers, agents, config):
    '''
    Run the given TestStep and return any error messages.
    
    Args:
        test_step_block Dictionary for the config file definition of this test step
        controllers Dictionary from String names to Controllers
        data_stores Dictioanry from String names to DataStores
        emulators Dictionary from String names to Emulators
        multiplexers Dictionary from String names to Multiplexers
        agents Dictionary from String names to Agents
        config Dictionary of configuration information from the configuration file 
    Return
        A list of Strings for all errors produced by the test step. An empty list means no errors occured.
    '''

    # Get the TestStep callablefrom 'type'
    step = TestStepFactory.get(test_step_block["type"])
    
    # If the TestStep type was not found, print an error message
    if step == None:
        print('Unknown TestStep type "' + test_step_block["type"] + '". If you were attempting to add a ' +
            "TestStep from an extension, make sure its location is listed in 'extension directories' in your " +
            "configuration file. Loaded TestSteps are:")
        print(list(TestStepFactory.names()))
        return
    
    # Parse all references to other ACTIVE components.
    _replace_active_references(test_step_block["parameters"], controllers, data_stores, emulators, multiplexers, config)
    
    # Run the test step 
    return step(**test_step_block["parameters"])
                
def _setup_environment(config, controllers, data_stores, emulators, multiplexers, agents, internal_variables, environment, emulator_threads, agent_threads):          
    '''
    Create all the Components for an Environment and start the Emulators.
    
    If an Agent has "main thread: true" set this will not return until the Agent is finished. 
    
    Args:
        config Dictionary of configuration information from the configuration file 
        controllers Dictionary from String names to Controllers
        data_stores Dictioanry from String names to DataStores
        emulators Dictionary from String names to Emulators
        multiplexers Dictionary from String names to Multiplexers
        agents Dictionary from String names to Agents
        internal_variables Dictionary of internal ACTIVE values
        environment String for where the Environment is being set up. Current valid values are Python and VOLTTRON
        emulator_threads Dictionary from string names to the thread running an emulator
        agent_threads Dictionary from string names to the thread running an agent
    '''
    
    
    # Initialzie all emulators in configuration
    if "emulators" in config:
        
        for emulator_block in config["emulators"]:
            
            emulator = _create_emulator(emulator_block, controllers, data_stores, emulators, multiplexers, config)
            
            # Start the emulator immediately
            _start_emulator(emulator, emulator_threads, emulator_block)
                
    # Assume that any base Python instance of ACTIVE is the original version. Start all controllers/data stores in 
    # that instance, only creating the rest as needed.
    if "Python" == environment:
        _initialize_base_components(controllers, data_stores, emulators, multiplexers, config)

    # Create each agent 
    for agent_block in config["agents"]:
        
        # If running inside VOLTTRON, don't run any agents other than the ones intended for VOLTTRON
        if environment == "Volttron" and agent_block["type"] != "volttron":
            continue
        
        # Save a copy of the agent's name in the internal variables so that the agent can look up its own definition
        internal_variables["name"] = agent_block["name"]
        
        agent_class = AgentFactory.get(agent_block["type"])
            
        _create_agent(agent_block, internal_variables, agents, controllers, data_stores, emulators, multiplexers, config)
        
        # If main thread is set, remove the agent from the list and run it immediately on the main thread
        if "main thread" in agent_block and agent_block["main thread"]:
            agent = agents[agent_block["name"]]
            del agents[agent_block["name"]]
            agent.start()
            
def _start_agent(agent, name, agent_threads):
    '''
    Start the given Agent in a thread.
    
    Args:
        agent The Agent to start
        name String name of the Agent
        agent_threads Dictionary from string names to a Thread running that Agent
    '''
    
    #agent.start()
    thread = threading.Thread(target = agent.start)
    thread.daemon = True
    thread.start()
    agent_threads[name] = thread
        
def _start_emulator(emulator, emulator_threads, emulator_block):
    '''
    Start the given Emulator in a thread.
    
    Args:
        emulator The Emulator to start
        emulator_threads Dictionary from emulator names to a Thread running that Emulator
        emulator_block Dictionary of configuration information for this Emulator from the config file
    '''
    
    #emulator.start()
    thread = threading.Thread(target = emulator.start)
    thread.daemon = True
    thread.start()
    emulator_threads[emulator_block["name"]] = thread
    
    # If a startup delay is noted, wait for the emulator to warmup before proceeding.
    if "startup delay" in emulator_block.keys():  
        time.sleep(emulator_block["startup delay"])  
        
def _stop_emulator(emulator, emulator_block, emulator_threads):
    '''
    Stop the given Emulator's thread.
    
    Args:
        emulator The Emulator to stop
        emulator_block Dictionary of configuration information for this Emulator from the config file
        emulator_threads Dictionary of string names to the Thread running that emulator
    '''
    
    # Signal the emulator to stop
    emulator.stop()
    
    # Wait for the thread to terminate
    emulator_threads[emulator_block["name"]].join()
    
    # Remove the stopped Thread from memory
    del emulator_threads[emulator_block["name"]]
    
    
 
    