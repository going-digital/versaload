from bitstring import BitArray

"""
Optimise screen

This flips screen characters, swapping INK and PAPER to minimise the amount
of INK on the screen. This makes the initial attributes more closely represent
the final screen.
"""
def optimiseScr(data):
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
            if pixelData.count(1) >= 32:
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
