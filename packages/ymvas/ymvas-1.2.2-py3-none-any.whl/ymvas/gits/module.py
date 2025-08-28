from functools import lru_cache
from os import name


class GitModule:
    root   : bool = False
    active : bool = False
    path   : str  = None
    url    : str  = None
    name   : str  = None
    user   : str  = None
    
    def __init__(
            self ,
            path ,
            root   = False,
            active = True,
            url    = None,
            name   = None,
            user   = None
        ):

        self.path   = path
        self.root   = root
        self.active = active
        self.url    = url
        self.name   = name
        self.user   = user

        

    @property
    def alias(self):
        return f"{self.user}/{self.name}"
    
    @property
    @lru_cache(maxsize=True)
    def settings(self):
        from .. import Settings 
        return Settings(self.path)



