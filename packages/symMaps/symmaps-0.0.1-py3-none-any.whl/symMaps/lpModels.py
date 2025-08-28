from symMaps.base import *
from scipy import sparse, optimize
from symMaps.lpSys import AMatrix, AMDict, LPSys
_adjF = adj.rc_pd

# To do: Loop through and change grid values in already compiled models.
class ModelShell:
	def __init__(self, db = None, sys = None, scalarDual = True, computeDual = True, solOptions = None, **kwargs):
		self.db = noneInit(db, SimpleDB())
		self.computeDual = computeDual
		self.scalarDual = scalarDual
		self.solOptions = self.defaultSolOptions | noneInit(solOptions, {}) # passed to optimize.linprog
		self.sys = noneInit(sys, LPSys(db = self.db, scalarDual = self.scalarDual))

	@property
	def defaultSolOptions(self):
		return {'method': 'highs', 'x0': None}
	
	def x0(self, attr = 'v', fill_value = 0):
		return self.sys.x0(attr = attr, fill_value = fill_value)

	def solve(self, **kwargs):
		""" Assumes that self.sys is compiled. """
		return optimize.linprog(**self.sys.out, **self.solOptions)

	def postSolve(self, sol, **kwargs):
		assert sol['status'] == 0, "scipy.optimize.linprog did not yield solution status == 0. Check output from self.solve()."
		dictSol = self.sys.unloadSol(sol) if self.computeDual else self.sys.unloadSolX(sol)
		[self.db.__setitem__(k,v) for k,v in dictSol.items()];
