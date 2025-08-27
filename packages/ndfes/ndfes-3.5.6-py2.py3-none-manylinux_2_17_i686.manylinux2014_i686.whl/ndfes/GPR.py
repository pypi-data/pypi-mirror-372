#!/usr/bin/env python3


class GPR(object):    
    """A class to perform Gaussian Process Regression. This class is a wrapper
       around sklearn.gaussian_process to enable support for gradient 
       evaluation of the GPR fit.

    Attributes
    ----------
    x : numpy.array, shape=(npts,ndim)
        The sampled data used to perform the fit
    
    y : numpy.array, shape=(npts)
        The sample values used to perform the fit

    dy : numpy.array, shape=(npts)
        The sample standard deviations used to perform the fit

    y0 : float
        The y0 value is subtracted from the interpolated values 

    gpr : sklearn.gaussian_process.GaussianProcessRegressor
        The GPR object that actually performs the calculations

    norm : sklearn.preprocessing.StandardScaler
        An object that transforms the interpolated features into a standard
        range to avoid dominating the fit by features that have a large range.
        The normalizer scales and shifts the features so it has 0 mean and
        unit standard deviation. xt = scale*x + shift

    xt : numpy.array, shape=(npts,ndim)
        The normalized sample data used to train the GPR. Interpolation from
        the trained model requires the same transformation to be applied to
        the interpolated points, which is performed internally by the class.
        

    Methods
    -------
    """
    
    def __init__( self, x, y, dy=None, y0=0,
                  n_restarts_optimizer=30,
                  normalize_y=True,
                  extra_error=0,
                  sigma_fit_tol=1000,
                  rbf_val=1.0,
                  rbf_val_min=1.e-3,
                  rbf_val_max=1.e+5,
                  const_val=1.0,
                  const_val_min=1.e-4,
                  const_val_max=1.e+4 ):
        """
        Parameters
        ----------
        x : numpy.array, shape=(npts,ndim)
            The sampled data used to perform the fit
    
        y : numpy.array, shape=(npts)
            The sample values used to perform the fit

        dy : numpy.array, shape=(npts), optional
            The sample standard deviations used to perform the fit

        y0 : float, default=0
            A value subtracted from the interpolated values

        n_restarts_optimizer : int, default=30
            The number of restarts of the optimizer for finding the kernel’s
            parameters which maximize the log-marginal likelihood.

        normalize_y : bool, default=True
            Whether or not to normalized the target values y by removing the
            mean and scaling to unit-variance. This is recommended for cases
            where zero-mean, unit-variance priors are used.
        
        extra_error : float, default=0
            Value added to the diagonal of the kernel matrix during fitting. 
            This can prevent a potential numerical issue during fitting, by 
            ensuring that the calculated values form a positive definite 
            matrix. It can also be interpreted as the variance of additional
            Gaussian measurement noise on the training observations.  Setting
            alpha to a nonzero number is the same as adding sqrt(alpha) to each
            element of the dy array.

        sigma_fit_tol : float, default=1000
            If the GPR fit does not match the points to within 
            y +/- (dy * sigma_fit_tol), then reperform the GPR fit with
            reduced errors for those points that were too far away from
            the input. This is an iterative procedure, so it can potentially
            be very expensive.  The default value was chosen such that
            the first iteration would be necessary under normal circumstances

        rbf_val : float or numpy.array with shape=(ndim,), default=1.0
            Initial value of the RBF length_scale parameter. If a float, 
            an isotropic kernel is used. If an array, an anisotropic kernel
            is used where each dimension of l defines the length-scale of 
            the respective feature dimension

        rbf_val_min : float, default=1.e-3
            Lower bound of the RBF length_scale parameter

        rbf_val_max : float, default=1.e+5
            Upper bound of the RBF length_scale parameter

        const_val : float, default=1.0
            Initial value of the constant kernel parameter

        const_val_min : float, default=1.e-4
            Lower bound of the constant kernel parameter

        const_val_max : float, default=1.e+4
            Upper bound of the constant kernel parameter

        """

        import numpy as np
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
        from sklearn.preprocessing import StandardScaler
        import sys
        
        xarr = np.array(x)
        if len(xarr.shape) == 1:
            self.x = np.atleast_2d(xarr).T
        else:
            self.x = xarr
        self.norm = StandardScaler().fit(self.x)
        self.xt = self.norm.transform(self.x)

        self.y = np.array(y)
        self.y0 = y0
        err = np.zeros( (self.y.shape[0]) )
        if dy is not None:
            self.dy = np.array(dy)
            err = self.dy**2 + extra_error**2
        else:
            self.dy = None
            err = err + extra_error**2


        params = { 'k1__constant_value': const_val,
                   'k1__constant_value_bounds': (const_val_min, const_val_max),
                   'k2__length_scale': rbf_val,
                   'k2__length_scale_bounds': (rbf_val_min,
                                               rbf_val_max)}
        
        kernel = C(params['k1__constant_value'],
                   params['k1__constant_value_bounds']) * \
                   RBF(params['k2__length_scale'],
                       params['k2__length_scale_bounds'])
            
        if sum(err) <= 1.e-12 or sigma_fit_tol < 1.e-6:
            sys.stderr.write("Performing GPR fit iteration " +
                             "assuming all points have no error\n")
            
            self.gpr = GaussianProcessRegressor\
                (kernel=kernel,
                 n_restarts_optimizer=n_restarts_optimizer,
                 normalize_y=normalize_y)

            self.gpr.fit(self.xt,self.y)
        
        else:

            terr = np.zeros( err.shape )
            terr[:] = err[:]
            fitok = False
            for it in range(200):

                if it > 0:
                    params = self.gpr.kernel_.get_params()
                    kernel = C(params['k1__constant_value'],
                               params['k1__constant_value_bounds']) * \
                               RBF(params['k2__length_scale'],
                                   params['k2__length_scale_bounds'])
                    
                self.gpr = GaussianProcessRegressor\
                    (kernel=kernel,
                     n_restarts_optimizer=n_restarts_optimizer,
                     alpha=terr,
                     normalize_y=normalize_y)

                sys.stderr.write("Performing GPR fit iteration " +
                                 "%i to achieve agreement to within "%(it) +
                                 "%.2f sigma of the errors\n"%(sigma_fit_tol))
                
                self.gpr.fit(self.xt,self.y)

                yp = self.GetValues(self.x).values
                
                allok = True
                numnotok = 0
                numchange = 0
                for ipt in range(err.shape[0]):
                    if err[ipt] < 1.e-12:
                        continue
                    sigma = np.sqrt(err[ipt])
                    ydif = abs(yp[ipt]-self.y[ipt])
                    ytol = sigma*sigma_fit_tol

                    haserr = terr[ipt] > 1.e-12

                    if ydif > ytol:
                        numnotok += 1
                    
                    if haserr and (ydif > ytol):
                        ratio = 0.5
                        if ydif > 1.e-8:
                            ratio = (ytol / ydif)**2
                        if ratio > 0.5:
                            ratio = 0.5
                        if terr[ipt] < 0.1 * err[ipt]:
                            ratio = 0

                        numchange += 1
                        #sys.stderr.write("i=%3i yref=%.3f ylo=%.3f yhi=%.3f yopt=%.3f; reducing alpha to %.4f\n"%(\
                            # ipt,self.y[ipt],ylo,yhi,yp[ipt],terr[ipt]*ratio))
                        terr[ipt] *= ratio
                        allok = False
                        
                if allok:
                    fitok = True
                    sys.stderr.write("GPR fit matches all points to within the "+
                                     "desired tolerance\n")
                    break
                else:
                    if numnotok > 0:
                        sys.stderr.write("GPR fit doesn't match %i values\n"%(numnotok))
                    
            if not fitok:
                sys.stderr.write("Not all GPR values fit within the desired tolerance\n")



        
    def GetValues(self,xpts,return_std=False,return_deriv=False):
        """Computes the GPR fit values (and optionally the standard errors and
        function gradients) at arbitrary points

        Parameters
        ----------        
        xpts : list of lists or numpy.ndarray shape=(npts,ndim)
            A list of evaluation points

        return_std : bool, default=False
            If True, then return the standard error at the evaluation points

        return_deriv : bool, default=False
            If True, then return the feature gradients at the evalution points

        Returns
        -------
        ndfes.EvalT
            A container holding the values, errors, and feature derivatives.
            The EvalT.values, EvalT.errors are numpy.array's shape=(npts,).
            EvalT.derivs is a (npts,ndim) array.  The EvalT.errors and 
            EvalT.derivs elements can be None, depending on the values of
            return_std and return_deriv
        """
        
        import numpy as np
        from . EvalT import EvalT
        
        x = np.atleast_2d(xpts)
        xt = self.norm.transform(x)
        sigma = None
        deriv = None
        value = None
        if not return_deriv:
            if not return_std:
                value = self.gpr.predict(xt,return_std=False)
            else:
                value,sigma = self.gpr.predict(xt,return_std=True)
        else:
            value,sigma = self.gpr.predict(xt,return_std=True)
            k2_l = self.gpr.kernel_.get_params()['k2__length_scale']
            deriv = np.zeros( (len(x),len(x[0])) )
            for key, x_star in enumerate(xt):
                # eval_gradient can't be true when eval site doesn't match X
                # this gives standard RBF kernel evaluations
                k_val=self.gpr.kernel_(self.xt, np.atleast_2d(x_star),
                                       eval_gradient=False).ravel()

                # x_i - x_star / l^2
                x_diff_over_l_sq = ((self.xt-x_star)/np.power(k2_l,2)) #.ravel()

                for dim in range(x_diff_over_l_sq.shape[1]):
                    # pair-wise multiply
                    intermediate_result = np.multiply(k_val, x_diff_over_l_sq[:,dim])

                    # dot product intermediate_result with the alphas
                    result = np.dot(intermediate_result, self.gpr.alpha_)

                    # store gradient at this point
                    deriv[key,dim] = result * self.gpr._y_train_std

                    deriv[key,dim] /= self.norm.scale_[dim]
                    
                # No! We don't want to shift the gradients, just scale
                #deriv[key,:] = self.norm.inverse_transform
                
        value -= self.y0
        return EvalT(value,deriv,sigma)


    def ShiftInterpolatedValues(self,e):
        """Sets the y0 attribute, which is subtracted from all interpolated
        values

        Parameters
        ----------
        e : float
            The value to be subtracted from all interpolated values
        """
        
        self.y0 += e
