class DataStoreFactory():
    '''
    Singleton factory for creating DataStores
    '''
    
    # Class level registry from DataStore names to classes
    registry = {}
    
    @staticmethod
    def get(name):
        '''
        Get the DataStore with the given name, if it exists.
        
        Args:
            name String name of the DataStore, as defined by the ActiveDataStore("name") decorator.
        Returns:
            The DataStore class with the given name if it exists. NoneType if it does not.
        '''
        if name in DataStoreFactory.registry:
            return DataStoreFactory.registry[name]
        
        return None
    
    @staticmethod
    def names():
        '''
        Get the names of all registered Strategies.
        
        Returns:
            A Set of Strings containing the name of every registered DataStore. 
        '''
        return DataStoreFactory.registry.keys()
    
    @staticmethod
    def register(data_store_class, name):
        '''
        Register a DataStore subclass with the given name.
        
        Args:
            data_store_class A Class that inherits from DataStore.
            name The String name to register data_store_class as. 
        '''
        DataStoreFactory.registry[name] = data_store_class


# Import our default DataStores after the class definition so that the factory will be finished importing by the time
# the DataStores try to automatically register themselves.
import active.datastore.file_system_data_store
import active.datastore.postgresql_data_store
import active.datastore.volttron_historian_data_store
    