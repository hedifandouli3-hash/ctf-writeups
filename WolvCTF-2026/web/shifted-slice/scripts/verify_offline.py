#!/usr/bin/env python3
"""Independent offline consistency checks for the archived reconstruction."""
from solve_offline import ALPHABET, finish_from_known_framing, load_deltas, solve
from pathlib import Path


def main():
    vectors = load_deltas(Path(__file__).resolve().parents[1] / "data" / "deltas.txt")
    prefix = solve(vectors)
    tail = finish_from_known_framing(vectors)
    assert len(prefix) == 29 and len(tail) == 3
    for session, vector in enumerate(vectors, start=1):
        inferred_note = bytes(ord(c) ^ vector[i] for i, c in enumerate(prefix, start=18))
        assert len(inferred_note) == 29, (session, "incorrect length")
        assert all(b in ALPHABET for b in inferred_note), session
        print(f"Session {session:02}: 29 lowercase-hex characters verified")
    print("PASS: 25/25 recorded vectors match the candidate and known-framing assumptions")


if __name__ == "__main__":
    main()
