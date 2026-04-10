import numpy as np
import mmh3


def hash_mmh3(item, depth, width):
    """Simple mmh3 hashing function" that map the result to the given depth and width."""
    for i in range(depth):
        index = mmh3.hash64(item, signed=False)[0] % width
        yield index
# 计算 depth 个哈希值，每个值都 映射到 [0, width) 的范围，用于 Count-Min Sketch 的不同哈希表层。

class CountMinSketch:
    """Simple Count-Min Sketch implementation for use in python,

       Args:
           width (int): The width of the count-min sketch
           depth (int): The depth of the count-min sketch (default is 4)
           hash_function (function): Hashing strategy function to use `hf(key, number)`
       Returns:
           CountMinSketch: A Count-Min Sketch object
    """

    def __init__(self, width, depth=4, hash_function=None):
        self.depth = depth # 哈希表的层数
        self.width = width # 哈希表的宽度
        self.table = np.zeros((depth, width)) # 初始化一个 2D 数组（depth 行 × width 列）
        self.keys = set() # 记录出现过的 keys
        self.hash_functions = hash_mmh3 if not hash_function else hash_function # 选择哈希函数

    def update(self, item, count=1):
        """Update the frequency of the item based on the given count."""
        for table, i in zip(self.table, self.hash_functions(item, self.depth, self.width)):
            table[i] += count

    def estimate(self, item):
        """Estimate the frequency of the given item."""
        return min(table[i] for table, i in zip(self.table, self.hash_functions(item, self.depth, self.width)))

    def reset(self):
        """Reset the count to the starting state."""
        self.table = np.zeros((self.depth, self.width))
