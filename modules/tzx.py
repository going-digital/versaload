# Copyright (C) 2008 Ian Chapman
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# VERSION 0.5
from struct import pack,unpack

# TZX Version
VER_MAJ = 1
VER_MIN = 20

# TZX Block Values
TZXBLK_SSDB   = 0x10 # Standard Speed Data Block
TZXBLK_TSDB   = 0x11 # Turbo Speed Data Block
TZXBLK_PTB    = 0x12 # Pure Tone Block
TZXBLK_PSB    = 0x13 # Pulse Sequence Block
TZXBLK_PDB    = 0x14 # Pure Data Block
TZXBLK_DRB    = 0x15 # Direct Recording Block
TZXBLK_CRTDB  = 0x16 # C64 ROM Type Data Block (Deprecated, Not Implemented)
TZXBLK_CTTDB  = 0x17 # C64 Turbo Tape Data Block (Deprecated, Not Implemented)
TZXBLK_CSWRB  = 0x18 # CSW Recording Block !!!!!!!!!!!!!!!!!!!!!
TZXBLK_GDB    = 0x19 # Generalized Data Block (Not Implemented)
TZXBLK_PB     = 0x20 # Pause Block
TZXBLK_GSB    = 0x21 # Group Start Block
TZXBLK_GEB    = 0x22 # Group End Block
TZXBLK_JTB    = 0x23 # Jump To Block
TZXBLK_LSB    = 0x24 # Loop Start Block
TZXBLK_LEB    = 0x25 # Loop End Block
TZXBLK_CSB    = 0x26 # Call Sequence Block
TZXBLK_RFSB   = 0x27 # Return From Sequence Block
TZXBLK_SELB   = 0x28 # Select Block
TZXBLK_ST48MB = 0x2A # Stop the Tape if in 48k Mode Block
TZXBLK_SSLB   = 0x2B # Set Signal Level Block
TZXBLK_TDB    = 0x30 # Text Description Block
TZXBLK_MB     = 0x31 # Message Block
TZXBLK_AIB    = 0x32 # Archive Info Block
TZXBLK_HTB    = 0x33 # Hardware Type Block
TZXBLK_EIB    = 0x34 # Emulation Info Block (Deprecated, Not Implemented)
TZXBLK_CIB    = 0x35 # Custom Information Block
TZXBLK_SB     = 0x40 # Snapshot Block (Deprecated, Not Implemented)
TZXBLK_GB     = 0x5A # Glue Block. Indentical to TZX

# Hardware Type Values
HTYPE_COMPUTER  = 0x00
HTYPE_XSTORAGE  = 0x01
HTYPE_ROMRAM    = 0x02
HTYPE_SOUND     = 0x03
HTYPE_JOYSTICK  = 0x04
HTYPE_MOUSE     = 0x05
HTYPE_OTHER     = 0x06
HTYPE_SERIAL    = 0x07
HTYPE_PARALLEL  = 0x08
HTYPE_PRINTER   = 0x09
HTYPE_MODEM     = 0x0A
HTYPE_DIGITIZER = 0x0B
HTYPE_NETWORK   = 0x0C
HTYPE_KEYBOARD  = 0x0D
HTYPE_ADDA      = 0x0E
HTYPE_EPROM     = 0x0F
HTYPE_GFX       = 0x10

# Hardware Info Values
HINFO_RUNS       = 0
HINFO_RUNS_SFX   = 1
HINFO_RUNS_NOSFX = 2
HINFO_NORUN      = 3

# Archive Info Values
AINFO_TITLE      = 0x00
AINFO_PUBLISHER  = 0x01
AINFO_AUTHOR     = 0x02
AINFO_PUBYEAR    = 0x03
AINFO_LANG       = 0x04
AINFO_TYPE       = 0x05
AINFO_PRICE      = 0x06
AINFO_PROTECTION = 0x07
AINFO_ORIGIN     = 0x08
AINFO_COMMENT    = 0xFF

# Compression Types for CSW
CSW_RLE          = 1
CSW_ZRLE         = 2


# Header elements are:
# 0 - Magic string
# 1 - 0x1A magic string terminator
# 2 - Major version number
# 3 - Minor version number
class TZX:
    """
    TZX File.

    Implements a TZX file layout for emulating computer cassettes.
    """
    def __init__(self):
        self.__numblocks = 0
        self.__header = ['ZXTape!',
                         pack('<B', 0x1A),
                         pack('<B', VER_MAJ),
                         pack('<B', VER_MIN)]

        self.__blocks = []

    def add_block(self, block):
        """
        Adds a TZX block to a TZX file layout.

        Technically it copies the block which means that after the block has been
        added to the TZX, subsequent alterations to the block will not be reflected
        in the TZX. This does however mean the block can reused.
        """
        self.__numblocks = self.__numblocks + 1
        self.__blocks.extend(block.get())

    def set_version(self, major, minor):
        """
        Sets the major and minor version of the TZX.

        By default, the TZX will have the major and minor numbers set to the
        values of the following variables:

        VER_MAJ
        VER_MIN

        If for some reason you need to write a TZX with a different version you can
        set it with this method. It is however the programmers responsibility to ensure
        that any blocks added to the TZX are valid for the TZX version they've specified.
        """
        self.__header[2] = pack('<B', major)
        self.__header[3] = pack('<B', minor)

    def write(self,fh):
        """
        Writes the complete TZX to a file.

        A valid file handle should be passed this method. It makes no checks as to the
        validity of the file for writing.
        """
        for element in self.__header:
            fh.write(element)

        for element in self.__blocks:
            fh.write(element)


# Header elements are:
# 0 - Block ID (8b)
# 1 - Pause after block (in ms) (16b)
# 2 - Data length (16b)
class Blk_SSDB:
    """
    Standard Speed Data Block

    Implements a TZX block for representing standard speed data.
    """
    id = TZXBLK_SSDB

    def __init__(self, plen=1000, data=None):
        self.__header = range(3)
        self.__header[0] = pack('<B', self.id)
        self.__header[2] = pack('<H', 0) # We must initialise data length to zero here
        self.__data = []
        self.pause(plen)
        self.encapsulate(data)

    def pause(self, plen=None):
        """
        Sets and returns the pause length after this block (in milliseconds).

        'plen' should be a value between 0 and 65535 inclusive.

        If 'plen' is 'None' the current value is returned and no change is made.
        """
        if plen is not None:
            self.__header[1] = pack('<H', plen)
        return unpack('<H', self.__header[1])[0]

    def encapsulate(self, data):
        """
        Encapsulates a block of data into a Standard Speed Data Block.

        If the calculated size of the 'data' in bytes is greater than 65,535 bytes then
        it will return a value of 1 and the data will not be encapsulated. A return
        value of 'None' means success. This method replaces any data that has
        previously been encapsulated.
        """
        l = 0
        if data is not None:
            l = byteslen(data)
            if (l > 65535):
                return 1
            else:
                self.__data = data[:]
        self.__header[2] = pack('<H', l)

    def datalen(self):
        """
        Returns the length in bytes of the currently encapsulated data.
        """
        return unpack('<H', self.__header[2])[0]

    def get(self):
        """
        Returns a complete Standard Speed Data Block.
        """
        ssdblock = self.__header[:]
        ssdblock.extend(self.__data)
        return ssdblock


# Header elements
# 0 - Block ID (8b)
# 1 - Length pilot pulse (16b)
# 2 - Length sync 1st pulse (16b)
# 3 - Length sync 2nd pulse (16b)
# 4 - Length zero bit pulse (16b)
# 5 - Length one bit pulse (16b)
# 6 - Length pilot tone (16b)
# 7 - Used bits (8b)
# 8 - Pause after block [ms] (16b)
# 9 - Data length (24b)
class Blk_TSDB:
    """
    Turbo Speed Data Block

    Implements a TZX block for representing turbo speed data.
    """
    id = TZXBLK_TSDB

    def __init__(self, ppulse=2168, spulse1=667, spulse2=735, bpulse0=855, bpulse1=1710, ptone=8063, ubits=8, plen=1000, data=None):
        self.__header = range(10)
        self.__header[0] = pack('<B', self.id)
        self.__header[9] = pack('<L', 0) # We must initialise data length to zero here
        self.__header[9] = self.__header[9][:3] # Its only 3 bytes, so truncate it
        self.__data = []
        self.pilotpulse(ppulse)
        self.syncpulse1(spulse1)
        self.syncpulse2(spulse2)
        self.bitpulse0(bpulse0)
        self.bitpulse1(bpulse1)
        self.pilottone(ptone)
        self.usedbits(ubits)
        self.pause(plen)
        self.encapsulate(data)

    def pilotpulse(self,ppulse=None):
        """
        Sets and returns the length of PILOT pulse (in T states).

        'ppulse' should be a value between 0 and 65535 inclusive.

        If 'ppulse' is 'None' the current value is returned and no change is made.
        """
        if ppulse is not None:
            self.__header[1] = pack('<H', ppulse)
        return unpack('<H', self.__header[1])[0]

    def syncpulse1(self,spulse1=None):
        """
        Sets and returns the length of the first SYNC pulse (in T states).

        'spulse1' should be a value between 0 and 65535 inclusive.

        If 'spulse1' is 'None' the current value is returned and no change is made.
        """
        if spulse1 is not None:
            self.__header[2] = pack('<H', spulse1)
        return unpack('<H', self.__header[2])[0]

    def syncpulse2(self,spulse2=None):
        """
        Sets and returns the length of the second SYNC pulse (in T states).

        'spulse2' should be a value between 0 and 65535 inclusive.

        If 'spulse2' is 'None' the current value is returned and no change is made.
        """
        if spulse2 is not None:
            self.__header[3] = pack('<H', spulse2)
        return unpack('<H', self.__header[3])[0]

    def bitpulse0(self,bpulse0=None):
        """
        Sets and returns the length of a ZERO bit pulse (in T states).

        'bpulse0' should be a value between 0 and 65535 inclusive.

        If 'bpulse0' is 'None' the current value is returned and no change is made.
        """
        if bpulse0 is not None:
            self.__header[4] = pack('<H', bpulse0)
        return unpack('<H', self.__header[4])[0]

    def bitpulse1(self,bpulse1=None):
        """
        Sets and returns the length of a ONE bit pulse (in T states).

        'bpulse1' should be a value between 0 and 65535 inclusive.

        If 'bpulse1' is 'None' the current value is returned and no change is made.
        """
        if bpulse1 is not None:
            self.__header[5] = pack('<H', bpulse1)
        return unpack('<H', self.__header[5])[0]

    def pilottone(self,ptone=None):
        """
        Sets and returns the length of a PILOT tone (in pulses).

        'ptone' should be a value between 0 and 65535 inclusive.

        If 'ptone' is 'None' the current value is returned and no change is made.
        """
        if ptone is not None:
            self.__header[6] = pack('<H', ptone)
        return unpack('<H', self.__header[6])[0]

    def usedbits(self,ubits=None):
        """
        Sets and returns the value of the used bits in the last byte.

        'ubits' should be a value between 0 and 8 inclusive. For example if this is 6
        then the bits used in the last byte are xxxxxx00 where MSb is the leftmost
        bit). If a value > 8 is used it will be set to 8.

        If 'ubits' is 'None' the current value is returned and no change is made.
        """
        if ubits is not None:
            if ubits > 8:
                ubits = 8
            self.__header[7] = pack('<B', ubits)
        return unpack('<B', self.__header[7])[0]

    def pause(self,plen=None):
        """
        Sets and returns the pause length after this block (in milliseconds).

        'plen' should be a value between 0 and 65535 inclusive.

        If 'plen' is 'None' the current value is returned and no change is made.
        """
        if plen is not None:
            self.__header[8] = pack('<H', plen)
        return unpack('<H', self.__header[8])[0]

    def datalen(self):
        """
        Returns the length in bytes of the currently encapsulated data.
        """
        # 3 byte value, so add empty byte and decode as long
        return unpack('<L',self.__header[9] + "\x00")[0]

    def encapsulate(self, data):
        """
        Encapsulates a block of data into a Turbo Speed Data Block.

        If the calculated size of the 'data' in bytes is greater than 16,777,215 bytes
        then it will return a value of 1 and the data will not be encapsulated. A
        return value of 'None' means success. This method replaces any data that has
        previously been encapsulated.
        """
        l = 0
        if data is not None:
            l=byteslen(data)
            if (l > 16777215):
                return 1
            else:
                self.__data = data[:]
        # 3 byte value so encode as long but strip last byte
        self.__header[9] = pack('<L', l)
        self.__header[9] = self.__header[9][:3]

    def get(self):
        """
        Returns a complete Turbo Speed Data Block.
        """
        tsdblock = self.__header[:]
        tsdblock.extend(self.__data)
        return tsdblock


# Header elements
# 0 - Block ID (8b)
# 1 - Length zero bit pulse (16b)
# 2 - Length one bit pulse (16b)
# 3 - Used bits (8b)
# 4 - Pause after block [ms] (16b)
# 5 - Data length (24b)
class Blk_PDB:
    """
    Pure Data Block

    Implements a TZX block for turbo speed data, but without pilot or sync pulses.
    """
    id = TZXBLK_PDB

    def __init__(self, bpulse0=855, bpulse1=1710, ubits=8, plen=1000, data=None):
        self.__header = range(6)
        self.__header[0] = pack('<B', self.id)
        self.__header[5] = pack('<L', 0) # We must initialise data length to zero here
        self.__header[5] = self.__header[5][:3] # Its only 3 bytes, so truncate it
        self.__data = []
        self.bitpulse0(bpulse0)
        self.bitpulse1(bpulse1)
        self.usedbits(ubits)
        self.pause(plen)
        self.encapsulate(data)

    def bitpulse0(self,bpulse0=None):
        """
        Sets and returns the length of a ZERO bit pulse (in T states).

        'bpulse0' should be a value between 0 and 65535 inclusive.

        If 'bpulse0' is 'None' the current value is returned and no change is made.
        """
        if bpulse0 is not None:
            self.__header[1] = pack('<H', bpulse0)
        return unpack('<H', self.__header[1])[0]

    def bitpulse1(self,bpulse1=None):
        """
        Sets and returns the length of a ONE bit pulse (in T states).

        'bpulse1' should be a value between 0 and 65535 inclusive.

        If 'bpulse1' is 'None' the current value is returned and no change is made.
        """
        if bpulse1 is not None:
            self.__header[2] = pack('<H', bpulse1)
        return unpack('<H', self.__header[2])[0]

    def usedbits(self,ubits=None):
        """
        Sets and returns the value of the used bits in the last byte.

        'ubits' should be a value between 0 and 8 inclusive. For example if this is 6
        then the bits used in the last byte are xxxxxx00 where MSb is the leftmost
        bit). If a value > 8 is used it will be set to 8.

        If 'ubits' is 'None' the current value is returned and no change is made.
        """
        if ubits is not None:
            if ubits > 8:
                ubits = 8
            self.__header[3] = pack('<B', ubits)
        return unpack('<B', self.__header[3])[0]

    def pause(self,plen=None):
        """
        Sets and returns the pause length after this block (in milliseconds).

        'plen' should be a value between 0 and 65535 inclusive.

        If 'plen' is 'None' the current value is returned and no change is made.
        """
        if plen is not None:
            self.__header[4] = pack('<H', plen)
        return unpack('<H', self.__header[4])[0]

    def datalen(self):
        """
        Returns the length in bytes of the currently encapsulated data.
        """
        # 3 byte value, so add empty byte and decode as long
        return unpack('<L',self.__header[5] + "\x00")[0]

    def encapsulate(self, data):
        """
        Encapsulates a block of data into a Pure Data Block.

        If the calculated size of the 'data' in bytes is greater than 16,777,215 bytes
        then it will return a value of 1 and the data will not be encapsulated. A
        return value of 'None' means success. This method replaces any data that has
        previously been encapsulated.
        """
        l = 0
        if data is not None:
            l=byteslen(data)
            if (l > 16777215):
                return 1
            else:
                self.__data = data[:]
        # 3 byte value so encode as long but strip last byte
        self.__header[5] = pack('<L', l)
        self.__header[5] = self.__header[5][:3]

    def get(self):
        """
        Returns a complete Pure Data Block.
        """
        pdblock = self.__header[:]
        pdblock.extend(self.__data)
        return pdblock


# Header values are:
# 0 - Block ID (8b)
# 1 - T-states per sample (16b)
# 2 - Pause after block (in ms) - (16b)
# 3 - Used bits in last byte (8b)
# 4 - Length of samples data (24b)
class Blk_DRB:
    """
    Direct Recording Block.

    Implements a TZX block which represents direct recording for when a Turbo
    Speed Data Block or similar cannot be used.
    """
    id = TZXBLK_DRB

    def __init__(self, tspsample=0, plen=1000, ubits=8, sampledata=None):
        self.__header=range(5)
        self.__header[0] = pack('<B', self.id)
        self.__header[4] = pack('<L', 0) # We must initialise data length to zero here
        self.__header[4] = self.__header[4][:3] # Its only 3 bytes, so truncate it
        self.__sampledata = []
        self.tstatespersample(tspsample)
        self.pause(plen)
        self.usedbits(ubits)
        self.encapsulate(sampledata)

    def tstatespersample(self,tspsample=None):
        """
        Sets and returns the number of T states per sample (bit of data)

        'tspsample' should be a value between 0 and 65535 inclusive.

        If 'tspsample' is 'None' the current value is returned and no change is made.
        """
        if tspsample is not None:
            self.__header[1] = pack('<H', tspsample)
        return unpack('<H', self.__header[1])[0]


    def pause(self,plen=None):
        """
        Sets and returns the pause length after this block (in milliseconds).

        'plen' should be a value between 0 and 65535 inclusive.

        If 'plen' is 'None' the current value is returned and no change is made.
        """
        if plen is not None:
            self.__header[2] = pack('<H', plen)
        return unpack('<H', self.__header[2])[0]

    def usedbits(self,ubits=None):
        """
        Sets and returns the value of the used bits in the last byte.

        'ubits' should be a value between 0 and 8 inclusive. For example if this is 6
        then the bits used in the last byte are xxxxxx00 where MSb is the leftmost
        bit). If a value > 8 is used it will be set to 8.

        If 'ubits' is 'None' the current value is returned and no change is made.
        """
        if ubits is not None:
            if ubits > 8:
                ubits = 8
            self.__header[3] = pack('<B', ubits)
        return unpack('<B', self.__header[3])[0]

    def datalen(self):
        """
        Returns the length in bytes of the currently encapsulated sample data.
        """
        # 3 byte value, so add empty byte and decode as long
        return unpack('<L',self.__header[4] + "\x00")[0]

    def encapsulate(self, sampledata):
        """
        Encapsulates a block of sample data into a Direct Recording Block.

        If the calculated size of the 'data' in bytes is greater than 16,777,215 bytes
        then it will return a value of 1 and the data will not be encapsulated. A
        return value of 'None' means success. This method replaces any data that has
        previously been encapsulated.

        Each sample value is represented by one bit only (0=low, 1=high). It is
        recommended that sample frequencies of 22050Hz or 44100Hz are used.
        """
        l = 0
        if sampledata is not None:
            l=byteslen(sampledata)
            if (l > 16777215):
                return 1
            else:
                self.__sampledata = sampledata[:]
        # 3 byte value so encode as long but strip last byte
        self.__header[4] = pack('<L', l)
        self.__header[4] = self.__header[4][:3]

    def get(self):
        """
        Returns a complete Direct Recording Block.
        """
        drblock = self.__header[:]
        drblock.extend(self.__sampledata)
        return drblock


# Header values are:
# 0 - Block ID (8b)
# 1 - Length not include ID and these byes (32b)
# 2 - Pause after block (in ms) - (16b)
# 3 - Sampling Rate (24b)
# 4 - Compression Type (8b)
# 5 - Number of stored pulses (after decompression) (32b)
class Blk_CSWRB:
    """
    CSW Recording Block.

    Implements a TZX block which represents a sequence of pulses encoded in CSW format
    V2 (Compressed Square Wave).
    """
    id = TZXBLK_CSWRB

    def __init__(self, plen=1000, srate=22050, ctype=CSW_RLE, spulses=0, sampledata=None):
        self.__header=range(6)
        self.__header[0] = pack('<B', self.id)
        self.__header[1] = pack('<L', 10)
        self.__sampledata = []
        self.pause(plen)
        self.samplerate(srate)
        self.compression(ctype)
        self.storedpulses(spulses)
        self.encapsulate(sampledata)

    def pause(self,plen=None):
        """
        Sets and returns the pause length after this block (in milliseconds).

        'plen' should be a value between 0 and 65535 inclusive.

        If 'plen' is 'None' the current value is returned and no change is made.
        """
        if plen is not None:
            self.__header[2] = pack('<H', plen)
        return unpack('<H', self.__header[2])[0]

    def samplerate(self,srate=None):
        """
        Sets and returns sample rate value.

        'srate' should be a value between 0 and 16,777,215 inclusive.

        If 'srate' is 'None' the current value is returned and no change is made.
        """
        if srate is not None:
            # 3 byte value so encode as long but strip last byte
            self.__header[3] = pack('<L', srate)
            self.__header[3] = self.__header[3][:3]
        # 3 byte value, so add empty byte and decode as long
        return unpack('<L', self.__header[3] + "\x00")[0]

    def compression(self, ctype=None):
        """
        Sets the compression used in the CSW sample data.

        'ctype' should be one of the following:
        CSW_RLE
        CSW_ZRLE

        If 'ctype' is 'None' the current value is returned and no change is made.
        """
        if ctype is not None:
            self.__header[4] = pack('<B', ctype)
        return unpack('<B', self.__header[4])[0]

    def storedpulses(self, spulses=None):
        """
        Sets the number of stored pulses, after decompression.

        'spulses' should be a value between 0 and 4,294,967,296 inclusive.

        If 'spulses' is 'None' the current value is returned and no change is made.
        """
        if spulses is not None:
            self.__header[5] = pack('<L', spulses)
        return unpack('<L', self.__header[5])[0]

    def datalen(self):
        """
        Returns the length in bytes of the currently encapsulated sample data.
        """
        # -10 to account for other block fields.
        return (unpack('<L',self.__header[1])[0] - 10)

    def encapsulate(self, sampledata):
        """
        Encapsulates a block of sample data into a CSW Recording Block.

        The encapsulated data should be in CSW format v2 (Compressed Square Wave)
        """
        l = 0
        if sampledata is not None:
            l=byteslen(sampledata)
            self.__sampledata = sampledata[:]
        # + 10 to account for other block fields.
        self.__header[1] = pack('<L', (l+10))


    def get(self):
        """
        Returns a complete CSW Recording Block.
        """
        cswrblock = self.__header[:]
        cswrblock.extend(self.__sampledata)
        return cswrblock

# Header elements are:
# 0 - Block ID (8b)
# 1 - Length of one pulse (in T states) (16b)
# 2 - Number of pulses (16b)
class Blk_PTB:
    """
    Pure Tone Block

    Implements a TZX block for simulating a pure tone on the tape.
    """
    id = TZXBLK_PTB

    def __init__(self, plen=0, pnum=0):
        self.__header = range(3)
        self.__header[0] = pack('<B', self.id)
        self.pulselen(plen)
        self.pulsenum(pnum)

    def pulselen(self, plen=None):
        """
        Sets and returns the pulse length (in T states).

        'plen' should be a value between 0 and 65535 inclusive.

        If 'plen' is 'None' the current value is returned and no change is made.
        """
        if plen is not None:
            self.__header[1] = pack('<H', plen)
        return unpack('<H', self.__header[1])[0]

    def pulsenum(self, pnum=None):
        """
        Sets and returns the number of pulses.

        'pnum' should be a value between 0 and 65535 inclusive.

        If 'pnum' is 'None' the current value is returned and no change is made.
        """
        if pnum is not None:
            self.__header[2] = pack('<H', pnum)
        return unpack('<H', self.__header[2])[0]

    def get(self):
        """
        Returns a complete Pure Tone Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
# 1 - Number of pulses (8b)
class Blk_PSB:
    """
    Pulse Sequence Block

    Implements a TZX block for representing a sequence of pulses.
    """
    id = TZXBLK_PSB

    def __init__(self):
        self.__pulses = []
        self.__header = [pack('<B', self.id),
                         pack('<B', len(self.__pulses))] # We must initialise this here

    def add_pulse(self, plen):
        """
        Adds a pulse to the Pulse Sequence Block.

        'plen' is the length of the pulse (in T states) and should be a value
        between 0 and 65535 inclusive.

        If a value of 1 is returned then the maximum number of pulses (255) has already
        been reached and the pulse will not be added. 'None' will be returned on
        success.
        """
        if (len(self.__pulses) == 255):
            return 1
        else:
            self.__pulses.append(pack('<H', plen))
            self.__header[1] = pack('<B', len(self.__pulses))

    def pulsenum(self):
        """
        Returns the number of pulses that have been added.
        """
        return len(self.__pulses)

    def get(self):
        """
        Returns a complete Pulse Sequence Block.
        """
        psblock = self.__header[:]
        psblock.extend(self.__pulses)
        return psblock


# Header elements are
# 0 - Block ID (8b)
# 1 - Number of calls (8b)
class Blk_CSB:
    """
    Call Sequence Block

    A TZX block analagous to a CALL statement. It executes a sequence of blocks
    then returns to the next block. It should be used in conjuction with a Return
    From Sequence Block. Call Sequence Blocks should never be nested.
    """
    id = TZXBLK_CSB

    def __init__(self):
        self.__calls = []
        self.__header = [pack('<B', self.id),
                         pack('<B', len(self.__calls))] # We must initialise this here

    def add_call(self, call):
        """
        Adds a call to the Call Sequence Block.

        'call' is a relative signed offset to the block. It should be a value between
        -32768 and 32767 inclusive. A negative value means jump backwards, whilst a
        positive value means forwards. Calls should never be nested.

        If a value of 1 is returned then the maximum number of calls (255) has already
        been reached and the call will not be added. 'None' will be returned on
        success.
        """
        if (len(self.__calls) == 255):
            return 1
        else:
            self.__calls.append(pack('<h', call))
            self.__header[1] = pack('<B', len(self.__calls))

    def callnum(self):
        """
        Returns the number of calls that have been added.
        """
        return len(self.__calls)

    def get(self):
        """
        Returns a complete Call Sequence Block.
        """
        csblock = self.__header[:]
        csblock.extend(self.__calls)
        return csblock

# Header elements are
# 0 - Block ID (8b)
class Blk_RFSB:
    """
    Return From Sequence Block.

    Implements a TZX block for terminating a call sequence. This TZX block has no
    body and should be used in conjunction with a Call Sequence Block.
    """
    id = TZXBLK_RFSB

    def __init__(self):
       self.__header = [pack('<B', self.id)]

    def get(self):
        """
        Returns a complete Return From Sequence Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
# 1 - Duration of pause (in ms) (16b)
class Blk_PB:
    """
    Pause Block (or Stop The Tape Block)

    Implements a TZX block for simulating silence on the tape or a "STOP THE TAPE"
    command.
    """
    id = TZXBLK_PB

    def __init__(self,duration=0):
        self.__header = range(2)
        self.__header[0] = pack('<B', self.id)
        self.duration(duration)

    def duration(self,duration=None):
        """
        Sets and returns the duration (in milliseconds) of silence.

        'duration' should be between 0 and 65535 inclusive. A value of 0 effectively
        means "STOP THE TAPE".

        If 'duration' is 'None' the current value is returned and no change is made.
        """
        if duration is not None:
            self.__header[1] = pack('<H',duration)
        return unpack('<H', self.__header[1])[0]

    def get(self):
        """
        Returns a complete Pause Block.
        """
        return self.__header[:]


# Header elements are:
# 0 - Block ID (8b)
# 1 - Group name string len (8b)
# 2 - Group name string
class Blk_GSB:
    """
    Group Start Block

    Implements a TZX block for representing a group of blocks treated as a single
    composite block.
    """
    id = TZXBLK_GSB

    def __init__(self, gname="Empty Group Name"):
        self.__header = range(3)
        self.__header[0] = pack('<B', self.id)
        self.groupname(gname)

    def groupname(self,gname=None):
        """
        Sets and returns the group name.

        If the group name string is larger than 255 bytes it will be truncated. It is
        recommended that you limit the string size to 30 bytes for the convenience of
        emulators.

        If 'gname' is 'None' the current value is returned and no change is made.
        """
        if gname is not None:
            self.__header[2] = gname[:255]
            self.__header[1] = pack('<B', len(self.__header[2]))
        return self.__header[2]

    def get(self):
        """
        Returns a complete Group Start Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
class Blk_GEB:
    """
    Group End Block.

    Implements a TZX block for terminating a group. This TZX block has no body and
    should be used in conjunction with a Group Start Block.
    """
    id = TZXBLK_GEB

    def __init__(self):
        self.__header = [pack('<B', self.id)]

    def get(self):
        """
        Returns a complete Group End Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
# 1 - Number of blocks to jump forwards/backwords (-ve means backwards) (16b)
class Blk_JTB:
    """
    Jump To Block

    Implements a TZX block for relative jumping to another TZX block.
    """
    id = TZXBLK_JTB

    def __init__(self, jump=1):
        self.__header = range(2)
        self.__header[0] = pack('<B', self.id)
        self.jump(jump)

    def jump(self, jump=None):
        """
        Sets and returns the relative block to jump to.

        'jump' should be between -32768 and 32767 inclusive, however it is recommended
        that you do not use 0 otherwise it may cause an infinite loop. A negative value
        means jump backwards, whilst a positive value means forwards.

        If 'jump' is 'None' the current value is returned and no change is made.
        """
        if jump is not None:
            self.__header[1] = pack('<h', jump)
        return unpack('<h', self.__header[1])[0]

    def get(self):
        """
        Returns a complete Jump To Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
# 1 - Number of repetitions (16b)
class Blk_LSB:
    """
    Loop Start Block.

    Implements a TZX block for initiating a loop in a similar fashion to BASIC's
    'FOR' statement. It should be used in conjunction with a Loop End Block.
    Nesting should be avoided.
    """
    id = TZXBLK_LSB

    def __init__(self, repetitions=2):
        self.__header = range(2)
        self.__header[0] = pack('<B', self.id)
        self.repetitions(repetitions)

    def repetitions(self, repetitions=None):
        """
        Sets and returns the number of repetitions the loop should perform.

        'repetitions' should be between 0 and 65535 inclusive, however it is
        recommended that you do not use 0 or 1.

        If 'repetitions' is 'None' the current value is returned and no change is made.
        """
        if repetitions is not None:
            self.__header[1] = pack('<H', repetitions)
        return unpack('<H', self.__header[1])[0]

    def get(self):
        """
        Returns a complete Loop Start Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
class Blk_LEB:
    """
    Loop End Block.

    Implements a TZX block for terminating a loop in a similar fashion to BASIC's
    'NEXT' statement. This TZX block has no body and should be used in conjunction
    with a Loop Start Block.
    """
    id = TZXBLK_LEB

    def __init__(self):
       self.__header = [pack('<B', self.id)]

    def get(self):
        """
        Returns a complete Loop End Block.
        """
        return self.__header[:]


# Header elements are
# 0 - Block ID (8b)
# 1 - Length of block, excluding ID and itself. (Always 0 as no body) (32b)
class Blk_ST48MB:
    """
    Stop the Tape if in 48k Mode Block

    Implements a TZX block for stopping the tape if the emulated machine is a 48K
    spectrum or is in 48k mode.
    """
    id = TZXBLK_ST48MB

    def __init__(self):
       self.__header = [pack('<B', self.id),
                        pack('<L', 0)] # Always 0

    def get(self):
        """
        Returns a complete Stop the Tape if in 48k Mode Block.
        """
        return self.__header[:]


# Header values are
# 0 - Block ID (8b)
# 1 - Number of bytes in description string (8b)
# 2 - Description
class Blk_TDB:
    """
    Text Description Block

    Implements a TZX block intended to identify parts of the tape.
    """
    id = TZXBLK_TDB

    def __init__(self, description="Empty Description"):
        self.__header = range(3)
        self.__header[0] = pack('<B', self.id)
        self.description(description)

    def description(self,description=None):
        """
        Sets and returns the description.

        If the description string is larger than 255 bytes it will be truncated. It is
        recommended that you limit the string size to 30 bytes for the convenience of
        emulators.

        If 'description' is 'None' the current value is returned and no change is made.
        """
        if description is not None:
            self.__header[2] = description[:255]
            self.__header[1] = pack('<B', len(self.__header[2]))
        return self.__header[2]

    def get(self):
        """
        Returns a complete Text Description Block.
        """
        return self.__header[:]

# Header values are
# 0 - Block ID (8b)
# 1 - Time in secs for msg to be shown (8b)
# 2 - Length of text (8b)
# 3 - Message
class Blk_MB:
    """
    Text Description Block

    Implements a TZX block intended to identify parts of the tape.
    """
    id = TZXBLK_MB

    def __init__(self, msg="Empty Message", t=0):
        self.__header = range(4)
        self.__header[0] = pack('<B', self.id)
        self.time(t)
        self.message(msg)


    def message(self, msg=None):
        """
        Sets and returns the message.

        If the message string is larger than 255 bytes it will be truncated. It is
        recommended that you limit the string size to 30 bytes and use no more than 8
        lines. Lines should be separated with a carriage return (0x0D).

        If 'msg' is 'None' the current value is returned and no change is made.
        """
        if msg is not None:
            self.__header[3] = msg[:255]
            self.__header[2] = pack('<B', len(self.__header[3]))
        return self.__header[3]

    def time(self, t=None):
        """
        Sets and returns the time (in seconds) that the message should be displayed
        for.

        't' should be between 0 and 255 inclusive. A value of 0 effectively means
        wait until the user clears the message.

        If 't' is 'None' the current value is returned and no change is made.
        """
        if t is not None:
            self.__header[1] = pack('<B', t)
        return unpack('<B', self.__header[1])[0]

    def get(self):
        """
        Returns a complete Message Block.
        """
        return self.__header[:]


# Header elements are:
# 0 - Block ID (8b)
# 1 - Length of block excluding ID and these bytes. (Always 1) (32b)
# 2 - Signal (8b)
class Blk_SSLB:
    """
    Set Signal Level Block.

    TZX block for setting the signal either low or high to avoid ambiguities with
    some custom loaders.
    """
    id = TZXBLK_SSLB

    def __init__(self, signal=0):
        self.__header = range(3)
        self.__header[0] = pack('<B', self.id)
        self.__header[1] = pack('<L', 1)
        self.signal(signal)

    def signal(self, signal=None):
        """
        Sets and returns the signal level.

        'signal' should be either 0 for low signal or 1 for high signal.

        If 'signal' is 'None' the current value is returned and no change is made.
        """
        if signal is not None:
            self.__header[2] = pack('<B', signal)
        return unpack('<B', self.__header[2])[0]

    def get(self):
        """
        Returns a complete Signal Level Block.
        """
        return self.__header[:]


# Header elements are:
# 0 - Block ID (8b)
# 1 - Number of hardware entries (8b)
class Blk_HTB:
    """
    Hardware Type Block.

    Implements a TZX block for holding information about hardware compatibility.
    """
    id = TZXBLK_HTB

    def __init__(self):
        self.__hardware = []
        self.__header = [pack('<B', self.id),
                         pack('<B', len(self.__hardware))] # We must initialise this here

    def add_hardware(self, htype, hid, hinfo):
        """
        Adds a hardware entry to the Hardware Type Block.

        'htype' is the main hardware category the device belongs in and should be one
        set to one of the HTYPE_* variables.

        'hid' is the specific hardware identifier. Please consult the TZX specification
        for the correct value to use.

        'hinfo' describes how this tape runs, or doesn't run on the hardware specified.
        It should be set to one of the following variables:
            HINFO_RUNS       : Tape runs and MAY OR MAY NOT use any special hardware
                               feautres
            HINFO_RUNS_SFX   : Tape RUNS AND USES any special features of the hardware
            HINFO_RUNS_NOSFX : Tape runs but DOES NOT USE any special features of the
                               hardware
            HINFO_NORUN      : DOES NOT RUN on the specified hardware.

        If a value of 1 is returned then the maximum number of hardware entries (255)
        has already been reached and the entry will not be added. 'None' will be
        returned on success.
        """
        if (len(self.__hardware) == 255):
            return 1
        else:
            self.__hardware.append(pack('<BBB', htype, hid, hinfo))
            self.__header[1] = pack('<B', len(self.__hardware))

    def hardwarenum(self):
        """
        Returns the number of hardware entries that have been added.
        """
        return len(self.__hardware)

    def get(self):
        """
        Returns a complete Hardware Type Block.
        """
        htblock = self.__header[:]
        htblock.extend(self.__hardware)
        return htblock


# Header elements are:
# 0 - Block ID (8b)
# 1 - Length of block excluding ID and these bytes (16b)
# 2 - Number of text strings
class Blk_AIB():
    """
    Archive Info Block.

    A TZX block for holding information about the tape file, useful to archivists
    and the curious. The Archive Info Block if present, should usually appear as
    the first block in a TZX file.
    """
    id = TZXBLK_AIB

    def __init__(self):
        self.__info = []
        self.__header = [pack('<B', self.id),
                         pack('<H', 1),
                         pack('<B', len(self.__info))] # We must initialise this here

    def add_info(self, textid, info):
        """
        Adds an information entry to the Archive Info Block.

        'textid' specifies what the information represents and should be one set to one
        of the AINFO_* variables.

        'info' is the actual text string itself. If 'info' is longer than 255 bytes, it
        will be truncated.

        If a value of 1 is returned then the maximum number of info entries (255)
        has already been reached and the entry will not be added. 'None' will be
        returned on success.
        """
        if (len(self.__info) == 255):
            return 1
        else:
            info = info[:255]
            # Ensure these values are in a single element for correct counting of info entries
            self.__info.append(pack('<BB', textid, len(info)) + info)
            # Calculate complete length of block
            self.__header[1] = pack('<H', (unpack('<H', self.__header[1])[0] + len(info) + 2))
            self.__header[2] = pack('<B', len(self.__info))

    def infonum(self):
        """
        Returns the number of info entries that have been added.
        """
        return len(self.__info)

    def get(self):
        """
        Returns a complete Archive Info Block.
        """
        aiblock = self.__header[:]
        aiblock.extend(self.__info)
        return aiblock


# Header elements are:
# 0 - Block ID (8b)
# 1 - Ident String (always 10 bytes)
# 2 - Length of custom info (16b)
class Blk_CIB:
    """
    Custom Information Block

    The custom info block is intended to hold pretty much any information you want.
    """
    id = TZXBLK_CIB

    def __init__(self, cid="No ID", data=None):
        self.__header=range(3)
        self.__header[0] = pack('<B', self.id)
        self.__header[2] = pack('<H', 0) # We must initialise this here
        self.__data = []
        self.setcid(cid)
        self.encapsulate(data)

    def setcid(self, cid=None):
        """
        Sets and returns the identification string for the Custom Info Block.

        'cid' will be truncated or extended to 10 characters by padding with
         spaces if necessary.

         If 'cid' is 'None' the current value is returned and no change is made.
        """
        if cid is not None:
            # Id is ALWAYS 10 chars. We space pad it if necessary.
            cid = cid.ljust(10)
            cid = cid[:10]
            self.__header[1] = cid
        return self.__header[1]

    def datalen(self):
        """
        Returns the length in bytes of the currently encapsulated data.
        """
        return unpack('<H',self.__header[2])[0]

    def encapsulate(self, data):
        """
        Encapsulates a block of custom data into the Custom Info Block.

        If the calculated size of the 'data' in bytes is greater than 65535 bytes
        then it will return a value of 1 and the data will not be encapsulated. A
        return value of 'None' means success. This method replaces any data that has
        previously been encapsulated.
        """
        l = 0
        if data is not None:
            l=byteslen(data)
            if (l > 65535):
                return 1
            else:
                self.__data = data[:]
        # 3 byte value so encode as long but strip last byte
        self.__header[2] = pack('<H', l)

    def get(self):
        """
        Returns a complete Custom Info Block.
        """
        ciblock = self.__header[:]
        ciblock.extend(self.__data)
        return ciblock


# Header elements are:
# 0 - Block ID (8b)
# 1 - Length of block minus header and this element (16b)
# 2 - Number of selections (8b)
class Blk_SELB:
    """
    Select Block.

    A TZX block which is useful when a tape consists of several separely loadable
    parts. Essentially it provides a mechanism whereby an emulator can give the
    user a choice about which part of the tape to load next.
    """
    id = TZXBLK_SELB

    def __init__(self):
        self.__selections = []
        self.__header = [pack('<B', self.id),
                         pack('<H', 0),
                         pack('<B', len(self.__selections))] # We must initialise this here

    def add_select(self, offset, desc):
        """
        Adds a selection to the Select Block.

        'offset' is a relative offset to the block and should be a value between -32768
        and 32767 inclusive. A negative value means jump backwards, whilst a positive
        value means forwards.

        'desc' is a text description which may appear for example in a menu presented
        to the user. If it is longer than 30 characters it will be truncated.

        If a value of 1 is returned then the maximum number of selection entries (255)
        has already been reached and the entry will not be added. 'None' will be
        returned on success.
        """
        if (len(self.__selections) == 255):
            return 1
        else:
            desc = desc[:30]
            # Ensure these values are in a single element for correct counting of info entries
            self.__selections.append(pack('<hB', offset, len(desc)) + desc)
            # Calculate complete length of block
            self.__header[1] = pack('<H', (unpack('<H', self.__header[1])[0] + len(desc) + 3))
            self.__header[2] = pack('<B', len(self.__selections))

    def selectnum(self):
        """
        Returns the number of selection entries that have been added.
        """
        return len(self.__selections)

    def get(self):
        """
        Returns a complete Select Block.
        """
        selblock = self.__header[:]
        selblock.extend(self.__selections)
        return selblock


def byteslen(structure=None):
    length = 0
    for element in structure:
        length = length + len(element)
    return length
