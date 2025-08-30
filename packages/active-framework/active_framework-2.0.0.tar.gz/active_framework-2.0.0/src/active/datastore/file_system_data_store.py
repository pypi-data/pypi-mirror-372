import os
import pathlib
import shutil

from active.datastore.decorators import ActiveDataStore
from active.datastore.file_system_data_store_base import FileSystemDataStoreBase 

@ActiveDataStore("File System")
class FileSystemDataStore(FileSystemDataStoreBase):
    '''
    A DataStore that saves files to a local directory.
    
    This ActiveDataStore is dynamically imported by ACTIVE, while the base class from which it inherits will be statically
    imported. This distinction is important because a Controller may be invoked through C bindings, in which case static
    class members will only be accessable from statically imported classes. In order to allow the data store to use static
    members, this empty subclass is neccesary purely for the dynamic import.
    '''
