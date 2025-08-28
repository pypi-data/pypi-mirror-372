# -*- coding: utf-8 -*-
"""
Python implementation of Austin Appleby's MurmurHash2 code.

https://github.com/aappleby/smhasher

Sources:
https://en.wikipedia.org/wiki/MurmurHash
https://github.com/aappleby/smhasher/blob/master/src/MurmurHash2.cpp
https://commons.apache.org/proper/commons-codec/jacoco/org.apache.commons.codec.digest/MurmurHash2.java.html
https://commons.apache.org/proper/commons-codec/jacoco/org.apache.commons.codec.digest/MurmurHash.java.html
"""


class MurmurHash2:

    __M32 = 0x5bd1e995
    __R32 = 24

    __M64 = 0xc6a4a7935bd1e995
    __R64 = 47

    @staticmethod
    def hash32(
        data: bytes,
        seed: int = 1,
    ) -> int:
        """
        Implementation of MurmurHash2 32 bits.

        Args
            data: bytes, data of file or string on bytes.
            seed: int; positive integer.

        Returns
            int: result of length 10 integers.
        """
        length = len(data)
        h = (seed ^ len(data)) & 0xFFFFFFFF

        i = 0
        while length >= 4:
            k = (data[i]) | (data[i+1] << 8) | (data[i+2] << 16) | (data[i+3] << 24)
            k = (k * MurmurHash2.__M32) & 0xFFFFFFFF
            k ^= (k >> MurmurHash2.__R32)
            k = (k * MurmurHash2.__M32) & 0xFFFFFFFF

            h = (h * MurmurHash2.__M32) & 0xFFFFFFFF
            h = h ^ k

            i += 4
            length -= 4

        # tails
        if length == 3:
            h ^= data[i + 2] << 16
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M32) & 0xFFFFFFFF

        elif length == 2:
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M32) & 0xFFFFFFFF

        elif length == 1:
            h ^= data[i]
            h = (h * MurmurHash2.__M32) & 0xFFFFFFFF

        h ^= (h >> 13)
        h = (h * MurmurHash2.__M32) & 0xFFFFFFFF
        h ^= (h >> 15)

        return h & 0xFFFFFFFF

    @staticmethod
    def hash64a(
        data: bytes,
        seed: int = 1,
    ) -> int:
        """
        Implementation of MurmurHash2 64 bits.

        Args
            data: bytes, data of file or string on bytes.
            seed: int; positive integer.

        Returns
            int: result of length 20 integers.
        """
        length = len(data)
        h = (seed ^ (len(data) * MurmurHash2.__M64)) & 0xFFFFFFFFFFFFFFFF

        i = 0
        while length >= 8:
            k = (data[i]) | \
                (data[i+1] << 8) | \
                (data[i+2] << 16) | \
                (data[i+3] << 24) | \
                (data[i+4] << 32) | \
                (data[i+5] << 40) | \
                (data[i+6] << 48) | \
                (data[i+7] << 56) & 0xFFFFFFFFFFFFFFFF

            k = (k * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            k ^= (k >> MurmurHash2.__R64)
            k = (k * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            h = h ^ k

            i += 8
            length -= 8

        # tails
        if length == 7:
            h ^= data[i + 6] << 48
            h ^= data[i + 5] << 40
            h ^= data[i + 4] << 32
            h ^= data[i + 3] << 24
            h ^= data[i + 2] << 16
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        elif length == 6:
            h ^= data[i + 5] << 40
            h ^= data[i + 4] << 32
            h ^= data[i + 3] << 24
            h ^= data[i + 2] << 16
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        elif length == 5:
            h ^= data[i + 4] << 32
            h ^= data[i + 3] << 24
            h ^= data[i + 2] << 16
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        elif length == 4:
            h ^= data[i + 3] << 24
            h ^= data[i + 2] << 16
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        elif length == 3:
            h ^= data[i + 2] << 16
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        elif length == 2:
            h ^= data[i + 1] << 8
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        elif length == 1:
            h ^= data[i]
            h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        h ^= (h >> MurmurHash2.__R64)
        h = (h * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
        h ^= (h >> MurmurHash2.__R64)

        return h & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def hash64b(
        data: bytes,
        seed: int = 1,
    ) -> int:
        """
        Implementation of MurmurHash2 64 bits optimized for 32-bit platforms.

        Args
            data: bytes, data of file or string on bytes.
            seed: int; positive integer.

        Returns
            int: result of length 20 integers.
        """
        length = len(data)
        h1 = (seed ^ (len(data) * MurmurHash2.__M64)) & 0xFFFFFFFFFFFFFFFF
        h2 = 0

        i = 0
        while length >= 8:
            k1 = (data[i]) | \
                (data[i+1] << 8) | \
                (data[i+2] << 16) | \
                (data[i+3] << 24)

            k2 = (data[i+4]) | \
                (data[i+5] << 8) | \
                (data[i+6] << 16) | \
                (data[i+7] << 24)

            k1 = (k1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            k1 ^= (k1 >> 47)
            k1 = (k1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            h1 = h1 ^ k1
            h1 = (h1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

            #
            k2 = (k2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            k2 ^= (k2 >> 47)
            k2 = (k2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            h2 = h2 ^ k2
            h2 = (h2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

            i += 8
            length -= 8


        # tails
        if length >= 4:
            k1 = (data[i]) | \
                (data[i+1] << 8) | \
                (data[i+2] << 16) | \
                (data[i+3] << 24)

            k1 = (k1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF
            k1 ^= (k1 >> 47)
            k1 = (k1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

            h1 = h1 ^ k1
            h1 = (h1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

            i += 4
            length -= 4

        # tails
        if length == 3:
            h2 ^= data[i + 2] << 16
            h2 ^= data[i + 1] << 8
            h2 ^= data[i]
            h2 = (h2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        elif length >= 2:
            h2 ^= data[i + 1] << 8
            h2 ^= data[i]
            h2 = (h2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        elif length >= 1:
            h2 ^= data[i]
            h2 = (h2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF


        h1 ^= (h2 >> 18)
        h1 = (h1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        h2 ^= (h1 >> 22)
        h2 = (h2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        h1 ^= (h2 >> 17)
        h1 = (h1 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        h2 ^= (h1 >> 19)
        h2 = (h2 * MurmurHash2.__M64) & 0xFFFFFFFFFFFFFFFF

        h = (h1 << 32) | h2

        return h & 0xFFFFFFFFFFFFFFFF
