import pygame
import time

# GLOBALS HERE
(WIDTH, HEIGHT) = (800, 800)
NUM_POINTS = 150        # how many points should exist on the curve.
COLOR_SPEED = 0.25
FADE_SPEED = 0.75

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

def draw_pts(pts, width=3, color=(255,0,0)):
    for pt in pts:
        pygame.draw.circle(surf, color, pt, width)

pygame.init()
surf = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lclick to place points | Enter to render | Backspace to reset")

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and curve:
                    polling = False
                elif event.key == pygame.K_BACKSPACE:
                    curve = []

        draw_segments(curve)
        draw_pts(curve)
        if curve:
            draw_segments([curve[-1], pygame.mouse.get_pos()])
        pygame.display.flip()

    # Animate scene
    has_quit = False
    points_on_curve = [curve[0]]
    animation_start = time.time()
    for i in range(NUM_POINTS + 1):
        w = i / NUM_POINTS
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
        nested_pts = bezier_curve(curve, w)
        for pts in nested_pts:
            draw_segments(pts)
            draw_pts(pts, 3)
        rgb_of_curve_segment = hsv_to_rgb(w * 360, 1, 1)
        points_on_curve.append(nested_pts[-1][0])
    
        # Now, draw the actual curve.
        for i in range(len(points_on_curve) - 1):
            # To get the hue for this segment, h = 360 * (elapsed * rate + %complete)
            h = 360 * (COLOR_SPEED * (time.time() - animation_start) + i / len(points_on_curve))
            draw_segments(points_on_curve[i:i + 2], hsv_to_rgb(h, 1, 1))
        pygame.display.flip()
        elapsed = time.perf_counter() - start
        time.sleep(max(1 / 60 - elapsed, 0))
    
    # Continue animating rainbow curve, and fade the segments to black
    waiting = not has_quit
    fade_start = time.time()
    while waiting:
        start = time.perf_counter()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                waiting = False

        surf.fill((0, 0, 0))
        darkness = FADE_SPEED * (time.time() - fade_start) * 255
        base_color = (100, 100, 255)
        new_color = [max(0, c - darkness) for c in base_color]
        draw_segments(curve, new_color)
        base_color = (255, 0, 0)
        new_color = [max(0, c - darkness) for c in base_color]
        draw_pts(curve, 3, new_color)

        # Copied from above
        for i in range(len(points_on_curve) - 1):
            # To get the hue for this segment, h = 360 * (elapsed * rate + %complete)
            h = 360 * (COLOR_SPEED * (time.time() - animation_start) + i / len(points_on_curve))
            draw_segments(points_on_curve[i:i + 2], hsv_to_rgb(h, 1, 1))

        pygame.display.flip()
        elapsed = time.perf_counter() - start
        time.sleep(max(1 / 60 - elapsed, 0))
