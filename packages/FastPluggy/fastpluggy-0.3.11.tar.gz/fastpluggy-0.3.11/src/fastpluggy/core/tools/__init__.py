def convert_param_type(param_type, value):
    if param_type == 'int' or param_type == int:
        return int(value)
    elif param_type == 'float' or param_type == float:
        return float(value)
    elif param_type == 'bool' or param_type == bool:
        if type(value) is bool:
            return bool(value)
        return value.lower() in ('true', '1', 'y')
    else:
        return value  # Default is string
