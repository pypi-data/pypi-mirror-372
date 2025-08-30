class DataStore():
        
    def copy(self, id, input):
        '''
        Copy the data to the store under the given id, appending to existing data as appropriate
        
        Args:
            id: The store specific identification method to specify data location, as a string
            input: The data to save
        '''
        
        return NotImplemented
        
        
    def copy_file(self, id, input):
        '''
        Copy the data in the given file to the store under the given id, appending to existing data as appropriate
        
        Args:
            id: The name of the category to save the input.
            input: String path to the file whose data should be copied
        '''
        
        return NotImplemented      
    
    def get_ids(self):
        '''
        Get a list of IDs which represent the top level partitions of data within the data store, of the kind
        which a user may wish to iterate through in order to view all sub-divisions of data.
        
        Return:
            A list of strings of data store specific IDs.
        '''
        
        return NotImplemented
    
    def get_names(self, id):
        '''
        Get the names of individual records under the subdivision named "id".
        
        Args:
            id: String for a data store specific subdivision of data
        Returns:
            A list of string names for records 
        '''
        
        return NotImplemented
    
    def get_visualization_type(self):
        '''
        Get a human readable visualization type, describing how data in this data store might be visualized.
        
        Valid values are:
        
        DATAFRAME: load() can be counted on to return data in a format which can be converted into a 
            dataframe. Visualization will be a graph with the x axis being a timestamp column and all
            numerical columns plottable on the y axis.
        FILES: load() will return the contents of an arbitrary file, which might be csv, an image, text, etc.
        NONE: This data store does not fit any of the other defined categories.
        
        Returns:
            One of the strings listed above.
        '''
        
        # Data stores have no guaranteed format by default.
        return "NONE"
    
    def load(self, id, name=None, num_items=None):
        '''
        Load up to the given number of store specific items (eg lines in a file, rows in a database, etc)
        
        Args:
            id: The store specific identification method to specify data location, as a string
            num_items: Number of store specific items to load, from the end of the store (eg most recent). A value of 
                None represents loading all data.
        '''
        
        return NotImplemented
        
    def load_to_file(self, id, name, path):
        '''
        Load the named data to a local file.
        
        Args:
            id: The name of the category to retrieve the input from.
            name: The name of the data to load.
            path: The path to save the file to.
        '''
        
        return NotImplemented
        
    def save(self, id, input):
        '''
        Move the file to a folder named id under own path.
        
        Args:
            id: The name of the category to save the input.
            input: String path to the file to save.
        '''
        
        return NotImplemented
        
    def set_timestamp(self):
        '''
        Set any saved data's timestamp equal to the current time, ensuring timestamp consistency over multiple copy/save
        operations
        '''
        
        return NotImplemented
    