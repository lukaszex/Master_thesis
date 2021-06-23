from readData import *
from crossoverFunctions import *
from mutationFunctions import *
import pandas as pd
import numpy as np
import random

class Population:
    def __init__(self, populationID_, generationNumber_, cities_, numberOfSpecimen_, type_, tournamentSize_, p_m_,
                 eliteSize_, migrationSize_, specimen_, pmx_ = 0, cx_ = 0, ox_ = 0, pmxEff_ = 0, cxEff_ = 0, oxEff_ = 0,
                 swap_ = 0, insert_ = 0, scramble_ = 0, inversion_ = 0, swapEff_ = 0, insertEff_ = 0, scrambleEff_ = 0,
                 inversionEff_ = 0):
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
        self.meanFitness = 0

    def createInitialPopulation(self):
        for i in range(self.numberOfSpecimen):
            route = random.sample(self.cities.keys(), len(self.cities.keys()))
            route = pd.Series([route, np.nan])
            self.specimen = self.specimen.append(route, ignore_index = True)
        self.specimen.columns = ['solution', 'fitness']
        if self.type == 'empirical':
            p_m = [[random.uniform(0.05, 0.15), random.uniform(0.05, 0.15), random.uniform(0.05, 0.15),
                    random.uniform(0.05, 0.15)] for j in range(self.specimen.shape[0])]
            self.specimen.insert(2, 'p_m', p_m)
        pass

    def selectParents(self):
        if self.type in ['normal', 'empirical']:
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

    def selectParentsAbsolute(self):
        self.meanFitness = self.specimen['fitness'].mean()
        self.specimen.insert(len(self.specimen.columns), 'p_c', np.zeros(self.specimen.shape[0], dtype = np.float))
        for i in range(self.specimen.shape[0]):
            self.specimen.iloc[i, -1] = 1 - 0.5*self.generationNumber/200 if self.specimen.iloc[i, 1] >= self.meanFitness else 1
        while self.parents.shape[0] < self.numberOfSpecimen - self.eliteSize:
            specimanNumber = int(random.random()*self.numberOfSpecimen)
            if random.random() < self.specimen.iloc[specimanNumber, -1]:
                self.parents = self.parents.append(self.specimen.iloc[specimanNumber, :])
        self.parents.drop('p_c', axis = 1, inplace = True)
        self.parents.sort_values(by = 'fitness', inplace = True)
        self.specimen.drop('p_c', axis = 1, inplace = True)
        pass

    def crossover(self):
        self.specimen = self.specimen.iloc[0:self.eliteSize, :]
        if self.type == 'normal':
            self.crossoverNormal()
        elif self.type == 'absolute':
            self.crossoverAbsolute()
        elif self.type == 'empirical':
            self.crossoverEmpirical()

    def crossoverNormal(self):
        self.parents = self.parents[['solution', 'fitness']]
        for i in range(int(self.parents.shape[0] / 2)):
            parent1 = self.parents.iloc[i, 0]
            parent1Fitness = self.parents.iloc[i, 1]
            parent2 = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 0]
            parent2Fitness = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 1]
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

    def crossoverAbsolute(self):
        self.parents = self.parents[['solution', 'fitness']]
        for i in range(int(self.parents.shape[0] / 2)):
            parent1 = self.parents.iloc[i, 0]
            parent2 = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 0]
            child1 = crossoverOX(parent1, parent2)
            child2 = crossoverOX(parent2, parent1)
            self.childrenList.append(child1)
            self.childrenList.append(child2)
        pass

    def crossoverEmpirical(self):
        #self.parents = self.parents[['fitness', 'p_m', 'solution']]
        if 'p_m' not in self.parents.columns:
            self.parents.insert(1, 'p_m', np.zeros(self.parents.shape[0], dtype = np.float))
        for i in range(int(self.parents.shape[0] / 2)):
            parent1Params = self.parents.iloc[i, 1]
            if type(parent1Params) is not list:
                parent1Params = [random.uniform(0.05, 0.15), random.uniform(0.05, 0.15), random.uniform(0.05, 0.15),
                                           random.uniform(0.05, 0.15)]
            parent1 = self.parents.iloc[i, 2]
            parent2Params = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 1]
            if type(parent2Params) is not list:
                parent2Params = [random.uniform(0.05, 0.15), random.uniform(0.05, 0.15), random.uniform(0.05, 0.15),
                                           random.uniform(0.05, 0.5)]
            parent2 = self.parents.iloc[self.numberOfSpecimen - self.eliteSize - i - 1, 2]
            child1Params, child2Params = crossoverParams(parent1Params, parent2Params)
            child1 = crossoverOX(parent1, parent2)
            child2 = crossoverOX(parent2, parent1)
            self.childrenList.append([child1, child1Params])
            self.childrenList.append([child2, child2Params])
        pass

    def mutate(self):
        if self.type == 'normal':
            self.mutateNormal()
        elif self.type == 'absolute':
            self.mutateAbsolute()
        elif self.type == 'empirical':
            self.mutateEmpirical()

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
            child = pd.Series({'solution': child, 'fitness': np.nan})
            self.specimen = self.specimen.append(child, ignore_index = True)
        pass

    def mutateAbsolute(self):
        for child in self.childrenList:
            fitness = self.evaluateSingleSpeciman(child)
            p_m = 0.01 + 0.09*self.generationNumber/200 if fitness >= self.meanFitness else 0.01
            if random.random() < p_m:
                self.inversion += 1
                child = mutationInversion(child)
            child = pd.Series({'solution': child, 'fitness': np.nan})
            self.specimen = self.specimen.append(child, ignore_index = True)
        pass

    def mutateEmpirical(self):
        for child in self.childrenList:
            for param in child[1]:
                if random.random() < param:
                    param += random.uniform(-0.01, 0.01)
        for child in self.childrenList:
            mutType = random.choices(['swap', 'insert', 'scramble', 'inversion'], child[1])
            if mutType == ['swap']:
                if random.random() < child[1][0]:
                    self.swap += 1
                    child[0] = mutationSwap(child[0])
            elif mutType == ['insert']:
                if random.random() < child[1][1]:
                    self.insert += 1
                    child[0] = mutationInsert(child[0])
            elif mutType == ['scramble']:
                if random.random() < child[1][2]:
                    self.scramble += 1
                    child[0] = mutationScramble(child[0])
            elif mutType == ['inversion']:
                if random.random() < child[1][3]:
                    self.inversion += 1
                    child[0] = mutationInversion(child[0])
            child = pd.Series({'solution': child[0], 'fitness': np.nan, 'p_m': child[1]})
            self.specimen = self.specimen.append(child, ignore_index = True)
        pass

    def evaluate(self):
        if 'fitness' not in self.specimen.columns:
            self.specimen.insert(len(self.specimen.columns), 'fitness', np.zeros(self.specimen.shape[0], dtype = np.float))
        if self.type in ['normal', 'absolute']:
            self.specimen = self.specimen[['solution', 'fitness']]
        elif self.type == 'empirical':
            self.specimen = self.specimen[['solution', 'fitness', 'p_m']]
        for i in range(self.numberOfSpecimen):
            self.specimen.iloc[i, 1] = self.evaluateSingleSpeciman(self.specimen.iloc[i, 0])
        self.specimen.sort_values(by = 'fitness', inplace = True)
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

    def processPopulation(self, retDict):
        self.selectParents()
        self.crossover()
        self.mutate()
        self.evaluate()
        retDict[self.populationID] = self

    def selectSpecimenForMigration(self):
        self.migrating = self.specimen.sample(self.migrationSize)
        self.specimen.drop(self.migrating.index, inplace = True)
        self.migrating = self.migrating[['solution', 'fitness']]

    def getStats(self):
        stats = {'best': self.specimen['fitness'].min(), 'mean': self.specimen['fitness'].mean(),
                 'worst': self.specimen['fitness'].max(), 'stddev': self.specimen['fitness'].std(),
                 'mutations': self.swap + self.insert + self.scramble + self.inversion, 'type': self.type}
        if self.type == 'empirical':
            stats['mutProbs'] = (np.mean(self.specimen.iloc[:, 2][0]), np.mean(self.specimen.iloc[:, 2][1]),
                                 np.mean(self.specimen.iloc[:, 2][2]), np.mean(self.specimen.iloc[:, 2][3]))
        return stats

if __name__ == '__main__':
    cities_ = readData('test1')
    pop = Population(1, 1, cities_, 50, 'normal', 5, 0.05, 10, 4, None)
    pop.createInitialPopulation()
    pop.evaluate()
    for it in range(2, 10):
        pop.selectParents()
        pop.crossover()
        pop.mutate()
        pop.evaluate()
        pop = Population(0, it, cities_, 50, 'absolute', 5, 0.05, 10, 4, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff, pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion,
                         pop.swapEff, pop.insertEff, pop.scrambleEff, pop.inversionEff)
    print('PMX: {}, OX: {}, CX: {}, swap: {}, insert: {}, scramble: {}, inversion: {}'.format(pop.pmxEff/pop.pmx,
          pop.oxEff/pop.ox, pop.cxEff/pop.cx, pop.swapEff/pop.swap, pop.insertEff/pop.insert, pop.scrambleEff/pop.scramble, pop.inversionEff/pop.inversion))
