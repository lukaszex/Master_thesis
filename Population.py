from readData import *
from crossoverFunctions import *
from mutationFunctions import *
import pandas as pd
import numpy as np
import random

class Population:
    def __init__(self, populationID_, generationNumber_, cities_, numberOfSpecimen_, type_, tournamentSize_, p_m_,
                 eliteSize_, migrationSize_, specimen_, pmx_, cx_, ox_, pmxEff_, cxEff_, oxEff_, swap_, insert_, scramble_, inversion_, swapEff_, insertEff_, scrambleEff_, inversionEff_):
        self.populationID = populationID_
        self.generationNumber = generationNumber_
        self.cities = cities_
        self.numberOfSpecimen = numberOfSpecimen_
        self.type = type_
        self.tournamentSize = tournamentSize_
        self.p_m = p_m_
        self.eliteSize = eliteSize_
        self.migrationSize = migrationSize_
        if specimen_ is None:
            self.specimen = pd.DataFrame()
        else:
            self.specimen = specimen_
        self.pmx = pmx_
        self.cx = cx_
        self.ox = ox_
        self.pmxEff = pmxEff_
        self.cxEff = cxEff_
        self.oxEff = oxEff_
        self.swap = swap_
        self.insert = insert_
        self.scramble = scramble_
        self.inversion = inversion_
        self.swapEff = swapEff_
        self.insertEff = insertEff_
        self.scrambleEff = scrambleEff_
        self.inversionEff = inversionEff_
        self.parents = pd.DataFrame()
        self.childrenList = []

    def createInitialPopulation(self):
        for i in range(self.numberOfSpecimen):
            route = random.sample(self.cities.keys(), len(self.cities.keys()))
            route = pd.Series([route, np.nan])
            self.specimen = self.specimen.append(route, ignore_index = True)
        self.specimen.columns = ['solution', 'fitness']
        pass

    def selectParents(self):
        if self.type == 'normal':
            self.selectParentsNormal()
        elif self.type == 'absolute':
            self.selectParentsAbsolute()

    def selectParentsNormal(self):
        for i in range(self.numberOfSpecimen - self.eliteSize):
            tournament = self.specimen.sample(self.tournamentSize)
            tournament.sort_values(by = 'fitness', inplace = True)
            self.parents = self.parents.append(tournament.iloc[0, :])
        self.parents.sort_values(by = 'fitness', inplace = True)
        pass

    def crossover(self):
        self.specimen = self.parents.iloc[0:self.eliteSize, :]
        if self.type == 'normal':
            self.crossoverNormal()

    def crossoverNormal(self):
        for i in range(int(self.parents.shape[0] / 2)):
            parent1 = self.parents.iloc[i, 1]
            parent1Fitness = self.parents.iloc[i, 0]
            parent2 = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 1]
            parent2Fitness = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 0]
            crossMethod = random.choice(['pmx', 'ox', 'cx'])
            if crossMethod == 'pmx':
                self.pmx += 1
                child1 = crossoverPMX(parent1, parent2)
                child2 = crossoverPMX(parent2, parent1)
                child1Fitness = self.evaluateSingleSpeciman(child1)
                child2Fitness = self.evaluateSingleSpeciman(child2)
                if min([child1Fitness, child2Fitness]) < min([parent1Fitness, parent2Fitness]):
                    self.pmxEff += 1
            elif crossMethod == 'ox':
                self.ox += 1
                child1 = crossoverOX(parent1, parent2)
                child2 = crossoverOX(parent2, parent1)
                child1Fitness = self.evaluateSingleSpeciman(child1)
                child2Fitness = self.evaluateSingleSpeciman(child2)
                if min([child1Fitness, child2Fitness]) < min([parent1Fitness, parent2Fitness]):
                    self.oxEff += 1
            elif crossMethod == 'cx':
                self.cx += 1
                child1 = crossoverCX(parent1, parent2)
                child2 = crossoverCX(parent2, parent1)
                child1Fitness = self.evaluateSingleSpeciman(child1)
                child2Fitness = self.evaluateSingleSpeciman(child2)
                if min([child1Fitness, child2Fitness]) < min([parent1Fitness, parent2Fitness]):
                    self.cxEff += 1
            self.childrenList.append(child1)
            self.childrenList.append(child2)
        pass

    def mutate(self):
        if self.type == 'normal':
            self.mutateNormal()

    def mutateNormal(self):
        for child in self.childrenList:
            if random.random() < self.p_m:
                beforeFitness = self.evaluateSingleSpeciman(child)
                mutMethod = random.choice(['swap', 'insert', 'scramble', 'inversion'])
                if mutMethod == 'swap':
                    self.swap += 1
                    child = mutationSwap(child)
                    afterFitness = self.evaluateSingleSpeciman(child)
                    if afterFitness < beforeFitness:
                        self.swapEff += 1
                elif mutMethod == 'insert':
                    self.insert += 1
                    child = mutationInsert(child)
                    afterFitness = self.evaluateSingleSpeciman(child)
                    if afterFitness < beforeFitness:
                        self.insertEff += 1
                elif mutMethod == 'scramble':
                    self.scramble += 1
                    child = mutationScramble(child)
                    afterFitness = self.evaluateSingleSpeciman(child)
                    if afterFitness < beforeFitness:
                        self.scrambleEff += 1
                elif mutMethod == 'inversion':
                    self.inversion += 1
                    child = mutationInversion(child)
                    afterFitness = self.evaluateSingleSpeciman(child)
                    if afterFitness < beforeFitness:
                        self.inversionEff += 1
            child = pd.Series([child, np.nan])
            self.specimen = self.specimen.append(child, ignore_index = True)
        self.specimen.iloc[self.eliteSize:, 1] = self.specimen.iloc[self.eliteSize:, 2]
        self.specimen = self.specimen[['solution', 'fitness']]
        pass

    def evaluate(self):
        if 'fitness' not in self.specimen.columns:
            self.specimen.insert(len(self.specimen.columns), 'fitness', np.zeros(self.specimen.shape[0], dtype = np.float))
        for i in range(self.numberOfSpecimen):
            length = 0
            for j in range(len(self.cities)):
                if j + 1 < len(self.cities):
                    destCityIndex = j + 1
                else:
                    destCityIndex = 0
                length += calculateDistance(self.cities[self.specimen.iloc[i, 0][j]], self.cities[self.specimen.iloc[i, 0][destCityIndex]])
                self.specimen.iloc[i, -1] = length
        self.specimen.sort_values(by = 'fitness', inplace = True)
        print('Generation: {}, best fitness: {}'.format(self.generationNumber, self.specimen.iloc[0, -1]))
        pass

    def evaluateSingleSpeciman(self, speciman):
        length = 0
        for j in range(len(self.cities)):
            if j + 1 < len(self.cities):
                destCityIndex = j + 1
            else:
                destCityIndex = 0
            length += calculateDistance(self.cities[speciman[j]], self.cities[speciman[destCityIndex]])
        return length


if __name__ == '__main__':
    cities_ = readData('test1')
    pop = Population(1, 0, cities_, 50, 'normal', 5, 0.05, 10, 4, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    pop.createInitialPopulation()
    pop.evaluate()
    for it in range(1, 50):
        pop.selectParents()
        pop.crossover()
        pop.mutate()
        pop.evaluate()
        pop = Population(0, it, cities_, 50, 'normal', 5, 0.05, 10, 4, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff, pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion,
                         pop.swapEff, pop.insertEff, pop.scrambleEff, pop.inversionEff)
    print('PMX: {}, OX: {}, CX: {}, swap: {}, insert: {}, scramble: {}, inversion: {}'.format(pop.pmxEff/pop.pmx,
          pop.oxEff/pop.ox, pop.cxEff/pop.cx, pop.swapEff/pop.swap, pop.insertEff/pop.insert, pop.scrambleEff/pop.scramble, pop.inversionEff/pop.inversion))
