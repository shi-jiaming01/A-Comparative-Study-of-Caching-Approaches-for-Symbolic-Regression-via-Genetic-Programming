from collections import OrderedDict
# from typing import Optional, Tuple, Any

class LRUCacheDict:
    """Standard LRU, implemented with OrderedDict"""
    def __init__(self, cache_size):
        self.cache = OrderedDict()
        self.cache_size = cache_size
    
    def __contains__(self, key):
        return key in self.cache
    
    def __getitem__(self, key):
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def __setitem__(self, key, value):
        self.cache[key] = value
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)

    def __len__(self):
        return len(self.cache)
    
    def clear(self):
        self.cache.clear()

class LRUCacheDictFreq:
    """Standard LRU, implemented with OrderedDict"""
    def __init__(self, cache_size):
        self.gen = 0
        self.cache = OrderedDict()
        self.cache_size = cache_size
    
    def __contains__(self, key):
        return key in self.cache
    
    def __getitem__(self, key):
        value, freq = self.cache.pop(key)  # remove to re-insert later
        self.cache[key] = [value, freq + 1]
        return value
    
    def __setitem__(self, key, value):
        self.cache[key] = [value, 0]
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)

    def __len__(self):
        return len(self.cache)
    
    def clear(self):
        self.cache.clear()


class InfCache:
    """Infinate cache size. Contains call counting function (Only for test)"""
    def __init__(self):
        self.cache = {} 

    def __getitem__(self, key):
        values = self.cache.pop(key)
        self.cache[key] = [values[0], values[1] + 1]
        return values[0]

    def __setitem__(self, key, value):
        self.cache[key] = [value, 0]

    def __contains__(self, key):
        return key in self.cache

    def __len__(self):
        return len(self.cache)
    
    def clear(self):
        self.cache.clear()

class SLRUCache: 
    """SLRU cache implemented with OrderedDict"""
    def __init__(self, cache_size, probationary_ratio):
        self.ratio = probationary_ratio
        self.probationary_cache = OrderedDict()  # Probation area: Newly added keys enter here. When full, the least recently used key is removed.
        self.protected_cache = OrderedDict()     # Protected area: Keys accessed in the probation area are promoted here. When full, the least recent key is demoted back to the probation area.
        self.cache_size_probationary = round(cache_size * probationary_ratio)
        self.cache_size_protected = cache_size - round(cache_size * probationary_ratio)

    def __contains__(self, item) -> bool:
        return item in self.probationary_cache or item in self.protected_cache
    
    def __len__(self) -> int:
        return len(self.probationary_cache) + len(self.protected_cache)
    
    def is_full(self) -> bool:
        return self.__len__() == self.cache_size_probationary + self.cache_size_protected
    
    def is_overflow(self) -> bool:
        return self.__len__() > self.cache_size_probationary + self.cache_size_protected
    
    def __setitem__(self, key, value):
        """Store new key-value pairs, discarding old values if necessary."""
        self.probationary_cache[key] = value # Write new key-value
        if len(self.probationary_cache) > self.cache_size_probationary:
            self.probationary_cache.popitem(last=False)

    def __getitem__(self, key):
        """Get the value of key and update the cache"""
        if key in self.probationary_cache:
            value = self.probationary_cache.pop(key)
            self.protected_cache[key] = value
            if len(self.protected_cache) > self.cache_size_protected:
                oldest_key, oldest_value = self.protected_cache.popitem(last=False)
                self.probationary_cache[oldest_key] = oldest_value
            return value
        # elif key in self.protected_cache:
        else:
            value = self.protected_cache[key]
            self.protected_cache.move_to_end(key)
            return value
        # else:
        #    raise KeyError(f"Key {key} not found in SLRUCache.")
    def clear(self):
        self.probationary_cache.clear()
        self.protected_cache.clear()



class TwoQueue:
    def __init__(self, cache_size, ratio):
        self.ratio = ratio
        self.A1in = OrderedDict() # FIFO. Newly added keys go here first. If it is full, the longest unused key will be deleted.
        self.A1out = OrderedDict() # FIFO only has keys. Add key-value pair in Am if key in A1out. Not included in cache_size.
        self.Am = OrderedDict() # LRU. Accessed key-value pairs are promoted here, and the least recently accessed ones are deleted.
        self.A1in_size = round(cache_size * ratio)
        self.A1out_size = round(cache_size * ratio / 2) # The paper recommends that A1out be half of A1in
        self.Am_size = cache_size - round(cache_size * ratio)

    def __contains__(self, item) -> bool:
        return item in self.Am or item in self.A1in # Determine whether key exists in Am or A1in
    
    def __len__(self) -> int:
        return len(self.Am) + len(self.A1in) # Returns the total length
    
    def is_full(self) -> bool:
        return self.__len__() == self.A1in_size + self.Am_size
    
    def is_overflow(self) -> bool:
        return self.__len__() > self.A1in_size + self.Am_size

    def __setitem__(self, key, value):
        if key in self.A1out:
            self.A1out.pop(key)
            self.Am[key] = value
            if len(self.Am) > self.Am_size:
                self.Am.popitem(last=False)
        else:
            self.A1in[key] = value
            if len(self.A1in) > self.A1in_size:
                oldest_key, _ = self.A1in.popitem(last=False)
                self.A1out[oldest_key] = None
                if len(self.A1out) > self.A1out_size:
                    self.A1out.popitem(last=False)

    def __getitem__(self, key):
        if key in self.A1in:
            value = self.A1in.pop(key)
            self.Am[key] = value
            if len(self.Am) > self.Am_size:
                self.Am.popitem(last=False)
            return value
        else: # key in self.Am
            value = self.Am[key]
            self.Am.move_to_end(key)
            return value

    def clear(self):
        self.A1in.clear()
        self.A1out.clear()
        self.Am.clear()


class _deque(object):
    'Fast searchable queue'

    def __init__(self):
        self.od = OrderedDict()

    def appendleft(self, key):
        if key in self.od:
            del self.od[key]
        self.od[key] = None

    def move_to_end(self, key):
        self.od.move_to_end(key)

    def pop(self):
        return self.od.popitem(0)[0]

    def remove(self, key):
        del self.od[key]

    def __len__(self):
        return len(self.od)

    def __contains__(self, k):
        return k in self.od
    
    def clear(self):
        self.od.clear()

class ARCCache(object):
    def __init__(self, cache_size):
        self.cached = {}
        self.c = cache_size
        self.p = 0

        self.t1 = _deque()
        
        self.b1 = _deque()

        self.t2 = _deque()

        self.b2 = _deque()

    def __contains__(self, key):
        return key in self.t1 or key in self.t2

    def replace(self, key):
        if self.t1 and ((key in self.b2 and len(self.t1) == self.p) or (len(self.t1) > self.p)):
            old = self.t1.pop()
            self.b1.appendleft(old)
        else:
            old = self.t2.pop()
            self.b2.appendleft(old)
        del self.cached[old]

    def __getitem__(self, key):
        if key in self.t1:
            self.t1.remove(key)
            self.t2.appendleft(key)
            return self.cached[key]
        else: # key in self.t2:
            self.t2.move_to_end(key)
            return self.cached[key]

    def __setitem__(self, key, value):
        if key in self.b1:
            self.p = min(self.c, self.p + max(len(self.b2) // len(self.b1), 1))
            self.replace(key)
            self.b1.remove(key)
            self.t2.appendleft(key)
            self.cached[key] = value
            return
        if key in self.b2:
            self.p = max(0, self.p - max(len(self.b1) // len(self.b2), 1))
            self.replace(key)
            self.b2.remove(key)
            self.t2.appendleft(key)
            self.cached[key] = value
            return

        if len(self.t1) + len(self.b1) >= self.c:
            if len(self.t1) < self.c:
                self.b1.pop()
                self.replace(key)
            else:
                del self.cached[self.t1.pop()]
        else:
            total = len(self.t1) + len(self.b1) + len(self.t2) + len(self.b2)
            if total >= self.c:
                if total >= (2 * self.c):
                    self.b2.pop()
                self.replace(key)
        self.t1.appendleft(key)
        self.cached[key] = value

    def __len__(self):
        return len(self.cached)
    
    def clear(self):
        self.t1.clear()
        self.b1.clear()
        self.t2.clear()
        self.b2.clear()
        self.cached.clear()


class TwoCache:
    def __init__(self, cache_size, ratio, complexity):
        self.ratio = ratio
        self.complexity = complexity
        self.cache_size_low = round(cache_size * ratio)
        self.cache_size_high = cache_size - round(cache_size * ratio)
        self.cache_low = SLRUCache(self.cache_size_low, 0.2)
        # self.cache_low = LRUCacheDict(self.cache_size_low)
        self.cache_high = SLRUCache(self.cache_size_high, 0.2)

    def __contains__(self, key) -> bool:
        if len(key) > self.complexity:
            return key in self.cache_high
        else:
            return key in self.cache_low
    
    def __len__(self) -> int:
        return len(self.cache_low) + len(self.cache_high)
    
    def is_full(self) -> bool:
        return self.__len__() == self.cache_size_low + self.cache_size_high
    
    def is_overflow(self) -> bool:
        return self.__len__() > self.cache_size_low + self.cache_size_high
    
    def __setitem__(self, key, value):
        """Store new key-value pairs, discarding old values if necessary."""
        if len(key) > self.complexity:
            self.cache_high[key] = value
        else:
            self.cache_low[key] = value
    def __getitem__(self, key):
        """Get the value of key and update the cache"""
        if len(key) > self.complexity:
            value = self.cache_high[key]
        else:
            value = self.cache_low[key]
        return value

    def clear(self):
        self.cache_low.clear()
        self.cache_high.clear()


