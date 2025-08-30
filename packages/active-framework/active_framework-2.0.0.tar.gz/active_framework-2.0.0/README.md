# ACTIVE

The Automated Control Testbed for Integration, Verification, and Emulation (ACTIVE) is operation management and algorithm testing software designed for building control.

## Installation

To install ACTIVE:

```
pip install Active --index-url https://code.ornl.gov/api/v4/projects/15464/packages/pypi/simple
```

To install on a machine with no internet connectivity:

```
pip download Active -d /path/to/my_folder --index-url https://code.ornl.gov/api/v4/projects/15464/packages/pypi/simple
(Move my_folder to the machine)
pip install /path/to/my_folder
```

## Usage 

From the command line:

```
active start config.json
```

See example.json for an example of a config file.

### Environment File Definition

An Environment configuration file is a .json format. It specifies all Components for the Environment as well as options such as source code directories. It follows this format:

```
{
	"GUI": false,
	"extension directories": [
		...
	],
	"controllers": [
		...
	],
	"data stores": [
		...
	],
	"multiplexers": [
		...
	],
	"emulators": [
		...
	],
	"agents": [
		...
	],
	"tests": [
		...
	]
}
```
All fields are optional. The specifications for each field are as follows:

```
{
	"GUI": false
}
```

The GUI field sets whether or not to stand up the ACTIVE Workbench web-based GUI. If omitted from the file, default is "false".

```
{
	"extension directories": [
		"/path/to/my/extension"
	]
}
```

The extension directories block contains a list of strings which are paths to directories containing user code. All code in an extension directory and all sub-directories will be imported, so any side effects from importing will apply to the current ACTIVE instance during start up. See [Extensions](#extensions) for a more detailed description of how to create an Extension.

```
"controllers": [
	{
		"name": "MyControllerName",
		"type": "MyControllerType",
		"parameters": {
			...
		}
	}
],
```

The controllers block contains a list of definitions for Controller Components. Each Controller contains a unique `name`. A controller also has a `type` and `parameters`. The contents of `parameters` are determined by the controller's `type`, while the `type` must be match either one of the default Controller types (see [Controllers](#controllers) for a list) or a custom user defined Controller marked with the `@ActiveController("MyControllerType")` decorator in one of the directories from the `extension directories` block above.

```
"data stores": [
	{
		"name": "MyDataStoreName",
		"type": "MyDataStoreType",
		"parameters": {
			...
		}
	}
],
```

The data stores block contains a list of definitions for Data Store Components. Each Data Store contains a unique `name`. A data store also has a `type` and `parameters`. The contents of `parameters` are determined by the data store's `type`, while the `type` must be match either one of the default DataStore types (see [Data Stores](#data-stores) for a list) or a custom user defined DataStore marked with the `@ActiveDataStore("MyDataStoreType")` decorator in one of the directories from the `extension directories` block above.

```
"emulators": [
	{
		"name": "MyEmulatorName",
		"type": "MyEmulatorType",
		"parameters": {
			...
		}
	}
],
```

The emulators block contains a list of definitions for Emulator Components. Unlike Controller or Data Store Components above, an Emulator will be started by ACTIVE when the Environment is started. Each Emulator contains a unique `name`. An emulator also has a `type` and `parameters`. The contents of `parameters` are determined by the emulator's `type`, while the `type` must be match either one of the default Emulator types (see [Emulator](#emulators) for a list) or a custom user defined Emulator marked with the `@ActiveEmulator("MyEmulatorType")` decorator in one of the directories from the `extension directories` block above. 

```
"agents": [
	{
		"name": "MyAgentName",
		"type": "MyAgentType",
		"parameters":{
			...
		},
		"strategy": {
			"type": "MyStrategyType",
			"parameters":{
				...
			}
		}
	}
]
```

The agents block contains a list of definitions for Agent Components. Unlike Controller or Data Store Components above, an Agent will be started by ACTIVE when the Environment is started. Each Agent contains a unique `name`. An agent also has a `type` and `parameters`. The contents of `parameters` are determined by the agent's `type`, while the `type` must be match either one of the default Agent types (see [Agent](#agents) for a list) or a custom user defined Agent marked with the `@ActiveAgent("MyAgentType")` decorator in one of the directories from the `extension directories` block above. 

Each Agent also contains another Component, a Strategy, defined under the `strategy` field. A Strategy contains `type` and `parameters` fields just like an Agent, though its type must be defined in an extension class with the `@ActiveStrategy("MyStrategyType` decorator. ACTIVE currently does not supply any default Strategies.

Not all fields need to be, or can be, set with raw JSON primitives. ACTIVE allows the use of special ACTIVE directives within the environment configuration file for ease of use or for references ACTIVE components. There are two ACTIVE directives:

-	The ACTIVE Component directive: This directive is of the format `!ACTIVE:MyComponentName`. It provides one of the Controllers, Data Stores, or Emulators as an argument to the constructor of the Component that uses it.
-	The file directive: This directive is of the format `!ACTIVE:!FILE-type:/path/to/my/file`. It loads a file of format `type` into the configuration file as a dictionary in place of the reference string. The only type of file currently supported is JSON.

For example, consider the following Environment configuration file:

```
{
	"extension directories": [
		"/path/to/my/extension"
	]
},
"controllers": [
	{
		"name": "MyControllerName",
		"type": "MyControllerType",
		"parameters": {
		}
	}
],
"agents": [
	{
		"name": "MyAgentName",
		"type": "MyAgentType",
		"parameters":{
		},
		"strategy": {
			"type": "MyStrategyType",
			"parameters":{
				"building_api": "!ACTIVE:MyControllerName",
				"zone_definitions": "!ACTIVE:!FILE-json:/home/data/test_building_2.json"
			}
		}
	}
]
```
When the `MyStrategyType` class's `__init__(building_api, zone_definitions)` constructor is called, `building_api` will contain a `MyControllerType` object while `zone_definitions` will contain a dictionary with the contents of test_building_2.json inside.


### Extensions

ACTIVE is designed to run user code without requiring users to modify ACTIVE's source. This is achieved through the creation of Extension package. An extension is any Python package with an ACTIVE decorator used to define one or more Components. 

Consider the case of wanting to add your own Strategy to run. You would create a .py file with content like:

```
from mypackage.genetic_algorithm_strategy_base import GeneticAlgorithmStrategyBase

from active.strategy.decoratorys import ActiveStrategy

@ActiveStrategy("GA")
class GeneticAlgorithmStrategy(GeneticAlgorithmStrategyBase)
```

Line 1 imports a user written base class named GeneticAlgorithmStrategyBase. This is not strictly neccesary. However, due to the dynamic way in which ACTIVE imports Component classes, static class members will not be available in any Component. This will cause issues with State management in c bindings, such as are used in EnergyPlus via the EnergyPlusController. It is therefore recommended that all custom Components follow this pattern and leave all business logic and data in a superclass as done in this example.

Line 2 imports the decorator.

Line 3 annotates the user's class as an ACTIVE Component. While this Extension is loaded, a Strategy in the Environment configuration file may be given the user defined name ("GA" in this example) as its `type` and ACTIVE will use this class for it. Extension names override previous names in the order they are specified in the `extension directories` block. This may be used to override default ACTIVE Components. (eg Giving your own class the annotation `@ActiveController("EnergyPlus")` will cause all ACTIVE's EnergyPlus Controllers to use your local class instead of the default one.)

Line 4 defines the class which will become the ACTIVE component (and the superclass it uses as discussed previously)

For an example extension, see examples/mypackage:

mystrategy.py is an example of injecting custom extension code into ACTIVE.

logger_controller.py is an example of overridding a default component.

## Architecture

ACTIVE conceives of each building operation scenario as a set of Components which manage one independent part of the control logic or communications apiece. 

### Components

A Component is a logical unit for the operation of building control. Components are intended, to the greatest degree logically possible, to be transparently swappable with other components of the same kind. Two different Data Stores should accept the same inputs when saving a piece of data. This is not always possible. A ThermostatController and a WaterHeaterController should not both have a get_water_temperature() method, but an EcobeeThermostatController and a BACNetThermostatController should both support a get_current_set_point() method or at least throw a NotImplementedError so that the user can appropriately handle a given piece of hardware's inability to perform a certain capability.

### Agents

An Agent is a backend that runs a Strategy. An Agent is responsible for determining how often and when certain parts of a Strategy are to be run. An Agent may also be required to initialize or interface with some other platform, such as VOLTTRON, in order to run a Strategy within that context.

Agents contain a start() function. This function is responsible for all business logic and is the only part of the Agent that will be invoked by ACTIVE.

All Agents have an additional optional parameter: "main thread". If "main thread" is present and true, the agent will be run to completion on the main ACTIVE thread, in the order it was defined in the environment file, before ACTIVE proceeds to launching any other Agents.

The SimpleAgent runs a Strategy for a given number of episodes, then creates the output files. 

| Parameter    | Definition |
| -------- | ------- |
| delay  | Integer defining the delay, in units of seconds, between each episode is run. Delay is relative to the time the first episode was run, such that if the run time is greater than the delay, the next episode will run immediately |
| num_episodes  | Integer defining the number of episodes for which the Strategy is to be run    |

Sample configuration:

```
{
	"name": "MachineLearning",
	"type": "simple",
	"parameters":{
		"delay": 0,
		"num_episodes": 1
	},
	"strategy": {
		...
	}
}
```

The EnergyPlusAPIAgent runs code inside an EnergyPlus simulation. It runs for a given number of episodes. During each episode, the Agent will direct the Strategy to perform any necessary calculations, then launch the EnergyPlus simulation for one episode, then have the Strategy output any files.

| Parameter    | Definition |
| -------- | ------- |
| begin_system_timestep_before_predictor_handler | String name for a Callable from the Strategy to register for EnergyPlus as the begin_system_timestep_before_predictor callback |
| emulator | An EnergyPlusAPI type ACTIVE Emulator which will run the simulation |
| episodes  | Integer defining the number of episodes for which the Strategy is to be run    |
| inside_system_iteration_loop_handler | String name for a Callable from the Strategy to register fo EnergyPlus as the inside_system_iteration_loop callback |

Sample configuration:

```
{
	"name": "MachineLearning",
	"type": "EnergyPlus API",
	"parameters":{
		"begin_system_timestep_before_predictor_handler": "run_rtus",
		"emulator": "!ACTIVE:EnergyPlus",
		"episodes": 2,
		"inside_system_iteration_loop_handler": "run_vavs"
	},
	"strategy": {
		...
	}
}
```

The IntersectClientAgent runs code inside an INTERSECT client. Functions from the Strategy will be invoked in response to defined events or messages. This Agent will never halt running on its own. Also, if it never receives any of the expected events or messages, it will never invoke any code.

| Parameter    | Definition |
| -------- | ------- |
| intersect_client | An IntersectController for the INTERSECT instance to be listened to. |
| service_mappings | A dictionary of four levels. The first level consists of unique INTERSECT service hierarchy definitions, in the format "organization.facility.type.subtype.capability". The second level is "events" and "messages" for that service. The third level are event types or operation sources, with the latter being of the form "capability.function". The last level are the values, strings that correspond this Agent's Strategy's functions. When an event or operation reply from INTERSECT is received  |

Sample configuration:

```
{
	"name": "MachineLearning",
	"type": "INTERSECT client",
	"parameters":{
		"intersect_client": "!ACTIVE:INTERSECT",
		"service_mappings": {
		    "oak-ridge-national-laboratory.none.bessd-pilot.soilcosm.digital-twin": {
				"events": {},
				"messages": {
					"SoilCosmDigitalTwin.perform_spinup": "save_model",
					"SoilCosmDigitalTwin.plot": "save_plot",
					"SoilCosmDigitalTwin.update_model": "update_model"
				}
		    },
		    "oak-ridge-national-laboratory.walker-branch.field.none.measurement": {
				"events": {
				    "observation made": "handle_new_observation"
				},
			"messages": {}
		    }
		}
	},
	"strategy": {
	...
	}
}
```

The VolttronAgent will install the ACTIVEBootstrapAgent (a VOLTTRON Agent, not an ACTIVE Agent) into the instance of VOLTTRON found at the VOLTTRON_HOME environmental variable's location if it does not already exist. It will then run that agent, which will open an instance of ACTIVE inside of Volttron. That instance of ACTIVE will then schedule the Strategy to run.

| Parameter    | Definition |
| -------- | ------- |
| schedule  | Dictionary of strings to integers. Keys are function names from Strategy. Values are the number of seconds between one invocation of that function and the next   |

Sample configuration:

```
{
	"name": "MachineLearning",
	"type": "volttron",
	"parameters":{
		"schedule": {
			"record": 5,
			"step": 300
		}
	},
	"strategy": {
		...
	}
}
```

### Controllers

A Controller manages all communications with some external program or device for the Strategy. Common Controller operations involve tasks such as retrieving data from a simulation or API or sending control signals to a device. There is no base Controller interface, as separate types of Controller (eg thermostat controllers vs data logger controllers) may have no overlap in functionality.

#### Clock Controllers

Clock Controllers handle communication with some time source.

The EnergyPlusAPI Clock Controller gets the current time from within a simulation run with EnergyPlus. It requires a local installation of EnergyPlus to function.

| Parameter    | Definition |
| -------- | ------- |
| emulator  | An EnergyPlusAPI Emulator in which the simulation will be run.   |

Sample configuration:

```
{
	"name": "SimulationClock",
	"type": "EnergyPlusAPI Clock",
	"parameters": {
		"emulator": "!ACTIVE:MyEnergyPlustAPIEmulator"
	}
}
```

The System Clock Controller gets the time from the operating system. It has no parameters.

Sample configuration:

```
{
	"name": "WallClock",
	"type": "System Clock",
	"parameters": {
	}
}
```

#### RTU Controllers

RTU Controller handle communications with a Roof Top Unit (RTU) and its associated Variable Air Volume (VAV) units. 

The EnergyPlus API RTU Controller communicates with a virtual RTU inside an EnergyPlus simulation.

| Parameter    | Definition |
| -------- | ------- |
| emulator  | An EnergyPlusAPI Emulator in which the simulation containing this RTU will be run.   |
| name | String unique name for this RTU |

Sample configuration:

```
{
	"name": "RTU 1",
	"type": "EnergyPlus API RTU",
	"parameters": {
		"emulator": "!ACTIVE:MyEnergyPlusAPIEmulator",
		"name": "RTU1"
	}
}
```

The BACNet RTU Controller communicates with an RTU over the BACNet protocol.

| Parameter    | Definition |
| -------- | ------- |
| address  | String representation of the device address. In the format of IP and port or the network:device "xx:yy" Bacnet address. |
| ip  | String defining own IP and network mask. In the format "xxx.xxx.xxx.xxx/xx" |
| port  | Integer port number for connection |
| vav_addresses  | Dictionary from String VAV names to dictionaries of parameter names to String BACNet object addresses for that parameter. |

Sample configuration:

```
{
	"name": "RTU1",
	"type": "BACNet RTU",
	"parameters": {
		"address": "127.17.0.101:47801"
		"ip": "127.17.0.100/24", 
		"port": 80,
		"vav_addresses": {
			"102": {
				"supply_airflow_rate": "3000011"
			},
			"103": {
				"supply_airflow_rate": "3000012"
			}
		}
	}
}
```

The CR1000X RTU Controller communicates with an RTU whose data is being published by a CR1000X data logger.

| Parameter    | Definition |
| -------- | ------- |
| url  | String base url where the data logger is publishing its data |
| vav_names  | List of Strings for each VAV name |

Sample configuration:

```
{
	"name": "RTU1",
	"type": "CR1000X RTU",
	"parameters": {
		"url": "127.17.0.102"
		"vav_names": [
			"102",
			"103"
		]
	}
}
```

#### Water Heater Controllers

Water Heater Controllers communicate with a water heater. 

There are no default implementations of the interface.

#### Other Controllers

The BACNetController communicates with a device using the BACNet protocol.

| Parameter    | Definition |
| -------- | ------- |
| ip  | String defining own IP and network mask. In the format "xxx.xxx.xxx.xxx/xx" |
| port  | Integer port number for connection |

Sample configuration:

```
{
	"name": "BACNet1",
	"type": "BACNet",
	"parameters": {
		"ip": "127.17.0.100/24", 
		"port": 80
	}
}
```

The CR3000 Controller communicates with a CR3000 data logger.

| Parameter    | Definition |
| -------- | ------- |
| tables  | List of Strings for the table names to download. Data from tables earlier in the list takes precedence over data from tables later in the list. |
| url  | String url for the server to scrape data from |

Sample configuration:

```
{
	"name": "DataLogger1",
	"type": "CR3000",
	"parameters": {
        "tables": ["my_table5sec", "my_table10min"],
        "url": "127.0.0.1:82"
    }
}
```

The Delta Solar Inverter Controller communicates with a Delta solar inverter.

| Parameter    | Definition |
| -------- | ------- |
| tables  | List of Strings for the table names to download. Data from tables earlier in the list takes precedence over data from tables later in the list. |
| url  | String url for the server to scrape data from |

Sample configuration:

```
{
	"name": "Inverter1",
	"type": "Delta Solar Inverter",
	"parameters": {
        "password": "password1", 
        "sn": "O1T0000000000", 
        "url": "https://delta-solar.vidagrid.com/api", 
        "username": "myname@company.com"
    }
}
```

The EnergyPlus Controller sets up and controls EnergyPlus simulations. The EnergyPlusController requires a local installation of EnergyPlus to function.

| Parameter    | Definition |
| -------- | ------- |
| console_out  | Boolean value determining whether to print the EnergyPlus output to std out    |

Sample configuration:

```
{
	"name": "EnergyPlus1",
	"type": "EnergyPlus",
	"parameters": {
		"console_out": false
	}
}
```

The HTTPController makes HTTP requests to an API. See also the HTTPEmulator for testing locally. 

| Parameter    | Definition |
| -------- | ------- |
| url  | String for the base url all other calls will be subpaths for   |


Sample configuration:

```
{
	"name": "API1",
	"type": "HTTP",
	"parameters": {
		"url": "http:/127.0.0.1:80"
	}
}
```

The INTERSECT Controller communicates with an INTERSECT protocol message bus. It can respond to events or messages or send messages. The ability to respond to messages is only available when provided to an IntersectAgent, with messages to listen to set in the IngersectAgent's "service_mappings". 

| Parameter    | Definition |
| -------- | ------- |
| intersect_configuration  | Dictionary of INTERSECT authentication credentials, as found in an INTERSECT configuration file. See INTERSECT documentation for full details.   |


Sample configuration:

```
{
	"name": "INTERSECT",
	"type": "INTERSECT",
	"parameters": {
		"intersect_configuration": {
		    "data_stores": {
		    },
		    "brokers": [
		        {
		            "host": "100.101.102.103",
		            "username": "intersect_username",
		            "password": "intersect_password",
		            "port": 1883,
		            "protocol": "mqtt3.1.1"
		        }
		    ]
		}
	}
}
```


### Data Stores

A Data Store manages all external communication with some method of storing data for the Strategy. Common operations for a Data Store include saving or retrieving data. Data Stores have the functions:

copy(id, input): Copy the object input into the data store, under bucket id.
copy_file(id, input): Read the file input and copy its contents into the data store, under bucket id.
get_ids(): Get all the top level buckets inside the data store.
get_names(id): Get the names of all individual data sets inside bucket id.
get_visualization_type(): Get the default visualization type for this data store. Will be one of:
    DATAFRAME: load() can be counted on to return data in a format which can be converted into a 
    	dataframe. Visualization will be a graph with the x axis being a timestamp column and all
        numerical columns plottable on the y axis.
    FILES: load() will return the contents of an arbitrary file, which might be csv, an image, text, etc.
    NONE: This data store does not fit any of the other defined categories.
load(id, name, num_items): Load the data inside bucket id. If num_items is specified, retrieve at most that many data
	sets. If name is specified, only retrieve the one data set of the name. The returned format will be described by
	get_visualization_type().
load_to_file(id, name, path): Copy the data located under bucket id with name name from the data store to a file located at path.
save(id, input): Copy the file input into the data store, under bucket id, then delete the file. 

The File System Data Store saves and retrieves data to a local file system. The data id is the folder name, while the data name is the file name within that directory.

| Parameter    | Definition |
| -------- | ------- |
| path  | String path where data will be saved   |

Sample configuration:

```
{
	"name": "LocalStorage",
	"type": "File System",
	"parameters": {
		"path": "/var/simdata/energyplus/data"
	}
}
```

The PostgreSQL Data Store saves and retrieves data to a PostgreSQL database. id is the table name, while name is a row's key.

| Parameter    | Definition |
| -------- | ------- |
| path  | String path where data will be saved   |

Sample configuration:

```
{
	"name": "Database",
	"type": "Postgres",
	"parameters": {
        "database": "mydb",
        "host": "localhost",
        "password": "password1",
        "port": "5432",
        "schema": {
            "table1": {
                "column1": "integer",
                "column2": "decimal"
            }
        },
        "user": "username"
	}
}
```

The PostgreSQL Data Store saves and retrieves data to a PostgreSQL database. id is the table name, while name is a row's key.

| Parameter    | Definition |
| -------- | ------- |
| database | String PostgreSQL internal database name  |
| host | String hostname for the server where the database is available |
| password | String password for the database |
| port | String port that the database is available on |
| schema | String Dictionary from table names to dictionaries from column names to PostgreSQL  |
| user | String username for the database |

Sample configuration:

```
{
	"name": "Database",
	"type": "Postgres",
	"parameters": {
        "database": "mydb",
        "host": "localhost",
        "password": "password1",
        "port": "5432",
        "schema": {
            "table1": {
                "column1": "integer",
                "column2": "decimal"
            }
        },
        "user": "username"
	}
}
```

### Emulators

An Emulator serves as a local instance of some type of external system, one which would be communicated with via a Controller or Data Store. They are used in scenarios when access to a real system is not available and in testing behavior without using real hardware. 

Emulators have start() and stop() functions that are called by ACTIVE to manage their states.

The BACnet Emulator is a virtual BACnet device.

| Parameter    | Definition |
| -------- | ------- |
| address  | String IP address with network mask defining where the device will be accessible from  |
| port  | Integer port number to listen on for the device  |
| deviceID  | Integer unique BACnet protocol ID for the device  |
| device_objects  | List of BACnet object definitions (see below) |

BACnet object definitions:
| Parameter    | Definition |
| -------- | ------- |
| instance | Integer for the BACnet object instance number  |
| type  | String defining the BACnet object type. Supported types are: "analog_input", "analog_output", "analog_value", "binary_input", "binary_output", "binary_value", "character_string", "date_value", "datetime_value", "humidity_input", "humidity_value", "make_state_text", "multistate_input", "multistate_output", "multistate_value", "temperature_input", "temperature_value" |
| value  | Value that the object will return when queried.  |


Sample configuration:

```
{
	"name": "Device1",
	"type": "BACnet",
	"parameters": {
		"address": "127.17.0.101/24",
		"port": 47808,
		"device_objects": [
			{
				"type": "analog_output",
				"instance": 3000023,
				"value": 89.9
			},
			{
				"type": "analog_input",
				"instance": 3000075,
				"value": 12.3
			},
			{
				"type": "analog_value",
				"instance": 3000079,
				"value": 34.5
			}		
		]
	}
},
```

The EnergyPlus API Emulator manages an EnergyPlus simulation of a building which it communicates with via the EnergyPlusAPI package.

| Parameter    | Definition |
| -------- | ------- |
| console_output  | Boolean for whether or not to print EnergyPlus logs to console. |
| energyplus_location | String path to the EnergyPlus install location, the directory where ConvertInputFormat is | 
| floor_config | Dictionary from string RTU names to lists of string zone names for zones associated with that RTU. Keys must correspond to entries in rtu_list. Values must appear in zone_list. |
| idf_file | String path to the .idf file to use during the simulation. |
| num_threads | Integer number of threads to use in the simulation |
| output_dir | String path for where EnergyPlus will save its output files |
| rtu_list | List of string names for RTUS in the simulation |
| variable_schema | Dictionary with form described below |
| weather_file | String path to the .epw file for the weather to use in the simulation |
| zone_list | List of string zone names in the simulation |

variable_schema is a dictionary of variables from the simulation of the following form:

```
"F_sched": { 
    "type": "output",
    "name": "Schedule Value",
    "scope": "RTU",
    "key_path": ["RTU", "fan_operation_schedule_name", "fan_schedule_name"],
},
```

Where "type" is either "output", "internal", or "actuator" and "scope" is either "Environment", "RTU", or "zone". "key_path" is omitted in the case that "scope" is "Environment".

Sample configuration: 

```
{
	"name": "EnergyPlus Simulation",
	"type": "EnergyPlus API",
	"parameters": {
		"console_output": true,
		"energyplus_location": "/usr/local/EnergyPlus-23-1-0/",
		"floor_config": {"RTU1": ["Room 101", "Room 102"]},
		"idf_file": "model.idf",
		"num_threads": 8,
		"output_dir": "active_energyplus_out",
		"rtu_list": ["RTU1"],
		"variable_schema": "!ACTIVE:!FILE-json:EnergyPlusSchema.json",
		"weather_file": "Knoxville_TMY3.epw",
		"zone_list": ["Room 101", "Room 102"]
	}
}
```

The HTTP Emulator works as a local server to handle HTTP requests. It is intended for use with the HTTP Controller.


| Parameter    | Definition |
| -------- | ------- |
| data  | Dictionary of paths and responses for the server. See emulator/http_emulator_base.py for a full description   |
| port  | Integer port for the server to listen on   |

Sample configuration:

```
{
	"name": "DataLogger1",
	"type": "HTTP",
	"parameters": {
		"port": 8008,
		"data": {
	        "/path" : [
	            {
	                "content-type": "application/json",
	                "data": {
	                    "my_value": "Content for /path?param1=foo",
	                    "value": "Content for /path?param1=foo"
	                },
	                "query parameters": {
	                    "param1": "foo"
	                }
	            },
	            {
	                "content-type": "application/json",
	                "data": {
	                    "value": "Default content for /path when param1 is not defined or =/= foo"
	                }
	            }
	        ]
	    }            
	}
}
```

### Strategies

A Strategy is a piece of control logic set to be run by an Agent and using Controller and/or Data Stores. For example, a Strategy for controlling a building might be run on an Agent, use Controllers for various devices in the building to obtain information about the building state, perform a machine learning algorithm to make control decisions, use the Controllers to modify the devices, then save the results in a database for a Data Store.

Strategies should have a step() function representing the passing of a full episode/time step of the Strategy's operation.

No default Strategies are currently provided. Users must define Strategies in an Extension.

## Testing

Environment files can have one or more tests defined. Tests are composed of a number of steps which are run sequentially. A test will halt the first time any step produces an error. Tests are defined in a list inside the tests section of an environment file.

```
"tests": [
	[
		# Test 1...
	]
]
```

In order to run tests, use

```
active test config.json
```

### Test Definition

Each test is defined by a number of sequential steps inside the environment file.

```
"tests": [
	[
		{
			// Step 1...
		},
		{
			// Step 2...
		}
	]
]
```

A step consists of one of the following actions:

A `function` step invokes a function that was registered through an [extension](#extensions). The process is similar to registering a Component, but the annotation is placed on a function definition instead of a class definition.

```
from active.testing.decorators import ActiveTestStep

@ActiveTestStep("my test")
def test():
```

The function should return a list of strings. Each error encountered during the test should be noted by a descriptive string in the list that explains the nature of the problem. An empty list represents a passing test. 

The step is defined via

```
{
	"action": "function",
	"type": "my test",
	"parameters": {
	
	}
}
```

where `type` must equal the name registered with `@ActiveTestStep("type")`. Parameters are given to the function as keyword arguments exactly as they are for Components.

A `start` step starts an Emulator or Agent.

```
{
	"action": "start",
	"component": "my emulator"
}
```

where `component` must equal the `name` of an Emulator or Agent.

A `stop` step stops an Emulator or Agent.

```
{
	"action": "stop",
	"component": "my emulator"
}
```

where `component` must equal the `name` of an Emulator or Agent.

A `wait` step simply waits the requested number of seconds before proceeding to the next step.

```
{
	"action": "wait",
	"seconds": 10
}
```

### Default Test Steps

Controllers have default Test Steps available. They are configurable to run any value getting functions for the Controller, optionally with a range of acceptable values to test for.

The **Clock Controller Value Check** is the default test for ClockControllers.

| Parameter    | Definition |
| -------- | ------- |
| controller  | ClockController to be tested   |
| skip  | List of string parameters (get_foo() functions on controller) to not test.   |
| values  | Dictionary from string parameters to a dictionary of, optionally, "min" or "max" values for the parameter  |

```
{
	"action": "function",
	"type": "Clock Controller Value Check",
	"parameters": {
		"controller": "!ACTIVE:my_clock_controller,
		"skip": [],
		"values": {}
	}
}
```

The **RTU Controller Value Check** is the default test for RTUControllers.

| Parameter    | Definition |
| -------- | ------- |
| controller  | RTUController to be tested   |
| skip  | List of string parameters (get_foo() functions on controller) to not test.   |
| values  | Dictionary from string parameters to a dictionary of, optionally, "min" or "max" values for the parameter  |

```
{
	"action": "function",
	"type": "RTU Controller Value Check",
	"parameters": {
		"controller": "!ACTIVE:my_rtu_controller,
		"skip": [],
		"values": {
	        "cooling_coil_electricity_rate": {
	        	"min": 0,
	        	"max": 100
	        },
	        "cooling_coil_inlet_temperature": {},
	        "fan_electricity_rate": {},
	        "fan_schedule": {},
	        "heating_coil_electricity_rate": {},
	        "heating_coil_outlet_temperature": {},
	        "heating_coil_set_point": {},
	        "outdoor_air_temperature": {},
	        "actuator_temperature": {},
	        "actuator_inlet_mass_flow_rate": {},
	        "cooling_load": {},
	        "cooling_set_point": {},
	        "enthalpy": {},
	        "fan_electricity_rate": {},
	        "floor_area": {},
	        "floor_volume": {},
	        "heating_load": {},
	        "heating_set_point": {},
	        "humidity": {},
	        "inlet_density": {},
	        "inlet_enthalpy": {},
	        "inlet_humidity": {},
	        "inlet_specific_heat": {},
	        "inlet_temperature": {},
	        "relative_humidity": {},
	        "supply_airflow_rate": {},
	        "temperature": {}
		}
	}
}
```

## ACTIVE Workbench

The ACTIVE Workbench is ACTIVE's built in GUI. It serves files from each Data Store in the Environment, according to the get_visualization_type() returned by the Data Store. Each bucket id will be user-selectable and will display each data set name under that bucket to download. DATAFRAME types will be additionally be displayed as a graph. FILES types will be displayed according to type, with .csvs being displayed as tables.

## Development

### Running in Docker

To build a test container:

```
build -t active  .
build run -it --rm --name=active active bash
./start-volttron.sh
source /home/volttron/volttron/env/bin/activate
pip3 install /active-0.0.1-py3-none-any.whl
active start config.json
```

You may ignore the ./start-volttron.sh line if not testing with a VOLTTRON agent.
