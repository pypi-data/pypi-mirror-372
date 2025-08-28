import itertools, numpy as np, pandas as pd
from collections.abc import Iterable
from pyDbs import adj, adjMultiIndex, Broadcast, Gpy, Gpy_, GpySet, GpyVariable, GpyScalar, GpyDict, SimpleDB
from pyDbs import cartesianProductIndex as CPI
_numtypes = (int,float,np.generic)


### -------- 	0: Small, auxiliary functions	-------- ###
def noneInit(x,FallBackVal):
	return FallBackVal if x is None else x

def is_iterable(arg):
	return isinstance(arg, Iterable) and not isinstance(arg, string_types)

def getIndex(symbol):
	""" Defaults to None if no index is defined. """
	if hasattr(symbol, 'index'):
		return symbol.index
	elif isinstance(symbol, pd.Index):
		return symbol
	elif not is_iterable(symbol):
		return None

def getValues(symbol):
	""" Defaults to the index, if no values are defined (e.g. if symbol is an index) """
	if isinstance(symbol, (pd.Series, pd.DataFrame, pd.Index)):
		return symbol
	elif hasattr(symbol,'v'):
		return symbol.v
	elif not is_iterable(symbol):
		return symbol

def getDomains(x):
	return [] if getIndex(x) is None else getIndex(x).names

def pdGb(x, by):
	if is_iterable(by):
		return x.groupby([k for k in x.index.names if k not in by])
	else:
		return x.groupby([k for k in x.index.names if k != by])

def pdSum(x,sumby):
	return pdGb(x, sumby).sum() if isinstance(x.index, pd.MultiIndex) else sum(x)

class Lag:
	"""
	Utility for creating lagged versions of pandas indices and Series.

	The Lag class provides static helpers that shift a pandas Index or Series
	backwards (i.e. create index/value pairs corresponding to v[index - lag]).
	It supports 1D indices and MultiIndex objects via level or dict specifications.

	Key methods
	- series(v, lag, level=None, fkeep=False, bfill='exo', exo=0):
	  Return a pd.Series with values shifted according to `lag`. Handles options:
		fkeep: keep forward-shifted indices outside original domain.
		bfill: how to backfill values not present in original series ('exo','ss', False).
		exo: numeric value used when bfill == 'exo'.
	- idx(idx, lag, level=None):
	  Return a shifted Index (or MultiIndex) corresponding to lag specification.

	Typical usage
	- Create lagged parameters or variables before adding them to linear
	  constraints in LPSys (see symMaps.lpSys.LPSys.initA_lag).
	"""
	@staticmethod
	def series(v, lag, level = None, fkeep = False, bfill = 'exo', exo = 0):
		"""Return a pd.Series shifted by `lag` on `level`.
		Index of the returned series represents positions after applying lag.
		Options:
		  - fkeep: keep forwarded indices outside original domain
		  - bfill: how to fill missing entries ('exo','ss', False)
		  - exo: numeric used when bfill == 'exo'
		"""
		vl = pd.Series(v.values, index = Lag.idx(v.index, lag, level = level))
		if fkeep is False:
			vl = vl[vl.index.isin(v.index)]
		if bfill == 'exo':
			return vl.combine_first(Lag.addExo(v, vl, exo))
		elif bfill == 'ss':
			return vl.combine_first(v)
		elif bfill is False:
			return vl

	@staticmethod
	def idx(idx, lag, level = None):
		"""Return an Index or MultiIndex shifted by `lag`.
		Dispatches to 1D or MultiIndex handlers based on idx type.
		"""
		return Lag.lagMIdx(idx, lag, level = level) if isinstance(idx, pd.MultiIndex) else Lag.lag1dIdx(idx, lag)

	@staticmethod
	def addExo(v, vl, exo):
		return pd.Series(0, index = v[~v.index.isin(vl.index)].index).add(exo)

	@staticmethod
	def lag1dIdx(idx, lag):
		""" Creates symbol[idx-lag] definition """
		return idx+lag

	@staticmethod
	def lagMIdx(idx, lags, level = None):
		return Lag.lagMIdx_dict(idx, lags) if isinstance(lags, dict) else Lag.lagMIdx_level(idx, lags, level)

	@staticmethod
	def lagMIdx_level(idx, lag, level):
		return idx.set_levels(idx.levels[idx.names.index(level)]+lag, level = level)

	@staticmethod
	def lagMIdx_dict(idx, lags):
		""" Dict maps from index level to lag """
		return idx.set_levels([idx.levels[idx.names.index(level)]+lag for level, lag in lags.items()], level = lags.keys())

class Lead(Lag):
	"""
	Lead is a thin wrapper around Lag that applies a forward shift.

	Lead inverts the sign of the lag input and then calls the Lag helpers.
	This allows callers to express leads (future indices) using the same
	interface as lags. All parameters and options are passed through to Lag.

	Example:
	  Lead.series(v, lead, fkeep=True, bfill=False)
	"""
	@staticmethod
	def series(v, lead, **kwargs):
		""" Applies Lag by inverting lead"""
		return Lag.series(v, Lead.invertLag(lead), **kwargs)

	@staticmethod
	def idx(idx, lead, **kwargs):
		""" Applies Lag by inverting lead"""
		return Lag.idx(idx, Lead.invertLag(lead), **kwargs)

	@staticmethod
	def invertLag(lag):
		return {k: -v for k,v in lag.items()} if type(lag) is dict else -lag

class Roll:
	"""
	Utilities to 'roll' (circularly shift) pandas indices and Series.

	Roll performs circular rotations of index levels. Unlike Lag, Roll does not
	create new index elements; it permutes existing ones. Methods mirror those
	of Lag but use numpy.roll semantics. Useful for circular boundary conditions
	or categorical index rotations.

	Key methods
	- series(v, roll, level=None): return a Series whose index is rolled.
	- idx(idx, roll, level=None): return rolled Index or MultiIndex.
	"""
	@staticmethod
	def series(v, roll, level = None):
		"""Return a pd.Series with its index circularly rotated by `roll` on `level`."""
		vl = pd.Series(v.values, index = Roll.idx(v.index, roll, level = level))
		return vl

	@staticmethod
	def idx(idx, roll, level = None):
		"""Return an Index or MultiIndex circularly rotated by `roll`."""
		return Roll.rollMIdx(idx, roll, level = level) if isinstance(idx, pd.MultiIndex) else Roll.roll1dIdx(idx, roll)

	@staticmethod
	def roll1dIdx(idx, roll):
		return pd.Index(np.roll(idx, roll), name = idx.name)

	@staticmethod
	def rollMIdx(idx, rolls, level = None):
		return Roll.rollMIdx_dict(idx, rolls) if isinstance(rolls, dict) else Roll.rollMIdx_level(idx, rolls, level)

	@staticmethod
	def rollMIdx_level(idx, roll, level):
		return idx.set_levels(np.roll(idx.levels[idx.names.index(level)], roll), level = level)

	@staticmethod
	def rollMIdx_dict(idx, rolls):
		return idx.set_levels([np.roll(idx.levels[idx.names.index(level)], roll) for level, roll in rolls.items()], level = rolls.keys())
	
	@staticmethod
	def invertRoll(roll):
		return {k: -v for k,v in roll.items()} if type(roll) is dict else -roll
