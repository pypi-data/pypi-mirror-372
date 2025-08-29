import numpy as np
import sep
from scipy import interpolate
import warnings
from photutils.aperture import EllipticalAperture, CircularAperture, EllipticalAnnulus, CircularAnnulus, aperture_photometry 
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import gaussian_filter
import warnings

"""
PetrosianCalculator
===================

Class to calculate the Petrosian radius and fractional light radii
using elliptical or circular apertures based on galaxy morphology.

Attributes
----------
galaxy_image : ndarray
    Input 2D galaxy image.
x, y : float
    Galaxy center coordinates.
a, b : float
    Semi-major and semi-minor axes of the galaxy.
theta : float
    Orientation angle (radians).

Methods
-------
calculate_petrosian_radius :
    Compute the Petrosian radius for a given flux threshold.
calculate_fractional_radius :
    Compute the radius enclosing a specific fraction of the total light.
"""
class PetrosianCalc:
    def __init__(self, image, x, y, a, b, theta, smoothing = 0.5):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.theta = theta
        self.image = gaussian_filter(image.astype(image.dtype.newbyteorder('=')), smoothing)
        
        
    def calculate_petrosian_radius(self, rp_thresh = 0.2, aperture = "elliptical", optimize_rp = True,
                                   interpolate_order = 3, Naround = 3, rp_step = 0.05, method = "sep"):
        """
        Calculate the Petrosian radius and associated parameters.

        Returns:
        --------
        tuple
            Arrays of eta, numerator, denominator, growth curve, radii, and the Petrosian radius.
        """
        
        scale = np.arange(3, len(self.image)/2, rp_step)        
        self.aperture = aperture
        if optimize_rp:
            if method == "sep":
                eta, raio, growth_curve, rp, eta_flag = self._optimize_eta(scale, 
                                                                           rp_thresh = rp_thresh, 
                                                                           method = "sep")
            elif method == "photutils":
                eta, raio, growth_curve, rp, eta_flag = self._optimize_eta(scale, 
                                                                           rp_thresh = rp_thresh, 
                                                                           method = "photutils")
            else:
                raise ValueError(f"Invalid method '{method}'. Choose 'sep' or 'photutils'.")
    
            
        else:
            
            if method == "sep":
                eta, raio, growth_curve, rp, eta_flag = self._standard_eta(scale, 
                                                                           rp_thresh = rp_thresh, 
                                                                           method = "sep")
            elif method == "photutils":
                eta, raio, growth_curve, rp, eta_flag = self._standard_eta(scale, 
                                                                           rp_thresh = rp_thresh, 
                                                                           method = "photutils")                
            else:
                raise ValueError(f"Invalid method '{method}'. Choose 'sep' or 'photutils'.")

        return eta, growth_curve, raio, rp, eta_flag

    def _optimize_eta(self, scale, rp_thresh=0.2, interpolate_order=3, Naround=3, method="sep"):
        eta_all, raio_all, growth_curve_all = [], [], []
        crossing_index = None
        eta_flag = 1
        rp = np.nan
    
        for i, s in enumerate(scale):
            try:
                if method == "sep":
                    num, den, eta_iter, radius, flux3 = self.calculate_eta_sep(s)
                elif method == "photutils":
                    num, den, eta_iter, radius, flux3 = self.calculate_eta_photutils(s)
                else:
                    raise ValueError(f"Invalid method '{method}'. Choose 'sep' or 'photutils'.")
    
                eta_all.append(eta_iter)
                raio_all.append(radius)
                growth_curve_all.append(flux3)
    
                if crossing_index is None and len(eta_all) >= 2:
                    if eta_all[-2] >= rp_thresh > eta_all[-1]:
                        crossing_index = i
    
            except Exception as e:
                print(f"[WARNING] Skipping radius {s:.2f}: {e}")
                continue
    
            if crossing_index is not None and (i - crossing_index >= Naround):
                break
    
        eta = np.array(eta_all)
        raio = np.array(raio_all)
        growth_curve = np.array(growth_curve_all)
    
        if crossing_index is not None:
            imin = max(crossing_index - Naround, 0)
            imax = min(crossing_index + Naround + 1, len(eta))
    
            x = np.array(raio[imin:imax]).flatten()
            y = np.array(eta[imin:imax]).flatten()
            
            
            if x.shape != y.shape:
                raise ValueError(f"x and y must have the same shape: x.shape={x.shape}, y.shape={y.shape}")

            valid = np.isfinite(x) & np.isfinite(y)

            if not np.any(valid):
                raise ValueError("No valid points for interpolation.")

            x, y = x[valid], y[valid]
                        
            x_unique, idx = np.unique(x, return_index=True)
            x, y = x_unique, y[idx]
    
            try:
                if len(x) < (interpolate_order + 1):
                    if len(x) >= 2:
                        interpolate_order = 1
                        print(f"[WARNING] Falling back to linear spline interpolation (k=1)")
                    else:
                        raise ValueError("Too few valid points for interpolation.")
    
                spl = interpolate.splrep(x, y, k=interpolate_order)
                xnew = np.linspace(x.min(), x.max(), 1000)
                ynew = interpolate.splev(xnew, spl)
                rp = xnew[np.argmin(np.abs(ynew - rp_thresh))]
                if not np.isfinite(rp):
                    raise ValueError("Resulting Petrosian radius is NaN or Inf.")
                eta_flag = 0
    
            except Exception as e:
                print(f"[WARNING] Interpolation failed: {e}")
                print("[INFO] Trying fallback linear interpolation...")
    
                try:
                    interp = interpolate.interp1d(y, x, kind="linear", bounds_error=False, fill_value="extrapolate")
                    rp = interp(rp_thresh)
                    eta_flag = 0 if np.isfinite(rp) else 1
                except Exception as e2:
                    print(f"[ERROR] Fallback interpolation also failed: {e2}")
                    rp = np.nan
                    eta_flag = 1
    
        else:
            print("[WARNING] Eta never crossed threshold or too few points for interpolation.")
            if len(eta) > 0 and len(raio) == len(eta):
                diff = np.abs(eta - rp_thresh)
                valid = np.isfinite(diff)
                if np.any(valid):
                    rp = raio[valid][np.nanargmin(diff[valid])]
                else:
                    rp = np.nan
            eta_flag = 1
    
        return eta, raio, growth_curve, rp, eta_flag    
    
    def _standard_eta(self, scale, rp_thresh=0.2, interpolate_order=3, Naround=3, method="sep"):
        eta_all, raio_all, growth_curve_all = [], [], []

        crossing_index = None
        eta_flag = 1
        rp = np.nan

        # Loop through the full scale, store everything
        for i, s in enumerate(scale):
            try:
                if method == "sep":
                    num, den, eta_iter, radius, flux3 = self.calculate_eta_sep(s)
                elif method == "photutils":
                    num, den, eta_iter, radius, flux3 = self.calculate_eta_photutils(s)
                else:
                    raise ValueError(f"Invalid method '{method}'. Choose 'sep' or 'photutils'.")
                
                eta_all.append(eta_iter)
                raio_all.append(radius)
                growth_curve_all.append(flux3)
    
                # Check for threshold crossing
                if crossing_index is None and len(eta_all) >= 2:
                    if eta_all[-2] >= rp_thresh > eta_all[-1]:
                        crossing_index = i
    
            except Exception as e:
                print(f"[WARNING] Skipping radius {s:.2f}: {e}")
                continue
    
        eta = np.array(eta_all)
        raio = np.array(raio_all)
        growth_curve = np.array(growth_curve_all)
    
        # --- If a crossing was detected
        if crossing_index is not None:
            imin = max(crossing_index - Naround, 0)
            imax = min(crossing_index + Naround + 1, len(eta))
            
            
            x = np.array(raio[imin:imax]).flatten()
            y = np.array(eta[imin:imax]).flatten()
            
            
            if x.shape != y.shape:
                raise ValueError(f"x and y must have the same shape: x.shape={x.shape}, y.shape={y.shape}")

            valid = np.isfinite(x) & np.isfinite(y)

            if not np.any(valid):
                raise ValueError("No valid points for interpolation.")

            x, y = x[valid], y[valid]
                           
            # Remove duplicates in x
            x_unique, idx = np.unique(x, return_index=True)
            x, y = x_unique, y[idx]
    
            # Interpolation
            try:
                if len(x) < (interpolate_order + 1):
                    if len(x) >= 2:
                        interpolate_order = 1
                        print(f"[WARNING] Falling back to linear spline interpolation (k=1)")
                    else:
                        raise ValueError("Too few valid points for interpolation.")
    
                spl = interpolate.splrep(x, y, k=interpolate_order)
                xnew = np.linspace(x.min(), x.max(), 1000)
                ynew = interpolate.splev(xnew, spl)
                rp = xnew[np.argmin(np.abs(ynew - rp_thresh))]

                if not np.isfinite(rp):
                    raise ValueError("Resulting Petrosian radius is NaN or Inf.")
    
                eta_flag = 0
    
            except Exception as e:
                print(f"[WARNING] Interpolation failed: {e}")
                print("[INFO] Trying fallback linear interpolation...")
    
                try:
                    interp = interpolate.interp1d(y, x, kind="linear", bounds_error=False, fill_value="extrapolate")
                    rp = interp(rp_thresh)
                    eta_flag = 0 if np.isfinite(rp) else 1
                except Exception as e2:
                    print(f"[ERROR] Fallback linear interpolation also failed: {e2}")
                    rp = np.nan
                    eta_flag = 1
    
        else:
            # No crossing detected, fallback to closest value
            print("[WARNING] No eta crossing found. Using closest point as fallback.")
            if len(eta) > 0 and len(raio) == len(eta):
                diff = np.abs(eta - rp_thresh)
                valid = np.isfinite(diff)
                if np.any(valid):
                    rp = raio[valid][np.nanargmin(diff[valid])]
                else:
                    rp = np.nan
            eta_flag = 1
    
        return eta, raio, growth_curve, rp, eta_flag
    
    
    def calculate_eta_sep(self, s):
        a_sma = s
        b_sma = (s*self.b/self.a if self.b/self.a != 1 else s-0.0001) 
        
        a_in = a_sma * 0.8
        a_out = a_sma * 1.25
        
        b_in = a_in * (self.b / self.a) 
        b_out = a_out * (self.b / self.a)  
        theta = self.theta  # in radians
        
        if self.aperture == "circular":
            flux_outer, _, _ = sep.sum_circle(self.image, [self.x], [self.y], [a_out], subpix=100)
            flux_inner, _, _ = sep.sum_circle(self.image, [self.x], [self.y], [a_in], subpix=100)
            flux_aperture, _, _ = sep.sum_circle(self.image, [self.x], [self.y], [a_sma], subpix=100)
            
            area_annulus = np.pi * (a_out**2 - a_in**2)
            area_aperture = np.pi * (a_sma**2)
            
            flux_annulus = flux_outer - flux_inner
            
            mean_annulus = flux_annulus/area_annulus
            mean_total = flux_aperture/area_aperture
            

        elif self.aperture == "elliptical":
            # Elliptical annulus: estimate mean flux in [a_in, a_out] annulus
            flux_outer, _, _ = sep.sum_ellipse(self.image, [self.x], [self.y], [a_out], [b_out], [self.theta], subpix=100)
            flux_inner, _, _ = sep.sum_ellipse(self.image, [self.x], [self.y], [a_in], [b_out * (a_in / a_out)], [self.theta], subpix=100)
            flux_aperture, _, _ = sep.sum_ellipse(self.image, [self.x], [self.y], [a_sma], [b_sma], [self.theta], subpix=100)
        
            flux_annulus = flux_outer - flux_inner

            # Area of elliptical annulus
            area_annulus = np.pi * (a_out * b_out - a_in * b_out * (a_in / a_out))
        
            # Total elliptical aperture
            area_aperture = np.pi * a_sma * b_sma

            # Mean intensities
            mean_annulus = flux_annulus / area_annulus
            mean_total = flux_aperture / area_aperture
        
        else:
            raise ValueError(f"Invalid method '{aperture}'. Choose 'circular' or 'elliptical'.")                
                
        if mean_total == 0 or not np.isfinite(mean_total):
            eta = np.nan
        else:
            eta = mean_annulus / mean_total
        
        return mean_annulus, mean_total, eta, s, flux_aperture
                    
    def calculate_eta_photutils(self, s):
        center = (self.x, self.y)
        a_sma = s
        theta = self.theta  # in radians

        if self.aperture == "circular":
            r_in = a_sma * 0.8
            r_out = a_sma * 1.25

            # Define circular apertures
            aperture = CircularAperture(center, r=a_sma)
            annulus = CircularAnnulus(center, r_in=r_in, r_out=r_out)

            # Compute fluxes
            flux_ap = aperture.do_photometry(self.image, method='exact')[0][0]
            flux_ann = annulus.do_photometry(self.image, method='exact')[0][0]

            # Areas
            area_aperture = aperture.area
            area_annulus = annulus.area

        elif self.aperture == "elliptical":
            b_sma = a_sma * self.b / self.a
            a_in = a_sma * 0.8
            a_out = a_sma * 1.25
            b_in = a_in * (self.b / self.a)
            b_out = a_out * (self.b / self.a)

            # Define elliptical apertures
            aperture = EllipticalAperture(center, a_sma, b_sma, theta=theta)
            annulus = EllipticalAnnulus(center, a_in, a_out, b_out, theta=theta)

            # Compute fluxes
            flux_ap = aperture.do_photometry(self.image, method='exact')[0][0]
            flux_ann = annulus.do_photometry(self.image, method='exact')[0][0]

            # Areas
            area_aperture = aperture.area
            area_annulus = annulus.area

        else:
            raise ValueError(f"Invalid aperture '{self.aperture}'. Choose 'circular' or 'elliptical'.")

        # Mean intensities
        mean_total = flux_ap / area_aperture
        mean_annulus = flux_ann / area_annulus

        # Petrosian eta
        if mean_total == 0 or not np.isfinite(mean_total):
            eta = np.nan
        else:
            eta = mean_annulus / mean_total

        return mean_annulus, mean_total, eta, s, flux_ap                
    
                
    def calculate_fractional_radius(self, f=0.5, rmax=50, step=0.5, aperture="elliptical", method="sep"):
        """
        Calculate the radius enclosing fraction `f` of the total flux.

        Returns
        -------
        r_f : float
            Radius where enclosed flux equals `f` * total flux.
        radii : ndarray
            Sampled radii.
        growth_curve : ndarray
            Total flux within each radius.
        """
        radii = np.arange(step, rmax + step, step)
        fluxes = []

        for r in radii:
            a = r
            b = r * self.b / self.a

            if method == "sep":
                if aperture == "elliptical":
                    b = b if self.b/self.a != 1 else r - 0.001
                    flux, _, _ = sep.sum_ellipse(self.image, [self.x], [self.y], [a], [b], [self.theta], subpix=100)
                elif aperture == "circular":
                    flux, _, _ = sep.sum_circle(self.image, [self.x], [self.y], [a], subpix=100)
                else:
                    raise ValueError(f"Invalid method '{aperture}'. Choose 'circular' or 'elliptical'.")
                fluxes.append(flux[0])

            elif method == "photutils":
                if aperture == "elliptical":
                    ap = EllipticalAperture((self.x, self.y), a, b, theta=self.theta)
                elif aperture == "circular":
                    ap = CircularAperture((self.x, self.y), a)
                else:
                    raise ValueError(f"Invalid method '{aperture}'. Choose 'circular' or 'elliptical'.")
                flux = ap.do_photometry(self.image, method="exact")[0][0]
                fluxes.append(flux)
            else:
                raise ValueError(f"Invalid method '{method}'. Choose 'sep' or 'photutils'.")

        growth_curve = np.array(fluxes)  # already total enclosed flux
        total_flux = growth_curve[-1]
    
        if total_flux <= 0:
            print("[WARNING] Total flux is non-positive.")
            return np.nan, radii, growth_curve

        target_flux = f * total_flux
        if np.all(growth_curve < target_flux):
            print("[WARNING] Desired flux fraction not reached within rmax.")
            return np.nan, radii, growth_curve

        try:
            # Clean up data for interpolation
            x = np.array(growth_curve)
            y = np.array(radii)
            valid = np.isfinite(x) & np.isfinite(y)
            x, y = x[valid], y[valid]

            # Remove duplicate x-values
            x_unique, idx = np.unique(x, return_index=True)
            x, y = x_unique, y[idx]

            # Optional: remove non-monotonic segments
            if len(x) > 1:
                monotonic = np.diff(x) > 0
                x = x[np.insert(monotonic, 0, True)]
                y = y[np.insert(monotonic, 0, True)]

            # Check point count for spline
            if len(x) < 4:
                print(f"[WARNING] Falling back to linear interpolation (too few points for spline)")
                raise ValueError("Too few points for cubic spline.")

            # Try cubic spline interpolation
            spl = interpolate.splrep(x, y, k=3)
            r_f = interpolate.splev(target_flux, spl)

            if not np.isfinite(r_f):
                raise ValueError("Interpolated result is not finite.")

        except Exception as e:
            print(f"[WARNING] Interpolation failed: {e}")
            print("[INFO] Trying fallback linear interpolation...")

            try:
                interp = interpolate.interp1d(x, y, kind="linear", bounds_error=False, fill_value="extrapolate")
                r_f = interp(target_flux)
                if not np.isfinite(r_f):
                    raise ValueError("Fallback result is not finite.")
            except Exception as e2:
                print(f"[ERROR] Fallback interpolation also failed: {e2}")
                r_f = np.nan        
        return r_f, radii, growth_curve                
    
    def calculate_kron_radius(self, rmax=None):
        """
        Manually compute the Kron radius within an elliptical aperture.

        Parameters
        ----------
        rmax : float, optional
            Maximum elliptical radius to consider (default: 8a).

        Returns
        -------
        r_kron : float
            Kron radius
        """
        if rmax is None:
            rmax = 8 * self.a
        ny, nx = self.image.shape
        Y, X = np.mgrid[0:ny, 0:nx]
        dx, dy = X - self.x, Y - self.y
        cos_t, sin_t = np.cos(self.theta), np.sin(self.theta)
        x_p = dx * cos_t + dy * sin_t
        y_p = -dx * sin_t + dy * cos_t
        r_ellip = np.sqrt((x_p / self.a)**2 + (y_p / self.b)**2)
        mask = r_ellip <= (rmax / self.a)
        I = self.image[mask]
        r = r_ellip[mask] * self.a  # Convert elliptical radius to pixel units
        return np.sum(r * I) / np.sum(I) if np.sum(I) > 0 else np.nan

