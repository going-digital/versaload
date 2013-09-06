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
infoblock.add_info(AINFO_TITLE,"Versaload test 2")
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

def addScreen(screenData,datamod):
    addPayload(0x5800, screenData[0x1800:0x1b00],datamod)
    for y in range(0,0x800,0x100):
        for base in range(0x0000,0x1800,0x800):
            addPayload(0x4000+base+y, screenData[base+y:0x100+base+y],datamod)

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
with open("print.asmgl") as labels:
    for line in labels:
        (label,dummy,value) = line.split()
        labelList[label]=int(value[1:-1],16)

execAddr = labelList['PAYLOAD_JUMP']
borderFlashAddr = labelList['BORDER_FLASH']
borderMainAddr = labelList['BORDER_MAIN']
printRoutine = labelList['PRINT_ROUTINE']
printParam = labelList['PRINT_PARAM']

def hexDump(str):
    print(":".join("{:02x}".format(ord(c)) for c in str))
def addExec(addr):
    # Jump to location, exiting loader
    addPayload(execAddr,pack("<BH",0xc3,addr), datamod)
def addCall(addr):
    # Call subroutine at location
    addPayload(execAddr,pack("<BH",0xcd,addr), datamod)
def borderFlash(colour):
    # Change colour of border flash
    addPayload(borderFlashAddr,pack("<B",0x8+colour), datamod)
def borderMain(colour):
    # Change main border colour
    addPayload(borderMainAddr,pack("<B",0x8+colour), datamod)
def printText(x,y,text):
    # Print message to screen.
    # Restricted to character square positions, and char codes 32-127
    # Simple routine that does not support wrapping, colour or control codes
    payload = pack("<2H",0x3d00,0x4000+(y//8)*0x800+(y%8)*0x20+x)
    payload = payload + text
    payload = payload + pack("<B",0)
    addPayload(printParam,payload,datamod)
    addCall(printRoutine)
    datamod.append(BitArray('0b10')*len(text))
def genFixup(src,dest,length,sp,pc):
    # Relocate memory block and execute payload
    # Z80 version
    """
        01 nn nn    ld      bc,length
        11 nn nn    ld      de,dest
        21 nn nn    ld      hl,src
        ed b0       ldir
        31 nn nn    ld      sp,spValFinal

        c3 nn nn    jp      pc
    """
    data = pack("<BHBHBH3BH2BH",\
        0x01,length,\
        0x11,dest,\
        0x21,src,\
        0xed,0xb0,\
        0x31,sp,\
        0xfb,\
        0xc3,pc\
        )
    return data

# Screen loading
screenData = open("test2.scr","rb").read()

# Maximise PAPER, minimise INK. This makes initial attributes more closely
# approximate final loading screen, and maximises 0 bits in screen bitmap
# which speeds loading (0 bits are always faster than 1 bits)
screenData = optimiseScr(screenData)

# Change border colour / effect to match loading screen
borderMain(7)   # Blue border
borderFlash(2)  # White flash

addScreen(screenData,datamod)

# Load up print Versaload add-on so we can print strings to screen during the load
addPayload(printRoutine,open("print.bin","rb").read(),datamod)

# Main code
mainData = open("test2.raw","rb").read()

# Load 0x5c00-0xbbff into final location
addPayload(0x5dc0, mainData[0x0000:0x5e40], datamod)
if len(mainData) > 0x5e40:
    addPayload(0xfc00, mainData[0x5e40:0x6240], datamod)
if len(mainData) > 0x6240:
    addPayload(0xc000, mainData[0x6240:], datamod)
addPayload(0x5b00, genFixup(0xfc00,0xbc00,0x400,0x5dc0,0x5dc0), datamod)
addExec(0x5b00)

# printText(0,23," Hello World of Spectrum fans!  ")
# printText(0,23,"                                ")
# printText(0,23,"  This is a demo of Versaload   ")
# printText(0,23," which can change border colour ")
# borderMain(1)   # Blue border
# borderMain(2)   # Red border
# borderMain(3)   # Magenta border
# borderMain(4)   # Green border
# borderMain(5)   # Cyan border
# borderMain(6)   # Yellow border
# borderMain(7)   # White border
# borderMain(6)   # Yellow border
# borderMain(5)   # Cyan border
# borderMain(4)   # Green border
# borderMain(3)   # Magenta border
# borderMain(2)   # Red border
# borderMain(1)   # Blue border
# printText(0,23," or print text whilst loading.  ")
# printText(0,23,"                                ")
# printText(0,23," But first, here's Penetrator!  ")
# # Patch out wait for keypress at 0x800c
# addPayload(0x800c, pack("<2B",0,0), datamod)

# Load relocate/execute code at 0x7000
# This relocates the 0x7c00-0x7fff code block back to the correct place
# and then jumps to the game entry point at 0x8000
# Memory map whilst loading:
#   0x4000-0x5AFF   Loading screen
#   0x5B00-0x5B80   ZX7 decompressor
#   0x6000-0xDFFF   Compressed image (may be less)
# Memory map after loading complete, before executing fixup/decompressor
#   0x4000-0x5AFF   Loading screen
#   0x5B80-0x5C00   Fixup code

#   0x8000-0xFFFF   Decompressed image
#
# addPayload(0x7000, genFixup(0x7c00,0xbc00,0x400,0x5fff,0x8000), datamod)

# Execute relocate code, then game
# addExec(0x7000)


# Add final tape state (so last symbol can be decoded)
datamod.append('0b1')

payloadblock = Blk_DRB(sampledata = datamod.tobytes())
payloadblock.tstatespersample(110*3.5)
payloadblock.pause(0)

tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('versaload2.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()
