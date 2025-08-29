import itertools, numpy as np, pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from collections.abc import Iterable
from six import string_types
from copy import deepcopy
_numtypes = (int,float,np.generic)
_adj_admissable_types = (pd.Index, pd.Series, pd.DataFrame)

# Content:
# 0. Small auxiliary functions
# 1. cartesianProductIndex: Creates sparse, cartesian product from iterator of indices.
# 3. adj: A small class used to subset and adjust pandas-like symbols.


### -------- 	0: Small, auxiliary functions	-------- ###
def noneInit(x,FallBackVal):
	return FallBackVal if x is None else x

def dictInit(key,df_val,kwargs):
	return kwargs[key] if key in kwargs else df_val

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

def sortAll(v, order = None):
	return reorderStd(v, order=order).sort_index() if isinstance(v, (pd.Series, pd.DataFrame)) else v

def reorderStd(v, order=None):
	return v.reorder_levels(noneInit(order, sorted(getIndex(v).names))) if isinstance(getIndex(v), pd.MultiIndex) else v


### -------- 	1. Cartesian product index	 -------- ###
def cartesianProductIndex(indices):
	""" Return the cartesian product of pandas indices; assumes no overlap in levels of indices. """
	if any((i.empty for i in indices)):
		return pd.MultiIndex.from_tuples([], names = [n for l in indices for n in l.names]) 
	else: 
		ndarray = fastCartesianProduct([i.values for i in indices])
		return pd.MultiIndex.from_arrays(concatArrays(ndarray, indices).T, names = [n for l in indices for n in l.names])

# Auxiliary function for cartesianProductIndex
def fastCartesianProduct(arrays):
	la = len(arrays)
	L = *map(len, arrays), la
	dtype = np.result_type(*arrays)
	arr = np.empty(L, dtype=dtype)
	arrs = *itertools.accumulate(itertools.chain((arr,), itertools.repeat(0, la-1)), np.ndarray.__getitem__),
	idx = slice(None), *itertools.repeat(None, la-1)
	for i in range(la-1, 0, -1):
		arrs[i][..., i] = arrays[i][idx[:la-i]]
		arrs[i-1][1:] = arrs[i]
	arr[..., 0] = arrays[0][idx]
	return arr.reshape(-1, la)

# Auxiliary function for cartesianProductIndex
def getndarray(onedarray):
	return pd.MultiIndex.from_tuples(onedarray).to_frame(index=False).values

# Auxiliary function for cartesianProductIndex
def ndarray_or_1darray(ndarray, indices, i):
	return getndarray(ndarray[:,i]) if isinstance(indices[i], pd.MultiIndex) else ndarray[:,i:i+1]

# Auxiliary function for cartesianProductIndex
def concatArrays(ndarray, indices):
	return np.concatenate(tuple(ndarray_or_1darray(ndarray, indices, i) for i in range(len(indices))), axis=1)

### -------- 	3. Class used for adjusting pandas objects	 -------- ###
class adj:
	@staticmethod
	def rc_AdjPd(symbol, alias = None, lag = None):
		if isinstance(symbol, pd.Index):
			return adj.AdjAliasInd(adj.AdjLagInd(symbol, lag=lag), alias = alias)
		elif isinstance(symbol, pd.Series):
			return symbol.to_frame().set_index(adj.AdjAliasInd(adj.AdjLagInd(symbol.index, lag=lag), alias=alias),verify_integrity=False).iloc[:,0]
		elif isinstance(symbol, pd.DataFrame):
			return symbol.set_index(adj.AdjAliasInd(adj.AdjLagInd(symbol.index, lag=lag), alias=alias),verify_integrity=False)
		elif hasattr(symbol,'v'):
			return adj.rc_AdjPd(symbol.vals, alias = alias, lag = lag)
		elif isinstance(symbol, _numtypes):
			return symbol
		else:
			raise TypeError(f"rc_AdjPd only uses instances {_adj_admissable_types} or gpy. Input was type {type(symbol)}")

	@staticmethod
	def AdjLagInd(index_,lag=None):
		if lag:
			if isinstance(index_,pd.MultiIndex):
				return index_.set_levels([index_.levels[index_.names.index(k)]+v for k,v in lag.items()], level=lag.keys())
			elif list(index_.domains)==list(lag.keys()):
				return index_+list(lag.values())[0]
		else:
			return index_
	@staticmethod
	def AdjAliasInd(index_,alias=None):
		alias = noneInit(alias,{})
		return index_.set_names([x if x not in alias else alias[x] for x in index_.names])
	
	@staticmethod
	def rc_pd(s=None,c=None,alias=None,lag=None, pm = True, **kwargs):
		return s if isinstance(s, _numtypes) else adj.rctree_pd(s=s, c = c, alias = alias, lag = lag, pm = pm, **kwargs)

	@staticmethod
	def rc_pdInd(s=None,c=None,alias=None,lag=None,pm=True,**kwargs):
		return None if isinstance(s,_numtypes) else adj.rctree_pdInd(s=s,c=c,alias=alias,lag=lag,pm=pm,**kwargs)

	@staticmethod
	def rctree_pd(s=None,c=None,alias=None,lag =None, pm = True, **kwargs):
		a = adj.rc_AdjPd(s,alias=alias,lag=lag)
		if pm:
			return a[adj.point_pm(getIndex(a), c, pm)]
		else:
			return a[adj.point(getIndex(a) ,c)]
	@staticmethod
	def rctree_pdInd(s=None,c=None,alias=None,lag=None,pm=True,**kwargs):
		a = adj.rc_AdjPd(s,alias=alias,lag=lag)
		if pm:
			return getIndex(a)[adj.point_pm(getIndex(a), c, pm)]
		else:
			return getIndex(a)[adj.point(getIndex(a),c)]
	@staticmethod
	def point_pm(pdObj,vi,pm):
		if isinstance(vi ,_adj_admissable_types) or hasattr(vi, 'v'):
			return adj.bool_ss_pm(pdObj,getIndex(vi),pm)
		elif isinstance(vi,dict):
			return adj.bool_ss_pm(pdObj,adj.rctree_pdInd(**vi),pm)
		elif isinstance(vi,tuple):
			return adj.rctree_tuple_pm(pdObj,vi,pm)
		elif vi is None:
			return pdObj == pdObj
	@staticmethod
	def point(pdObj, vi):
		if isinstance(vi ,_adj_admissable_types) or hasattr(vi, 'v'):
			return adj.bool_ss(pdObj,getIndex(vi))
		elif isinstance(vi,dict):
			return adj.bool_ss(pdObj,adj.rctree_pdInd(**vi))
		elif isinstance(vi,tuple):
			return adj.rctree_tuple(pdObj,vi)
		elif vi is None:
			return pdObj == pdObj
	@staticmethod
	def rctree_tuple(pdObj,tup):
		if tup[0]=='not':
			return adj.translate_k2pd(adj.point(pdObj,tup[1]),tup[0])
		else:
			return adj.translate_k2pd([adj.point(pdObj,vi) for vi in tup[1]],tup[0])
	@staticmethod
	def rctree_tuple_pm(pdObj,tup,pm):
		if tup[0]=='not':
			return adj.translate_k2pd(adj.point_pm(pdObj,tup[1],pm),tup[0])
		else:
			return adj.translate_k2pd([adj.point_pm(pdObj,vi,pm) for vi in tup[1]],tup[0])
	@staticmethod
	def bool_ss(pdObjIndex,ssIndex):
		o,d = adj.overlap_drop(pdObjIndex,ssIndex)
		return pdObjIndex.isin([]) if len(o)<len(ssIndex.names) else pdObjIndex.droplevel(d).isin(adj.reorder(ssIndex,o))
	@staticmethod
	def bool_ss_pm(pdObjIndex,ssIndex,pm):
		o = adj.overlap_pm(pdObjIndex, ssIndex)
		if o:
			return pdObjIndex.droplevel([x for x in pdObjIndex.names if x not in o]).isin(adj.reorder(ssIndex.droplevel([x for x in ssIndex.names if x not in o]),o))
		else:
			return pdObjIndex==pdObjIndex if pm is True else pdObjIndex.isin([])
	@staticmethod
	def overlap_drop(pdObjIndex,index_):
		return [x for x in pdObjIndex.names if x in index_.names],[x for x in pdObjIndex.names if x not in index_.names]
	@staticmethod
	def overlap_pm(pdObjIndex,index_):
		return [x for x in pdObjIndex.names if x in index_.names]
	@staticmethod
	def reorder(index_,o):
		return index_ if len(index_.names)==1 else index_.reorder_levels(o)
	@staticmethod
	def translate_k2pd(l,k):
		if k == 'and':
			return sum(l)==len(l)
		elif k == 'or':
			return sum(l)>0
		elif k == 'not' and isinstance(l,(list,set)):
			return ~l[0]
		elif k == 'not':
			return ~l

class Broadcast:
	@staticmethod
	def idx(x,y, how = 'inner'):
		""" 
		Broadcast indices x,y. Cartesian product for domains that are not overlapping, merge on inner. 
		"""
		overlap = [d for d in x.names if d in y.names]
		if overlap:
			df = pd.merge(x.to_frame(index=False), y.to_frame(index=False), on = overlap, how = how)
			if df.shape[1] == 1:
				return pd.Index(df.iloc[:,0], name = df.columns[0])
			else:
				return pd.MultiIndex.from_frame(df[list(x.names)+[name for name in y.names if name not in overlap]])
		else:
			return cartesianProductIndex([x, y])

	@staticmethod
	def seriesToIdx(series, idx, how = 'left'):
		""" 
		Broadcast a Series (indexed by Index or MultiIndex) to align with idx.
		Values from `series` are repeated across the new dimensions as appropriate
		(i.e., Cartesian expansion along dimensions that series doesn't have).
		Assumes that dimensions in series overlaps with domains in idx.

		Parameters
		----------
		series : pd.Series 
		idx : pd.MultiIndex (or Index)

		Returns
		-------
		broadcasted_series : pd.Series 
		"""
		dfSeries = series.to_frame(name='_values_').reset_index()
		overlap = [d for d in series.index.names if d in idx.names]
		if not overlap:
			raise ValueError("Series has no common index names with idx." 
							 "Broadcasting requires reconciling what values in series are mapped to domains in idx.")
		df = pd.merge(idx.to_frame(index=False), dfSeries, on = overlap, how = how)
		fullDomains = list(idx.names)+[name for name in series.index.names if name not in overlap]
		if len(fullDomains)==1:
			return pd.Series(df['_values_'].values, index = pd.Index(df.iloc[:,0], name = idx.name), name = series.name)
		else:
			return pd.Series(df['_values_'].values, index = pd.MultiIndex.from_frame(df[fullDomains]), name = series.name)

	@staticmethod
	def series(x, y, how = 'inner'):
		""" Broadcast, x,y to common index/multiindex. Return both."""
		idx = Broadcast.idx(x.index, y.index, how = how)
		return Broadcast.seriesToIdx(x, idx), Broadcast.seriesToIdx(y, idx)


	@staticmethod
	def valuesToIdx(values, idx, how = 'left'):
		"""
		If isinstance(values, pd.Series) --> use seriesToIdx.
		If values is not an iterable (or string) --> return pd.Series(values, index = idx)  
		"""
		if isinstance(values, pd.Series):
			return Broadcast.seriesToIdx(values, idx, how = how)
		elif not is_iterable(values):
			return pd.Series(values, index = idx)
		else:
			raise TypeError("values can only be pd.Series or a scalar to be broadcasted to index")

	@staticmethod
	def values(x, y, how = 'inner'):
		""" Equivalent to series method, but allows for x,y to be scalars."""
		if all((isinstance(k, pd.Series) for k in (x,y))):
			return Broadcast.series(x,y,how=how)
		elif isinstance(x, pd.Series):
			return x, Broadcast.valuesToIdx(y, x.index, how =how)
		elif isinstance(y, pd.Series):
			return Broadcast.valuesToIdx(x, y.index, how = how)
		else:
			return x,y

class ExcelSymbolLoader:
	"""
	Reads a symbol-oriented Excel file with a README sheet.

	README columns (minimum): Sheet | Type
	Optional: Unit | Index | Description  (Index is documentation-only)

	- 'set' sheets:
		One or more columns, each column name becomes the index level name.
		1 column  -> pd.Index
		2+ columns -> pd.MultiIndex
		The loader uses the *sheet* column names and order (NOT README.Index).

	- 'variable' sheets:
		Value column name must equal the sheet name (symbol).
		Index columns are *all other columns in the sheet*, in sheet order.
		Returns a pd.Series named after the sheet.

	- 'scalar' sheets:
		Single column named after the sheet; first non-NA value taken as scalar.

	Parameters
	----------
	path : str
		Path to the Excel workbook.
	readme_sheet : str
		Name of the README sheet.
	validate_readme_index : bool
		If True, validate that columns listed in README.Index exist in the sheet.
		Order is not enforced; this is a presence-only check.
		(No use for construction.)
	"""

	def __init__(
		self,
		path: str,
		readme_sheet: str = "README",
		validate_readme_index: bool = False,
	):
		self.path = path
		self.readme_sheet = readme_sheet
		self.validate_readme_index = validate_readme_index

		self._xls: Optional[pd.ExcelFile] = None
		self._readme: Optional[pd.DataFrame] = None

	# ---- Public API ---------------------------------------------------------
	def __call__(self) -> Dict[str, Any]:
		"""Load all symbols defined in README, using per-type helpers."""
		self._xls = pd.ExcelFile(self.path)
		self._readme = pd.read_excel(self._xls, self.readme_sheet)

		required_cols = {"Sheet", "Type"}
		missing = required_cols - set(self._readme.columns)
		if missing:
			raise ValueError(f"README is missing required columns: {missing}")

		data: Dict[str, Any] = {}
		meta: Dict[str, Dict[str, Any]] = {}

		for _, row in self._readme.iterrows():
			sheet = str(row["Sheet"])
			typ = str(row["Type"]).strip().lower()
			unit = row.get("Unit", None)
			desc = row.get("Description", None)
			idx_doc = row.get("Index", None)  # doc only; not used for construction

			if sheet == self.readme_sheet:
				continue
			if sheet not in self._xls.sheet_names:
				raise ValueError(f"Sheet '{sheet}' listed in README not found in workbook.")

			df = pd.read_excel(self._xls, sheet_name=sheet)
			df = self._prepare_sheet(df)

			if typ == "set":
				obj = self._load_set(sheet, df, idx_doc)
			elif typ == "variable":
				obj = self._load_variable(sheet, df, idx_doc)
			elif typ == "scalar":
				obj = self._load_scalar(sheet, df)
			else:
				raise ValueError(f"Unknown Type '{typ}' for sheet '{sheet}'")

			data[sheet] = obj
			meta[sheet] = {
				"Type": typ,
				"Unit": unit,
				"Index": idx_doc,		 # documentation only
				"Description": desc
			}

		# Optional metadata
		data["__meta__"] = pd.DataFrame(meta).T
		return data

	# ---- Helpers (type-specific) -------------------------------------------

	def _load_set(self, sheet: str, df: pd.DataFrame, idx_doc) -> Any:
		"""Build a pd.Index or pd.MultiIndex from a set sheet."""
		if df.shape[1] == 0:
			raise ValueError(f"Set sheet '{sheet}' must have at least one column.")

		# Validate (documentation-only)
		if self.validate_readme_index and pd.notna(idx_doc):
			expect = self._split_doc_index(idx_doc)
			missing = [c for c in expect if c not in df.columns]
			if missing:
				raise ValueError(
					f"Set sheet '{sheet}' is missing columns listed in README.Index: {missing}"
				)

		# Use *sheet* columns and order as the definition, not README.Index
		cols = list(df.columns)
		df_clean = df.dropna(how="all", subset=cols)

		if len(cols) == 1:
			col = cols[0]
			return pd.Index(df_clean[col].dropna(), name=col)
		else:
			# MultiIndex: level names are the sheet's column names in the given order
			return pd.MultiIndex.from_frame(df_clean[cols], names=cols)

	def _load_variable(self, sheet: str, df: pd.DataFrame, idx_doc) -> pd.Series:
		"""
		Build a pd.Series from a variable sheet.
		Uses all columns except the value column (== sheet name) as index columns.
		Sheet column order defines index level order.
		"""
		if sheet not in df.columns:
			raise ValueError(
				f"Variable sheet '{sheet}' must contain a value column named '{sheet}'. "
				f"Found columns: {list(df.columns)}"
			)

		# Validate (documentation-only)
		if self.validate_readme_index and pd.notna(idx_doc):
			expect = set(self._split_doc_index(idx_doc))
			missing = [c for c in expect if c not in df.columns]
			if missing:
				raise ValueError(
					f"Variable sheet '{sheet}' is missing index columns listed in README.Index: {missing}"
				)

		idx_cols = [c for c in df.columns if c != sheet]
		if len(idx_cols) == 0:
			# 0-D variable: use first non-NA value
			vals = df[sheet].dropna()
			if vals.empty:
				raise ValueError(f"Variable sheet '{sheet}' has no non-NA values.")
			s = pd.Series(vals.iloc[0], name=sheet)
			return s

		# Respect *sheet* column order for index levels
		dfv = df.dropna(subset=[sheet])
		s = dfv.set_index(idx_cols)[sheet]
		s.name = sheet
		return s

	def _load_scalar(self, sheet: str, df: pd.DataFrame):
		"""Build a scalar from a scalar sheet (single column named after sheet)."""
		if sheet not in df.columns:
			raise ValueError(f"Scalar sheet '{sheet}' must have a single column named '{sheet}'.")
		vals = df[sheet].dropna()
		if vals.empty:
			raise ValueError(f"Scalar sheet '{sheet}' contains no value.")
		return vals.iloc[0]

	# ---- Internal utilities -------------------------------------------------
	@staticmethod
	def _prepare_sheet(df: pd.DataFrame) -> pd.DataFrame:
		"""Normalize a sheet: drop fully empty rows, drop unnamed columns."""
		df = df.dropna(how="all")
		# Drop unnamed columns that sometimes appear (e.g., trailing blanks)
		cols = [c for c in df.columns if isinstance(c, str) and c.strip() != ""]
		return df[cols]

	@staticmethod
	def _split_doc_index(spec) -> List[str]:
		"""Split README.Index doc string into list of column names (doc-only)."""
		if pd.isna(spec):
			return []
		raw = str(spec).strip()
		if not raw or raw == "-":
			return []
		# Accept separators: ';', ',', or whitespace
		if ";" in raw or "," in raw:
			out = []
			for chunk in raw.replace(",", ";").split(";"):
				t = chunk.strip()
				if t:
					out.append(t)
			return out
		# Fallback: whitespace-separated
		return [p for p in raw.split() if p]

class adjMultiIndex:
	@staticmethod
	def bc(x,y,fill_value = 0):
		""" Broadcast domain of 'x' to conform with domain of 'y'. """
		y, y_dom, x_dom = getIndex(y), getDomains(y), getDomains(x)
		if y_dom:
			if not x_dom:
				return pd.Series(x, index = y)
			elif set(x_dom).intersection(set(y_dom)):
				return x.sort_index().add(pd.Series(0, index = y).sort_index(),fill_value=fill_value) if (set(x_dom)-set(y_dom)) else pd.Series(0, index = y).sort_index().add(x.sort_index(),fill_value=fill_value)
			else:
				return pd.Series(0, index = cartesianProductIndex([getIndex(x),y])).add(x,fill_value=fill_value)
		else:
			return x
	@staticmethod
	def bcAdd(x,y,fill_value = 0):
		""" broadcast domain of 'x' to conform with domain of 'y' and add"""
		y_dom, x_dom = getDomains(y), getDomains(x)
		if y_dom:
			if not x_dom:
				return y+x
			elif set(x_dom).intersection(set(y_dom)):
				return x.sort_index().add(y.sort_index(), fill_value = fill_value) if (set(x_dom)-set(y_dom)) else y.sort_index().add(x.sort_index(), fill_value=fill_value)
			else:
				return pd.Series(0, index = cartesianProductIndex([getIndex(x),getIndex(y)])).add(x,fill_value=fill_value).add(y, fill_value=fill_value)
		else:
			return x+y
	@staticmethod
	def applyMult(symbol, mapping):
		""" Apply 'mapping' to a symbol using multiindex """
		if isinstance(symbol,pd.Index):
			try: 
				return (pd.Series(0, index = symbol).sort_index().add(pd.Series(0, index = adj.rc_pd(mapping,symbol)).sort_index())).dropna().index.reorder_levels(symbol.names+[k for k in mapping.names if k not in symbol.names])
			except KeyError:
				return adhocFix_pandasRemovesIndexLevels(symbol,mapping)
		elif isinstance(symbol,pd.Series):
			if symbol.empty:
				return pd.Series([], index = pd.MultiIndex.from_tuples([], names = symbol.index.names + [k for k in mapping.names if k not in symbol.index.names]))
			else:
				s = symbol.sort_index().add(pd.Series(0, index = adj.rc_pd(mapping,symbol)).sort_index())
				try: 
					return s.reorder_levels(symbol.index.names+[k for k in mapping.names if k not in symbol.index.names])
				except KeyError:
					s.index = adhocFix_pandasRemovesIndexLevels(s.index, mapping)
					return s
	@staticmethod
	def grid(v0,vT,index,gridtype='linear',phi=1):
		""" If v0, vT are 1d numpy arrays, returns 2d array. If scalars, returns 1d arrays. """
		if gridtype == 'linear':
			return np.linspace(v0,vT,len(index))
		elif gridtype=='polynomial':
			return np.array([v0+(vT-v0)*((i-1)/(len(index)-1))**phi for i in range(1,len(index)+1)])
	@staticmethod
	def addGrid(v0,vT,index,name,gridtype = 'linear', phi = 1, sort_levels=None, sort_index = False):
		""" NB: Make sure that v0 and vT are sorted similarly (if they are defined over indices, that is) """
		if sort_index:
			v0 = v0.sort_index()
			vT = vT.sort_index()
		if isinstance(v0,pd.Series):
			return pd.DataFrame(adjMultiIndex.grid(v0,vT,index,gridtype=gridtype,phi=phi).T, index = v0.index, columns = index).stack().rename(name).reorder_levels(index.names+v0.index.names if sort_levels is None else sort_levels)
		else:
			return pd.Series(adjMultiIndex.grid(v0,vT,index,gridtype=gridtype,phi=phi), index = index,name=name)

def adhocFix_pandasRemovesIndexLevels(symbol, mapping):
	""" When multiindices are matched, redundant index levels are dropped automatically - this keeps them """
	s1,s2 = pd.Series(0, index = symbol), pd.Series(0, index = adj.rc_pd(mapping,symbol))
	x,y = s1.add(s2).dropna().index, s2.add(s1).dropna().index
	x_df, y_df = x.to_frame().set_index(list(set(x.names).intersection(y.names))), y.to_frame().set_index(list(set(x.names).intersection(y.names)))
	return pd.MultiIndex.from_frame(pd.concat([x_df, y_df], axis =1).reset_index())