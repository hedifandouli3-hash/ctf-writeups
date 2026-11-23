# Shifted Slice — a reproducible WolvCTF 2026 case study

**Category:** Web / Cryptographic Integrity  
**Competition:** WolvCTF 2026  
**Artifacts:** an original challenge-list screenshot, transcript excerpts supplied by the solver, 25 archived XOR-difference vectors, and self-contained offline verification scripts.

![Original challenge-list screenshot](images/challenge_tile_original.png)

*Figure 1. Original uploaded screenshot of the WEB challenge list. The highlighted tile is consistent with the solver's reported completion; this image is not a literal flag-acceptance message.*

## TL;DR

An owned-record ticket was issued when `z-owned` occupied bytes **112–175** of a 304-byte serialized bundle. Later captured manifests showed a different record at those same positions. The archived client transcript reports a 64-byte response when the earlier ticket was reused. What came back was binary data, **not a readable flag**. A separate offline investigation used byte differences from 25 sessions and a known record format to reconstruct a candidate. The user reports a solved challenge; the original submission receipt has not been supplied here.

This version differs from the earlier short summary: you can now **execute the offline reconstruction yourself**, with no dependency on a live server or third-party Python library. The archive does not contain the original challenge source or a complete packet capture, so the reproduced part is the *mathematical verification from saved deltas*, not a fresh online replay of a closed competition service.

## 1. Files and quick start

The download contains:

```text
Shifted_Slice_Reproducible/
├── README.md
├── data/
│   └── deltas.txt                 # 25 user-supplied 64-byte XOR deltas
├── images/
│   ├── challenge_tile_original.png
│   └── layout_comparison.png
├── scripts/
│   ├── inspect_layout.py          # Calculate both manifest layouts
│   ├── solve_offline.py           # Derive the candidate from the deltas
│   └── verify_offline.py          # Check all recorded deltas
└── Shifted_Slice_Writeup.pdf
```

Requirements: **Python 3.9+**; standard library only. Open a terminal in the extracted directory and run:

```bash
python scripts/inspect_layout.py
python scripts/solve_offline.py
python scripts/verify_offline.py
```

The solver should print **29 single-candidate offsets**, a four-byte framing result, and the reconstructed `wctf{...}` candidate. The verifier should print **PASS: 25/25**. If anything differs, compare `data/deltas.txt` with the recorded vectors rather than editing the expected output.

## 2. The first clue: tickets and bytes are different things

The saved API responses indicate that users could request a ticket for `z-owned`, whereas ticket requests for `m-sealed` and other keys were rejected. At revision 0, the captured manifest was:

```json
{
  "revision": 0,
  "total_bytes": 304,
  "records": [
    {"key": "m-sealed",   "kind": "sealed", "bytes": 64},
    {"key": "p-public",   "kind": "public", "bytes": 48},
    {"key": "z-owned",    "kind": "owned",  "bytes": 64},
    {"key": "zz-scratch", "kind": "owned",  "bytes": 128}
  ]
}
```

The contiguous layout is obtained by summing the sizes of the preceding records:

| Record | Bytes | Inclusive positions |
|---|---:|---|
| `m-sealed` | 64 | 0–63 |
| `p-public` | 48 | 64–111 |
| `z-owned` | 64 | **112–175** |
| `zz-scratch` | 128 | 176–303 |

The archived response to a ticket request for the owned record included `"range": "bytes=112-175"` and `"revision": 0`. Thus, **the authorized logical object** (`z-owned`) was represented in the ticket response by **a positional range** (112–175). A base64url-decoded sample ticket has 59 bytes and contains big-endian integers corresponding to start 112, end 175, and bundle size 304. The trailing 32 bytes *may* be a signature or MAC; without source code or key material the exact algorithm is not verified.

## 3. The central observation: the bundle can move

Another preserved manifest, after modifications made by the original test scripts, listed:

| Record | Bytes | Inclusive positions |
|---|---:|---|
| `a-pub` | 48 | 0–47 |
| `b-pub` | 64 | 48–111 |
| `m-sealed` | 64 | **112–175** |
| `z-owned` | 64 | 176–239 |
| `zz-scratch` | 64 | 240–303 |

The total is still 304. The record identity at positions 112–175 changed from `z-owned` to `m-sealed`.

![Original and modified manifest layouts](images/layout_comparison.png)

*Figure 2. Diagram calculated from the two supplied manifests. The outlined interval is the original ticket range, not a second ticket.*

This establishes the **layout change**. It does *not* by itself prove that an old ticket is still accepted. For that, we need the original client's saved outcome.

### How the archived investigation proceeded (reported, not re-executed here)

The Antigravity audit maps these investigation phases to original files and transcript entries:

1. `explore_shifted.py` and `read_slice.py` inspected the manifest and observed the ticket issued for `z-owned` (reported transcript Step 666).
2. `probe_tickets.py` tested key restrictions, reporting 403 responses for other keys (reported Step 1093).
3. `test_solution.py` captured the reordered manifest and read result (reported Step 743). Its notes describe a record rename, a public-record addition and compaction. **These steps are historical evidence, not requests made while preparing this package.**
4. `test_owned_known.py` described comparisons with a known note record in a separate experimental layout; those measurements led to saved XOR deltas.
5. `twentyfive_session_analysis.py`, `solve_closing_brace.py`, and `verify_flag_solution.py` performed offline reconstruction and checking (reported Steps 2204, 2159/3274, and 2208).

The experiment using `x-known` was **a separate experiment** from the manifest placing `m-sealed` at 112–175. Do not combine their layouts into one imagined request sequence.

## 4. What the historical client actually received

The user-provided excerpt of `test_solution.py` shows this response handling:

```python
resp = opener.open(req_bundle)
content = resp.read()
print("SUCCESS! Read length:", len(content))
print("Content (hex):", content.hex())
print("Content (raw):", content)
```

Recorded output (truncated here, full string in the audit):

```text
SUCCESS! Read length: 64
Content (hex): eaf087610841b7693ebfc6a59ede2799...
```

Because `resp.read()` returns the HTTP response body, the script handled the received bytes without an explicit `.decode()`, `.strip()`, or decompression step. `content.hex()` changed their *display*, not their contents. The transcript's printed output does not include a raw HTTP status line or `Content-Range` response header. A successful `urllib.request.urlopen` path is consistent with a non-error response, but we cannot name its exact status from this printout.

The evidence supports that the old range was apparently accepted even after the record layout changed. The more specific assertion that the server's revision-checking code was missing is **a plausible explanation**, not a directly inspected implementation fact.

## 5. Why reading 64 bytes was not yet the end

The response was binary, and the 64 returned bytes were not directly readable as `wctf{...}` text. The original investigation therefore treated access control and cryptographic interpretation separately.

The offline analysis uses the relationship between two aligned byte strings under a shared masking stream:

```text
Csealed = Psealed XOR K
Cknown  = Pknown  XOR K
--------------------------------
Delta   = Csealed XOR Cknown
        = Psealed XOR Pknown
```

**Assumptions matter:** each paired comparison must use matching keystream positions and correct record framing. Session-to-session variations in the resulting deltas reflect differences in compared plaintext values (and alignment), not simply “different random keystreams.” This package accepts the **recorded deltas** as input; it does not claim to reproduce the original server-side cryptographic collection.

## 6. Deriving the first 29 characters from the saved data

The analysis assumes that each position of the secret's inner token and the corresponding known-note field is a **lowercase hexadecimal** character. Let `H` be the 16-byte ASCII alphabet `0123456789abcdef`.

At a given absolute byte offset `j`, an admissible secret character `x` must satisfy:

```text
x in H and (x XOR Delta_session[j]) in H
```

Because the secret text is assumed fixed, every saved session supplies another constraint on `x`. Intersect these constraints across all 25 vectors. `scripts/solve_offline.py` executes this exact calculation for offsets **18 through 46**:

```python
for offset in range(18, 47):
    options = {
        c for c in ALPHABET
        if all((c ^ d[offset]) in ALPHABET for d in deltas)
    }
    if len(options) != 1:
        raise ValueError(f"Offset {offset}: {len(options)} candidates")
```

Using the 25 vectors in `data/deltas.txt`, **each of these 29 offsets has exactly one surviving character**. The program prints every candidate count and the resulting prefix. This is a locally rerunnable observation, not merely a claim copied from the audit.

## 7. Resolving the last three characters and brace

The saved investigation attributes the remaining characters to a known record-framing sequence: `\nowned`, beginning at byte position 47 of the paired note record. The relevant delta starts `39 0e 4f 13` in every supplied vector. In the original notes, the calculations are:

| Offset | Delta | Assumed known-note character | Result in sealed record |
|---:|---|---|---|
| 47 | `0x39` | newline (`0x0a`) | `0x33` = `3` |
| 48 | `0x0e` | `o` (`0x6f`) | `0x61` = `a` |
| 49 | `0x4f` | `w` (`0x77`) | `0x38` = `8` |
| 50 | `0x13` | `n` (`0x6e`) | `0x7d` = `}` |

The included solver checks that the same four-byte result follows from **every supplied delta**; it does not simply append a hardcoded suffix. The framing assumption comes from the user's archived description of the record format and was not separately established from server source in this workspace.

Putting the two stages together yields the archived **candidate**, printed when you run the solver. The script includes checks for its expected format and length.

## 8. Verification: test the hypothesis instead of trusting it

Run:

```bash
python scripts/verify_offline.py
```

This program recomputes the 29 singleton candidates and the inferred trailer, then checks that the plaintext implied by each session delta stays within the lowercase-hex alphabet. It prints a per-session result followed by:

```text
PASS: 25/25 recorded vectors match the candidate and known-framing assumptions
```

This is **mathematical consistency relative to the saved vectors**. It is not the same as an independent successful submission of the exact string to CTFd. The user reports a completed challenge, and the original screenshot is consistent with that report, but no explicit accepted-submission receipt is present in the supplied evidence.

## 9. Where the reconstruction stops

The publicly shareable reconstruction has three different confidence levels:

| Claim | Evidence level |
|---|---|
| Contiguous layouts and range equality | Direct arithmetic from pasted manifests; independently rerunnable |
| 25-session intersections and candidate format | Independently executed on user-supplied vectors in this package |
| Earlier ticket apparently accepted after changed layout | Reported client stdout, not independently replayed live |
| Exact server revision-validation routine, token MAC algorithm | Inferred, no backend source |
| Explicit flag acceptance by challenge platform | User-reported; highlighted screenshot supports but does not directly display receipt |

The original Antigravity files (`test_solution.py`, `test_owned_known.py`, `transcript.jsonl`, and others) were **not uploaded as original files here**. The scripts in this folder are **new offline reproductions** based on user-provided extracts, **not copies falsely attributed to the original investigation**.

## 10. Takeaway

The authorization story is about *which object is allowed to be read*: a signature on an old byte range is insufficient if records move underneath it. The cryptographic story is about *what a binary read reveals*: paired representations may still leak relationships about underlying plaintext. For a credible CTF write-up, show the clue, the hypothesis, the observed result, the independently reproducible calculation, and the limits of your evidence.

**Provenance:** Written from the user's saved manifest/ticket/client excerpts, Antigravity audit (`Pasted text(8).txt`), supplied 25 difference vectors, described local execution logs, and uploaded original challenge-list screenshot. The original live server was not contacted while preparing this document.
