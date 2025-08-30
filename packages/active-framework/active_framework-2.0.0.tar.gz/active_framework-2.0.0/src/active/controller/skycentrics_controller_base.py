import hashlib
import hmac
import base64
import requests
import time
from email.utils import formatdate

class SkycentricsControllerBase():
    '''
    Business logic implementation for a Skycentrics Controller.
    
    ACTIVE environment file prototype:
    
    {
        "client_id": "abcdefg", 
        "client_secret": "hijklm", 
        "device_mac": "0a0a0a0a0a", 
        "password": "password1", 
        "url": "https://api.skycentrics.com", 
        "username": "myname@company.com"
    }
    
    Parameters:
        _cache: Dictionary of cached device data for the current transaction.
        client_id: String Skycentrics client id
        client_secret: String Skycentrics client secret
        device_mac: String name for this device in Skycentrics
        url: URL for the Skycentrics API
    '''

    def __init__(self, client_id="", client_secret="", device_mac="", password="", url="https://api.skycentrics.com", username=""):
        '''
        The default constructor.
        
        Parameters:
            client_id: String Skycentrics client id
            client_secret: String Skycentrics client secret
            device_mac: String name for this device in Skycentrics
            password: String Skycentrics account password
            url: URL for the Skycentrics API
            username: String Skycentrics username
        '''
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_mac = device_mac
        self.url = url
        
        # Calculate the user token
        token_content = username + ':' + hashlib.md5(password.encode('utf-8')).hexdigest()
        self.user_token =  base64.b64encode(token_content.encode('utf-8')).decode()
        
        # Get the metadata
        self.metadata = self._get_metadata(device_mac)
        
        self._cache = None
    
    def get_device_data(self):
        '''
        Get this device's data
        
        Return:
            An HTTP response for the device's data
        '''
        
        reqLine = '/api/devices/' + str(self.metadata['id']) + '/data' 
        urlDevice = self.url + reqLine
        httpDate = str(self._get_current_date_http())
        apiToken = str(self._create_api_token("GET " + reqLine + " HTTP/1.1", httpDate, '', ''))
                
        reqHeader = {"x-sc-api-token": apiToken, "Date": httpDate, "Accept":"application/json"}
        
        attempts = 0
        
        while attempts < 50:
        
            try:
                
                response = requests.get(urlDevice, headers = reqHeader).json()
                if "error" in response:
                    print("Error getting device data from SkycentricsApi: " + str(response['error']['message']))
                    attempts += 1
                    time.sleep(1)
                    continue
                
                return response
                           
            except requests.exceptions.RequestException as e:
                print(e)
                attempts += 1
                time.sleep(1)
                
        return []
    
    def set_device_parameter(self, parameter_url, payload):
        '''Send a PUT to the remote URL, ending with the url, with the payload
        
        Args:
            parameter_url: String ending segment of the url to PUT to, everything past "/api/device/{deviceID}/"
            payload: The payload for the PUT, as a JSON string, for the new parameter values
        '''    
        
        reqLine = '/api/devices/' + str(self.metadata['id']) + '/' + parameter_url
        urlDevice = self.url + reqLine
        httpDate = str(self._get_current_date_http())
        
        apiToken = str(self._create_custom_authentication_token("PUT " + reqLine + " HTTP/1.1", httpDate, payload))
        
        reqHeader = {"x-sc-api-token": apiToken, "Date": httpDate, "Content-Type":"application/json" , "Accept":"application/json"}
        try:    
            response  = requests.put(urlDevice, headers = reqHeader, data = (payload))
                       
        except requests.exceptions.RequestException as e:
            print(e)
            
    def start_transaction(self):
        '''
        Start a transaction by caching the device data.
        '''
        
        self._cache = self.get_device_data()
            
    def stop_transaction(self):
        '''
        End the current transaction by deleting the cached data.
        '''
        
        self._cache = None

    def _create_api_token(self, reqLine, date, contentType, contentData):
        '''
        creates the API token based on the information provided following this rule
        Refer to Skycentrics API doc for more information
        
        Args:
            reqLine: The API url string to generate the token for as a string
            date: The current date as a string
            contentType: The type of the content for the token as a string
            contentData: The data to be sent alongside the token as a string
        Return:
            The API token as a string
        '''
        
        data =  reqLine+ '\n' + date + '\n' + contentType + '\n' + hashlib.md5(contentData.encode("utf-8")).hexdigest()
        hash = hmac.new(self.client_secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
        return self.client_id + ':' + base64.b64encode(hash).decode().rstrip('\n')
    
    def _create_custom_authentication_token(self, reqLine, date, contentData):
        '''
        creates the API custom authentication token based on the information provided following this rule
        Refer to Skycentrics API doc for more information
        
        @param reqLine: A string of PUT + the trailing url for the API call + HTTP/1.1
        @param date: The formatted date string
        @param contentData: The content of the PUT 
        Return:
            The custom authentication token as a string
        '''

        data =  reqLine+ '\n' + date + '\n' + 'application/json' + '\n' + hashlib.md5(contentData.encode("utf-8")).hexdigest()
        hash = hmac.new(self.client_secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
        return self.client_id + ':' + base64.b64encode(hash).decode().rstrip('\n')     
    
    def _get_current_date_http(self):
        '''
        returns the current date in HTTP-Date format
        '''
        return formatdate(None, False, True)
    
    def _get_metadata(self, device_mac):
        '''
        Gets the list of devices loaded on Skycentrics API
        
        Args:
            device_mac: The string for the MAC of the device whose metadata is sought
        Return:
            Dictionary of metadata for the device, or an empty dictionary if the MAC was not found
        '''
        
        reqLine = '/api/devices/?auth=' + self.user_token  
        urlDevice = self.url + reqLine
        httpDate = str(self._get_current_date_http())
        
        apiToken = str(self._create_api_token("GET " + reqLine + " HTTP/1.1", httpDate, '', ''))
                
        reqHeader = {"x-sc-api-token": apiToken, "Date": httpDate}
        
        attempts = 0
        
        while attempts < 100:
        
            try:
                
                response = requests.get(urlDevice, headers = reqHeader)
                
                if "error" in response:
                    print("Error getting device list from SkycentricsApi: " + str(response['error']['message']))
                    attempts += 1
                    time.sleep(1)
                    continue
                
                device_list = response.json()
                
                for device in device_list:
                    
                    if str(device['mac']) == device_mac:
                        return device
                           
            except Exception as e:
                print("Error getting skycentrics device list ")
                print(e)
                attempts += 1
                time.sleep(1)
            
        #In case of failure, return an empty dictionary
        return {}
    
    
