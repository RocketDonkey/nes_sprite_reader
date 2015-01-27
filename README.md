#### NES Sprite Reader

A very basic 'tool' to read sprite data from NES ROMs (well, at least Super
Mario Bros. 3) and either dump them all out or write specific patterns. This is
mostly a learning experiment and therefore is not complete/useful, but if there
is one person out there who finds it useful then it was all worth it.

An example of usage can be found in `example_reader.py`. The general idea is to
import `nes_sprite_reader` into your code and then instantiate an
`NESSpriteReader` with the path to the ROM and the color palette definitions:
```python
rom = nes_sprite_reader.NESSpriteReader(
    './super_mario_3.nes',
    smb3_palettes.PALETTES,
)
```

From there, you can use `rom.DrawSprite(...)` to draw a specific sprite,
`rom.WriteAndNumberAllSprites` to dump a BMP that contains all sprites (with the
beginning of each row numbered, for reference), or `rom.DrawSpriteBlock`, which
will draw a block of sprites (see `roms/smb3/smb3_sprites.py` for an example).
That will let you combine arbitrary sprites, such as:

![alt text][example_bmp]

[example_bmp]: https://github.com/RocketDonkey/nes_sprite_reader/blob/master/example_mario_sprites.bmp "Example BMP"
