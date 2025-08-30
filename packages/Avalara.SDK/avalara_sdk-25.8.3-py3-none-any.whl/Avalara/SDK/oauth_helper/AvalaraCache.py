from datetime import datetime, timedelta

from threading import Lock
from time import sleep

# from typing import Any


class AvalaraCache(dict):
    """Custom implementaion of dictionary with time based expiry for cache"""

    __initialized: bool
    __background_worker_sleep_interval_in_seconds: float
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(AvalaraCache, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, *args):
        if self.__instance.__initialized:
            return
        self.__instance.__initialized = True
        self.__background_worker_sleep_interval_in_seconds = 0.500
        self.__lock = Lock()
        # Thread(target=self.__background_worker, daemon=True).start()
        dict.__init__(self, args)

    def __getitem__(self, key):
        # return dict.__getitem__(self, key)[0]
        return dict.__getitem__(self, key)

    def set_item_with_ttl(self, key, val, seconds):
        """Sets item in cache with time to live in seconds.

        Args:
            key (_type_): Cache item key
            val (_type_): Cache item value.
            seconds (int ): Time to live in seconds.
        """
        self.__setitem__(key, val, seconds)

    def delete_item_from_cache(self, key):
        """Deletes item from cache if item is present

        Args:
            key (_type_): Cache item key
        """
        if key in self:
            del self[key]

    def __setitem__(self, key, val, seconds=3600):
        lifetime = timedelta(seconds=seconds)
        expiration = datetime.utcnow() + lifetime
        dict.__setitem__(self, key, (val, expiration))

    def remove_expired_items(self):
        """Removes expired items from cache.\n
        This functon is executed in background thread periodically"""
        with self.__lock:
            for item, value in list(self.items()):
                item_expired = datetime.utcnow() > value[1]
                if item_expired:
                    del self[item]

    def __background_worker(self):
        while True:
            self.remove_expired_items()
            sleep(self.__background_worker_sleep_interval_in_seconds)
