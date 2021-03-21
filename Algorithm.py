from Population import *
import multiprocessing as mp
from matplotlib import pyplot as plt
import sys
import datetime
import logging

colors = {'normal': 'black', 'absolute': 'red', 'empirical': 'blue'}

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
             self.stats.append({'best': [], 'mean': [], 'worst': [], 'stddev': [], 'mutations': [], 'mutProbs': [], 'type': []})

    def initialize(self):
        if self.type == 'normal':
            for popNumber in range(8):
                pop = Population(popNumber, 0, self.cities, 100, 'normal', 3, 0.2, 10, self.migrationSize, None)
                pop.createInitialPopulation()
                pop.evaluate()
                self.populations.append(pop)
        elif self.type in ['static', 'dynamic']:
            pop0 = Population(0, 0, self.cities, 100, 'absolute', 3, None, 10, self.migrationSize, None)
            pop1 = Population(1, 0, self.cities, 100, 'empirical', 3, None, 10, self.migrationSize, None)
            pop2 = Population(2, 0, self.cities, 100, 'normal', 3, 0.2, 10, self.migrationSize, None)
            pop3 = Population(3, 0, self.cities, 100, 'absolute', 3, None, 10, self.migrationSize, None)
            pop4 = Population(4, 0, self.cities, 100, 'empirical', 3, None, 10, self.migrationSize, None)
            pop5 = Population(5, 0, self.cities, 100, 'normal', 3, 0.2, 10, self.migrationSize, None)
            pop6 = Population(6, 0, self.cities, 100, 'absolute', 3, None, 10, self.migrationSize, None)
            pop7 = Population(7, 0, self.cities, 100, 'empirical', 3, None, 10, self.migrationSize, None)
            self.populations = [pop0, pop1, pop2, pop3, pop4, pop5, pop6, pop7]
            for pop in self.populations:
                pop.createInitialPopulation()
                pop.evaluate()
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
        #if self.type in ['normal', 'static']:
        for pop in retDict.values():
            newPop = Population(pop.populationID, self.generationNumber, cities_, pop.numberOfSpecimen, pop.type, pop.tournamentSize,
                                pop.p_m, pop.eliteSize, pop.migrationSize, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff,
                                pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion, pop.swapEff,
                                pop.insertEff, pop.scrambleEff, pop.inversionEff)
            self.newPopulations.append(newPop)
        # elif self.type == 'dynamic':
        #     for pop in retDict.values():
        #         if (self.generationNumber > self.migrationFrequency and
        #                 pop.specimen['fitness'].min() >= self.stats[pop.populationID]['best'][self.generationNumber - self.migrationFrequency]):
        #             logging.info('Population {} - change of type'.format(pop.populationID))
        #

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

    def changeType(self):
        self.newPopulations = []
        for pop in self.populations:
            if pop.specimen['fitness'].min() >= 0.95*self.stats[pop.populationID]['best'][self.generationNumber - self.migrationFrequency]:
                logging.info('Population {} - change of type'.format(pop.populationID))
                newType = pop.type
                while newType == pop.type:
                    newType = random.choice(['normal', 'absolute', 'empirical'])
                if newType == 'normal':
                    newPop = Population(pop.populationID, self.generationNumber, self.cities, pop.numberOfSpecimen, 'normal',
                                     3, 0.1, 10, self.migrationSize, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff,
                                     pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion, pop.swapEff,
                                     pop.insertEff, pop.scrambleEff, pop.inversionEff)
                elif newType == 'absolute':
                    newPop = Population(pop.populationID, self.generationNumber, self.cities, pop.numberOfSpecimen, 'absolute',
                                     3, None, 10, self.migrationSize, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff,
                                     pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion,
                                     pop.swapEff, pop.insertEff, pop.scrambleEff, pop.inversionEff)
                elif newType == 'empirical':
                    newPop = Population(pop.populationID, self.generationNumber, self.cities, pop.numberOfSpecimen, 'empirical',
                                     3, None, 10, self.migrationSize, pop.specimen, pop.pmx, pop.cx, pop.ox, pop.pmxEff,
                                     pop.cxEff, pop.oxEff, pop.swap, pop.insert, pop.scramble, pop.inversion,
                                     pop.swapEff, pop.insertEff, pop.scrambleEff, pop.inversionEff)
            else:
                newPop = pop
            self.newPopulations.append(newPop)
        self.populations = self.newPopulations
        pass

    def receiveStats(self):
        for pop in self.populations:
            data = pop.getStats()
            self.stats[pop.populationID]['best'].append(data['best'])
            self.stats[pop.populationID]['mean'].append(data['mean'])
            self.stats[pop.populationID]['worst'].append(data['worst'])
            self.stats[pop.populationID]['stddev'].append(data['stddev'])
            self.stats[pop.populationID]['mutations'].append(data['mutations'])
            self.stats[pop.populationID]['type'].append(data['type'])
            if pop.type == 'empirical':
                self.stats[pop.populationID]['mutProbs'].append(data['mutProbs'])

    def setLogOutput(self):
        path = sys.path[0] + "\\logs\\" + self.type + "\\"
        fileName = str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + '.txt'
        logging.basicConfig(filename = path + fileName, filemode = 'w', level = logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    def logOutData(self):
        bestFirst = min([self.stats[i]['best'][0] for i in range(8)])
        bestLast = min([self.stats[i]['best'][-1] for i in range(8)])
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
        pmxProc = [pop.pmxEff/pop.pmx for pop in self.populations]
        cxProc = [pop.cxEff/pop.cx for pop in self.populations]
        oxProc = [pop.oxEff/pop.ox for pop in self.populations]
        swapProc = [pop.swapEff/pop.swap for pop in self.populations]
        insertProc = [pop.insertEff/pop.insert for pop in self.populations]
        scrambleProc = [pop.scrambleEff/pop.scramble for pop in self.populations]
        inversionProc = [pop.inversionEff/pop.inversion for pop in self.populations]
        logging.info('PMX: {}, CX: {}, OX: {}, swap: {}, insert: {}, scramble: {}, inversion: {}'.
                     format(np.mean(pmxProc), np.mean(cxProc), np.mean(oxProc), np.mean(swapProc),
                            np.mean(insertProc), np.mean(scrambleProc), np.mean(inversionProc)))
    def plotOut(self):
        self.plotBest()
        self.plotMean()
        self.plotStddev()
        if self.type in ['static', 'dynamic']:
            self.plotMutations()
            self.plotMutProbs()
        if self.type == 'dynamic':
            self.plotTypes()

    def plotBest(self):
        plt.figure(figsize = [30, 30])
        for i in range(8):
            plt.plot(self.stats[i]['best'], label = '{} ({})'.
                     format(self.populations[i].populationID, self.populations[i].type),
                     color = colors[self.populations[i].type])
        plt.xlabel('Pokolenie')
        plt.ylabel('Najlepsza wartość funkcji celu')
        plt.grid()
        plt.legend()
        plt.show()

    def plotMean(self):
        plt.figure(figsize=[30, 30])
        for i in range(8):
            plt.plot(self.stats[i]['mean'], label = '{} ({})'.
                     format(self.populations[i].populationID, self.populations[i].type),
                     color = colors[self.populations[i].type])
        plt.xlabel('Pokolenie')
        plt.ylabel('Średnia wartość funkcji celu')
        plt.grid()
        plt.legend()
        plt.show()

    def plotStddev(self):
        plt.figure(figsize=[30, 30])
        for i in range(8):
            plt.plot(pd.Series(self.stats[i]['stddev']).rolling(window = 5).mean(), label = '{} ({})'.
                     format(self.populations[i].populationID, self.populations[i].type),
                     color = colors[self.populations[i].type])
        plt.xlabel('Pokolenie')
        plt.ylabel('Odchylenie standardowe wartości funkcji celu')
        plt.grid()
        plt.legend()
        plt.show()

    def plotMutations(self):
        plt.figure(figsize=[30, 30])
        for i in range(8):
            mutations = [self.stats[i]['mutations'][j] - self.stats[i]['mutations'][j - 1] for j in range(1, len(self.stats[i]['mutations']))]
            plt.plot(pd.Series(mutations).rolling(window = 5).mean(), label = '{} ({})'.
                     format(self.populations[i].populationID, self.populations[i].type),
                     color = colors[self.populations[i].type])
        plt.xlabel('Pokolenie')
        plt.ylabel('Liczba mutacji')
        plt.grid()
        plt.legend()
        plt.show()

    def plotMutProbs(self):
        plt.figure(figsize = [30, 30])
        swapProbs = pd.Series([self.stats[1]['mutProbs'][i][0] for i in range(len(self.stats[1]['mutProbs']))]).fillna(method = 'ffill')
        insertProbs = pd.Series([self.stats[1]['mutProbs'][i][1] for i in range(len(self.stats[1]['mutProbs']))]).fillna(method = 'ffill')
        scrambleProbs = pd.Series([self.stats[1]['mutProbs'][i][2] for i in range(len(self.stats[1]['mutProbs']))]).fillna(method = 'ffill')
        inversionProbs = pd.Series([self.stats[1]['mutProbs'][i][3] for i in range(len(self.stats[1]['mutProbs']))]).fillna(method = 'ffill')
        plt.plot(swapProbs.rolling(window = 5).mean(), label = 'swap')
        plt.plot(insertProbs.rolling(window = 5).mean(), label = 'insert')
        plt.plot(scrambleProbs.rolling(window = 5).mean(), label = 'scramble')
        plt.plot(inversionProbs.rolling(window = 5).mean(), label = 'inversion')
        plt.xlabel('Pokolenie')
        plt.ylabel('Prawdopodobieństwo mutacji')
        plt.grid()
        plt.legend()
        plt.show()

    def plotTypes(self):
        plt.figure(figsize = [30, 30])
        normalPops = []
        absPops = []
        empPops = []
        for i in range(self.numberOfGenerations):
            normalPops.append(0)
            absPops.append(0)
            empPops.append(0)
            for j in range(8):
                if self.stats[j]['type'][i] == 'normal':
                    normalPops[i] += 1
                elif self.stats[j]['type'][i] == 'absolute':
                    absPops[i] += 1
                elif self.stats[j]['type'][i] == 'empirical':
                    empPops[i] += 1
        plt.plot(normalPops, label = 'normal')
        plt.plot(absPops, label = 'absolute')
        plt.plot(empPops, label = 'empirical')
        plt.ylim(bottom = 0)
        plt.xlabel('Pokolenie')
        plt.ylabel('Liczba populacji')
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
                logging.info('Population: {}, best fitness: {}'.format(pop.populationID, pop.specimen.iloc[0, 1]))
            self.receiveStats()
            if it % self.migrationFrequency == 0 and it > 0:
                self.migrate()
                if self.type == 'dynamic':
                    self.changeType()
            it += 1
        self.logOutData()
        self.plotOut()


if __name__ == '__main__':
    cities_ = readData('test1')
    alg = Algorithm('dynamic', 'ladder', 10, 10, cities_, 100)
    alg.run()
    pass