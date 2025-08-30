def ActiveDataStore(name):
    '''
    Decorator for a DataStore.
    
    Usage: 
    @ActiveDataStore("My DataStore Name")
    class MyDataStore()
    
    Args:
        name String specifying the unique name that the DataStore will be referenced by.
    '''
    
    def ActiveDataStoreDecorator(data_store_class):
        
        # On import, register the new DataStore with the factory
        DataStoreFactory.register(data_store_class, name)
    return ActiveDataStoreDecorator

# Factories don't need to be imported until after Decorators are defined, and need to be deferred to prevent circular imports
# from default Factories registerations.
from active.datastore.data_store_factory import DataStoreFactory