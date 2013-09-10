PYTHON=python
FUSE=/Applications/Fuse.app/Contents/MacOS/Fuse
PASMO=./pasmo
TZXLIST=./tzxlist
TAPE2WAV=./tape2wav
EXORAW=./exomizer207/src/exoraw
TAPECONV=./tapeconv
CC=clang
ZX7=./zx7compress

all: versaload.tzx versaload.wav

%.bin: %.asm
	$(PASMO) --bin $< $@ $<gl
%.asmgl: %.asm
	$(PASMO) --bin $< $@ $<gl
%.wav: %.tzx
	$(TAPE2WAV) -r 96000 $< $@

# Exomizer rules - see http://www.amstrad.es/forum/viewtopic.php?f=6&p=43320
#
%.exo: %
	# For use with deexo.asm
	$(EXORAW) $< -o $@
%.exo_simple: %
	# For use with deexo_simple.asm
	$(EXORAW) $< -c -o $@
%.exo_b: %
	# For use with deexo_b.asm
	$(EXORAW) $< -b -o $@
%.exo_simple_b: %
	# For use with deexo_simple_b.asm
	$(EXORAW) $< -b -c -o $@

# ZX7 rules
%.zx7: % zx7compress
	$(ZX7) $< $@

setbaud.asm: setbaud.py
	# Autogenerate setbaud.asm
	$(PYTHON) setbaud.py

boot2.bin: setbaud.bin

boot1.bin: boot2.bin

test_packed.bin: test.raw.exo_b
test2_packed.bin: test2.raw.exo_b

test.tzx: boot1.bin test.scr buildtzx.py print.bin genfont.bin test_packed.bin
	# Construct loader
	$(PYTHON) buildtzx.py
	# Add loading screen metadata to TZX
	$(TAPECONV) -s test.scr test.tzx test.tzx
	# Report loading time
	$(TZXLIST) test.tzx

test2.tzx: boot1.bin test2.scr buildtzx.py print.bin test2_packed.bin
	# Construct loader
	$(PYTHON) test2.py
	# Add loading screen metadata to TZX
	$(TAPECONV) -s test2.scr test2.tzx test2.tzx
	# Report loading time
	$(TZXLIST) test2.tzx

fuse: test.tzx
	$(FUSE) --machine plus2 --no-detect-loader --tape test.tzx

fuse2: test2.tzx
	$(FUSE) --machine plus2 --no-detect-loader --tape test2.tzx

zx7compress: zx7/src/compress.c zx7/src/optimize.c zx7/src/zx7.c
	$(CC) zx7/src/compress.c zx7/src/optimize.c zx7/src/zx7.c -o zx7compress

clean:
	rm -f *.bin *.tzx *.wav *.asmgl *.exo *.exo_b *.exo_simple *.exo_simple_b *.zx7
	rm -f setbaud.asm
