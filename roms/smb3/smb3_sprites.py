"""NES Sprite Reader - Super Mario Brothers 3.

Based on the ROM with MD5 sum:
  bb5c4b6d4d78c101f94bdb360af502f3

Sprite patterns for Super Mario Brothers 3. Loading the sprites places each one
of them into an array. The values below indicate which specific sprites
comprise the overall sprite. The way they are organized is intended to mirror
the structure of the final image. For example:

    EXAMPLE = (
      (0, 1),
      (2, 3),
    )

would indicate that EXAMPLE is comprised of four sprite tiles, and they
should be arranged such that the first 'row' contains sprites 0 and 1 from the
sprite array, and the second row contains sprites 2 and 3.

There are definitely much better ways to do this (such as using an emulator and
tracking down exactly which sprites are use in which situations), but as this
is more of an experiment, this (very, very) manual approach is used. In any
case, many of these follow certain patterns, so this could likely be automated
as well.
"""

# Border for a 4-tile height sprite (in some cases, a sprite ends just at the
# border of a tile, so this adds a little padding if needed).
BORDER = (
  (30,),
  (30,),
  (30,),
  (30,),
)


###############
# SMALL MARIO #
###############
SMALL_MARIO_LEFT = (
  (60, 62),
  (61, 63),
)


#################
# REGULAR MARIO #
#################

# Starts at 5376 (why not the beginning??).
REGULAR_LEFT_RUN_2 = (
  (5376, 5378),
  (5377, 5379),
  (5380, 5382),
  (5381, 5383),
)


#################
# RACCOON MARIO #
#################
RACCOON_LEFT_CROUCH = (
    (52,),
    (53, 54, 55, 56),
)
RACCOON_LEFT_RUN_1 = ()
RACCOON_LEFT_RUN_2 = (
  (0, 2, 30, 30),
  (1, 3, 30, 30),
  (4, 6, 8, 30),
  (5, 7, 9, 30),
)
RACCOON_LEFT_WALK = (
  (10, 12, 30),
  (11, 13, 30),
  # Fix.
  (14, 30, 28),
  (15, 30, 43),
)
RACCOON_LEFT_STAND_TAIL_UP = (
  (44, 46, 30),
  (45, 47, 30),
  (24, 26, 28),
  (25, 27, 29),
)
RACCOON_LEFT_STAND_TAIL_DOWN = (
  (44, 46, 30),
  (45, 47, 30),
  (24, 26, 28),
  (25, 27, 29),
)

# This is probably copied and flipped on the Y-axis in-game.
RACCOON_STRAIGHT_AHEAD = (
  (37,),
  (38,),
  (39,),
)

RACCOON_RIGHT_CROUCH = ()
RACCOON_RIGHT_RUN_1 = ()
RACCOON_RIGHT_RUN_2 = ()
RACCOON_RIGHT_WALK = ()
RACCOON_RIGHT_STAND_TAIL_UP = ()
RACCOON_RIGHT_STAND_TAIL_DOWN = ()

RACCOON_RIGHT_STAND_TAIL_UP = (
  (64, 66, 68, 30),
  (65, 67, 69, 30),
)

RACCOOON_FLY_PREP_1 = ()
RACCOOON_FLY_PREP_1 = ()
RACCOOON_FLY_PREP_1 = ()
RACCOOON_FLY_PREP_1 = ()


#################
# TANOOKI MARIO #
#################

# These start at 4095.
TANOOKI_LEFT_RUN_2 = (
  (4096, 4098, 30, 30),
  (4097, 4099, 30, 30),
  (4100, 4102, 4104, 30),
  (4101, 4103, 4105, 30),
)


################
# HAMMER MARIO #
################

# These start at 4352.
HAMMER_LEFT_RUN_2 = (
  (4352, 4354, 30),
  (4353, 4355, 30),
  (4356, 4358, 30),
  (4357, 4359, 30),
)


##############
# FROG MARIO #
##############

# These start at 5121.
FROG_LEFT_FULL_HOP = (
  (5121, 5123, 30),
  (5124, 5167, 30),
  (5144, 5146, 5148),
  (5145, 5147, 5149),
)

FROG_LEFT_CROUCH = (
  (5120, 5122, 30),
  (5121, 5123, 30),
  (5124, 5126, 5128),
  (5125, 5127, 5129),
)


###########
# ENEMIES #
###########
GHOST = (
  (916, 918),
  (917, 919),
)

GOOMBA = (
  (8186, 8188),
  (8187, 8189),
)


##################
# RANDOM OBJECTS #
##################
MUSIC_BOX = (
  (312, 314),
  (313, 315),
)
