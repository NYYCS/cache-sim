# Experimental Analysis on Different Caching Strategies

## Introduction

This reports shows the benchmark performance of various caching strategy in a simulated environment, analyses the advantage and disadvantage of each caching strategy and presents a optimal caching strategy for 2D matrix multiplication.

The various caching strategy can be divided into three distinct categories, namely placement policy, eviction policy and write policy.

Here is the definitions of cache terms that will be used throughout the report:

- **Cache Entry**: A storage unit for caching memory block inside cache
- **Cache Entry Set**: A set comprising of one or more cache entry, the size of a cache entry set is determined by the placement policy
- **Tag**: Bits that determine the exact address of a memory block inside a cache entry
  The experiment benchmarks common caching strategy which will be given a brief overview below.

Cache entry has the following structure
```
[ tag ][ block ][ flags ][ dirty ][ valid ]
tag: for comparing address
block: cached memory block
flags: flags for evict policy
dirty: is cache entry written
valid: is cache entry valid
```

### Placement Policy

Cache is always smaller in size when compared to a backing store. To cache a specific memory block from a backing store, there is a question of where should the cache place the memory block inside itself.

Placement policy dictates the possible position of a memory block inside the cache.

There are three types of placement policies:

- Direct Mapping: A memory block can only take up a single position in cache.
- Set Associative: A memory block can take up multiple position in cache.
- Fully Associative: A memory block can freely take up any position in cache.

### Eviction Policy

If a cache is full, the cache needs to decide which cache entry to be evicted to allow new memory block to be cached

Eviction policy dictates which cache entry to evict

Common eviction policies:

- LRU ( Least Recently Used ): Evicts the least recently used cache entry
- LFU ( Least Frequently Used ): Evicts the least frequently used cache entry

### Write Policy

When data is written to the cache, the cache must decide when to update the data to the backing store

Write policy dictates when to update the data

Common write policies:

- Write Through: Data is immediately written to the backing store
- Write Back: Data is written only after the associated cache entry is evicted from cache

# Benchmark

## Setup

A simulation of matrix multiplication is used to calculate different caching strategies hit ratio in CPU.

Any read / write to the memory is first checked in the cache, if a cache miss occurs, the cache reads / writes data from the memory based on the caching strategy.

A cache entry is evicted based on the eviction policy if there is a cache conflict and the associated cache entry set is full.

A counter keep tracks of all read, write, evict, miss, tag comparisons, serving as the benchmarking data.

## Metrics

A cache most important metric is its hit ratio, this be calculated using the formula:

```
hit ratio = 1 - total_misses / total_reads
```

Hence, hit ratio can also be optimized by decreasing total cache miss.

Another metric to consider is the tag comparisons. Although not computationally expensive to compare cache entry tag, the sheer amount of tag comparisons is also a factor to consider when optimizing cache design on a hardware level.

## Performance

```
Hit Ratio of Place Policy / Evict Policy

                            Hit Ratio  Comparison
---------------------  ---  ---------  ----------
Fully Associative      LFU  0.0104103   231661569
4-way Set Associative  LFU  0.310501     17999456
2-way Set Associative  LFU  0.469733     16320450
Direct Mapping          -   0.549703     12681216
2-way Set Associative  LRU  0.633057     18571312
4-way Set Associative  LRU  0.635824     34347684
Fully Associative      LRU  0.645837   1668654022
---------------------  ---  ---------  ----------
```

### Place Policy

![Place Policy against Hit Ratio](./Average%20Hit%20Ratio%20Different%20Place%20Policy.png)

From the graph, we can see that fully associative cache has the highest hit ratio, while direct mapping cache has the lowest. We know that if a read is a cache miss, the cache will any cache entry. Using this perspective, is easy to see why full associative cache has the highest hit ratio. A memory block can freely be placed in any cache entry, hence it has a lower chance of evicting a cache entry, compare this to direct mapping cache, where a memory block has only one position to take, thus more easily causing cache conflicts, raising the amount of evicts.

While fully associative cache might have the highest ratio, one also need to take into consideration the amount of tag comparisons it must do for every read. For every read, a fully associative cache will at worst cases compare every cache entry tag to find a check for cache hits, while a direct mapping cache will always only compare cache entry tag once for cache hits.

Set associative cache is essentially the spectrum between direct mapping and fully associative caches, offering both sides advantage albeit slightly more complex to implement.

![Place Policy against Tag Comparisons](./Tag%20Comparisons%20Across%20Different%20Placement%20Policy.png)

Using the above two graph, we can see that set associative cache offers extremely competitive hit ratios with fully associative cache, while having extremely low total tag comparisons.

### Evict Policy

![Evict Policy against Hit Ratio](./Hit%20Ratio%20Across%20Different%20Placement%20Policy.png)

The evict policy cache hit data for direct mapped cache is omitted as direct mapped cache does not have a evict policy.

We can see that LRU average hit ratio is significantly higher that LFU, this is largely due to the read pattern of matrix multiplication.

Each term of the result can be expressed as:

```
    c[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j] + ... + a[i][n] * b[n][j]
Where i, j is the position of the element, n is the size of the matrix
```

Computing each `c[i][j]` requires at least `n` times of reads, hence it is important to cache `c[i][j]`

For each iteration of adding `a[i][k] + b[k][j]` to `c[i][j]`, a LRU cache will always cache `c[i][j]`, a LFU cache might evict `c[i][j]`, as it will the element before (i, j) has more uses of `a[i][k] + b[k][j]`, therefore evicting `c[i][j]` from cache.

For small enough LRU caches, `c[i][j]` might never be cached as the previous `a[i][k] + b[k][j]` uses is simply too much for `a[i][k] + b[k][j]` to be evicted, therefore not enough space for `c[i][j]`.

### Write Policy

![Write Policy against Writes](./Hit%20Ratio%20Across%20Different%20Placement%20Policy.png)

As we can see write back cache has lower writes to backing store, therefore write back cache should be preferred when designing cache. However it does come at the cost of having to compare the `dirty` bit every time a cache entry gets evicted from cache.

### LFU Evict Policy

Cache with LFU evict policy compared comparatively worse than LRU caches, this is in large part due to the nature of matrix multiplication, which exhibits extremely high temporal locality, therefore it is unsuited for caching matrix multiplication.

LFU cache should be used for read patterns that exhibit high frequency reads of specific resources, an example of this is a DNS cache, where most of network traffic are directed towards a set of well known hostnames, using LRU cache isn't suitable as a recently resolved and relatively unknown hostname will be cached, thereby evicting more popular hostname IP address, causing more cache misses.

### Optimal Common Caching Strategy for Matrix Multiplication

Using the caching strategy with the highest hit ratio, namely full associative with LRU, the hit ratio is around `0.64`, however when factoring in the disproportionate amount of tag comparisons associated with fully associative cache, a better design might be a 2-way associative cache with LRU with hit ratio of about `0.63`, however its tag comparisons is comparatively much more lower, roughly only one percent of the total tag comparisons of a fully associative cache.

Thereforce this report suggest that a 2-way associative cache, LRU, write back cache is most optimal for matrix multiplication.