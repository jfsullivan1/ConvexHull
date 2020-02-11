import math
import sys
import copy
from hypothesis import given
import hypothesis.strategies as st
EPSILON = sys.float_info.epsilon

@given(st.lists(st.tuples(st.integers(0,1000000), st.integers(0,1000000))), 3, None, None, True)


def yint(p1, p2, x, y3, y4):
	"""
	Given two points, p1 and p2, an x coordinate, x, and y coordinates y3 and
	y4, compute and return the (x,y) coordinates of the y intercept of the
	line segment p1->p2 with the line segment (x,y3)->(x,y4)
	"""
	x1, y1 = p1
	x2, y2 = p2
	x3 = x
	x4 = x
	px = ((x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / \
		float((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
	py = ((x1*y2 - y1*x2)*(y3-y4) - (y1 - y2)*(x3*y4 - y3*x4)) / \
		float((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3-x4))
	return px, py


def triangleArea(a, b, c):
	"""
	Given three points a,b,c, computes and returns the area defined by the
	triangle a,b,c. Note that this area will be negative  if a,b,c represents
	a clockwise sequence, positive if it is counter-clockwise, and zero if
	the points are collinear.
	"""
	return (a[0]*b[1] - a[1]*b[0] + a[1]*c[0]
			- a[0]*c[1] + b[0]*c[1] - c[0]*b[1]) / 2.0


def cw(a, b, c):
	"""
	Given three points a,b,c, returns True if and only if  a,b,c represents a
	clockwise sequence (subject to floating-point precision)
	"""
	return triangleArea(a, b, c) < -EPSILON


def ccw(a, b, c):
	"""
	Given three points a,b,c, returns True if and only if  a,b,c represents a
	counter-clockwise sequence (subject to floating-point precision)
	"""
	return triangleArea(a, b, c) > EPSILON


def collinear(a, b, c):
	"""
	Given three points a,b,c, returns True if and only if  a,b,c are collinear
	(subject to floating-point precision)
	"""
	return abs(triangleArea(a, b, c)) <= EPSILON


def clockwiseSort(points):
	"""
	Given a list of points, sort those points in clockwise order about their
	centroid.
	Note: this function modifies its argument.
	"""
	# get mean x coord, mean y coord
	xavg = sum(p[0] for p in points) / len(points)
	yavg = sum(p[1] for p in points) / len(points)
	angle = lambda p:  ((math.atan2(p[1] - yavg, p[0] - xavg) + 2*math.pi) % (2*math.pi))
	points.sort(key=angle)


def computeHull(points):
	"""
	Replace the implementation of computeHull with a correct computation of
	the convex hull using the divide-and-conquer algorithm
	"""
	newpoints = copy.deepcopy(points)
	#if (len(newpoints) <= 6):
	naiveHull(newpoints)
	#else:
		#divAndConquer(newpoints)
	return newpoints


def naiveHull(points):
	"""
	Brute force Convex Hull solve
	Given a list of points, return a list of points in clockwise order that
	represents the convex hull of the points.
	"""

	clockwiseSort(points)
	pointslength = len(points)

	notAllConvexAngles = True
	# Keep looping through the points until no concave angles are found
	while notAllConvexAngles:
		count = 0
		i = 0
		while i < pointslength:
			# we will take advantage of the fact that a triangle area that is
			# negative means that the tree points for a concave ange and the
			# vertex (second point) should be removed from the list of points
			triangle_area = triangleArea(points[i], points[(i + 1) % pointslength],
										 points[(i + 2) % pointslength])
			# If triangle area is negative, remove the middle point

			# If we have a line of points, we will skip it because
			# we know it's part of the hull
			isCollinear = collinear(points[i], points[(i+1) % pointslength],
							points[(i+2) % pointslength])
			
			# We don't have to execute this conditional if it's collinear. 
			if not isCollinear:
				if triangle_area <= 0:
					points.pop((i + 1) % pointslength)
					pointslength -= 1
					count += 1
					notAllConvexAngles = True
			i += 1
		if count == 0:
			notAllConvexAngles = False
	return points


#def divAndConquer(points):
