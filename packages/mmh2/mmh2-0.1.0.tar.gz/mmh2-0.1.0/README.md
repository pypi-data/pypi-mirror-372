# mmh2

Python implementation of Austin Appleby's MurmurHash2 code.

> [smhasher](https://github.com/aappleby/smhasher)


# Usage

```python
>>> from mmh2 import MurmurHash2
>>>
>>> MurmurHash2.hash32(b"abc", 0)
324500635
>>> MurmurHash2.hash64a(b"abc", 0)
11297775770902552315
>>> MurmurHash2.hash64b(b"abc", 0)
14767186587890852743
```
