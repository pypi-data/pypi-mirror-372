import BAC0
import time

from BAC0.core.devices.local.models import (
    analog_input,
    analog_output,
    analog_value,
    binary_input,
    binary_output,
    binary_value,
    character_string,
    date_value,
    datetime_value,
    humidity_input,
    humidity_value,
    make_state_text,
    multistate_input,
    multistate_output,
    multistate_value,
    temperature_input,
    temperature_value,
)
from BAC0.core.devices.local.object import ObjectFactory

class BACnetEmulatorBase():
    '''
    Mock BACnet device.
    
    Parameters:
        device: BACnet connection.
    '''
    
    def __init__(self, address="127.17.0.101/24", port=47808, deviceID=101, device_objects=[]):
        '''
        Default constructor
        
        Args:
            address String IP address.
            port Int port number for the device.
            deviceID Int device ID
            device_objects List of object definitions of the form 
                {
                    "type": "foo",
                    "instance": 0,
                    "value": 1
                }
                
                where "foo" is one of:
                    analog_input,
                    analog_output,
                    analog_value,
                    binary_input,
                    binary_output,
                    binary_value,
                    character_string,
                    date_value,
                    datetime_value,
                    humidity_input,
                    humidity_value,
                    make_state_text,
                    multistate_input,
                    multistate_output,
                    multistate_value,
                    temperature_input,
                    temperature_value
        '''
        
        self.address = address
        self.port = port
        self.deviceID = deviceID
        self.device_objects = device_objects
        
    def start(self):
        
        # Initialize the device with nothing in it
        self.device = BAC0.lite(ip=self.address, port=self.port, deviceId=self.deviceID)
        ObjectFactory.clear_objects()
        
        # Define all the endpoints used in data.config
        for obj in self.device_objects:
            if "analog_input" == obj["type"]:
                _new_objects = analog_input(instance=obj["instance"], presentValue=obj["value"])
            if "analog_output" == obj["type"]:
                _new_objects = analog_output(instance=obj["instance"], presentValue=obj["value"])
            if "analog_value" == obj["type"]:
                _new_objects = analog_value(instance=obj["instance"], presentValue=obj["value"])

    
        # Add the objects to the device
        _new_objects.add_objects_to_application(self.device)
        
        while True:
            time.sleep(10)
        
    def stop(self):
        '''
        Stop the device.
        '''
        self.device.disconnect()
        
if __name__ == "__main__":
    
    # If run as a script, create an emulated device with default values
    instance = BACnetEmulator()
    
    while True:
        time.sleep(10)
