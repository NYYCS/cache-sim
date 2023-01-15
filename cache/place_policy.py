from collections import namedtuple
import math


from cache import Cache


class PlacePolicy:
    def __init__(self, cache: Cache) -> None:
        self.cache = cache


def bit_mask(length):
    return (1 << length) - 1


class _SetAssociative(PlacePolicy):
    def __init__(self, cache: Cache, *, set_size) -> None:
        super().__init__(cache)
        self.set_size = set_size
        self.total_sets = self.cache.total_entries // self.set_size

        self._offset_bits = int(math.log2(self.cache.block_size))
        self._index_bits = int(math.log2(self.total_sets))

        address_bits = int(math.log2(self.cache.store.size))
        self._tag_bits = address_bits - self._index_bits - self._offset_bits

    def split_address(self, address):
        offset = address & bit_mask(self._offset_bits)
        address >>= self._offset_bits
        index = address & bit_mask(self._index_bits)
        address >>= self._index_bits
        tag = address & bit_mask(self._tag_bits)
        return tag, index, offset

    def get_cache_entry_set(self, index):
        lower = index * self.set_size
        upper = lower + self.set_size
        return self.cache.entries[lower:upper]


class DirectMapping(_SetAssociative):
    def __init__(self, cache: Cache) -> None:
        super().__init__(cache, set_size=1)


class TwoWaySetAssociative(_SetAssociative):
    def __init__(self, cache: Cache) -> None:
        super().__init__(cache, set_size=2)


class FourWaySetAssociative(_SetAssociative):
    def __init__(self, cache: Cache) -> None:
        super().__init__(cache, set_size=4)


class FullyAssociative(_SetAssociative):
    def __init__(self, cache: Cache) -> None:
        super().__init__(cache, set_size=cache.total_entries)
