Versaload
=========

## Faster data encoding from cassette for retro platforms
Most cassette loading systems use two symbols, one twice the length of the other. For example, the Sinclair Spectrum ROM loader has the following timings (note 3.5T = 1μs):
```
 ___
|   |___|         489μs (1710T), probability 50.0%, '0'
 _______
|       |_______| 977μs (3420T), probability 50.0%, '1'
```
Note that a sequence of '1's loads at half the speed of '0's. This gives a data rate of around *1535 bit∙s⁻¹*. In an attempt to speed up loading speeds and make cassette tapes harder to copy, games manufacturers developed faster loaders that were still reliable enough to make it through replication and work on consumer equipment. One of the fastest was used by [Microsphere](http://www.worldofspectrum.org/infoseekpub.cgi?regexp=^Microsphere$ ), which runs at double the speed of the default loader, *3070 bit∙s⁻¹*:
```
 _
| |_|               244μs (855T), probability 50.0%, '0'
 ___
|   |___|           489μs (1710T), probability 50.0%, '1'
```
The Commodore C64 was known for its extremely slow loading, so both commercial developers and home users were quick to speed things up. One of the most popular home speedup systems was [Turbotape](http://codebase64.org/doku.php?id=base:turbotape_loader_source), which was both reliable and fast. This uses timing similar to Microsphere, but note that the '1' bit is not double the length of the '0' bit, which gives a substantial speed boost.
```
 _
| |_|               216μs, 50.0%, '0'
 __
|  |__|             326μs, 50.0%, '1'
```
This gives a data rate of around *3849 bit∙s⁻¹*. But all this information tells us we can use pulse lengths between 216μs and 977μs, so why not use them all? Because the longer the symbols, the slower the load. But techniques such as [Huffman coding](http://en.wikipedia.org/wiki/Huffman_coding) and [range coding](http://en.wikipedia.org/wiki/Range_encoding) can maximise the data rate, taking advantage of the longer symbols. The bit rate is maximised by the following proportions:
```
 _
| |_|               220μs, 23.5%
 __
|  |__|             330μs, 19.4%
 ___
|   |___|           440μs, 15.3%
 ____
|    |____|         550μs, 12.2%
 _____
|     |_____|       660μs,  9.6%
 ______
|      |______|     770μs,  8.0%
 _______
|       |_______|   880μs,  6.5%
 ________
|        |________| 990μs,  5.5%

```
This gives a data rate of around *6632 bit∙s⁻¹* for the same data rate, but requires a range coder. Huffman is much simpler, although slightly less efficient. Here is the Huffman mapping, with bit encodings:
```
 _
| |_|               220μs, 25.00%, '00' (110μs per bit)
 __
|  |__|             330μs, 25.00%, '01' (165μs per bit)
 ___
|   |___|           440μs, 12.50%, '100' (147μs per bit)
 ____
|    |____|         550μs, 12.50%, '101' (183μs per bit)
 _____
|     |_____|       660μs,  6.25%, '1100' (165μs per bit)
 ______
|      |______|     770μs,  6.25%, '1101' (193μs per bit)
 _______
|       |_______|   880μs,  6.25%, '1110' (220μs per bit)
 ________
|        |________| 990μs,  6.25%, '1111' (248μs per bit)

```
This gives a predicted rate of around *6562 bit∙s⁻¹*, a small sacrifice for the code complexity reduction. This is 4.2 times the speed of the Spectrum default loader.
That is the theory, but practical tests will be conducted when the code is functionally complete. Experiments are ongoing…

## Prerequisites
Requires [Make](http://www.gnu.org/software/make/), [Python](http://www.python.org) and [Pasmo](http://pasmo.speccy.org) to build. [Fuse](http://fuse-emulator.sourceforge.net) and Fuse utils (tzxlist) are also used for debugging.
