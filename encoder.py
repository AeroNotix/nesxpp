# Implementation of https://wiki.nesdev.com/w/index.php/PPU_pattern_tables

import operator
import os

# Need to turn the encoded form of:

# [[3, 3, 3, 3, 3, 3, 3, 3],
# [3, 1, 3, 3, 3, 1, 3, 3],
# [3, 3, 1, 3, 1, 3, 3, 3],
# [3, 3, 3, 1, 3, 3, 3, 3],
# [3, 3, 1, 3, 1, 3, 3, 3],
# [3, 1, 3, 3, 3, 1, 3, 3],
# [3, 3, 3, 3, 3, 3, 3, 3],
# [3, 3, 3, 3, 3, 3, 3, 3]]

# Into:

# [([1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 0, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 0, 1, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 1, 1, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 0, 1, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 0, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]),
# ([1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1])]
#
# And vice versa
#
# Where a pixel value of 0 is the background and the remaining
# numbers are colours in the current palette. Both bitplanes are
# combined to create the encoded form. We need to separate them back
# out to create the raw CHR file.

NES_BITMAP_DIMENSION = 8
CHR_BANK_SIZE = 4096
SPRITES_IN_CHR_BANK = 256
SINGLE_SPRITE_SIZE = 16


class IncorrectBitmapSize(Exception):
    pass


class IncorrectCHRBankSize(Exception):
    pass


def encode(bitmap):
    if len(bitmap) != NES_BITMAP_DIMENSION and all(lambda row: len(row) == NES_BITMAP_DIMENSION, bitmap):
        raise IncorrectBitmapSize()

    out = []

    for row in bitmap:
        bitplane0 = [0] * NES_BITMAP_DIMENSION
        bitplane1 = [0] * NES_BITMAP_DIMENSION
        for idx, colour in enumerate(row):
            if colour == 1:
                bitplane0[idx] = 1
            if colour == 2:
                bitplane1[idx] = 1
            if colour == 3:
                bitplane0[idx] = 1
                bitplane1[idx] = 1
        out.append((bitplane0, bitplane1))
    return out


def decode(filepath):
    '''Somewhat facerolled'''
    if os.stat(filepath).st_size != CHR_BANK_SIZE:
        raise IncorrectCHRBankSize()
    out = []
    with open(filepath, 'r') as chr_file:
        for x in range(SPRITES_IN_CHR_BANK):
            encoded_sprite = []
            sprite = chr_file.read(SINGLE_SPRITE_SIZE)
            bitplane0 = sprite[0:8]
            bitplane1 = sprite[8:]
            for idx in range(8):
                bp0 = map(int, list('{0:08b}'.format(ord(bitplane0[idx]))))
                # int(x)*2 so we can simply add the two bitplanes
                # together to get the PPU pattern table version
                bp1 = map(lambda x: int(x)*2, list('{0:08b}'.format(ord(bitplane1[idx]))))
                encoded_sprite.append(map(operator.add, bp0, bp1))
            out.append(encoded_sprite)
    return out
