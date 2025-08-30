from typing import Union

from active.agent.agent import Agent
from active.agent.decorators import ActiveAgent

from intersect_sdk import (
    INTERSECT_JSON_VALUE,
    IntersectClient,
    IntersectClientCallback,
    IntersectClientConfig,
    IntersectDirectMessageParams,
    default_intersect_lifecycle_loop,
)

@ActiveAgent("INTERSECT client")
class IntersectAgent(Agent):
    '''
    Agent for running a Strategy in response to INTERSECT events.
    
    ACTIVE configuration file parameters prototype:
    
    {
        "intersect_configuration": {
            "data_stores": {
                "minio": [
                    {
                        "host": "XXX.XXX.XXX.XXX",
                        "username": "minio_username",
                        "password": "minio_password",
                        "port": 30020,
                    },
                ],
            },
            "brokers": [
                {
                    "host": "XXX.XXX.XXX.XXX",
                    "username": "intersect_username",
                    "password": "intersect_password",
                    "port": 30011,
                    "protocol": "mqtt3.1.1",
                },
            ]
        },
        "service_mappings": {
            "facility.site.system.subsystem.service": {
                "events": {
                    "event_name": "event_callback"
                },
                "messages": {
                    "operation_name": "message_callback"
                }
            }
        }
    }
    
    Parameters:
        intersect_client: The INTERSECT Client being listened to.
        service_mappings: Dictionary from string INTERSECT service designations to maps of string INTERSECT event/operation
            names to string names of functions from the Strategy to call in response to that event type/operation. 
    '''
    
    def __init__(self, strategy, internal_active_parameters, intersect_client=None, service_mappings={}):
        '''
        Default constructor
        
        Args:
            strategy: The Strategy to run.
            internal_active_parameters: Dictionary of parameters from the ACTIVE configuration file
            intersect_configuration: A map of INTERSECT configuration values for brokers and data stores. See the INTERSECT
                documentation for a full description.
            service_mappings: Dictionary from string INTERSECT service designations to maps of string INTERSECT 
                event/operation names to string names of functions from the Strategy to call in response to that event
                type/operation. 
        '''
        
        super().__init__(strategy, internal_active_parameters)  
        
        # Parse service mappings by getting each function from the Strategy
        self.service_mappings = service_mappings    
        for service in self.service_mappings:
            for type in self.service_mappings[service]:
                for subtype in self.service_mappings[service][type]:
                    self.service_mappings[service][type][subtype] = getattr(self.strategy, self.service_mappings[service][type][subtype])
            
        self.client = intersect_client
        self.client.event_handlers = service_mappings
        self.client.message_handlers = service_mappings
        
        
        
        # # start listening to events from every service listed
        # config = IntersectClientConfig(
        #     initial_message_event_config=IntersectClientCallback(
        #         services_to_start_listening_for_events=list(service_mappings.keys())
        #     ),
        #     **intersect_configuration,
        # )
        #
        # self.client = IntersectClient(
        #     config=config,
        #     event_callback=self.event_callback,
        #     user_callback=self.user_callback,
        # )
        
    def event_callback(
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
        for service in self.service_mappings:
            if service == _source:
                
                # Get the registered event types for this service
                event_types = self.service_mappings[service]["events"]
                
                # Find the sent event type and invoke the registered function
                for event_type in event_types.keys():
                    if event_type == _event_name:
                        getattr(self.strategy, event_types[event_type])(payload)
                        return None
                    
        # Unexpected event. 
        print("Got unrecognized event " + _event_name + " from service " + _source)
        return None
        

    def user_callback(
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
        for service in self.service_mappings:
            if service == _source:
                
                # Get the registered operations for this service
                operation_types = self.service_mappings[service]["messages"]
                
                # Find the responding operation type and invoke the registered function
                for operation_type in operation_types.keys():
                    if operation_type == _operation:
                        getattr(self.stracontegy, operation_types[operation_type])(payload)
                        return None
                    
        # Unexpected message return
        print("Got unrecognized message from operation " + _operation + " and service " + _source)
        return None        

    def start(self):
        '''
        Run the Intersect client indefinitely
        '''
        
        # default_intersect_lifecycle_loop(
        #     self.client.client,
        # )
        self.client.listen_forever()
        