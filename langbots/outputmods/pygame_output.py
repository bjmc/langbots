#!/usr/bin/python
import os
import sys
import tempfile

# Third-party modules
import pygame

# App modules
from langbots import lib

Surfaces = lib.struct("Surfaces", ["robots", "bullet", "robot_surfaces"])
RobotSurfaces = lib.struct("RobotSurfaces", ["body", "turret"])

def create_screen(size, caption):
    """Create Pygame display with pixel size (width, height) and caption.""" 
    window = pygame.display.set_mode(size)
    pygame.display.set_caption(caption)
    return pygame.display.get_surface()

def load_image(filename, rotate=None):
    """Load image and return Pygame surface."""
    path = os.path.join("images", filename)
    surface = pygame.image.load(path) 
    return (pygame.transform.rotate(surface, rotate) if rotate else surface)

def draw(screen, surface, pos, angle=None):
    """Draw surface in screen at pos (x, y) with an optional rotation angle."""
    surface2 = (pygame.transform.rotate(surface, angle) if angle else surface)
    x, y = pos
    w, h = surface2.get_size()
    screen.blit(surface2, map(int, (x - w/2.0, y - h/2.0)))  

def draw_field(screen, field, surfaces, video):                
    """Draw field to Pygame surface."""             
    screen.fill((0, 40, 0)) 
    for robot in field.robots.values():
        robot_surfaces = surfaces.robots[robot.name]
        draw(screen, robot_surfaces.body, (robot.x, robot.y), robot.angle)
        turret_angle = robot.angle + robot.turret_angle
        draw(screen, robot_surfaces.turret, (robot.x, robot.y), turret_angle)
    for bullet in field.bullets:
        draw(screen, surfaces.bullet, (bullet.x, bullet.y), bullet.angle)
    if video:
        temp = tempfile.NamedTemporaryFile(suffix=".jpg")
        #temp.close()
        pygame.image.save(screen, temp.name)
        sys.stdout.write(open(temp.name).read())
        temp.close()
    else:
        pygame.display.flip()
 
def init(screen_size, robot_images, video=False):
    """Init the module."""
    pygame.init()
    screen_width, screen_height = screen_size
    if video:
        screen = pygame.Surface(screen_size)
    else:
        screen = create_screen(screen_size, "Language Wars")
    # Rotate robot images +90 degrees right so they are horizontal
    robots_surfaces = {}
    for robot_name, basename in robot_images.iteritems():
        body_surface = load_image("robots/%s-body.png" % basename, rotate=-90.0)
        turret_surface = load_image("robots/%s-turret.png" % basename, rotate=-90.0)    
        robot_surfaces = RobotSurfaces(body=body_surface, turret=turret_surface)
        robots_surfaces[robot_name] = robot_surfaces
    bullet_surface = load_image("bullet.png")
    surfaces = Surfaces(robots=robots_surfaces, bullet=bullet_surface)
    return screen, surfaces

def get_output_callback(screen, surfaces, video=False):
    """Get the output draw callback."""
    def _draw_callback(field):
        return draw_field(screen, field, surfaces, video)
    return _draw_callback
