from collections import Counter


def bit_mask(length):
    return (1 << length) - 1


class EvictPolicy:
    def __init__(self, cache) -> None:
        self.cache = cache


class LRU(EvictPolicy):
    def evict_cache_entry_from_set(self, address):
        _, index, _ = self.cache.split_address(address)

        def predicate(cache_entry):
            return cache_entry.flags

        lru = min(self.cache.get_cache_entry_set(index), key=predicate)
        lru.valid = 0

        return lru.copy()

    def update_cache_entry_set(self, address):
        tag, index, _ = self.cache.split_address(address)
        old_flags = self.cache.get_cache_entry(address).flags

        for cache_entry in self.cache.get_cache_entry_set(index):
            if cache_entry.tag == tag:
                cache_entry.flags = self.cache.place_policy.set_size
            elif cache_entry.flags > old_flags:
                cache_entry.flags -= 1


class LFU(EvictPolicy):
    def __init__(self, cache) -> None:
        super().__init__(cache)
        self.__counter = Counter()

    def evict_cache_entry_from_set(self, address):
        _, index, _ = self.cache.split_address(address)

        def predicate(cache_entry):
            return cache_entry.flags

        lfu = min(self.cache.get_cache_entry_set(index), key=predicate)
        lfu.valid = 0

        counter_key = lfu.tag
        counter_key = counter_key << self.cache.place_policy._index_bits | index
        
        self.__counter.pop(counter_key)

        return lfu.copy()

    def update_cache_entry_set(self, address):
        tag, index, _ = self.cache.split_address(address)

        tag_index = tag
        tag_index = tag_index << self.cache.place_policy._index_bits | index

        self.__counter[tag_index] += 1

        def predicate(item):
            tag_index, _ = item
            return index == (tag_index & bit_mask(self.cache.place_policy._index_bits))

        set_cache_entry_counts = map(
            lambda item: item[0],
            sorted(
                filter(
                    predicate,
                    self.__counter.items(),
                ),
                key=lambda item: item[1],
            ),
        )

        for cache_entry in self.cache.get_cache_entry_set(index):
            for flags, tag_index in enumerate(set_cache_entry_counts):
                tag_index >>= self.cache.place_policy._index_bits
                entry_tag = tag_index
                if entry_tag == cache_entry.tag:
                    cache_entry.flags = flags
                    break
