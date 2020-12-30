import random

def getMutPoints(length):
    gene1 = random.randint(0, length - 1)
    gene2 = random.randint(0, length - 1)
    mutpoint1 = min(gene1, gene2)
    mutpoint2 = max(gene1, gene2)
    if mutpoint2 == mutpoint1:
        if mutpoint2 < length:
            mutpoint2 += 1
        else:
            mutpoint1 -= 1
    return mutpoint1, mutpoint2

def mutationSwap(child):
    mutpoint1, mutpoint2 = getMutPoints(len(child))
    child[mutpoint1], child[mutpoint2] = child[mutpoint2], child[mutpoint1]
    return child

def mutationInsert(child):
    mutpoint1, mutpoint2 = getMutPoints(len(child))
    transfered = child[mutpoint2]
    del(child[mutpoint2])
    child.insert(mutpoint1 + 1, transfered)
    return child

def mutationScramble(child):
    mutpoint1, mutpoint2 = getMutPoints(len(child))
    scrambledPart = child[mutpoint1:mutpoint2 + 1]
    random.shuffle(scrambledPart)
    child[mutpoint1:mutpoint2 + 1] = scrambledPart
    return child

def mutationInversion(child):
    mutpoint1, mutpoint2 = getMutPoints(len(child))
    inversedPart = child[mutpoint1:mutpoint2 + 1]
    inversedPart.reverse()
    child[mutpoint1:mutpoint2 + 1] = inversedPart
    return child


if __name__ == '__main__':
    mutationInversion([1, 2, 3, 4, 5, 6, 7])