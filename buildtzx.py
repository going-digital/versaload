# Prerequisite:
#
# bitstring
#   sudo pip install bitstring OR sudo easy_install bitstring
#
#import os
import sys
sys.path.append("modules")
from tzx import *
from zxfile import *
from bitstring import BitArray

tape = TZX()

timeMargin = 1.1

"""
File metadata
"""
infoblock = Blk_AIB()
infoblock.add_info(AINFO_TITLE,"Versaload test")
infoblock.add_info(AINFO_AUTHOR,"Peter Knight (going-digital)")
infoblock.add_info(AINFO_PUBYEAR,"2013")
infoblock.add_info(AINFO_PROTECTION,"Versaload")
infoblock.add_info(AINFO_COMMENT,"http://github.com/going-digital/versaload")
#infoblock.add_info(AINFO_PUBLISHER,"")
#infoblock.add_info(AINFO_LANG,"")
#infoblock.add_info(AINFO_TYPE,"")
#infoblock.add_info(AINFO_PRICE,"")
#infoblock.add_info(AINFO_ORIGIN,"")
tape.add_block(infoblock)

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

# These are absolute minimums for the Spectrum ROM.
#
bitpulse0_ROM_min = 506
bitpulse1_ROM_min = 1314
pilotpulse_ROM_min = 1772
pilottone_header_ROM_min = 4024
pilottone_data_ROM_min = 2331

loaderblock1.bitpulse0(bitpulse0_ROM_min*timeMargin)
loaderblock1.bitpulse1(bitpulse1_ROM_min*timeMargin)
loaderblock1.pilotpulse(pilotpulse_ROM_min*timeMargin)
loaderblock1.pilottone(pilottone_header_ROM_min*timeMargin)
loaderblock1.pause(0)
tape.add_block(loaderblock1)

loaderblock2 = Blk_TSDB(data=loaderdata.get())
loaderblock2.bitpulse0(bitpulse0_ROM_min*timeMargin)
loaderblock2.bitpulse1(bitpulse1_ROM_min*timeMargin)
loaderblock2.pilotpulse(pilotpulse_ROM_min*timeMargin)
loaderblock2.pilottone(pilottone_data_ROM_min*timeMargin)
loaderblock2.pause(10)
tape.add_block(loaderblock2)

"""
Payloads
"""

# Sync pattern to synchronise loader with stream
versaHeader = BitArray('2*0xccf0f0,4*0xf0ccf0,2*0xccf0f0')
# Calibration - correct for speed of tape playback
# 4 cycles of 880us
versaHeader.append(BitArray('4*0xff00'))

# Generate bitstream
rawdata = open("test.scr","rb").read()

# Load address
loadAddress = 0x8000
data = BitArray(uintle=loadAddress, length=16)
# End address
endAddress = loadAddress + len(rawdata)
data.append(BitArray(uintle=endAddress, length=16))
# Data
data.append(BitArray(bytes=rawdata))

# Modulate datastream
#
# Encodes bits with the Versaload 8 symbol method
# Some padding may be necessary to encode the bit sequence. '0' is always used,
# as this produces the shortest output.

symbol00    = BitArray('2*0b1,2*0b0')
symbol01    = BitArray('3*0b1,3*0b0')
symbol100   = BitArray('4*0b1,4*0b0')
symbol101   = BitArray('5*0b1,5*0b0')
symbol1100  = BitArray('6*0b1,6*0b0')
symbol1101  = BitArray('7*0b1,7*0b0')
symbol1110  = BitArray('8*0b1,8*0b0')
symbol1111  = BitArray('9*0b1,9*0b0')

datamod = versaHeader

while data.length > 0:
    # 2 bit sequences
    if data.length < 2:
        data.append('0b0')
    if data[0:2]=='0b00':
        datamod.append(symbol00)
        data=data[2:]
    elif data[0:2]=='0b01':
        datamod.append(symbol01)
        data=data[2:]
    else:
        # 3 bit sequences
        if data.length < 3:
            data.append('0b0')
        if data[0:3]=='0b100':
            datamod.append(symbol100)
            data=data[3:]
        elif data[0:3]=='0b101':
            datamod.append(symbol101)
            data=data[3:]
        else:
            # 4 bit sequences
            if data.length < 4:
                data.append('0b0')
            if data[0:4]=='0b1100':
                datamod.append(symbol1100)
                data=data[4:]
            elif data[0:4]=='0b1101':
                datamod.append(symbol1101)
                data=data[4:]
            elif data[0:4]=='0b1110':
                datamod.append(symbol1110)
                data=data[4:]
            else:
                datamod.append(symbol1111)
                data=data[4:]

payloadblock = Blk_DRB(sampledata = datamod.tobytes())
payloadblock.tstatespersample(110)

tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('versaload.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()
