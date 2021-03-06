import random

class Species:
    def __init__(self, firstGenome):
        self.EXCESS_COEFF = 1.5
        self.WEIGHT_DIFF_COEFF = 0.8
        self.COMPATIBILITY_THRESHOLD = 1.0

        self.champion = firstGenome
        self.genomes = [firstGenome]
        self.bestFitness = firstGenome.fitness
        self.averageFitness = 0
        self.staleness = 0

    def add(self, genome):
        self.genomes.append(genome)

    def belongsTo(self, genome):
        excessAndDisjoint = self.getExcessDisjoint(genome, self.champion)
        averageWeightDiff = self.averageWeightDiff(genome, self.champion)
        largeGenomeNormaliser = len(genome.connections)/20.

        compatibility = (self.EXCESS_COEFF * excessAndDisjoint/largeGenomeNormaliser) + (self.WEIGHT_DIFF_COEFF * averageWeightDiff)
        return compatibility < self.COMPATIBILITY_THRESHOLD

    def getExcessDisjoint(self, genome1, genome2):
        matching = 0
        for c1 in genome1.connections:
            for c2 in genome2.connections:
                if c1.innovationNumber == c2.innovationNumber:
                    matching += 1
                    break

        return len(genome1.connections) + len(genome2.connections) - 2 * matching

    def averageWeightDiff(self, genome1, genome2):
        matching = 0
        totalDiff = 0
        for c1 in genome1.connections:
            for c2 in genome2.connections:
                if c1.innovationNumber == c2.innovationNumber:
                    matching += 1
                    totalDiff += abs(c1.weight - c2.weight)
                    break
        if matching == 0: return 100
        return totalDiff/matching

    def sortSpecies(self):
        for i in range(len(self.genomes) - 1):
            maxIndex = i
            for j in range(i + 1, len(self.genomes)):
                if self.genomes[j].fitness > self.genomes[maxIndex].fitness:
                    maxIndex = j
            tmp = self.genomes[i]
            self.genomes[i] = self.genomes[maxIndex]
            self.genomes[maxIndex] = tmp

        if len(self.genomes) > 0 and self.genomes[0].fitness > self.bestFitness:
            self.staleness = 0
            self.bestFitness = self.genomes[0].fitness
            self.champion = self.genomes[0]
        else: self.staleness += 1

    def setAverage(self):
        if len(self.genomes) == 0:
            self.averageFitness = 0
            return

        sum = 0.0
        for genome in self.genomes:
            sum += genome.fitness
        self.averageFitness = sum/len(self.genomes)

    def cull(self):
        if len(self.genomes) > 2:
            self.genomes = self.genomes[:len(self.genomes)/2]

    def fitnessSharing(self):
        for genome in self.genomes:
            genome.fitness /= float(len(self.genomes))

    def getRandomGenome(self):
        fitnessSum = 0
        for genome in self.genomes:
            fitnessSum += genome.fitness

        rand = random.random() * fitnessSum
        runningSum = 0

        for genome in self.genomes:
            runningSum += genome.fitness
            if runningSum >= rand:
                return genome

    def createGenome(self, innovationHistory):
        if random.random() < 0.25:
            genome = self.getRandomGenome().clone()
        else:
            parent1 = self.getRandomGenome()
            parent2 = self.getRandomGenome()

            if parent1.fitness > parent2.fitness:
                genome = parent1.crossover(parent2)
            else:
                genome = parent2.crossover(parent1)

        genome.mutate(innovationHistory)
        return genome