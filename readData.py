import numpy as np
def readData(fileName):
    cities = {}
    fileName += '.txt'
    with open(fileName) as f:
        lines = f.readlines()
    for line in lines:
        line = line.split()
        id = int(line[0])
        cities[id] = (float(line[1]), float(line[2]))
    return cities

def calculateDistance(city1, city2):
    return np.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)

if __name__ == '__main__':
    print(readData('test2'))