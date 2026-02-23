"""
Encodes a 30x30 pixel image into bitstream following custom 32-bit instruction set.

Refer to SETUP.md for usage.
"""


import os
import struct
from PIL import Image


IMAGE_PATH = 'maze.png'
BITSTREAM_PATH = 'maze_v2.bin'


class MazeInstruction:
    """Parses pixel information to custom instruction"""

    #OPCODES
    BUILD_WALL = 0x1
    PLACE_ENT = 0x2

    #ENTITY (RGB)
    STARTPOINT = (0, 183, 239)
    ENDPOINT = (237, 28, 36)
    HEART = (34, 177, 80)
    GEM = (255, 242, 0)
    MONSTER = (111, 49, 152)
    MONSTER_FACING = (181, 165, 213)

    #FUNCTION1 (ENTITY), 1-HOT
    SPEP_FUNCT1 = 0x1
    HEART_FUNCT1 = 0x2
    GEM_FUNCT1 = 0x4
    MONSTER_FUNCT1 = 0x8

    #FUNCTION2 (ENTITY TYPE), 1-HOT
    SP_FUNCT2 = 0x1
    EP_FUNCT2 = 0x2

    #FUNCTION3 (ROTATION), 1-HOT
    NORTH = 0x1
    EAST = 0x2
    SOUTH = 0x4
    WEST = 0x8


    def __init__(self, path=IMAGE_PATH):
        """Init Read Write"""

        self.bitstream = []
        self.script_dir = os.path.dirname(__file__)
        self.image_path = os.path.join(self.script_dir, path)
        self.img = Image.open(self.image_path).convert('RGB')
    
    def _gen_wall(self, x, y):
        """Generate Walls if Black, logs L/R half"""

        if self.img.getpixel((x,y)) == (0, 0, 0):
            if x > 14:
                self.data_right |= (1 << (14 - (x - 15)))
            else:
                self.data_left |= (1 << (14-x))

    def _gen_entity(self, x, y):
        """Instructions for place entity opcode"""

        instr = 0
        match self.img.getpixel((x,y)):
            case self.STARTPOINT:
                instr = (
                    (y << 24) 
                    | (x << 16) 
                    | (self.SPEP_FUNCT1 << 12) 
                    | (self.SP_FUNCT2 << 8) 
                    | (self.NORTH << 4) 
                    | self.PLACE_ENT
                )
            case self.ENDPOINT:
                instr = (
                    (y << 24) 
                    | (x << 16) 
                    | (self.SPEP_FUNCT1 << 12) 
                    | (self.EP_FUNCT2 << 8) 
                    | (self.NORTH << 4) 
                    | self.PLACE_ENT
                )
            case self.HEART:
                instr = (
                    (y << 24) 
                    | (x << 16) 
                    | (self.HEART_FUNCT1 << 12) 
                    | (0x1 << 8) 
                    | (self.NORTH << 4) 
                    | self.PLACE_ENT
                )
            case self.GEM:
                instr = (
                    (y << 24) 
                    | (x << 16) 
                    | (self.GEM_FUNCT1 << 12) 
                    | (0x1 << 8) 
                    | (self.NORTH << 4) 
                    | self.PLACE_ENT
                )
            case self.MONSTER:
                orientation = self.NORTH
                direction = [
                    ((0, -1), self.NORTH),
                    ((1, 0),  self.EAST),
                    ((0, 1),  self.SOUTH),
                    ((-1, 0), self.WEST)
                ]

                for (dx, dy), ori in direction:
                    nx, ny = x + dx, y + dy
                    if self.img.getpixel((nx,ny)) == self.MONSTER_FACING:
                        orientation = ori
                
                instr = (
                    (y << 24) 
                    | (x << 16) 
                    | (self.MONSTER_FUNCT1 << 12) 
                    | (0x1 << 8) 
                    | (orientation << 4) 
                    | self.PLACE_ENT
                )
        if instr:
            self.bitstream.append(instr)

    def generate_bitstream(self, path=BITSTREAM_PATH):
        """Main function for bitstream generation"""

        self.bin_path = os.path.join(self.script_dir, path)
        for y in range(30):
            self.data_left = 0
            self.data_right = 0
            for x in range(30):
                self._gen_wall(x, y)
                self._gen_entity(x, y)
            instr_1 = ((self.data_left) << 16) | (0x0 << 12) | (y << 4) | self.BUILD_WALL
            instr_2 = ((self.data_right) << 16) | (0xF << 12) | (y << 4) | self.BUILD_WALL
            self.bitstream.append(instr_1)
            self.bitstream.append(instr_2)
            
        binary_data = struct.pack(f'>{len(self.bitstream)}I', *self.bitstream)
        with open(self.bin_path, "wb") as f:
            f.write(binary_data)

if __name__ == "__main__":
    encoder = MazeInstruction(IMAGE_PATH)
    encoder.generate_bitstream(BITSTREAM_PATH)