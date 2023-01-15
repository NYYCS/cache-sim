class CacheEntry:
    def __init__(self, **kwargs):
        self.tag = kwargs.pop("tag", 0)
        self.block = kwargs.pop("block", 0)
        self.flags = kwargs.pop("flags", 0)
        self.dirty = kwargs.pop("dirty", 0)
        self.valid = kwargs.pop("valid", 0)

    def copy(self):
        copy = self.__class__(
            tag=self.tag,
            block=self.block,
            flags=self.flags,
            dirty=self.dirty,
            valid=self.valid,
        )
        return copy


class CacheEvent:
    CACHE_MISS = "CACHE_MISS"
    CACHE_READ = "CACHE_READ"
    CACHE_WRITE = "CACHE_WRITE"
    CACHE_EVICT = "CACHE_EVICT"
    CACHE_COMPARE = "CACHE_COMPARE"


class Cache:
    def __init__(self, store, *, size, place_policy, evict_policy, write_policy):
        self._event_handlers = {}
        self.store = store
        self.size = size
        self.block_size = store.block_size
        self.total_entries = self.size // self.block_size
        self.place_policy = place_policy(self)
        self.evict_policy = evict_policy(self)
        self.write_policy = write_policy(self)
        self.entries = [CacheEntry() for _ in range(self.total_entries)]

    def on_event(self, event_name, callback):
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []

        self._event_handlers[event_name].append(callback)

    def dispatch(self, event_name, *args, **kwargs):
        handlers = self._event_handlers.get(event_name, [])

        for handler in handlers:
            handler(self, *args, **kwargs)

    def split_address(self, address):
        return self.place_policy.split_address(address)

    def get_cache_entry_set(self, index):
        return self.place_policy.get_cache_entry_set(index)

    def get_cache_entry(self, address):
        tag, index, _ = self.split_address(address)
        for cache_entry in self.get_cache_entry_set(index):
            self.dispatch("CACHE_COMPARE")
            if cache_entry.valid and tag == cache_entry.tag:
                return cache_entry

    def has_cache_entry(self, address):
        return self.get_cache_entry(address) is not None

    def is_cache_entry_set_full(self, index):
        for cache_entry in self.get_cache_entry_set(index):
            if not cache_entry.valid:
                return False
        return True

    def fetch_and_cache_block(self, address):
        tag, index, _ = self.split_address(address)
        block = self.store.read_block(address)

        if self.is_cache_entry_set_full(index):
            evicted = self.evict_policy.evict_cache_entry_from_set(address)
            self.dispatch("CACHE_EVICT", address, evicted)

        for cache_entry in self.get_cache_entry_set(index):
            if not cache_entry.valid:
                cache_entry.tag = tag
                cache_entry.block = block
                cache_entry.flags = 0
                cache_entry.dirty = 0
                cache_entry.valid = 1
                break

    def read_byte(self, address):
        *_, offset = self.split_address(address)

        if not self.has_cache_entry(address):
            self.dispatch("CACHE_MISS", address)
            self.fetch_and_cache_block(address)

        self.evict_policy.update_cache_entry_set(address)
        cache_entry = self.get_cache_entry(address)

        return (cache_entry.block >> (offset * 8)) & 0xFF

    def read_block(self, address):
        self.dispatch("CACHE_READ", address)
        block = 0
        for byte_address in reversed(range(address, address + self.block_size)):
            block <<= 8
            block |= self.read_byte(byte_address)
        return block

    def write_byte(self, address, byte):
        *_, offset = self.split_address(address)

        if not self.has_cache_entry(address):
            self.dispatch("CACHE_MISS", address)
            self.fetch_and_cache_block(address)

        self.evict_policy.update_cache_entry_set(address)
        cache_entry = self.get_cache_entry(address)
        cache_entry.dirty = 1

        shift = byte << (8 * offset)
        mask = 0xFF << (8 * offset)

        cache_entry.block = ~mask & cache_entry.block | shift

        self.dispatch("CACHE_WRITE", address, cache_entry)

    def write_block(self, address, block):
        for byte_address in range(address, address + self.block_size):
            self.write_byte(byte_address, block & 0xFF)
            block >>= 8
