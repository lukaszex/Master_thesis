import random

def getXPoints(length):
    gene1 = random.randint(0, length)
    gene2 = random.randint(0, length)
    xpoint1 = min(gene1, gene2)
    xpoint2 = max(gene1, gene2)
    if xpoint2 == xpoint1:
        if xpoint2 < length:
            xpoint2 += 1
        else:
            xpoint1 -= 1
    return xpoint1, xpoint2

def crossoverPMX(parent1, parent2):
    child = [None]*len(parent1)
    xpoint1, xpoint2 = getXPoints(len(parent1))
    child[xpoint1:xpoint2] = parent1[xpoint1:xpoint2]
    for i, elem in enumerate(parent2[xpoint1:xpoint2]):
        ind = i + xpoint1
        if elem not in child:
            while child[ind] is not None:
                ind = parent2.index(child[ind])
            child[ind] = elem
    for i in range(len(child)):
        if child[i] is None:
            child[i] = parent2[i]
    return child

def crossoverOX(parent1, parent2):
    child = [None] * len(parent1)
    xpoint1, xpoint2 = getXPoints(len(parent1))
    child[xpoint1:xpoint2] = parent1[xpoint1:xpoint2]
    ind1 = xpoint2
    ind2 = xpoint2
    l = len(parent1)
    while None in child:
        if parent2[ind1 % l] not in child:
            child[ind2 % l] = parent2[ind1 % l]
            ind2 += 1
        ind1 += 1
    return child

def crossoverCX(parent1, parent2):
    child = [None]*len(parent1)
    cycles = [-1]*len(parent1)
    while -1 in cycles:
        newCycleNumber = max(cycles) + 1
        startInd = cycles.index(-1)
        indices = []
        ind = startInd
        while ind not in indices:
            cycles[ind] = newCycleNumber
            indices.append(ind)
            ind = parent2.index(parent1[ind])
    cyclesSet = set(cycles)
    for cycle in cyclesSet:
        cycleIndices = [i for i, elem in enumerate(cycles) if elem == cycle]
        for cycleIndex in cycleIndices:
            if cycle % 2 == 0:
                child[cycleIndex] = parent1[cycleIndex]
            else:
                child[cycleIndex] = parent2[cycleIndex]
        pass
    return child


if __name__ == '__main__':
    print(crossoverCX([4, 3, 6, 7, 5, 2, 1], [1, 2, 3, 4, 5, 6, 7]))