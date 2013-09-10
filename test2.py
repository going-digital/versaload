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
with open("setbaud.asmgl") as labels:
    for line in labels:
        (label,dummy,value) = line.split()
        labelList[label]=int(value[1:-1],16)
borderFlashAddr = labelList['BORDER_FLASH']
borderMainAddr = labelList['BORDER_MAIN']
borderErrorFlashAddr = labelList['BORDER_ERROR_FLASH']
borderErrorMainAddr = labelList['BORDER_ERROR_MAIN']
printRoutine = labelList['PRINT_ROUTINE']
printParam = labelList['PRINT_PARAM']
baud = labelList['BAUD'] # Note: baud rate is set in setbaud.py

"""
Payload
"""
# Note that baud rate is set in two places:
# Below (for mastering) and near the bottom of boot2.asm (playback)
#
payload = Versaload(baud=baud)

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
    payload.execute(printRoutine,0.001*len(text))

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

borderMain(7)       # Blue border
borderFlash(2)      # Black flash
borderErrorMain(2)  # Red border
borderErrorFlash(0) # Magenta flash

# Loading screen
addScreen(optimiseScr(open("test2.scr","rb").read()))

# Load print routine
payload.load(printRoutine,open("print.bin","rb").read())

# Main code
mainData = open("test2.raw","rb").read()

# Load 0x5c00-0xbbff into final location
printColourText(0,0,"Versaload",7,2,bright=True)
printColourText(0,1,"test2 3000baud",7,2,bright=True)

payload.load(0x5dc0, mainData[0x0000:0x5e40])
if len(mainData) > 0x5e40:
    payload.load(0xfc00, mainData[0x5e40:0x6240])
if len(mainData) > 0x6240:
    payload.load(0xc000, mainData[0x6240:])
payload.load(0x5b00, genFixup(0xfc00,0xbc00,0x400,0x5dc0,0x5dc0))
payload.execute(0x5b00,0)


payloadblock = Blk_DRB(sampledata = payload.get().tobytes())
payloadblock.tstatespersample(payload.tStatesPerSample())
payloadblock.pause(0)
tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('test2.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()