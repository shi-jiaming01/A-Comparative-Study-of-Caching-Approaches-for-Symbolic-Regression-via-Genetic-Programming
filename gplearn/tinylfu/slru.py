from typing import Optional, Tuple, Any

from .lru_cache import LRUCache


class SLRUCache:
    """
    An SLRU tinylfu item has the following lifecycle:

    New item is inserted to probational segment. This item becomes the most recently used item in the probational segment.

    If the probational segment is full, the least recently used item is evicted from tinylfu.
    If an item in the probational segment is accessed (with get or set), the item is migrate to the protected segment. This item becomes the most recently used item of the protected segment.

    If the protected segment is full, the least recently used item from the segment is moved to probational segment. This item becomes the most recently used item in the probational segment.
    If an item in the protected segment is accessed, it becomes the most recently used item of the protected segment.
    """

    def __init__(self, probation_cap=128, protected_cap=128):
        self.probation_cap = probation_cap
        self.protected_cap = protected_cap
        self.probational_cache = LRUCache(probation_cap) # 试验区, 新加入的key先进入这里。如果空间满了，最久未使用的 key 会被删除。
        self.protected_cache = LRUCache(protected_cap) # 保护区, 试验区被访问晋升到保护区, 保护区满了最久的降级为试验区

    def __contains__(self, item) -> bool:
        return item in self.probational_cache or item in self.protected_cache # 判断 key 是否存在于缓存(不论在哪个区)

    def __len__(self) -> int:
        return len(self.probational_cache) + len(self.protected_cache) #返回总长度

    def is_full(self) -> bool:
        """Check if the cache is full."""
        return self.protected_cache.is_full() and self.probational_cache.is_full() #两个同时满才true

    def set(self, key, value):
        """Store a new views, potentially discarding an old value."""
        if key in self.protected_cache: # 在保护区,更新
            self.protected_cache.set(key, value)

        elif key in self.probational_cache: # 在试验区,移到保护区
            self.probational_cache.remove(key)
            self.protected_cache.set(key, value)
        else:
            self.probational_cache.set(key, value) #否则进入试验区

    def get(self, key):
        """Store a new views, potentially discarding an old value."""
        if key in self.protected_cache:
            return self.protected_cache.get(key)

        if key in self.probational_cache:
            item_value = self.probational_cache.get(key) #这里有问题,没有删除导致重复缓存 
            self.protected_cache.set(key, item_value)
            return item_value

        return None

    def remove(self, key: str): # 两个缓存同时清除
        """Remove key from the cache. Return None if key is not present."""
        if key in self.protected_cache:
            return self.protected_cache.remove(key)
        if key in self.probational_cache:
            return self.probational_cache.remove(key)

        return None

    def get_victim(self) -> Optional[Tuple[Any, Any]]:
        """Get the last key:value pair in the cache. Cache is ordered following the SLRU scheme."""
        if len(self) >= (self.protected_cap + self.probation_cap):
            return self.probational_cache.get_victim()

        return None
    
    def clear(self) -> None:
        self.probational_cache.clear()
        self.protected_cache.clear()
