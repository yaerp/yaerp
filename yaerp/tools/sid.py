from yaerp.tools.singleton import Singleton


class SIDCounter:
    _sid = 0

    def __init__(self):
        SIDCounter._sid = 0

    def new(self) -> int:
        SIDCounter._sid += 1
        return SIDCounter._sid
    
    def print_form(self, sid: int) -> str:
        return str.rjust(str(sid), 5)

class SID(SIDCounter, metaclass=Singleton):
    ''' Sequence Identifier '''
    def __init__(self):
        super().__init__()