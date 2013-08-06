PASMO=./pasmo
TZXLIST=./tzxlist
PYTHON=python
FUSE=/Applications/Fuse.app/Contents/MacOS/Fuse

%.bin: %.asm
	$(PASMO) --bin $< $@ gl

boot1.bin: boot2.bin

#test.tzx: boot1.bin
#    $(PYTHON) buildtzx.py
#    $(TZXLIST) test.tzx

#fuse: versaload.tzx
#    $(FUSE) --machine plus2 --no-detect-loader --tape versaload.tzx

all: boot1.bin

clean:
	rm -f *.bin
	rm -f *.tzx
