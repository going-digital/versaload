Versaload
=========

Cassette tape loading from the future for the ZX Spectrum.

## Faster data encoding
Further 40% speedup using 4 symbol modulation. The Sinclair ROM loader has the following timings:
```
 ___
|   |___|         '0' in 855T (855T per bit)
 _______
|       |_______| '1' in 1710T (1710T per bit)
```
Note that a sequence of '1's loads at half the speed of '0's. Next, the Microsphere loader, as used in all the Microsphere games. It runs at double the speed of the ROM loader:
```
 _
| |_|             '0' in 428T (428T per bit)
 ___
|   |___|         '1' in 855T (855T per bit)
```
Now Versaload, which uses the full timing range of both methods:
```
 _
| |_|             '0' in 428T (428T per bit)
 ___
|   |___|         '10' in 855T (428T per bit)
 _____
|     |_____|     '111' in 1283T (428T per bit)
 _______
|       |_______| '110' in 1710T (570T per bit)
```
Note that common sequences like '0000...', '101010...' and '1111...' are all encoded at 428T per bit, and even the worst case pattern '110110...' is encoded at 570T per bit.
