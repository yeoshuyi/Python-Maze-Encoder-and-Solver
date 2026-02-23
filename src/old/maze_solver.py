"""
Takes in binary file encoded by maze_encoder.py
"""


import struct
import os
import heapq
import time
from PIL import Image, ImageDraw
from collections import deque


BITSTREAM_PATH = 'maze.bin'
GIF_PATH = 'maze.gif'


class MazeSolver:
    def __init__(self, path=BITSTREAM_PATH):
        self.script_dir = os.path.dirname(__file__)
        self.bin_path = os.path.join(self.script_dir, path)
        self.grid = [[0 for i in range(30)] for i in range(30)]
        self.start_pos = None
        self.end_pos = None
        self.frames = []
        self._parse_bin()

    def _parse_bin(self):
        with open(self.bin_path, "rb") as f:
            data = f.read()
            count = len(data) // 4
            instructions = struct.unpack(f'>{count}I', data)

        for instr in instructions:
            opcode = instr & 0xF
            match opcode:
                case 0x1:
                    y = (instr >> 4) & 0xFF
                    half = (instr >> 12) & 0xF
                    wall_data = (instr >> 16) & 0x7FFF
                    
                    for i in range(15):
                        if wall_data & (1 << (14 - i)):
                            x = i if half == 0 else i + 15
                            if 0 <= x < 30 and 0 <= y < 30:
                                self.grid[y][x] = 1
                case 0x2:
                    y = (instr >> 24) & 0xFF
                    x = (instr >> 16) & 0xFF
                    funct2 = (instr >> 8) & 0xF
                    match funct2:
                        case 0x1:
                            self.start_pos = (x, y)
                        case 0x2:
                            self.end_pos = (x, y)
    
    def solve_maze(self):
        bfs_q = deque([(self.start_pos, [self.start_pos])])
        bfs_visited = {self.start_pos}
        bfs_done = False
        bfs_path = []
        bfs_steps = 0
        bfs_set = False
        bfs_elapsed = 0

        dfs_q = deque([(self.start_pos, [self.start_pos])])
        dfs_visited = {self.start_pos}
        dfs_done = False
        dfs_path = []
        dfs_steps = 0
        dfs_set = False
        dfs_elapsed = 0

        start_h = abs(self.end_pos[0] - self.start_pos[0]) + abs(self.end_pos[1] - self.start_pos[1])
        astar_q = [(start_h, self.start_pos, [self.start_pos])]
        astar_visited_costs = {self.start_pos: 0}
        astar_done = False
        astar_path = []
        astar_steps = 0
        astar_set = False
        astar_elapsed = 0

        steps = 0
        scale = 12
        maze_w = 30 * scale
        padding = 40
        canvas_w = (maze_w * 3) + (padding * 4)
        canvas_h = maze_w + 100

        curr_time = time.time()

        while not (bfs_done and dfs_done and astar_done):
            if bfs_done and not bfs_set:
                bfs_steps = steps
                bfs_set = True
            if dfs_done and not dfs_set:
                dfs_steps = steps
                dfs_set = True
            if astar_done and not astar_set:
                astar_steps = steps
                astar_set = True
            steps += 1

            if bfs_q and not bfs_done:
                curr_time = time.time()
                (curr_x, curr_y), path = bfs_q.popleft()
                bfs_path = path
                if (curr_x, curr_y) == self.end_pos: bfs_done = True
                else:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = curr_x + dx, curr_y + dy
                        if 0 <= nx < 30 and 0 <= ny < 30 and self.grid[ny][nx] == 0 and (nx, ny) not in bfs_visited:
                            bfs_visited.add((nx, ny))
                            bfs_q.append(((nx, ny), path + [(nx, ny)]))
                bfs_elapsed += time.time() - curr_time
                curr_time = time.time()
            
            if dfs_q and not dfs_done:
                curr_time = time.time()
                new_node = False
                while dfs_q and not new_node:
                    (curr_x, curr_y), path = dfs_q.pop()
                    dfs_path = path

                    if (curr_x, curr_y) == self.end_pos:
                        dfs_path = path
                        dfs_visited.add((curr_x, curr_y))
                        dfs_done = True
                        new_node = True
                        break
                    
                    neighbors = []
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = curr_x + dx, curr_y + dy
                        if 0 <= nx < 30 and 0 <= ny < 30 and self.grid[ny][nx] == 0:
                            if (nx, ny) not in dfs_visited:
                                neighbors.append((nx, ny))

                    neighbors.sort(key=lambda pos: abs(pos[0] - self.end_pos[0]) + abs(pos[1] - self.end_pos[1]), reverse=True)

                    for nx, ny in neighbors:
                        dfs_visited.add((nx, ny))
                        dfs_q.append(((nx, ny), path + [(nx, ny)]))
                        new_node = True
                dfs_elapsed += time.time() - curr_time
                curr_time = time.time()
            
            if astar_q and not astar_done:
                curr_time = time.time()
                f, (curr_x, curr_y), path = heapq.heappop(astar_q)
                astar_path = path
                if (curr_x, curr_y) == self.end_pos: astar_done = True
                else:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = curr_x + dx, curr_y + dy
                        if 0 <= nx < 30 and 0 <= ny < 30 and self.grid[ny][nx] == 0:
                            new_g = astar_visited_costs[curr_x, curr_y] + 1
                            if (nx, ny) not in astar_visited_costs or new_g < astar_visited_costs[nx, ny]:
                                astar_visited_costs[(nx, ny)] = new_g
                                h = abs(self.end_pos[0] - nx) + abs(self.end_pos[1] - ny)
                                heapq.heappush(astar_q, (new_g + h, (nx, ny), path + [(nx, ny)]))
                astar_elapsed += time.time() - curr_time
                curr_time = time.time()
            
            frame = Image.new('RGB', (canvas_w, canvas_h), (240, 240, 240))
            draw = ImageDraw.Draw(frame)

            self._draw_submaze(
                draw, 0 * (maze_w + padding) + padding, 50, 
                scale, bfs_visited, bfs_path, "BFS", 
                steps if bfs_steps == 0 else bfs_steps,
                bfs_elapsed
            )
            self._draw_submaze(
                draw, 1 * (maze_w + padding) + padding, 50, 
                scale, dfs_visited, dfs_path, " Greedy DFS", 
                steps if dfs_steps == 0 else dfs_steps,
                dfs_elapsed
            )
            self._draw_submaze(
                draw, 2 * (maze_w + padding) + padding, 50,
                scale, set(astar_visited_costs.keys()), astar_path, "A-Star", 
                steps if astar_steps == 0 else astar_steps,
                astar_elapsed
            )
            
            self.frames.append(frame)
        
        #Add 30 frame delay
        for i in range(30):
            self.frames.append(frame)
        
        self.frames[0].save(os.path.join(self.script_dir, GIF_PATH),
            save_all=True, append_images=self.frames[1:], duration=40, loop=0)

    def _draw_submaze(self, draw, offset_x, offset_y, scale, visited, path, title, step_text, time):
        draw.text((offset_x + 40, offset_y - 30), title, fill=(0,0,0))
        draw.text((offset_x + 40, offset_y + (30*scale) + 10), f"Steps: {step_text}", fill=(100,100,100))
        draw.text((offset_x + 120, offset_y + (30*scale) + 10), f"Path Length: {len(path)}", fill=(100,100,100))
        draw.text((offset_x + 240, offset_y + (30*scale) + 10), f"Elapsed Time: {time*1000:.2f}ms", fill=(100,100,100))
        
        for y in range(30):
            for x in range(30):
                rect = [offset_x + x*scale, offset_y + y*scale, offset_x + (x+1)*scale, offset_y + (y+1)*scale]
                if self.grid[y][x] == 1: draw.rectangle(rect, fill=(0,0,0))
                elif (x, y) in visited: draw.rectangle(rect, fill=(200, 255, 200))
        
        for x, y in path:
            rect = [offset_x + x*scale, offset_y + y*scale, offset_x + (x+1)*scale, offset_y + (y+1)*scale]
            draw.rectangle(rect, fill=(255, 0, 0))

        for pos, color in [(self.start_pos, (0, 183, 239)), (self.end_pos, (237, 28, 36))]:
            if pos:
                x, y = pos
                draw.rectangle([offset_x + x*scale, offset_y + y*scale, offset_x + (x+1)*scale, offset_y + (y+1)*scale], fill=color)

if __name__ == "__main__":
    solver = MazeSolver(BITSTREAM_PATH)
    solver.solve_maze()