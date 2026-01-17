import pygame
import random

import ctypes
ctypes.windll.user32.SetProcessDPIAware() # lock screen size

pygame.init()

DEAD = (0, 0, 0) 
ALIVE = (0, 255, 128) 
GRIDLINES = (128, 128, 128)
SEPARATOR = (50, 50, 50)  # Color for separating the 9 grids

WIDTH, HEIGHT = 800, 800
GRID_COUNT = 3  # 3x3 grid of games
SEPARATOR_WIDTH = 10  # Width of separator between games
GAME_SIZE = (WIDTH - (GRID_COUNT + 1) * SEPARATOR_WIDTH) // GRID_COUNT  # Size of each game area
TILE_SIZE = 5
GRID_WIDTH = GAME_SIZE // TILE_SIZE
GRID_HEIGHT = GAME_SIZE // TILE_SIZE
FPS = 60

screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
clock = pygame.time.Clock()

def gen(num):
    return set([(random.randrange(0, GRID_HEIGHT), random.randrange(0, GRID_WIDTH)) for _ in range(num)])

def draw_grid(positions, offset_x, offset_y):
    for position in positions:
        col, row = position
        top_left = (offset_x + col * TILE_SIZE, offset_y + row * TILE_SIZE)
        pygame.draw.rect(screen, ALIVE, (*top_left, TILE_SIZE, TILE_SIZE))
    
    for row in range(GRID_HEIGHT):
        y_pos = offset_y + row * TILE_SIZE
        pygame.draw.line(screen, GRIDLINES, (offset_x, y_pos), (offset_x + GAME_SIZE, y_pos))
    
    for col in range(GRID_WIDTH):
        x_pos = offset_x + col * TILE_SIZE
        pygame.draw.line(screen, GRIDLINES, (x_pos, offset_y), (x_pos, offset_y + GAME_SIZE))
    
def adjust_grid(positions):
    all_neighbors = set()
    new_positions = set()
    
    for position in positions:
        neighbors = get_neighbors(position)
        all_neighbors.update(neighbors)
        
        neighbors = list(filter(lambda x: x in positions, neighbors))
        
        if len(neighbors) in [2, 3]:
            new_positions.add(position)
            
    for position in all_neighbors:
        neighbors = get_neighbors(position)
        neighbors = list(filter(lambda x: x in positions, neighbors))
        
        if len(neighbors) == 3:
            new_positions.add(position)

    return new_positions

def get_neighbors(pos):
    x, y = pos
    neighbors = []
    for dx in [-1, 0, 1]:
        if x + dx < 0 or x + dx >= GRID_WIDTH:
            continue
        for dy in [-1, 0, 1]:
            if y + dy < 0 or y + dy >= GRID_HEIGHT:
                continue
            if dx == 0 and dy == 0:
                continue
            
            neighbors.append((x + dx, y + dy))
            
    return neighbors

def get_grid_index(mouse_x, mouse_y):
    """Returns which of the 9 grids (grid_row, grid_col) the mouse is in, or None if in separator"""
    for grid_row in range(GRID_COUNT):
        for grid_col in range(GRID_COUNT):
            offset_x = SEPARATOR_WIDTH + grid_col * (GAME_SIZE + SEPARATOR_WIDTH)
            offset_y = SEPARATOR_WIDTH + grid_row * (GAME_SIZE + SEPARATOR_WIDTH)
            
            if (offset_x <= mouse_x < offset_x + GAME_SIZE and 
                offset_y <= mouse_y < offset_y + GAME_SIZE):
                # Convert to local coordinates
                local_x = mouse_x - offset_x
                local_y = mouse_y - offset_y
                col = local_x // TILE_SIZE
                row = local_y // TILE_SIZE
                return (grid_row, grid_col, col, row)
    
    return None

def main():
    running = True
    playing = True
    count = 0
    update_freq = 15
    step = 0
    
    # Create 9 independent grids
    grids = [[set() for _ in range(GRID_COUNT)] for _ in range(GRID_COUNT)]
    
    # Initialize each grid with random cells
    for row in range(GRID_COUNT):
        for col in range(GRID_COUNT):
            grids[row][col] = gen(random.randrange(30, 40) * GRID_WIDTH)
    
    while running:
        clock.tick(FPS)
        
        if playing:
            count += 1
            
        if count >= update_freq:
            count = 0
            step += 1
            # Update all 9 grids independently
            for row in range(GRID_COUNT):
                for col in range(GRID_COUNT):
                    grids[row][col] = adjust_grid(grids[row][col])
            
        pygame.display.set_caption(f"Active at step {step}" if playing else f"Paused at step {step}")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                result = get_grid_index(*pygame.mouse.get_pos())
                if result:
                    grid_row, grid_col, col, row = result
                    pos = (col, row)
                    
                    if pos in grids[grid_row][grid_col]:
                        grids[grid_row][grid_col].remove(pos)
                    else:
                        grids[grid_row][grid_col].add(pos)
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing
                    
                if event.key == pygame.K_c:
                    for row in range(GRID_COUNT):
                        for col in range(GRID_COUNT):
                            grids[row][col] = set()
                    playing = False
                    count = 0
                    
                if event.key == pygame.K_g:
                    for row in range(GRID_COUNT):
                        for col in range(GRID_COUNT):
                            grids[row][col] = gen(random.randrange(30, 40) * GRID_WIDTH)

        screen.fill(SEPARATOR)
        
        # Draw all 9 grids
        for grid_row in range(GRID_COUNT):
            for grid_col in range(GRID_COUNT):
                offset_x = SEPARATOR_WIDTH + grid_col * (GAME_SIZE + SEPARATOR_WIDTH)
                offset_y = SEPARATOR_WIDTH + grid_row * (GAME_SIZE + SEPARATOR_WIDTH)
                
                # Fill background for this grid
                pygame.draw.rect(screen, DEAD, (offset_x, offset_y, GAME_SIZE, GAME_SIZE))
                
                # Draw this grid
                draw_grid(grids[grid_row][grid_col], offset_x, offset_y)
        
        pygame.display.update()

    pygame.quit()
    
if __name__ == "__main__":
    main()