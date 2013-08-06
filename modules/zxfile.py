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
from struct import pack, unpack
from operator import xor

# Spectrum Values
SPEC_FILE_PROG = 0
SPEC_FILE_NARR = 1
SPEC_FILE_CARR = 2
SPEC_FILE_CODE = 3
SPEC_FLAG_HEAD = 0
SPEC_FLAG_DATA = 0xFF


# Header elements are:
# 0 - File type
# 1 - File name (always exactly 10 bytes, space padded)
# 2 - Data block length
# 3 - File parameter 1
# 4 - File parameter 2
# Flag byte and checksum are held separately because they
# are not in the XOR checksum calculation
class ZX_FileHdr:
    """
    Spectrum File Header.

    A class which defines the layout of a spectrum file header.
    """
    def __init__(self, ftype=SPEC_FILE_PROG, fname='EMPTY NAME', dblen=0, par1=0, par2=0):
        self.__header = range(5)
        self.__flag = SPEC_FLAG_HEAD
        self.__cksum = 0
        self.filetype(ftype)
        self.filename(fname)
        self.setdatalen(dblen)
        self.param1(par1)
        self.param2(par2)

    def filetype(self, ftype=None):
        """
        Sets and returns the spectrum file type.

        'ftype' should be one of the following variables or 'None':
            SPEC_FILE_PROG      : Usually a BASIC program. [Program:]
            SPEC_FILE_NARR      : Number array. [Number array:]
            SPEC_FILE_CARR      : Character array. [Character array:]
            SPEC_FILE_CODE      : Block of code or SCREEN$. [Bytes:]

        If 'ftype' is 'None' then the file type is not changed but the current file
        type is still returned.
        """
        if ftype is not None:
            self.__header[0] = pack('<B', ftype)
        return unpack('<B', self.__header[0])[0]

    def setdatalen(self, dlen=None):
        """
        Sets and returns the data block length.

        The data block length should be the size of the data in bytes, in the
        corresponding spectrum data section (see ZX_FileData class). It should be
        between 0 and 65535 bytes inclusive.

        If 'dlen' is 'None' the current value is returned and no change is made.
        """
        if dlen is not None:
            self.__header[2] = pack('<H', dlen)
        # Unpack always returns a tuple, hence the [0]
        return unpack('<H', self.__header[2])[0]

    def filename(self, fname=None):
        """
        Sets and returns the spectrum filename.

        'fname' will be truncated or extended to 10 characters by padding with
         spaces in order to be a valid spectrum file name.

         If 'fname' is 'None' the current value is returned and no change is made.
        """
        if fname is not None:
            # Filenames are ALWAYS 10 chars, space padded if necessary so ensure it
            fname = fname.ljust(10)
            fname = fname[:10]
            self.__header[1] = fname
        return self.__header[1]

    def param1(self, par1=None):
        """
        Sets and returns the first file parameter.

        The exact meaning of the first file parameter depends upon the file's type.
        Quoting from http://www.worldofspectrum.org/faq/reference/48kreference.htm:

        "If the file is a PROGRAM file, parameter 1 holds the autostart line number (or
        a number >=32768 if no LINE parameter was given) and parameter 2 holds the
        start of the variable area relative to the start of the program. If it's a CODE
        file, parameter 1 holds the start of the code block when saved, and parameter 2
        holds 32768."

        If 'par1' is 'None' the current value is returned and no change is made.
        """
        if par1 is not None:
            self.__header[3] = pack('<H', par1)
        return unpack('<H', self.__header[3])[0]

    def param2(self, par2=None):
        """
        Sets and returns the second file parameter.

        The exact meaning of the second file parameter depends upon the file's type.
        Quoting from http://www.worldofspectrum.org/faq/reference/48kreference.htm:

        "If the file is a PROGRAM file, parameter 1 holds the autostart line number (or
        a number >=32768 if no LINE parameter was given) and parameter 2 holds the
        start of the variable area relative to the start of the program. If it's a CODE
        file, parameter 1 holds the start of the code block when saved, and parameter 2
        holds 32768."

        If 'par2' is 'None' the current value is returned and no change is made.
        """
        if par2 is not None:
            self.__header[4] = pack('<H', par2)
        return unpack('<H', self.__header[4])[0]

    def get(self):
        """
        Returns a complete spectrum file header.
        """
        # Always ensure checksum is up to date before returning data
        self.__calccksum()
        # Return everything as a list
        zxfilehdr = [pack('<B', self.__flag)]
        zxfilehdr.extend(self.__header)
        zxfilehdr.extend([pack('<B', self.__cksum)])
        return zxfilehdr

    # Calculate the XOR checksum (each individual byte has to be XORed)
    # Caution: Unlike spectrum file data, the flag *IS NOT* part of the checksum
    def __calccksum(self):
        self.__cksum = 0
        for element in self.__header:
            for byte in element:
                self.__cksum = xor(self.__cksum, ord(byte))


class ZX_FileData:
    """
    Spectrum File Data

    A class which defines spectrum file data layout.
    """
    def __init__(self, data=None):
        self.__flag = SPEC_FLAG_DATA
        self.__data = []
        self.__cksum = 0
        if data is not None:
            self.encapsulate(data)

    def encapsulate(self, data):
        """
        Encapsulates a block of data into a spectrum data section.

        If the calculated size of the 'data' in bytes is greater than 65535 then it
        will return a value of 1 and the data will not be encapsulated. A return value
        of 'None' means success. This method replaces any data that has previously been
        encapsulated.
        """
        if (byteslen(data) > 65535):
            return 1
        else:
            self.__data = data[:]

    def datalen(self):
        """
        Returns the size of the encapsulated data in bytes.
        """
        length = 0
        for element in self.__data:
            length = length + len(element)
        return length

    def get(self):
        """
        Returns a complete spectrum file data layout.
        """
        # Always ensure checksum is up to date before returning data
        self.__calccksum()
        # Return everything as a list
        zxfiledata = [pack('<B', self.__flag)]
        zxfiledata.extend(self.__data)
        zxfiledata.extend([pack('<B', self.__cksum)])
        return zxfiledata

    # Calculate the XOR checksum (each individual byte has to be XORed)
    # Caution: Unlike a spectrum file header, the flag *IS* part of the checksum
    def __calccksum(self):
        # Calculate the XOR checksum (each individual byte has to be XORed)
        self.__cksum = self.__flag
        for element in self.__data:
            for byte in element:
                self.__cksum = xor(self.__cksum, ord(byte))


def byteslen(structure=None):
    length = 0
    for element in structure:
        length = length + len(element)
    return length
