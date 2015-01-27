"""Super Mario Bros. 3 - Color Palettes.

Based on the ROM with MD5 sum:
  bb5c4b6d4d78c101f94bdb360af502f3

The color palettes are defined in assorted areas across memory, which is very
helpfully laid out by [1]. An example entry:

    10539-1053C sm/big/rac Mario Palette

Means that the the four bytes representing the palette for Small/Big/Raccoon
Mario can be found at 0x10539. This looks like:

    $ xxd -s 0x10539 -l 0x4 -p super_mario_3.nes
    0016360f

Each byte maps to the NES_PALETTE below (from [2]). It seems like the second
and third bytes are 'switched', so the following mapping is used:

    0 |2 |1 |3
    --|--|--|-
    00|16|36|0f

Where 0-3 are the digits calculated from overlaying the two 8-byte channels
from the sprite.

Uber-valuable resources:
    [1] http://datacrystal.romhacking.net/wiki/Super_Mario_Bros._3:ROM_map
    [2] http://nesdev.com/NESDoc.pdf
"""

PALETTES = (
    ('regular_mario_palette', 0x10539),
    ('regular_luigi_palette', 0x1053d),
    ('fire_mario_palette', 0x10541),
    ('frog_mario_palette', 0x10549),
    ('tanooki_mario_palette', 0x1054d),
    ('hammer_mario_palette', 0x10551),
    ('lava_palette', 0x36daa),
    ('bowser_palette', 0x36dfe),
)
