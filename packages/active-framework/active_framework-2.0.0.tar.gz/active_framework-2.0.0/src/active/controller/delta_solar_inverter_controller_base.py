import base64
import datetime
import json

from active.controller.http_controller_base import HTTPControllerBase

from zoneinfo import ZoneInfo

class DeltaSolarInverterControllerBase(HTTPControllerBase):
    '''
    Base class for communications with a solar inverter through the Delta API.
    
    ACTIVE environment file prototype:
    
    {
        "password": "password", 
        "sn": "O1T0000000000", 
        "url": "https://delta-solar.vidagrid.com/api", 
        "username": "myname@company.com"
    }
    
    Parameters:
        auth_token: String token used for authentication with Delta API
        _cache: Dictionary of data cached from start of current transaction
        sn: Delta defined string for the sn of the device to query data from
    '''
    
    def __init__(self, password="", sn="", url="", username=""):
        '''
        The default constructor.
        
        Args:
            password String password for the vidagrid account
            sn String serial number for the inverter
            url: String url for the http server to query data from
            username String username for the account
        '''
        
        super().__init__(url=url)
        
        # Initialize data members
        self.sn = sn
        self._cache = None
        
        # Create the token according to Delta API's rules
        raw_token = username+ ':' + password
        self.auth_token = base64.b64encode(raw_token.encode('utf-8')).decode('utf-8')
    
    def get_aggregate_photovoltaic_power(self):
        '''
        Get the aggregate photovoltaic power
        
        Return:
            The aggregate photovoltaic power as a float
        '''
        
        return self._get_with_cache(["curr", "Inverter", "AggPVPower"])
    
    def get_backup_charge(self):
        '''
        Get the backup charge as a percentage of max charge.
        
        Return:
            The backup charge as a float
        '''
        
        return self._get_with_cache(["curr", "BMS", "BackupSoC"])
    
    def get_battery_capacities(self):
        '''
        Get the capacities for each battery in units of Watt-hours.
        
        Return:
            A list of floats of each batterys capacity in Watt-hours, ordered by battery number.
        '''
        
        # Get the data for all batteries.
        pv_data = self._get_with_cache(["curr"])
        
        # The list of cappacities to return
        currents = []
        
        # The next battery index to get
        next_index = 1
        
        # The name of the parameter to read for the next battery.
        next_key = "bat" + str(1) + "Cap"
        
        # Get each battery capacitiy,then calculate the next parameter name
        while next_key in pv_data:
            currents.append(pv_data[next_key])
            next_index += 1
            next_key = "bat" + str(next_index) + "Cap"
            
        return currents
    
    def get_battery_charge_energy_totals(self):
        '''
        Get the total charge energy for each battery, in units of Watt-hours.
        
        Returns:
            A list of floats for each battery's total charge energy, ordered by battery number.
        '''
        
        # Get the battery data
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        # Get the charge energy from each battery
        states = []
        
        for b in batteries:
            states.append(b["chgEnergy"])
            
        # Get the previous battery data
        batteries =  self._get_with_cache(["prev", "BMS", "BAT"])
        
        # Get the charge energy from each battery
        prev_states = []
        
        for b in batteries:
            prev_states.append(b["chgEnergy"])
            
        # Get the differences between last measurement and the previous timestep
        deltas = []
    
        for i in range(len(states)):
            deltas.append(states[i] - prev_states[i])
    
        return deltas
    
    def get_battery_charge_powers(self):
        '''
        Get the current charge power for each battery, in units of Watts.
        
        Return:
            A list of floats for the current charge power for each battery, ordered by battery number.
        '''
        
        # Get the battery data
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        # Make a list of each battery's charge power.
        states = []
        
        for b in batteries:
            states.append(b["chgPower"])
            
        return states   
    

    def get_battery_currents(self):
        '''
        Get the currents for each battery, in units of Amperes.
        
        Returns:
            A list of floats for the currents, ordered by battery numbers
        '''
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            states.append(b["Current"])
            
        return states   
    
    def get_battery_discharge_energy_totals(self):
        '''
        Get the total amount of energy discharge for each battery, in units of Watt-hours
        
        Returns:
            A list of floats for the total discharge energy for each battery, ordered by battery numbers
        '''
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            if "dischEnergy" in b:
                states.append(b["dischEnergy"])
            elif "dischgEnergy" in b:
                states.append(b["dischgEnergy"])
                
        batteries =  self._get_with_cache(["prev", "BMS", "BAT"])
        
        prev_states = []
        
        for b in batteries:
            if "dischEnergy" in b:
                prev_states.append(b["dischEnergy"])
            elif "dischgEnergy" in b:
                prev_states.append(b["dischgEnergy"])
            
        # Get the differences between last measurement and the previous timestep
        deltas = []
    
        for i in range(len(states)):
            deltas.append(states[i] - prev_states[i])
    
        return deltas  
    
    def get_battery_discharge_powers(self):
        '''
        Get the discharge power for each battery.
        
        Returns:
            A list of floats for the total discharge energy for each battery, ordered by battery numbers
        '''
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            if "dischPower" in b:
                states.append(b["dischPower"])
            elif "dischgPower" in b:
                states.append(b["dischgPower"])
            
        return states   
        
    
    def get_battery_states(self):
        '''
        Get a human readable description of each battery's state.
        
        Values are "standby", "enable", "fault", and "sleep".
        
        Returns:
            A list of strings of the above battery states, ordered by battery number.
        '''
        
        codes = {}
        codes[1] = "standby"
        codes[3] = "enable"
        codes[5] = "fault"
        codes[10] = "sleep"
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            states.append(codes[int(b["State"])])
            
        return states
    

    def get_battery_state_of_charges(self):
        '''
        Get each battery's state of charge, as a percent.
        
        Returns:
            A list of floats of states of charge, ordered by batter number.
        '''
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            states.append(b["Soc"])
            
        return states   
        
    
    def get_battery_statuses(self):
        '''
        Get a human readable description of the charging states for each battery.
        
        Valid values are "chargin", "dischargin", and "standby"
        
        Returns:
            A list of strings for the charging statuses, ordered by battery number.
        '''
        
        codes = {}
        codes[0] = "charging"
        codes[1] = "discharging"
        codes[2] = "standby"
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            states.append(codes[int(b["Status"])])
            
        return states
    
    def get_battery_voltages(self):
        '''
        Get the voltages for each battery, in units of Volts.
        
        Return:
            A list of floats for each voltage, ordered by battery number.
        '''
        
        batteries =  self._get_with_cache(["curr", "BMS", "BAT"])
        
        states = []
        
        for b in batteries:
            states.append(b["Volt"])
            
        return states   
    
    def get_charge_end(self):
        '''
        Get the datetime.time for when the charge ended.
        
        Return:
            The time the charge ended.
        '''
        
        return self._convert_minutes_to_time(self._get_with_cache(["curr", "TOU", "chargeEnd"]))
    
    def get_charge_power(self):
        '''
        Get the charge power, in units of Watts.
        
        Return:
            The charge power as a float
        '''
        
        value = self._get_with_cache(["curr", "TOU", "chargePower"], default=0)
        
        # If the value is None, replace it with a 0
        if not value is None:
            return value
        
        return 0
    
    def get_charge_start(self):
        '''
        Get the datetime.time for when the charge ended.
        
        Return:
            The time the charge ended.
        '''
        
        return self._convert_minutes_to_time(self._get_with_cache(["curr", "TOU", "chargeStart"]))
    
    def get_discharge_end(self):
        '''
        Get the datetime.time for when the discharge ended.
        
        Return:
            The time the discharge ended.
        '''
        
        return self._convert_minutes_to_time(self._get_with_cache(["curr", "TOU", "dischargeEnd"]))
    
    def get_discharge_power(self):
        '''
        Get the discharge power, in units of Watts.
        
        Return:
            The discharge power as a float
        '''
        
        value = self._get_with_cache(["curr", "TOU", "dischargePower"], default=0)
            
        # If the value is None, replace it with a 0
        if not value is None:
            return value
        
        return 0
    
    def get_discharge_start(self):
        '''
        Get the datetime.time for when the discharge start.
        
        Return:
            The time the discharge started.
        '''
        
        return self._convert_minutes_to_time(self._get_with_cache(["curr", "TOU", "dischargeStart"]))
    
    def get_energy_consumption(self):
        '''
        Get the energy consumption.
        
        Returns:
            The energy consumption as a float
        '''
        
        curr = self._get_with_cache(["curr", "Inverter", "ComsumpEnergy"])
        prev = self._get_with_cache(["prev", "Inverter", "ComsumpEnergy"])
        
        return curr - prev
            
    
    def get_grid_energy_bought(self):
        '''
        Get the amount of energy bought from the grid.
        
        Returns:
            The grid energy bought as a float
        '''
        
        curr =  self._get_with_cache(["curr", "Inverter", "GridBuyEnergy"])
        prev =  self._get_with_cache(["prev", "Inverter", "GridBuyEnergy"])
        
        return curr - prev
    
    def get_load_power(self):
        '''
        Get the load power, in units of Watts.
        
        Returns:
            The load power as a float.
        '''
        
        return self._get_with_cache(["curr", "Inverter", "loadP"])
    
    def get_measurement_time(self):
        '''
        Get the time the last measurement was taken.
        
        Returns:
            The time of the last measurement, as a timestamp
        '''
        
        return self._get_with_cache(["curr", "time"])
    
    def get_pcs_op_mode(self):
        '''
        Get a human readable description of the operation mode for the Power Conditioning System.
        
        Valid values are "EMS_SELF_CONSUMPTION_MODE", "EMS_ZERO_EXPORT_MODE", and "EMS_TOU_MODE"
        
        Return:
            A string for the operation mode.
        '''
        
        codes = {}
        codes[1] = "EMS_SELF_CONSUMPTION_MODE"
        codes[2] = "EMS_ZERO_EXPORT_MODE"
        codes[3] = "EMS_TOU_MODE"

        code = int(self._get_with_cache(["curr", "TOU", "pcsOpMode"]))
        
        if code in codes:
            return codes[code]
        
        return "UNRECOGNIZED PCS OP MODE CODE: " + str(code)
    
    def get_photovoltaic_average_currents(self):
        '''
        Get the average current for each photovoltaic unit.
        
        Returns:
            A list of floats for each average current, ordered by photovoltaic unit number.
        '''
        
        pv_data = self._get_with_cache(["curr", "Photovoltaic"])
        
        currents = []
        
        next_index = 1
        next_key = "PV" + str(1) + "AvgCurr"
        
        while next_key in pv_data:
            currents.append(pv_data[next_key])
            next_index += 1
            next_key = "PV" + str(next_index) + "AvgCurr"
            
        return currents
    
    def get_photovoltaic_average_voltages(self):
        '''
        Get the average voltage for each photovoltaic unit.
        
        Returns:
            A list of floats for the average volatages, orderd by photovoltaic unit number
        '''
        
        pv_data = self._get_with_cache(["curr", "Photovoltaic"])
        
        voltages = []
        
        next_index = 1
        next_key = "PV" + str(1) + "AvgVolt"
        
        while next_key in pv_data:
            voltages.append(pv_data[next_key])
            next_index += 1
            next_key = "PV" + str(next_index) + "AvgVolt"
            
        return voltages
    
    def get_photovoltaic_energy_today(self):
        '''
        Get the amount of photovoltaic energy for today, in units of Watt-hours.
        
        Return:
            A list of floats for the energies, ordered by photovoltaic unit number
        '''
        
        return self._get_with_cache(["curr", "Inverter", "pvTodayE"])
    
    def get_photovoltaic_energy_total(self):
        '''
        Get the total amount of photovoltaic energy, in units of Watt-hours.
        
        Return:
            A list of floats for the energies, ordered by photovoltaic unit number
        '''
        
        curr =  self._get_with_cache(["curr", "Inverter", "pvInfoSumE"])
        prev =  self._get_with_cache(["prev", "Inverter", "pvInfoSumE"])
        
        return curr - prev
    
    def get_sn(self):
        '''
        Get the sn.
        
        Returns:
            The sn as a string
        '''
        
        return self._get_with_cache(["curr", "sn"])
    
    def get_stat(self):
        '''
        Get the stat
        
        Returns:
            The stat as an integer
        '''
        
        return self._get_with_cache(["curr", "stat"])
    
    def get_state_of_health(self):
        '''
        Get the state of health
        
        Returns:
            The state of health as a float.
        '''
        
        # TODO Check if it's intentional that only the first battery has a StateofHealth defined.
        return self._get_with_cache(["curr", "BMS", "BAT", 0, "StateofHealth"])
    
    def is_grid_on(self):
        '''
        Get whether the grid is on.
        
        Return:
            Boolean True if the grid is on. False if it is off or unknown
        '''
        
        status = self._get_with_cache(["curr", "Inverter", "gridStatus"])
        
        #Status 0 = unknown, 1 = on, 2 == off
        return int(status) == 1
    
    def start_transaction(self):
        '''
        Begin a transaction. Calls to the remote API will not be made until the transaction is ended.
        '''
        
        # Also save the date the transaction started
        today = datetime.datetime.today()
        
        self._cache = self._get()
        self._cache["transaction_date"] = today
        
    def stop_transaction(self):
        '''
        End any current transaction, allowing new data to be read.
        '''
        
        self._cache = None
        
    def _convert_minutes_to_time(self, minutes_past_midnight):
        '''
        Convert the minutes past midnight into an equivalent datetime value
        
        Args:
            minutes_past_midnight: Minutes past midnight as an int
        Returns:
            The equivalent datetime, assuming that the date is either current or, if in a transaction, when
            the transaction started.
        '''
            
        # Minutes are the two high bytes
        minutes_low = minutes_past_midnight % 16
        minutes_high = int(minutes_past_midnight / 16) % 16 * 16
        minutes = minutes_high + minutes_low
        
        # Hours are the two low bytes
        hours_low = int(minutes_past_midnight / 16 / 16) % 16
        hours_high = int(minutes_past_midnight / 16 / 16 / 16) % 16 * 16
        hours = hours_high + hours_low

        t = datetime.time(hour=hours, minute=minutes)
        
        # Combine the calculated time with the date
        if self._cache == None:
            return datetime.datetime.combine(datetime.datetime.now(), t)
        
        else:
            return datetime.datetime.combine(self._cache["transaction_date"], t)
        
    def _get(self):
        '''
        Perform an HTTP get on the endpoint for the latest data, consisting of the last two timesteps.
        
        Returns:
            The json data from the call, as a dictionary of the format 
            {
                "curr": {last measurement dictionary},
                "prev": {second to last measurement dictionary}
        '''
        
        headers = {"Authorization":"Basic "+ self.auth_token}
        
        # We want the previous two timesteps, separated by 5 minutes each. Delta uses GMT+4
        now = datetime.datetime.now(ZoneInfo("Etc/GMT+4"))
        last = now - datetime.timedelta(minutes=15)
        
        # Perform the GET
        #data = self.get_json("sitequery/" + self.device_id + "?start=" + str(last) + "&end=" + str(now), headers
        #                      = headers)
        
        # headers['X-HTTP-Method-Override'] = "GET"
        headers["Content-type"] = "application/json"
        query = {
                "start": str(last),
                "end": str(now)
            }
        print(query)
        data = self.post("inverter/history/" + self.sn, json.dumps(query), headers=headers)
        data = json.loads(data)
        print(data)
        
        # Get the latest data and the measurement previous to it
        prev = None
        curr = None 

                
        # Measurements are in chronological order
        prev = data["data"][-2]
        curr = data["data"][-1]

        items = {}
        items["prev"] = prev
        items["curr"] = curr
        
        return items

    
    def _get_with_cache(self, json_path, default=None):
        '''
        Get a value from the Delta API json return data, using the cache if available.
        
        Args:
            json_path: A list of strings and/or integers, describting a path into the json data
            default: The value to return in case the requested key is not returned.
        Returns:
            The value in the json data at json_path
        '''
        
        # If inside of a transaction, the cache will exist
        if self._cache:
            dictionary = self._cache
            
        else:    
            # If not in a transaction, get the latest data
            dictionary = self._get()
            
        print(dictionary)    
            
        # Iterate through the path and get the data there
        for key in json_path:
            
            # Keep going if the key is present
            if key in dictionary:
                dictionary = dictionary[key]
                
            # If the key wasn't present, return the default value
            return default
            
        return dictionary
            