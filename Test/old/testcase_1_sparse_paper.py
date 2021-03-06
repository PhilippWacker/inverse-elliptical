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

resol = 6
rect = Rectangle((0,0), (1,1), resol=resol)
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
		return  -4/log10(e)*np.logical_or(np.logical_and(np.logical_and(x < 0.5, x >= 0.4375), y < 0.28125), np.logical_and(np.logical_and( x< 0.5 , x >= 0.4375) ,y >= 0.375 - tol)) + 2/log10(e)*np.logical_and(np.logical_and(x < 0.8125, x >= 0.75), np.logical_and(y >= 0.1875, y < 0.75)) + 0
def u_D_term(x, y):
	return np.logical_and(x >= 1-10**-8, True)*2.0

u_D = mor.mapOnRectangle(rect, "handle", lambda x,y: u_D_term(x,y))

def boundary_D_boolean(x): # special Dirichlet boundary condition
		if x[0] >= 1-10**-8:
			return True
		elif x[0] <= 10**-8:
			return True
		else:
			return False

#f = mor.mapOnRectangle(rect, "handle", lambda x, y: 0*x)# (((x-.6)**2 + (y-.85)**2) < 0.1**2)*(-20.0) + (((x-.2)**2 + (y-.75)**2) < 0.1**2)*20.0)
f = Constant(0)

fwd = linEllipt2dRectangle(rect, f, u_D, boundary_D_boolean)
m1 = GeneralizedGaussianWavelet2d(rect, 0.1, 1.5, resol)
m2 = GeneralizedWavelet2d(rect, 0.1, 1.5, resol, p=1.01)
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
	uOpt_sparse = mor.mapOnRectangle(rect, "wavelet", data["uOpt_sparse_waveletcoeffs"])
	uTruth = mor.mapOnRectangle(rect, "handle", lambda x, y: myUTruth(x, y))
	invProb.obs = obs
	invProb.obspos = obspos
	invProb.gamma = gamma
	invProb.resol = resol
	invProb2.obs = obs
	invProb2.obspos = obspos
	invProb2.gamma = gamma
	invProb2.resol = resol
	start = time.time()
	invProb.plotSolAndLogPermeability(uTruth, obs=obs)
	invProb.plotSolAndLogPermeability(uOpt)
	invProb.plotSolAndLogPermeability(uOpt_sparse)
	print("uOpt: in invProb1-norm = \t" + str(invProb.I(uOpt)) + " = " +  str(invProb.Phi(uOpt)) + " + " + str(invProb.prior.normpart(uOpt)) + " = (Phi + norm)")
	print("uOpt: in invProb2-norm = \t" + str(invProb2.I(uOpt)) + " = " +  str(invProb2.Phi(uOpt)) + " + " + str(invProb2.prior.normpart(uOpt)) + " = (Phi + norm)")
	print("uOpt_sparse: in invProb1-norm = " + str(invProb.I(uOpt_sparse)) + " = " +  str(invProb.Phi(uOpt_sparse)) + " + " + str(invProb.prior.normpart(uOpt_sparse)) + " = (Phi + norm)")
	print("uOpt_sparse: in invProb2-norm = " + str(invProb2.I(uOpt_sparse)) + " = " +  str(invProb2.Phi(uOpt_sparse)) + " + " + str(invProb2.prior.normpart(uOpt_sparse)) + " = (Phi + norm)")
	# uOpt_sparse = invProb2.find_uMAP(uOpt, nit=50, method = 'BFGS', adjoint=True, version=0);invProb2.plotSolAndLogPermeability(uOpt_sparse)
	# uOpt = invProb.find_uMAP(uOpt, nit=50, method = 'BFGS', adjoint=True, version=0);invProb.plotSolAndLogPermeability(uOpt)
else:
	N_obs = 500
	obspos = np.random.uniform(0, 1, (2, N_obs))
	obspos = [obspos[0,:], obspos[1, :]]
	invProb.obspos = obspos
	invProb2.obspos = obspos

	#uTruth = mor.mapOnRectangle(rect, "wavelet", packWavelet(unitvec(4, 2)+0.5*unitvec(4,3)))
	#uTruth = m1.sample()
	uTruth = mor.mapOnRectangle(rect, "handle", lambda x, y: myUTruth(x, y))

	obs = invProb.Gfnc(uTruth) + np.random.normal(0, gamma, (N_obs,))
	invProb.plotSolAndLogPermeability(uTruth, obs=obs)
	invProb.obs = obs
	invProb2.obs = obs
	#u0 = mor.mapOnRectangle(rect, "wavelet", m1._mean)
	u0 = mor.mapOnRectangle(rect, "wavelet", m1._mean)
	u02 = mor.mapOnRectangle(rect, "wavelet", m2._mean)
	#uOpt = invProb.find_uMAP(u0, nit=3,  method='BFGS', adjoint=False)
	uOpt = u0
	uOpt2 = u02
	uOpt = invProb.find_uMAP(uOpt, nit=50, method = 'BFGS', adjoint=True, version=0);invProb.plotSolAndLogPermeability(uOpt)
	uOpt2 = invProb2.find_uMAP(uOpt2, nit=50, method = 'BFGS', adjoint=True, version=0);invProb2.plotSolAndLogPermeability(uOpt2)


