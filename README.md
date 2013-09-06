Versaload
=========

## Faster data encoding from cassette for retro platforms
Versaload uses the accumulated tricks from reliable fast tape loaders of the past, adding modern techniques and a modern mastering system to achieve much improved loading times on retro machines using original tape equipment. To achieve this new speed, it uses several innovations:

  * Uses tape signal timing based on three known good loaders - the Sinclair ZX Spectrum ROM (1982), [Turbo Tape 64](http://codebase64.org/doku.php?id=base:turbotape_loader_source) (1983) and the [Microsphere loader](http://www.worldofspectrum.org/infoseekpub.cgi?regexp=^Microsphere$ ) (1984).
  * Automatic calibration to tape playback speed
  * Uses 4 symbols instead of 2, to improve data density.
  * Very fast synchronisation
  * Python based scriptable tape mastering environment, compatible with standard emulator file formats and audio output.

This gives a predicted rate of around *4500 bit∙s⁻¹*, 3 times the speed of the Spectrum default loader.

More information on this is [in the wiki.](https://github.com/going-digital/versaload/wiki)

## Prerequisites
  * [Make](http://www.gnu.org/software/make/)
  * [Python](http://www.python.org)
  * [Pasmo](http://pasmo.speccy.org)
  * [Fuse](http://fuse-emulator.sourceforge.net)
  * Fuse-utils (tzxlist, tap2wav)
  * [Python Bitstring](http://code.google.com/p/python-bitstring/)

## Credits
Uses Ian Chapman's [Python TZX library](http://software.amiga-hardware.com/pytzx.cgi).
Uses Einar Saukas's [ZX7 compression library](http://www.worldofspectrum.org/infoseekid.cgi?id=0027996).
Uses Magnus Lind's [Exomizer 2](http://hem.bredband.net/magli143/exo/) with Metalbrain's Z80 unpacker.

## Licenses
Files in the zx7 directory are provided under a BSD-3 license. See zx7.txt for details.
Files in the Exomizer207 directory are provided under a seperate license. See zx7.txt for details.
Files in the modules directory are provided under a GPL-2 license. See directory contents for details.

Other files are provided under the MIT license described below.

The MIT License (MIT)

Copyright (c) 2013 Peter Knight aka GoingDigital

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
