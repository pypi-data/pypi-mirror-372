import json
import os
import pathlib
import shutil

from  active.datastore.data_store import DataStore

class FileSystemDataStoreBase(DataStore):
    '''
    A DataStore that saves files to a local directory.
    
    '''
    
    def __init__(self, path):
        '''
        The default constructor.
    
        Args:
            path: String for the base path 
        '''
        
        self.path = path
        
    def copy(self, id, input):
        '''
        Copy the data to the end of the given file
        
        Args:
            id: The relative path of the file to save to as a String
            input: The content to append to the file
        '''
        
        # Get the full path name
        path2 = os.path.join(self.path, id)
        
        # Make directory structure
        pathlib.Path(path2).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path2, "a+") as target:
            if type(input) == dict:
                target.write(json.dumps(input))
            elif type(input) == list:
                
                full = ""
                
                for i in input:
                    
                    if type(i) == dict:
                        full = full + json.dumps(i)
                    else:
                        full = full + i
                        
                    full = full + ","
                    
            else:
                target.write(input)
        
        
    def copy_file(self, id, input):
        '''
        Copy the file to a folder named id under own path.
        
        Args:
            id: The name of the category to save the input.
            input: String path to the file to save.
        '''
        
        # Directory path
        dir_path = os.path.join(self.path, id)
        
        # Get the full new path
        path2 = os.path.join(self.path, id, os.path.basename(input))
    
        # make the directory if it oesn't exist
        if not os.path.exists(dir_path):
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        shutil.copyfile(input, path2)     
        
    def get_names(self, id):
        '''
        
        '''
        
        # Get the full new path
        path2 = os.path.join(self.path, id)
        
        return [ f.path for f in os.scandir(path2) if not f.is_dir() ]
        
    def get_ids(self):
        '''
        Get the names of subfolders in this folder.
        
        Return:
            A list of strings for each subfolder's name
        '''
        
        pathlib.Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        
        subfolders = [x[0] for x in os.walk(self.path)]
        
        subfolders.insert(0, self.path)
        
        return subfolders
        
    def get_visualization_type(self):
        '''
        Get a human readable visualization type, describing how data in this data store might be visualized.
        
        Return:
            The string "FILES"
        '''
        
        return "FILES"
    
    # def get(self, id, name):
    #
    #

        
    def load_to_file(self, id, name, path):
        '''
        Load the named data to a local file.
        
        Args:
            id: The name of the category to retrieve the input from.
            name: The name of the data to load.
            path: The path to save the file to.
        '''
        
        # Get the full new path
        path2 = os.path.join(self.path, id, name)
        
        os.rename(path2, path)
        
    def save(self, id, input):
        '''
        Move the file to a folder named id under own path.
        
        Args:
            id: The name of the category to save the input.
            input: String path to the file to save.
        '''
        
        # Directory path
        dir_path = os.path.join(self.path, id)
        
        # Get the full new path
        path2 = os.path.join(self.path, id, os.path.basename(input))
    
        # make the directory if it oesn't exist
        if not os.path.exists(dir_path):
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        shutil.copyfile(input, path2)
        os.remove(input)
        
    def set_timestamp(self):
        '''
        Not implemented. A file system will always manage its own timestamps
        '''
        
        pass
    