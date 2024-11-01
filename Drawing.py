import json
import math
import random

import pygame
import argparse

TILE_OFFSET = 1
SCALE = 20
COBBLE = pygame.transform.scale(pygame.image.load("./assets/cobble.jpg"), (SCALE, SCALE))
MOSSY = pygame.transform.scale(pygame.image.load("./assets/mossy.jpg"), (SCALE, SCALE))
WOOL = pygame.transform.scale(pygame.image.load("./assets/wool.jpg"), (SCALE, SCALE))
BRICK = pygame.transform.scale(pygame.image.load("./assets/bricks.jpg"), (SCALE, SCALE))
TRAP = pygame.transform.scale(pygame.image.load("./assets/trap.jpg"), (SCALE, SCALE))

image_dict = {
    1: COBBLE,
    2: MOSSY,
    3: BRICK,
    4: TRAP,
    5: WOOL
}

def start_drawing_mode(size: int, path: str):
    if not path:
        grid = [[0 for _ in range(size)] for _ in range(size)]
    else:
        with open(path, "r") as f:
            grid = json.load(f)
            # TODO PLEASE FIX
            size = len(grid)
    screen_size = size * SCALE + TILE_OFFSET * (size + 1)
    screen = pygame.display.set_mode((screen_size, screen_size))
    for i in range(size):
        for j in range(size):
            grid[i][j] = int(grid[i][j])
    mouse_surface = pygame.Surface((SCALE, SCALE), pygame.SRCALPHA)
    mouse_surface.set_alpha(128)
    draw_press, delete_press = False, False
    mode = 'free'
    circle_center = (-1, -1)
    selected_block = 1
    drawing = True
    while drawing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mode == 'free':
                    if event.button == 1:
                        draw_press = True
                    elif event.button == 3:
                        delete_press = True
                elif mode == 'circle':
                    if circle_center == (-1, -1):
                        circle_center = (mx, my)
                    else:
                        radius = (mx - circle_center[0], my - circle_center[1])
                        radius = round(math.sqrt(radius[0] ** 2 + radius[1] ** 2))
                        coords = draw_circle(grid, circle_center, radius)
                        for x, y in coords:
                            grid[y][x] = selected_block
                        circle_center = (-1, -1)
                elif mode == 'fill':
                    fill(grid, (mx, my))
            if event.type == pygame.MOUSEBUTTONUP:
                if mode == 'free':
                    if event.button == 1:
                        draw_press = False
                    elif event.button == 3:
                        delete_press = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    mode = 'circle' if mode != 'circle' else 'free'
                if event.key == pygame.K_f:
                    mode = 'fill' if mode != 'fill' else 'free'
                if event.key == pygame.K_s:
                    with open('pattern.json', 'w') as f:
                        json.dump(grid, f)
                        drawing = False
                if event.key == pygame.K_1:
                    selected_block = 1
                if event.key == pygame.K_2:
                    selected_block = 2
                if event.key == pygame.K_3:
                    selected_block = 3
                if event.key == pygame.K_4:
                    selected_block = 4
        screen.fill((155, 161, 157))
        mx, my = pygame.mouse.get_pos()
        mx, my = clip_mouse((mx, my), size)
        if draw_press:
            if mode == 'free':
                grid[my][mx] = selected_block

        elif delete_press:
            if mode == 'free':
                grid[my][mx] = 0

        for i in range(size):
            for j in range(size):
                current_rect = get_rect_from_coor((j, i))
                if grid[i][j] == 0:
                    pygame.draw.rect(screen,
                                     (0, 0, 0),
                                     get_rect_from_coor((j, i)))
                elif grid[i][j] != 0:
                    screen.blit(image_dict[grid[i][j]], current_rect.topleft)

        mouse_rect = get_rect_from_coor((mx, my))
        mouse_surface.fill((255, 255, 255))
        pygame.draw.rect(mouse_surface, (255, 255, 255), mouse_rect)
        screen.blit(mouse_surface, (mouse_rect.x, mouse_rect.y))
        pygame.display.update()


def get_rect_from_coor(coor: tuple[int, int]) -> pygame.rect.Rect:
    return pygame.rect.Rect(
        (TILE_OFFSET * (coor[0] + 1) + SCALE * coor[0], TILE_OFFSET * (coor[1] + 1) + SCALE * coor[1], SCALE, SCALE))


def clip_mouse(coor: tuple[int, int], grid_size: int) -> tuple[int, int]:
    x, y = coor
    x = int(x / (SCALE + TILE_OFFSET))
    y = int(y / (SCALE + TILE_OFFSET))
    x = max(0, x)
    x = min(x, grid_size - 1)
    y = max(0, y)
    y = min(y, grid_size - 1)
    return x, y


def draw_circle(grid: list, center: tuple[int, int], radius: int) -> set:
    # TODO: grid is unnecessary
    c_coor = set({})
    angle = 0.
    while angle < 360:
        x = round(center[0] + radius * math.cos(angle))
        x = max(0, x)
        x = min(x, len(grid)-1)
        y = round(center[1] + radius * math.sin(angle))
        y = max(0, y)
        y = min(y, len(grid)-1)
        c_coor.add((x, y))
        angle += 0.01
    return c_coor

def fill(grid: list, start: tuple[int, int]):
    if not(0 <= start[0] <= len(grid)-1) or not(0 <= start[1] <= len(grid)-1):
        return
    if grid[start[0]][start[1]] != 0:
        return
    if random.random() < 1:
        grid[start[0]][start[1]] = 1
    else:
        grid[start[0]][start[1]] = 2
    fill(grid, (start[0]+1, start[1]))
    fill(grid, (start[0]-1, start[1]))
    fill(grid, (start[0], start[1]+1))
    fill(grid, (start[0], start[1]-1))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=15, help='Size of the canvas')
    parser.add_argument('--path', type=str, default='', help='Path of the file to open')
    args = parser.parse_args()
    pygame.init()
    start_drawing_mode(args.size, args.path)
