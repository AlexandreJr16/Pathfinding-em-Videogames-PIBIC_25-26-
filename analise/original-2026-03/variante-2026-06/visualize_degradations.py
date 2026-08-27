import os
import random
import math
import argparse

def load_map(filename):
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return None, 0, 0
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    header = {}
    grid_start = 0
    for i, line in enumerate(lines):
        parts = line.split()
        if not parts: continue
        if parts[0] == 'type': header['type'] = parts[1]
        elif parts[0] == 'height': header['height'] = int(parts[1])
        elif parts[0] == 'width': header['width'] = int(parts[1])
        elif parts[0] == 'map':
            grid_start = i + 1
            break
            
    height = header['height']
    width = header['width']
    grid = []
    for i in range(grid_start, grid_start + height):
        row = [c == '.' for c in lines[i].strip()]
        grid.append(row)
        
    return grid, height, width

def save_as_ppm_upscaled(grid, original_grid, filename, scale=4):
    """
    Saves the grid as an upscaled PPM file for better visibility.
    - White: Traversable
    - Gray: Originally Blocked
    - Red: Newly Blocked
    """
    height = len(grid)
    width = len(grid[0])
    
    with open(filename, 'w') as f:
        f.write(f"P3\n{width * scale} {height * scale}\n255\n")
        for i in range(height):
            # Repeat each row 'scale' times
            row_content = []
            for j in range(width):
                if grid[i][j]: color = "255 255 255 "
                elif not original_grid[i][j]: color = "180 180 180 "
                else: color = "255 0 0 "
                row_content.append(color * scale)
            
            full_row = "".join(row_content) + "\n"
            for _ in range(scale):
                f.write(full_row)

def save_base_as_ppm_upscaled(grid, filename, scale=4):
    height = len(grid)
    width = len(grid[0])
    with open(filename, 'w') as f:
        f.write(f"P3\n{width * scale} {height * scale}\n255\n")
        for i in range(height):
            row_content = []
            for j in range(width):
                color = "255 255 255 " if grid[i][j] else "0 0 0 "
                row_content.append(color * scale)
            full_row = "".join(row_content) + "\n"
            for _ in range(scale):
                f.write(full_row)

# Degradation Algorithms (Translated from src/map.cpp)

def radial_obstacle(grid, height, width, raio, aspecto):
    xa = random.randint(0, height - 1)
    ya = random.randint(0, width - 1)
    blocked = 0
    if grid[xa][ya]:
        for y in range(-raio, raio + 1):
            for x in range(-int(raio * aspecto), int(raio * aspecto) + 1):
                ix, iy = xa + x, ya + y
                dist = math.sqrt((x / aspecto)**2 + y**2)
                if dist <= raio and 0 <= ix < height and 0 <= iy < width:
                    if grid[ix][iy]:
                        grid[ix][iy] = False
                        blocked += 1
    return blocked

def linear_obstacle(grid, height, width, length):
    px, py = [0, 0, 1, -1], [-1, 1, 0, 0]
    xa, ya = random.randint(0, height - 1), random.randint(0, width - 1)
    blocked = 0
    if grid[xa][ya]:
        dir = random.randint(0, 3)
        currX, currY = xa, ya
        for _ in range(length):
            if 0 <= currX < height and 0 <= currY < width:
                if grid[currX][currY]:
                    grid[currX][currY] = False
                    blocked += 1
            currX, currY = currX + px[dir], currY + py[dir]
    return blocked

def sparse_obstacle(grid, height, width, raio, density):
    xa, ya = random.randint(0, height - 1), random.randint(0, width - 1)
    blocked = 0
    if grid[xa][ya]:
        for y in range(-raio, raio + 1):
            for x in range(-raio, raio + 1):
                ix, iy = xa + x, ya + y
                dist = math.sqrt(x*x + y*y)
                if dist <= raio and 0 <= ix < height and 0 <= iy < width:
                    if random.random() < density and grid[ix][iy]:
                        grid[ix][iy] = False
                        blocked += 1
    return blocked

def organic_obstacle(grid, height, width, num_cells):
    px, py = [0, 0, 1, -1], [-1, 1, 0, 0]
    xa, ya = random.randint(0, height - 1), random.randint(0, width - 1)
    blocked = 0
    if grid[xa][ya]:
        currX, currY = xa, ya
        for _ in range(num_cells * 5):
            if blocked >= num_cells: break
            if 0 <= currX < height and 0 <= currY < width:
                if grid[currX][currY]:
                    grid[currX][currY] = False
                    blocked += 1
            d = random.randint(0, 3)
            currX, currY = currX + px[d], currY + py[d]
            if not (0 <= currX < height and 0 <= currY < width):
                currX, currY = xa, ya
    return blocked

def stochastic_obstacle(grid, height, width):
    x, y = random.randint(0, height - 1), random.randint(0, width - 1)
    if grid[x][y]:
        grid[x][y] = False
        return 1
    return 0

def degrade_map(grid, height, width, target_percent, mode):
    original_traversable = sum(row.count(True) for row in grid)
    target_blocked = int(original_traversable * target_percent)
    current_blocked = 0
    tries, max_tries = 0, height * width * 2
    
    if mode == "radial":
        raio = max(2, min(height, width) // 20)
        while current_blocked < target_blocked and tries < max_tries:
            current_blocked += radial_obstacle(grid, height, width, raio, 1.0)
            tries += 1
    elif mode == "linear":
        length = max(10, min(height, width) // 2)
        while current_blocked < target_blocked and tries < max_tries:
            current_blocked += linear_obstacle(grid, height, width, length)
            tries += 1
    elif mode == "sparse":
        raio = max(5, min(height, width) // 10)
        while current_blocked < target_blocked and tries < max_tries:
            current_blocked += sparse_obstacle(grid, height, width, raio, 0.4)
            tries += 1
    elif mode == "organic":
        num_cells = max(20, (height * width) // 250)
        while current_blocked < target_blocked and tries < max_tries:
            current_blocked += organic_obstacle(grid, height, width, num_cells)
            tries += 1
    elif mode == "stochastic":
        while current_blocked < target_blocked and tries < max_tries * 5:
            current_blocked += stochastic_obstacle(grid, height, width)
            tries += 1
    return current_blocked

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="maps/den000d.map")
    parser.add_argument("--outdir", default="visualizations")
    parser.add_argument("--scale", type=int, default=4)
    args = parser.parse_args()
    
    if not os.path.exists(args.outdir): os.makedirs(args.outdir)
        
    base_maps = ["maps/den501d.map", "maps/arena.map", "maps/den500d.map", "maps/lak506d.map"]
    for m_path in base_maps:
        grid, h, w = load_map(m_path)
        if grid:
            m_name = os.path.basename(m_path).replace(".map", "")
            save_base_as_ppm_upscaled(grid, os.path.join(args.outdir, f"base_{m_name}.ppm"), args.scale)
            print(f"Generated upscaled base for {m_name}")

    modes = ["radial", "linear", "sparse", "organic", "stochastic"]
    for mode in modes:
        grid, h, w = load_map(args.map)
        if grid:
            import copy
            original_grid = copy.deepcopy(grid)
            random.seed(42)
            degrade_map(grid, h, w, 0.3, mode)
            m_name = os.path.basename(args.map).replace(".map", "")
            save_as_ppm_upscaled(grid, original_grid, os.path.join(args.outdir, f"blocking_{mode}_30.ppm"), args.scale)
            print(f"Generated upscaled 30% {mode} for {m_name}")

if __name__ == "__main__":
    main()
