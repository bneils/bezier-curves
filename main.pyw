import pygame
import time
import settings

def hsv_to_rgb(h, s, v):
    h %= 360
    if s < 0: s = 0
    if s > 1: s = 1
    if v < 0: v = 0
    if v > 1: v = 1
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

def distance(pt1, pt2):
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5

class BezierAnimation:
    def __init__(self, surf):
        self.pts = []
        self.surf = surf
        self.curve_approximation = []

    def bezier_curve(self, w):
        """This is a parametric function, w in this case is "t".
        The domain is between 0 and 1, and the function is supplied by a list of points to lerp across.

        This returns a list of each nesting points. (for animation purposes)"""
        pts = self.pts
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

    def connect_pts(self, pts, color = settings.SEGMENT_COLOR, width = settings.SEGMENT_WIDTH):
        for i in range(1, len(pts)):
            pygame.draw.aaline(self.surf, color, pts[i - 1], pts[i], width)

    def draw_pts(self, pts, color = settings.POINT_COLOR, width = settings.POINT_RADIUS):
        for pt in pts:
            pygame.draw.circle(self.surf, color, pt, width)

    def poll_points(self):
        """Register clicks from the user to form as the outline for the curve."""
        self.pts = []
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.surf.fill(settings.BACKGROUND_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.pts.append(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.pts:
                        return self.pts
                    elif event.key == pygame.K_BACKSPACE:
                        self.pts = []

            self.connect_pts(self.pts)
            self.draw_pts(self.pts)
            if self.pts:
                self.connect_pts([self.pts[-1], pygame.mouse.get_pos()])
            pygame.display.flip()

    def animate_lerped_scene(self):
        """Animates the lerp segments and the rainbow curve"""
        self.points_on_curve = []
        self.curve_approximation = []
        self.start_of_animation = time.time()
        for i in range(settings.NUM_POINTS + 1):
            w = i / settings.NUM_POINTS
            loop_begin = time.perf_counter()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # User quit animation, back to the drawing board
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    return False # signals that lerp wasn't successful

            # Calculate a % of the total animation time (w), and find the pt in the bezier curve
            # Each point is remembered so it can be connected to form lines (to make an illusion of a curve)
            # We don't wanna crash, and create an immense amount of points, would we?
            self.surf.fill(settings.BACKGROUND_COLOR)
            nested_pts = self.bezier_curve(w)
            pt = nested_pts[-1][0]
            self.curve_approximation.append(
                0 if i == 0 else
                self.curve_approximation[-1] + distance(pt, self.points_on_curve[-1])
            )

            self.points_on_curve.append(pt)
            for pts in nested_pts:
                self.connect_pts(pts)
                self.draw_pts(pts)
            
            self.draw_curve()
            
            # Timing trickery to stay close to 60 ticks a second
            pygame.display.flip()
            elapsed = time.perf_counter() - loop_begin
            time.sleep(max(settings.MINIMUM_ANIMATION_SPEED / settings.NUM_POINTS - elapsed, 0))
        return True

    def draw_curve(self):
        """Draws the rainbow bezier curve"""
        for i in range(len(self.points_on_curve) - 1):
            # To get the hue for this segment, h = 360 * (elapsed * rate + %complete)
            # We have to use distances along the curve because the curve may advance at different
            # rates for uniform values of w.
            elapsed = settings.COLOR_SPEED * (time.time() - self.start_of_animation)
            h = 360 * (self.curve_approximation[i] / self.curve_approximation[-1] - elapsed)
            self.connect_pts(self.points_on_curve[i:i + 2], hsv_to_rgb(h, 1, 1))

    def idle_animation_fade(self):
        """Continue animating rainbow curve, and fade the segments to black"""
        fade_start = time.time()
        while True:
            loop_begin = time.perf_counter()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    return

            self.surf.fill(settings.BACKGROUND_COLOR)
            percent_faded = settings.FADE_SPEED * (time.time() - fade_start)

            if percent_faded < 1:
                self.connect_pts(self.pts, [
                    lerp(seg_ch, b_ch, percent_faded)
                    for seg_ch, b_ch in zip(settings.SEGMENT_COLOR, settings.BACKGROUND_COLOR)
                ], settings.SEGMENT_WIDTH)

                self.draw_pts(self.pts, [
                    lerp(pt_ch, b_ch, percent_faded)
                    for pt_ch, b_ch in zip(settings.POINT_COLOR, settings.BACKGROUND_COLOR)
                ], settings.POINT_RADIUS)
            self.draw_curve()

            pygame.display.flip()
            elapsed = time.perf_counter() - loop_begin
            time.sleep(max(1 / 60 - elapsed, 0))    # 60 execs / 1 second

def main():
    pygame.init()
    surf = pygame.display.set_mode(settings.SIZE)
    pygame.display.set_caption("Lclick to place points | Enter to render | Backspace to reset")
    scene = BezierAnimation(surf)

    while True:
        scene.poll_points()
        if scene.animate_lerped_scene():
            scene.idle_animation_fade()

if __name__ == "__main__":
    main()