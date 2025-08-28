from symMaps.base import *
from scipy import sparse
_adjF = adj.rc_pd

class AMatrix:
	""" Defines matrices in long-form. """
	def __init__(self, name, values = None, v = None, constr = None, vIdx = None, constrIdx = None):
		self.name = name # unique identifier
		self.v = v # name of variable the coefficient applies to 
		self.constr = constr # name of constraint the coefficient applies to
		self.values = values
		self.vIdx = vIdx
		self.constrIdx = constrIdx

	def __len__(self):
		return len(self.values)

	@property
	def isscalar(self):
		return all((x is None for x in (self.vIdx, self.constrIdx)))

class AMDict:
	def __init__(self, symbols = None):
		""" Simple keyword database with gpy symbols. 
			Slightly different logic than SimpleDB, as it allows for key!=self.symbols[key].name"""
		self.symbols = noneInit(symbols, {})

	def __getitem__(self,item):
		return self.symbols[item]

	def __setitem__(self,item,value):
		""" Add gpy directly with itentifier item:str, or using item:tuple. """
		if isinstance(value, AMatrix):
			self.symbols[item] = value
		else:
			self.symbols[item] = AMatrix(item, **value)

	def __call__(self, item, attr = 'value'):
		return getattr(self[item], attr)

	def __iter__(self):
		return iter(self.symbols.values())

	def __delitem__(self,item):
		del(self.symbols[item])

	def __len__(self):
		return len(self.symbols)


class LPSys:
	"""
	LPSys — a helper for building and compiling linear programs using pandas indices.

	Purpose
	- Provide a high-level, index-aware API for declaring variables, constraints
	  and their linear relationships using pandas Index / MultiIndex objects.
	- Maintain sparse definitions (series over partial domains) and compile them
	  into the dense structures required by solvers (e.g. scipy.optimize.linprog).

	Key concepts / attributes
	- self.v: dict mapping variable name -> domain (pd.Index, pd.MultiIndex or None for scalar).
	- self.eq, self.ub: dict mapping constraint name -> domain (pd.Index, pd.MultiIndex or None for scalar).
	- self.lp: dict-like store for problem components:
		- 'A_eq' / 'A_ub' : AMDictionaries of AMatrix objects (matrix coefficients).
		- 'c', 'l', 'u' etc: coefficient dictionaries (GpyDict / pandas Series).
	- self.maps: compiled mappings from pandas domains to stacked global variable indices.
	- self.len: dict of lengths for domains (used when building arrays).
	- self.out: compiled arguments (A, b, c, bounds) ready for solver.

	Important methods (high-level)
	- compileMaps(): build internal mappings (self.maps) from declared domains (self.v, self.eq, self.ub).
	- compileParams() / compileParams(...): convert self.lp parameter dicts to solver vectors/matrices.
	- initA_infer(name, series, v, constr, attr='eq'): add AMatrix using inference from series index.
	- initA_lag(...), initA_roll(...): helpers to add matrix coefficients where the variable
	  index is a lag/roll (calls symMaps.base.Lag / Lead / Roll utilities).
	- lazyA(...), lazyA_lag(...): broadcast a (possibly partial) coefficient series across
	  combined domains and add as AMatrix; variants handle lag/roll mappings before broadcasting.
	- sparse_bounds() / dense_bounds(): helpers to convert bound declarations to solver bounds.
	- unloadSol(sol): map solver solution back to pandas Series / dictionaries for variables and duals.

	Notes on lags/leads/rolls
	- This class uses Lag, Lead and Roll utilities (defined in symMaps.base) to transform
	  pandas indices/series before building matrix blocks. These utilities are expected
	  to return aligned pd.Index / pd.Series objects that match the intended constraint domains.
	- When adding lagged coefficients, the constraint domain and variable domain can be
	  different; initA_lag / lazyA_lag handle mapping between them via index transformations.

	Usage (brief example)
		self.v = {'y': pd.MultiIndex.from_product([t, i])}
		self.eq = {'vec_tx0': t[1:]}
		self.compileMaps()
		# add parameter defined on y domain
		par = pd.Series(..., index=self.v['y'])
		# add a lagged coefficient that aligns par[t-1,i] with constraint vec_tx0[t]
		self.initA_lag('vec_tx0_y', series=par, v='y', constr='vec_tx0', attr='eq',
					   lag=1, level='t', fkeep=False, bfill=False)

	Implementation details
	- Internally uses lightweight AMatrix objects and AMDict containers to keep the
	  model sparse until compileParams() is called.
	- Many methods accept scalar, 1d or nd index inputs and dispatch based on
	  pandas Index vs MultiIndex types.

	See also
	- symMaps.base.Lag, Lead, Roll — helpers for index/series transformations.
	- AMatrix, AMDict definitions in this module (below) — low-level matrix block abstractions.
	"""
	def __init__(self, db = None, v = None, eq = None, ub = None, scalarDual = True):
		self.db = noneInit(db, SimpleDB()) # database
		self.v = noneInit(v, {}) # used for establishing global domains for variables.
		self.eq = noneInit(eq, {}) # used for domains eq. constraints.
		self.ub = noneInit(ub, {}) # used for domains ineq. constraints.
		# self.lp = {k: GpyDict() for k in ('c','b_eq','b_ub','l','u')} | {k: GpyConstrDict() for k in ('A_ub', 'A_eq')} # collect dense parameters here.
		self.lp = {k: GpyDict() for k in ('c','b_eq','b_ub','l','u')} | {k: AMDict() for k in ('A_ub', 'A_eq')} # collect dense parameters here.
		self.out = {k: None for k in ('c','A_ub', 'b_ub', 'A_eq','b_eq','bounds')} # store final objects here.
		self.len = dict.fromkeys(('v','eq','ub'))
		self.maps = dict.fromkeys(('v','eq','ub'))
		self.scalarDual = scalarDual # if True this checks for instances where lower bound = upper bound. The shadow value is then added to the upper bound. 

	def __getitem__(self, item):
		return self.maps['v'][item]

	def __call__(self, x, name, **kwargs):
		""" Subset x with index of variable 'name' using linear indexing from self.maps."""
		return x[self[name].values]

	def get(self, x, name, **kwargs):
		""" __call__ method, but returned as pandas object (or scalar)"""
		return x[self[name][0]] if self.v[name] is None else pd.Series(x[self[name]], index = self[name].index, name = name)

	def x0(self, attr = 'v', fill_value = 0):
		return np.concatenate([self.xFromDb(name, attr = attr, fill_value = fill_value) for name in self.v])

	def xFromDb(self, name, attr = 'v', fill_value = 0):
		return self.db[name].array(attr = attr) if name in self.db.symbols else np.full(len(self.v[name]), fill_value)

	def unloadSol(self, sol, pfeq = None, pfub = None, pfl = None, pfu = None, **kwargs):
		return (self.unloadSolX(sol) | self.unloadSolDualEq(sol, prefix = pfeq) | self.unloadSolDualUb(sol, prefix = pfub) | self.undloadSolDualLower(sol, prefix=pfl) | self.undloadSolDualUpper(sol, prefix=pfu))

	def unloadSolX(self, sol):
		""" Map solution array to dictionary of pd.Series (or scalar) """
		return {k: self.get(sol['x'], k) for k in self.v}

	# Get shadow values on constraints:
	def getDualConstr(self, x, name, attr = 'eq', **kwargs):
		return x[self.maps[attr][name][0]] if getattr(self,attr)[name] is None else pd.Series(x[self.maps[attr][name].values], index = self.maps[attr][name].index, name = name)

	def unloadSolDualEq(self, sol, prefix = None, **kwargs):
		prefix = noneInit(prefix, 'λeq_')
		return {f'{prefix}{k}': self.getDualConstr(sol['eqlin']['marginals'], k, 'eq') for k in self.eq}

	def unloadSolDualUb(self, sol, prefix = None, **kwargs):
		prefix = noneInit(prefix, 'λub_')
		return {f'{prefix}{k}': self.getDualConstr(sol['ineqlin']['marginals'], k, 'ub') for k in self.ub}

	# Get shadow values on bounds:
	def getDualBound(self, x, name, **kwargs):
		return x[self.maps['v'][name][0]] if self.v[name] is None else pd.Series(x[self.maps['v'][name].values], index = self.maps['v'][name].index, name = name)

	def undloadSolDualLower(self, sol, prefix = None, **kwargs):
		vals = self.scalarDualLower(sol) if self.scalarDual else sol['lower']['marginals']
		prefix = noneInit(prefix, 'λl_')
		return {f'{prefix}{k}': self.getDualBound(vals, k) for k in self.v}

	def undloadSolDualUpper(self, sol, prefix = None, **kwargs):
		vals = self.scalarDualUpper(sol) if self.scalarDual else sol['upper']['marginals']
		prefix = noneInit(prefix, 'λu_')
		return {f'{prefix}{k}': self.getDualBound(vals, k) for k in self.v}

	# Adjust for shadow values when lower and upper bounds coincide - set lower bound to zero and add to upper bound:
	def scalarDualLower(self, sol):
		return np.where(self.out['bounds'][:,0]==self.out['bounds'][:,1], 0, sol['lower']['marginals'])

	def scalarDualUpper(self, sol):
		return np.where(self.out['bounds'][:,0]==self.out['bounds'][:,1], np.add(sol['lower']['marginals'], sol['upper']['marginals']), sol['upper']['marginals'])

	def compile(self, **kwargs):
		self.compileMaps()
		self.compileParams()
		return self.out 

	def compileMaps(self):
		"""
		Build internal mappings from declared pandas domains to stacked global indices.

		Purpose
		- Inspect self.v, self.ub, self.eq and create self.maps entries that map each pandas
		  Index / MultiIndex position to an integer position in the stacked variable
		  vector used by the solver.

		Parameters
		- None (reads declarations from self.v, self.eq, and self.ub)

		Returns
		- None (updates self.maps and self.len in-place)

		Notes
		- Must be called after declaring variables / constraints and before compiling
		  parameters or building solver arrays.
		"""
		[self.compileMaps1d(attr) for attr in ('v','eq','ub')];

	def compileParams(self):
		"""
		Compile sparse parameter declarations into solver-ready arrays.

		Purpose
		- Convert entries stored in self.lp (c, l, u, A_eq, A_ub, etc.) into the
		  dense / sparse numpy arrays and vectors required by the solver and store
		  the result in self.out.

		Parameters
		- None (reads from self.lp (c, l, u, A_eq, A_ub, etc.))

		Returns
		- None (updates self.out in-place)

		Notes
		- Assumes compileMaps() has already been run and self.maps is available.
		- scipy.optimize.linprog only works with sparse A_eq, A_ub (as of version 1.16). 
		- Sparse vectors are implemented below, but we call the dense versions here (sparse matrices)
		"""
		self.out['c'] = self.dense_c()
		self.out['b_eq'] = self.dense_b_eq()
		self.out['b_ub'] = self.dense_b_ub()
		self.out['bounds'] = self.dense_bounds()
		self.out['A_eq'] = self.sparse_A_eq()
		self.out['A_ub'] = self.sparse_A_ub()
		return self.out

	def compileMaps1d(self, attr):
		keys, vals = list(getattr(self,attr).keys()), list(getattr(self, attr).values())
		steps = np.array([0]+[1 if x is None else len(x) for x in vals]).cumsum()
		self.len[attr] = steps[-1]
		self.maps[attr] = {keys[i]: pd.Series(range(steps[i], steps[i+1]), index = getIndex(vals[i])) for i in range(len(keys))}

	### METHODS TO ADD COEFFICIENTS A_eq, A_ub from self.lp['A_eq'], self.lp['A_ub']:
	def getVIdx(self, a):
		if a.isscalar:
			return self.getIdx_scalar(a.v, 'v')
		elif a.vIdx is None:
			return self.getIdx_scalarAttr(a, a.v, 'v')
		else:
			return self.getIdx_vecAttr(a.vIdx, a.v, 'v')

	def getConstrIdx(self, a, attr):
		""" attr ∈ {'eq','ub'}"""
		if a.isscalar:
			return self.getIdx_scalar(a.constr, attr)
		elif a.constrIdx is None:
			return self.getIdx_scalarAttr(a, a.constr, attr)
		else:
			return self.getIdx_vecAttr(a.constrIdx, a.constr, attr)

	def getIdx_scalar(self, name, attr):
		return self.maps[attr][name][0]
	def getIdx_scalarAttr(self, a, name, attr):
		return np.full(len(a), self.getIdx_scalar(name, attr))
	def getIdx_vecAttr(self, idx, name, attr):
		return self.maps[attr][name][idx].values

	def getGlobalIdx1d(self, name, idx, attr):
		return self.maps[attr][name][0] if idx is None else self.maps[attr][name][idx].values

	def sparse_A_ub(self):
		if len(self.lp['A_ub'])>0:
			return sparse.coo_array((np.hstack([sym.values for sym in self.lp['A_ub']]), 
									(np.hstack([self.getConstrIdx(sym, 'ub') for sym in self.lp['A_ub']]), 
									 np.hstack([self.getVIdx(sym) for sym in self.lp['A_ub']]))), shape = (self.len['ub'], self.len['v']))
		else:
			return sparse.coo_array(([], ([],[])), shape = (self.len['ub'], self.len['v']))

	def sparse_A_eq(self):
		if len(self.lp['A_eq'])>0:
			return sparse.coo_array((np.hstack([sym.values for sym in self.lp['A_eq']]), 
									(np.hstack([self.getConstrIdx(sym, 'eq') for sym in self.lp['A_eq']]), 
									 np.hstack([self.getVIdx(sym) for sym in self.lp['A_eq']]))), shape = (self.len['eq'], self.len['v']))
		else:
			return sparse.coo_array(([], ([],[])), shape = (self.len['eq'], self.len['v']))

	# Methods for initializing A-blocks:
	def initA_infer(self, name, series = None, v = None, constr = None, attr = None):
		"""
		Add an AMatrix block by inferring vIdx and constrIdx from `series`.

		Purpose
		- Create and register an AMatrix using the provided pd.Series. The method
		  infers the variable-domain (vIdx) and constraint-domain (constrIdx) from
		  the series.index and aligns those with declared domains for `v` and `constr`.

		Parameters
		- name: unique identifier for the AMatrix block
		- series: pd.Series containing coefficients over some subset of the combined domain
		- v: variable name (must exist in self.v)
		- constr: constraint name (must exist in self.eq)
		- attr: 'eq' or 'ub' (which AMDict to register under)
		- kwargs: additional options forwarded to AMatrix construction (broadcasting, etc.)

		Returns
		- None (registers AMatrix in self.lp['A_<attr>'])
		"""
		self.lp[f'A_{attr}'][name] = AMatrix(name, values = series.values, v = v, constr= constr, 
													vIdx  = self.inferIdx(series, v, 'v'), 
													constrIdx = self.inferIdx(series, constr, attr))

	def inferIdx(self, series, name, attr):
		if getattr(self,attr)[name] is None:
			return None
		else:
			return self.inferIdxFromIdx(series.index, name, attr)
	def inferIdxFromIdx(self, idx, name, attr):
		if isinstance(getattr(self,attr)[name], pd.MultiIndex):
			return self.inferNdIdx(idx, name, attr)
		else:
			return self.infer1dIdx(idx, name, attr)
	def inferNdIdx(self, idx, name, attr):
		return self.maps[attr][name][pd.MultiIndex.from_arrays([idx.get_level_values(n) for n in self.maps[attr][name].index.names])].index
	def infer1dIdx(self, idx, name, attr):
		return self.maps[attr][name][idx.get_level_values(self.maps[attr][name].index.name)].index


	# Methods to initialize vectors c, b_eq, b_ub, l, u:
	def lazyV(self, name, series = None, v = None, attr = None, how = 'inner'):
		""" series: pd.Series or scalar. Domains has to be consistent with variable domains. attr ∈ {'v','l','u'}"""
		if self.v[v] is None:
			self.lp[attr][(name, v)] = series # scalar index
		else:
			self.lp[attr][(name, v)] = Broadcast.valuesToIdx(series, self.v[v], how = how)

	def lazyC(self, name, **kwargs):
		self.lazyV(name, attr = 'c', **kwargs)
	def lazyL(self, name, **kwargs):
		self.lazyV(name, attr = 'l', **kwargs)
	def lazyU(self, name, **kwargs):
		self.lazyV(name, attr = 'u', **kwargs)

	def lazyB(self, name, series = None, constr = None, attr = None, how = 'inner'):
		""" series: pd.Series or scalar. Domains has to be consistent with constraint domains. """
		if getattr(self, attr)[constr] is None:
			self.lp[f'b_{attr}'][(name, constr)] = series # scalar index
		else:
			self.lp[f'b_{attr}'][(name, constr)] = Broadcast.valuesToIdx(series, getattr(self, attr)[constr], how = how)


	def initA_lag(self, name, series = None, v = None, constr = None, attr = None, lag = None, level = None, fkeep = False, bfill = False, **kwargs):
		"""
		Add lagged linear constraint. 
		name: Unique identifier added to self.lp[f'A_{attr}'].
		series: pd.Series, coefficients to apply to lagged variable.
		lag: int or dict with, lag/lead specification (see Lag.series).
		level: None or str, specifies level of inddex to lag if type(lag) is int.
		v: str, name of variable the coefficient applies to in linear constraint.
		attr: 'eq' or 'ub', constraint type.
		fkeep: bool. If True --> keep indices that are leaded beyond original index. 
		bfill: False or in ('exo','ss'). Specifies how to backfill values that are not in original parameter. If False --> we do not fill in any values.
		kwargs: passed to Lag.series.
		"""
		laggedSeries = Lag.series(series, lag, level = level, fkeep = fkeep, bfill = bfill, **kwargs)
		self._addLaggedA(name, laggedSeries, v = v, constr = constr, attr= attr, lag = lag, level = level)

	def _addLaggedA(self, name, laggedSeries, v = None, constr = None, attr = None, lag = None, level = None):
		self.lp[f'A_{attr}'][name] = AMatrix(name, values = laggedSeries.values, v = v, constr = constr, 
													vIdx = self.inferIdxFromIdx(Lead.idx(laggedSeries.index, lag, level = level) , v, 'v'),
													constrIdx = self.inferIdx(laggedSeries, constr, attr))

	def initA_roll(self, name, series = None, v = None, constr = None, attr = None, roll = None, level = None, **kwargs):
		""" Similar to initA_lag, but with circular index reference. """
		rollSeries = Roll.series(series, roll, level = level,**kwargs)
		self._addRolledA(name, rollSeries, v = v, constr = constr, attr = attr, roll = roll, level = level)

	def _addRolledA(self, name, rollSeries, v = None, constr = None, attr= None, roll = None, level = None):
		self.lp[f'A_{attr}'][name] = AMatrix(name, values = rollSeries.values, v = v, constr = constr, 
													vIdx = self.inferIdxFromIdx(Roll.idx(rollSeries.index, Roll.invertRoll(roll), level = level) , v, 'v'),
													constrIdx = self.inferIdx(rollSeries, constr, attr))		


	def lazyA_lag(self, name, series = None, v = None, constr = None, attr = None, constrIdx = None, vIdx = None, lag = None, **kwargs):
		""" Same inputs as self.lazyA with added lag method on the variable index. Note: only works when constraint and variable are pd.Indices (not scalars)"""
		vIdx, constrIdx = noneInit(vIdx, self.v[v]), noneInit(constrIdx, getattr(self,attr)[constr])
		vSeries = Broadcast.valuesToIdx(series, vIdx) # broadcast to full variable index.
		lSeries = Lag.series(vSeries, lag, fkeep = True, bfill = False) # lag series mapped to variable index.
		fIdx = Broadcast.idx(constrIdx, lSeries.index) # broadcast full index.
		flSeries = Broadcast.valuesToIdx(lSeries, fIdx) # full lagged series.
		self._addLaggedA(name, flSeries, v = v, constr = constr, attr= attr, lag = lag)

	def lazyA_roll(self, name, series = None, v = None, constr = None, attr = None, constrIdx = None, vIdx = None, roll = None, **kwargs):
		""" Same inputs as self.lazyA with added lag method on the variable index. Note: only works when constraint and variable are pd.Indices (not scalars)"""
		vIdx, constrIdx = noneInit(vIdx, self.v[v]), noneInit(constrIdx, getattr(self,attr)[constr])
		vSeries = Broadcast.valuesToIdx(series, vIdx) # broadcast to full variable index.
		lSeries = Roll.series(vSeries, roll) # roll series mapped to variable index.
		fIdx = Broadcast.idx(constrIdx, lSeries.index) # broadcast full index.
		flSeries = Broadcast.valuesToIdx(lSeries, fIdx) # full lagged series.
		self._addRolledA(name, flSeries, v = v, constr = constr, attr= attr, lag = lag)

	def lazyA(self, name, series = None, v = None, constr = None, attr = None, constrIdx = None, vIdx = None, **kwargs):
		""" 
		Broadcast a (possibly partial) coefficient series over combined domains and add as AMatrix.

		Purpose
		- Given a pd.Series that covers some subset of the combined constraint-variable
		  domain, broadcast it to the full combined index and register an AMatrix block.

		Parameters
		- name: str, unique identifier added in self.lp[f'A_{attr}'].
		- series: pd.Series or scalar, coefficients defined over a subset of the cartesian product of vIdx and constrIdx.
		- v: str, name of variable accessed in self.v.
		- constr: str, name of constraint accessed in getattr(self, attr).
		- attr: 'eq' or 'ub' , indicates type of constraint.
		- constrIdx: None or pd.Index. Domain of constraint (subset of the full domain in getattr(self, attr)[constr]). If None --> use full domain.
		- vIdx: None or pd.Index. Domain of variable (subset of the full domain in self.v[v]). If None --> use full domain.
		"""
		vIdx, constrIdx = noneInit(vIdx, self.v[v]), noneInit(constrIdx, getattr(self,attr)[constr])
		if all((isinstance(x, pd.Index) for x in (vIdx, constrIdx))):
			fIdx = Broadcast.idx(vIdx, constrIdx)
			fSeries = Broadcast.valuesToIdx(series, fIdx)
			values, vIdx, constrIdx = fSeries.values, self.inferIdx(fSeries, v, 'v'), self.inferIdx(fSeries, constr, attr)
		elif constrIdx is None: 
			fSeries = Broadcast.valuesToIdx(series, vIdx)
			values, vIdx = fSeries.values, fSeries.index
		elif vIdx is None:
			fSeries = Broadcast.valuesToIdx(series, constrIdx) # Map coefficient to constraint index
			values, constrIdx = fSeries.values, fSeries.index
		else: 
			values = series # scalar 
		self.lp[f'A_{attr}'][name] = AMatrix(name, values = values, v = v, constr = constr, vIdx = vIdx, constrIdx = constrIdx)


	# NOTE: Sparse vectors are not yet implemented in scipy optimize 1.16 - only matrices A_eq, A_ub from above. 
	def dense_bounds(self):
		bounds = np.full((self.len['v'], 2), np.nan)
		if len(self.lp['l'])>0:
			bounds[self._rowsStack('l','v'), 0] = self._dataStack('l')
		if len(self.lp['u'])>0:
			bounds[self._rowsStack('u','v'), 1] = self._dataStack('u')
		return bounds
	def sparse_bounds(self):
		if len(self.lp['l'])>0:
			l = self._dataStack('l')
			lRowIdx = self._rowsStack('l','v')
		else:
			l,lRowIdx = [], []
		if len(self.lp['u'])>0:
			u = self._dataStack('u')
			uRowIdx = self._rowsStack('u','v')
		else:
			u,uRowIdx = [], []
		return sparse.coo_array((np.hstack([l,u]), (np.hstack([lRowIdx, uRowIdx]), np.hstack([np.zeros(len(l)), np.ones(len(u))]))), shape = (self.len['v'], 2))

	def dense_c(self):
		c = np.zeros(self.len['v'])
		if len(self.lp['c'])>0:
			c[self._rowsStack('c','v')] = self._dataStack('c')
		return c
	def sparse_c(self):
		if len(self.lp['c'])>0:
			return sparse.coo_array((self._dataStack('c'), (self._rowsStack('c','v'),)), shape = (self.len['v'],))
		else:
			return sparse.coo_array(([], ([],)), shape = (self.len['v'],))

	def dense_b_eq(self):
		b = np.zeros(self.len['eq'])
		if len(self.lp['b_eq'])>0:
			b[self._rowsStack('b_eq','eq')] = self._dataStack('b_eq')
		return b
	def sparse_b_eq(self):
		if len(self.lp['b_eq'])>0:
			return sparse.coo_array((self._dataStack('b_eq'), (self._rowsStack('b_eq','eq'), )), shape = (self.len['eq'],))
		else:
			return sparse.coo_array(([], ([],)), shape = (self.len['eq'],))

	def dense_b_ub(self):
		b = np.zeros(self.len['ub'])
		if len(self.lp['b_ub'])>0:
			b[self._rowsStack('b_ub','ub')] = self._dataStack('b_ub')
		return b
	def sparse_b_ub(self):
		if len(self.lp['b_ub'])>0:
			return sparse.coo_array((self._dataStack('b_ub'), (self._rowsStack('b_ub','ub'), )), shape = (self.len['ub'],))
		else:
			return sparse.coo_array(([], ([],)), shape = (self.len['ub'],))

	def _dataStack(self,key):
		return np.hstack([sym.array() for sym in self.lp[key]])
	def _rowsStack(self, key, attr):
		return np.hstack([self.getGlobalIdx1d(sym.name, sym.index, attr) for sym in self.lp[key]])

