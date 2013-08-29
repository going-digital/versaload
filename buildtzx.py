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
import bitstring
from bitstring import BitArray

tape = TZX()

timeMargin = 1.2

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

#loaderblock1.bitpulse0(bitpulse0_ROM_min*timeMargin)
#loaderblock1.bitpulse1(bitpulse1_ROM_min*timeMargin)
#loaderblock1.pilotpulse(pilotpulse_ROM_min*timeMargin)
loaderblock1.pilottone(pilottone_header_ROM_min*timeMargin)
loaderblock1.pause(0)
tape.add_block(loaderblock1)

loaderblock2 = Blk_TSDB(data=loaderdata.get())
#loaderblock2.bitpulse0(bitpulse0_ROM_min*timeMargin)
#loaderblock2.bitpulse1(bitpulse1_ROM_min*timeMargin)
#loaderblock2.pilotpulse(pilotpulse_ROM_min*timeMargin)
loaderblock2.pilottone(pilottone_data_ROM_min*timeMargin)
loaderblock2.pause(0)
tape.add_block(loaderblock2)

"""
Payload setup
"""
# Sync pattern to synchronise loader with stream
# Starts at 5.42110s into audio
versaHeader = BitArray('10*0xcc,2*0xf0c,4*0xc3c,2*0xf0c')

# Calibration - correct for speed of tape playback
# 4 cycles of 880us
versaHeader.append(BitArray('4*0xff00'))

blockNumber = 0x0000

"""
Payload blocks
"""
datamod = BitArray()

def addPayload(loadAddress, rawdata, datamod):
    # Build payload block
    # See https://github.com/going-digital/versaload/wiki/Payload
    #
    endAddress = loadAddress + len(rawdata)
    checkSum = 0x0000
    data = bitstring.pack('<4H',blockNumber,loadAddress,endAddress,checkSum)
    data.append(BitArray(bytes=rawdata))
    #data = BitArray(bytes=rawdata)

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

    datamod.append(versaHeader)

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
                else: # data[0:4] must be '0b1111'
                    datamod.append(symbol1111)
                    data=data[4:]

# Interlaced screen loading
screenData = open("test.scr","rb").read()
addPayload(0x5800, screenData[0x1800:0x1c00], datamod) # Attributes
addPayload(0x4000, screenData[0x0000:0x0100], datamod) # Row 0
addPayload(0x4800, screenData[0x0800:0x0900], datamod)
addPayload(0x5000, screenData[0x1000:0x1100], datamod)
addPayload(0x4400, screenData[0x0400:0x0500], datamod) # Row 4
addPayload(0x4c00, screenData[0x0c00:0x0d00], datamod)
addPayload(0x5400, screenData[0x1400:0x1500], datamod)
addPayload(0x4200, screenData[0x0200:0x0300], datamod) # Row 2
addPayload(0x4a00, screenData[0x0a00:0x0b00], datamod)
addPayload(0x5200, screenData[0x1200:0x1300], datamod)
addPayload(0x4600, screenData[0x0600:0x0700], datamod) # Row 6
addPayload(0x4e00, screenData[0x0e00:0x0f00], datamod)
addPayload(0x5600, screenData[0x1600:0x1700], datamod)
addPayload(0x4100, screenData[0x0100:0x0200], datamod) # Row 1
addPayload(0x4900, screenData[0x0900:0x0a00], datamod)
addPayload(0x5100, screenData[0x1100:0x1200], datamod)
addPayload(0x4500, screenData[0x0500:0x0600], datamod) # Row 5
addPayload(0x4d00, screenData[0x0d00:0x0e00], datamod)
addPayload(0x5500, screenData[0x1500:0x1600], datamod)
addPayload(0x4300, screenData[0x0300:0x0400], datamod) # Row 3
addPayload(0x4b00, screenData[0x0b00:0x0c00], datamod)
addPayload(0x5300, screenData[0x1300:0x1400], datamod)
addPayload(0x4700, screenData[0x0700:0x0800], datamod) # Row 7
addPayload(0x4f00, screenData[0x0f00:0x1000], datamod)
addPayload(0x5700, screenData[0x1700:0x1800], datamod)

# Add final tape state (so last symbol can be decoded)
datamod.append('0b1')

payloadblock = Blk_DRB(sampledata = datamod.tobytes())
payloadblock.tstatespersample(110*3.5)

tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('versaload.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()
