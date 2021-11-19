import pygame
import time

from pygame import draw

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
clock = pygame.time.Clock()

# Adjust this to increase the animation duration
duration = 5

while True:
    curve = []
    polling = True
    while polling:
        clock.tick(60)
        surf.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    curve.append(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not curve:
                        pygame.quit()
                        quit()
                    else:
                        polling = False

        draw_segments(curve)
        draw_pts(curve)
        if curve:
            draw_segments([curve[-1], pygame.mouse.get_pos()])
        pygame.display.flip()

    # Animate scene
    start = time.time()
    animating = True
    points_on_curve = [curve[0]]
    while animating:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                # Reset to the polling phase
                if event.key == pygame.K_BACKSPACE:
                    animating = False

        # Calculate a % of the total animation time (w), and find the pt in the bezier curve
        # Each point is remembered so it can be connected to form lines (to make an illusion of a curve)
        w = (time.time() - start) / duration

        # We don't wanna crash, and create an immense amount of points, would we?
        surf.fill((0, 0, 0))
        if w <= 1:
            nested_pts = bezier_curve(curve, w)
            for pts in nested_pts[:-1]:
                draw_segments(pts)
                draw_pts(pts, 3)
            points_on_curve.append(nested_pts[-1][0])

        # Now, draw the actual curve.
        draw_segments(points_on_curve, (255, 255, 255))

        pygame.display.flip()
