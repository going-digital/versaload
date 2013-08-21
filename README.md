Versaload
=========

## Faster data encoding from cassette for retro platforms
Versaload uses the accumulated tricks from reliable fast tape loaders of the past, adding modern techniques and a modern mastering system to achieve much improved loading times on retro machines using original tape equipment. To achieve this new speed, it uses several innovations:

  * Uses tape signal timing based on three known good loaders - the Sinclair ZX Spectrum ROM (1982), [Turbo Tape 64](http://codebase64.org/doku.php?id=base:turbotape_loader_source) (1983) and the [Microsphere loader](http://www.worldofspectrum.org/infoseekpub.cgi?regexp=^Microsphere$ ) (1984).
  * Automatic calibration to tape playback speed
  * Uses 8 symbols instead of 2, to improve data density.
  * [Huffman coding](http://en.wikipedia.org/wiki/Huffman_coding) is used to optimise the data rate across different symbol lengths.
  * Very fast synchronisation
  * Python based scriptable tape mastering environment, compatible with standard emulator file formats and audio output.

This gives a predicted rate of around *6562 bit∙s⁻¹*, 4.2 times the speed of the Spectrum default loader.

More information on this is [in the wiki.](https://github.com/going-digital/versaload/wiki)

## Prerequisites
  * [Make](http://www.gnu.org/software/make/)
  * [Python](http://www.python.org)
  * [Pasmo](http://pasmo.speccy.org)
  * [Fuse](http://fuse-emulator.sourceforge.net)
  * Fuse-utils (tzxlist, tap2wav)
  * [Python Bitstring](http://code.google.com/p/python-bitstring/)
This code incorporates Ian Chapman's Python TZX library.
