#!/usr/bin/env python3
"""Reproduce byte ranges from the two captured manifest record lists."""
ORIGINAL = [("m-sealed",64),("p-public",48),("z-owned",64),("zz-scratch",128)]
SHIFTED  = [("a-pub",48),("b-pub",64),("m-sealed",64),("z-owned",64),("zz-scratch",64)]

def show(records):
    pos = 0
    ranges = {}
    for key, size in records:
        print(f"  {key:<12} {pos:>3}..{pos+size-1:<3} ({size} bytes)")
        ranges[key] = (pos, pos+size-1)
        pos += size
    assert pos == 304
    print("  Total:", pos, "bytes")
    return ranges

if __name__ == '__main__':
    print('Revision 0')
    before=show(ORIGINAL)
    print('\nModified layout')
    after=show(SHIFTED)
    assert before['z-owned'] == (112,175)
    assert after['m-sealed'] == (112,175)
    print('\nObserved mismatch: bytes 112-175 moved from z-owned to m-sealed.')
