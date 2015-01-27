"""NES Sprite Reader - Example using Super Mario Brothers 3.

A simple example of how to use the SpriteReader, which involves loading in a
ROMs sprite map and palettes and then writing the sprites.
"""

from roms.smb3 import smb3_sprites
from roms.smb3 import smb3_palettes

import nes_sprite_reader


def main():
  """Read an NES ROM (in .nes format)."""
  # Load the target ROM.
  rom = nes_sprite_reader.NESSpriteReader(
      './super_mario_3.nes',
      smb3_palettes.PALETTES,
  )

  # Print the ROM's header data.
  rom.PrintHeaderData()

  # Write all of the sprites to an output file. This can be used to visually
  # inspect the layout and build new sprite mappings.
  rom.WriteAndNumberAllSprites(
      per_row=10,
      palette=rom.palettes['regular_mario_palette'],
  )

  # Write a BMP using a sprite mapping from smb3_sprites. 'None' is passed as
  # the img argument, which means a new Image will be created; otherwise, an
  # Image instance can also be passed.
  rom.DrawSprite(
      img=None,
      sprites=smb3_sprites.RACCOON_LEFT_RUN_2,
      palette=rom.palettes['regular_mario_palette'],
  ).save('example_mario_single_sprite.bmp')

  # Create a single BMP comprised of multiple sprites from smb3_sprites. The
  # input is an iterable of iterables, where the 'outer' iterable contains
  # the sprites to be written on that row, and the 'inner' iterable contains
  # the sprites themselves (which will be written one after another).
  #
  # This creates a BMP that Mario in his various forms on the top level, with a
  # bottom comprised of alternating Goombas/small Marios, with the small Marios
  # using different palettes (most of which small Mario can't use during the
  # game).
  sprite_block = (
      (
        (smb3_sprites.REGULAR_LEFT_RUN_2,
         rom.palettes['regular_mario_palette']),
        (smb3_sprites.BORDER,
         rom.palettes['regular_mario_palette']),
        (smb3_sprites.REGULAR_LEFT_RUN_2,
         rom.palettes['fire_mario_palette']),
        (smb3_sprites.BORDER,
         rom.palettes['regular_mario_palette']),
        (smb3_sprites.RACCOON_LEFT_RUN_2,
         rom.palettes['regular_mario_palette']),
        (smb3_sprites.TANOOKI_LEFT_RUN_2,
         rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.HAMMER_LEFT_RUN_2,
         rom.palettes['hammer_mario_palette']),
        (smb3_sprites.FROG_LEFT_FULL_HOP,
         rom.palettes['frog_mario_palette']),
      ),
      (
        (smb3_sprites.GOOMBA, rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.SMALL_MARIO_LEFT, rom.palettes['regular_mario_palette']),
        (smb3_sprites.GOOMBA, rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.SMALL_MARIO_LEFT, rom.palettes['fire_mario_palette']),
        (smb3_sprites.GOOMBA, rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.SMALL_MARIO_LEFT, rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.GOOMBA, rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.SMALL_MARIO_LEFT, rom.palettes['hammer_mario_palette']),
        (smb3_sprites.GOOMBA, rom.palettes['tanooki_mario_palette']),
        (smb3_sprites.SMALL_MARIO_LEFT, rom.palettes['regular_luigi_palette']),
      ),
  )
  rom.DrawSpriteBlock(
      img=None,
      sprite_block=sprite_block,
  ).save('example_mario_sprites.bmp')


if __name__ == '__main__':
  main()
