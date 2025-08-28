
class YException(Exception):
    
    def __init__(self, key:str ):
        from .messages import errors

        self._key  = key
        self._data = errors[key]
        self._msg  = self.data['msg']
        self._code = self.data['code']

        super().__init__(self._msg)

