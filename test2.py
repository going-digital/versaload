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
loaderheader = ZX_FileHdr(SPEC_FILE_PROG, '\x16\x0b\x0cLoading', 0, 0, 0)
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
countBlock = labelList['COUNT_BLOCK']
countDisable = labelList['COUNT_DISABLE']
countStates = labelList['COUNT_STATES']

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
def initPrint():
    # Load print routine
    payload.load(printRoutine,open("print.bin","rb").read())

def printText(x,y,text):
    # Print message to screen.
    # Restricted to character square positions, and char codes 32-127
    # Simple routine that does not support wrapping, colour or control codes
    data = pack("<2H",0x3d00,0x4000+(y//8)*0x800+(y%8)*0x20+x)
    data = data + text
    data = data + pack("<B",0)
    payload.load(printParam,data)
    payload.execute(printRoutine,0.001*len(text))

def setAttr(x,y,length,ink,paper,bright=False,flash=False):
    attrData = ink + 8*paper
    if bright:
        attrData = attrData + 0x40
    if flash:
        attrData = attrData + 0x80
    attrAddr = 0x5800 + y*32 + x
    payload.load(attrAddr,pack("<B",attrData)*length)

def printColourText(x,y,text,ink,paper,bright=False,flash=False):
    setAttr(x,y,len(text),ink,paper,bright,flash)
    printText(x,y,text)

"""
Countdown functions
"""
def countTime(bits):
    secs = bits // baud
    bits %= baud
    mins = secs // 60
    secs %= 60
    bits //= countStates
    if bits == 0:
        # This would be read as 65536 bits. Add 1 bit to fix things up.
        bits = 1
    data = pack("<3BHB",mins,secs//10,secs%10,bits,0xa5)
    payload.load(countBlock,data)
def countDisable():
    payload.load(countDisable,pack("<B",0x00))

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
def genFixup(src,dest,length,pc):
    # Relocate memory block and execute payload
    # Z80 version
    """
        01 nn nn    ld      bc,length
        11 nn nn    ld      de,dest
        21 nn nn    ld      hl,src
        ed b0       ldir
        c1          pop     bc
        c3 nn nn    jp      pc
    """
    data = pack("<BH",0x01,length)
    data = data + pack("<BH",0x11,dest)
    data = data + pack("<BH",0x21,src)
    data = data + pack("<2B",0xed,0xb0)
    data = data + pack("<B",0xc1)
    data = data + pack("<BH",0xc3,pc)
    return data

"""
Construct payload
"""
payload.delay(0.5)  # Wait for BASIC to execute. Let tape AGC settle.

# Set up border colours for the load
#
borderMain(7)       # White border
borderFlash(2)      # Red flash
borderErrorMain(2)  # Red border
borderErrorFlash(0) # Black flash

# Prepare loading screen
#
# Maximise use of paper by flipping character squares
screen = optimiseScr(open("test2.scr","rb").read())
# Place 'm' at (31,22) for countdown timer and set up attributes for timer
screenmod = screen[0:0x10df] + pack("<B",0xe3)
screenmod += screen[0x10e0:0x11df] + pack("<B",0x77)
screenmod += screen[0x11e0:0x12df] + pack("<B",0x7f)
screenmod += screen[0x12e0:0x13df] + pack("<B",0x6b)
screenmod += screen[0x13e0:0x14df] + pack("<B",0x63)
screenmod += screen[0x14e0:0x15df] + pack("<B",0x73)
screenmod += screen[0x15e0:0x16df] + pack("<B",0xc6)
screenmod += screen[0x16e0:0x17df] + pack("<B",0x00)
screenmod += screen[0x17e0:0x1ade] + pack("<2B",0x72,0x7b)
screenmod += screen[0x1ae0:0x1afe] + pack("<2B",0x72,0x72)

# Load loading screen
#
addScreen(screenmod)

# Main code
mainData = open("test2.raw","rb").read()

# Estimate payload length, for countdown timer
payloadBits = len(mainData) * 8 * (256*8+200) / (256*8) + baud/2

# Turn on countdown timer
def loadWithCountdown(addr, data, bits):
    while len(data) > 0:
        countTime(bits)
        bits -= 80+40 # Allowance for countdown block
        payload.load(addr,data[0:0x100])

        # Adjust parameters for next time around
        bits -= 80 # Allowance for data header
        bits -= 8*len(data[0:0x100])
        addr += len(data[0:0x100])
        data = data[0x100:]
    return bits

# Original is 6ae1 long, 0x5dc0 to c8a1
# Load 0x5dc0..0xbc00
payloadBits = loadWithCountdown(0x5dc0, mainData[0x0000:0x5e40],payloadBits)
if len(mainData) > 0x5e40:
    # Load 0xbc00..0xc000 to 0xd000+
    payloadBits = loadWithCountdown(0xd000, mainData[0x5e40:0x6240],payloadBits)
if len(mainData) > 0x6240:
    payloadBits = loadWithCountdown(0xc000, mainData[0x6240:],payloadBits)
payload.load(0xb493, pack("<H",5)) # Einar's patch to shorten startup delay
payload.load(0x4000, genFixup(0xd000,0xbc00,0x400,0x5dc0))

# Hide countdown timer - loading is complete
#setAttr(30,22,2,6,6,bright=True)
#setAttr(30,23,2,6,6,bright=True)

# Execute game
payload.execute(0x4000,0)


payloadblock = Blk_DRB(sampledata = payload.get().tobytes())
payloadblock.tstatespersample(payload.tStatesPerSample())
payloadblock.pause(0)
tape.add_block(payloadblock)

# Almost complete, the final stage is to write the TZX to a file.
tzxfile = open('test2.tzx', 'wb')
tape.write(tzxfile)
tzxfile.close()