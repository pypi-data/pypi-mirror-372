from pyenergyplus.api import EnergyPlusAPI

class EnergyPlusControllerBase():
    '''
   Base class for the Controller for simulation using EnergyPlus.
    
    Parameters:
        api: The EnergyPlusAPI to invoke the local EnergyPlus installation.
    '''
    
    def __init__(self, console_out=False):
        '''
        Default constructor.
        
        Args:
            console_out: Boolean flag for whether to output EnergyPlus logs to console during simulation.
        '''
        
        self.console_out = console_out
        self.api = EnergyPlusAPI()
        
    def get_cooling_coil_electricity_rate(self, state):
        '''
        Get the cooling coil electricity rate.
        
        Args:
            state: Current agent's StrategyState.
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, "Cooling Coil Electricity Rate", "ROOFTOP COOLING COIL")
        
    def get_enthalpy(self, state, argument1, argument2):
        '''
        Get enthalpy.
        
        Args:
            state: Current agent's StrategyState
            argument1: 
            argument2: 
        Returns:
            ???
        '''
        
        enthalpy_calc = self.api.functional.psychrometrics(state.state_id)
        return enthalpy_calc.enthalpy(state.state_id,argument1,argument2)
    
    def get_enthalpy_drybulb(self, state, argument1, argument2):
        '''
        Get enthalpy drybulb.
        
        Args:
            state: Current agent's StrategyState
            argument1: 
            argument2: 
        Returns:
            ???
        '''
        
        enthalpy_calc = self.api.functional.psychrometrics(state.state_id)
        return enthalpy_calc.dry_bulb(state.state_id, argument1, argument2)
    
    def get_fan_electricity_rate(self, state):
        '''
        Get the fan electricity rate
        
        Args:
            state: Current agent's StrategyState
        Returns:
            ???
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, "Cooling Coil Electricity Rate", "ROOFTOP COOLING COIL")
        
    def get_internal_variable_value(self, state, argument):    
        '''
        Get ???
        
        Args:
            state: Current agent's StrategyState
            argument: 
        Returns:
            ???
        '''
        
        return self.api.exchange.get_internal_variable_value(state.state_id, argument)
        
    def get_inlet_density_for_primary_air_connection(self, state, zone):
        '''
        Get the inlet density for primary air connection.
        
        Args:
            state: Current agent's StrategyState
            zone: String name of zone
        Returns:
            ???
        '''
        
        return self.api.exchange.get_internal_variable_handle(state.state_id, "Inlet Density for Primary Air Connection", f"Room {zone} VAV Reheat")
        
    def get_inlet_mass_flow_rate(self, state, zone):
        '''
        Get inlet mass flow rate
        
        Args:
            state: Current agent's StrategyState
            zone: String name of zone
        Returns:
            ???
        '''
        
        return self.api.exchange.get_actuator_handle(state.state_id, "Primary Air Connection", "Inlet Mass Flow Rate", f"Room {zone} VAV Reheat")
        
    def get_inlet_temperature_for_primary_air_connection(self, state, zone):
        '''
        Get inlet temperature for primary air connection.
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of zone.
        '''
        
        return self.api.exchange.get_internal_variable_handle(state.state_id,"Inlet Temperature for Primary Air Connection", f"Room {zone} VAV Reheat")
        
    def get_outlet_mass_flow_rate(self, state, zone):
        '''
        Get outlet mass flow rate
        
        Args:
            state: Current agent's StrategyState
            zone: String name of zone
        Returns:
            ???
        '''
        
        return self.api.exchange.get_actuator_handle(state.state_id, "Primary Air Connection", "Outlet Mass Flow Rate", f"Room {zone} VAV Reheat")
        
    def get_outlet_temperature(self, state, zone):
        '''
        Get the outlet temperature.
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of zone
        Returns:
            ???
        '''
        
        return self.api.exchange.get_actuator_handle(state.state_id, "Primary Air Connection", "Outlet Temperature", f"Room {zone} VAV Reheat")
        
    def get_qdot_reheatcoil(self, state, zone):
        '''
        Get qdot reheat coil
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of zone.
        Returns:
            ???
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, "PythonPlugin:OutputVariable", f'Qdot_reheatcoil_{zone}')
        
    def get_remaining_sensible_load_to_cooling_setpoint(self, state, zone):
        '''
        Get remaining sensible load to cooling setpoint. 
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of zone
        Returns:
         ???
        '''
        
        return self.api.exchange.get_internal_variable_handle(state.state_id,"Remaining Sensible Load to Cooling Setpoint", f"Room {zone} VAV Reheat")

    def get_remaining_sensible_load_to_heating_setpoint(self, state, zone):
        '''
        Get remaining sensible load to heating setpoint. 
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of zone
        Returns:
         ???
        '''
        
        return self.api.exchange.get_internal_variable_handle(state.state_id, "Remaining Sensible Load to Heating Setpoint", f"Room {zone} VAV Reheat")
    
    def get_rooftop_cooling_coil_outlet(self, state):
        '''
        Get the rooftop cooling coil output.
        
        Args:
            state: Current agent's StrategyState
        Returns:
            ???
        '''
        
        return self.api.exchange.get_actuator_handle(state.state_id, component_type="System Node Setpoint", control_type="Temperature Setpoint", actuator_key="RoofTop Cooling Coil Outlet")

    def get_rooftop_heating_coil_outlet(self, state):
        '''
        Get the rooftop heating coil output.
        
        Args:
            state: Current agent's StrategyState
        Returns:
            ???
        '''
        
        return self.api.exchange.get_actuator_handle(state.state_id, component_type="System Node Setpoint", control_type="Temperature Setpoint", actuator_key="RoofTop Heating Coil Outlet")
    
    def get_site_outdoor_air_drybulb_temperature(self, state):
        '''
        Get the site outdoor air dry temperature.
        
        Args:
            state: Current agent's StrategyState.
        Returns:
            ???
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, u"SITE OUTDOOR AIR DRYBULB TEMPERATURE", u"ENVIRONMENT")

    def get_variable_value(self, state, argument):
        '''
        Get ???
        
        Args:
            state: Current agent's StrategyState
            argument: 
        Returns:
            ???
        '''
        
        return self.api.exchange.get_variable_value(state.state_id, argument)
    
    def get_warmup_flag(self, state):
        '''
        Get the warmup flag.
        
        Args:
            state: Current agent's StrategyState
        Returns:
            ???
        '''
        
        return self.api.exchange.warmup_flag(state.state_id)

    def get_zone_air_relative_humidity(self, state, zone):    
        '''
        Get the zone air relative humidity.
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of the zone.
        Returns:
            ???
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, "Zone Air Relative Humidity", f'Room {zone}')
        
    def get_zone_air_temperature(self, state, zone):    
        '''
        Get the zone air temperature.
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of the zone.
        Returns:
            ???
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, "Zone Air Temperature", f'Room {zone}')
    
    def get_zone_air_humidity_ratio(self, state, zone):
        '''
        Get the zone air humidity ratio.
        
        Args:
            state: Current agent's StrategyState.
            zone: String name of the zone.
        '''
        
        return self.api.exchange.get_variable_handle(state.state_id, "Zone Air Humidity Ratio", f"Room {zone}")
    
    def is_ready(self, state):
        '''''
        Get whether the API is ready
        
        Args:
            state: Current agent's StrategyState.
        Returns:
            Boolean True if the API is ready. False otherwise.
        '''
        
        return self.api.exchange.api_data_fully_ready(state.state_id)
    
    def set_actuator_value(self, state, argument1, argument2):
        '''
        Set the actuator value.
        
        Args:
            state: Current agent's StrategyState.
            argument1:
            argument2:
        '''

        self.api.exchange.set_actuator_value(state.state_id, argument1, argument2)
        
        
    def step(self, state, begin_system_handler, inside_system_handler, epw_file_path, idf_file_path):
        '''
        Advance the simulation a step.
        
        Args:
            state: StrategyState with the current agent's state information
            begin_system_handler: Callable with a single state_id argument, to be invoked by EnergyPlus as the callback for
                "begin_system_timestep_before_predictor" and "begin_new_environment"
            inside_system_handler: Callable with a single state_id argument, to be invoked by EnergyPlus as the callback for
                "inside_system_iteration_loop"
            epw_file_path: String path to the .epw file.
            idf_file_path: String path to the .idf file.
        '''
        
        # Initialize the state on EnergyPlus if it hasn't been already
        if state.state_id == None:
            state.state_id = self.api.state_manager.new_state()
            print("state")
            print(state.state_id)
        
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 102")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 103")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 104")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 105")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 106")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 202")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 203")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 204")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 205")
        # api.exchange.request_variable(state, "Zone Air Relative Humidity", "Room 206")
        self.api.runtime.callback_begin_system_timestep_before_predictor(state.state_id, begin_system_handler)
        self.api.runtime.callback_inside_system_iteration_loop(state.state_id, inside_system_handler)
        
        self.api.runtime.set_console_output_status(state.state_id, self.console_out)

        self.api.runtime.run_energyplus(state.state_id, [
            
            '-w', epw_file_path,
            idf_file_path
            
        ])
        
        # v= api.runtime.run_energyplus(state, [
            
        #         '-w', '/Users/4ka/Knoxville_TMY3.epw',
        #         '-r', '/Users/4ka/EP_baseline.idf'
                
        #     ])
        
        # api.runtime.run_energyplus(state, [
                
        #         '-w', 'D:/Dropbox (ORNL)/Research/Sensor Impact/add_rl_sensor/Knoxville_TMY3.epw',
        #         'D:/Dropbox (ORNL)/Research/Sensor Impact/add_rl_sensor/BaselineModel/model.idf'
                
        #     ])
        #api.state_manager.reset_state(state)
        self.api.state_manager.delete_state(state.state_id)
        state.state_id = self.api.state_manager.new_state()
        self.api.runtime.callback_begin_new_environment(state.state_id, begin_system_handler)
