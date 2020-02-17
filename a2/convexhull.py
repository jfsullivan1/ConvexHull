import math
import sys
import copy
import operator
from hypothesis import given
import hypothesis.strategies as st
import random
import time
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
	hull = getHull(points)
	#print(checkHull(hull, points))
	return hull
	

def getHull(points):
	newpoints = copy.deepcopy(points)
	if (len(newpoints) <= 3):
		clockwiseSort(newpoints)
		return newpoints
	if (len(newpoints) <= 9):
		return naiveHull(newpoints)
	else:
		newpointsLeft, newpointsRight = splitPoints(newpoints)
		if not newpointsLeft:
			clockwiseSort(newpointsRight)
			return newpointsRight
		if not newpointsRight:
			clockwiseSort(newpointsLeft)
			return newpointsLeft
		return merge(getHull(newpointsLeft), getHull(newpointsRight))


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
	minX = points[0][0]
	maxX = points[-1][0]
	midLine = (minX + maxX) / 2
	lengthOfList = len(points)
	leftHalf = []
	rightHalf = []

	# I split these up here so we won't get any divide by zero errors, although I kept try catches in my merge code just incase.
	for i in range(0, lengthOfList):
		if points[i][0] <= midLine:
			leftHalf.append(points[i])
		if points[i][0] > midLine:
			rightHalf.append(points[i])
	return leftHalf, rightHalf

def merge(hullOne, hullTwo):

	leftHull = hullOne
	rightHull = hullTwo

	rightMostLeftHull = 0
	leftMostRightHull = 0

	# Find the index of the right most point on the left hull
	for index in range(len(leftHull)):
		if leftHull[index][0] > leftHull[rightMostLeftHull][0]:
			rightMostLeftHull = index

	# Find the index of the left most point on the right hull
	for index in range(len(rightHull)):
		if rightHull[index][0] < rightHull[leftMostRightHull][0]:
			leftMostRightHull = index	
	
	i = rightMostLeftHull
	j = leftMostRightHull

	# Finds the x value where we will draw a line down the middle for finding y-intercepts
	avg = ( leftHull[i][0] + rightHull[j][0] ) / 2

	# We want to find the max and min Y values so we know how long our "Y axis" is.
	# We can set our mininmum Y value to always be 0.  
	# Technically, we could just have arbitrary large Y values, but we want to be exact for big input sizes.
	minY = 0
	maxY = 0

	fullHull = leftHull + rightHull
	for xPoint in range(len(fullHull)):
		if fullHull[xPoint][1] > maxY:
			maxY = fullHull[xPoint][1]

	#Upper tangent
	upperTanFound = False
	pointSwitched = False
	while upperTanFound == False:	
		pointSwitched = False	
		try:
			if yint(leftHull[i], rightHull[((j+1) % len(rightHull))], avg, minY, maxY)[1] < yint(leftHull[i], rightHull[j], avg, minY, maxY)[1]:
				j = (j+1) % len(rightHull)
				pointSwitched = True
		except(ZeroDivisionError):
			if (rightHull[((j+1) % len(rightHull))][1] < rightHull[j][1]):
				j = (j+1) % len(rightHull)
				pointSwitched = True	
		try:
			if yint(leftHull[((i-1) % len(leftHull))], rightHull[j], avg, minY, maxY)[1] < yint(leftHull[i], rightHull[j], avg, minY, maxY)[1]:
				i = (i-1) % len(leftHull)
				pointSwitched = True
		except(ZeroDivisionError):
			if (rightHull[((j+1) % len(rightHull))][1] < rightHull[j][1]):
				i = (i-1) % len(leftHull)
				pointSwitched = True
		if pointSwitched == False:
			upperTanFound = True

	x = rightMostLeftHull
	y = leftMostRightHull

	# Lower tangent. 
	lowerTanFound = False
	pointSwitched = False
	while lowerTanFound == False:	
		pointSwitched = False	
		try:
			if yint(leftHull[((x+1) % len(leftHull))], rightHull[y], avg, minY , maxY)[1] > yint(leftHull[x], rightHull[y], avg, minY, maxY)[1]:
				x = (x+1) % len(leftHull)
				pointSwitched = True
		except(ZeroDivisionError):
			if(leftHull[((x+1) % len(leftHull))][1] < leftHull[x][1]):
				x = (x+1) % len(leftHull)
				pointSwitched = True
		try:
			if yint(leftHull[x], rightHull[((y-1) % len(rightHull))], avg, minY, maxY)[1] > yint(leftHull[x], rightHull[y], avg, minY, maxY)[1]:
				y = (y-1) % len(rightHull)
				pointSwitched = True
		except(ZeroDivisionError):
			if (rightHull[((y-1) % len(rightHull))][1] > rightHull[y][1]):
				y = (y-1) % len(rightHull)
				pointSwitched = True
			
		if pointSwitched == False:
			lowerTanFound = True

	mergedList = []
	notInHull = []

	# Remove points not in left half
	iterator = (i + 1) % len(leftHull)
	while iterator != x :
		notInHull.append(leftHull[iterator])
		iterator = (iterator + 1) % len(leftHull)
	
	# Remove points not in right half
	iterator = (y+1) % len(rightHull)
	while iterator != j:
		notInHull.append(rightHull[iterator])
		iterator = (iterator + 1) % len(rightHull)

	newHull = leftHull + rightHull
	for hullPoint in newHull:
		if hullPoint not in notInHull:
			mergedList.append(hullPoint)
	clockwiseSort(mergedList)
	return mergedList

# This was for testing purposes, leaving it just in case TA's want to use it to benchmark 

#if __name__ == "__main__":
	#points = []
	#for i in range(0, 120000):
		#tup = ((random.randint(1,120000)), random.randint(1,120000))
		#points.append(tup)
	#stopwatch = time.time()
	#naiveHull(points)
	#sys.stderr.write(" ========== Benchmark Time NAIVE: %s sec. ==========\n" %(time.time() - stopwatch))
	#stopwatch = time.time()
	#computeHull(points)
	#sys.stderr.write(" ========== Benchmark Time DIVIDE&CONQ: %s sec. ==========\n" %(time.time() - stopwatch))