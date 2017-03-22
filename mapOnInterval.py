from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, pi, sqrt, log, pi
import haarWavelet as hW
from scipy.interpolate import InterpolatedUnivariateSpline

""" This is a class modelling maps on the interval [0,1]. There are four ways of defining a function: 
	 	-> By explicit discretization values on a grid over [0,1], 
		-> by fourier expansion ([a0, a1, a2, b1, b2] means a0 + a1*cos(pi*x) + a2*cos(2*pi*x) + b1*sin(pi*x) + b2*sin(2*pi*x))
		-> by wavelet expansion as used in haarWavelet.py
		-> by function handle
	Missing information is calculated from the defining parameter (fourier is the exception so far)
"""

class mapOnInterval():
	def __init__(self, inittype, param, numSpatialPoints=2**9, interpolationdegree=3):
		# there are three possibilities of initializing a mapOnInterval instance:
		# 1) By explicit values on a discretization: inittype == "expl"
		# 2) By Fourier expansion: inittype == "fourier"
		# 3) By Haar Wavelet expansion: inittype == "wavelet"
		self._values = None
		self._fouriermodes = None
		self._waveletcoeffs = None
		self.interpolationdegree = 3
		self._handle = None
		self.inittype = inittype
		self.numSpatialPoints = numSpatialPoints
		
		if inittype == "expl": # no Fourier expansion!
			self._values = param
			#self.waveletcoeffs = hW.waveletanalysis(self.values)
			#self._handle = InterpolatedUnivariateSpline(np.linspace(0, 1, len(self.values), endpoint=False), self.values, k=3, ext=3)
		elif inittype == "fourier":
			self._fouriermodes = param # odd cardinality!!
			#self._values = evalmodes(self.fouriermodes, np.linspace(0, 1, numSpatialPoints, endpoint=False))
			#self._waveletcoeffs = hW.waveletanalysis(self.values)
			self._handle = lambda x: evalmodes(self.fouriermodes, x)
		elif inittype == "wavelet": # no Fourier expansion!
			self._waveletcoeffs = param
			#self._values = hW.waveletsynthesis(self.waveletcoeffs)
			#self.handle = InterpolatedUnivariateSpline(np.linspace(0, 1, len(self.values), endpoint=False), self.values, k=3, ext=3)
		elif inittype == "handle":
			self._handle = np.vectorize(param)
			#self._values = self.handle(np.linspace(0, 1, numSpatialPoints, endpoint=False))
			#self.waveletcoeffs = hW.waveletanalysis(self.values)
		else:
			raise ValueError("inittype neither expl nor fourier nor wavelet")
		
		# The next four properties manage the variables values, fouriermodes, waveletcoeffs and handle: As each instance of an moi is generated by one of those, the others might be empty and might still need to be calculated
		
	@property
	def values(self):
		if self._values is None: # property not there yet, get from initialization data
			if self.inittype == "fourier":
				self._values = evalmodes(self.fouriermodes, np.linspace(0, 1, self.numSpatialPoints, endpoint=False))
			elif self.inittype == "wavelet":
				self._values = hW.waveletsynthesis(self.waveletcoeffs)
			elif self.inittype == "handle":
				self._values = self.handle(np.linspace(0, 1, self.numSpatialPoints, endpoint=False))
			else:
				raise Exception("Wrong value for self.inittype")
			return self._values
		else:
			return self._values
	
	@property
	def fouriermodes(self):
		if self._fouriermodes is None:
			if self.inittype == "expl":
				raise NotImplementedError("(expl -> fourier) not yet implemented")
			elif self.inittype == "wavelet":
				raise NotImplementedError("(wavelet -> fourier) not yet implemented")
			elif self.inittype == "handle":
				raise NotImplementedError("(handle -> fourier) not yet implemented")
			else:
				raise Exception("Wrong value for self.inittype")
			return self._fouriermodes
		else:
			return self._fouriermodes
			
	@property
	def waveletcoeffs(self):
		if self._waveletcoeffs is None:
			if self.inittype == "expl":
				self._waveletcoeffs = hW.waveletanalysis(self.values)
			elif self.inittype == "fourier":
				self._waveletcoeffs = hW.waveletanalysis(self.values)
			elif self.inittype == "handle":
				self._waveletcoeffs = hW.waveletanalysis(self.values)
			else:
				raise Exception("Wrong value for self.inittype")
			return self._waveletcoeffs
		else:
			return self._waveletcoeffs		
	
	@property
	def handle(self):
		if self._handle is None:
			if self.inittype == "expl":
				self._handle = InterpolatedUnivariateSpline(np.linspace(0, 1, len(self.values), endpoint=False), self.values, k=self.interpolationdegree, ext=3)
			elif self.inittype == "fourier":
				self._handle = lambda x: evalmodes(self.fouriermodes, x)
			elif self.inittype == "wavelet":
				self._handle = InterpolatedUnivariateSpline(np.linspace(0, 1, len(self.values), endpoint=False), self.values, k=self.interpolationdegree, ext=3)
			else:
				raise Exception("Wrong value for self.inittype")
			return self._handle
		else:
			return self._handle
	
	# overloading of basic arithmetic operations, in order to facilitate f + g, f*3 etc. for f,g mapOnInterval instances
	def __add__(self, m):
		if isinstance(m, mapOnInterval): # case f + g
			if self.inittype == "fourier":
				if m.inittype == "fourier":
					return mapOnInterval("fourier", self.fouriermodes + m.fouriermodes)
				else:
					return mapOnInterval("expl", self.values + m.values)
			elif self.inittype == "expl":
				return mapOnInterval("expl", self.values + m.values)
			elif self.inittype == "wavelet":
				if m.inittype == "wavelet":
					return mapOnInterval("wavelet", [w1 + w2 for w1, w2 in zip(self.waveletcoeffs, m.waveletcoeffs)])
			elif self.inittype == "handle":
				if m.inittype == "fourier" or m.inittype == "handle":
					return mapOnInterval("handle", lambda x: self.handle(x) + m.handle(x))
			else:
				raise Exception("Wrong value for self.inittype in __add__")
		else: # case f + number
			if self.inittype == "handle":
				return mapOnInterval("handle", lambda x: self.handle(x) + m)
			else:
				return mapOnInterval("expl", self.values + m)
	
	def __sub__(self, m):
		if isinstance(m, mapOnInterval): # case f - g
			if self.inittype == "fourier":
				if m.inittype == "fourier":
					return mapOnInterval("fourier", self.fouriermodes - m.fouriermodes)
				else:
					return mapOnInterval("expl", self.values - m.values)
			elif self.inittype == "expl":
				return mapOnInterval("expl", self.values - m.values)
			elif self.inittype == "wavelet":
				if m.inittype == "wavelet":
					return mapOnInterval("wavelet", [w1 - w2 for w1, w2 in zip(self.waveletcoeffs, m.waveletcoeffs)])
			elif self.inittype == "handle":
				if m.inittype == "fourier" or m.inittype == "handle":
					return mapOnInterval("handle", lambda x: self.handle(x) - m.handle(x))
			else:
				raise Exception("Wrong value for self.inittype in __add__")
		else: # case f - number
			if self.inittype == "handle":
				return mapOnInterval("handle", lambda x: self.handle(x) - m)
			else:
				return mapOnInterval("expl", self.values - m)
	
	def __mul__(self, m):
		if isinstance(m, mapOnInterval): # case f * g
			if self.inittype == "fourier":
				return mapOnInterval("expl", self.values * m.values)
			elif self.inittype == "expl":
				return mapOnInterval("expl", self.values * m.values)
			elif self.inittype == "wavelet":
				return mapOnInterval("expl", self.values * m.values)
			elif self.inittype == "handle":
				if m.inittype == "fourier" or m.inittype == "handle":
					return mapOnInterval("handle", lambda x: self.handle(x) * m.handle(x))
			else:
				raise Exception("Wrong value for self.inittype in __add__")
		else: # case f * number
			if self.inittype == "handle":
				return mapOnInterval("handle", lambda x: self.handle(x) * m)
			elif self.inittype == "wavelet":
				return mapOnInterval("wavelet", [w1 * m for w1 in self.waveletcoeffs])
			elif self.inittype == "fourier":
				return mapOnInterval("fourier", [fm * m for fm in self.fouriermodes])
			else:
				return mapOnInterval("expl", self.values * m)
	def __div__(self, m):
		raise Exception("use f * 1/number for f/number")
	def __truediv__(self, m):
		return self.__div__(m)
			

##### So far: integrate and differentiate yield only np-arrays instead of moi functions! Maybe fix this in the future

def integrate(x, f, primitive=True): 
	# integrates fncvals over x, returns primitive if primitive==True and integral over x if primitive==False
	if isinstance(f, mapOnInterval):
		fncvals = f.values
	else: 
		raise Exception()
	assert(len(x) == len(fncvals))
	delx = x[1]-x[0]
	if not primitive:
		return np.trapz(f.values, dx=delx)
	M = fncvals
	res = np.zeros_like(fncvals)
	res[0] = fncvals[0]*delx # should not be used for plotting etc. but is needed for compatibility with differentiate
	for i, val in enumerate(x[1:]): # this is slow!
		y = np.trapz(fncvals[0:i+2], dx=delx)
		res[i+1] = y
	return mapOnInterval("expl", res)
	
def differentiate(x, f): # finite differences
	if isinstance(f, mapOnInterval):
		fncvals = f.values
	else:
		raise Exception()
	fprime = np.zeros_like(fncvals)
	fprime[1:] = (fncvals[1:]-fncvals[:-1])/(x[1]-x[0])
	fprime[0] = fprime[1]
	return mapOnInterval("expl", fprime)

def evalmodes(modesvec, x):
	# evaluates fourier space decomposition in state space
	N = len(modesvec)
	freqs = np.reshape(np.linspace(1, N//2, N/2), (-1, 1))
	x = np.reshape(x, (1, -1))
	entries = 2*pi*np.dot(freqs, x)
	fncvec = np.concatenate((np.tile(np.array([1]),(1,x.shape[1])), np.cos(entries), np.sin(entries)), axis=0)
	return np.reshape(np.dot(modesvec, fncvec), (-1,))
	
if __name__ == "__main__":
	x = np.linspace(0, 1, 2**9, endpoint=False)
	f1 = mapOnInterval("fourier", [0,0,1,0,1], 2**9)
	#plt.ion()
	#plt.plot(x, f1.values)
	#hW.plotApprox(x, f1.waveletcoeffs)
	
	f2 = mapOnInterval("expl", np.array([4,2,3,1,2,3,4,5]), 4)
	#hW.plotApprox(x, f2.waveletcoeffs)
	
	f3 = mapOnInterval("handle", lambda x: sin(3*x)-x**2*cos(x))
	#hW.plotApprox(x, f3.waveletcoeffs)
	
	
	hW.plotApprox(x, (f1*f3).waveletcoeffs)
	plt.show()
	
	
