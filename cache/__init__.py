from .cache import Cache
from .store import Store
from .place_policy import DirectMapping, FullyAssociative, TwoWaySetAssociative, FourWaySetAssociative
from .evict_policy import LRU, LFU
from .write_policy import WriteThrough, WriteBack

class PlacePolicy:
    DirectMapping = DirectMapping
    FullyAssociative = FullyAssociative
    TwoWaySetAssociative = TwoWaySetAssociative
    FourWaySetAssociative = FourWaySetAssociative

class EvictPolicy:
    LRU = LRU
    LFU = LFU

class WritePolicy:
    WriteThrough = WriteThrough
    WriteBack = WriteBack

__all__ = (
    Cache,
    Store,
    PlacePolicy,
    EvictPolicy,
    WritePolicy
)