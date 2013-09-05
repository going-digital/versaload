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
loaderheader = ZX_FileHdr(SPEC_FILE_PROG, '\x16\x0b\x0cLoading', 0, 1, 0)
loaderdata = ZX_FileData(loaderprog)
loaderheader.setdatalen(loaderdata.datalen())
loaderblock1 = Blk_SSDB(data=loaderheader.get())
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

#loaderblock1.pilottone(pilottone_header_ROM_min*timeMargin)
#loaderblock1.pause(0)
tape.add_block(loaderblock1)

loaderblock2 = Blk_SSDB(data=loaderdata.get())
#loaderblock2.pilottone(pilottone_data_ROM_min*timeMargin)
loaderblock2.pause(0)
tape.add_block(loaderblock2)

"""
Payload setup
"""
# Sync pattern to synchronise loader with stream
# Starts at 5.42110s into audio
versaHeader = BitArray('1*0b11110000')
versaHeader.append(BitArray('0b11110000101011110000'))
versaHeader.append(BitArray('0b10111100001111000010'))
versaHeader.append(BitArray('0b10101010111100001111'))
versaHeader.append(BitArray('0b00001111000011110000'))

# Calibration - correct for speed of tape playback
# 4 cycles of 880us
versaHeader.append(BitArray('4*0b11110000'))

symbol00 = BitArray('1*0b1,1*0b0')
symbol01 = BitArray('2*0b1,2*0b0')
symbol10 = BitArray('3*0b1,3*0b0')
symbol11 = BitArray('4*0b1,4*0b0')

blockNumber = 0x0000

"""
Payload blocks
"""
datamod = BitArray()

def addPayload(loadAddress, rawdata, datamod):
    if len(rawdata) > 0x100:
        # Divide into 0x100 long blocks
        addPayload(loadAddress, rawdata[0:0x100], datamod)
        addPayload(loadAddress+0x100, rawdata[0x100:], datamod)
    else:
        print "Payload",hex(loadAddress)
        # Build payload block
        # See https://github.com/going-digital/versaload/wiki/Payload
        #
        endAddress = (loadAddress + len(rawdata)) & 0xffff
        checkSum = 0x0000
        data = bitstring.pack('<4H',blockNumber,loadAddress,endAddress,checkSum)
        data.append(BitArray(bytes=rawdata))
        #data = BitArray(bytes=rawdata)

        # Modulate datastream
        #
        # Encodes bits with the Versaload 4 symbol method
        # Some padding may be necessary to encode the bit sequence. '0' is always used,
        # as this produces the shortest output.

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
            elif data[0:2]=='0b10':
                datamod.append(symbol10)
                data=data[2:]
            else: # data[0:2] must be '0b1111'
                datamod.append(symbol11)
                data=data[2:]
    return

def optimiseScr(data):
    # Flips INK/PAPER to maximise the amount of paper
    # This makes the interlace-loaded screen look more accurate earlier.
    dataBits = BitArray(bytes=data)
    for block in range(0,3):
        addrAttr = 0x1800 + 0x100 * block
        addrPixel = 0x0800 * block
        for char in range(0,256):
            addrAttr2 = 8*(addrAttr + char)
            addrPixel2 = 8*(addrPixel + char)
            pixelData = dataBits[addrPixel2:addrPixel2+8]
            pixelData.append(dataBits[addrPixel2+0x0800:addrPixel2+0x0808])
            pixelData.append(dataBits[addrPixel2+0x1000:addrPixel2+0x1008])
            pixelData.append(dataBits[addrPixel2+0x1800:addrPixel2+0x1808])
            pixelData.append(dataBits[addrPixel2+0x2000:addrPixel2+0x2008])
            pixelData.append(dataBits[addrPixel2+0x2800:addrPixel2+0x2808])
            pixelData.append(dataBits[addrPixel2+0x3000:addrPixel2+0x3008])
            pixelData.append(dataBits[addrPixel2+0x3800:addrPixel2+0x3808])
            if pixelData.count(1) > 32:
                # More INK than PAPER in this square

                # Flip pixels
                pixelData = ~pixelData
                dataBits[addrPixel2:addrPixel2+8]=pixelData[0:8]
                dataBits[addrPixel2+0x0800:addrPixel2+0x0808]=pixelData[8:16]
                dataBits[addrPixel2+0x1000:addrPixel2+0x1008]=pixelData[16:24]
                dataBits[addrPixel2+0x1800:addrPixel2+0x1808]=pixelData[24:32]
                dataBits[addrPixel2+0x2000:addrPixel2+0x2008]=pixelData[32:40]
                dataBits[addrPixel2+0x2800:addrPixel2+0x2808]=pixelData[40:48]
                dataBits[addrPixel2+0x3000:addrPixel2+0x3008]=pixelData[48:56]
                dataBits[addrPixel2+0x3800:addrPixel2+0x3808]=pixelData[56:64]

                # Flip attributes
                attribute = dataBits[addrAttr2:addrAttr2+8]
                dataBits[addrAttr2:addrAttr2+8]=[
                    attribute[0],attribute[1],
                    attribute[5],attribute[6],attribute[7],
                    attribute[2],attribute[3],attribute[4]
                    ]
    data = dataBits.tobytes()
    return data


datamod.append(BitArray('2000*0b1100'))
# Wait for BASIC to execute
#datamod.append(BitArray('40*0b10'))

# Wait for loader to clear screen
#datamod.append(BitArray('480*0b10'))

# Extract important addresses from Pasmo output
labelList = {}
with open("boot2.asmgl") as labels:
    for line in labels:
        (label,dummy,value) = line.split()
        labelList[label]=int(value[1:-1],16)

execAddr = labelList['PAYLOAD_JUMP']
borderFlashAddr = labelList['BORDER_FLASH']
borderMainAddr = labelList['BORDER_MAIN']

def addExec(addr):
    addPayload(execAddr,pack("<BH",0xc3,addr), datamod)
def addCall(addr):
    addPayload(execAddr,pack("<BH",0xcd,addr), datamod)
def borderFlash(colour):
    addPayload(borderFlashAddr,pack("<B",0x8+colour), datamod)
def borderMain(colour):
    addPayload(borderMainAddr,pack("<B",0x8+colour), datamod)

# Screen loading
screenData = open("test.scr","rb").read()

# Maximise PAPER, minimise INK. This makes initial attributes more closely
# approximate final loading screen, and maximises 0 bits in screen bitmap
# which speeds loading (0 bits are always faster than 1 bits)
screenData = optimiseScr(screenData)

# Load attributes
addPayload(0x5800, screenData[0x1800:0x1c00], datamod)

# Change border colour / effect to match loading screen
borderMain(1)   # Blue border
borderFlash(7)  # White flash

# Load every 4th row
addPayload(0x4000, screenData[0x0000:0x0100], datamod) # Row 0
addPayload(0x4800, screenData[0x0800:0x0900], datamod)
addPayload(0x5000, screenData[0x1000:0x1100], datamod)
addPayload(0x4100, screenData[0x0100:0x0200], datamod) # Row 1
addPayload(0x4900, screenData[0x0900:0x0a00], datamod)
addPayload(0x5100, screenData[0x1100:0x1200], datamod)
addPayload(0x4200, screenData[0x0200:0x0300], datamod) # Row 2
addPayload(0x4a00, screenData[0x0a00:0x0b00], datamod)
addPayload(0x5200, screenData[0x1200:0x1300], datamod)
addPayload(0x4300, screenData[0x0300:0x0400], datamod) # Row 3
addPayload(0x4b00, screenData[0x0b00:0x0c00], datamod)
addPayload(0x5300, screenData[0x1300:0x1400], datamod)
addPayload(0x4400, screenData[0x0400:0x0500], datamod) # Row 4
addPayload(0x4c00, screenData[0x0c00:0x0d00], datamod)
addPayload(0x5400, screenData[0x1400:0x1500], datamod)
addPayload(0x4500, screenData[0x0500:0x0600], datamod) # Row 5
addPayload(0x4d00, screenData[0x0d00:0x0e00], datamod)
addPayload(0x5500, screenData[0x1500:0x1600], datamod)
addPayload(0x4600, screenData[0x0600:0x0700], datamod) # Row 6
addPayload(0x4e00, screenData[0x0e00:0x0f00], datamod)
addPayload(0x5600, screenData[0x1600:0x1700], datamod)
addPayload(0x4700, screenData[0x0700:0x0800], datamod) # Row 7
addPayload(0x4f00, screenData[0x0f00:0x1000], datamod)
addPayload(0x5700, screenData[0x1700:0x1800], datamod)
borderFlash(0) # White flash

def genFixup(src,dest,length,spVal,pc):
    # Z80 version
    """
        01 nn nn    ld      bc,length
        11 nn nn    ld      de,dest
        21 nn nn    ld      hl,src
        31 nn nn    ld      sp,spVal
        ed b0       ldir
        c3 nn nn    jp      pc
    """
    data = pack("<BHBHBHBH3BH",0x01,length,0x11,dest,0x21,src,0x31,spVal,0xed,0xb0,0xc3,pc)
    #print ":".join("{:02x}".format(ord(c)) for c in data)
    return data

# Main code
mainData = open("test.raw","rb").read()

# Load 0x8000-0xbbff into final location
addPayload(0x8000, mainData[0x0000:0x3c00], datamod)

# Load 0xbc00-0xbfff block to 0x7c00 to avoid overwriting loader
addPayload(0x7c00, mainData[0x3c00:0x4000], datamod)

# Load 0xc000-0xffff into final location
addPayload(0xc000, mainData[0x4000:0x8000], datamod)

# Patch out wait for keypress at 0x800c
addPayload(0x800c, pack("<2B",0,0), datamod)

# Load relocate/execute code at 0x7000
addPayload(0x7000, genFixup(0x7c00,0xbc00,0x400,0x5fff,0x8000), datamod)

# Execute relocate code, then game
addExec(0x7000)


# Add final tape state (so last symbol can be decoded)
datamod.append('0b1')

payloadblock = Blk_DRB(sampledata = datamod.tobytes())
payloadblock.tstatespersample(110*3.5)
payloadblock.pause(0)

tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('versaload.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()
