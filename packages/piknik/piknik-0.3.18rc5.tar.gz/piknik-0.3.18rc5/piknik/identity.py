import hashlib


class Identity:
    
    def __init__(self, fingerprint):
        self.__id = bytes.fromhex(fingerprint)
       

    def id(self):
        return self.__id.hex()


    def __eq__(self, other):
        return other.id() == self.id()

       
    def uri(self):
        h = hashlib.sha256()
        h.update(self.__id)
        z = h.digest()
        return 'sha256:' + z.hex()


    def __str__(self):
        return self.id()
