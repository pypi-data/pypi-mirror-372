import json

from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from builtins import isinstance

class Server(BaseHTTPRequestHandler):
    '''
    Basic HTTP server to mock endpoint functionality.
    
    Params:
        data: Dictionary of String paths lists of data to be sent in response to the requests and potentially a dictionary
            of query parameters (string keys to string values) that must be matched to get the response.
    '''
        
    def __init__(self, data, *args, **kwargs):
        '''
        The default constructor.
        
        Args:
            data: Dictionary of String paths lists of data to be sent in response to the requests and potentially a 
                dictionary of query parameters (string keys to string values) that must be matched to get the response.
        '''
        self.data = data
        super().__init__(*args, **kwargs)    
        
    def do_GET(self):
        '''
        Handle get requests
        '''
        
        self._handle_call("GET")
        
    def do_POST(self):
        '''
        Handle post requests
        '''
        
        self._handle_call("POST")
        
    def do_PUT(self):
        '''
        Handle put requests
        '''
        
        self._handle_call("PUT")
    
    def construct_response(self, endpoint):
        '''
        Reply with the given data.
        
        Args:
            endpoint: An endpoint definition from the json configuration file, 
        '''
        
        # Get the response content
        content = endpoint["content"]
        
        self.send_response(200)
        
        # Detect content type from the endpoint definition
        if "content-type" in endpoint:
            self.send_header('Content-type', endpoint["content-type"])
        else:
            self.send_header('Content-type', "text/plain")
            
        self.end_headers()
        
        # Write the content either as JSON for a dictionary or a raw string
        if isinstance(content, dict):
            self.wfile.write(json.dumps(content).encode())
        else:
            self.wfile.write(str(content).encode())
            
    def _handle_call(self, method):
        '''
        Respond approrpiately to the given method call.
        
        Args:
            method: String for the HTTP method invoked. "GET", "PUT", etc.
        '''
        
        # Get the path the request was for.
        parsed_url = urlparse(self.path)

        # If path is supported, try to construct a response
        if parsed_url.path in self.data:
        
            # Get the query parameters from the request url
            parameters = parse_qs(parsed_url.query)
            
            # Whether or not a valid response was found to the user's request
            found = False
            
            # Check each potential endpoint defined for the requested path
            for endpoint in self.data[parsed_url.path]:
                
                found = True
                
                # Check that the method matches
                if "method" in endpoint and endpoint["method"] != method:
                    found = False
                    break
                
                # If query parameters are defined, check the request against them
                if "query parameters" in endpoint:
                    
                    # Every query parameter defined must exist in the request and must have the requested value, or there
                    # is no match
                    for param in endpoint["query parameters"]:
                        
                        if not param in parameters or endpoint["query parameters"][param] != parameters[param][0]:
                            found = False
                            
                            break
                    
                    # If all checks passed, reply with this endpoint's data
                    if found:
                        self.construct_response(endpoint)
                            
                        break
                    
                # If no query parameters were defined, then this is the default endpoint for when no others matched, so 
                # reply with it.
                else:
                    self.construct_response(endpoint)
                    
            # If no endpoints matched and there was no default, send a 404.    
            if not found:
                self.send_response(404)
                self.end_headers()
                self.wfile.write("")          
        
        # Path was not recognized, send a 404 response
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("")
        
    
class HTTPEmulatorBase():
    '''
    Emulator for an HTTP API.
    
    Parameters:
        data: Dictionary of paths to endpoint responses.
        port: Integer for port number to listen on.
    '''
    
    def __init__(self, port=8008, data={}):
        '''
        The default constructor.
        
        Args:
            data: Dictionary of endpoint definitions, in the following format:
                {
                    "/path" : [
                        {
                            "method": "GET",
                            "content-type": "application/json",
                            "data": {
                                "my_value": "Content for /path?param1=foo",
                                "value": "Content for /path?param1=foo"
                            },
                            "query parameters": {
                                "param1": "foo"
                            }
                        },
                        {
                            "content-type": "application/json",
                            "data": {
                                "value": "Default content for /path when param1 is not defined or =/= foo"
                            }
                        }
                    ],
                    "/other/path": [
                        ...
                    ],
                    ...
                }
            port: Integer for port number to listen on.
        '''
        
        self.data = data
        self.port = port
    
    def start(self):
        '''
        Start the server
        '''
        
        # Create and stand up a server
        custom_server = partial(Server, self.data)
        self.server = HTTPServer(('', self.port), custom_server)
        self.server.serve_forever()
        
    def stop(self):
        '''
        Stop the server
        '''
        
        self.server.shutdown()
