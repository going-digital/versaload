Versaload
=========

## Faster data encoding on the ZX Spectrum
Further 35% speedup using 4 symbol modulation. The Sinclair ROM loader has the following timings (note 3.5T = 1μs):
```
 ___
|   |___|         '0' in 1710T (489μs per bit)
 _______
|       |_______| '1' in 3420T (977μs per bit)
```
Note that a sequence of '1's loads at half the speed of '0's. This gives a data rate of around *1364 bits/sec*. Next, the Microsphere loader, as used in all the Microsphere games. It runs at double the speed of the ROM loader, *2729 bits/sec*:
```
 _
| |_|             '0' in 855T (244μs per bit)
 ___
|   |___|         '1' in 1710T (489μs per bit)
```
Now Versaload, which uses the full timing range of both methods:
```
 _
| |_|             '0' in 855T (244μs per bit)
 ___
|   |___|         '10' in 1710T (244μs per bit)
 _____
|     |_____|     '111' in 2565T (244μs per bit)
 _______
|       |_______| '110' in 3420T (326μs per bit)
```
Note that common sequences like '0000...', '101010...' and '1111...' are all encoded at 244μs per bit, and even the worst case pattern '110110...' is encoded at 326μs per bit. For a random data sequence, the typical data rate is *3686 bits/sec*.

## Faster data encoding on the Commodore machines
The ROM loader on the Commodore machines is universally recognised as being spectacularly slow due to its aggressive use of unnecessary data duplication and framing. However, a commonly used alternative was TurboTape.
```
 _
| |_|   '0' in 216μs (216μs per bit)
 __
|  |__| '1' in 326μs (326μs per bit)
```
This gives a data rate of around *3690 bits/sec*. Versaload uses the following timings:
```
 _
| |_|       '00' in 220μs (110μs per bit)
 __
|  |__|     '01' in 330μs (165μs per bit)
 ___
|   |___|   '11' in 440μs (220μs per bit)
 ____
|    |____| '10' in 550μs (275μs per bit)

```
This gives a data rate of around *5195 bits/sec* for the same data rate. These timings may be applicable to the ZX Spectrum too. Experiments are ongoing.
