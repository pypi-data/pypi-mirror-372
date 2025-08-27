import threading
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar, Generic, Tuple, ContextManager
import warnings

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class ConcurrentDictionary(Generic[K, V]):
    """
    A thread-safe dictionary implementation using a re-entrant lock.
    All operations that mutate or access the dictionary are protected.

    Example usage of update_atomic:

        d = ConcurrentDictionary({'x': 0})
        # Atomically increment the value for 'x'
        d.update_atomic('x', lambda v: v + 1)
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._lock = threading.RLock()
        self._dict: Dict[K, V] = dict(*args, **kwargs)  # type: ignore
        self._key_locks: Dict[K, threading.RLock] = {}

    def _get_key_lock(self, key: K) -> threading.RLock:
        with self._lock:
            if key not in self._key_locks:
                self._key_locks[key] = threading.RLock()
            return self._key_locks[key]

    class _KeyLockContext:
        def __init__(self, outer : "ConcurrentDictionary[K,V]", key: K):
            self._outer = outer
            self._key = key
            self._lock = outer._get_key_lock(key)

        def __enter__(self) -> V:
            self._lock.acquire()
            return self._outer._dict[self._key]

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
            self._lock.release()

    def get_locked(self, key: K) -> ContextManager[V]:
        """
        Context manager: lock the key, yield its value, unlock on exit.

        Usage:
            with d.get_locked('x') as value:
                # safely read/update value for 'x'
        """
        return self._KeyLockContext(self, key)

    def key_lock(self, key: K):
        """
        Context manager: lock the key, yield nothing, unlock on exit.

        Usage:
            with d.key_lock('x'):
                # safely update d['x'] or perform multiple operations
        """
        lock = self._get_key_lock(key)
        return lock

    def __getitem__(self, key: K) -> V:
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key: K, value: V) -> None:
        warnings.warn(
            f"Direct assignment (D[key] = value) is discouraged. "
            f"Use assign_atomic() for assigning a value to a new key safely, "
            f"or update_atomic() for thread-safe update of an existing dictionary key.",
            stacklevel=2
        )
        self.assign_atomic(key, value)


    def __delitem__(self, key: K) -> None:
        with self._lock:
            del self._dict[key]


    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            return self._dict.get(key, default)


    def setdefault(self, key: K, default: V) -> V:
        with self._lock:
            return self._dict.setdefault(key, default)


    def assign_atomic(self, key: K, value: V) -> None:
        """
        Atomically assign a value to a key.

        This method ensures that the assignment is performed atomically,
        preventing
        """
        self.update_atomic(key, lambda _: value)
        
    
    def update_atomic(self, key: K, func: Callable[[V], V]) -> None:
        """
        Atomically modify the value for a key using func(old_value) -> new_value.

        This method ensures that the read-modify-write sequence is performed atomically,
        preventing race conditions in concurrent environments.

        Example:
            d = ConcurrentDictionary({'x': 0})
            # Atomically increment the value for 'x'
            d.modify_atomic('x', lambda v: v + 1)
        """
        with self._lock:
            if key in self._dict:
                old_value = self._dict[key]
                new_value = func(old_value)
                self._dict[key] = new_value
            else:
                # If the key does not exist, we can set it directly
                self._dict[key] = func(None) # type: ignore


    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            return self._dict.pop(key, default)


    def popitem(self) -> tuple[K, V]:
        with self._lock:
            return self._dict.popitem()


    def clear(self) -> None:
        with self._lock:
            self._dict.clear()


    def keys(self) -> List[K]:
        with self._lock:
            return list(self._dict.keys())


    def values(self) -> List[V]:
        with self._lock:
            return list(self._dict.values())


    def items(self) -> List[Tuple[K, V]]:
        with self._lock:
            return list(self._dict.items())


    def __contains__(self, key: K) -> bool:
        with self._lock:
            return key in self._dict


    def __len__(self) -> int:
        with self._lock:
            return len(self._dict)


    def __iter__(self) -> Iterator[K]:
        with self._lock:
            return iter(list(self._dict))


    def __repr__(self) -> str:
        with self._lock:
            return f"ConcurrentDictionary({self._dict!r})"