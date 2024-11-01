import json
import math
import random

import pygame
import argparse

TILE_OFFSET = 1
SCALE = 20
EMPTY = pygame.Surface((SCALE, SCALE))
EMPTY.fill((0, 0, 0))
COBBLE = pygame.transform.scale(pygame.image.load("./assets/cobble.jpg"), (SCALE, SCALE))
WOOL = pygame.transform.scale(pygame.image.load("./assets/wool.jpg"), (SCALE, SCALE))
BRICK = pygame.transform.scale(pygame.image.load("./assets/bricks.jpg"), (SCALE, SCALE))
TRAP = pygame.transform.scale(pygame.image.load("./assets/trap.jpg"), (SCALE, SCALE))

image_dict = {
    0: EMPTY,
    1: COBBLE,
    2: BRICK,
    3: TRAP,
    4: WOOL
}


def start_drawing_mode(size: int, path: str):
    if not path:
        grid = [[0 for _ in range(size)] for _ in range(size)]
        w, h = (size, size)
    else:
        with open(path, "r") as f:
            grid = json.load(f)
        w, h = (len(grid[0]), len(grid))
    screen_w = w * SCALE + TILE_OFFSET * (w + 1)
    screen_h = h * SCALE + TILE_OFFSET * (h + 1)
    screen = pygame.display.set_mode((screen_w, screen_h))
    for i in range(h):
        for j in range(w):
            grid[i][j] = int(grid[i][j])
    mouse_surface = pygame.Surface((SCALE, SCALE), pygame.SRCALPHA)
    mouse_surface.set_alpha(128)
    draw_press, delete_press = False, False
    mode = 'free'
    circle_size = 6
    rect_topleft = (-1, -1)
    circle_center = (-1, -1)
    selected_block = 1
    drawing = True
    clock = pygame.time.Clock()
    while drawing:
        mx, my = pygame.mouse.get_pos()
        mx, my = clip_coor((mx, my), (w, h), mouse=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawing = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mode == 'free':
                    draw_press = True
                elif mode == 'circle':
                    coords = draw_circle(circle_center, circle_size)
                    for x, y in coords:
                        grid[y][x] = selected_block
                elif mode == 'fill':
                    fill(grid, (mx, my), selected_block)
                    mode = 'free'
                elif mode == 'rect':
                    if rect_topleft == (-1, -1):
                        rect_topleft = (mx, my)
                    else:
                        rect_coor = draw_rect(rect_topleft, (mx, my))
                        for x, y in rect_coor:
                            grid[y][x] = selected_block
                        rect_topleft = (-1, -1)
            if event.type == pygame.MOUSEBUTTONUP:
                if mode == 'free':
                    if event.button == 1:
                        draw_press = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    mode = 'circle' if mode != 'circle' else 'free'
                if event.key == pygame.K_f:
                    mode = 'fill' if mode != 'fill' else 'free'
                if event.key == pygame.K_r:
                    mode = 'rect' if mode != 'rect' else 'free'
                if event.key == pygame.K_s:
                    with open('pattern.json', 'w') as f:
                        json.dump(grid, f)
                        drawing = False
                if event.key == pygame.K_0:
                    selected_block = 0
                if event.key == pygame.K_1:
                    selected_block = 1
                if event.key == pygame.K_2:
                    selected_block = 2
                if event.key == pygame.K_3:
                    selected_block = 3
                if event.key == pygame.K_4:
                    selected_block = 4
            if event.type == pygame.MOUSEWHEEL:
                if mode == 'circle':
                    circle_size += event.y
                    if circle_size < 2:
                        circle_size = 2
        clock.tick(60)
        screen.fill((180, 180, 180))

        if draw_press:
            if mode == 'free':
                grid[my][mx] = selected_block

        for i in range(h):
            for j in range(w):
                current_rect = get_rect_from_coor((j, i))
                screen.blit(image_dict[grid[i][j]], current_rect.topleft)

        if mode == 'rect' and rect_topleft != (-1, -1):
            for j, i in draw_rect(rect_topleft, (mx, my)):
                j, i = clip_coor((j, i), (w, h))
                screen.blit(image_dict[selected_block], get_rect_from_coor((j, i)))
        if mode == 'circle':
            circle_center = (mx, my)
            for j, i in draw_circle(circle_center, circle_size):
                j, i = clip_coor((j, i), (w, h))
                screen.blit(image_dict[selected_block], get_rect_from_coor((j, i)))

        mouse_rect = get_rect_from_coor((mx, my))
        mouse_surface.fill((255, 255, 255))
        pygame.draw.rect(mouse_surface, (255, 255, 255), mouse_rect)
        screen.blit(mouse_surface, (mouse_rect.x, mouse_rect.y))
        pygame.display.update()


def get_rect_from_coor(coor: tuple[int, int]) -> pygame.rect.Rect:
    return pygame.rect.Rect(
        (TILE_OFFSET * (coor[0] + 1) + SCALE * coor[0], TILE_OFFSET * (coor[1] + 1) + SCALE * coor[1], SCALE, SCALE))


def clip_coor(coor: tuple[int, int], grid_size: tuple[int, int], mouse: bool = False) -> tuple[int, int]:
    x, y = coor
    if mouse:
        x = int(x / (SCALE + TILE_OFFSET))
        y = int(y / (SCALE + TILE_OFFSET))
    x = max(0, x)
    x = min(x, grid_size[0] - 1)
    y = max(0, y)
    y = min(y, grid_size[1] - 1)
    return x, y


def draw_rect(topleft: tuple[int, int], btmright: tuple[int, int]) -> list[tuple[int, int]]:
    if topleft[0] <= btmright[0]:
        xrange = range(topleft[0], btmright[0] + 1)
    else:
        xrange = range(btmright[0], topleft[0] + 1)
    if topleft[1] <= btmright[1]:
        yrange = range(topleft[1], btmright[1] + 1)
    else:
        yrange = range(btmright[1], topleft[1] + 1)
    rect_coor = []
    rect_coor += [(p, topleft[1]) for p in xrange]
    rect_coor += [(p, btmright[1]) for p in xrange]
    rect_coor += [(topleft[0], p) for p in yrange]
    rect_coor += [(btmright[0], p) for p in yrange]
    return rect_coor


def draw_circle(center: tuple[int, int], size: int) -> list[tuple[int, int]]:
    points = []
    if size % 2 == 1:
        cx, cy = center[0] + .5, center[1] + .5
        offset = 0
        r = size // 2
    else:
        cx, cy = center[0] + 1.5, center[1] + 0.5
        offset = -1
        r = size // 2 - 1
    x = r
    y = 0
    p = 1 - r
    while x >= y:
        points.append((cx + x, cy + y))
        points.append((cx - x + offset, cy + y))
        points.append((cx + x, cy - y + offset))
        points.append((cx - x + offset, cy - y + offset))
        points.append((cx + y, cy + x))
        points.append((cx - y + offset, cy + x))
        points.append((cx + y, cy - x + offset))
        points.append((cx - y + offset, cy - x + offset))

        y += 1

        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * y - 2 * x + 1
    return [(int(p[0]), int(p[1])) for p in points]


def fill(grid: list, start: tuple[int, int], selected_block: int):
    to_fill = {start}
    w, h = len(grid[0]), len(grid)
    while to_fill:
        nex = to_fill.pop()
        if grid[nex[1]][nex[0]] != 0:
            continue
        grid[nex[1]][nex[0]] = selected_block
        neighbors = [(nex[0] - 1, nex[1]), (nex[0] + 1, nex[1]), (nex[0], nex[1] - 1), (nex[0], nex[1] + 1)]
        neighbors = [n for n in neighbors if (0 <= n[0] < w) and (0 <= n[1] < h)]
        to_fill.update(neighbors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=15, help='Size of the canvas')
    parser.add_argument('--path', type=str, default='', help='Path of the file to open')
    args = parser.parse_args()
    pygame.init()
    start_drawing_mode(args.size, args.path)
