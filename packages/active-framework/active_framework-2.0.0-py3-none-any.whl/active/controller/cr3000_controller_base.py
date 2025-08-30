import pandas as pd

from datetime import datetime
from io import StringIO

from active.controller.http_controller_base import HTTPControllerBase

class CR3000ControllerBase(HTTPControllerBase):
    '''
    Base class for communications with a CR3000 data logger over HTTP.
    
    ACTIVE environment file prototype:
    
    {
        "tables": ["my_table5sec", "my_table10min"],
        "url": "127.0.0.1:82"
    }
    
    Parameters:
        _cache: Pandas Dataframe for the data from all specified tables, cached at the start of the 
            transaction.
        _cached_timestamp: Datetime for when the current transaction started.
        tables: List of strings for the table names to download. Data from tables earlier in the list takes
            precedence over data from tables later in the list.
        url: String url for the server to scrape data from
    '''
    
    
    def __init__(self, tables=[], url=""):
        '''
        The default constructor.
        
        Args:
            tables: List of strings for the table names to download. Data from tables earlier in the list takes
                precedence over data from tables later in the list.
            url: String url for the server to scrape data from
        '''
        
        super().__init__(url=url)

        self.tables = tables
        
        self._cache = None
        self._cached_timestamp = None
        
    def get_charge_current_phase_a(self):
        '''
        Get the charge current for phase A in units of Amperes.
        
        Return:
            The charge current phase A as a float
        '''
    
        return self._get_with_cache("EV_I_A(1)")
    
    def get_charge_current_phase_b(self):
        '''
        Get the charge current for phase B in units of Amperes.
        
        Return:
            The charge current phase B as a float
        '''
    
        return self._get_with_cache("EV_I_B(1)")
    
    def get_charge_power(self):
        '''
        Get the charge power in units of Watts.
        
        Return:
            The charge power as a float
        '''
    
        return self._get_with_cache("EV_W(1)")
    
    def get_charge_power_factor(self):
        '''
        Get the charge power factor.
        
        Return:
            The charge power factor as a float
        '''
    
        return self._get_with_cache("EV_PF(1)")
        
    def get_charging_apparent_power(self):
        '''
        Get the charging apparent power in units of Volt-Amperes.
        
        Return:
            The charging apparent power as a float
        '''
    
        return self._get_with_cache("EV_VA(1)")
        
    def get_charging_net_energy(self):
        '''
        Get the charging net energy in units of Kilowatt-Hours.
        
        Return:
            The charging net energy as a float
        '''
    
        return self._get_with_cache("EV_NetEnergy(1)")
        
    def get_charging_reactive_power(self):
        '''
        Get the charging reactive power in units of Volt-Ampere Reactives.
        
        Return:
            The charging reactive power as a float
        '''
    
        return self._get_with_cache("EV_VAR(1)")
        
    def get_charging_voltage(self):
        '''
        Get the charging voltage in units of Volts.
        
        Return:
            The charging voltage as a float
        '''
    
        return self._get_with_cache("EV_V_AB(1)")
    
    def get_cold_temperature_average(self):
        '''
        Get the average cold temperature.
        
        Return:
            The average cold temperature as a float
        '''
    
        return float(self._get_with_cache("T_Cold_Avg"))
    
    def get_discharge_current_phase_a(self):
        '''
        Get the discharge current for phase A in units of Amperes.
        
        Return:
            The charge current phase A as a float
        '''
    
        return self._get_with_cache("EV_I_A(2)")
    
    def get_discharge_current_phase_b(self):
        '''
        Get the discharge current for phase B in units of Amperes.
        
        Return:
            The charge current phase B as a float
        '''
    
        return self._get_with_cache("EV_I_B(2)")
    
    def get_discharge_power(self):
        '''
        Get the discharge power in units of Watts.
        
        Return:
            The discharge power as a float
        '''
    
        return self._get_with_cache("EV_W(2)")
    
    def get_discharge_power_factor(self):
        '''
        Get the discharge power factor.
        
        Return:
            The discharge power factor as a float
        '''
    
        return self._get_with_cache("EV_PF(2)")
        
    def get_discharging_apparent_power(self):
        '''
        Get the discharging apparent power in units of Volt-Amperes.
        
        Return:
            The discharging apparent power as a float
        '''
    
        return self._get_with_cache("EV_VA(2)")
        
    def get_discharging_net_energy(self):
        '''
        Get the discharging net energy in units of Kilowatt-Hours.
        
        Return:
            The discharging net energy as a float
        '''
    
        return self._get_with_cache("EV_NetEnergy(2)")
        
    def get_discharging_reactive_power(self):
        '''
        Get the discharging reactive power in units of Volt-Ampere Reactives.
        
        Return:
            The discharging reactive power as a float
        '''
    
        return self._get_with_cache("EV_VAR(2)")
    
    def get_discharging_voltage(self):
        '''
        Get the discharging voltage in units of Volts.
        
        Return:
            The discharging voltage as a float
        '''
    
        return self._get_with_cache("EV_V_AB(2)")
    
    def get_garage_temperature_average(self):
        '''
        Get the average garage temperature
        
        Return:
            The average garage temperature as a float
        '''
    
        return float(self._get_with_cache("HPWHrunning_Tgarage"))
    
    def get_level_1_thermostat_location_temperature(self):
        '''
        Get the temperature at the location of the level one thermostat in units of degrees Fahrenheit.
        
        Return:
            The temperature as a float
        '''
    
        return self._get_with_cache("T_L1_Tstat_Avg")
    
    def get_level_2_thermostat_location_temperature(self):
        '''
        Get the temperature at the location of the level two thermostat in units of degrees Fahrenheit.
        
        Return:
            The temperature as a float
        '''
    
        return self._get_with_cache("T_L2_Tstat_Avg")
    
    def get_outside_temperature(self):
        '''
        Get the outside temperature in units of degrees Fahrenheit.
        
        Return:
            The outside temperature as a float
        '''
    
        return self._get_with_cache("T_Outside_Avg")
    
    def get_water_heater_tank_out_temperature_average(self):
        '''
        Get the water heater's average tank out temperature
        
        Return:
            The water heater's average tank out temperature as a float
        '''
    
        return self._get_with_cache("T_HPHW2_out_Avg")
    
    def get_water_heater_tank_out_voltage_total(self):
        '''
        Get the water heater's total tank out voltage
        
        Return:
            The water heater's total tank out voltage as a float
        '''
    
        return self._get_with_cache("V_HPWH2out_Tot")
    
    def get_whole_house_energy(self):
        '''
        Get the whole house energy in units of Watts.
        
        Return:
            The whole house energy as a float
        '''
    
        return self._get_with_cache("W_WholeHouse_Tot")
        
    
    def is_available(self):
        '''
        Check if the device is ready to receive communication.
        
        Return:
            True, this device cannot report back an inoperable state
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
    
    def get_measurement_taken(self):
        '''
        Get the timestamp at which the last measurement was taken. Inside a transaction, this is defined as
        the time the transaction started. Outside of a transaction, it is the current time.
        
        Return:
            A datetime for the last measurement.
        '''
        
        if self._cached_timestamp != None:
            return self._cached_timestamp
        
        return datetime.now()
    
    def start_transaction(self):
        '''
        Start a transaction by downloading and caching all data.
        '''
        
        self._cache = self._get_tables()
        self._cached_timestamp = datetime.now()
        
    def stop_transaction(self):
        '''
        Stop the current transaction by clearing all caches.
        '''
        
        self._cache = None
        self._cached_timestamp = None
    
    def _get_tables(self):
        '''
        Get the latest record from all tables of interest.
        
        Return:
            A dataframe with one row. For each column, the value comes from the first table in "tables" 
            which had that parameter defined.
        '''

        # The dataframe under construction
        df = None
        
        # Download each table
        for table in self.tables:
        
            # Get the table from the data logger
            payload = self.get("?command=NewestRecord&table=" + table)

            # Parse the HTML, then transpose if the table 
            curr_df = pd.read_html(StringIO(payload))[0]
            
            if len(curr_df) != 1:
                curr_df = curr_df.T
            
            # Take the first row as column names, then drop that row
            curr_df.columns = curr_df.iloc[0]
            curr_df = curr_df.iloc[1:]

            # For every table but the first, combine the latest dataframe with the merged one
            if df is not None:
                df = df.combine_first(curr_df)
            else:
                df = curr_df
        
        # Convert from Pandas data types to Python native ones
        df =  df.astype('object')
        
        return df

    def _get_with_cache(self, parameter):
        '''
        Get the requested parameter name from the first table in the list of tables in which it appears. 
        Take the parameter from the cache if in a transaction. Otherwise, poll the tables.
        '''
        
        # Get the value from the cache if it exists
        if self._cache is not None:
            return self._cache[parameter].iloc[0]
        
        # Otherwise do a GET on the tables
        else:
            return self._get_tables()[parameter].iloc[0]

