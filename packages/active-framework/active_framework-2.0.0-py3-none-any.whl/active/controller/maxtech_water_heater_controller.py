'''
Created on February, 2019
Implemented by Robert Smith
email: smithrw@ornl.gov

This material was prepared by UT-Battelle, LLC (UT-Battelle) under Contract DE-AC05-00OR22725
with the U.S. Department of Energy (DOE). All rights in the material are reserved by DOE on 
behalf of the Government and UT-Battelle pursuant to the contract. You are authorized to use
the material for Government purposes but it is not to be released or distributed to the public.
NEITHER THE UNITED STATES NOR THE UNITED STATES DEPARTMENT OF ENERGY, NOR UT-Battelle, NOR ANY
OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LEGAL LIABILITY OR
RESPONSIBILITY FOR THE ACCURACY, COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, 
PRODUCT, OR PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE PRIVATELY OWNED RIGHTS.
'''

import json
from Commodity import Commodity
from datetime import datetime
from Device import Device

class WaterHeater(Device):
    ''' This class represents a physical water heater accessible through SkyCentrics API. It receives certain data from the API and can push changes to the API.
    
    '''
    
    def __init__(self, api, database_api, home_name, json):
        ''' The defualt constructor
        
        @param api: A SkycentricAPI with the information neccesary for connecting to the remote API.
        @param database_api: A DatabaseAPI object with information neccesary for connecting to the database.
        @param home_name: The name of the home containing this device
        @param json: Dictionary form of the json representation of the device information as obtained from the api's device list
        '''
        Device.__init__(self, api, database_api, home_name, json)
        
        #Override with the specific WaterHeater type
        self.device_type = "WaterHeater"
        
        #The present energy storage capacity
        self.capacity = None
        
        #The commodity
        self.commodity = None
        
        #Timestamp of the last heartbeat
        self.last_heartbeat = None
        
        #The state
        self.op_state = None
        
        #The override flag, either 0 or 1
        self.override = None
        
        #The device's power in W
        self.power = None
        
        self.update()
        
    def send_event(self, type, duration):
        '''Send an event to the remote api.
        
        @TODO There are more events in the web UI. Document them here
        @param type: The type of the event as a string. Valid values are:
            "CPE": Critical Peak Event
            "GE": Grid Emergency
            "LU": Load Up
        @param duration: The duration of the event in seconds as a number
        '''
        print "This is an execution of WaterHeater.send_event"
        
        #Create the event and send it to the API
        dict = {"event": type, "duration": duration}
        self.api.set_device_parameter(self.id, "event", json.dumps(dict))    
        
    def send_to_database(self):
        ''' Add a row in the appropriate database table representing the water heater's current state
        
        '''

        self.database_api.put_item("WaterHeaters", item={
                'device_id': str(self.id),
                'device_name': self.name,
                "data_timestamp": str(datetime.now()),
                "capacity": self.capacity,
                "commodity": self.commodity.to_json(),
                "last_heartbeat": self.last_heartbeat,
                "op_state": self.op_state,
                "override": self.override,
                "power": self.power
            })
        
    def shed_load(self, state, duration):
        '''Send a shed load event to the remote api.
        
        @param state: Number flag that sets the shed load state on or off. Should be 0 for off or 1 for on
        @param duration: The duration of the event in seconds as a number
        '''
        
        #Create the event and send it to the API
        dict = {"s": state, "duration": duration}
        self.api.set_device_parameter(self.id, "load_shed", json.dumps(dict))            
        
    def update(self):
        ''' Update own information with the latest data from the remote api
        
        '''
        
        json_data = self.api.GetDeviceData(self.id)
        
        #Search the commodaties for the present energy storage capacity and power
        for comm in json_data['commodities']:
            if comm['code'] == 0:
                self.power = comm['instantaneous']
            elif comm['code'] == 7:
                self.capacity = comm['cumulative']
                print('wh capacity: ' + str(self.capacity))
                break
            
        self.commodity = Commodity(json_data.get('commodity', {}))
        self.last_heartbeat = json_data.get('time', -1)
        self.op_state = json_data.get('state', "MISSING STATE")
        self.override = json_data.get('override', -1)
        
