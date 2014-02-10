import numpy as np
from misc import Genetics



class MatrixBuilder(object):
	def __init__(self, codonFreqs):
		
		# Need to be provided by user
		self.STATE = codonFreqs

		# Genetics variables		
		self.molecules = Genetics()

	def isTI(self, source, target):
		''' Returns True for transition, False for transversion.'''
		if (source in self.molecules.pyrims and target in self.molecules.purines):
			return False
		else:
			return True	
	
	
	def isSyn(self, source, target):
		''' Given a source codon and target codon, return True if the change is synonymous.'''
		if (self.molecules.codon_dict[source] == self.molecules.codon_dict[target]):
			return True
		else:
			return False
	
	
	def getCodonFreq(self, codon):
		''' Get the frequency for a given codon. '''
		Freq = self.STATE[self.molecules.codons.index(codon)]
		return Freq	
	
		
	def calcMutProb(self, source, target):
		''' Calculates a substitution probability between two codons. If single mutation, return the probability/rate. Else, return 0. ''' 
		mydiff=''
		for i in range(3):
			if source[i] == target[i]:	
				continue
			else:	
				mydiff+=source[i]+target[i]
		
		# Either no change >1 mutations. It's probability is zero. We will correct the diagonal later.	
		if len(mydiff)!=2:
			return 0
		
		# If a single mutational step away, return the probability
		else:		
			# Transitions
			if self.isTI(mydiff[0], mydiff[1]):
				if self.isSyn(source, target):
					return self.synTI(source, target)
				else:
					return self.nonSynTI(source, target)
			# Transversions
			else:
				if self.isSyn(source, target):
					return self.synTV(source, target)
				else:
					return self.nonSynTV(source, target)
				
				
	def buildQ(self):
		''' Builds the 61x61 matrix Q '''
		
		transMatrix = np.ones([61,61]) # Look at me, hardcoding that there are 61 codons!
		source_count=0
		for s in range(61):
			source = self.molecules.codons[s]
			for t in range(61):
				target = self.molecules.codons[t]
				rate = self.calcMutProb(source, target)
				transMatrix[s][t] = rate
			
			# Fill in the diagonal position so the row sums to 0. Confirm.
			transMatrix[s][s]= -1*(np.sum( transMatrix[s] ))
			assert (np.sum(transMatrix[s]==0)), "Row in matrix does not sum to 0."
		
		transMatrix = self.scaleMatrix(transMatrix)
		return transMatrix	
	
	
	
	
	def scaleMatrix(self, mat):
		''' Scale Q matrix so -Sum(pi_iQ_ii)=1 (Goldman and Yang 1994). '''
		scale_factor = 0
		for i in range(61):
			scale_factor += (mat[i][i] * self.STATE[i])
		scale_factor*=-1.
		mat = np.divide(mat, scale_factor)
		
		######## CHECK THAT THE SCALING WORKED OUT ##############
		sum=0.
		for i in range(61):
			sum += (mat[i][i] * self.STATE[i])
		assert(round(sum) == -1.0), "Matrix scaling was a bust."
		return mat		
		
		
		
		

	########################################################## 
	## Base functions for computing rates. Not implemented. ## 
	def synTI(self, source, target):
		return 0
	def synTV(self, source, target):
		return 0
	def nonSynTI(self, source, target):
		return 0
	def nonSynTV(self, source, target):
		return 0
	###########################################################
		
	
		
class SellaMatrix(MatrixBuilder):
	def __init__(self, stateFreqs, mu, kappa):
		''' Implement the Sella (2005) model '''
		super(SellaMatrix, self).__init__(stateFreqs)
		self.MU = mu
		self.KAPPA = kappa
	
	def fix(self, source_freq, target_freq):
		''' Given pi(i) and pi(j), where pi() is the equilibrium a given codon in that column, return probability_of_fixation_(i->j). '''
		if target_freq == 0 or source_freq == 0:
			return 0 # If either has 0 frequency, we should never reach it.
		elif source_freq == target_freq:
			return 1 # confirmed correct
		else:
			return ( (np.log(target_freq) - np.log(source_freq)) / (1 - source_freq/target_freq) )


	def synTI(self, source, target):
		''' Probability of synonymous transition '''
		return ( self.MU * self.KAPPA )
	
	
	def synTV(self, source, target):
		''' Probability of synonymous tranversion '''
		return ( self.MU )
	
	
	def nonSynTI(self, source, target):
		''' Probability of nonsynonymous transition '''
		sFreq = self.getCodonFreq(source)
		tFreq = self.getCodonFreq(target)
		return ( self.MU * self.KAPPA * self.fix(sFreq, tFreq) )				
	
		
	def nonSynTV(self, source, target):
		''' Probability of nonsynonymous tranversion '''
		sFreq = self.getCodonFreq(source)
		tFreq = self.getCodonFreq(target)
		return ( self.MU * self.fix(sFreq, tFreq) )	

				


class GY94Matrix(MatrixBuilder):
	def __init__(self, stateFreqs, kappa, omega):
		'''Implement the GY94 model '''
		super(GY94Matrix, self).__init__(stateFreqs)
		self.KAPPA = kappa
		self.OMEGA = omega
		
	
	def synTI(self, source, target):
		''' Probability of synonymous transition '''
		return ( self.getCodonFreq(target) * self.KAPPA )
	
	
	def synTV(self, source, target):
		''' Probability of synonymous tranversion '''
		return ( self.getCodonFreq(target) )
	
	
	def nonSynTI(self, source, target):
		''' Probability of nonsynonymous transition '''
		return ( self.getCodonFreq(target) * self.KAPPA * self.OMEGA )				
	
		
	def nonSynTV(self, source, target):
		''' Probability of nonsynonymous tranversion '''
		return ( self.getCodonFreq(target) * self.OMEGA )	
