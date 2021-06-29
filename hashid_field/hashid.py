import sys
from functools import total_ordering

from hashids_cpp import Hashids as Hashids_cpp
from hashids import Hashids, _is_uint


@total_ordering
class Hashid(object):
    def __init__(
        self,
        id,
        salt='',
        min_length=0,
        alphabet=Hashids.ALPHABET,
        hashids=None,
        hashids_cpp=None,
        prefix=None
    ):
        if hashids is None:
            self._salt = salt
            self._min_length = min_length
            self._alphabet = alphabet
            self._prefix = prefix
            self._hashids = Hashids(salt=self._salt, min_length=self._min_length, alphabet=self._alphabet)
            self._hashids_cpp = Hashids_cpp(self._salt, self._min_length, self._alphabet)
        else:
            self._hashids = hashids
            self._hashids_cpp = hashids_cpp
            self._salt = hashids._salt
            self._min_length = hashids._min_length
            self._alphabet = hashids._alphabet
            self._prefix = prefix

        # First see if we were given an already-encoded and valid Hashids string
        value = self.decode(id)
        if value is not None:
            self._id = value
            self._hashid = id
        else:
            # Next see if it's a positive integer
            try:
                id = int(id)
            except (TypeError, ValueError):
                raise ValueError("id must be a positive integer or valid Hashid value")
            if not _is_uint(id):
                raise ValueError("id must be a positive integer")

            # Finally, set our internal values
            self._id = id
            # If the id is numerical, we only lazily compute the hashid itself
            # as it might not be always needed
            self._hashid = None

    @property
    def id(self):
        return self._id

    @property
    def hashid(self):
        """ Compute the hashid lazily, if it is not already computed """
        if self._hashid is None:
            self._hashid = self.encode(self.id)

        return self._hashid

    @property
    def hashids(self):
        return self._hashids

    def encode(self, id):
        hid = self._hashids_cpp.encode_int(id)

        if self._prefix:
            return '%s_%s' % (self._prefix, hid)
        else:
            return hid

    def decode(self, hashid):
        # Shortcut, to not do unnecessary computation
        if type(hashid) == int:
            return None

        if isinstance(hashid, str) and self._prefix is not None:
            if hashid.startswith(self._prefix):
                hashid = hashid[len(self._prefix) + 1:]
            else:
                return None

        id = self._hashids.decode(hashid)
        if len(id) == 1:
            return id[0]
        else:
            return None

    def __repr__(self):
        return "Hashid({}): {}".format(self.id, self.hashid)

    def __str__(self):
        return self.hashid

    def __int__(self):
        return self.id

    def __long__(self):
        return int(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id and self.hashid == other.hashid and self._prefix == other._prefix
        if isinstance(other, str):
            return self.hashid == other
        if isinstance(other, int):
            return self.id == other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.id < other.id
        if isinstance(other, type(self.id)):
            return self.id < other
        return NotImplemented

    def __len__(self):
        return len(self.hashid)

    def __hash__(self):
        return hash(self.hashid)

    def __reduce__(self):
        return (self.__class__, (self.id, self._salt, self._min_length, self._alphabet))
