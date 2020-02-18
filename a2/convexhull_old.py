import math
import sys
import copy
import operator
from itertools import cycle, islice
#from hypothesis import given
#import hypothesis.strategies as st
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
	Computation of the convex hull with a divide-and-conquer algorithm
	"""
	newpoints = copy.deepcopy(points)
	if (len(newpoints) <= 900000000):
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
	sortByX(points)
	lengthOfList = len(points)
	leftHalf = points[0:(lengthOfList//2)]
	rightHalf = points[(lengthOfList//2)::]
	#clockwiseSort(leftHalf)
	#clockwiseSort(rightHalf)
	
	return leftHalf, rightHalf

def merge(hullOne, hullTwo):
	leftHull = hullOne
	rightHull = hullTwo

	leftHullForComputations = copy.deepcopy(leftHull)
	rightHullForComputations = copy.deepcopy(rightHull)
	#Sort so we can find the leftmost and rightmost points
	sortByX(leftHullForComputations)
	sortByX(rightHullForComputations)

	
	#Find the leftmost and rightmost points 
	rightMostLeftHull = leftHullForComputations[-1]
	leftMostRightHull = rightHullForComputations[0]

	# i = rightMostLeftHull
	# j = leftMostRightHull

	# Finds the x value where we will draw a line down the middle for finding y-intercepts
	yAxis = (rightMostLeftHull[0] + leftMostRightHull[0]) // 2

	# We want to find the max and min Y values so we know how long our "Y axis" is.
	# We can set our mininmum Y value to always be 0.  
	# Technically, we could just have arbitrary large Y values, but we want to be exact for big input sizes.
	minY = 0
	maxY = 0
	fullHull = leftHull + rightHull

	for xPoint in range(len(fullHull)):
		if fullHull[xPoint][1] > maxY:
			maxY = fullHull[xPoint][1]
	
	minYint = sys.maxsize
	maxYint = 0
	upperTangent = (leftHull[0], rightHull[0])
	lowerTangent = (leftHull[0], rightHull[0])

	# print(f"leftHull:  {leftHull}")
	# print(f"rightHull:  {rightHull}")
	clockwiseSort(leftHull)
	clockwiseSort(rightHull)
	# print(f"leftHullS: {leftHull}")
	# print(f"rightHullS: {rightHull}")

	# Compute the upper and lower tangents of the two hulls by brute force
	for i in range(len(leftHull)):
		for j in range(len(rightHull)):
			try:
				temp = yint(leftHull[i], rightHull[j], yAxis, minY, maxY)
			except(ZeroDivisionError):
				continue
			if temp[1] < minYint:
				minYint = temp[1]
				upperTangent = [leftHull[i], rightHull[j]]
				upperTangentIndex = (i, j)
			if temp[1] > maxYint:
				maxYint = temp[1]
				lowerTangent = [leftHull[i], rightHull[j]]
				lowerTangentIndex = (i, j)
	
	# print(f"upperTangentIndex: {upperTangentIndex}")
	# print(f"lowerTangentIndex: {lowerTangentIndex}")


	# upperTangent(point, point)
	# lowerTangent(point, point)
	# upperTangentIndex(left index, right index)


	mergedHull = []
	mergedHull.append(upperTangent[0])
	i = upperTangentIndex[1]
	while i != lowerTangentIndex[1]:
		if i == len(rightHull):
			i = 0
		else:
			mergedHull.append(rightHull[i])
			i += 1
	mergedHull.append(rightHull[i])

	i = lowerTangentIndex[0]
	while i != upperTangentIndex[0]:
		if i == len(leftHull):
			i = 0
		else:
			mergedHull.append(leftHull[i])
			i += 1


	# length = len(rightHull)
	# start = upperTangentIndex[1]
	# stop = lowerTangentIndex[1]
	# # This will be the final list to return
	# mergedHull = []
	# mergedHull.append(leftHull[upperTangentIndex[0]])
	# tempList = []

	# # create a list of points from 
	# # if stop < start
	# if(stop < start):
	# 	difference  = abs((stop+length)-start)
	# 	tempList = list(islice(rightHull, start, start+difference))

	# else:
	# 	tempList = rightHull[start:stop]

	# for i in range(len(tempList)):
	# 	mergedHull.append(tempList[i])
	
	# mergedHull.append(lowerTangent[1])

	# #######

	# length = len(rightHull)
	# start = lowerTangentIndex[0]
	# stop = upperTangentIndex[0]
	# # This will be the final list to return
	# tempList = []

	# # create a list of points from 
	# # if stop < start
	# if(stop < start):
	# 	difference  = abs((stop+length)-start)
	# 	tempList = list(islice(leftHull, start, start+difference))

	# else:
	# 	tempList = leftHull[start:stop]

	# for i in range(len(tempList)):
	# 	mergedHull.append(tempList[i])
	
	clockwiseSort(mergedHull)
	return mergedHull