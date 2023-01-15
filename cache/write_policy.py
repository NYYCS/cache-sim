class WritePolicy:

    def __init__(self, cache) -> None:
        self.cache = cache


class WriteThrough(WritePolicy):

    def __init__(self, cache) -> None:
        super().__init__(cache)
        cache.on_event("CACHE_WRITE", self.write_to_store)

    def write_to_store(self, cache, address, cache_entry):
        self.cache.store.write_block(address, cache_entry.block)

class WriteBack(WritePolicy):

    def __init__(self, cache) -> None:
        super().__init__(cache)
        cache.on_event("CACHE_EVICT", self.write_to_store)

    def write_to_store(self, cache, address, cache_entry):
        if cache_entry.dirty:
            self.cache.store.write_block(address, cache_entry.block)