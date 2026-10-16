"""NES planar 8x8 2bpp codec. No game-specific addresses."""
def decode_tile(data):
    if len(data)!=16: raise ValueError('A tile must contain 16 bytes')
    return bytes(((data[y]>>(7-x))&1)|(((data[y+8]>>(7-x))&1)<<1) for y in range(8) for x in range(8))
def encode_tile(pixels):
    if len(pixels)!=64 or any(p>3 for p in pixels): raise ValueError('Invalid tile pixels')
    out=bytearray(16)
    for y in range(8):
        for x in range(8):
            p=pixels[y*8+x];out[y]|=(p&1)<<(7-x);out[y+8]|=((p>>1)&1)<<(7-x)
    return bytes(out)
