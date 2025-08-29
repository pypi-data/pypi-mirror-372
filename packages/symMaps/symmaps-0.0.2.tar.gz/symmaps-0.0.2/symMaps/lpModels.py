from symMaps.base import *
from scipy import sparse, optimize
from symMaps.lpSys import AMatrix, AMDict, LPSys
_adjF = adj.rc_pd

### Auxiliary loop methods:
def loopUnpackToDFs(solsLoop, idxLoop = None):
	soli = solsLoop[next(iter(solsLoop))]
	return {k: loopUnpackToDF_k(solsLoop, k, soli, idxLoop = idxLoop) for k in soli}

def loopUnpackToDF_k(solsLoop, k, soli, idxLoop = None):
	""" Unpack symbol 'k' in dictionary of solutions. """
	if isinstance(soli[k], pd.Series):
		return pd.DataFrame(np.vstack([solsLoop[l][k].values for l in solsLoop]).T, index = soli[k].index, columns = idxLoop)
	else:
		return pd.Series([solsLoop[l][k] for l in solsLoop], index = idxLoop)


# To do: Loop through and change grid values in already compiled models.
class ModelShell:
	def __init__(self, db = None, sys = None, scalarDual = True, computeDual = True, solOptions = None, **kwargs):
		self.scalarDual = scalarDual
		self.sys = noneInit(sys, LPSys(db = db, scalarDual = self.scalarDual))
		self.computeDual = computeDual
		self.solOptions = self.defaultSolOptions | noneInit(solOptions, {}) # passed to optimize.linprog

	@property
	def db(self):
		return self.sys.db	

	@property
	def defaultSolOptions(self):
		return {'method': 'highs', 'x0': None}
	
	def x0(self, attr = 'v', fill_value = 0):
		return self.sys.x0(attr = attr, fill_value = fill_value)

	def solve(self, **kwargs):
		""" Assumes that self.sys is compiled. """
		sol = optimize.linprog(**self.sys.out, **self.solOptions)
		assert sol['status'] == 0, "scipy.optimize.linprog did not yield solution status == 0."
		return sol

	def postSolve(self, sol, **kwargs):
		""" A standard post solution routine. """
		return self.sys.unloadSol(sol) if self.computeDual else self.sys.unloadSolX(sol)

	def postSolveToDB(self, sol, **kwargs):
		dictSol = self.postSolve(sol, **kwargs)
		[self.db.__setitem__(k,v) for k,v in dictSol.items()];

	def lazyLoopAsDFs(self, grids, idxLoop, **kwargs):
		return loopUnpackToDFs(self.lazyLoop(grids, idxLoop, **kwargs), idxLoop)

	def lazyLoop(self, grids, idxLoop, **kwargs):
		return {l: self.lazyLoop_l(grids, l, idxLoop, **kwargs) for l in idxLoop}

	def lazyLoop_l(self, grids, l, idxLoop, kwCompile = None, kwSolve = None, kwPostSolve = None):
		if isinstance(grids, pd.Series):
			self.db.aom(grids.xs(l), name = grids.name, priority = 'first') # update parameter value in database.
		else:
			[self.db.aom(grid.xs(l), name = grid.name, priority = 'first') for grid in grids] # update parameter values if grids is a list of series.
		self.compile(**noneInit(kwCompile, {}))
		return self.postSolve(self.solve(**noneInit(kwSolve, {})), **noneInit(kwPostSolve, {}))