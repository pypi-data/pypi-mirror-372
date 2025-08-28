from .schedules import Schedule
from functools import lru_cache
import yaml

class Contact:

    def __init__(self, path:str):
        self.path = path
        self.data = {}

    def _load(self):
        try:
            with open(self.path,'r') as f:
                self.data = yaml.safe_load(f.read())
        except Exception:
            pass

    def schedule(self):
        self._load()
        s = Schedule(self.path)

        birthday = self.data.get("birthday")
        s.data = {
            "active" : True,
            'is-all-day' : 'true'
        }

        if birthday is not None:
            bdate = Schedule._date(birthday)
            s.data['cron'] = f"0 0 {bdate.day} {bdate.month} *"
            s.data['start'] = birthday
        else:
            s.data['active'] = False 

        s._is_contact = True
        s._loaded = True

        return s
    
    @property
    @lru_cache
    def birthdate(self):
        self._load()
        bd = self.data.get('birthday')
        if bd is None:
            return None
        return Schedule._date(bd)
