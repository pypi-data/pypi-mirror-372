from gitlab_ps_utils.json_utils import json_pretty
import operator
from functools import reduce
from re import match

# TODO: Move this function to gitlab_ps_utils.dict_utils
def get_from_dict(d, keys):
    return reduce(operator.getitem, keys, d)

# TODO: Move this function to gitlab_ps_utils.dict_utils
def set_in_dict(d, keys, value):
    get_from_dict(d, keys[:-1])[keys[-1]] = value

# TODO: Move this function to gitlab_ps_utils.dict_utils
def set_extra_field_in_dict(d, keys, new_field, value):
    get_from_dict(d, keys[:-1])[keys[-1]][new_field] = value

def process_line(d, level, keyword, bracket):
    """
        Processes the individual line extracted through the regex pattern

        If an open bracket is detected, we create another dictionary layer

        If a closed bracket is detected, we assume that layer is finished converting and
        move back up the dictionary hierarchy

        If only a keyword is found, we assume that is a key/value pair we need to append to the
        current dictionary layer
    """
    if bracket == "{":
        # Create new nested level in the dict
        level.append(keyword.strip())
        set_in_dict(d, level, {})
    elif bracket == "}":
        # Traverse back up the dictionary layers
        level.pop()
    if '{' in bracket and '}' in bracket:
        level.pop()
        new_keyword = bracket.split(" ")[1]
        level.append(new_keyword.strip())
        set_in_dict(d, level, {})
    if keyword and not bracket:
        # Append another key/value pair to the current layer of the dictionary
        field = keyword.split(' ')[0]
        value = " ".join(keyword.split(' ')[1:])
        set_extra_field_in_dict(d, level, field, value)

def convert_groovy_to_dict(groovy_string):
    as_dict = {}
    level = []
    multiline_comment = False
    ## Initial loop to do some basic matching
    for line in groovy_string.splitlines():
        if "/*" in line:
            multiline_comment = True
            continue
        if "*/" in line:
            multiline_comment = False
            continue
        if multiline_comment:
            continue
        if m := match(r'(\t+|[ ]+|)([A-Za-z0-9\(\)\"\'\ \,\[\]\.\/\-\&\$\:\*\@]*|)(\t+|[ ]+|)([\{\}\ A-Za-z]+|)', line.split(" //")[0]):
            keyword = m.groups()[1]
            bracket = m.groups()[-1]
            process_line(as_dict, level, keyword, bracket)
    return as_dict
