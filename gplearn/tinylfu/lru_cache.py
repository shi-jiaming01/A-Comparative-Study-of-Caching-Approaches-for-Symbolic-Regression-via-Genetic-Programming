from collections import OrderedDict
from typing import Optional, Tuple, Any


class LRUCache(OrderedDict):
    """
       A dictionary-like container that stores a given maximum items.
       If an additional item is added when the LRUCache is full, the least
       recently used key is discarded to make room for the new item.
       """

    def __init__(self, capacity=128):
        super().__init__()
        self.cache = OrderedDict() # 使用有序字典
        self.size = capacity # 设定缓存大小

    def __contains__(self, item: str) -> bool:
        return item in self.cache

    def __len__(self) -> int:
        return len(self.cache)

    def is_full(self) -> bool:
        """Check if the cache is full.""" 
        return len(self.cache) == self.size

    def get(self, key: str) -> Optional[Any]:
        """Gets the item, but also makes it most recent.""" # 获取缓存中的 key，并将其移动到最近使用位置（队尾）
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)  # Gotta keep this pair fresh, move to end of OrderedDict
            return self.cache[key]

    def set(self, key: str, value: object) -> Optional[Tuple[Any, Any]]:
        """Store a new views, potentially discarding an old value."""
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.size:
            return self.cache.popitem(last=False)
        return None, None

    def remove(self, key: str) -> Optional[Tuple[Any, Any]]:
        """Remove key from the cache. Return None if key is not present."""
        if key in self.cache:
            return self.cache.pop(key)

        return None

    def get_victim(self) -> Optional[Tuple[Any, Any]]:
        """Get the last key:value pair in the cache. Cache is ordered following the LRU scheme."""
        if self.size == len(self.cache): # 回最久未使用的 key（队首）
            oldest = next(iter(self.cache))
            return oldest

        return None
    
    def clear(self) -> None:
        self.cache.clear()
