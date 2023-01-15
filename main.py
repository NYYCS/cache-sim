import multiprocessing
import itertools
import pandas as pd

from cache import Cache, Store, PlacePolicy, EvictPolicy, WritePolicy
from mat_mul import mat_mul


STORE_SIZE = 65536
STORE_BLOCK_SIZE = 4
CACHE_SIZE = 1024

MATRIX_SIZE = 64

place_policies = (
    ("Direct Mapping", PlacePolicy.DirectMapping),
    ("2-way Set Associative", PlacePolicy.TwoWaySetAssociative),
    ("4-way Set Associative", PlacePolicy.FourWaySetAssociative),
    ("Fully Associative", PlacePolicy.FullyAssociative),
)

evict_policies = (("LRU", EvictPolicy.LRU), ("LFU", EvictPolicy.LFU))

write_policies = (
    ("Write Through", WritePolicy.WriteThrough),
    ("Write Back", WritePolicy.WriteBack),
)   


def cache_test(place_policy, evict_policy, write_policy, queue):
    place_policy_name, place_policy = place_policy
    evict_policy_name, evict_policy = evict_policy
    write_policy_name, write_policy = write_policy
    test_name = f"{place_policy_name} + {evict_policy_name} + {write_policy_name}"
    store = Store(size=STORE_SIZE, block_size=STORE_BLOCK_SIZE)
    cache = Cache(
        store,
        size=CACHE_SIZE,
        place_policy=place_policy,
        evict_policy=evict_policy,
        write_policy=write_policy,
    )
    stats = mat_mul(cache, matrix_size = MATRIX_SIZE)
    queue.put((test_name, stats))


if __name__ == "__main__":
    print("Running tests...")
    test_results = multiprocessing.Queue()

    df = pd.DataFrame(
        {
            "Cache Strategy": [],
            "Writes": [],
            "Hit Ratio": [],
            "Comparisons": [],
        }
    )

    cache_tests = [
        multiprocessing.Process(
            target=cache_test,
            args=(
                place_policy,
                evict_policy,
                write_policy,
                test_results,
            ),
        )
        for place_policy, evict_policy, write_policy in itertools.product(
            place_policies, evict_policies, write_policies
        )
    ]

    for test in cache_tests:
        test.start()

    for i, test in enumerate(cache_tests):
        test_name, stats = test_results.get()
        place_policy, evict_policy, write_policy = test_name.split("+")
        df.loc[len(df.index)] = {
            "Place Policy": place_policy,
            "Evict Policy": evict_policy,
            "Write Policy": write_policy,
            "Writes": stats.writes,
            "Hit Ratio": stats.hit_ratio,
            "Comparisons": stats.comparisons,
        }

    df.to_csv("test_results.csv")
    print("Done all tests!")
