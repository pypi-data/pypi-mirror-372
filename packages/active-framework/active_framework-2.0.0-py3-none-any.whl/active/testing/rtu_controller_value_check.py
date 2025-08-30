from active.testing.decorators import ActiveTestStep

@ActiveTestStep("RTU Controller Value Check")
def rtu_controller_value_check(controller, skip, values):
    '''
    Perform a test on an RTU Controller, checking that all outputs can be returned and are as expected given user values.
    
    The list of parameters that can be tested is:
        cooling_coil_electricity_rate
        cooling_coil_inlet_temperature
        fan_electricity_rate
        fan_schedule
        heating_coil_electricity_rate
        heating_coil_outlet_temperature
        heating_coil_set_point
        outdoor_air_temperature
        actuator_temperature
        actuator_inlet_mass_flow_rate
        cooling_load
        cooling_set_point
        enthalpy
        fan_electricity_rate
        floor_area
        floor_volume
        heating_load
        heating_set_point
        humidity
        inlet_density
        inlet_enthalpy
        inlet_humidity
        inlet_specific_heat
        inlet_temperature
        relative_humidity
        supply_airflow_rate
        temperature
    
    Args:
        controller: A ClockController to test.
        skip: A list of parameters to not test, for cases where part of the interface is not supported.
        value: Dictionary from string parameter names to a dictionary with keys of "min" and "max". If either is defined, the return
            value will be tested to ensure it is above and/or below the listed values.
    Return:
        A list of Strings, providing human readable explanations for each error that occurred. An empty list represents a passing test.
    '''
    
    errors = []
    
    if not "cooling_coil_electricity_rate" in skip:
        curr_values = get_user_values("cooling_coil_electricity_rate", values)
        errors.extend(test_function(controller.get_cooling_coil_electricity_rate, curr_values))
        
    if not "cooling_coil_inlet_temperature" in skip:
        curr_values = get_user_values("cooling_coil_inlet_temperature", values)
        errors.extend(test_function(controller.get_cooling_coil_inlet_temperature, curr_values))
        
    if not "fan_electricity_rate" in skip:
        curr_values = get_user_values("fan_electricity_rate", values)
        errors.extend(test_function(controller.get_fan_electricity_rate, curr_values))
        
    if not "fan_schedule" in skip:
        curr_values = get_user_values("fan_schedule", values)
        errors.extend(test_function(controller.get_fan_schedule, curr_values))
        
    if not "heating_coil_electricity_rate" in skip:
        curr_values = get_user_values("heating_coil_electricity_rate", values)
        errors.extend(test_function(controller.get_heating_coil_electricity_rate, curr_values))
        
    if not "heating_coil_outlet_temperature" in skip:
        curr_values = get_user_values("heating_coil_outlet_temperature", values)
        errors.extend(test_function(controller.get_heating_coil_outlet_temperature, curr_values))
        
    if not "heating_coil_set_point" in skip:
        curr_values = get_user_values("heating_coil_set_point", values)
        errors.extend(test_function(controller.get_heating_coil_set_point, curr_values))
        
    if not "outdoor_air_temperature" in skip:
        curr_values = get_user_values("outdoor_air_temperature", values)
        errors.extend(test_function(controller.get_outdoor_air_temperature, curr_values))
        
    # Unless all vav parameters were skipped, log an error if there are no VAVs.
    if len(controller.vavs) == 0:
        
        vav_parameters = ["actuator_temperature", "actuator_inlet_mass_flow_rate", "cooling_load", "cooling_set_point", "enthalpy", 
                          "fan_electricity_rate", "floor_area", "floor_volume", "heating_load", "heating_set_point", "humidity", 
                          "inlet_density", "inlet_enthalpy", "inlet_humidity", "inlet_humidity", "inlet_specific_heat", 
                          "inlet_temperature", "relative_humidity", "supply_airflow_rate", "temperature"]
        
        for vav_parameter in vav_parameters:
            if not vav_parameter in skip:
                errors.append("No VAVs defined for controller, but VAV parameters were not all skipped.")
                break
        
    #Also test each VAV unit
    for vav in controller.vavs:
        
        if not "actuator_temperature" in skip:
            curr_values = get_user_values("actuator_temperature", values)
            errors.extend(test_function(controller.get_actuator_temperature, curr_values))
            
        if not "actuator_inlet_mass_flow_rate" in skip:
            curr_values = get_user_values("actuator_inlet_mass_flow_rate", values)
            errors.extend(test_function(controller.get_actuator_inlet_mass_flow_rate, curr_values))
            
        if not "cooling_load" in skip:
            curr_values = get_user_values("cooling_load", values)
            errors.extend(test_function(controller.get_cooling_load, curr_values))
            
        if not "cooling_set_point" in skip:
            curr_values = get_user_values("cooling_set_point", values)
            errors.extend(test_function(controller.get_cooling_set_point, curr_values))
            
        if not "enthalpy" in skip:
            curr_values = get_user_values("enthalpy", values)
            errors.extend(test_function(controller.get_enthalpy, curr_values))
            
        if not "fan_electricity_rate" in skip:
            curr_values = get_user_values("fan_electricity_rate", values)
            errors.extend(test_function(controller.get_fan_electricity_rate, curr_values))
            
        if not "floor_area" in skip:
            curr_values = get_user_values("floor_area", values)
            errors.extend(test_function(controller.get_floor_area, curr_values))
            
        if not "floor_volume" in skip:
            curr_values = get_user_values("floor_volume", values)
            errors.extend(test_function(controller.get_floor_volume, curr_values))
            
        if not "heating_load" in skip:
            curr_values = get_user_values("heating_load", values)
            errors.extend(test_function(controller.get_heating_load, curr_values))
            
        if not "heating_set_point" in skip:
            curr_values = get_user_values("heating_set_point", values)
            errors.extend(test_function(controller.get_heating_set_point, curr_values))
            
        if not "humidity" in skip:
            curr_values = get_user_values("humidity", values)
            errors.extend(test_function(controller.get_humidity, curr_values))
            
        if not "inlet_density" in skip:
            curr_values = get_user_values("inlet_density", values)
            errors.extend(test_function(controller.get_inlet_density, curr_values))
            
        if not "inlet_enthalpy" in skip:
            curr_values = get_user_values("inlet_enthalpy", values)
            errors.extend(test_function(controller.get_inlet_enthalpy, curr_values))
            
        if not "inlet_humidity" in skip:
            curr_values = get_user_values("inlet_humidity", values)
            errors.extend(test_function(controller.get_inlet_humidity, curr_values))
            
        if not "inlet_specific_heat" in skip:
            curr_values = get_user_values("inlet_specific_heat", values)
            errors.extend(test_function(controller.get_inlet_specific_heat, curr_values))
            
        if not "inlet_temperature" in skip:
            curr_values = get_user_values("inlet_temperature", values)
            errors.extend(test_function(controller.get_inlet_temperature, curr_values))
            
        if not "relative_humidity" in skip:
            curr_values = get_user_values("relative_humidity", values)
            errors.extend(test_function(controller.get_relative_humidity, curr_values))
            
        if not "supply_airflow_rate" in skip:
            curr_values = get_user_values("supply_airflow_rate", values)
            errors.extend(test_function(controller.get_supply_airflow_rate, curr_values))
            
        if not "temperature" in skip:
            curr_values = get_user_values("temperature", values)
            errors.extend(test_function(controller.get_temperature, curr_values))
        
    return errors