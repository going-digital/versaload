PASMO=./pasmo
TZXLIST=./tzxlist
PYTHON=python
FUSE=/Applications/Fuse.app/Contents/MacOS/Fuse
TAPE2WAV=./tape2wav

%.bin: %.asm
	$(PASMO) --bin $< $@ gl
%.wav: %.tzx
	$(TAPE2WAV) $< $@

boot1.bin: boot2.bin

versaload.tzx: boot1.bin test.scr
	$(PYTHON) buildtzx.py
#    $(TZXLIST) test.tzx

fuse: versaload.tzx
	$(FUSE) --machine plus2 --no-detect-loader --tape versaload.tzx

all: versaload.tzx versaload.wav

clean:
	rm -f *.bin
	rm -f *.tzx
	rm -f *.wav
