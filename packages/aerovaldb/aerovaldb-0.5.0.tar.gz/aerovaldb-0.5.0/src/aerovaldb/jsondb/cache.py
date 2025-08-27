import logging
import os
import sys
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from pathlib import Path
from typing import Hashable, TypedDict

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override
logger = logging.getLogger(__name__)


class CacheMissError(FileNotFoundError):
    """
    Raised by cache implementations when a cache miss occurs
    that the implementation is unable to handle (by eg.
    delegating it).
    """

    pass


class LRUQueue:
    """
    Small helper class that efficiently maintains a LRUQueue
    by combining a set and deque to maintain a unique constraint
    on the queue. Re-adding an element will return it to the
    end of the queue.
    """

    def __init__(self):
        self._set = set()
        self._deque = deque()

    @property
    def size(self) -> int:
        """Returns the lenth of the queue."""
        return len(self._set)

    def add(self, item: Hashable):
        """
        Adds an item to the queue.
        """
        if item in self._set:
            self._deque.remove(item)

        self._set.add(item)
        self._deque.appendleft(item)

    def pop(self) -> Hashable:
        """Removes and returns the top item from the queue."""
        item = self._deque.pop()
        self._set.remove(item)
        return item

    def remove(self, item: Hashable):
        """
        Removes an item from the queue.
        """
        if item in self._set:
            self._set.remove(item)
            self._deque.remove(item)


class BaseCache(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def hit_count(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def miss_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str, *, bypass_cache: bool = False) -> str:
        raise NotImplementedError

    @abstractmethod
    def put(self, obj: str, *, key: str):
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def evict(self, file_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_valid(self, key: str) -> bool:
        raise NotImplementedError


class CacheEntry(TypedDict):
    file: str

    last_modified: float


class LRUFileCache(BaseCache):
    """
    Implements an in-memory LRU cache for file content.
    """

    def __init__(self, *, max_size: int):
        """
        :param max_size : The maximum size of the cache in terms of number of entries / files.

        Files will be ejected based on least recently used, when full.
        """
        self._hit_count: int = 0
        self._miss_count: int = 0
        self._max_size: int = max_size

        # Stores the actual cached content, indexed by canonical file path.
        self._entries: defaultdict[str, CacheEntry | None] = defaultdict(lambda: None)

        # Stores queue of cache accesses, used for implementing LRU logic.
        self._queue = LRUQueue()

    def _get_entry(self, abspath: str):
        """Returns an element from the cache."""
        self._queue.add(abspath)
        self._hit_count = self._hit_count + 1
        logger.debug(f"Returning contents from file {abspath} from cache.")
        return self._entries[abspath]["file"]  # type: ignore

    @override
    def clear(self) -> None:
        logger.debug("Cache cleared.")

        self._entries = defaultdict(lambda: None)
        self._queue = LRUQueue()

        # Tally of cache hits and misses.
        self._hit_count = 0
        self._miss_count = 0

    @property
    @override
    def hit_count(self) -> int:
        """Returns the number of cache hits since the last `invalidate_all()` call.

        Note:
        -----
        This does not include calls with `no_cache=True`
        """
        return self._hit_count

    @property
    @override
    def size(self) -> int:
        """Returns the current size of the cache in terms of number of elements."""
        return self._queue.size

    @property
    @override
    def miss_count(self) -> int:
        """Returns the number of cache misses since the last `invalidate_all()` call.

        Note:
        -----
        This does not include calls with `no_cache=True`
        """
        return self._miss_count

    def _canonical_file_path(self, file_path: str | Path) -> str:
        """
        Returns an absolute file path with symlinks removed for a file to
        ensure correct lookup.

        :param file_path : The file path.

        :return : The file path converted to canonical file path.
        """
        return str(os.path.realpath(file_path))

    def _read_file(self, file_path: str | Path) -> str:
        abspath = self._canonical_file_path(file_path)
        logger.debug(f"Reading file {abspath}")

        with open(abspath, "r") as f:
            return f.read()

    def _put_entry(self, abspath: str, *, obj: str):
        self._entries[abspath] = {
            "file": obj,
            "last_modified": os.path.getmtime(abspath),
        }
        while self.size > self._max_size:
            key = self._queue.pop()
            self.evict(str(key))

    @override
    def get(self, key: str, *, bypass_cache: bool = False) -> str:
        abspath = self._canonical_file_path(key)

        if bypass_cache:
            return self._read_file(abspath)

        if self.is_valid(abspath):
            return self._get_entry(abspath)

        self._miss_count += 1
        obj = self._read_file(abspath)
        self._queue.add(abspath)
        self._put_entry(abspath, obj=obj)
        return obj

    @override
    def put(self, obj, *, key: str):
        abspath = self._canonical_file_path(key)
        self._put_entry(abspath, obj=obj)
        logger.debug("%s of %s entries in cache", self.size, self._max_size)

    @override
    def evict(self, file_path: str | Path) -> None:
        """
        Invalidates the cache for a file path, ensuring it will be re-read on the next read.

        :param file_path : The file path to invalidate cache for.
        """
        abspath = self._canonical_file_path(file_path)
        logger.debug(f"Clearing cache for file {abspath}.")
        if abspath in self._entries:
            del self._entries[abspath]
            self._queue.remove(abspath)

    @override
    def is_valid(self, file_path: str | Path) -> bool:
        """
        Checks whether a cache element is valid.

        :param file_path: The file path to check for.

        :returns : Boolean indicating cache validity.
        """
        abspath = self._canonical_file_path(file_path)

        cache = self._entries[abspath]
        if cache is None:
            return False

        if not os.path.exists(abspath):
            return False

        if os.path.getmtime(abspath) > cache["last_modified"]:
            return False

        return True


class KeyCacheDecorator(BaseCache):
    """Decorator for other cache implementations which extends it with support for
    sub-parts of a json file.
    """

    def __init__(self, cache: BaseCache, *, max_size: int = 64):
        if not isinstance(cache, BaseCache):
            raise TypeError(f"Cache is of type {type(cache)}, expected BaseCache")

        self._cache = cache

        self._entries: dict[str, CacheEntry | None] = defaultdict(lambda: None)
        self._queue = LRUQueue()

        self._miss_count = 0
        self._hit_count = 0
        self._max_size = max_size

    def _split_key(self, key: str) -> tuple[str, str | None]:
        splt = key.split("::")
        if len(splt) == 1:
            return (splt[0], None)
        elif len(splt) == 2:
            return tuple(splt)  # type: ignore

        raise ValueError(
            f"Unexpected number of elements in '{key}'. Expected 1 or 2, got {len(splt)}."
        )

    @property
    @override
    def hit_count(self) -> int:
        return self._hit_count

    @property
    @override
    def size(self) -> int:
        return self._queue.size

    @property
    @override
    def miss_count(self) -> int:
        return self._miss_count

    @override
    def get(self, key: str, *, bypass_cache: bool = False) -> str:
        fp, k = self._split_key(key)

        if k is None:
            return self._cache.get(fp, bypass_cache=bypass_cache)

        if self.is_valid(key):
            if (entry := self._entries[key]) is not None:
                self._hit_count += 1
                return entry["file"]

        self._miss_count += 1
        raise CacheMissError

    @override
    def put(self, obj, *, key: str) -> None:
        fp, _ = self._split_key(key)
        self._entries[key] = {
            "file": obj,
            "last_modified": os.path.getmtime(fp),
        }
        self._queue.add(key)
        while self.size > self._max_size:
            key = self._queue.pop()  # type: ignore
            self.evict(str(key))

        logger.debug("%s of %s entries in cache", self.size, self._max_size)

    @override
    def clear(self) -> None:
        self._entries = defaultdict(lambda: None)
        self._miss_count = 0
        self._hit_count = 0
        self._queue = LRUQueue()

    @override
    def evict(self, key: str) -> None:
        logger.debug(f"Invalidating cache for key {key}.")
        if key in self._entries:
            del self._entries[key]
            self._queue.remove(key)

    @override
    def is_valid(self, key: str) -> bool:
        fp, k = self._split_key(key)
        if k is None:
            # File access is delegated to sub-cache.
            return self._cache.is_valid(fp)

        cache = self._entries[key]
        if cache is None:
            return False

        if not os.path.exists(fp):
            return False

        if os.path.getmtime(fp) > cache["last_modified"]:
            return False

        return True
