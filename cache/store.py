import numpy as np
import math


class Store:

    def __init__(self, *, size, block_size):
        self.size = size
        self.block_size = block_size
        self._bytes = np.zeros(self.size).astype(int)

        self.reads = 0
        self.writes = 0
        
    def read_byte(self, address):
        return self._bytes[address]

    def read_block(self, address):
        self.reads += 1
        address = math.floor(address / self.block_size) * self.block_size
        block = 0
        for index in reversed(range(address, address + self.block_size)):
            block <<= 8
            block |= self._bytes[index]
        return block

    def write_byte(self, address, byte):
        self._bytes[address] = byte
    
    def write_block(self, address, block):
        self.writes += 1
        address = math.floor(address / self.block_size) * self.block_size
        for byte_address in range(address, address + self.block_size):
            self.write_byte(byte_address, block & 0xFF)
            block >>= 8