import BAC0
import socket
import time

class BACnetControllerBase():
    '''
    Base class for the business logic of controlling a device via the BACnet protocol for communication.
    
    ACTIVE configuration file parameters prototype
    
    {
        "name": "BACNet1",
        "type": "BACNet",
        "parameters": {
            "ip": "127.17.0.100/24", 
            "port": 80
        }
    }
    
    Parameters:
        bacnet: A BAC0 connection to the BACnet network.
    '''
    
    def __init__(self, ip="127.17.0.100/24", port=80):
        '''
        Default constructor.
        
        Args:
            ip String defining own IP and network mask. In the format "xxx.xxx.xxx.xxx/xx"
            port Integer port number for connection
        '''
        self.bacnet = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((ip, port))
            self.host_ip = s.getsockname()[0]
            s.close()
            self.bacnet = BAC0.connect(ip=self.host_ip)                
        except Exception as e:
            print(e)
            
    def disconnect(self):
        '''
        Disconnect from the BACnet network.
        
        Returns:
            The string '1' if the disconnect succeeded, '-1' if it failed. 
        '''
        if self.bacnet is not None:        
            try:
                self.bacnet.disconnect()
            except Exception as e:
                print(e)
                return '-1'
            return '1'
            
    def read(self, address, ptype, baddr, pname='presentValue'):
        '''
        Read a value from a BACnet device.
        
        Args:
            address: String representation of the device address. In the format of IP and port or the network:device "xx:yy" 
                Bacnet address.
            ptype: Bacnet object type as a string, eg "analogOutput" or "analogValue"
            baddr: Object instance number as a string, eg "1"
            pname: Property value name as a string.
        Returns:
            A string of the returned value or None if the read failed.
        '''
        if self.bacnet is not None:
            try:
                out = self.bacnet.read(f'{address} {ptype} {baddr} {pname}')
            except Exception as e:
                print(e)
                return -1
            return str(out)
        return None

    def write(self, address, ptype, baddr, pvalue, pname='presentValue', priority=6):
        '''
        Write a value to a BACnet device.
        
        Args:
            address: String representation of the device address. In the format of IP and port or the network:device "xx:yy" 
                Bacnet address.
            ptype: Bacnet object type as a string, eg "analogOutput" or "analogValue"
            baddr: Object instance number as a string, eg "1"
            pname: Property value name as a string.
            pvalue: The new value as a string. 
            priority: Priority as a string.
        Returns:
            The string '1' if the write succeeded, '-1' if it failed.
        '''
        if self.bacnet is not None:
            try:
                self.bacnet.write(f'{address} {ptype} {baddr} {pname} {pvalue} - {priority}')
            except Exception as e:
                print(e)
                return '-1'
            return '1'

