from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, pi, sqrt, log, pi, exp, log10
import math
import sys 
sys.path.append('..')
import mapOnRectangle as mor
from fwdProblem import *
from invProblem2d import *
from rectangle import *
import smtplib
from email.mime.text import MIMEText

resol = 7
rect = Rectangle((0,0), (1,1), resol=resol)
rect_coarse = Rectangle((0,0), (1,1), resol=resol-2)
gamma = 0.01

def myUTruth(x, y):
		"""if x[0] <= 0.5 +tol  and x[0] >= 0.45 - tol and x[1] <= 0.5+tol:
			return -4
		elif x[0] <= 0.5+tol and x[0] >= 0.45 - tol and x[1] >= 0.6 - tol:
			return -4
		elif x[0] <= 0.75 + tol and x[0] >= 0.7 - tol and x[1] >= 0.2 - tol and x[1] <= 0.8+tol:
			return 2
		else:
			return 0"""
		#if x.ndim == 1 and x.shape[0] == 2:
		#return  -4/log10(e)*np.logical_or(np.logical_and(np.logical_and(x < 0.5, x >= 0.4375), y < 0.5), np.logical_and(np.logical_and( x< 0.5 , x >= 0.4375) ,y >= 0.625 - tol)) + 2/log10(e)*np.logical_and(np.logical_and(x < 0.8125, x >= 0.75), np.logical_and(y >= 0.1875, y < 0.75)) + 0
		return np.logical_or(np.logical_and(np.logical_and((x+0.5)**2 + (y-0.2)**2 <= 1.2, (x+0.5)**2 + (y-0.25)**2 >= 0.9), y <=0.3), np.logical_and(np.logical_and((x+0.5)**2 + (y-0.2)**2 <= 1.2, (x+0.5)**2 + (y-0.25)**2 >= 0.9), y >=0.5))*(-40.0)
		#return x*0+1

def u_D_term(x, y):
	return np.logical_and(x >= 0.5, y <= 0.625)*0.0

u_D = mor.mapOnRectangle(rect, "handle", lambda x,y: u_D_term(x,y))

def boundary_D_boolean(x): # special Dirichlet boundary condition
		if x[1] <= tol:
			return True
		else:
			return False
f = mor.mapOnRectangle(rect, "handle", lambda x, y: ( ((x-.2)**2 + (y-.6)**2) < 0.1**2)*(-200.0)) #+ (((x-.8)**2 + (y-.75)**2) < 0.05**2)*20.0)


fwd = linEllipt2dRectangle(rect, f, u_D, boundary_D_boolean)
m1 = GeneralizedGaussianWavelet2d(rect_coarse, 0.0001, 1.0, rect_coarse.resol+1)
m2 = GaussianFourier2d(rect, np.zeros((31,31)), 1.0, 1.0)
invProb = inverseProblem(fwd, m1, gamma)
invProb2 = inverseProblem(fwd, m2, gamma)


if len(sys.argv) > 1:
	data = unpickleData(sys.argv[1])
	obspos = data["obspos"]
	obs = data["obs"]
	gamma = data["gamma"]
	resol = data["resol"]
	u0 = mor.mapOnRectangle(rect, "wavelet", data["u0_waveletcoeffs"])
	uOpt = mor.mapOnRectangle(rect, "wavelet", data["uOpt_waveletcoeffs"])
	uTruth = mor.mapOnRectangle(rect, "handle", lambda x, y: myUTruth(x, y))
	invProb.obs = obs
	invProb.obspos = obspos
	invProb.gamma = gamma
	invProb.resol = resol
	invProb2.obs= obs
	invProb2.obspos = obspos
	invProb2.gamma=gamma
	start = time.time()
	invProb.plotSolAndLogPermeability(uOpt)
else:
	N_obs = 200
	obspos = np.random.uniform(0, 1, (2, N_obs))
	obspos = [obspos[0,:], obspos[1, :]]
	
	phi = np.random.uniform(-pi/16, 1.5*pi/4, (N_obs,))
	r = np.random.normal(1.1, 0.1, (N_obs,))
	xx = r*np.cos(phi)-0.5
	yy = r*np.sin(phi)+0.2
	xx = (xx + np.abs(xx))/2 # take positive part
	yy = (yy + np.abs(yy))/2
	yy = 1- (1-yy + np.abs(1-yy))/2 # take part < 1
	obspos = np.concatenate((xx.reshape((-1,1)), yy.reshape((-1,1))), axis=1).T
	
	invProb.obspos = obspos

	#uTruth = mor.mapOnRectangle(rect, "wavelet", packWavelet(unitvec(4, 2)+0.5*unitvec(4,3)))
	#uTruth = m1.sample()
	uTruth_temp = mor.mapOnRectangle(rect_coarse, "handle", lambda x, y: myUTruth(x, y))
		
	uTruth = mor.mapOnRectangle(rect, "wavelet", uTruth_temp.waveletcoeffs)
	#uTruth_wc = mor.mapOnRectangle(rect, "wavelet", packWavelet(np.array(unpackWavelet(uTruth.waveletcoeffs))))
	#uTruth_expl = mor.mapOnRectangle(rect, "expl", np.array(uTruth.values))
	
	#uTruth = uTruth_wc

	obs = invProb.Gfnc(uTruth) + np.random.normal(0, gamma, (N_obs,))
	invProb.plotSolAndLogPermeability(uTruth, obs=obs)
	invProb.obs = obs
	#u0 = mor.mapOnRectangle(rect, "wavelet", m1._mean)
	u0 = mor.mapOnRectangle(rect, "wavelet", m1._mean)
	#uOpt = invProb.find_uMAP(u0, nit=3,  method='BFGS', adjoint=False)
	#start = time.time()
	uOpt = u0
	uOpt = invProb.find_uMAP(uOpt, nit=50, method = 'BFGS', adjoint=True, version=0);invProb.plotSolAndLogPermeability(uOpt)
	for kk in range(25):
		uOpt = invProb.find_uMAP(uOpt, nit=250, method = 'BFGS', adjoint=True, version=0);
	invProb.plotSolAndLogPermeability(uOpt)
	m2mean = m2._mean 
	m2mean[0,0] = 3
	u02 = mor.mapOnRectangle(rect, "fourier", m2mean)
	uOpt2 = u02
	uOpt2 = invProb2.find_uMAP(uOpt2, nit=100, method = 'BFGS', adjoint=False);invProb2.plotSolAndLogPermeability(uOpt2)
