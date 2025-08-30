class EnergyPlusAPIEmulatorState():
    '''
    Holder for state variables for an EnergyPlusAPIEmulator
    
    Parameters:
        api: EnergyPlusAPI reference to the running EnergyPlus instance.
        building_model_config: Dictionary of building information
        console_output: Boolean flag for whether or not to output EnergyPlus logs to console.
        _ep_key_map: Map of string schema names to string EnergyPlus internal names for all seen variables.
        floor_config: Dictionary from string RTU names to lists of string zone names for zones associated with that RTU
        idf_file: String path to the idf file to run for the simulation.
        num_threads: Integer number of threads to use in the simulation
        output_dir: String path for the directory where EnergyPlus will save its output
        psychrometrics: Handle to the EnergyPlus psychrometrics instance
        RTU_list: List of string RTU names
        state_id: Integer state number for the EnergyPlus simulation.
        ts: Integer simulation interval in minutes
        variable_handles: Dictionary from variable names to integer handles to that variable within the simulation
        variable_schema:  Dictionary of all RTU and VAV variables read from or written to EP. Example: 
                EnergyPlusAPI().exchange.get_variable_handle(state, "Zone Air Temperature", "Room 203")
        weather_file: String path to the .epw weather file to run in the simulation.
        zone_list: List of string zone names.
    '''

    
    def __init__(self):
        
        # Initialize parameters
        self.api = None
        self.state_id = None
        self.psychrometrics = None
        
        self._ep_key_map = {} # caching the ep_keys for each variable

        self.ts = 0 # simulation interval in minutes
        
        self.console_output = False
        self.floor_config = {}
        self.idf_file = ""
        self.num_threads = 1
        self.RTU_list = []
        self.variable_handles = {}
        self.variable_schema = {}
        self.weather_file = ""
        self.zone_list = []
        self.output_dir = ""
        self.building_model_config = None
        