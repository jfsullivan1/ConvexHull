from convexhull import computeHull
import random
import time

def main():
    points = []

    for x in range(320000):
        randy = (random.randint(1,10000000), random.randint(1,10000000))
        points.append(randy) 
    start = time.process_time()
    computeHull(points)
    print(time.process_time() - start)

main()
