from symMaps.base import *
_adjF = adj.rc_pd


class SimpleSys:
	def __init__(self, db = None, v = None, maps = None, iterAux = True):
		self.db = noneInit(db, SimpleDB()) # database
		self.v = noneInit(v, {}) # variables
		self.maps = noneInit(maps, {}) # mapping from pandas index to global linear variable index.
		self.auxMaps = {}
		self.auxMapsIdx = {}
		self.iterAux = iterAux

	def x0(self, attr = 'v', fill_value = 0):
		return np.concatenate([self.xFromDb(name, attr = attr, fill_value = fill_value) for name in self.v])

	def xFromDb(self, name, attr = 'v', fill_value = 0):
		return self.db[name].array(attr = attr) if name in self.db.symbols else np.full(len(self.v[name]), fill_value)

	def compile(self):
		keys, vals = list(self.v.keys()), list(self.v.values())
		steps = np.array([0]+[1 if x is None else len(x) for x in vals]).cumsum()
		self.len = steps[-1]
		self.maps = {keys[i]: pd.Series(range(steps[i], steps[i+1]), index = getIndex(vals[i])) for i in range(len(keys))}

	def __getitem__(self, item):
		return (self.auxMaps | self.maps)[item]

	def __iter__(self):
		return iter(self.maps | self.auxMaps) if self.iterAux else iter(self.maps)

	def __len__(self):
		return len(self.maps | self.auxMaps) if self.iterAux else len(self.maps)

	def __call__(self, x, name, **kwargs):
		""" Subset x with index of variable 'name' using linear indexing from self.maps."""
		return x[self[name]]

	def get(self, x, name, **kwargs):
		""" __call__ method, but returned as pandas object"""
		return x[self[name][0]] if self[name].index is None else pd.Series(x[self[name]], index = self[name].index, name = name)
		
	def getr(self, x, name, **kwargs):
		""" Like the get method, but more robust (adds more potential adjustments to the symbol) """
		if self.symbols[name] is None: # check if the symbol is a scalar
			return x[self[name][0]] # return without pandas object
		else:
			k = _adjF(self[name], **kwargs)
			return pd.Series(x[k], index = k.index, name = name)

	def unloadSol(self, x):
		return {k: self.get(x, k) for k in self}

	# def applyMapGlobalIdx(self, symbol, m):
	# 	return pd.Series(symbol[m.values].values, m.index)

	# def addSymFromMap(self, name, symbol, m):
	# 	self.auxMapsIdx[name] = m
	# 	self.auxMaps[name] = self.applyMapGlobalIdx(self[symbol], m)

	# def _dropna(self, glbSymbol, m):
	# 	""" Only keep elements in mapping (pd.Series) that are in the "global" version in self"""
	# 	return self._reverseMap(adj.rc_pd(self._reverseMap(m), self[glbSymbol]))

	# @staticmethod
	# def _reverseMap(m):
	# 	return pd.Series(m.index.values, index = pd.MultiIndex.from_tuples(m.values, names = m.index.names)
	# 														 if isinstance(m.index, pd.MultiIndex) else pd.Index(m.values, name = m.index.name))

	# def addLaggedSym(self, name, symbol, lags, dropna = False, **kwargs):
	# 	m = self.lagMaps(adj.rc_pd(self[symbol], **kwargs), lags)
	# 	return self.addSymFromMap(name, symbol, self._dropna(symbol, m) if dropna else m)

	# def getLagFromSol(self, x, symbol, lags, dropna=False, **kwargs):
	# 	""" Return a lagged symbol like self.addLaggedSym, but without adding it to the compilation stage."""
	# 	glbIdx = self.applyMapGlobalIdx(self[symbol], self.lagMaps(adj.rc_pd(self[symbol], **kwargs), lags))
	# 	return pd.Series(x[glbIdx], index = glbIdx.index)

	# def getLag(self, x, lags, dropna = False, **kwargs):
	# 	""" Return a lagged symbol like getLagFromSol, but where x is the "non-shifted" symbol (pd.Series) instead of the global vector"""
	# 	m = self.lagMaps(adj.rc_pd(x, **kwargs), lags)
	# 	return pd.Series(x[m.values].values, index = x.index)

	# def addRolledSym(self, name, symbol, rolls, **kwargs):
	# 	self.addSymFromMap(name, symbol, self.rollMaps(adj.rc_pd(self[symbol], **kwargs), rolls))

	# def getRollFromSol(self, x, symbol, rolls, dropna=False, **kwargs):
	# 	""" Return a rolled symbol like self.addRolledSym, but without adding it to the compilation stage."""
	# 	glbIdx = self.applyMapGlobalIdx(self[symbol], self.rollMaps(adj.rc_pd(self[symbol], **kwargs), rolls))
	# 	return pd.Series(x[glbIdx], index = glbIdx.index)

	# def getRoll(self, x, rolls, dropna = False, **kwargs):
	# 	""" Return a shifted symbol like getShiftFromSol, but where x is the "non-shifted" symbol (pd.Series) instead of the global vector"""
	# 	m = self.rollMaps(adj.rc_pd(x, **kwargs), rolls)
	# 	return pd.Series(x[m.values].values, index = x.index)

	# def addShiftedSym(self, name, symbol, shifts, dropna = False, opt = None, **kwargs):
	# 	m = self.shiftMaps(adj.rc_pd(self[symbol], **kwargs), shifts, **noneInit(opt, {}))
	# 	return self.addSymFromMap(name, symbol, self._dropna(symbol, m) if dropna else m)

	# def getShiftFromSol(self, x, symbol, shifts, dropna=False, opt= None, **kwargs):
	# 	""" Return a shifted symbol like self.addShiftedSym, but without adding it to the compilation stage."""
	# 	glbIdx = self.applyMapGlobalIdx(self[symbol], self.shiftMaps(adj.rc_pd(self[symbol], **kwargs), shifts, **noneInit(opt, {})))
	# 	return pd.Series(x[glbIdx], index = glbIdx.index)

	# def getShift(self, x, shifts, dropna = False, opt = None, **kwargs):
	# 	""" Return a shifted symbol like getShiftFromSol, but where x is the "non-shifted" symbol (pd.Series) instead of the global vector"""
	# 	m = self.shiftMaps(adj.rc_pd(x, **kwargs), shifts, **noneInit(opt, {}))
	# 	return pd.Series(x[m.values].values, index = x.index)

	# def lagMaps(self, m, lags):
	# 	return self._lagMaps(m.index, lags) if isinstance(m.index, pd.MultiIndex) else self._lagMap(m.index, lags)

	# @staticmethod
	# def _lagMaps(idx, lags):
	# 	return pd.Series(idx.set_levels([SymMaps._lagLevelMap(idx, idx.names.index(level),lag) for level,lag in lags.items()], level = lags.keys()).values, index  = idx)

	# @staticmethod
	# def _lagLevelMap(idx, levelInt, lag):
	# 	return idx.levels[levelInt].map(SymMaps._lagMap(idx.levels[levelInt], lag))

	# @staticmethod
	# def _lagMap(idx, lag):
	# 	return pd.Series(idx-lag, index = idx)

	# def rollMaps(self, m, rolls):
	# 	return self._rollMaps(m.index, rolls) if isinstance(m.index, pd.MultiIndex) else self._rollMap(m.index, rolls)

	# @staticmethod
	# def _rollMaps(idx, rolls):
	# 	return pd.Series(idx.set_levels([SymMaps._rollLevelMap(idx, idx.names.index(level), roll) for level,roll in rolls.items()], level = rolls.keys()).values, index  = idx)

	# @staticmethod
	# def _rollLevelMap(idx, levelInt, roll):
	# 	return idx.levels[levelInt].map(SymMaps._rollMap(idx.levels[levelInt], roll))

	# @staticmethod
	# def _rollMap(idx, roll):
	# 	return pd.Series(np.roll(idx, roll), index = idx)

	# def shiftMaps(self, m, shifts, **kwargs):
	# 	return self._shiftMaps(m.index, shifts, **kwargs) if isinstance(m.index, pd.MultiIndex) else self._shiftMap(m.index, shifts, **kwargs)

	# @staticmethod
	# def _shiftMaps(idx, shifts, **kwargs):
	# 	return pd.Series(idx.set_levels([SymMaps._shiftLevelMap(idx, idx.names.index(level), shift, **kwargs) for level,shift in shifts.items()], level = shifts.keys(), verify_integrity=False).values, index = idx)

	# @staticmethod
	# def _shiftLevelMap(idx, levelInt, shift, **kwargs):
	# 	idxLevel = pd.Series(idx.levels[levelInt], idx.levels[levelInt]).convert_dtypes() # allows for NA without breaking type definition
	# 	return idx.levels[levelInt].map(SymMaps._shiftOptions(idxLevel, shift, **kwargs))

	# @staticmethod
	# def _shiftMap(idx, shift, **kwargs):
	# 	return SymMaps._shiftOptions(pd.Series(idx, idx).convert_dtypes(), shift, **kwargs)

	# @staticmethod
	# def _shiftOptions(m, shift, fill_value=None, useLoc = None, useIloc = None):
	# 	if useLoc == 'nn':
	# 		return m.shift(shift, fill_value = m.iloc[shift-1 if shift>0 else shift])
	# 	elif fill_value:
	# 		return m.shift(shift, fill_value = fill_value)
	# 	elif useLoc:
	# 		return m.shift(shift, fill_value = m.loc[useLoc])
	# 	elif useIloc:
	# 		return m.shift(shift, fill_value = m.iloc[useIloc])
	# 	else:
	# 		return m.shift(shift)
