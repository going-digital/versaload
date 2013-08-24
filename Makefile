PYTHON=python
FUSE=/Applications/Fuse.app/Contents/MacOS/Fuse
PASMO=./pasmo
TZXLIST=./tzxlist
TAPE2WAV=./tape2wav
EXOMIZER=./exomizer

%.bin: %.asm
	$(PASMO) --bin $< $@ gl
%.wav: %.tzx
	$(TAPE2WAV) -r 96000 $< $@
%.exo: %
	$(EXOMIZER) raw -c $< -o $@

boot1.bin: boot2.bin

versaload.tzx: boot1.bin test.scr buildtzx.py
	$(PYTHON) buildtzx.py
	$(TZXLIST) versaload.tzx # Reports duration of loading

fuse: versaload.tzx
	$(FUSE) --machine plus2 --no-detect-loader --tape versaload.tzx

all: versaload.wav

clean:
	rm -f *.bin
	rm -f *.tzx
	rm -f *.wav
