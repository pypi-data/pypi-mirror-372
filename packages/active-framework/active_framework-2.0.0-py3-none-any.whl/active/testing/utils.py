def get_user_values(parameter, values):
    '''
    Get the dictionary of values for the specified parameter
    
    Args:
        parameter String name for the parameter's whose user defined required values are sought
        values Dictionary of all user defined parameter values
    Return:
        An empty dictionary if there were no user defined values for this parameter, or the dictionary of user defined parameters if it
        was defined.
    '''
    
    curr_values = {}
    
    if parameter in values:
        curr_values = values[parameter]
        
    return curr_values
    
def test_function(function, values):
    '''
    Test the given function, checking that the function returns and produces a value within any constrains specified.
    
    Args:
        function Callable function to be tested. Must not have arguments.
        values Dictionary which may have keys "min" and/or "max" to represent the valid range of the function's return values.
    Return:
        A list of Strings of any exceptions thrown, if NotImplemented was returned, or any violations of contstraints listed in 
        values.
    '''
    
    errors = []
    
    try:
        returned = function()
    except Exception as e:
        errors.append(str(function.__name__) + " threw exception: " + str(e))
        return errors
    
    if returned == NotImplemented:
        
        errors.append(str(function.__name__) + " is not implemented. If your device does not support this operation, this parameter " \
                      + "should be added to the list of skipped parameters in the test.")
        
    else:
        if "min" in values:
            if returned < values["min"]:
                errors.append(str(function.__name__) + " returned " + str(returned) + " which is less than minimum expected value " \
                            + str(values["min"]))
                
        if "min" in values:
            if returned < values["min"]:
                errors.append(str(function.__name__) + " returned " + str(returned) + " which is less than minimum expected value " \
                            + str(values["min"]))
        
    return errors   
    