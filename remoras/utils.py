import json
import os
from typing import Union

def load_obj_or_path(obj: Union[list, str]):
    """Check the type of `obj`. If it is a string treat it like a json filepath, else just return it"""
    if type(obj) is str:
        assert os.path.exists(obj), f"Unable to find specified file at {obj}"

        with open(obj, 'r') as f:
            objs = json.loads(f.read())
    else: # we have a list
        objs = obj

    return objs
