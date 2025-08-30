from active.controller.decorators import ActiveController
from active.controller.rtu_controller import RTUController, VAVUnit

class EnergyPlusAPIVAVUnit(VAVUnit):
    '''
    Sub-unit of the Controller which holds functions related to only one specific VAV unit.

    ACTIVE Environment file parameters prototype

    {
        "name": "RTU 1",
        "type": "EnergyPlus API RTU",
        "parameters": {
            "emulator": "!ACTIVE:MyEnergyPlusAPIEmulator",
            "name": "RTU1"
        }
    }
    
    Parameters:
        emulator: EnergyPlusAPIEmulator representing the simulation in which the virtual VAV exists.
        zone: String name for the zone this VAV occupies.
    '''
    
    def __init__(self, emulator=None, zone=""):
        '''
        Default constructor.
        
        Args:
            emulator: The EnergyPlusAPIEmulator representing the simulation in which the virtual VAV exists.
            zone: String name for the zone this VAV occupies.
        '''
        
        # Initialize parameters
        self.emulator = emulator
        self.zone = zone
    
    def get_actuator_temperature(self):
        '''
        Get the actuator outlet temperature in degrees Celsius.
        
        Returns:
            The float actuator temperature
        '''
        
        return self.emulator.read_var("T_outlet", self.zone)

    def get_actuator_inlet_mass_flow_rate(self):
        '''
        Get the actuator_inlet_mass_flow_rate in kg/s
        
        Returns:
            The float actuator inlet mass flow rate
        '''
        return self.emulator.read_var('Mdot_inlet', self.zone)    

    def get_cooling_load(self):
        '''
        Get the cooling load in W
        
        Returns:
            The float cooling load
        '''
        return self.emulator.read_var('Qdot_Req_cooling', self.zone)

    def get_cooling_set_point(self):
        '''
        Get the cooling set point in degrees Celsius.
        
        Returns:
            The float cooling set point
        '''
        return self.emulator.read_var('T_zone_cool_SP', self.zone)
    
    def get_dry_bulb(self, h):
        
        # TODO
        # Reimpliment in non-ACTIVE class
        #T_outlet_SP = max(self.v_z['T_inlet'], self.env.fn_dry_bulb(H_outlet_desired, self.v_z['W_zone']))
        #T_outlet_SP = min(T_outlet_SP, self.env.fn_dry_bulb(self.l_z['reheatcoil_cap']/Mdot_outlet_desired+self.v_z['H_inlet'], self.v_z['W_zone']))
        W_zone = self.get_humidity()
        return self.emulator.fn_dry_bulb(h, W_zone)
        
    def get_enthalpy(self, h):
        
        # TODO
        # Reimplement in non-ACTIVe class
        #???
        #return self.emulator.fn_enthalpy(self.v_z['T_zone'], self.v_z['W_zone'])
        #self.env.fn_enthalpy(self.v_z['T_inlet'], self.v_z['W_zone'])
        W_zone = self.get_humidity()
        return self.emulator.fn_enthalpy(h, W_zone)
        
    def get_floor_area(self):
        '''
        Get the floor area
        
        Returns:
            The float floor area
        '''
        return self.emulator.read_var("floor_area", self.zone)
    
    def get_floor_volume(self):
        '''
        Get the floor volume
        
        Returns:
            The float floor volume
        '''
        
        return self.emulator.read_var("floor_volume", self.zone)
    
    def get_heating_load(self):
        '''
        Get the heating load in W
        
        Returns:
            The float heating load
        '''
        
        return self.emulator.read_var('Qdot_Req_heating', self.zone)
    
    def get_heating_set_point(self):
        '''
        Get the heating set point in degrees Celsius
        
        Returns:
            The float heating set point
        '''
        
        return self.emulator.read_var('T_zone_heat_SP', self.zone)
    
    def get_humidity(self):
        '''
        Get the humidity in kg/kgDA
        
        Returns:
            The float humidity
        '''
        
        return self.emulator.read_var('W_zone', self.zone)
    
    def get_inlet_density(self):
        '''
        Get the inlet density kg/m3
        
        Return:
            The float inlet density
        '''
        
        return self.emulator.read_var("rho_inlet", self.zone)
        
    def get_inlet_enthalpy(self):
    
        T_inlet = self.get_inlet_temperature()
        W_inlet = self.get_humidity()
        return self.emulator.fn_enthalpy(T_inlet, W_inlet)
    
    # def get_inlet_enthalpy(self):
    #     '''
    #     Get the inlet enthalpy in J/kgDA
    #
    #     Return:
    #         The float inlet enthalpy
    #     '''
    #
    #     return self.emulator.read_var("T_inlet", self.zone)
    
    def get_inlet_humidity(self):
        '''
        Get the inlet humidity ratio in kg/kgDA
        
        Return:
            The float inlet humidity ratio
        '''
        
        return self.emulator.read_var("W_inlet", self.zone)
    
    def get_inlet_specific_heat(self):
        '''
        Get the inlet specific heat in J/kgK
        
        Return:
            The float inlet specific heat
        '''
        
        return self.emulator.read_var("Cp_inlet", self.zone)
    
    def get_inlet_temperature(self):
        '''
        Get the inlet temperature in degrees Celsius.
        
        Return:
            The float inlet temperature.
        '''
        
        return self.emulator.read_var("T_inlet", self.zone)
    
    def get_relative_humidity(self):
        '''
        Get the zone's relative humidity as a percentage.
        
        Return:
            The float zone relative humidity
        '''
        
        return self.emulator.read_var("RH_zone", self.zone)
    
    def get_temperature(self):
        '''
        Get the zone's temperature in degrees Celsius
        
        Return:
            The zone's temperature as a float
        '''
        
        return self.emulator.read_var("T_zone", self.zone)
    

        
    def get_zone_enthalpy(self):
    
        # T_zone = self.get_temperature()
        # W_zone = self.get_humidity()
        # return self.emulator.fn_enthalpy(T_zone, W_zone)
        T_zone = self.get_temperature()
        W_zone = self.get_humidity()
        return self.emulator.fn_enthalpy(T_zone, W_zone)
    
    # def get_zone_enthalpy(self):
    #     '''
    #     Get the zone's enthalpy in J/kgDA
    #
    #     Return:
    #         The zone's enthalpy as a float
    #     '''
    #
    #     return self.emulator.read_var("T_zone", self.zone)
    
    def is_available(self):
        
        return self.emulator.env_ready(True)
    
    def is_simulation_ready(self):
        '''
        Check whether any simulation backing the unit is ready to run.
        
        Should always be False if the unit is not available (from is_available()) even if the simulation is internally
        initialized.
        
        Return:
            True if the simulation for this unit is ready and if is_available() is true. Also True if is_available() is
            true and this device is not simulated. False otherwise. 
        '''
        
        # Always available, no simulation
        return self.emulator.env_ready(False)
    
    def set_actuator_humidity(self, value):
        '''
        Set the actuator outlet relative humidity ratio.
        
        Args:
            value: Float for the desired relative humidity ratio in kg/kgDA
        '''
        
        self.emulator.set_control_action("W_outlet", self.zone, value)
        
    def set_actuator_inlet_mass_flow_rate(self, value):
        '''
        Set the actuator inlet mass flow rate.
        
        Args:
            value: Float for the desired inlet mass flow rate in kg/s
        '''
        
        self.emulator.set_control_action("Mdot_inlet", self.zone, value)
        
    def set_actuator_outlet_mass_flow_rate(self, value):
        '''
        Set the actuator outlet mass flow rate.
        
        Args:
            value: Float for the desired inlet mass flow rate in kg/s
        '''
        
        self.emulator.set_control_action("Mdot_outlet", self.zone, value)
    
    def set_actuator_temperature(self, value):
        '''
        Set the actuator outlet temperature.
        
        Args:
            value: Float for the desired temperature in degrees Celsius.
        '''
        self.emulator.set_control_action("T_outlet", self.zone, value)


@ActiveController("EnergyPlus API RTU")
class EnergyPlusAPIRTUController(RTUController):
    '''
    A Controller for an RTU in an EnergyPlus simulation using the EnergyPlusAPI for communication.
    
    Parameters:
        building_model_config: Dictionary of building information from the Emulator.
        emulator: The EnergyPlusAPIEmulator managing the simulation in which this virtual RTU exists.
        name: String name for this RTU.
        vavs: Dictionary from string zone names to VAVUnit objects representing the VAV in that zone.
    '''
    
    def __init__(self, emulator=None, name=""):
        '''
        The default constructor.
        
        Args:
            emulator: The EnergyPlusAPIEmulator managing the simulation in which this virtual RTU exists.
            name: String name for this RTU.
        '''
        
        # Initialize parameters
        self.building_model_config = emulator.get_building_config()
        self.emulator = emulator
        self.name = name
        self.vavs = {}
        
        # Create a VAV for each zone
        for zone in self.building_model_config['zone_list']:
            self.vavs[zone] = EnergyPlusAPIVAVUnit(emulator=self.emulator, zone=zone)
        
    def get_cooling_coil_electricity_rate(self):  
        '''
        Get the cooling coil electricity rate for each individual stage in W.
        
        Return:
            A list of the float cooling coil electricity rate for each stage, in order
        '''
        
        # FIXME
        # What if the RTU is multi-stage?
        # Return a list with the one stage the RTU uses
        return [ self.emulator.read_var('power_reading_cool_coil', self.name) ]
    
    def get_cooling_coil_inlet_temperature(self):
        '''
        Get the cooling coil inlet temperature for each sensor in degrees Celsius.
        
        Return:
            The list of float cooling coil inlet temperatures, one per sensor.
        '''
        
        # Fixme
        # What if the RTU has multiple sensors?
        # Return a list with the one coil's temperature
        return [ self.emulator.read_var('T_RTU_cool_coil_inlet', self.name) ]
    
    def get_cooling_coil_outlet_temperature(self):
        '''
        Get the cooling coil outlet temperature in degrees Celsius.
        
        Return:
            The float cooling coil outlet temperature.
        '''
        
        return self.emulator.read_var('T_RTU_cool_coil_outlet', self.name)
    
    def get_fan_electricity_rate(self):
        '''
        Get the fan electricity rate in W.
        
        Return:
            The float fan electricity rate.
        '''
        
        return self.emulator.read_var('power_reading_fan', self.name)
    
    def get_fan_schedule(self):
        '''
        Get the fan schedule
        
        Return:
            Integer 1 for "On" or Integer 0 for "Off"
        '''
        
        return self.emulator.read_var("F_sched", self.name)
    
    def get_heating_coil_electricity_rate(self):  
        '''
        Get the heating coil electricity rate in W.
        
        Return:
            The float heating coil electricity rate
        '''
        
        return self.emulator.read_var('power_reading_heat_coil', self.name)
    
    def get_heating_coil_outlet_temperature(self):
        '''
        Get heating coil outlet temperature in degrees Celsius.
        
        Return:
            The float heating coil outlet temperature.
        '''
        
        return self.emulator.read_var('T_RTU_heat_coil_outlet', self.name)
    
    def get_heating_coil_set_point(self):
        '''
        Get the heating coil set point.
        
        Return:
            The float heating coil set point.
        '''
        
        return self.emulator.read_var('RTU_SA_heatingcoil_setpoint', self.name)
    
    def get_outdoor_air_temperature(self):
        '''
        Get the outdoor air temperature in degrees Celsius.
        
        Return:
            The float outdoor air temperature
        '''
        
        return self.emulator.read_var('T_OA', self.name)
    
    def is_available(self):
        
        return self.emulator.env_ready(True)
    
    def is_interactive(self):
        '''
        Whether or not it is possible to arbitrarily call this Controller or if it can only be invoked in a special 
            environment.
            
        Return:
            False, this Controller can only be invoked inside of EnergyPlus C++ bindings and must not be directly invoked
                by a Strategy.
        '''
        
        return False
    
    def is_simulation_ready(self):
        '''
        Check whether any simulation backing the unit is ready to run.
        
        Should always be False if the unit is not available (from is_available()) even if the simulation is internally
        initialized.
        
        Return:
            True if the simulation for this unit is ready and if is_available() is true. Also True if is_available() is
            true and this device is not simulated. False otherwise. 
        '''
        
        # Always available, no simulation
        return self.emulator.env_ready(False)
    
    def set_cooling_coil_set_point(self, value):
        '''
        Set the cooling coil setpoint.
        
        Args:
            value: The desired float cooling coil setpoint
        '''
        
        self.emulator.set_control_action('RTU_SA_coolingcoil_setpoint', self.name, value) 
    
    def set_heating_coil_set_point(self, value):
        '''
        Set the heating coil setpoint.
        
        Args:
            value: The desired float heating coil setpoint.
        '''
        
        self.emulator.set_control_action('RTU_SA_heatingcoil_setpoint', self.name, value) 
        
    