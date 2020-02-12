import math
import sys
import copy
import operator
from hypothesis import given
import hypothesis.strategies as st
EPSILON = sys.float_info.epsilon

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
	if (len(newpoints) <= 6):
		return naiveHull(newpoints)
	else:
		newpointsLeft, newpointsRight = splitPoints(newpoints)
		hullOne = computeHull(newpointsLeft)
		hullTwo = computeHull(newpointsRight)
		return merge(hullOne, hullTwo)

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


def sortByX(points):
	points.sort()

def splitPoints(points):
	lengthOfList = len(points)
	leftHalf = points[0:(lengthOfList//2)]
	rightHalf = points[(lengthOfList//2)::]
	return leftHalf, rightHalf

def merge(hullOne, hullTwo):
	leftHull = copy.deepcopy(hullOne)
	rightHull = copy.deepcopy(hullTwo)

	#Sort so we can find the leftmost and rightmost points
	leftHull.sort()
	rightHull.sort()

	#Find the leftmost and rightmost points 
	rightMostLeftHull = leftHull[-1]
	leftMostRightHull = rightHull[0]

	# These are deepcopied so I can reuse them for both tangents later. 
	i = copy.deepcopy(rightMostLeftHull)
	j = copy.deepcopy(leftMostRightHull)
 
	# Finds the x value where the two hulls will be split in half (for finding y-intercepts)
	yAxis = (i[0] + j[0]) / 2

	sortedByYValueLeftHull = sorted(leftHull, key=lambda item: (-item[0], item[1]))
	sortedByYValueRightHull = sorted(rightHull, key=lambda item: (-item[0], item[1]))

	# We want to find the max and min Y values so we know how long our "Y axis" is. 
	# Technically, we could just have arbitrary large Y values, but we want to be exact for big input sizes.
	minY = 0
	maxY = 0
	minYLeft = sortedByYValueLeftHull[0][1]
	maxYLeft = sortedByYValueLeftHull[-1][1]
	minYRight = sortedByYValueRightHull[0][1]
	maxYRight = sortedByYValueRightHull[-1][1]

	if minYLeft <= minYRight:
		minY = minYLeft
	else:
		minY = minYRight

	if maxYLeft >= maxYRight:
		maxY = maxYLeft
	else:
		maxY = maxYRight

	# Seesaw algorithm (Two-finger) 
	# Upper tangent, i->j will be the upper tangent at the end of this loop. 
	while(yint(i, rightHull[(rightHull.index(j)+1) % len(rightHull)], yAxis, minY, maxY)[1] > yint(i, j, yAxis, minY, maxY)[1] or
		yint(leftHull[(leftHull.index(i)-1) % len(leftHull)], j, yAxis, minY, maxY)[1] > yint(i, j, yAxis, minY, maxY)[1]):
			if yint(i, rightHull[(rightHull.index(j)+1) % len(rightHull)], yAxis, minY, maxY)[1] > yint(i, j, yAxis, minY, maxY)[1]:
				j = rightHull[(rightHull.index(j)+1) % len(rightHull)]
			else:
				i = leftHull[(leftHull.index(i)-1) % len(leftHull)]

	x = copy.deepcopy(rightMostLeftHull)
	y = copy.deepcopy(leftMostRightHull)
	# Lower tangent. 
	while(yint(leftHull[(leftHull.index(x)+1) % len(leftHull)], y, yAxis, minY, maxY)[1] > yint(x, y, yAxis, minY, maxY)[1] or
        yint(x, rightHull[(rightHull.index(y)-1) % len(rightHull)], yAxis, minY, maxY)[1] > yint(x, y, yAxis, minY, maxY)[1]):
            if yint(leftHull[(leftHull.index(x)+1) % len(leftHull)], y, yAxis, minY , maxY)[1] > yint(x, y, yAxis, minY, maxY)[1]:
                x = leftHull[(leftHull.index(x)+1) % len(leftHull)]
            else:
                y = rightHull[(rightHull.index(y)-1) % len(rightHull)]
	

	mergedList = []
	notInHull = []

	# Remove points not in left half
	iterator = leftHull[(leftHull.index(i) + 1) % len(leftHull)]
	while iterator != x:
		notInHull.append(iterator)
		iterator = leftHull[(leftHull.index(iterator) + 1) % len(leftHull)]
	

	iterator = rightHull[(rightHull.index(y)+1) % len(rightHull)]
	while iterator != j:
		notInHull.append(iterator)
		iterator = rightHull[(rightHull.index(iterator) + 1) % len(rightHull)]

	newHull = leftHull + rightHull
	for i in newHull:
		if i not in notInHull:
			mergedList.append(i)
	
	clockwiseSort(mergedList)
	return mergedList