import json
import math

import pygame
import argparse
import easygui

TILE_OFFSET = 2
SCALE = 20
TARGET_SCREEN_SIZE = 600
EMPTY = pygame.Surface((SCALE, SCALE))
EMPTY.fill((0, 0, 0))
COBBLE = pygame.transform.scale(pygame.image.load("assets/tiles/cobble.jpg"), (SCALE, SCALE))
WOOL = pygame.transform.scale(pygame.image.load("assets/tiles/wool.jpg"), (SCALE, SCALE))
BRICK = pygame.transform.scale(pygame.image.load("assets/tiles/bricks.jpg"), (SCALE, SCALE))
TRAP = pygame.transform.scale(pygame.image.load("assets/tiles/trap.jpg"), (SCALE, SCALE))

# Spider icon is by xmyonli at https://www.deviantart.com/xmyonli/art/Minecraft-Spider-Icon-for-Window-346140117
WINDOW_ICON = pygame.image.load("assets/icon/main_icon.png")

image_dict = {
    0: EMPTY,
    1: COBBLE,
    2: BRICK,
    3: TRAP,
    4: WOOL
}

keyboard_mapping = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4
}


def start_drawing_mode(size: int, path: str):
    """
    Main loop for the drawing script

    Args:
        size (int): Size of the square canvas.
        path (int): Path of the file to open, if specified. If none an empty size x size canvas will be created.

    Returns:
        None
    """
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
    pygame.display.set_caption('Optimal Carpets - Canvas')
    pygame.display.set_icon(WINDOW_ICON)
    for i in range(h):
        for j in range(w):
            grid[i][j] = int(grid[i][j])
    mouse_surface = pygame.Surface((SCALE, SCALE), pygame.SRCALPHA)
    mouse_surface.set_alpha(128)
    draw_press, delete_press = False, False
    mode = 'free'
    circle_radius = 6
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
                    coords = draw_circle(circle_center, circle_radius)
                    for x, y in coords:
                        x, y = clip_coor((x, y), (w, h))
                        grid[y][x] = selected_block
                elif mode == 'fill':
                    to_fill = fill(grid, (mx, my), selected_block)
                    for x, y in to_fill:
                        grid[y][x] = selected_block
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
                    save_path = easygui.filesavebox(default="pattern.json", filetypes=["*.png"])
                    with open(save_path, 'w') as f:
                        json.dump(grid, f)
                    drawing = False
                if event.key == pygame.K_p:
                    save_path = easygui.filesavebox(default="blueprint.png", filetypes=["*.png"])
                    pygame.image.save(screen, save_path)
                    drawing = False
                if event.key in keyboard_mapping.keys():
                    selected_block = keyboard_mapping.get(event.key)
            if event.type == pygame.MOUSEWHEEL:
                if mode == 'circle':
                    circle_radius += event.y
                    if circle_radius < 2:
                        circle_radius = 2
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
            for j, i in draw_circle(circle_center, circle_radius):
                j, i = clip_coor((j, i), (w, h))
                screen.blit(image_dict[selected_block], get_rect_from_coor((j, i)))

        mouse_rect = get_rect_from_coor((mx, my))
        mouse_surface.fill((255, 255, 255))
        pygame.draw.rect(mouse_surface, (255, 255, 255), mouse_rect)
        screen.blit(mouse_surface, (mouse_rect.x, mouse_rect.y))
        pygame.display.update()


def get_rect_from_coor(coor: tuple[int, int]) -> pygame.rect.Rect:
    """
    Returns the rectangle of the grid from the given coordinates. The input coordinates are therefore converted into ones
    in the grid space, and a rectangle of dimension SCALE X SCALE is created.

    Args:
        coor (tuple[int, int]): Input coordinates to be converted.

    Returns:
        pygame.rect.Rect: Rectangle of the grid.
    """
    return pygame.rect.Rect(
        (TILE_OFFSET * (coor[0] + 1) + SCALE * coor[0], TILE_OFFSET * (coor[1] + 1) + SCALE * coor[1], SCALE, SCALE))


def clip_coor(coor: tuple[int, int], grid_size: tuple[int, int], mouse: bool = False) -> tuple[int, int]:
    """
    Clips the input coordinates inside the grid if necessary. If mouse is False, the function expects coordinates belonging
    to the grid, and are clipped between 0 and the grid width/height. Otherwise, the function expects coordinates from the
    window point of view and are preventively converted into grid space coordinates.

    Args:
        coor (tuple[int, int]): coordinates to clip
        grid_size (tuple[int, int]): (width, height) of the grid
        mouse (bool, optional): If these coordinates come from the grid space or are raw mouse coordinates. Defaults to False.

    Returns:
        tuple[int, int]: clipped coordinates (x, y)
    """
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
    """
    Computes the perimeter of a rectangle given its top left corner and its bottm right corner.

    Args:
        topleft (int): Topleft corner coordinates
        btmright (int): Bottom right corner coordinates

    Returns:
        list[tuple[int, int]]: Returns the list of the coordinates of the points belonging to the perimeter of the specified
        rectangle in the form [(x0, y0), (x1, y1), ...]
    """
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


def draw_circle(center: tuple[int, int], radius: int) -> list[tuple[int, int]]:
    """
    Computes the perimeter of a circle given its center and radius. The function starts from the point (r, 0) and iteratively
    moves to the next point following this process:
    - if x^2 + (y+1)^2 <= radius then (x, y+1) is the next point and y gets updated accordingly.
    - otherwise the next point of the circle is chosen to be (x-1, y+1)
    The above process stops when x >= y i.e. when the first octave is built. The other 7 remaining octaves are constructed
    by symmetry. From the first one

    Args:
        center (tuple[int, int]): Circle's center coordinate
        radius (int): Radius of the circle

    Returns:
        list[tuple[int, int]]: Returns the list of the coordinates of the points belonging to the perimeter of the specified
        circle in the form [(x0, y0), (x1, y1), ...]

    Notes:
        Due to how the algorithm works, this function can ONLY generate circles with an odd diameter.
    """
    cx, cy = center[0] + 0.5, center[1] + 0.5
    points = []
    x = radius
    y = 0
    while x >= y:
        points.append((cx + x, cy + y))
        points.append((cx + y, cy + x))
        points.append((cx - y, cy + x))
        points.append((cx - x, cy + y))
        points.append((cx - x, cy - y))
        points.append((cx - y, cy - x))
        points.append((cx + x, cy - y))
        points.append((cx + y, cy - x))
        if x ** 2 + (y + 1) ** 2 - radius ** 2 >= 0:
            x -= 1
        y += 1

    return [(int(p[0]), int(p[1])) for p in points]


def fill(grid: list[list[int]], start: tuple[int, int], selected_block: int):
    """
    Fills a closed region with the selected block. A closed region is by definition a perimeter without holes made with
    blocks equal to the selected block.

    Args:
        grid (list[list[int]]): The canvas grid
        start (int): Starting point of the fill
        selected_block (int): selected block for filling

    Returns:
        set[tuple[int, int]]: Returns the set of the coordinates of the points to fill in the form {(x0, y0), (x1, y1), ...}
    """
    unexplored = [start]
    to_fill = set({})
    w, h = len(grid[0]), len(grid)
    while unexplored:
        nex = unexplored.pop()
        if grid[nex[1]][nex[0]] == selected_block:
            continue
        to_fill.add(nex)
        neighbors = [(nex[0] - 1, nex[1]), (nex[0] + 1, nex[1]), (nex[0], nex[1] - 1), (nex[0], nex[1] + 1)]
        neighbors = [clip_coor(n, (w, h)) for n in neighbors]
        neighbors = [n for n in neighbors if n not in to_fill]
        unexplored += neighbors
    return to_fill


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=15, help='Size of the canvas')
    parser.add_argument('--path', type=str, default='', help='Path of the file to open')
    args = parser.parse_args()
    pygame.init()
    start_drawing_mode(args.size, args.path)
