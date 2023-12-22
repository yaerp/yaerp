from hashlib import blake2s
from yaerp.tools.singleton import Singleton
from yaerp.tools.text import container2str


class _SecureToken:
    def __init__(self, salt: str=None, digest_size: int = 12, open_number: bool=False):
        if salt:
            self._alg = blake2s(digest_size=digest_size, salt=salt.encode())
        else:
            self._alg = blake2s(digest_size=digest_size)
        self._open_number = open_number
        self._number = 0
        self._token = ''

    def update(self, data: str | list | dict | tuple) -> str:
        self._input_string = container2str(data)
        self._number += 1
        self._alg.update(self._token.encode())
        self._alg.update(self._input_string.encode())
        self._token = self._alg.hexdigest()
        return self.token()

    def token(self) -> str:
        if self._open_number:
            return f'{self._number:04}_{self._token}'
        else:
            return self._token
    
    def plain(self) -> str:
        return self._input_string


class secure_token(_SecureToken, metaclass=Singleton):
    def __init__(self, salt: str='', digest_size: int = 12, open_number: bool=False):
        super().__init__(salt, digest_size, open_number)
