import threading

from intersect_sdk import (
    INTERSECT_JSON_VALUE,
    IntersectClient,
    IntersectClientCallback,
    IntersectClientConfig,
    IntersectDirectMessageParams,
    default_intersect_lifecycle_loop,
)

class IntersectExecution():
    '''
    The execution handler for a single INTERSECT message and its reply
    
    Params:
        client: INTNERSECT Client that will handle sending the message and listening for its reply.
        message_handler: Callable to invoke for handling the reply message
        stop: Boolean flag for whether the execution is ready to stop looping
    '''
    
    def __init__(self, client_config, message_handler):
        '''
        The default constructor.
        
        Args:
            client_config: An IntersectClientCOnfig containing information on the INTERSECT connection information and 
                message to send.
            message_handler: Callable to invoke to handle a response
        '''
        
        # Flag for whether its time to stop looping while waiting for the service to respond
        self.stop = False
        self.message_handler = message_handler
        
        self.client = IntersectClient(
            config=client_config,
            user_callback=self.handle_message,
            event_callback=self._event_callback
        )
        
    def handle_message(
        self,
        _source: str,
        _operation: str,
        _has_error: bool,
        payload: INTERSECT_JSON_VALUE,
    ) -> None:   
        """
        Handler for responses to INTERSECT messages. Delegate to the IntersectController's handler function, then shutdown
        the client.

        Params:
          - _source: the source of the event
          - _operation: the name of the operation from the service which emitted the event.
          - has_error: Boolean flag for whether the service experienced an error.
          - payload: the actual value of the emitted event.
        """
        
        # Handle the message as specified by the Controller
        self.message_handler(_source, _operation, _has_error, payload)
        
        # Shutdown the client and stop the loop
        self.stop = True
        
    def start(self):
        '''
        Start the client, sending the message, and wait for a response.
        '''
        
        event = threading.Event()
        
        self.client.startup()
        while not self.stop:
            
            # If the client is disconnected and can't recover, stop without 
            if self.client.considered_unrecoverable():
                break
            event.wait(1)
            
        self.client.shutdown(reason='Execution ended.')
        
    def _event_callback(
        self,
        _source: str,
        _operation: str,
        _event_name: str,
        payload: INTERSECT_JSON_VALUE,
    ) -> None:
        '''
        Dummy event callback method solely to surpress the logging errors from INTERSECT.
        '''
        pass

class IntersectControllerBase():
    '''
    Controller for sending messages to an INTERSECT broker instance.
    
    ACTIVE Environment file parameters prototype
    
    {
        "name": "INTERSECT Instance",
        "type": "INTERSECT",
        "parameters": {
            "intersect_configuration": {
                "data_stores": {
                },
                "brokers": [
                    {
                        "host": "100.101.102.103",
                        "username": "intersect_username",
                        "password": "intersect_password",
                        "port": 1883,
                        "protocol": "mqtt3.1.1"
                    }
                ]
            }
        }
    }
    
    Parameters:
        event_handlers: Dictionary from string INTERSECT unique capability names to a dictionary of string event names to
            Callables to invoke in response to events of that type.
        intersect_configuration: Dictionary of values for defining the INTERSECT brokers and data stores. See INTERSECT's
            documentation for a full description.
        message_handlers: Dictionary from strings of the form "Capability.operation" as defined in INTERSECT to a dictionary
            of string operation names to Callables to invoke in response to messages from that operation.
    '''
    
    def __init__(self, intersect_configuration):
        '''
        The default constructor.
        '''
        
        self.event_handlers = {}
        self.intersect_configuration = intersect_configuration
        self.message_handlers = {}

    def handle_event(
        self,
        _source: str,
        _operation: str,
        _event_name: str,
        payload: INTERSECT_JSON_VALUE,
    ) -> None:
        """
        Handler for subscribed INTERSECT events. Dispatch the appropriate Callable from the Strategy according to event
        type.

        Params:
          - _source: the source of the event
          - _operation: the name of the operation from the service which emitted the event.
          - _event_name: the name of the event.
          - payload: the actual value of the emitted event.
        """

        # Find the source service
        for service in self.event_handlers:
            if service == _source:
                
                # Get the registered event types for this service
                event_types = self.event_handlers[service]["events"]
                
                # Find the sent event type and invoke the registered function
                for event_type in event_types.keys():
                    if event_type == _event_name:
                        #getattr(self.strategy, event_types[event_type])(payload)
                        event_types[event_type](payload)
                        return None
                    
        # Unexpected event. 
        print("Got unrecognized event " + _event_name + " from service " + _source)
        return None
        

    def handle_message(
        self,
        _source: str,
        _operation: str,
        _has_error: bool,
        payload: INTERSECT_JSON_VALUE,
    ) -> None:   
        """
        Handler for responses to INTERSECT messages. Dispatch the appropriate Callable from the Strategy based on 
        operation name.

        Params:
          - _source: the source of the event
          - _operation: the name of the operation from the service which emitted the event.
          - has_error: Boolean flag for whether the service experienced an error.
          - payload: the actual value of the emitted event.
        """
        
        # Find the source service
        for service in self.message_handlers:
            if service == _source:
                
                # Get the registered operations for this service
                operation_types = self.message_handlers[service]["messages"]
                
                # Find the responding operation type and invoke the registered function
                for operation_type in operation_types.keys():
                    if operation_type == _operation:
                        #getattr(self.stracontegy, operation_types[operation_type])(payload)
                        operation_types[operation_type](payload)
                        return None
                    
        # Unexpected message return
        print("Got unrecognized message from operation " + _operation + " and service " + _source)
        return None 
        
    def listen_forever(self):
        '''
        Listen to incoming events forever. This should only be invoked by an Agent.
        '''
        
        # Create the configuration with the list of services to listen to
        config = IntersectClientConfig(
            initial_message_event_config=IntersectClientCallback(
                services_to_start_listening_for_events=list(self.event_handlers.keys())
            ),
            **self.intersect_configuration,
        )
        
        # Create the client and run it in a loop infinitely
        client = IntersectClient(
            config=config,
            event_callback=self.handle_event
        )
        
        default_intersect_lifecycle_loop(
            client,
        )
        
    def send(self, destination, operation, payload):
        '''
        Send a message to an INTERSECT service.
        
        Args:
            destination: String for the INTERSECT capability's unique name.
            operation: String name of the operation to send the message to.
            payload: Arbitrary payload to send as the message's data.
        '''
        
        # Create an initial message consisting of the user defined message
        initial_messages = [
            IntersectDirectMessageParams(
                destination=destination,
                operation=operation,
                payload=payload,
            )
        ]
        
        # Create the configuration with that initial message
        config = IntersectClientConfig(
            initial_message_event_config=IntersectClientCallback(
                messages_to_send=initial_messages
            ),
            **self.intersect_configuration,
        )
        
        # Create an execution for sending the message and launch it in a new thread
        execution = IntersectExecution(config, self.handle_message)
        thread = threading.Thread(target = execution.start)
        thread.daemon = True
        thread.start()
        
    def send_and_wait(self, destination, operation, payload):
        '''
        Send a message to an INTERSECT service and handle the reply.
        
        Args:
            destination: String for the INTERSECT capability's unique name.
            operation: String name of the operation to send the message to.
            payload: Arbitrary payload to send as the message's data.
        '''
        
        # Create an initial message consisting of the user defined message
        initial_messages = [
            IntersectDirectMessageParams(
                destination=destination,
                operation=operation,
                payload=payload,
            )
        ]
        
        # Create the configuration with that initial message
        config = IntersectClientConfig(
            initial_message_event_config=IntersectClientCallback(
                messages_to_send=initial_messages
            ),
            **self.intersect_configuration,
        )
        
        # Create an execution for sending the message and launch it in a new thread
        execution = IntersectExecution(config, self.handle_message)
        thread = threading.Thread(target = execution.start)
        #thread.daemon = True
        thread.start()
        thread.join()
