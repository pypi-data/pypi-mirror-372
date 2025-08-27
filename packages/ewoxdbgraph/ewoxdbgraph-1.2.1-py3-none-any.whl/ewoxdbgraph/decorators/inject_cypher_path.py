from pathlib import Path
from functools import wraps

def InjectCypherPath(func):
    """ Decorator to inject the path of the file where the function is defined into the function call. 
    This allows the function to access files relative to its own location.
    """
    defining_file:str = func.__code__.co_filename
    path = Path(defining_file).parent

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, str(path), *args, **kwargs)
    return wrapper