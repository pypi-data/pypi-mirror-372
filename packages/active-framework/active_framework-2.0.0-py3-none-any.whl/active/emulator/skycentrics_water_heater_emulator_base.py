import base64
import hashlib
import hmac

from datetime import datetime
from email.utils import formatdate
from urllib.parse import urlparse

from active.emulator.http_emulator_base import HTTPEmulatorBase, Server

def _create_api_token(self, reqLine, date, contentType, contentData):
    '''
        creates the API token based on the information provided following this rule
        Refer to Skycentrics API doc for more information
        
    '''
    
    data =  reqLine+ '\n' + date + '\n' + contentType + '\n' + hashlib.md5(contentData).hexdigest()
        
    return self.client_id + ':' + hmac.new(self.client_secret, data, hashlib.sha1).digest().encode('base64').rstrip('\n')   
                                   
def _create_custom_authentication_token(self, reqLine, date, contentData):
    '''
        creates the API custom authentication token based on the information provided following this rule
        Refer to Skycentrics API doc for more information
        
        @param reqLine: A string of PUT + the trailing url for the API call + HTTP/1.1
        @param date: The formatted date string
        @param contentData: The content of the PUT 
        
    '''

    return self.client_id + ':' + hmac.new(self.client_secret,
                                   reqLine + '\n' +
                                   date + '\n' +
                                   'application/json' + '\n' +
                                   hashlib.md5(contentData).hexdigest(),
                                   hashlib.sha1).digest().encode('base64').rstrip('\n')      
                                   
def _get_current_date_http(self):
    '''
    returns the current date in HTTP-Date format
    '''
    return formatdate(None, False, True)      

class SkycentricsWaterHeaterServer(Server):
    '''
    
    '''
    
    def __init__(self, client_secret, data, *args, **kwargs):
        '''
        The default constructor.
        
        Args:
            data: Dictionary of String paths lists of data to be sent in response to the requests and potentially a 
                dictionary of query parameters (string keys to string values) that must be matched to get the response.
        '''
        
        super().__init__(data, *args, **kwargs)    
        self.client_secret = client_secret
         
    def do_GET(self):
        '''
        Handle get requests
        '''
        
        recv_token = self.headers.get("x-sc-api-token")
        correct_token = str(_create_api_token("GET " + urlparse(self.path).path + " HTTP/1.1", _get_current_date_http(), '', ''))
        
        if not recv_token == correct_token:
            self.send_response(401)
            self.end_headers()
            self.wfile.write({})
            return
        
        self._handle_call("GET")
        
    def do_PUT(self):
        '''
        Handle put requests
        '''

        recv_token = self.headers.get("x-sc-api-token")
        correct_token = str(self._create_custom_authentication_token("PUT " + urlparse(self.path).path + " HTTP/1.1", _get_current_date_http(), self.rfile.read()))

        if not recv_token == correct_token:
            self.send_response(401)
            self.end_headers()
            self.wfile.write({})
            return
        
        self._handle_call("PUT")
    

class SkycentricsWaterHeaterEmulatorBase(HTTPEmulatorBase):
    '''
    Business logic for an emulator for a water heater from the Skycentrics API.
    
    Parameters:
        data: Dictionary of paths to endpoint responses.
        port: Integer for port number to listen on.
    '''
    
    def __init__(self, capacity=0, id="0", name="water heater 0", override=0, password="test skycentrics password", port=8008, power=0, state=0, 
                 username="test skycentrics username"):
        '''
        The default constructor.
        
        Args:
            port: Integer for port number to listen on.
        '''
        
        # data = {
        #     "/api/devices" + id + "/data": [
        #         {
        #             "method": "GET",
        #             "content-type": "application/json",
        #             "data": {
        #                 "commodities": [
        #                     {
        #                         "code": 0,
        #                         "instantaneous": power
        #                     },
        #                     {
        #                         "code": 7,
        #                         "cumulative": capacity
        #                     }
        #                 ],
        #                 "last_heartbeat": str(datetime.now()),
        #                 "override": override,
        #                 "state": state
        #             }
        #         },
        #         {
        #             "method": "PUT",
        #             "content-type": "application/json",
        #             "data": {
        #             }
        #         },
        #     ],
        #     "/api/devices": [
        #         {
        #             "method": "GET",
        #             "content-type": "application/json",
        #             "data": [
        #                 {
        #                     "id": id,
        #                     "name": name
        #                 }
        #             ],
        #             "query parameters": {
        #                 "auth": base64.b64encode(username + ':' + hashlib.md5(password).hexdigest())
        #             }
        #         }
        #     ]
        # }
        

    
    def start(self):
        '''
        Start the server
        '''
        pass
        
        # # Create and stand up a server
        # custom_server = partial(SkycentricsWaterHeaterServer, self.data)
        # self.server = HTTPServer(('', self.port), custom_server)
        # self.server.serve_forever()
        