Versaload
=========

## Faster data encoding from cassette for retro platforms
Most cassette loading systems use two symbols, one twice the length of the other. For example, the Sinclair Spectrum ROM loader has the following timings (note 3.5T = 1μs):
```
 ___
|   |___|         '0' in 1710T (489μs per bit), probability 50.0%
 _______
|       |_______| '1' in 3420T (977μs per bit), probability 50.0%
```
Note that a sequence of '1's loads at half the speed of '0's. This gives a data rate of around *1364 bits/sec*. In an attempt to speed up loading speeds and make cassette tapes harder to copy, games manufacturers developed faster loaders that were still reliable enough to make it through replication and work on consumer equipment. One of the fastest was used by [Microsphere](http://www.worldofspectrum.org/infoseekpub.cgi?regexp=^Microsphere$ ), which runs at double the speed of the default loader, *2729 bits/sec*:
```
 _
| |_|             '0' in 855T (244μs per bit), probability 50.0%
 ___
|   |___|         '1' in 1710T (489μs per bit), probability 50.0%
```
The Commodore C64 was known for its extremely slow loading, so both commercial developers and home users were quick to speed things up. One of the most popular home speedup systems was [Turbotape](http://codebase64.org/doku.php?id=base:turbotape_loader_source), which was both reliable and fast. This uses timing similar to Microsphere, but note that the '1' bit is not double the length of the '0' bit.
```
 _
| |_|   '0' in 216μs (216μs per bit), probability 50.0%
 __
|  |__| '1' in 326μs (326μs per bit), probability 50.0%
```
This gives a data rate of around *3690 bits/sec*. But all this information tells us we can use pulse lengths between 216μs and 977μs, so why not use them all? Because the longer the symbols, the slower the load. But techniques such as [Huffman coding](http://en.wikipedia.org/wiki/Huffman_coding) and [range coding](http://en.wikipedia.org/wiki/Range_encoding) can maximise the data rate, taking advantage of the longer symbols. Versaload proposes the following timings:
```
 _
| |_|               220μs, probability 27.3%
 __
|  |__|             330μs, probability 18.2%
 ___
|   |___|           440μs, probability 13.7%
 ____
|    |____|         550μs, probability 10.9%
 _____
|     |_____|       660μs, probability  9.1%
 ______
|      |______|     770μs, probability  7.8%
 _______
|       |_______|   880μs, probability  6.8%
 ________
|        |________| 990μs, probability  6.1%

```
This gives a data rate of around *6607 bits/sec* for the same data rate. That is the theory, but practical tests will be conducted when the code is functionally complete. Experiments are ongoing...
