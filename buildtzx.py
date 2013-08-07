import os
import sys
sys.path.append("modules")
from tzx import *
from zxfile import *

tape = TZX()

"""
Loader
"""
loaderprog = open("boot1.bin","rb").read()
loaderheader = ZX_FileHdr(SPEC_FILE_PROG, 'Versaload', 0, 1, 0)
loaderdata = ZX_FileData(loaderprog)
loaderheader.setdatalen(loaderdata.datalen())
loaderblock1 = Blk_TSDB(data=loaderheader.get())
#
# Set to absolute fastest settings then back off by 10%
# This achieves 2176 baud instead of 1535 baud with the stock ROM loader.
#
loaderblock1.bitpulse0(557)   # Works 506
loaderblock1.bitpulse1(1445)  # Works 1314
loaderblock1.pilotpulse(1949) # Works 1772
loaderblock1.pilottone(4426)  # Works 4024
loaderblock1.pause(0)         # Works 0
loaderblock2 = Blk_TSDB(data=loaderdata.get())
loaderblock2.bitpulse0(557)
loaderblock2.bitpulse1(1445)
loaderblock2.pilotpulse(1949)
loaderblock2.pilottone(2564)  # Works 2331
loaderblock2.pause(10)

"""
Compile tape
"""
tape.add_block(loaderblock1)
tape.add_block(loaderblock2)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('versaload.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()
