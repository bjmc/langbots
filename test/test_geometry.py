#!/usr/bin/python
import unittest
import sys
import os

from langbots import geometry

class TestShapes(unittest.TestCase):
    def test_cross_product(self):
        self.assertEqual(geometry.cross_product((1, 2), (3, 4)), 1*4-2*3)
        self.assertEqual(geometry.cross_product((3, -2), (1, -1)), 3*(-1)-(-2)*(1))
                            
    def test_may_overlpap(self):
        self.assertFalse(geometry.may_overlap([(0, 0)], [(1, 1)]))
        rhombus = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.assertFalse(geometry.may_overlap(rhombus, [(1, 1.01)]))
        self.assertFalse(geometry.may_overlap(rhombus, [(1.01, 1.0)]))
        self.assertTrue(geometry.may_overlap(rhombus, [(1, 0.9)]))
        self.assertTrue(geometry.may_overlap(rhombus, [(1, -0.9)]))
        self.assertTrue(geometry.may_overlap(rhombus, [(-1, 0.9)]))
        self.assertTrue(geometry.may_overlap(rhombus, [(-1, -0.9)]))        
        self.assertTrue(geometry.may_overlap(rhombus, [(1.01, 1.0), (-1, -0.9)]))
        
    def test_check_point_in_triangle(self):
        triangle = [(-2.0, 0.0), (0.0, -1.0), (1.0, 1.0)]
        outside_points = [(2.0, 1.0), (0.0, 1.0), (1.0, 0.9), (-1.0, -0.6)]
        for out_point in outside_points:
            self.assertFalse(geometry.check_point_in_triangle(out_point, triangle))
        inside_points = [(0.0, 0.0), (0.0, 0.5), (0.5, 0.75), (-1.0, -0.4)]
        for in_point in inside_points:
            self.assertTrue(geometry.check_point_in_triangle(in_point, triangle))
            
    def test_check_collision_of_triangles(self):
        triangle1 = [(-2.0, 0.0), (0.0, -1.0), (1.0, 1.0)]                            
        self.assertFalse(geometry.check_collision_of_triangles(triangle1,
            [(0.0, -1.1), (1.0, 0.0), (2.0, 0.0)]))
        self.assertTrue(geometry.check_collision_of_triangles(triangle1,
            [(-1.0, 0.0), (0.0, 1.0), (0.0, 2.0)]))

    def test_get_direction_for_rotation(self):
        self.assertEqual(geometry.get_direction_for_rotation(45, 60), +1)            
        self.assertEqual(geometry.get_direction_for_rotation(45, 160), +1)
        self.assertEqual(geometry.get_direction_for_rotation(45, 200), +1)
        self.assertEqual(geometry.get_direction_for_rotation(45, -190), +1)
        self.assertEqual(geometry.get_direction_for_rotation(45, -100), -1)
        self.assertEqual(geometry.get_direction_for_rotation(45, -20), -1)
        self.assertEqual(geometry.get_direction_for_rotation(150, 360.0), -1)
        
if __name__ == '__main__':
    unittest.main()
