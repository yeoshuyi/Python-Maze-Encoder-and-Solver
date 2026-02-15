"""
Takes in binary file encoded by maze_encoder.py
"""


import struct
import os
from PIL import Image, ImageDraw
from collections import deque


BITSTREAM_PATH = 'maze.bin'
GIF_PATH = 'maze_solve.gif'


class MazeSolver:
    def __init__(self, path=BITSTREAM_PATH):
        self.script_dir = os.path.dirname(__file__)
        self.bin_path = os.path.join(self.script_dir, path)
        self.grid = [[0 for _ in range(30)] for _ in range(30)]
        self.start_pos = None
        self.end_pos = None
        self.frames = []

    def _parse_bin(self):
        with open(self.bin_path, "rb") as f:
            data = f.read()
            count = len(data) // 4
            instructions = struct.unpack(f'>{count}I', data)

        for instr in instructions:
            opcode = instr & 0xF
            if opcode == 0x1:
                y = (instr >> 4) & 0xFF
                half = (instr >> 12) & 0xF
                pixel_data = (instr >> 16) & 0x7FFF
                
                for i in range(15):
                    if pixel_data & (1 << (14 - i)):
                        x = i if half == 0 else i + 15
                        if 0 <= x < 30 and 0 <= y < 30:
                            self.grid[y][x] = 1
            
            elif opcode == 0x2:
                y = (instr >> 24) & 0xFF
                x = (instr >> 16) & 0xFF
                funct2 = (instr >> 8) & 0xF
                if funct2 == 0x1: self.start_pos = (x, y)
                elif funct2 == 0x2: self.end_pos = (x, y)

    def _draw_frame(self, visited, current_path=None):
        scale = 480 // 30
        img = Image.new('RGB', (480, 480), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        for y in range(30):
            for x in range(30):
                rect = [x * scale, y * scale, (x + 1) * scale, (y + 1) * scale]
                if self.grid[y][x] == 1:
                    draw.rectangle(rect, fill=(0, 0, 0))
                elif (x, y) in visited:
                    draw.rectangle(rect, fill=(0, 255, 0)) 
        
        if current_path:
            for x, y in current_path:
                rect = [x * scale, y * scale, (x + 1) * scale, (y + 1) * scale]
                draw.rectangle(rect, fill=(255, 0, 0))

        for pos, color in [(self.start_pos, (0, 183, 239)), (self.end_pos, (237, 28, 36))]:
            if pos:
                x, y = pos
                draw.rectangle([x*scale, y*scale, (x+1)*scale, (y+1)*scale], fill=color)
        
        self.frames.append(img)

    def solve_bfs(self):
        self._parse_bin()

        queue = deque([(self.start_pos, [self.start_pos])])
        visited = {self.start_pos}

        while queue:
            (curr_x, curr_y), path = queue.popleft()
            
            if (curr_x, curr_y) == self.end_pos:
                for i in range(10): self._draw_frame(visited, path)
                break

            self._draw_frame(visited, path)

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = curr_x + dx, curr_y + dy
                if 0 <= nx < 30 and 0 <= ny < 30 and self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))

        self.frames[0].save(
            os.path.join(self.script_dir, GIF_PATH),
            save_all=True, append_images=self.frames[1:], 
            optimize=False, duration=40, loop=0
        )

if __name__ == "__main__":
    solver = MazeSolver(BITSTREAM_PATH)
    solver.solve_bfs()