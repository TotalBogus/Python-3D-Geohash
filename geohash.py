# based on the C examples from
# https://www.forceflow.be/2013/10/07/morton-encodingdecoding-through-bit-interleaving-implementations/

# A 3D (MSB first) morton key is of the form: (a1, b1, c1), (a2, b2, c2), (a3, b3, c3)
# where a, b, and c are all the integers to be interleaved and (a1, b1, c1)
# is an octet of all the MSBs of the three integers a, b, and c
# the magic morton number (0x249249) is the interleaving pattern 0b1001001001001001001001
# all patterns are limited to only 63 bits, higher order bits aren't used anyway
# the 18 hash tables take up about 120kB of space but are much faster than raw code
# Both encodeing and decoding takes under 500ns on a 13900K

# get all subsets of the magic morton number between 0 and 2**22 - 1
x3e = {i:m for i, m in enumerate(sorted(set([i & 0x249249 for i in range(0, 2**22)])))}
y3e = {i:m<<1 for i, m in x3e.items()} # y-axis bits are shifted up by one vs the x-axis
z3e = {i:m<<2 for i, m in x3e.items()} # z-axis bits are shifted up one more again

x2e = {i<<8:(m << 24) for i, m in x3e.items()} # next input byte up (i<<8)
y2e = {i<<8:(m << 24) for i, m in y3e.items()} # next output hash word up (m<<24)
z2e = {i<<8:(m << 24) for i, m in z3e.items()}

x1e = {i<<16:(m << 48) & (2**63)-1 for i, m in x3e.items() if i < 32} # only first 32 entries are needed
y1e = {i<<16:(m << 48) & (2**63)-1 for i, m in y3e.items() if i < 32} # the rest are never used in a 63b hash
z1e = {i<<16:(m << 48) & (2**63)-1 for i, m in z3e.items() if i < 32} # *AND* they'd create hash colisions anyway

x3d = {v:k for k,v in x3e.items()} # inverse morton lookup tables for each byte
y3d = {v:k for k,v in y3e.items()}
z3d = {v:k for k,v in z3e.items()}

x2d = {v:k for k,v in x2e.items()}
y2d = {v:k for k,v in y2e.items()}
z2d = {v:k for k,v in z2e.items()}

x1d = {v:k for k,v in x1e.items()}
y1d = {v:k for k,v in y1e.items()}
z1d = {v:k for k,v in z1e.items()}

def encode(x, y, z):
    """
    Encodes a 3D floating-point vector to a 63b morton key
    Each vector *MUST* be between (-1.0, -1.0, -1.0) and (1.0, 1.0, 1.0)
    """
    # Axes are converted to 21 bit, unsigned integers
    # their bits are then interleaved as (z, y, x) and
    # the result is a single 63 bit, unsigned integer
    
    xi = int(0x100000*x + 0x100000 + 0.5) # (-1.0, 1.0) -> (0, 2**21)
    yi = int(0x100000*y + 0x100000 + 0.5) # i.e. ((f + 1) * 2**20) + 0.5
    zi = int(0x100000*z + 0x100000 + 0.5) # +0.5 fixes an fp math rounding error
    
    h1 = x1e[xi & 0xff0000] | y1e[yi & 0xff0000] | z1e[zi & 0xff0000]
    h2 = x2e[xi & 0xff00]   | y2e[yi & 0xff00]   | z2e[zi & 0xff00]
    h3 = x3e[xi & 0xff]     | y3e[yi & 0xff]     | z3e[zi & 0xff]
    
    return h1 | h2 | h3

def decode(hash):
    """Convert a 3D morton key back into a 3D vector"""
    # All bitwise ANDs below are using shifted (and 63b clipped) versions of the magic 3D morton number
    # 9.5367431640625e-07 is (thankfully) exactly equal to 1 / 2**20
    x = x1d[hash & 0x1249000000000000] | x2d[hash & 0x249249000000]  | x3d[hash & 0x249249]
    y = y1d[hash & 0x2492000000000000] | y2d[hash & 0x492492000000]  | y3d[hash & 0x492492]
    z = z1d[hash & 0x4924000000000000] | z2d[hash & 0x924924000000]  | z3d[hash & 0x924924]
    
    return x * 9.5367431640625e-7 - 1, y * 9.5367431640625e-7 - 1, z * 9.5367431640625e-7 - 1
