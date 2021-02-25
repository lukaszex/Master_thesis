from Population import *
import multiprocessing as mp
from matplotlib import pyplot as plt
import sys
import datetime
import logging

class Algorithm:
    def __init__(self, type_, topology_, migrationFrequency_, migrationSize_, cities_, numberOfGenerations_):
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
        self.cities = cities_
        self.numberOfGenerations = numberOfGenerations_
        self.populations = []
        self.stats = []
        for popID in range(8):
            self.stats.append({'best': [], 'mean': [], 'worst': [], 'stddev': []})

    def initialize(self):
        if self.type == 'normal':
            for popNumber in range(8):
                pop = Population(popNumber, 0, self.cities, 100, 'normal', 3, 0.1, 10, self.migrationSize, None)
                pop.createInitialPopulation()
                pop.evaluate()
                self.populations.append(pop)
        elif self.type == 'static':
            i = 0
            while len(self.populations) < 8:
                pop1 = Population(i, 0, self.cities, 100, 'absolute', 3, 0.1, 10, self.migrationSize, None)
                pop2 = Population(i + 1, 0, self.cities, 100, 'absolute', 3, 0.1, 10, self.migrationSize, None)
                pop1.createInitialPopulation()
                pop2.createInitialPopulation()
                pop1.evaluate()
                pop2.evaluate()
                self.populations.append(pop1)
                self.populations.append(pop2)
                i += 2
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
        logging.info('===MIGRATION===')
        for ID, pop in enumerate(self.populations):
            pop.selectSpecimenForMigration()
            pop.migrating = pop.migrating.sample(frac = 1)
            if hasattr(self.topology[ID], '__iter__'):
                targetIDs = list(self.topology[ID])
            else:
                targetIDs = [self.topology[ID]]
            splittedMigrating = np.array_split(pop.migrating, len(targetIDs))
            i = 0
            for targetID in targetIDs:
                self.populations[targetID].specimen = self.populations[targetID].specimen.append(splittedMigrating[i], ignore_index = True)
                self.populations[targetID].specimen.sort_values(by = 'fitness', inplace = True)
                i += 1
            pass
        pass

    def receiveStats(self):
        for pop in self.populations:
            if self.type == 'normal':
                data = pop.getStats()
                self.stats[pop.populationID]['best'].append(data['best'])
                self.stats[pop.populationID]['mean'].append(data['mean'])
                self.stats[pop.populationID]['worst'].append(data['worst'])
                self.stats[pop.populationID]['stddev'].append(data['stddev'])

    def setLogOutput(self):
        path = sys.path[0] + "\\logs\\" + self.type + "\\"
        fileName = str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + '.txt'
        logging.basicConfig(filename = path + fileName, filemode = 'w', level = logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    def logOutData(self):
        bestFirsts = []
        bestLasts = []
        for i in range(8):
            bestFirsts.append(self.stats[i]['best'][0])
            bestLasts.append(self.stats[i]['best'][-1])
        bestFirst = min(bestFirsts)
        bestLast = min(bestLasts)
        convs = []
        for i in range(8):
            try:
                convs.append(min([ind for ind, val in enumerate(self.stats[i]['best']) if val <= 1.05*bestLast]))
            except ValueError:
                continue
        conv = min(convs)
        logging.info('Solution value: {}, Improvement: {}, Convergence: {}'.format(bestLast, bestFirst/bestLast, conv))
        if self.type == 'normal':
            self.logOutDataNormal()

    def logOutDataNormal(self):
        pmxProc = []
        cxProc = []
        oxProc = []
        swapProc = []
        insertProc = []
        scrambleProc = []
        inversionProc = []
        for pop in self.populations:
            pmxProc.append(pop.pmxEff/pop.pmx)
            cxProc.append(pop.cxEff/pop.cx)
            oxProc.append(pop.oxEff/pop.ox)
            swapProc.append(pop.swapEff/pop.swap)
            insertProc.append(pop.insertEff/pop.insert)
            scrambleProc.append(pop.scrambleEff/pop.scramble)
            inversionProc.append(pop.inversionEff/pop.inversion)
        logging.info('PMX: {}, CX: {}, OX: {}, swap: {}, insert: {}, scramble: {}, inversion: {}'.
                     format(np.mean(pmxProc), np.mean(cxProc), np.mean(oxProc), np.mean(swapProc),
                            np.mean(insertProc), np.mean(scrambleProc), np.mean(inversionProc)))
    def plotOut(self):
        plt.figure(figsize = [30, 30])
        for i in range(8):
            plt.plot(self.stats[i]['best'], label = self.populations[i].populationID)
        plt.xlabel('Pokolenie')
        plt.ylabel('Najlepsza wartość funkcji celu')
        plt.grid()
        plt.legend()
        plt.show()
        plt.figure(figsize=[30, 30])
        for i in range(8):
            plt.plot(self.stats[i]['mean'], label=self.populations[i].populationID)
        plt.xlabel('Pokolenie')
        plt.ylabel('Średnia wartość funkcji celu')
        plt.grid()
        plt.legend()
        plt.show()
        plt.figure(figsize=[30, 30])
        stddevs = []
        for i in range(8):
            row = []
            for j in range(len(self.stats[i]['stddev'])):
                row.append(self.stats[i]['stddev'][j])
            stddevs.append(row)
        plt.plot(np.mean(stddevs, axis = 0), label = 'Średnie odchylenie standardowe wartości funkcji celu w populacjach')
        plt.xlabel('Pokolenie')
        plt.ylabel('Odchylenie standardowe wartości funkcji celu')
        plt.grid()
        plt.legend()
        plt.show()

    def run(self):
        self.setLogOutput()
        self.initialize()
        it = 1
        while it <= self.numberOfGenerations:
            logging.info('-----Generation {}-----'.format(it))
            self.processPopulations()
            for pop in self.populations:
                logging.info('Population: {}, best fitness: {}'.format(pop.populationID, pop.specimen.iloc[0, -1]))
            if it % self.migrationFrequency == 0 and it > 0:
                self.migrate()
            self.receiveStats()
            it += 1
        self.logOutData()
        self.plotOut()


if __name__ == '__main__':
    cities_ = readData('test1')
    alg = Algorithm('static', '1+2circle', 10, 10, cities_, 20)
    alg.run()
    pass