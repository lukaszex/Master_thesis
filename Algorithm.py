from Population import *
import multiprocessing

class Algorithm:
    def __init__(self, type_, topology_, migrationFrequency_, migrationNumber_):
        self.type = type_
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
        self.migrationNumber = migrationNumber_

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
        jobs = []
        for pop in self.populations:
            j = multiprocessing.Process(target = pop.processPopulation)
            jobs.append(j)
            j.start()
        for j in jobs:
            j.join()

if __name__ == '__main__':
    alg = Algorithm('normal', '1wayCircle', 5, 2)
    cities_ = readData('test1')
    alg.initialize(cities_)
    for it in range(5):
        alg.processPopulations()
        print('\n\n\n')
    pass