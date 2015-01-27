"""NES Sprite Reader - Pull sprites out of an NES ROM.

This already exits in 1,480,208 other places, implemented far better than this
ever will be. Therefore we should make a new one. This is solely for learning
purposes - the general idea is to make it somewhat easy to pull out sprite data
from CHR_ROM and apply palettes. Currently no attempt is made at automatically
determining where palettes are, so the mechanic for specifying them involves:

  1. Locate the addresses for various palettes (using resources such as [1]).
  2. Providing that address to the palette constructors, which will generate the
     palette found at that location in the ROM.

See example_reader.py for an example of how to use.

Resources:
  [1] http://datacrystal.romhacking.net/wiki/Super_Mario_Bros._3:ROM_map
  [2] http://www.emulationzone.org/sections/wakdhacks/docs/sprites.txt
  [3] http://fms.komkon.org/EMUL8/NES.html
  [4] http://www.sonicepoch.com/sm3mix/disassembly.html
  [5] http://nesdev.com/NESDoc.pdf
"""

import binascii
import itertools
import math
import sys

import nes_palette

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


SECTION_SIZE_FORMAT = (
    '| {section: <10}'
    '| {banks: <10}'
    '| 0x{length: <8x}'
    '| 0x{start: <8x}'
    '| 0x{end: <8x}|'
)


DEFAULT_PALETTE = {
    '0': (0xff, 0xff, 0xff),
    '1': (0x75, 0x75, 0x75),
    '2': (0xbc, 0xbc, 0xbc),
    '3': (0x00, 0x00, 0x00),
}


def ConvertToHex(bytes_):
  """Convert a series of bytes into their hexadecimal (integer) equivalent.

  Args:
    bytes_: The bytes to convert.

  Returns:
    The hexadecimal integer represented by the bytes.
  """
  return int(binascii.hexlify(bytes_), 16)


def CompositeSpriteValue(nibble_1, nibble_2):
  """Given two nibbles, return a string representing their composite value.

  A composite value is calculated by comparing each bit of the bytes, and
  assigning different values based on the states:

    * 0 and 0 -> 0
    * 0 and 1 -> 1
    * 1 and 0 -> 2
    * 1 and 1 -> 3

  Args:
    nibble_1: A zero-padded 4-bit string (e.g. 0011).
    nibble_2: A zero-padded 4-bit string (e.g. 0011).

  Returns:
    A string containing the mapped value for each pair.
  """
  return ''.join(str(int(n1+n2, 2)) for n1, n2 in zip(nibble_1, nibble_2))


def GetSpriteSize(sprite):
  """Given a sprite comprised of multiple tiles, calculate the size in pixels.

  Args:
    sprite: An iterable of iterables containing the sprite tiles that make up
        the sprite. See roms/smb3/smb3_sprites for examples.

  Returns:
    A tuple of the form (width, height), where width is the pixel width of the
        combined sprite, and height is the pixel height.
  """
  return len(max(sprite, key=len))*8, len(sprite)*8


def GetBlockSize(sprite_block):
  """Given a sprite block, calculate the size in pixels.

  Args:
    sprite: An iterable of iterables containing the sprite tiles that make up
        the sprite. See roms/smb3/smb3_sprites for examples.

  Returns:
    A tuple of the form (width, height), where width is the pixel width of the
        combined sprite, and height is the pixel height.
  """
  img_width = img_height = 0
  for block_row in sprite_block:
    row_width = col_height = 0
    # Ignore the palette.
    for sprite, _ in block_row:
      sprite_width, sprite_height = GetSpriteSize(sprite)
      row_width += sprite_width

      # The height of the row is the height of the tallest sprite.
      if sprite_height > col_height:
        col_height = sprite_height

    # If this row is longer than the longest observed row, widen img_width.
    if row_width > img_width:
      img_width = row_width

    # Increase the overall height.
    img_height += col_height

  return (img_width, img_height)


def MaybeEnlargeImage(img, width, height, x_val, y_val):
  """Enlarge an Image if there is not enough space to write the sprite.

  In the case where an Image is being iteratively built, it may be the case that
  the Image isn't large enough to contain the next sprite. In that case,
  calculate the required size and return the newly enlarged Image.

  Args:
    img: The Image instance.
    width: The width (in pixels) of the data to write.
    height: The height (in pixels) of the data to write.
    x_val: The integer x-coordinate at which the data will be written.
    y_val: The integer y-coordinate at which the data will be written.

  Returns:
    An Image instance that is large enough to contain the new data.
  """
  img_width, img_height = img.size
  max_width = max(img_width, width + x_val)
  max_height = max(img_height, height + y_val)

  if (max_height > img_height) or (max_width > img_width):
    # NOTE: When DrawSprite is invoked as part of a large loop, this could
    # incur quite a few resizes. Therfore in that situation, it would be best
    # to create a large canvas and then crop before writing. This would avoid
    # numerous resizes.
    enlarged_image = Image.new(img.mode, (max_width, max_height), 'white')
    enlarged_image.paste(img, (0, 0))
    img = enlarged_image.copy()
    del enlarged_image

  return img


class NESSpriteReader(object):
  """Container for an NESSpriteReader.

  Args:
    file_path: The path to the .nes ROM to be loaded.
    palettes: A dictionary of the form {name: palette_address}, where
        palette_address is the address of the 4-byte sequence representing the
        palette (see smb3/smb3_palettes.py for an example).
  """

  def __init__(self, file_path, palettes=None):
    with open(file_path, 'rb') as f:
      self._file_data = f.read()

    # Header data.
    self.constant = self._file_data[:4]
    self.prg_banks = ConvertToHex(self._file_data[4])
    self.chr_banks = ConvertToHex(self._file_data[5])
    self.flags_6 = ConvertToHex(self._file_data[6])
    self.flags_7 = ConvertToHex(self._file_data[7])
    self.prg_ram_size = ConvertToHex(self._file_data[8])
    self.flags_9 = ConvertToHex(self._file_data[9])
    self.flags_10 = ConvertToHex(self._file_data[0xA])
    self.zero_fill = ConvertToHex(self._file_data[0xA:0xF])

    # Start addresses / lengths.
    header_length = 16
    self.prg_length = self.prg_banks * 16384
    self.chr_length = self.chr_banks * 8192

    self.prg_start = header_length
    self.chr_start = header_length + self.prg_length

    self.chr_data = self._file_data[
        self.chr_start:self.chr_start+self.chr_length]

    # Read all sprites from chr_data. As described elsewhere, sprites are 16
    # bytes each, so read in steps of 16.
    self.sprites = []
    for index in range(0, self.chr_length, 16):
      self.LoadSprite(self.chr_data[index:index+16])

    # Load the color palettes.
    self.palettes = {}
    if palettes:
      self.LoadPalettes(palettes)

  def PrintHeaderData(self):
    """Print the ROM's header data.

    The header is structure as follows:

    0x0          0x4          0x8          0xc
    +------------+------------+------------+------------+
    | NES\x1a    | PC CC F6 F7| RS F9 F10 Z| Z Z Z Z    |
    +------------+------------+------------+------------+

    0x0: Constant (4e45531a = 'NES\x1a').
    0x4: PRG_ROM - Number of PRG banks, which is what contains the executable
        code of the ROM. Each bank is exactly 16K (16,384 bytes).
    0x5: CHR_ROM - Number of CHR banks, which contain the sprites (character
        data). Each bank is exactly 8K (8,192 bytes). Each bank can contain up
        to 512 sprites, and each sprite is stored in 16 bytes. Note that this
        isn't true for all sprites (such as the ones that are stored in the PRG
        banks), but is is true for our case.
    0x6: Flags 6.
    0x7: Flags 7.
    0x8: PRG_RAM_SIZE.
    0x9: Flags 9.
    0xa: Flags 10.
    0xb-0xf: Zero fill.
    """
    print '+{:-^30}+'.format('')
    print '|{: ^30}|'.format('Header Section')
    print '+{:-^30}+'.format('')
    print '| 0x0 Constant : {: <14}|'.format(binascii.hexlify(self.constant))
    print '| 0x4 PRG Banks: {: <14}|'.format(self.prg_banks)
    print '| 0x5 CHR Banks: {: <14}|'.format(self.chr_banks)
    print '| 0x6 Flags 6  : {: <14}|'.format(self.flags_6)
    print '| 0x7 Flags 7  : {: <14}|'.format(self.flags_7)
    print '| 0x8 PRG RAM  : {: <14}|'.format(self.prg_ram_size)
    print '| 0x9 Flags 9  : {: <14}|'.format(self.flags_9)
    print '| 0xa Flags 10 : {: <14}|'.format(self.flags_10)
    print '| 0xb Zero Fill: {: <14}|'.format(self.zero_fill)
    print '+{:-^30}+'.format('')
    print

    print '+{:-^59}+'.format('')
    print ('|' + ' {: <10}|'*5).format(
        'Section', 'Banks', 'Length', 'Start', 'End')
    print '+{:-^59}+'.format('')

    print SECTION_SIZE_FORMAT.format(
        section='PRG ROM',
        banks=self.prg_banks,
        length=self.prg_length,
        start=self.prg_start,
        end=self.prg_start+self.prg_length,
    )
    print SECTION_SIZE_FORMAT.format(
        section='CHR ROM',
        banks=self.chr_banks,
        length=self.chr_length,
        start=self.chr_start,
        end=self.chr_start+self.chr_length,
    )
    print '+{:-^59}+'.format('')

  def LoadSprite(self, sprite_data):
    """Load a specific sprite and store its representation.

    Each sprite is represented by two 8-byte channels (16 total bytes) that are
    overlayed on top of each other to create the final sprite using the
    following algorithm:

    channel_a
    * Split each byte into the high bits and low bits (4 each).
    * Convert each piece into its binary equivalent.

    channel_b
    * Perform the same operation as with channel_a, but instead 'combine' with
      channel_a, creating a composite bit using the following logic:
      - ca=0, cb=0 -> 0
      - ca=0, cb=1 -> 1
      - ca=1, cb=0 -> 2
      - ca=1, cb=1 -> 3

    The resulting sprite will be stored in self.sprites.

    Args:
      sprite_data: The 16-bytes representing a given sprite.
    """
    channel_a = binascii.hexlify(sprite_data[:8])
    channel_b = binascii.hexlify(sprite_data[8:16])

    # As each channel contains 8 bytes but we are iterating through the hex
    # representation, pull two bytes at a time.
    sprite = []
    for position in range(0, 16, 2):
      # Create a single 8-bit 'row'.
      ca_byte = channel_a[position:position+2]
      cb_byte = channel_b[position:position+2]

      # Break apart the high and low components.
      hi_a, low_a = ca_byte
      hi_b, low_b = cb_byte

      # Convert the bytes into their 4-bit string representation (0-padded).
      # This could all be simplified by using comprehensions, but this is more
      # explicit and easier for me to follow.
      hi_a_bin = '{:04b}'.format(int(hi_a, 16))
      hi_b_bin = '{:04b}'.format(int(hi_b, 16))
      low_a_bin = '{:04b}'.format(int(low_a, 16))
      low_b_bin = '{:04b}'.format(int(low_b, 16))

      # Store the row.
      sprite.append(
          CompositeSpriteValue(hi_a_bin, hi_b_bin) +
          CompositeSpriteValue(low_a_bin, low_b_bin)
      )

    self.sprites.append(sprite)

  def LoadPalettes(self, palettes):
    """Load the color palettes for this ROM.

    Args:
      palettes: A dictionary of the form {name: palette_address}, where
          palette_address is the address of the 4-byte sequence representing the
          palette (see smb3/smb3_palettes.py for an example).
    """
    for palette_name, address in palettes:
      palette_bytes = self._file_data[address:address+0x4]

      # Note that the values for keys 1 and 2 are 'switched'.
      self.palettes[palette_name] = {
          '0': nes_palette.NES_PALETTE[palette_bytes[0]],
          '1': nes_palette.NES_PALETTE[palette_bytes[2]],
          '2': nes_palette.NES_PALETTE[palette_bytes[1]],
          '3': nes_palette.NES_PALETTE[palette_bytes[3]],
      }

  def DrawSprite(self, img=None, sprites=None, palette=None, x_val=0, y_val=0):
    """Draw a sprite at a position on an image.

    Args:
      img: The Image instance to which to write the sprite. If no Image is
          provided, a new one will be created.
      sprites: An iterable of iterables, where each inner iterable contains index
          numbers of sprites to draw. E.g [(1, 2), (3, 4)] represents a sprite
          that is composed of sprites 1, 2, 3 and 4, with 1 and 2 on top and 3 and
          4 below them.
      palette: A dictionary containing the palette data for this sprite.
      x_val: The x-coordinate of the point at which to write the sprite.
      y_val: The y-coordinate of the point at which to write the sprite.

    Returns:
      The Image instance with the new sprite written.
    """
    width, height = GetSpriteSize(sprites)

    if img is None:
      img = Image.new('RGB', (width+x_val, height+y_val), 'white')
    else:
      # Make sure the image has enough space - if not, enlarge it.
      img = MaybeEnlargeImage(img, width, height, x_val, y_val)

    if palette is None:
      palette = DEFAULT_PALETTE.copy()

    for block_row_index, row in enumerate(sprites):
      for block_col_index, sprite_number in enumerate(row):
        # This is now a single sprite to write, so pull its data.
        sprite = self.sprites[sprite_number]
        for sprite_row_index, sprite_row in enumerate(sprite):
          for sprite_col_index, value in enumerate(sprite_row):
            # The coordinate values are the sum of the current index of the
            # sprite (which will be between 0-7), plus 8x the current position
            # in the sprite block (to make sure that sprites are properly offset
            # from each other), plus any initial x/y starting coordinates.
            x_coord = x_val+sprite_col_index+(block_col_index*8)
            y_coord = y_val+sprite_row_index+(block_row_index*8)
            img.putpixel((x_coord, y_coord), palette[value])

    return img

  def DrawSpriteBlock(self, img=None, sprite_block=None):
    """Draw a block of sprites.

    A block of sprites is defined as an iterable of iterables, where the 'outer'
    iterable contains the sprites to be written on that row, and the 'inner'
    iterable contains the sprites themselves (which will be written one after
    another). Each item in the inner iterable is a tuple of the form
    (sprite, palette). See example_reader.py for an example.

    Args:
      img: A PIL.Image instance (or None, in which case a new Image will be
          created).
      sprite_block: An iterable of iterables, where each inner iterable contains
          tuples of the form (sprite, palette).

    Returns:
      The Image instance with the block of sprites drawn.
    """
    img_width, img_height = GetBlockSize(sprite_block)

    if img is None:
      img = Image.new('RGB', (img_width, img_height), 'white')

    last_sprite_width = 0
    last_sprite_height = 0
    for row_idx, sprite_row in enumerate(sprite_block):
      for sprite_idx, (sprite, palette) in enumerate(sprite_row):
        img = self.DrawSprite(
            img, sprite, palette,
            x_val=last_sprite_width,
            y_val=last_sprite_height,
        )
        last_sprite_width += (len(max(sprite, key=len))*8)
      last_sprite_height += 32
      last_sprite_width = 0

    return img

  def WriteAndNumberAllSprites(
      self, file_name='all_sprites.bmp', palette=None, per_row=10):
    """Output the entire set of sprites in rows of 10, numbering each row.

    The primary use for this is to generate an image containing all of the
    sprites with garish numbers at the beginning of each row that represent the
    index of the first sprite in the sprite array.

    Args:
      file_name: The name of the output file.
      palette: A dictionary of the form {'num': (R, G, B)}, where 'num' is a
          string representing a number from 0-3, and (R, G, B) is a tuple
          containing the integer RGB values for each key. If no palette is
          provided, a simple grey will be used.
      per_row: The number of sprite tiles to print on each row (default: 10).
    """
    height = ((len(self.sprites) / per_row) + 1) * 8

    img = Image.new('RGB', (8*per_row, height), 'white')
    draw = ImageDraw.Draw(img)
    # TODO: We need a bitmapped font so that it is legible. Since the sprite
    # tiles are small, most fonts are completely illegible. For now, we write
    # the tile number at the beginning of each row - less convenient but more
    # portable (for now).
    # font = ImageFont.truetype(
    #     '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-ExtraLight.ttf',
    #     size=4,
    # )
    font = ImageFont.load_default()

    if palette is None:
      palette = DEFAULT_PALETTE.copy()

    for row_index in xrange(0, len(self.sprites), per_row):
      # Tiles are 8 pixels tall, so this calculates the proper y-offset
      # regardless of the per_row number chosen.
      y_offset = (row_index/per_row) * 8

      # On each row, print as many sprites as specified in per_row.
      for col_index in xrange(per_row):
        # This is wrapped in a try/except solely to handle the final row of
        # sprites. An index error will be raised when there are no additional
        # sprites to load, so since this will only occur once, this is the
        # kindest on performance.
        try:
          # The syntax for referencing the sprite to draw is ugly.
          self.DrawSprite(
              img, [[row_index+col_index]], palette,
              x_val=col_index*8,
              y_val=y_offset,
          )
        except IndexError:
          break
      # Write the number of the first tile in the row. Write after the tiles are
      # drawn so that the text doesn't get covered by the tile. Use a garish
      # green for no good reason other than it is green.
      draw.text((0, y_offset), str(row_index), (0, 255, 0), font=font)

    img.save(file_name)
