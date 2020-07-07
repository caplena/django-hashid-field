from hashids import Hashids
from hashids_cpp import Hashids as Hashids_cpp

from .hashid import Hashid


class HashidDescriptor(object):
    def __init__(
        self,
        name,
        salt='',
        min_length=0,
        alphabet=Hashids.ALPHABET,
        hashids=None,
        hashids_cpp=None,
        prefix=None
    ):
        self.name = name
        self.salt = salt
        self.min_length = min_length
        self.alphabet = alphabet
        self.prefix = prefix

        if hashids is None:
            self._hashids = Hashids(salt=self.salt, min_length=self.min_length, alphabet=self.alphabet)
            self._hashids_cpp = Hashids_cpp(self.salt, self.min_length, self.alphabet)
        else:
            self._hashids = hashids
            self._hashids_cpp = Hashids_cpp(self.salt, self.min_length, self.alphabet)

    def __get__(self, instance, owner=None):
        if instance is not None and self.name in instance.__dict__:
            return instance.__dict__[self.name]
        else:
            return None

    def __set__(self, instance, value):
        if isinstance(value, Hashid) or value is None:
            instance.__dict__[self.name] = value
        else:
            try:
                instance.__dict__[
                    self.name
                ] = Hashid(value, hashids=self._hashids, hashids_cpp=self._hashids_cpp, prefix=self.prefix)
            except ValueError:
                instance.__dict__[self.name] = value
