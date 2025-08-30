import psychrolib

from active.controller.http_controller_base import HTTPControllerBase
from active.controller.rtu_controller import RTUController, VAVUnit

class CR1000XVAVUnit(VAVUnit):
    '''
    Representation of one VAV for the RTU.
    
    Parameters:
        air_density: Float air density in lbs/ft3.
        controller: DataLoggerRTUControllerBase for the containing RTU
        name: Unique string name for this VAV's zone. Should be equal to "foo" within the data logger provided variable 
                "WH_RTU_VAVfoo_Tot"
    '''
    
    def __init__(self, controller, name, air_density=0.0765):
        '''
        The default constructor.
        
        Args:
            air_density: Float air density in lbs/ft3.
            controller: DataLoggerRTUControllerBase which will handle communications.
            name: The unique string name of this VAV's zone. Should be equal to "foo" within the data logger provided 
                variable "RH_Room_foo"
        '''
        
        self.air_density = air_density
        self.controller = controller
        self.name = name
        
    def get_actuator_temperature(self):
        '''
        Get the actuator outlet temperature in degrees Celsius.
        
        Returns:
            The float actuator temperature
        '''
        return self.controller._get_parameter("T_out")
    
    def get_actuator_inlet_mass_flow_rate(self):
        '''
        Get the actuator_inlet_mass_flow_rate in kg/s
        
        Returns:
            The float actuator inlet mass flow rate
        '''
        
        return self.controller._get_parameter("AirACFM_RTU_Tot") * self.air_density
    
    def get_humidity(self):
        '''
        Get the humidity in kg/kgDA
        
        Returns:
            The float humidity
        '''
        
        return self.controller._get_parameter("RH_Room_" + self.name)
    
    def get_inlet_humidity(self):
        '''
        Get the inlet humidity ratio in kg/kgDA
        
        Return:
            The float inlet humidity ratio
        '''
        
        # FIXME check that this is right
        #return self.get_json("/get_point")['payload']['output'][self.name]["W_inlet"]
        return self.controller._get_parameter("RH_Sup_tot")
    
    def get_inlet_temperature(self):
        '''
        Get the inlet temperature in degrees Celsius.
        
        Return:
            The float inlet temperature.
        '''
        
        # FIXME check that this is right
        #return self.get_json("/get_point")['payload']['output'][self.name]["T_inlet"]
        return self.controller._get_parameter("T_Sup_tot")
    
    def get_relative_humidity(self):
        '''
        Get the zone's relative humidity as a percentage.
        
        Return:
            The float zone relative humidity
        '''
        
        return self.controller._get_parameter("RH_Room_" + self.name)
    
    def get_temperature(self):
        '''
        Get the zone's temperature in degrees Celsius
        
        Return:
            The zone's temperature as a float
        '''
        
        return self.controller._get_parameter("T_Room_" + self.name)
    
    def is_available(self):
        '''
        Check whether the unit is ready to receive requests
        
        Return:
            True if the unit is ready, False if it is not.
        '''
        
        # Always available
        return True
    
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
        return True
    
    def set_actuator_humidity(self, value):
        '''
        Set the actuator outlet relative humidity ratio.
        
        Args:
            value: Float for the desired relative humidity ratio in kg/kgDA
        '''
        
        self.controller._set_parameter("RH_out", value)
        
    def set_actuator_inlet_mass_flow_rate(self, value):
        '''
        Set the actuator inlet mass flow rate.
        
        Args:
            value: Float for the desired inlet mass flow rate in kg/s
        '''
        
        self.controller._set_parameter("AirACFM_RTU_Tot", value / self.air_density)
        
    def set_actuator_temperature(self, value):
        '''
        Set the actuator outlet temperature.
        
        Args:
            value: Float for the desired temperature in degrees Celsius.
        '''
        
        self.controller._set_parameter("T_out", value)

class CR1000XRTUControllerBase(HTTPControllerBase, RTUController):
    '''
    Base class for communications with an RTU behind a data logger over HTTP.
    
    ACTIVE configuration file parameters prototype
    
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
    
    Parameters:
        fields: List of strings for the final portion of all URIs in the public table. Consists of every 'foo' where 
            "dl:public.foo" exists in the external web server API.
        name: String name for an arbitrary VAV to pull data from when the data is replicated across all zones.
        vavs: Dictionary of string zone names to a CR1000XVAVUnit for that zone.
    '''
    
    def __init__(self, url="", vav_names=[]):
        '''
        The default constructor.
        
        Args:
            url: String url for the data logger's http server.
            vav_names: List of strings for each VAV name.
        '''
        
        super().__init__(url=url)
        
        # Arbitrarily use first zone name to get data from
        self.name = vav_names[0]
        
        self.vavs = {}
        
        for vav_name in vav_names:
            self.vavs[vav_name] = CR1000XVAVUnit(self, vav_name)
            
        # Get list of all fields
        symbols = self.get_json("?command=browsesymbols&uri=dl:public&format=json")["symbols"]
        print(symbols)
        self.fields = [ i["uri"] for i in symbols ]
        
        # Get only last segment of field URIs
        for i in range(len(self.fields)):
            self.fields[i] = self.fields[i][self.fields[i].rindex(".")+1:]
            
    def get_cooling_coil_electricity_rate(self):  
        '''
        Get the cooling coil electricity rate for each individual stage in W.
        
        Return:
            A list of the float cooling coil electricity rate for each stage, in order
        '''
        
        # List of rates per stage to return
        rates = []
        
        # Current stage number
        curr_stage = 1
        
        # Keep added rates for each stage until the next stage is no longer in the returned data poin
        while "WH_RTU_Comp" + str(curr_stage) + "_Tot" in self.fields:
        
            rates.append(self._get_parameter("WH_RTU_Comp" + str(curr_stage) + "_Tot"))
            curr_stage += 1 
        
        return rates
    
    def get_cooling_coil_inlet_temperature(self):
        '''
        Get the cooling coil inlet temperature in degrees Celsius.
        
        Return:
            The float cooling coil inlet temperature.
        '''
        
        # Get current data
        data = self.get_json("/get_point")['payload']['output'][self.name]
        
        # List of temperatures per sensor to return
        temperatures = []
        
        # Current sensor number
        curr_sensor = 1
        
        # Keep added rates for each sensor until the next sensor is no longer in the returned data point
        while "T_ReturnMix" + str(curr_sensor) in data:
        
            temperatures.append(data["T_ReturnMix" + str(curr_sensor)])
            curr_sensor += 1 
        
        return temperatures
    
    def get_fan_electricity_rate(self):
        '''
        Get the fan electricity rate in W.
        
        Return:
            The float fan electricity rate.
        '''
        
        # Fan electricity rate is the sum of this value plus every WH_RTU_Cond*_Tot value in the system.
        rate = self._get_parameter("WH_RTU_EvapFan_Tot")
        
        # Current cond number
        curr_cond = 1
        
        # Keep accumulating electricity for each cond until next cond is no longer in the returned data point
        while "WH_RTU_Cond" + str(curr_cond) + "_Tot" in self.fields:
        
            rate += self._get_parameter["WH_RTU_Cond" + str(curr_cond) + "_Tot"]
            curr_cond += 1 
        
        return rate
    
    def get_heating_coil_electricity_rate(self):  
        '''
        Get the heating coil electricity rate in W.
        
        Return:
            The float heating coil electricity rate
        '''
        
        # Sum WH_RTU_VAVzone_Tot across all zones
        total = 0
        
        for vav_name in self.vavs.keys():
            total += self._get_parameter("WH_RTU_VAV" + str(vav_name) + "_Tot")
            
        return total
    
    def get_heating_coil_outlet_temperature(self):
        '''
        Get heating coil outlet temperature in degrees Celsius.
        
        Return:
            The float heating coil outlet temperature.
        '''
        
        return self._get_parameter("T_Sup_tot")
    
    def get_outdoor_air_temperature(self):
        '''
        Get the outdoor air temperature in degrees Celsius.
        
        Return:
            The float outdoor air temperature
        '''
        
        return self._get_parameter("T_out")
    
    def is_available(self):
        '''
        Check if the RTU is ready to receive communication.
        
        Return:
            True, this RTU cannot report back an inoperable state
        '''
        
        return True
    
    def is_interactive(self):
        '''
        Whether or not it is possible to arbitrarily call this Controller or if it can only be invoked in a special 
            environment.
            
        Return:
            True
        '''
        
        return True
    
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
        return True
    
    def _get_parameter(self, param):
        '''
        Get json formatted most recent data point for the given parameter.
        
        Args:
            param: String parameter name to get
        Return:
            The parameter value given by the data logger.
        '''
        
        return \
            self.get_json("?command=dataquery&uri=dl:public.{0}&format=json&mode=most-recent".format(param))['data'][0]['vals'][0]
        
    def _set_parameter(self, param, value):
        '''
        Set the given parameter to a new value on the data logger.
        
        Args:
            param: String parameter name to set
            value: Integer or float new value for the parameter
        '''
        
        self.get("?command=setvalueex&uri=dl:public.{0}&value={1}".format(param, str(value)))
        
            