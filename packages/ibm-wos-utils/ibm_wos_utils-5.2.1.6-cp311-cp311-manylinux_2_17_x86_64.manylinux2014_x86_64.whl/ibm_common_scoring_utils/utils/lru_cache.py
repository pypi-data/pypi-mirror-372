# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2018, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from collections import OrderedDict
from threading import Lock


class LRUCache(OrderedDict):
    """Custom LRU cache which limits the size, evicts the recently used when full.
    Usage:
        cache = LRUCache(maxsize=10)  # Initialize cache
        cache["key1"] = "value"       # Set/Add key in cache
        cache["key1"]                 # Get key value, throws error if no key found
        cache.get("key1")             # Get key value, returns None if no key found
    """

    def __init__(self, maxsize=128, *args, **kwds):
        self.maxsize = maxsize
        self.lock = Lock()
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        with self.lock:
            value = super().__getitem__(key)
            self.move_to_end(key)
            return value

    def __setitem__(self, key, value):
        with self.lock:
            super().__setitem__(key, value)
            if len(self) > self.maxsize:
                oldest = next(iter(self))
                del self[oldest]

    def get(self, key):
        with self.lock:
            return super().get(key)
