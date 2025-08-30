import requests

class HTTPControllerBase():
    '''
    Controller for communications with an HTTP based API.
    
    ACTIVE Environment file parameters prototype:
    
    {
        "name": "API1",
        "type": "HTTP",
        "parameters": {
            "url": "http:/127.0.0.1:80"
        }
    }
    
    Parameters:
        session: requests session for HTTP.
        url: String url for the base address, with no trailing /
    '''
    
    def __init__(self, url=""):
        '''
        Default constructor.
        
        Args:
            url: String base url all other requests will be appended to.
        '''
        
        self.session = requests.Session()
        self.url = url
        
        # Ensure that the url lacks the trailing /
        if self.url.endswith("/"):
            self.url = self.url[:-1]

        
    def get(self, path):
        '''
        Perform a GET operation on the given path.
        
        Args:
            path: String path for the endpoint. A GET will be performed on (url + path)
        Return
            The String content returned by the endpoint.
        '''
        
        # Ensure that the path starts with a /
        full_path = path
        if not full_path.startswith("/"):
            full_path = "/" + full_path
            
        return requests.get(self.url + full_path).content.decode("utf-8")
    
    def get_json(self, path, headers={}):
        '''
        Perform a GET operation on the given path and format the returned value as json.
        
        Args:
            path: String path for the endpoint. A GET will be performed on (url + path)
            headers: Dictionary from strings to strings to include as headers for the request.
        Return
            The dictionary of JSON formatted content returned by the endpoint.
        '''
        
        # Ensure that the path starts with a /
        full_path = path
        if not full_path.startswith("/"):
            full_path = "/" + full_path

        return requests.get(self.url + full_path, headers=headers).json()
    
    def post(self, path, payload, headers={}):
        '''
        Perform a POST operation on the given path with the given data and headers.
        
        Args
            path: String path for the endpoint. A PUT will be performed on (url + path)
            payload: The data, of any time, to be sent with the PUT.
            headers: Dictionary of Strings to Strings, defining all content headers.
        Return
            The String content returned by the endpoint.
        '''
        
        # Ensure that the path starts with a /
        full_path = path
        if not full_path.startswith("/"):
            full_path = "/" + full_path
            
        return requests.post(self.url + full_path, data = payload, headers = headers).content.decode("utf-8")
    
    def put(self, path, payload, headers={}):
        '''
        Perform a PUT operation on the given path with the given data and headers.
        
        Args
            path: String path for the endpoint. A PUT will be performed on (url + path)
            payload: The data, of any time, to be sent with the PUT.
            headers: Dictionary of Strings to Strings, defining all content headers.
        Return
            The String content returned by the endpoint.
        '''
        
        # Ensure that the path starts with a /
        full_path = path
        if not full_path.startswith("/"):
            full_path = "/" + full_path
            
        return requests.put(self.url + full_path, data = payload, headers = headers).content.decode("utf-8")

