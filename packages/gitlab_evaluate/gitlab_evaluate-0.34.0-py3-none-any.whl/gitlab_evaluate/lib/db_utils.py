from dataclasses import dataclass
from typing import Optional, get_args

from copy import deepcopy as copy
from dacite import from_dict

db_dc_mapping = {
    int: 'INTEGER',
    bool: 'INTEGER',
    str: 'TEXT',
    Optional[str]: 'TEXT',
    float: 'REAL'
}

def schema_from_list(elements, primary_key=None):
    elements = copy(elements)
    if primary_key:
        key_index = elements.index(primary_key)
        elements[key_index] = f"{elements[key_index]} PRIMARY KEY"
    return ','.join(c.lower() for c in elements)

def schema_from_dataclass(dataclass: dataclass, primary_key=None):
    elements = []
    for field_name, field_type in dataclass.__annotations__.items():
        # Extract type from optional wrapper
        if hasattr(field_type, '_name') and field_type._name == 'Optional':
            datatype = db_dc_mapping[field_type.__args__[0]]
        # Fallback optional check when running on Python 3.8
        elif 'Union' in str(field_type):
            datatype = db_dc_mapping[get_args(field_type)[0]]
        else:
            datatype = db_dc_mapping[field_type]
        element = f"{field_name} {datatype}"
        if field_name == primary_key:
            element += " PRIMARY KEY"
        elements.append(element)
    return schema_from_list(elements)

def convert_retain_bool(dataclass: dataclass, data):
    """
        Return a SQLite row as a dictionary with properly casted boolean values in place of integer values
    """
    to_convert = copy(dict(data))
    for field_name, field_type in dataclass.__annotations__.items():
        if field_type == bool:
            to_convert[field_name] = bool(to_convert[field_name])
    return from_dict(data_class=dataclass, data=to_convert)
