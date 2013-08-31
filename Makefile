PYTHON=python
FUSE=/Applications/Fuse.app/Contents/MacOS/Fuse
PASMO=./pasmo
TZXLIST=./tzxlist
TAPE2WAV=./tape2wav
EXOMIZER=./exomizer
TAPECONV=./tapeconv

%.bin: %.asm
	$(PASMO) --bin $< $@ $<gl
%.wav: %.tzx
	$(TAPE2WAV) -r 96000 $< $@
%.exo: %
	$(EXOMIZER) raw -c $< -o $@

boot1.bin: boot2.bin Makefile

versaload.tzx: boot1.bin test.scr buildtzx.py Makefile
	# Construct loader
	$(PYTHON) buildtzx.py
	# Add loading screen metadata to TZX
	$(TAPECONV) -s test.scr versaload.tzx versaload.tzx
	# Report loading time
	$(TZXLIST) versaload.tzx

fuse: versaload.tzx Makefile
	$(FUSE) --machine plus2 --no-detect-loader --tape versaload.tzx

all: versaload.wav

clean:
	rm -f *.bin
	rm -f *.tzx
	rm -f *.wav
