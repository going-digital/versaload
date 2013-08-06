PASMO=./pasmo
TZXLIST=./tzxlist
PYTHON=python
FUSE=/Applications/Fuse.app/Contents/MacOS/Fuse

%.bin: %.asm
	$(PASMO) --bin $< $@ gl

boot1.bin: boot2.bin

versaload.tzx: boot1.bin
	$(PYTHON) buildtzx.py
#    $(TZXLIST) test.tzx

fuse: versaload.tzx
	$(FUSE) --machine plus2 --no-detect-loader --tape versaload.tzx

all: versaload.tzx

clean:
	rm -f *.bin
	rm -f *.tzx
