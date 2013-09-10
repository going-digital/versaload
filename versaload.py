import struct
import math
from bitstring import BitArray

class Bmc:
    """
    Bmc Biphase Mark Coding

    Generate biphase mark coding streams
    """
    def __init__(self):
        self.__lastState = False
        self.__data = BitArray()

    def add(self,datastream):
        """
        Add datastream
        """
        for b in datastream:
            if self.__lastState:
                if b:
                    self.__data.append('0b00')
                    self.__lastState = False
                else:
                    self.__data.append('0b01')
            else:
                if b:
                    self.__data.append('0b11')
                    self.__lastState = True
                else:
                    self.__data.append('0b10')

    def get(self):
        """
        Return modulated datastream
        """
        return self.__data

class Versaload:
    """
    Versaload

    Build an unmodulated datastream
    """
    def __init__(self, baud=3000):
        self.__blockNumber = 0
        self.__bitstream = BitArray()
        self.__baud = baud
    def __addheader(self):
        self.__bitstream.append('0b0011111111111101')
    def delay(self, time):
        print "Wait ",time
        self.__bitstream.append('0b1'*int(math.ceil((self.__baud*time))))
    def load(self, address, data):
        while len(data) > 0:
            #
            # Split into 256 byte blocks
            #
            print hex(self.__blockNumber),"Load",hex(address)
            dataBlock = data[:0x100]
            #
            # Build header
            #
            length = len(dataBlock) % 256
            dataChecksum = 0
            for byte in list(dataBlock):
                dataChecksum = (dataChecksum + ord(byte)) % 256
            dataChecksum = (256 - dataChecksum) % 256
            header = struct.pack('<HH',self.__blockNumber,address)
            header += struct.pack('<BBB',length,0,dataChecksum)
            headerChecksum = 0
            for byte in list(header):
                headerChecksum = (headerChecksum + ord(byte)) % 256
            headerChecksum = (256 - headerChecksum) % 256
            header += struct.pack('<B',headerChecksum)
            #
            # Generate bitstream
            #
            self.__addheader()
            self.__bitstream.append(BitArray(bytes=header))
            self.__bitstream.append(BitArray(bytes=dataBlock))
            #
            # Prepare for next block
            #
            self.__blockNumber += 1
            data = data[0x100:]
            address = address + 0x100
        self.__bitstream.append('0xff')

    def execute(self, address, execTime):
        print hex(self.__blockNumber),"Exec",hex(address)
        #
        # Build header
        #
        header = struct.pack('<HH',self.__blockNumber, address)
        header += struct.pack('<BBB',0,1,0)
        headerChecksum = 0
        for byte in list(header):
            headerChecksum = (headerChecksum + ord(byte)) % 256
        headerChecksum = (256 - headerChecksum) % 256
        header += struct.pack('<B',headerChecksum)
        #
        # Generate bitstream
        #
        self.__addheader()
        self.__bitstream.append(BitArray(bytes=header))
        self.__bitstream.append('0xff')
        #
        # Add pause to resync after execution
        #
        self.delay(execTime)
        #
        # Prepare for next block
        #
        self.__blockNumber += 1

    def tStatesPerSample(self):
        #
        # For TZX format, assumes 3.5MHz Z80 clock rate
        #
        # Note this is very Sinclair-centric.
        # Amstrad: 4.0MHz Z80 clock rate
        # Commodore: 2.0MHz 6502 clock rate
        #
        return int(round(0.5*3500000/self.__baud))

    def get(self):
        #
        # Modulate bitstream before returning it
        #
        modulated = Bmc()
        modulated.add(self.__bitstream)
        return modulated.get()
