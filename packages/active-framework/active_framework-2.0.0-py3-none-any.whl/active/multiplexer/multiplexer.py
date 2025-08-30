class Multiplexer():
    '''
    A class that aggregates one or more Controllers and/or DataStores so that they can be used together as a unit with 
    greater functionality.
    '''
    
    def __init__(self):
        '''
        The default constructor
        '''
        
        pass
    
    def end_transaction(self):
        '''
        End the current transaction.
        '''
        
        self._unset_timestamps()
    
    def start_transaction(self):
        '''
        Begin a transaction, a set of calls which should be logically treated as ocuring simultaneously even if the 
        implementation may require multiple calls to perform all functionality.
        '''
        
        self._set_timestamps()
        
    def _set_timestamps(self):
        '''
        Set any timestamps associated with the calls to the sub-Components.
        '''
        
        raise NotImplemented
    
    def _unset_timestamps(self):
        '''
        Unset any timestamps associated with the calls to the sub-Components.
        '''
        
        raise NotImplemented
    