from symMaps.base import *
from symMaps.lpSys import AMatrix, AMDict, LPSys
from symMaps.lpModels import ModelShell
from scipy import sparse, optimize
_adjF = adj.rc_pd

# A few basic functions for the energy models:
def fuelCost(db):
	""" 
	 - 'pFuel' (fuel price) is defined over 'idxF' (fuel index). Default unit: €/GJ.
	 - 'uEm' (emission intensity) is defined over 'idxF','idxEm' (emission index). Default unit: Ton emission/GJ fuel input. 
	 - 'taxEm' (tax on emissions) is defined over 'idxEm' (emission index). Default unit: €/ton emission output.
	"""
	return db('pFuel').add(pdSum((db('uEm') * db('taxEm')).dropna(), 'idxEm'), fill_value=0)

def mc(db):
	""" 
	- 'uFuel': Fuelmix is defined over 'idxF', 'idxGen' (generator index). Default unit: GJ input/GJ output.
	- 'VOM': variable operating and maintenance costs is defined over 'idxGen'. Default unit: €/GJ output.
	"""
	return pdSum((db('uFuel') * fuelCost(db)).dropna(), 'idxF').add(db['VOM'], fill_value=0)

def fuelConsumption(db, sumOver='idxGen'):
	"""
	- 'generation': dispatched energy defined over 'idxGen'. Default unit: GJ.
	- 'uFuel': Fuelmix is defined over 'idxF', 'idxGen' (generator index). Default unit: GJ input/GJ output.
	"""
	return pdSum((db('generation') * db('uFuel')).dropna(), sumOver)

def emissionsFuel(db, sumOver='idxF'):
	""" 
	- 'fuelCons': fuel input defined over 'idxF'. Default unit: GJ. 
	 - 'uEm' (emission intensity) is defined over 'idxF','idxEm' (emission index). Default unit: Ton emission/GJ fuel input. 
	"""
	return pdSum((db('fuelCons') * db('uEm')).dropna(), sumOver)

def plantEmissionIntensity(db):
	""" 
	- 'uFuel': Fuelmix is defined over 'idxF', 'idxGen' (generator index). Default unit: GJ input/GJ output.
	 - 'uEm' (emission intensity) is defined over 'idxF','idxEm' (emission index). Default unit: Ton emission/GJ fuel input. 
	"""
	return (db('uFuel') * db('uEm')).groupby('idxGen').sum()

class MBasic(ModelShell):
	def compile(self, **kwargs):
		""" Compile model """
		self.initArgs()
		return self.sys.compile(**kwargs)

	def initArgs(self):
		[getattr(self, f'initArg_{k}')() for k in ('v','eq','ub') if hasattr(self, k)]; # specify domains for variables and equations
		[getattr(self, f'initArgsV_{k}')() for k in self.v]; # specify c,l,u for all variables
		[getattr(self, f'initArgsEq_{k}')() for k in self.eq]; # add A_eq and b_eq.
		[getattr(self, f'initArgsUb_{k}')() for k in self.ub]; # add A_ub and b_ub.

	def initArgs_v(self):
		""" self.sys.v dictionary"""
		self.sys.v.update({'generation': self.db['idxGen'],'demand': self.db['idxCons']})

	def initArgs_eq(self):
		""" self.sys.eq dictionary"""
		self.sys.eq.update({'equilibrium': None})

	def initArgsV_generation(self):
		self.sys.lp['c'][('mc', 'generation')] = self.db['mc'] # assumes that mc is defined over index 'idxGen'.
		self.sys.lp['u'][('cap', 'generation')] = self.db['genCap'] # assumes that genCap is defined over index 'idxGen'.

	def initArgsV_demand(self):
		self.sys.lp['c'][('mwp', 'demand')] = -self.db['mwp'] # assumes that mwp is defined over index 'idxCons'.
		self.sys.lp['u'][('cap', 'demand')] = self.db['load'] # assumes that load is defined over index 'idxCons'.

	def initArgsEq_equilibrium(self):
		self.sys.lazyA('eq2Gen', series = 1,  v = 'generation', constr = 'equilibrium',attr='eq')
		self.sys.lazyA('eq2Dem', series = -1, v = 'demand', constr = 'equilibrium',attr='eq')

	def postSolve(self, sol, **kwargs):
		super().postSolve(sol)
		self.db['surplus'] = -solution['fun']
		self.db['fuelCons'] = fuelConsumption(self.db)
		self.db['emissions'] = emissionsFuel(self.db)


class MBasicEmCap(MBasic):
	# Add additional constraint:
	def initArgs_ub(self):
		""" self.sys.ub dictionary"""
		self.sys.ub.update({'emCap': None})

	def initArgsUb_emCap(self):
		self.sys.lazyA('emCap2Gen', series = plantEmissionIntensity(self.db),  v = 'generation', constr = 'emCap',attr='ub')
		self.sys.lp['b_ub'] = self.db('CO2Cap')


class MBasicRES(MBasic):

	def RESGenIdx(self, CO2Idx = 'CO2'):
		""" Subset of idxGen that is considered Renewable Energy based on emission intensities """
		s = self.db('uFuel') * self.db('uEm').xs(CO2Idx,level='idxEm')
		return s[s <= 0].index

	def initArgs_ub(self):
		""" self.sys.ub dictionary"""
		self.sys.ub.update({'RES': None})

	def initArgsUb_emCap(self):
		self.sys.lazyA('RES2Gen', series = pd.Series(-1, index = self.RESGenIdx()),  v = 'generation', constr = 'RES',attr='ub')
		self.sys.lazyA('RES2Dem', series = pd.Series(self.db('RESCap'), index = self.RESGenIdx()),  v = 'generation', constr = 'RES',attr='ub')
