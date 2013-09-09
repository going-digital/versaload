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
from versaload import *
from screenutil import *

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
tape.add_block(loaderblock1)
loaderblock2 = Blk_SSDB(data=loaderdata.get())
loaderblock2.pause(0)
tape.add_block(loaderblock2)


"""
Extract key addresses from Pasmo output

Some loader features make live code modifications to the loading routine.
Here we extract those addresses from the Pasmo output to use later.
"""
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
borderFlashAddr = labelList['BORDER_FLASH']
borderMainAddr = labelList['BORDER_MAIN']
borderErrorFlashAddr = labelList['BORDER_ERROR_FLASH']
borderErrorMainAddr = labelList['BORDER_ERROR_MAIN']
printRoutine = labelList['PRINT_ROUTINE']
printParam = labelList['PRINT_PARAM']

"""
Payload
"""
payload = Versaload(baud=3000)

"""
Border functions

These alter the code of the loader to change the border colour effects during
loading.
"""
def borderFlash(colour):
    # Change colour of loading border flash
    payload.load(borderFlashAddr,pack("<B",0x8+colour))
def borderMain(colour):
    # Change main loading border colour
    payload.load(borderMainAddr,pack("<B",0x8+colour))
def borderErrorFlash(colour):
    # Change colour of error state border flash
    payload.load(borderErrorFlashAddr,pack("<B",0x8+colour))
def borderErrorMain(colour):
    # Change main border colour in error state
    payload.load(borderErrorMainAddr,pack("<B",0x8+colour))

"""
Print functions

This allows printing to the screen using ROM or custom character sets.
Print functions will not work until print function has been loaded on Spectrum
side.
"""
def printText(x,y,text):
    # Print message to screen.
    # Restricted to character square positions, and char codes 32-127
    # Simple routine that does not support wrapping, colour or control codes
    data = pack("<2H",0x3d00,0x4000+(y//8)*0x800+(y%8)*0x20+x)
    data = data + text
    data = data + pack("<B",0)
    payload.load(printParam,data)
    payload.execute(printRoutine,0.01*len(text))

def printColourText(x,y,text,ink,paper,bright=False,flash=False):
    # Print message to screen, with attributes
    attrData = ink + 8*paper
    if bright:
        attrData = attrData + 0x40
    if flash:
        attrData = attrData + 0x80
    attrAddr = 0x5800 + y*32 + x
    payload.load(attrAddr,pack("<B",attrData)*len(text))
    printText(x,y,text)

"""
Screen loader

Fancy screen loading. Loads attributes first, then uses interlace loading.
"""
def addScreen(screenData):
    # Load attributes first
    payload.load(0x5800, screenData[0x1800:0x1b00])
    # Load 1/8 of screen per scan over 8 scans
    for y in [0,4,2,6,1,5,3,7]:
        y2=y*0x100
        for base in range(0x0000,0x1800,0x800):
            payload.load(0x4000+base+y2, screenData[base+y2:0x100+base+y2])


"""
Debug: print string as hexadecimal
"""
def hexDump(str):
    print(":".join("{:02x}".format(ord(c)) for c in str))

"""
Fixup

Generate short machine code to relocate data, set SP and execute.
Used at the final stage of loading to overwrite the versaload routine and
correct the memory map, then execute the final payload.
"""
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
    data = pack("<BHBHBH3BHBH",\
        0x01,length,\
        0x11,dest,\
        0x21,src,\
        0xed,0xb0,\
        0x31,sp,\
        0xc3,pc\
        )
    return data

"""
Construct payload
"""
payload.delay(0.5)  # Wait for BASIC to execute. Let tape AGC settle.

borderMain(1)   # Blue border
borderFlash(0)  # Black flash
borderErrorMain(2)   # Red border
borderErrorFlash(0)  # Magenta flash


# Loading screen
addScreen(optimiseScr(open("test.scr","rb").read()))

# Change border colour / effect to match loading screen

# Load print routine
payload.load(printRoutine,open("print.bin","rb").read())
printColourText(12,11,"Loading",7,2,bright=True)

# Main code
payloadBlock = open("test_packed.bin","rb").read()
payload.load(0x5c00,payloadBlock[0:0x400])
printText(1,23,"Hello World of Spectrum fans!")
payload.load(0x6000,payloadBlock[0x400:0x800])
printText(1,23,"                             ")
payload.load(0x6400,payloadBlock[0x800:0xc00])
printText(1,23," This is a demo of Versaload ")
payload.load(0x6800,payloadBlock[0xc00:0x1000])
printText(1,23,"which can change border colour")
payload.load(0x6c00,payloadBlock[0x1000:0x1400])
printText(1,23,"or print text whilst loading. ")
payload.load(0x7000,payloadBlock[0x1400:0x1800])
printText(1,23,"                             ")
payload.load(0x7400,payloadBlock[0x1800:0x1c00])
printText(7,23,"Check progress at")
payload.load(0x7800,payloadBlock[0x1c00:0x2000])
printText(4,23,"github.com/going-digital")
payload.load(0x7c00,payloadBlock[0x2000:0x2400])
printText(0,23,"or the World of Spectrum forums")
payload.load(0x8000,payloadBlock[0x2400:0x2800])
printText(0,23,"                               ")
payload.load(0x8400,payloadBlock[0x2800:0x2c00])
printText(3,23,"This loader uses Exomizer   ")
payload.load(0x8800,payloadBlock[0x2c00:0x3000])
printText(0,23,"which saves lots of loading time")
payload.load(0x8c00,payloadBlock[0x3000:0x3400])
printText(0,23,"                                ")
payload.load(0x9000,payloadBlock[0x3400:0x3800])
printText(1,23,"But anyway, here's Penetrator!")
payload.load(0x9400,payloadBlock[0x3800:])

# # Complete load
payload.load(0x5b00, genFixup(0x7c00,0xfc00,0x400,0x5c00,0x5c00))
printColourText(11,11,"Unpacking",7,2,bright=True)
payload.execute(0x5b00,0)

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

payloadblock = Blk_DRB(sampledata = payload.get().tobytes())
payloadblock.tstatespersample(payload.tStatesPerSample())
payloadblock.pause(0)
tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('test.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()
