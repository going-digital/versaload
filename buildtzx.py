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
loaderblock1.bitpulse0(650)
loaderblock1.bitpulse1(1710)
loaderblock2 = Blk_TSDB(data=loaderdata.get())
loaderblock2.bitpulse0(650)
loaderblock2.bitpulse1(1710)
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
