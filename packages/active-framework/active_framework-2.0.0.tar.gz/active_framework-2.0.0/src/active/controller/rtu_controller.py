from active.controller.decorators import ActiveController

class VAVUnit():
    '''
    Sub-unit of the Controller which holds functions related to only one specific VAV unit.
    '''
    
    def __init__(self):
        '''
        Default constructor.
        
        '''
        
        pass
    
    def get_actuator_temperature(self):
        '''
        Get the actuator outlet temperature in degrees Celsius.
        
        Returns:
            The float actuator temperature
        '''
        
        return NotImplemented

    def get_actuator_inlet_mass_flow_rate(self):
        '''
        Get the actuator_inlet_mass_flow_rate in kg/s
        
        Returns:
            The float actuator inlet mass flow rate
        '''
        
        return NotImplemented

    def get_cooling_load(self):
        '''
        Get the cooling load in W
        
        Returns:
            The float cooling load
        '''
        
        return NotImplemented

    def get_cooling_set_point(self):
        '''
        Get the cooling set point in degrees Celsius.
        
        Returns:
            The float cooling set point
        '''
        
        return NotImplemented
    
    def get_enthalpy(self):
        '''
        Get the zone's enthalpy in J/kgDA
        
        Return:
            The zone's enthalpy as a float
        '''
        
        return NotImplemented
    
    def get_fan_electricity_rate(self):
        '''
        Get the fan electricity rate in W.
        
        Return:
            The float fan electricity rate.
        '''
        
        return NotImplemented
        
    def get_floor_area(self):
        '''
        Get the floor area
        
        Returns:
            The float floor area
        '''
        
        return NotImplemented
    
    def get_floor_volume(self):
        '''
        Get the floor volume
        
        Returns:
            The float floor volume
        '''
        
        return NotImplemented
    
    def get_heating_load(self):
        '''
        Get the heating load in W
        
        Returns:
            The float heating load
        '''
        
        return NotImplemented
    
    def get_heating_set_point(self):
        '''
        Get the heating set point in degrees Celsius
        
        Returns:
            The float heating set point
        '''
        
        return NotImplemented
    
    def get_humidity(self):
        '''
        Get the humidity in kg/kgDA
        
        Returns:
            The float humidity
        '''
        
        return NotImplemented
    
    def get_inlet_density(self):
        '''
        Get the inlet density kg/m3
        
        Return:
            The float inlet density
        '''
        
        return NotImplemented
    
    def get_inlet_enthalpy(self):
        '''
        Get the inlet enthalpy in J/kgDA
        
        Return:
            The float inlet enthalpy
        '''
        
        return NotImplemented
    
    def get_inlet_humidity(self):
        '''
        Get the inlet humidity ratio in kg/kgDA
        
        Return:
            The float inlet humidity ratio
        '''
        
        return NotImplemented
    
    def get_inlet_specific_heat(self):
        '''
        Get the inlet specific heat in J/kgK
        
        Return:
            The float inlet specific heat
        '''
        
        return NotImplemented
    
    def get_inlet_temperature(self):
        '''
        Get the inlet temperature in degrees Celsius.
        
        Return:
            The float inlet temperature.
        '''
        
        return NotImplemented
    
    def get_relative_humidity(self):
        '''
        Get the zone's relative humidity as a percentage.
        
        Return:
            The float zone relative humidity
        '''
        
        return NotImplemented
    
    def get_supply_airflow_rate(self):
        '''
        Get the zone's supply airflow rate.
        
        Return:
            The float supply airflow rate
        '''
        
        return NotImplemented
    
    def get_temperature(self):
        '''
        Get the zone's temperature in degrees Celsius
        
        Return:
            The zone's temperature as a float
        '''
        
        return NotImplemented
    
    def is_available(self):
        '''
        Check whether the unit is ready to receive requests
        
        Return:
            True if the unit is ready, False if it is not.
        '''
        
        return NotImplemented
    
    def is_simulation_ready(self):
        '''
        Check whether any simulation backing the unit is ready to run.
        
        Should always be False if the unit is not available (from is_available()) even if the simulation is internally
        initialized.
        
        Return:
            True if the simulation for this unit is ready and if is_available() is true. Also True if is_available() is
            true and this device is not simulated. False otherwise. 
        '''
        
        return NotImplemented
    
    def set_actuator_humidity(self, value):
        '''
        Set the actuator outlet relative humidity ratio.
        
        Args:
            value: Float for the desired relative humidity ratio in kg/kgDA
        '''
        
        return NotImplemented
        
    def set_actuator_inlet_mass_flow_rate(self, value):
        '''
        Set the actuator inlet mass flow rate.
        
        Args:
            value: Float for the desired inlet mass flow rate in kg/s
        '''
        
        return NotImplemented
    
    def set_actuator_outlet_mass_flow_rate(self, value):
        '''
        Set the actuator outlet mass flow rate.
        
        Args:
            value: Float for the desired outlet mass flow rate in kg/s
        '''
        
        return NotImplemented
    
    def set_actuator_temperature(self, value):
        '''
        Set the actuator outlet temperature.
        
        Args:
            value: Float for the desired temperature in degrees Celsius.
        '''
        
        return NotImplemented
    
    def set_supply_airflow_rate(self, value):
        '''
        Set the supply airflow rate.
        
        Args:
            value: Float for the desired supply airflow rate
        '''
        
        return NotImplemented


class RTUController():
    '''
    A Controller for an RTU in an EnergyPlus simulation using the EnergyPlusAPI for communication.
    '''
    
    def __init__(self):
        '''
        The default constructor.
        '''

        pass
        
    def get_cooling_coil_electricity_rate(self):  
        '''
        Get the cooling coil electricity rate for each individual stage in W.
        
        Return:
            A list of the float cooling coil electricity rate for each stage, in order
        '''
        
        return NotImplemented
    
    def get_cooling_coil_inlet_temperature(self):
        '''
        Get the cooling coil inlet temperature for each sensor in degrees Celsius.
        
        Return:
            The list of float cooling coil inlet temperatures, one per sensor.
        '''
        
        return NotImplemented
    
    def get_fan_electricity_rate(self):
        '''
        Get the fan electricity rate in W.
        
        Return:
            The float fan electricity rate.
        '''
        
        return NotImplemented
    
    def get_fan_schedule(self):
        '''
        Get the fan schedule
        
        Return:
            Integer 1 for "On" or Integer 0 for "Off"
        '''
        
        return NotImplemented
    
    def get_heating_coil_electricity_rate(self):  
        '''
        Get the heating coil electricity rate in W.
        
        Return:
            The float heating coil electricity rate
        '''
        
        return NotImplemented
    
    def get_heating_coil_outlet_temperature(self):
        '''
        Get heating coil outlet temperature in degrees Celsius.
        
        Return:
            The float heating coil outlet temperature.
        '''
        
        return NotImplemented
    
    def get_heating_coil_set_point(self):
        '''
        Get the heating coil set point.
        
        Return:
            The float heating coil set point.
        '''
        
        return NotImplemented
    
    def get_outdoor_air_temperature(self):
        '''
        Get the outdoor air temperature in degrees Celsius.
        
        Return:
            The float outdoor air temperature
        '''
        
        return NotImplemented
    
    def is_available(self):
        '''
        Check if the RTU is ready to receive communication.
        
        Return:
            True if the RTU is ready for communication, False if not
        '''
        
        return NotImplemented
    
    def is_interactive(self):
        '''
        Whether or not it is possible to arbitrarily call this Controller or if it can only be invoked in a special 
            environment.
            
        Return:
            True if this object's functions can be freely called, False if the RTU requires a special environment to be 
            arranged by the Agent.
        '''
        
        return NotImplemented
    
    def is_simulation_ready(self):
        '''
        Check whether any simulation backing the unit is ready to run.
        
        Should always be False if the unit is not available (from is_available()) even if the simulation is internally
        initialized.
        
        Return:
            True if the simulation for this unit is ready and if is_available() is true. Also True if is_available() is
            true and this device is not simulated. False otherwise. 
        '''
        
        return NotImplemented
    
    def set_cooling_coil_set_point(self, value):
        '''
        Set the cooling coil setpoint.
        
        Args:
            value: The desired float cooling coil setpoint
        '''
        
        return NotImplemented
    
    def set_heating_coil_set_point(self, value):
        '''
        Set the heating coil setpoint.
        
        Args:
            value: The desired float heating coil setpoint.
        '''
        
        return NotImplemented
        
    