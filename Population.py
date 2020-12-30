from readData import *
import pandas as pd
import numpy as np
import random

class Population:
    def __init__(self, populationID_, generationNumber_, cities_, numberOfSpecimen_, type_, tournamentSize_, p_m_,
                 eliteSize_, migrationSize_):
        self.populationID = populationID_
        self.generationNumber = generationNumber_
        self.cities = cities_
        self.numberOfSpecimen = numberOfSpecimen_
        self.type = type_
        self.tournamentSize = tournamentSize_
        self.p_m = p_m_
        self.eliteSize = eliteSize_
        self.migrationSize = migrationSize_
        self.specimen = pd.DataFrame()
        self.parents = pd.DataFrame()
        self.children = pd.DataFrame()

    def createInitialPopulation(self):
        for i in range(self.numberOfSpecimen):
            route = np.array(random.sample(self.cities.keys(), len(self.cities.keys())))
            route = pd.Series(route)
            self.specimen = self.specimen.append(route, ignore_index = True)

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
        self.children = self.parents.iloc[0:self.eliteSize, :]
        crossMethod = random.choice(['pmx', 'ox', 'cx'])
        if crossMethod == 'pmx':
            crossoverPMX()
        elif crossMethod == 'ox':
            crossoverOX()
        elif crossMethod == 'cx':
            crossoverCX()

    def evaluate(self):
        self.specimen.insert(len(self.specimen.columns), 'fitness', np.zeros(self.specimen.shape[0], dtype = np.float))
        for i in range(self.numberOfSpecimen):
            length = 0
            for j in range(len(self.cities)):
                if j + 1 < len(self.cities):
                    destCityIndex = j + 1
                else:
                    destCityIndex = 0
                length += calculateDistance(self.cities[self.specimen.iloc[i, j]], self.cities[self.specimen.iloc[i, destCityIndex]])
                self.specimen.iloc[i, -1] = length
        self.specimen.sort_values(by = 'fitness', inplace = True)


if __name__ == '__main__':
    cities_ = readData('test2')
    pop = Population(1, 1, cities_, 100, 'normal', 5, 0.01, 10, 4)
    pop.createInitialPopulation()
    pop.evaluate()
    pop.selectParents()
    pop.crossover()
