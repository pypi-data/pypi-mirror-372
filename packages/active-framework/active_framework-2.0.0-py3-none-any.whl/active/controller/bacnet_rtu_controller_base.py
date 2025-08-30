from active.controller.bacnet_controller_base import BACnetControllerBase
from active.controller.rtu_controller import RTUController, VAVUnit

class BACNetVavUnit(VAVUnit):
    '''
    Representation of one VAV for the RTU.
    
    Parameters:
        addresses: Dictionary from String value names to Stirng BACNet object instance numbers
        controller: BACnetRTUControllerBase for the RTU which contains this VAV.
    '''
    
    def __init__(self, rtu, addresses):
        '''
        The default constructor.
        
        Args:
            rtu: The containing BACnetRTUControllerBase for the RTU which contains this VAV.
            addresses: Dictionary from String value names to Stirng BACNet object instance numbers, of the format:
                {
                    "supply_airflow_rate": "3000079"
                }
        '''
        
        self.addresses = addresses
        self.controller = rtu
        
    def get_supply_airflow_rate(self):
        '''
        Get the zone's supply airflow rate.
        
        Return:
            The float supply airflow rate
        '''

        return float(self.controller.read(self.controller.address, 'analogValue', self.addresses["supply_airflow_rate"]))
    
    def is_available(self):
        '''
        Check whether the unit is ready to receive requests
        
        Return:
            True if the unit is ready, False if it is not.
        '''
        
        # Always available
        return True
    
    def set_supply_airflow_rate(self, value):
        '''
        Set the supply airflow rate.
        
        Args:
            value: Float for the desired supply airflow rate
        '''
        
        self.controller.write(self.controller.address, 'analogValue', self.addresses["supply_airflow_rate"], value, 'presentValue')

class BACnetRTUControllerBase(BACnetControllerBase, RTUController):
    '''
    Base class for the business logic of controller an RTU over the BACnet communication protocol.
    
    ACTIVE configuration file parameters prototype
    
    {
        "name": "BACNet1",
        "type": "BACNet RTU",
        "parameters": {
            "address": "127.17.0.101:47801"
            "ip": "127.17.0.100/24", 
            "port": 80,
            "vav_addresses": {
                "102": {
                    "supply_airflow_rate": "3000011"
                }
            }
        }
    }
    
    '''
    
    def __init__(self, ip="127.17.0.100/24", port=80, address="", vav_addresses={}):
        '''
        The default constructor.
        
        Args:
            ip: String defining own IP and network mask. In the format "xxx.xxx.xxx.xxx/xx"
            port: Integer port number for the connection
            address: String representation of the device address. In the format of IP and port or the network:device "xx:yy" 
                Bacnet address.
            vav_addresses: Dictionary from String VAV names to dictionaries of parameter names to BACNet object addresses 
                for that parameter. Of the form:
                {
                    "101": {
                        "supply_airflow_rate": "3000079"
                    }
                }
        '''
        
        # Initialize data members
        super().__init__(ip=ip, port=port)
        self.address = address
        
        # Create a VAV for each zone
        self.vavs = {}
        for name in vav_addresses.keys():
            self.vavs[name] = BACNetVavUnit(self, vav_addresses[name])
        
    def get_heating_coil_set_point(self):
        '''
        Get the heating coil set point.
        
        Return:
            The float heating coil set point.
        '''
        
        return float(self.read(self.address, 'analogValue', 3000020))
    
    def set_cooling_coil_set_point(self, value):
        '''
        Set the cooling coil setpoint.
        
        Args:
            value: The desired float cooling coil setpoint
        '''
        
        self.write(self.address, 'analogValue', 3000020, value, 'presentValue')
        
    def set_heating_coil_set_point(self, value):
        '''
        Set the heating coil setpoint.
        
        Args:
            value: The desired float heating coil setpoint.
        '''
        
        self.write(self.address, 'analogValue', 3000020, value, 'presentValue')
        