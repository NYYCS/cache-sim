import random

from cache_stats import CacheStats

def mat_mul(cache, *, matrix_size):
    stats = CacheStats(cache)

    def mat_create(address):
        for i in range(matrix_size):
            for j in range(matrix_size):
                elem = random.randint(0, 3)
                block_address = address + ((i * matrix_size) + j) * cache.block_size
                cache.write_block(block_address, elem)
        return address
    
    MATRIX_SIZE = matrix_size * matrix_size * cache.block_size
    mat_a = mat_create(0)
    mat_b = mat_create(MATRIX_SIZE)
    mat_c = 2 * MATRIX_SIZE

    for i in range(matrix_size):
        for j in range(matrix_size):
            for k in range(matrix_size):
                elem_a = cache.read_block(mat_a + (i * matrix_size + k) * 4)
                elem_b = cache.read_block(mat_b + (k * matrix_size + j) * 4)
                elem_c = cache.read_block(mat_c + (i * matrix_size + j) * 4)
                cache.write_block(mat_c + (i * matrix_size + j) * 4, elem_c + (elem_a * elem_b))

    return stats