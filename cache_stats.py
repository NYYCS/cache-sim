class CacheStats:
    def __init__(self, cache):
        self.cache = cache
        self.reads = 0
        self.misses = 0
        self.evicts = 0
        self.comparisons = 0

        cache.on_event("CACHE_READ", self.increment_read)
        cache.on_event("CACHE_MISS", self.increment_misses)
        cache.on_event("CACHE_EVICT", self.increment_evicts)
        cache.on_event("CACHE_COMPARE", self.increment_comparisons)

    def increment_read(self, *_):
        self.reads += 1

    def increment_misses(self, *_):
        self.misses += 1

    def increment_evicts(self, *_):
        self.evicts += 1

    def increment_comparisons(self, *_):
        self.comparisons += 1

    @property
    def writes(self):
        return self.cache.store.writes

    @property
    def hit_ratio(self):
        return 1.0 - (self.misses / self.reads)
