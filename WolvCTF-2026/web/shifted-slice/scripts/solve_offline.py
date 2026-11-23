#!/usr/bin/env python3
"""Reproduce the archived 25-session candidate derivation entirely offline.

Input: data/deltas.txt, 25 sixty-four-byte hexadecimal difference vectors.
No network access, external packages, or CTF server required.
"""
from pathlib import Path
import argparse

ALPHABET = set(map(ord, "0123456789abcdef"))
EXPECTED_PREFIX = "2ad127e3d6d87a29e350f89b89c41"


def load_deltas(path: Path) -> list[bytes]:
    lines = [line.strip() for line in path.read_text(encoding="ascii").splitlines() if line.strip()]
    deltas = [bytes.fromhex(line) for line in lines]
    if len(deltas) != 25 or any(len(d) != 64 for d in deltas):
        raise ValueError(f"Expected 25 vectors, each exactly 64 bytes; got {len(deltas)} vectors")
    return deltas


def solve(deltas: list[bytes]) -> str:
    result = []
    print("Offset | Candidates | Values")
    print("-------+------------+----------------")
    for offset in range(18, 47):
        options = {c for c in ALPHABET if all((c ^ d[offset]) in ALPHABET for d in deltas)}
        chars = "".join(sorted(map(chr, options)))
        print(f"{offset:>6} | {len(options):>10} | {chars}")
        if len(options) != 1:
            raise ValueError(f"Offset {offset} has {len(options)} candidates: {chars!r}")
        result.append(chars)
    return "".join(result)


def finish_from_known_framing(deltas: list[bytes]) -> str:
    # The paired note record framing contains '\nowned' beginning at absolute byte index 47.
    known = b"\nowned"
    tail = bytes(deltas[0][47 + index] ^ char for index, char in enumerate(known[:4]))
    for i, d in enumerate(deltas[1:], 1):
        if bytes(d[47 + idx] ^ c for idx, c in enumerate(known[:4])) != tail:
            raise ValueError(f"Framing mismatch in delta {i+1}")
    print("Trailer inferred from known framing (47..50):", repr(tail))
    if not (all(chr(c) in "0123456789abcdef" for c in tail[:3]) and tail[3:4] == b"}"):
        raise ValueError("Trailer does not match expected three hex characters and closing brace")
    return tail[:3].decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deltas", type=Path, default=Path(__file__).resolve().parents[1]/"data"/"deltas.txt")
    args = parser.parse_args()
    deltas = load_deltas(args.deltas)
    prefix = solve(deltas)
    suffix = finish_from_known_framing(deltas)
    candidate = "wctf{" + prefix + suffix + "}"
    print("Unique candidate across offsets 18..46:", prefix)
    print("Derived ending from framing:", suffix + "}")
    print("Reconstructed candidate:", candidate)
    print("Candidate length:", len(candidate))
    assert prefix == EXPECTED_PREFIX
    assert len(candidate) == 38


if __name__ == "__main__":
    main()
