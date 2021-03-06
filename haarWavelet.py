from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, pi, sqrt, log
import time

# CAREFUL: This works only for signals in [0,1]! Also, every signal f has to have number of elements = 2**J for some integer J!


# definition of scaling function, mother wavelet and scaled versions
def phifnc_plain(x):
	if x >= 0:
		if x < 1:
			return 1
	return 0
phifnc = np.vectorize(phifnc_plain)
phi_scale = lambda x, n, k: 2**(-n/2) * phifnc(x/2**(n) - k)
psifnc = lambda x: phifnc(2*x) - phifnc(2*x-1)
psi_scale = lambda x, n, k: 2**(-n/2) * psifnc(x/2**(n) - k)


# wavelet analysis of signal
def waveletanalysis(f):
	a = [f]
	d = [0]
	J = int(log(len(f), 2)) # maximal resolution
	for j in range(J):
		a_last = a[-1]
		a.append((a_last[0::2] + a_last[1::2])/sqrt(2))
		d.append((-a_last[0::2] + a_last[1::2])/sqrt(2))
	
	w = [a[-1]/(2**(J/2))] # adjust for absolute size
	for j in range(J):
		#w.append(d[J-j])
		w.append(d[J-j]/(2**(J/2))) # adjust for absolute size
	return w

# wavelet synthesis of wavelet decomposition (inverse operation of waveletanalysis)
def waveletsynthesis(w,xs=None):
	if True:
		if xs is None:
			J = len(w)-1
			xs = np.linspace(0, 1, 2**J, endpoint=False)
		else:
			J = int(log(len(xs), 2))
		f = np.zeros_like(xs) + w[0]
		for j in range(1, len(w)):
			for k, c in enumerate(w[j]):
				#f = f - c*psi_scale(xs, -j+1, k)
				psivec = np.zeros_like(xs)
				#psivec[2**(J-j)*k:2**(J-j)*k + 2**(J-j-1)] = 1
				#psivec[2**(J-j)*k + 2**(J-j-1):2**(J-j)*(k+1)] = -1
				psivec[2**(J-j+1)*k:2**(J-j+1)*k + 2**(J-j)] = -2**((j-1)/2)
				psivec[2**(J-j+1)*k + 2**(J-j):2**(J-j+1)*(k+1)] = 2**((j-1)/2)
				f = f + c*psivec
		"""f = np.zeros_like(xs)
		for j in range(len(w)):
			for k, c in enumerate(w[j]):
				#f = f - c*psi_scale(xs, -j+1, k)
				psivec = np.zeros_like(xs)
				psivec[2**(J-j)*k:2**(J-j)*k + 2**(J-j-1)] = 1
				psivec[2**(J-j)*k + 2**(J-j-1):2**(J-j)*(k+1)] = -1
				f = f - c*psivec
		#return f/2**(J/2)"""
	return f

def bumpletsynthesis(w, xs=None):
	if True:
		if xs is None:
			J = len(w)-1
			xs = np.linspace(0, 1, 2**J, endpoint=False)
		else:
			J = int(log(len(xs), 2))
		f = np.zeros_like(xs) + w[0]
		for j in range(1, len(w)):
			for k, c in enumerate(w[j]):
				#f = f - c*psi_scale(xs, -j+1, k)
				psivec = np.zeros_like(xs)
				#psivec[2**(J-j)*k:2**(J-j)*k + 2**(J-j-1)] = 1
				#psivec[2**(J-j)*k + 2**(J-j-1):2**(J-j)*(k+1)] = -1
				psivec[2**(J-j)*k:2**(J-j)*k + 2**(J-j)] = 1.0
				f = f + c*psivec
		"""f = np.zeros_like(xs)
		for j in range(len(w)):
			for k, c in enumerate(w[j]):
				#f = f - c*psi_scale(xs, -j+1, k)
				psivec = np.zeros_like(xs)
				psivec[2**(J-j)*k:2**(J-j)*k + 2**(J-j-1)] = 1
				psivec[2**(J-j)*k + 2**(J-j-1):2**(J-j)*(k+1)] = -1
				f = f - c*psivec
		#return f/2**(J/2)"""
	return f

def getApprox(x, w):
	J = len(w)-1
	f = np.zeros_like(x)+w[0]
	recon = [f]
	for j in range(1, len(w)):
		for k, c in enumerate(w[j]):
			psivec = np.zeros_like(x)
			psivec[2**(J-j+1)*k:2**(J-j+1)*k + 2**(J-j)] = -2**((j-1)/2)
			psivec[2**(J-j+1)*k + 2**(J-j):2**(J-j+1)*(k+1)] = 2**((j-1)/2)
			f = f + c*psivec
		recon.append(f)
	return recon
	
# utility for plotApprox
"""def getApprox_old(x, w):
	J = len(w)-1
	recon = [np.zeros_like(x)]
	for j in range(J+1):
		term = 0
		for k, c in enumerate(w[j]):
			term = term + c*psi_scale(x, -j+1, k)
		recon.append(recon[-1] - term)
	#for k in range(len(recon)):
	#	recon[k] = recon[k]/2**(J/2)
	return recon"""

# plots successive approximations
def plotApprox(x, w):
	recon = getApprox(x, w)
	plt.figure()
	for n, r in enumerate(recon):
		plt.subplot(len(recon), 1, n+1)
		plt.plot(x, r) 


if __name__ == "__main__":
	J = 10
	num = 2**J
	x = np.linspace(0, 1, 2**(J), endpoint=False)
	gg1 = lambda x: 1 + 2**(-J)/(x**2+2**J) + 2**J/(x**2 + 2**J)*np.cos(32*x)
	g1 = lambda x: gg1(2**J*x)
	gg2 = lambda x: (1 - 0.4*x**2)/(2**(J+3)) + np.sin(7*x/(2*pi))/(1 + x**2/2**J)
	g2 = lambda x: gg2(2**J*x)
	gg3 = lambda x: 3 + 3*(x**2/(2**(2*J)))*np.sin(x/(8*pi))
	g3 = lambda x: gg3(2**J*x)
	gg4 = lambda x: (x**2/3**J)*0.1*np.cos(x/(2*pi))-x**3/8**J + 0.1*np.sin(3*x/(2*pi))
	g4 = lambda x: gg4(2**J*x)
	

	vec1 = g2(x[0:int(0.7*2**(J-2))])
	vec2 = g1(x[int(0.7*2**(J-2)):int(0.92*2**(J-1))])
	vec3 = g3(x[int(0.92*2**(J-1)):int(2**(J)-0.8*2**(J-1))])
	vec4 = g4(x[int(2**(J)-0.8*2**(J-1)):2**(J)])

	f = np.concatenate((vec1, vec2, vec3, vec4))

	w = waveletanalysis(f)
	ff = waveletsynthesis(w)
	plt.figure()
	plt.ion()
	plt.plot(x, f)
	plt.plot(x, ff,'r')
	plt.show()
	
	plt.ion()
	plt.plot(x, f)
	plt.plot(x, ff, 'r')
	#plotApprox(x, w)
	recon = getApprox(x, w)
	plt.figure()
	NN = 11
	for k in range(NN):
		plt.subplot(NN, 1, k+1)
		plt.plot(x, recon[k])
		plt.ylim([-2.7,3.8])
		plt.axis('off')
		plt.gca().axes.get_yaxis().set_visible(False)
	
	"""x = np.linspace(0, 1, 2**(13), endpoint=False)
	f = x**2*np.sin(12*x)
	w = waveletanalysis(f)
	ff = waveletsynthesis(w, x)
	plt.plot(x, f)
	plt.plot(x, ff, 'r')
	plt.ion()
	plt.show()"""




