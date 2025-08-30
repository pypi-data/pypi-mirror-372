from active.testing.decorators import ActiveTestStep

@ActiveTestStep("Clock Controller Value Check")
def clock_controller_value_check(controller, skip, values):
    '''
    Perform a test on a Clock Controller, checking that all outputs can be returned and are as expected given user values.
    
    The list of parameters that can be tested is:
        time
    
    Args:
        controller: A ClockController to test.
        skip: A list of parameters to not test, for cases where part of the interface is not supported.
        value: Dictionary from string parameter names to a dictionary with keys of "min" and "max". If either is defined, the return
            value will be tested to ensure it is above and/or below the listed values.
    Return:
        A list of Strings, providing human readable explanations for each error that occurred. An empty list represents a passing test.
    '''
    
    errors = []
    
    if not "time" in skip:
        curr_values = get_user_values("time", values)
        errors.extend(test_function(controller.get_time, curr_values))
        
    return errors