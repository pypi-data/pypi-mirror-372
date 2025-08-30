import datetime
import json
import time

from pathlib import Path
from subprocess import Popen, PIPE

from active.emulator.energyplusapi_emulator_state import EnergyPlusAPIEmulatorState

from pyenergyplus.api import EnergyPlusAPI

class EnergyPlusAPIEmulatorBase():
    '''
    Base class for the Emulator for running an EnergyPlus simulation and communicating with it through the EnergyPlusAPI.
    '''
    
    ########################################
    # These variables exist at the class level so that they can be accessed inside the time step handler functions, whose 
    # prototypes cannot be changed in order to maintain compatibility with pyenergyplus's API. 

    # State for the currently running emulator. 
    state = EnergyPlusAPIEmulatorState()
    ######################################## 
    
    def __init__(self, console_output=False, energyplus_location="", floor_config={}, idf_file="", num_threads=1,
                 output_dir="active_energyplus_out", rtu_list={}, variable_schema = {}, weather_file="", zone_list={}):
        '''
        The default constructor
        
        Args:
            console_output: Boolean flag for whether or not to output EnergyPlus logs to the console.
            energyplus_location: String for the location of EnergyPlus, the directory where ConvertInputFormat exists.
            floor_config: Dictionary from string RTU names to lists of string zone names associated with that RTU.
            idf_file: String path to the idf file to run in the simulation.
            num_threads: Integer number of threads to use in the simulation
            output_dir: String path to the folder to save EnergyPlus output files.
            rtu_list: List of strings of RTU names.
            variable_schema:  Dictionary of all RTU and VAV variables read from or written to EP. Example: 
                EnergyPlusAPI().exchange.get_variable_handle(state, "Zone Air Temperature", "Room 203")
            weather_file: String path to the .epw weather file for the simulation.
            zone_list: List of string names for zones.
        '''

        # Initialize variables        
        EnergyPlusAPIEmulatorBase.state.console_output = console_output
        EnergyPlusAPIEmulatorBase.state.floor_config = floor_config
        EnergyPlusAPIEmulatorBase.state.idf_file = idf_file
        EnergyPlusAPIEmulatorBase.state.num_threads = num_threads
        EnergyPlusAPIEmulatorBase.state.RTU_list = rtu_list
        EnergyPlusAPIEmulatorBase.state.variable_schema = variable_schema
        EnergyPlusAPIEmulatorBase.state.weather_file = weather_file
        EnergyPlusAPIEmulatorBase.state.zone_list = zone_list
        
        # Create the output directory if it doesn't exist
        EnergyPlusAPIEmulatorBase.state.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Ensure path ends with /
        if not energyplus_location.endswith("/"):
            energyplus_location = energyplus_location + "/"
        
        # Create an epjson file from the idf file
        epjson_process = Popen([energyplus_location + "ConvertInputFormat", idf_file], stdout=PIPE)
        epjson_process.communicate()
        epjson_file = idf_file[:-3] + "epJSON"
        
        # Parse the epjson file
        EnergyPlusAPIEmulatorBase.state.building_model_config, _ = self._parse_model_epjson(epjson_file, floor_config, 
                                                                                            rtu_list, zone_list)
        
        # Delete the epjson file
        Path(epjson_file).unlink()
        
        # Start EnergyPlus
        EnergyPlusAPIEmulatorBase.state.api = EnergyPlusAPI()
        EnergyPlusAPIEmulatorBase.state.state_id = EnergyPlusAPIEmulatorBase.state.api.state_manager.new_state() 
        EnergyPlusAPIEmulatorBase.state.psychrometrics = self._functional_psychrometrics()
        
        # Set EnergyPlus's console output
        EnergyPlusAPIEmulatorBase.state.api.runtime.set_console_output_status(EnergyPlusAPIEmulatorBase.state.state_id, 
                                                                              EnergyPlusAPIEmulatorBase.state.console_output)
        
    def env_ready(self, for_data_logging=False) -> bool:
        '''
        Check if the environment is ready for simulation.
        
        Args:
            for_data_logging: Boolean flag for whether to additionally check for the warmup flag.
        Returns:
            True if the simulation is ready (and also if the warmup flag is set if for_data_logging was True) or False
                otherwise
        '''
        if not EnergyPlusAPIEmulatorBase.state.api.exchange.api_data_fully_ready(EnergyPlusAPIEmulatorBase.state.state_id):
            return False
        if for_data_logging:
            if EnergyPlusAPIEmulatorBase.state.api.exchange.warmup_flag(EnergyPlusAPIEmulatorBase.state.state_id):
                return False
        return True
    
    def fn_dry_bulb(self, H, W):
        '''
        EnergyPlusAPI function to calculate the air temperature in Celsius 
        as a function of air specific enthalpy [H] (Joules per kilogram) 
        and humidity ratio [W] (kilograms of water per kilogram of dry air).

        - in EnergyPlusAPI: `EnergyPlusAPI().functional.psychrometrics.dry_bulb()`
        - in EnergyPlusPlugin: `EnergyPlusPlugin().api.functional.psychrometrics.api.psyTdbFnHW()`
        - in BACnet: `psychrolib.GetTDryBulbFromEnthalpyAndHumRatio()`

        Reference: https://bigladdersoftware.com/epx/docs/8-7/module-developer/psychrometric-services.html

        Parameters
        ----------
        H : float
            Air specific enthalpy in Joules per kilogram.
        W : float
            Humidity ratio in kilograms of water per kilogram of dry air.
        
        Returns
        -------
        float
            Air temperature in Celsius.
        '''
        return EnergyPlusAPIEmulatorBase.state.psychrometrics.dry_bulb(EnergyPlusAPIEmulatorBase.state.state_id, H, W)
    
    def fn_enthalpy(self, Tdb, W):
        '''
        EnergyPlusAPI function to calculate the specific enthalpy of air in Joules per kilogram 
        as a function of dry bulb temperature [Tdb] (Celsius) and humidity ratio [W] 
        (kilograms of water per kilogram of dry air).

        - in EnergyPlusAPI: `EnergyPlusAPI().functional.psychrometrics.enthalpy()`
        - in EnergyPlus: `EnergyPlusAPI().functional.psychrometrics.api.psyHFnTdbW()`
        - in BACnet: `psychrolib.GetHumRatioFromRelHum()` and `psychrolib.GetMoistAirEnthalpy()`

        Reference: https://bigladdersoftware.com/epx/docs/8-7/module-developer/psychrometric-services.html

        Parameters
        ----------
        Tdb : float
            Dry bulb temperature in Celsius.
        W : float
            Humidity ratio in kilograms of water per kilogram of dry air.
        
        Returns
        -------
        float
            Specific enthalpy of air in Joules per kilogram.
        '''
        
        return EnergyPlusAPIEmulatorBase.state.psychrometrics.enthalpy(EnergyPlusAPIEmulatorBase.state.state_id, Tdb, W)
        
    def get_building_config(self):
        '''
        Getter for the building model configuration
        
        Return:
            The dictionary containing the building model configuration.
        '''
        
        return EnergyPlusAPIEmulatorBase.state.building_model_config
    
    def get_variable_handle(self, component_type=None):
        
        if component_type:
            h = EnergyPlusAPIEmulatorBase.state.api.exchange.get_actuator_handle(
                state=EnergyPlusAPIEmulatorBase.state.state_id,
                component_type=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['unit'],
                control_type=component_type,
                actuator_key=ep_key
            )            
        else:
            h = EnergyPlusAPIEmulatorBase.state.api.exchange.get_variable_handle(
                state=EnergyPlusAPIEmulatorBase.state.state_id,
                variable_name=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name'],
                variable_key=ep_key
            )
        if h == -1:
            raise ValueError(f"Failed to create output variable handle for var_name: {var_name}, name: {EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name']}, ep_key: {ep_key}")

        return h
        
    def launch(self, 
        ) -> None:
        '''
        Launch a new EnergyPlus simulation.
        '''
        self._request_output_variables()
        
        EnergyPlusAPIEmulatorBase.state.api.runtime.run_energyplus(EnergyPlusAPIEmulatorBase.state.state_id, [
            '--output-directory', EnergyPlusAPIEmulatorBase.state.output_dir,
            '-w', EnergyPlusAPIEmulatorBase.state.weather_file,
            '-j', str(EnergyPlusAPIEmulatorBase.state.num_threads),
            EnergyPlusAPIEmulatorBase.state.idf_file
        ])
        
        self._reset_state()
        
    def read_var(self,  var_name, key):
        '''
        Get the value of a variable from the EnergyPlus simulation.
        If a variable handle is not registered, register it first.

        Parameters
        ----------
        var_name : str
            The name of the variable defined in VAVBox or RTU class to get.
        key : str
            The key is RTU/VAV name.

        Returns
        -------
        float
            The value of the variable.
        '''
        ep_key = self._ep_key(var_name, key)
        if (var_name, ep_key) not in EnergyPlusAPIEmulatorBase.state.variable_handles:
            self._check_var(var_name)
            self._register_variable(var_name, ep_key)

        if EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'output':
            return EnergyPlusAPIEmulatorBase.state.api.exchange.get_variable_value(EnergyPlusAPIEmulatorBase.state.state_id, EnergyPlusAPIEmulatorBase.state.variable_handles[(var_name, ep_key)])
        elif EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'internal':
            return EnergyPlusAPIEmulatorBase.state.api.exchange.get_internal_variable_value(EnergyPlusAPIEmulatorBase.state.state_id, EnergyPlusAPIEmulatorBase.state.variable_handles[(var_name, ep_key)])
        elif EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'actuator':
            return EnergyPlusAPIEmulatorBase.state.api.exchange.get_actuator_value(EnergyPlusAPIEmulatorBase.state.state_id, EnergyPlusAPIEmulatorBase.state.variable_handles[(var_name, ep_key)])
        
        raise ValueError(f"Unknown control variable : {var_name}, key {key}, ep_key {ep_key}. Not supposed to happen.")
        
    def set_begin_system_timestep_before_predictor_handler(self, handler):
        '''
        Set the handler for callback_begin_system_timestep_before_predictor in EnergyPlus
        
        Args:
            handler: The Callable handler to register 
        '''
    
        EnergyPlusAPIEmulatorBase.state.api.runtime.callback_begin_system_timestep_before_predictor(EnergyPlusAPIEmulatorBase.state.state_id, handler) 
        
    def set_control_action(self, var_name, key, value):
        '''
        Set the value of a control action to the EnergyPlus simulation.
        If a variable handle is not registered, register it first.

        Parameters
        ----------
        var_name : str
            The name of the variable defined in VAVBox or RTU class to set.
        key : str
            The key is RTU/VAV name.
        value : float
            The value to set for the variable.
        '''
        ep_key = self._ep_key(var_name, key)
        if (var_name, ep_key) not in EnergyPlusAPIEmulatorBase.state.variable_handles:
            self._check_var(var_name)
            self._register_variable(var_name, ep_key)
        
        if EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'actuator':
            EnergyPlusAPIEmulatorBase.state.api.exchange.set_actuator_value(EnergyPlusAPIEmulatorBase.state.state_id, EnergyPlusAPIEmulatorBase.state.variable_handles[(var_name, ep_key)], value)
        else:
            raise ValueError(f"Unknown control variable : {var_name}, key {key}, ep_key {ep_key}. Not supposed to happen.")
        
    def set_inside_system_iteration_loop_handler(self, handler):
        '''
        Set the handler for callback_inside_system_iteration_loop in EnergyPlus
        
        Args:
            handler: The Callable handler to register 
        '''
        
        EnergyPlusAPIEmulatorBase.state.api.runtime.callback_inside_system_iteration_loop(EnergyPlusAPIEmulatorBase.state.state_id, handler)
        
    def start(self):
        '''
        Start the simulation
        '''
        
        # Setup needs to happen in the constructor, while the simulation shouldn't be launched until the Agent has had time
        # to register handlers.
        pass

    
    def stop(self):
        '''
        Stop EnergyPlus
        '''
        
        # TODO
        pass
    
    def timestamp(self):
        '''
        Get the current timestamp in timesteps in the simulation.

        Returns
        -------
        tuple
            The timestamp in the format (year, month, day, hour, minute).
        '''
        y = EnergyPlusAPIEmulatorBase.state.api.exchange.year(EnergyPlusAPIEmulatorBase.state.state_id)
        m = EnergyPlusAPIEmulatorBase.state.api.exchange.month(EnergyPlusAPIEmulatorBase.state.state_id)
        d = EnergyPlusAPIEmulatorBase.state.api.exchange.day_of_month(EnergyPlusAPIEmulatorBase.state.state_id)
        h = EnergyPlusAPIEmulatorBase.state.api.exchange.hour(EnergyPlusAPIEmulatorBase.state.state_id)
        min = EnergyPlusAPIEmulatorBase.state.api.exchange.minutes(EnergyPlusAPIEmulatorBase.state.state_id) - 1 # EnergyPlus starts from 1 minute
        
        return datetime.datetime(y, m, d, hour=h, minute=min)
    
    def _check_var(self, var_name):
        '''
        Check if the variable is defined in the schema.

        Parameters
        ----------
        var_name : str
            The name of the variable defined in VAVBox or RTU class to get.
        
        Returns
        -------
        bool
            True if the variable is defined in the schema, False otherwise.
        '''
        if var_name not in EnergyPlusAPIEmulatorBase.state.variable_schema:
            raise ValueError(f"Unknown variable name: {var_name}")
        if not EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] in ['output', 'internal', 'actuator']:
            raise ValueError(f"Unknown variable type: {var_name}")
        if not self.env_ready():
            return False
        return True
    
    def _ep_key(self, var_name: str, key: str) -> str:
        '''
        Given RTU/Zone name key, return the EnergyPlusAPI simulation key for variable retrieval.

        Parameters
        ----------
        var_name: str
            The variable name defined in the variable schema.
        key : str
            The RTU/Zone name key.

        Returns
        -------
        str
            The EnergyPlusAPI simulation key.
        '''
        if (var_name, key) in EnergyPlusAPIEmulatorBase.state._ep_key_map: # speed up ep_key lookup
            return EnergyPlusAPIEmulatorBase.state._ep_key_map[(var_name, key)]

        ep_key = None
        v_schema = EnergyPlusAPIEmulatorBase.state.variable_schema
        if var_name not in v_schema:
            raise ValueError(f"Unknown variable name in building config: {var_name}")
        if 'key_path' not in v_schema[var_name]: # this is the case for Environment scope
            ep_key = v_schema[var_name]['scope'] # the scope name is then the key
        elif len(v_schema[var_name]['key_path']) == 1 and v_schema[var_name]['key_path'][0] == v_schema[var_name]['scope']:
            ep_key = key # the EP key is the key itself
        else: # follow key_path to get the ep_key
            config = EnergyPlusAPIEmulatorBase.state.building_model_config['zone_config']
            if v_schema[var_name]['scope'] == 'RTU':
                config = EnergyPlusAPIEmulatorBase.state.building_model_config['RTU_config']
            # replace the first element of the key_path with the key
            k = key
            d = config[k] # the 1st element of the key_path must be 'zone' or 'RTU'
            for p in v_schema[var_name]['key_path'][1:]:
                k = d[p]
                d = d[p]
            ep_key = k
            
        EnergyPlusAPIEmulatorBase.state._ep_key_map[(var_name, key)] = ep_key # cache the ep_key
        return ep_key
    
    def _functional_psychrometrics(self):
        '''
        Return an instance of EP function API's psychrometrics function class. One per state.
        '''
        
        return EnergyPlusAPIEmulatorBase.state.api.functional.psychrometrics(EnergyPlusAPIEmulatorBase.state.state_id)
        
    def _parse_model_epjson(self, f_in, floor_config, rtu_list, zone_list):
        '''
        Parse the EnergyPlus model in EPJSON format and extract RTU, Zone and other information.
        The `user_config` is a dictionary to specify a subset of RTUs and zones of user interest.
        The format of `user_config` is like:
        {
            "RTU_list": ["RTU-1", "RTU-2"],
            "zone_list": ["Room 101", "Room 102", "Zone 201", "Zone 202"],
            "floor_config": {
                "RTU-1": ["Room 101", "Room 102"],
                "RTU-2": ["Zone 201", "Zone 202"]
            }
        }
    
        Parameters
        ----------
        f_in : str
            The path to the EPJSON file.
        user_config : dict, optional
            The user configuration to specify the subset of RTUs and zones of interest.
        '''
        with open(f_in, 'r') as f:
            epin = json.load(f)
    
        # filter RTUs based on user_config
        rtus = list(epin['AirLoopHVAC'].keys())
        print('full RTU list:', rtus)
        user_defined_rtus = []
        if rtu_list is not None and rtu_list:
            for r in rtu_list:
                if r not in rtus:
                    print('WARNING: user defined RTU not found in model config:', r, '. Ignored.')
                else:
                    user_defined_rtus.append(r)
            rtus = user_defined_rtus
        print('RTUs to use:', rtus)
    
        # filter zones based on user_config
        zones = list(epin['Zone'].keys())
        print('full zone list:', zones)
        user_defined_zones = []
        if zone_list is not None and zone_list:
            for z in zone_list:
                if z not in zones:
                    print('WARNING: user defined zone not found in model config:', z, '. Ignored.')
                else:
                    user_defined_zones.append(z)
            zones = user_defined_zones # USER specify the zones to be configured
        print('zones to use:', zones)
    
        model_config = {
            'RTU_list': rtus,
            'zone_list': zones,
            'floor_config': {} if floor_config is None or not floor_config else floor_config,
            'zone_config': {},
            'RTU_config': {}
        }
    
        vav_names = {}
        # vav_python_class_paths = {} # we no longer use EnergyPlusPlugin
        for zone in zones:
            # ATU name --> VAV name
            atu_name = None
            for atu in epin['ZoneHVAC:AirDistributionUnit'].keys():
                if atu.startswith(zone):
                    if atu_name is not None:
                        print('ERROR: multiple ATUs found for zone:', zone, '. Unhandled, using the first match:', atu_name)
                    else:
                        atu_name = atu
            if atu_name is None:
                print('ATU not found for zone:', zone)
                continue
            vav_name = epin['ZoneHVAC:AirDistributionUnit'][atu_name]['air_terminal_name']
            vav_names[zone] = vav_name
            model_config['zone_config'][zone] = {
                'ATU_name': atu_name,
                'VAV_name': vav_name
            }
            # # if VAV object is user defined, find the python class name
            # if epin['ZoneHVAC:AirDistributionUnit'][atu_name]["air_terminal_object_type"] == "AirTerminal:SingleDuct:UserDefined":
            #     # get calling manager name
            #     calling_manager = epin["AirTerminal:SingleDuct:UserDefined"][vav_name]["overall_model_simulation_program_calling_manager_name"]
            #     # get python class name
            #     # TODO: we only support user defined VAV control using python plugin, what if it's not python plugin?
            #     python_config = epin["PythonPlugin:Instance"][calling_manager]
            #     python_class_path = python_config["python_module_name"] + "." + python_config["plugin_class_name"]
            #     vav_python_class_paths[zone] = python_class_path
    
        model_config['vav_names'] = vav_names
        # print("vav_python_class_paths:", vav_python_class_paths)
    
        heating_setpoint_schedule_names = {}
        cooling_setpoint_schedule_names = {}
        for zone in zones:
            thermo = zone + ' Thermostat'
            thermo_sp = epin['ZoneControl:Thermostat'][thermo]['control_1_object_type']
            thermo_control_name = epin['ZoneControl:Thermostat'][thermo]['control_1_name']
            heating_setpoint_schedule_names[zone] = epin[thermo_sp][thermo_control_name]['heating_setpoint_temperature_schedule_name']
            cooling_setpoint_schedule_names[zone] = epin[thermo_sp][thermo_control_name]['cooling_setpoint_temperature_schedule_name']
            model_config['zone_config'][zone]['heating_setpoint_schedule_name'] = heating_setpoint_schedule_names[zone]
            model_config['zone_config'][zone]['cooling_setpoint_schedule_name'] = cooling_setpoint_schedule_names[zone]
        model_config['heating_setpoint_schedule_names'] = heating_setpoint_schedule_names
        model_config['cooling_setpoint_schedule_names'] = cooling_setpoint_schedule_names
        
    
        # print("heating_setpoint_schedule_names:")
        # print(heating_setpoint_schedule_names)
        # print("cooling_setpoint_schedule_names:")
        # print(cooling_setpoint_schedule_names)
    
        fan_operation_schedule_names = {}
        heating_node_names = {}
        cooling_node_names = {}
        for branch in epin['Branch'].keys():
            which_rtu = None
            for rtu_name in rtus:
                if branch.startswith(rtu_name):
                    if which_rtu is not None:
                        print('ERROR: multiple RTUs found in branch:', branch, '. Unhandled, using the first matched RTU:', which_rtu)
                    else:
                        which_rtu = rtu_name
            if which_rtu is None:
                print("INFO: branch not associated with any RTU:", branch)
                continue
            model_config['RTU_config'][which_rtu] = {}
            for comp in epin['Branch'][branch]['components']:
                if comp['component_object_type'] == 'Fan:VariableVolume':
                    fan_name = comp['component_name']
                    fan_operation_schedule_names[which_rtu] = {'fan_name': fan_name, 'fan_schedule_name': epin['Fan:VariableVolume'][fan_name]['availability_schedule_name']}
                    model_config['RTU_config'][which_rtu]['fan_operation_schedule_name'] = fan_operation_schedule_names[which_rtu]
                if comp['component_object_type'] == 'CoilSystem:Cooling:DX':
                    comp_name = comp['component_name'] # this is cooling system name, not cooling coil name
                    cooling_node_names[which_rtu] = {
                        'component_name': comp_name,
                        'cooling_coil_name': epin["CoilSystem:Cooling:DX"][comp_name]['cooling_coil_name'],
                        'node_name': comp['component_outlet_node_name'],
                        'inlet_node_name': comp['component_inlet_node_name'],
                    }
                    model_config['RTU_config'][which_rtu]['cooling_node_name'] = cooling_node_names[which_rtu]
                if comp['component_object_type'] == 'Coil:Heating:Fuel':
                    comp_name = comp['component_name']
                    heating_node_names[which_rtu] = {
                        'component_name': comp_name,
                        'node_name': comp['component_outlet_node_name']
                    }
                    model_config['RTU_config'][which_rtu]['heating_node_name'] = heating_node_names[which_rtu]
    
        # print("fan_operation_schedule_names:")
        # print(fan_operation_schedule_names)
        # print("heating_node_names")
        # print(heating_node_names)
        # print("cooling_node_names")
        # print(cooling_node_names)
    
        return model_config, epin
    
    
    def _register_variable(self, var_name, ep_key):
        '''
        Register a variable handle using EnergyPlusAPI.

        Parameters
        ----------
        var_name : str
            The name of the variable defined in VAVBox or RTU class.
        ep_key: str
            The key is RTU/VAV name or system node names obtained from parsing the epJSON file.
        '''
        h = -1
        if EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'output':
            h = EnergyPlusAPIEmulatorBase.state.api.exchange.get_variable_handle(
                state=EnergyPlusAPIEmulatorBase.state.state_id,
                variable_name=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name'],
                variable_key=ep_key
            )
            if h == -1:
                raise ValueError(f"Failed to create output variable handle for var_name: {var_name}, name: {EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name']}, ep_key: {ep_key}")
        elif EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'internal':
            h = EnergyPlusAPIEmulatorBase.state.api.exchange.get_internal_variable_handle(
                state=EnergyPlusAPIEmulatorBase.state.state_id,
                variable_type=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name'],
                variable_key=ep_key
            )
            if h == -1: # handle not found, create it
                raise ValueError(f"Internal variable handle not found for var_name: {var_name}, name: {EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name']}, ep_key: {ep_key}")
        elif EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'actuator':
            h = EnergyPlusAPIEmulatorBase.state.api.exchange.get_actuator_handle(
                state=EnergyPlusAPIEmulatorBase.state.state_id,
                component_type=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['unit'],
                control_type=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name'],
                actuator_key=ep_key
            )
            if h == -1: # handle not found, create it
                raise ValueError(f"Actuator variable handle not found for var_name: {var_name}, name: {EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name']}, ep_key: {ep_key}")
        else:
            raise ValueError(f"Unknown variable name: {var_name} with ep_key {ep_key}")
        
        EnergyPlusAPIEmulatorBase.state.variable_handles[(var_name, ep_key)] = h
        
    def _request_output_variables(self):
        '''
        Request all output variables for a EnergyPlus simulation.
        **Important**: this must be called before running the EnergyPlus simulation.

        Using this function, we no longer require output variables to be defined in the IDF file.
        '''
        vars_requested = set()
        for var_name in EnergyPlusAPIEmulatorBase.state.variable_schema.keys():
            if EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['type'] == 'output':
                u_list = None
                if EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['scope'] == 'zone':
                    u_list = EnergyPlusAPIEmulatorBase.state.building_model_config['zone_list']
                elif EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['scope'] == 'RTU':
                    u_list = EnergyPlusAPIEmulatorBase.state.building_model_config['RTU_list']
                elif EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['scope'] == 'Environment':
                    u_list = ['Environment']
                for key in u_list:
                    ep_key = self._ep_key(var_name, key)
                    if (var_name, ep_key) not in vars_requested: # avoid duplicate requests
                        EnergyPlusAPIEmulatorBase.state.api.exchange.request_variable(state=EnergyPlusAPIEmulatorBase.state.state_id, 
                            variable_name=EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name'], 
                            variable_key=ep_key)
                        print(f"INFO: Requested output variable: {var_name}, name: {EnergyPlusAPIEmulatorBase.state.variable_schema[var_name]['name']}, key: {ep_key}, by unit: {key}")
                        vars_requested.add((var_name, ep_key))
                        
    def _reset_state(self):
        '''
        Reset the state of the EnergyPlus simulation. 
        On Linux deployment, this is done by deleting the state and creating a new one.
        '''
        EnergyPlusAPIEmulatorBase.state.api.state_manager.delete_state(state=EnergyPlusAPIEmulatorBase.state.state_id)
        EnergyPlusAPIEmulatorBase.state.state_id = EnergyPlusAPIEmulatorBase.state.api.state_manager.new_state()
        EnergyPlusAPIEmulatorBase.state.psychrometrics = self._functional_psychrometrics()

        EnergyPlusAPIEmulatorBase.state.variable_handles = {} # with a new state, all variable handles are invalid
            