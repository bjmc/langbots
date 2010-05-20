#!/usr/bin/python
import sys
import math
import itertools

def pairwise(it):
    """Return overlapped pairs in iterator."""
    return itertools.izip(it, itertools.islice(it, 1, None))

def sum_vectors(vectors):
    """Sum list of vectors."""
    return tuple(sum(values) for (values) in zip(*vectors))

def substract_vectors(v1, v2):
    """Substract two vectors."""
    return tuple((x - y) for (x, y) in zip(v1, v2))

def invert_vector(v):
    """Change sign of vector."""
    return tuple(-x for x in v)   

def cross_product(v1, v2):
    """Return cross-product module of two 2D vectors."""
    (x1, y1), (x2, y2) = v1, v2
    return x1*y2 - y1*x2

def torad(angle):
    """Transform angle in degrees to radians."""
    return angle * math.pi / 180.0

def normalize_angle(angle):
    """Return angle between (-180.0, 180.0]."""
    return ((angle - 180.0) % 360.0) - 180.0

def get_direction_for_rotation(start_angle, end_angle):
    """Get optimal rotate direction to go from start to end angle."""
    start = [math.cos(torad(start_angle)), math.sin(torad(start_angle))]
    end = [math.cos(torad(end_angle)), math.sin(torad(end_angle))]
    return cmp(cross_product(start, end), 0.0)

def may_overlap(points1, points2):
    """Return True if polygons *maybe* overlap, False otherwise."""    
    x_points1, y_points1 = zip(*points1)
    x_points2, y_points2 = zip(*points2)
    return not(min(x_points2) > max(x_points1) or 
               min(y_points2) > max(y_points1) or
               max(x_points2) < min(x_points1) or
               max(y_points2) < min(y_points1))

def check_collision_of_polygons(polygon1, polygon2):
    """Return True if polygons collide (both must be convex)."""
    if not may_overlap(polygon1, polygon2):
        return False
    get = get_triangles_for_polygon
    return any(check_collision_of_triangles(triangle1, triangle2)
        for triangle1 in get(polygon1) for triangle2 in get(polygon2))
    
def check_collision_of_triangles(triangle1, triangle2):
    """Return True if triangle1 collides with triangle2."""
    if not may_overlap(triangle1, triangle2):
        return False
    # Check if any vertex of the triangle is inside the other  
    if (any(check_point_in_triangle(point, triangle2) for point in triangle1) or
             any(check_point_in_triangle(point, triangle1) for point in triangle2)):
        return True
    # Note: We do not take in account the case of those intersected triangles 
    # where no vertex is inside the other triangle. To do that we would have to 
    # check the intersection of the triangles' sides.
    return False

def get_triangles_for_polygon(polygon):
    """Get triangles that form the polygon."""
    a, other_points = polygon[0], polygon[1:]
    for (b, c) in pairwise(other_points):
        yield (a, b, c)
     
def check_point_in_polygon(point, polygon):
    """Return True if point is inside polygon (must be convex)."""
    return any(check_point_in_triangle(point, triangle) for triangle in
               get_triangles_for_polygon(polygon))
                 
def check_point_in_triangle(point, triangle):
    """Check if point is in triangle using the cross-product test."""
    if not may_overlap([point], triangle):
        return False  
    # See http://www.blackpawn.com/texts/pointinpoly/default.html
    def _check_same_side(p1, p2, a, b):
        sub_ba = substract_vectors(b, a)
        cp1 = cross_product(sub_ba, substract_vectors(p1, a))
        cp2 = cross_product(sub_ba, substract_vectors(p2, a))
        return (cp1 * cp2 >= 0)    
    a, b, c = triangle
    return (_check_same_side(point, a, b, c) and 
            _check_same_side(point, b, a, c) and 
            _check_same_side(point, c, a, b))

### Unused
            
def get_circle_boundaries(circle):
    """Get min/max positions for boundaries (square) of a circle."""
    (cx, cy), radius = circle
    return [(cx-radius, cy-radius), (cx+radius, cy+radius)]

#def check_collision_of_polygon_and_circle(polygon, circle):
#    if any(check_point_in_triangle((cx, cy), triangle) 
#           for triangle in get_triangles_for_polygon(polygon)):
#       return True
#    # optional
#    return any(check_collision_of_segment_and_circle(segment, circle) 
#               for segment in get_segments_for_polygon(polygon)):
#       return True
#    return False
            
def check_collision_of_triangle_and_circle(triangle, circle):
    if not may_overlap(triangle, get_circle_boundaries(circle)):
        return False  
    (cx, cy), radius = circle
    if check_point_in_triangle((cx, cy), triangle):
        return True
    ta1, ta2, ta3 = triangle
    return any(get_collision_point_of_segment_and_circle(segment, circle) 
               for segment in [(ta1, ta2), (ta2, ta3), (ta3, ta1)])

def get_collision_point_of_segment_and_circle(segment, circle):
    if not may_overlap([segment], get_circle_boundaries(circle)):
        return False  
    (x0, y0), (x1, y1) = segment    
    m_perpendicular = (x1 - x0) / (y0 - y1)
    alpha = math.atan(m_perpendicular)
    kx = radius * math.cos(alpha)
    ky = radius * math.sin(alpha)
    (cx, cy), radius = circle
    perpendicular_segment = ((cx + kx, cy + ky), (cx - kx, cy - ky))
    return get_collision_point_of_segments(segment, perpendicular_segment)

def get_collision_point_of_segments(segment1, segment2):
    """Return point of collision of 2 segments (None if no collision)."""
    if not may_overlap(segment1, segment2):
        return
    (x1a, y1a), (x1b, y1b) = segment1
    (x2a, y2a), (x2b, y2b) = segment2
    m1 = (y1b - y1a) / (x1b - x1a)
    m2 = (y2b - y2a) / (x2b - x2a)
    xcol = (y2a - y1a + m1*x1a - m2*x2a) / (m1 - m2)
    if xcol >= x1a and xcol <= x1b:
        ycol = m1 * (xcol - x1a) + y1a
        return xcol, ycol
