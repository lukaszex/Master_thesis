from Population import *
import multiprocessing as mp

class Algorithm:
    def __init__(self, type_, topology_, migrationFrequency_, migrationSize_):
        self.type = type_
        self.generationNumber = 0
        if topology_ == '1wayCircle':
            self.topology = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 0}
        elif topology_ == '2waysCircle':
            self.topology = {0: [1, 7], 1: [0, 2], 2: [1, 3], 3: [2, 4], 4: [3, 5], 5: [4, 6], 6: [5, 7], 7: [6, 0]}
        elif topology_ == '1+2circle':
            self.topology = {0: [1, 2], 1: [2, 3], 2: [3, 4], 3: [4, 5], 4: [5, 6], 5: [6, 7], 6: [7, 0], 7: [0, 1]}
        elif topology_ == '2+3circle':
            self.topology = {0: [2, 3], 1: [3, 4], 2: [4, 5], 3: [5, 6], 4: [6, 7], 5: [7, 0], 6: [0, 1], 7: [1, 2]}
        elif topology_ == 'ladder':
            self.topology = {0: [1, 2], 1: [0, 3], 2: [3, 4], 3: [2, 5], 4: [5, 6], 5: [4, 7], 6: [7, 0], 7: [6, 1]}
        elif topology_ == 'hierarchical':
            self.topology = {0: 4, 1: 4, 2: 5, 3: 5, 4: 6, 5: 6}
        self.migrationFrequency = migrationFrequency_
        self.migrationSize = migrationSize_

    def initialize(self, cities_):
        self.populations = []
        if self.type == 'normal':
            for popNumber in range(8):
                pop = Population(popNumber, 0, cities_, 50, 'normal', 5, 0.05, 10, 4, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                pop.createInitialPopulation()
                pop.evaluate()
                self.populations.append(pop)
        pass

    def processPopulations(self):
        manager = mp.Manager()
        retDict = manager.dict()
        jobs = []
        for pop in self.populations:
            j = mp.Process(target = pop.processPopulation, args = (retDict, ))
            jobs.append(j)
            j.start()
        for j in jobs:
            j.join()
        self.newPopulations = []
        self.generationNumber += 1
        for pop in retDict.values():
            newPop = Population(pop.populationID, self.generationNumber, cities_, pop.numberOfSpecimen, pop.type, pop.tournamentSize,
                                pop.p_m, pop.eliteSize, pop.migrationSize, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff,
                                pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion, pop.swapEff,
                                pop.insertEff, pop.scrambleEff, pop.inversionEff)
            self.newPopulations.append(newPop)
        self.populations = self.newPopulations
        self.populations.sort(key = lambda x: x.populationID)
        pass

    def migrate(self):
        print('===MIGRATION===')
        for ID, pop in enumerate(self.populations):
            pop.selectSpecimenForMigration()
            targetIDs = list(self.topology[ID])
            splittedMigrating = np.array_split(pop.migrating, len(targetIDs))
            i = 0
            for ID in targetIDs:
                self.populations[ID].specimen = self.populations[ID].specimen.append(splittedMigrating[i], ignore_index = True)
                self.populations[ID].specimen.sort_values(by = 'fitness', inplace = True)
                i += 1
            pass
        pass


if __name__ == '__main__':
    alg = Algorithm('normal', '2waysCircle', 5, 2)
    cities_ = readData('test1')
    alg.initialize(cities_)
    for it in range(2):
        alg.processPopulations()
        print('\n\n\n')
    alg.migrate()
    pass