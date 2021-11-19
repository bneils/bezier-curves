import pygame
import time

from pygame import draw

def hsv_to_rgb(h, s, v):
    h %= 360
    if s > 1:
        s %= 1
    if v > 1:
        v %= 1
    # 0 <= h < 360 "hue"
    # 0 <= s <= 1   "saturation"
    # 0 <= v <= 1   "value/brightness"
    # https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    r, g, b = [
        (c, x, 0),
        (x, c, 0),
        (0, c, x),
        (0, x, c),
        (x, 0, c),
        (c, 0, x), # heh.
    ][int(h // 60)]
    return ((r + m) * 255, (g + m) * 255, (b + m) * 255)

def lerp(a, b, w):
    return a + (b - a) * w

def bezier_curve(pts, w):
    # This is a parametric function, w in this case is "t".
    # The domain is between 0 and 1, and the function is supplied by a list of points to lerp across.

    # This returns a list of each nesting points. (for animation purposes)
    #  e.g. list of 4 points:
    #  initial 4 points.
    #  lerped 3 points
    #  lerped 2 points
    #  lerped 1 point(s)
    result = [pts]
    while len(pts) > 1:
        pts = [
            # Get a point between these two 2d points
            (lerp(pts[i][0], pts[i + 1][0], w), 
                lerp(pts[i][1], pts[i + 1][1], w))
            for i in range(len(pts) - 1)
        ]
        result.append(pts)
    return result

def draw_segments(pts, color=(100, 100, 255)):
    for i in range(1, len(pts)):
        pygame.draw.aaline(surf, color, pts[i - 1], pts[i], 2)

def draw_pts(pts, width=7):
    for pt in pts:
        pygame.draw.circle(surf, (255, 0, 0), pt, width)

pygame.init()
surf = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Lclick to place points | Enter to render | Backspace to reset")

# How many points are made a second.
courseness = 100
while True:
    curve = []
    polling = True
    while polling:
        time.sleep(1 / 60)
        surf.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    curve.append(event.pos)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and curve:
                polling = False

        draw_segments(curve)
        draw_pts(curve)
        if curve:
            draw_segments([curve[-1], pygame.mouse.get_pos()])
        pygame.display.flip()

    # Animate scene
    has_quit = False
    points_on_curve = [(curve[0], hsv_to_rgb(0, 1, 1))]
    for i in range(courseness + 1):
        w = i / courseness
        start = time.perf_counter()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Reset to the polling phase
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                has_quit = True
        
        if has_quit:
            break

        # Calculate a % of the total animation time (w), and find the pt in the bezier curve
        # Each point is remembered so it can be connected to form lines (to make an illusion of a curve)

        # We don't wanna crash, and create an immense amount of points, would we?
        surf.fill((0, 0, 0))
        if i < courseness:
            nested_pts = bezier_curve(curve, w)
            for pts in nested_pts:
                draw_segments(pts)
                draw_pts(pts, 3)
            rgb_of_curve_segment = hsv_to_rgb(w * 360, 1, 1)
            points_on_curve.append(
                (nested_pts[-1][0], rgb_of_curve_segment)
            )
        
            # Now, draw the actual curve.
            for i in range(len(points_on_curve) - 1):
                (pt1, color1) = points_on_curve[i]
                (pt2, _) = points_on_curve[i + 1]
                draw_segments([pt1, pt2], color1)
        else:
            # Copied code from above... too lazy to make a function
            for i in range(len(points_on_curve) - 1):
                pt1, color1 = points_on_curve[i]
                pt2, _ = points_on_curve[i + 1]
                draw_segments([pt1, pt2], color1)
        pygame.display.flip()
        
        elapsed = time.perf_counter() - start
        time.sleep(max(1 / 60 - elapsed, 0))
    
    # Wait and do nothing
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                waiting = False