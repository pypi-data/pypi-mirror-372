"""
MagCUSPS
-----------------------

.. currentmodule:: mag_cusps
    
    preprocess
    get_bowshock_radius
    get_bowshock
    get_interest_points
    process_interest_points
    process_points
    Shue97
    Liu12
    Rolland25
    fit_to_analytical
"""

# __init__.pyi for topology_analysis

from typing import overload
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


def preprocess(
    mat: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    new_shape: np.ndarray,
) -> np.ndarray:
    """
    Transform a matrix from a non uniform grid to a uniform grid, of shape `new_shape`,
    using X, Y and Z containing the actual position of the center of each grid of each matrix indices. 

    Parameters
    ----------
    mat : np.ndarray
        Input matrix array of doubles, shape (x, y, z, i).
    X, Y, Z : np.ndarray
        Input matrices used in orthonormalisation.
    new_shape : np.ndarray
        Integer array of shape (4,) specifying new shape dimensions.

    Returns
    -------
    np.ndarray
        Orthonormalised matrix as a NumPy array with shape matching `new_shape`.
    """



def get_bowshock_radius(
    theta: float,
    phi: float,
    Rho: np.ndarray,
    earth_pos: np.ndarray,
    dr: float
) -> float:
    """
    Calculate bowshock radius given angles and input data.

    Parameters
    ----------
    theta : float
        Polar angle in radians.
    phi : float
        Azimuthal angle in radians.
    Rho : np.ndarray
        Density matrix array.
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    dr : float
        Step size for radius calculation.

    Returns
    -------
    float
        Computed bowshock radius.
    """

def get_bowshock(
    Rho: np.ndarray,
    earth_pos: np.ndarray,
    dr: float,
    nb_phi: int,
    max_nb_theta: int
) -> np.ndarray:
    """
    Find the bow shock by finding the radius at which dRho_dr * r**3 is minimum,
    casting rays from the earth_pos at angles (theta, phi)

    Parameters
    ----------
    Rho : np.ndarray
        Density matrix array of shape (x,y,z,).
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    dr : float
        Step size for radius calculation.
    nb_phi : int
        Number of divisions in phi.
    max_nb_theta : int
        Maximum number of divisions in theta.

    Returns
    -------
    np.ndarray
        Array of points with shape (N, 3) representing bowshock coordinates.
    """


def get_interest_points(
    J_norm: np.ndarray,
    earth_pos: np.ndarray,
    Rho: np.ndarray,
    theta_min: float,
    theta_max: float,
    nb_theta: int,
    nb_phi: int,
    dx: float,
    dr: float,
    alpha_0_min: float,
    alpha_0_max: float,
    nb_alpha_0: int,
    r_0_mult_min: float,
    r_0_mult_max: float,
    nb_r_0: int,
    avg_std_dev: float | None = None
) -> np.ndarray:
    """
    Calculate interest points from inputs.

    Parameters
    ----------
    J_norm : np.ndarray
        Normalized current density matrix of shape (x,y,z,i,).
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    Rho : np.ndarray
        Density matrix array of shape (x,y,z,).
    theta_min, theta_max : float
        Angle bounds for theta.
    nb_theta, nb_phi : int
        Number of divisions for theta and phi.
    dx, dr : float
        Step sizes.
    alpha_0_min, alpha_0_max : float
        Bounds for alpha_0.
    nb_alpha_0 : int
        Number of alpha_0 divisions.
    r_0_mult_min, r_0_mult_max : float
        Multiplicative range for r_0 where r_0 = r_0_mult * r_I with r_I the inner radius in the simulation.
    nb_r_0 : int
        Number of r_0 divisions.
    avg_std_dev : Optional[float]
        Optional output parameter for average standard deviation.

    Returns
    -------
    np.ndarray
        Interest points array with shape (nb_theta*nb_phi, 4).
    """

def process_interest_points(
    interest_points: np.ndarray,
    nb_theta: int,
    nb_phi: int,
    shape_sim: np.ndarray,
    shape_real: np.ndarray,
    earth_pos_sim: np.ndarray,
    earth_pos_real: np.ndarray,
) -> np.ndarray:
    """
    Transform interest points from simulation coordinates to real coordinates.

    Parameters
    ----------
    interest_points : np.ndarray
        Interest points array with shape (N, 4).
    nb_theta, nb_phi : int
        Number of divisions in theta and phi.
    shape_sim, shape_real : np.ndarray
        Shape arrays of shape (4,) describing simulation and real data shapes.
    earth_pos_sim, earth_pos_real : np.ndarray
        Earth position vectors of shape (3,) for simulation and real.

    Returns
    -------
    np.ndarray
        Processed interest points array of shape (N, 4).
    """

def process_points(
    points: np.ndarray,
    shape_sim: np.ndarray,
    shape_real: np.ndarray,
    earth_pos_sim: np.ndarray,
    earth_pos_real: np.ndarray,
) -> np.ndarray:
    """
    Transform points from simulation coordinates to real coordinates.

    Parameters
    ----------
    points : np.ndarray
        Points array with shape (N, 3).
    shape_sim, shape_real : np.ndarray
        Shape arrays of shape (4,) describing simulation and real data shapes.
    earth_pos_sim, earth_pos_real : np.ndarray
        Earth position vectors of shape (3,) for simulation and real.

    Returns
    -------
    np.ndarray
        Processed points array of shape (N, 3).
    """


@overload
def Shue97(
    params: np.ndarray,
    theta: float
) -> float:
    """
    Analytical approximation of the Magnetopause topology as written by Shue in his 1997 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (2,).
    theta : float
        Angle at which the radius should be calculated. 
    
    Returns
    -------
    float
        Radius at this angle.
    """
  
@overload
def Shue97(
    params: np.ndarray,
    theta: np.ndarray
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Shue in his 1997 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (2,).
    theta : np.ndarray
        Angles at which the radii should be calculated. 
    
    Returns
    -------
    np.ndarray
        Radii at these angles.
    """


@overload
def Liu12(
    params: np.ndarray,
    theta: float, phi: float
) -> float:
    """
    Analytical approximation of the Magnetopause topology as written by Liu in his 2012 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (10,).
    theta, phi : float
        Angle at which the radius should be calculated. 
    
    Returns
    -------
    float
        Radius at this angle.
    """

@overload
def Liu12(
    params: np.ndarray,
    theta: np.ndarray, phi: np.ndarray
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Liu in his 2012 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (10,).
    theta, phi : np.ndarray
        Angles at which the radii should be calculated. 
    
    Returns
    -------
    float
        Radii at these angles.
    """

@overload
def Liu12(
    params: np.ndarray,
    theta: np.ndarray, phi: float
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Liu in his 2012 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (10,).
    theta : np.ndarray
        Angles at which the radii should be calculated. 
    phi : float
        Angle at which the radii should be calculated. 
    
    Returns
    -------
    float
        Radii at these angles.
    """
    
@overload
def Liu12(
    params: np.ndarray,
    theta: float, phi: np.ndarray
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Liu in his 2012 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (10,).
    theta : float
        Angle at which the radii should be calculated. 
    phi : np.ndarray
        Angles at which the radii should be calculated. 
    
    Returns
    -------
    float
        Radii at these angles.
    """
  
    
@overload
def Rolland25(
    params: np.ndarray,
    theta: float, phi: float
) -> float:
    """
    Analytical approximation of the Magnetopause topology as written by Rolland in his 2025 thesis.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (11,).
    theta, phi : float
        Angle at which the radius should be calculated. 
    
    Returns
    -------
    float
        Radius at this angle.
    """
    
@overload
def Rolland25(
    params: np.ndarray,
    theta: np.ndarray, phi: np.ndarray
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Rolland in his 2025 thesis.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (11,).
    theta, phi : np.ndarray
        Angles at which the radii should be calculated. 
    
    Returns
    -------
    np.ndarray
        Radii at these angles.
    """
 
@overload
def Rolland25(
    params: np.ndarray,
    theta: np.ndarray, phi: float
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Rolland in his 2025 thesis.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (11,).
    theta : np.ndarray
        Angles at which the radii should be calculated. 
    phi : float
        Angle at which the radii should be calculated. 
    
    Returns
    -------
    np.ndarray
        Radii at these angles.
    """

@overload
def Rolland25(
    params: np.ndarray,
    theta: float, phi: np.ndarray
) -> np.ndarray:
    """
    Analytical approximation of the Magnetopause topology as written by Rolland in his 2025 thesis.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (11,).
    theta : float
        Angle at which the radii should be calculated. 
    phi : np.ndarray
        Angles at which the radii should be calculated. 
    
    Returns
    -------
    np.ndarray
        Radii at these angles.
    """


def fit_to_analytical(
    interest_points: np.ndarray,
    initial_params: np.ndarray,
    lowerbound: np.ndarray,
    upperbound: np.ndarray,
    radii_of_variation: np.ndarray,
    analytical_function: str = "Rolland25",
    nb_runs: int = 10,
    max_nb_iterations_per_run: int = 50,
) -> tuple[np.ndarray, float] | None:
    """
    Analytical fitting of the Shue97, Liu12 or Rolland25 analytical functions 
    to an array of interest points. N equals respectively 2, 10 and 11.

    Parameters
    ----------
    interest_points : np.ndarray
        Interest point array to fit to of shape (`nb_interest_points`, 4).
    initial_parameters : np.ndarray
        Parameters array with shape (N,).
    lowerbound, upperbound : np.ndarray
        Parameters array with shape (N,) corresponding to the lower and upper bounds
        that the parameters can take during fitting.
    radii_of_variation : np.ndarray
        Parameters array with shape (N,) corresponding to the maximum distance each 
        of the parameters will randomly move away for the initial_params at the 
        beginning of a run.
    analytical_function : str
        Analytical function used.
    nb_runs : int
        Number of times the fitting algorithm will start again with other randomly 
        selected initial parameters.
    max_nb_iterations_per_run : int
        Maximum number of iterations the fitting algorithm will do before stopping
        even if it hasn't converged.
    
    Returns
    -------
    (np.ndarray, float)
        Array of the final parameters after fit and the fitting cost of these parameters. 
    """


def get_grad_J_fit_over_ip(
    params: np.ndarray,
    interest_points: np.ndarray,
    J_norm: np.ndarray, earth_pos: np.ndarray,
    analytical_function: str = "Rolland25",
    dx: float = 0.5, dy: float = 0.5, dz: float = 0.5
) -> float | None:
    """
    Ratio of the current density gradient along the magnetopause between the 
    Shue97, Liu12 or Rolland25 analytical functions and the interest points. 
    N equals respectively 2, 10 and 11.
    
    Parameters
    ----------
    params : np.ndarray
        Parameters for the analytical function of shape (N,).
    interest_points : np.ndarray
        Interest point array of shape (`nb_interest_points`, 4).
    J_norm : np.ndarray
        Normalised current density matrix of shape (X, Y, Z).
    earth_pos : np.ndarray
        Position of the Earth of shape (3,).
    analytical_function : str
        Analytical function corresponding to the parameters.
    dx, dy, dz : Optional[int]
        Used to calculate the gradient. Default value is 0.5.
    
    Returns
    -------
    float
        ||grad(||J_fit||)|| / ||grad(||J_ip||)||.
    """
    

def interest_point_flatness_checker(
    interest_points: np.ndarray,
    nb_theta: int, nb_phi: int,
    threshold: float, phi_radius: float
) -> tuple[float, bool]:
    """
    Checks in the (earth_pos,x,z) plane at what angle the interest points recede towards +x
    past a given threshold. Will also say if the interest points are concave, as an extreme case
    
    Parameters
    ----------
    interest_points : np.ndarray
        Interest point array of shape (`nb_interest_points`, 4).
    nb_theta, nb_phi : int
        Number of phi and theta.
    threshold : Optional[float]
        How many grid cells before the dayside is considered to have receded.
        Default value is 2.0.
    phi_radius : Optional[float]
        The angle phi to consider both sides of the (earth_pos,x,z) plane to average.
        out any possible outliers in the plane. Default value is 0.3.
    
    Returns
    -------
    (float, bool)
        Returns the angle at which the day-side stops being considered flat, and whether it was concave.
    """


def get_delta_r0(
    r0: float,
    interest_points: np.ndarray,
    nb_theta: int, nb_phi: int,
    theta_used: float = 0.2
) -> float:
    """
    Return r_0 from the parameters minus the average distance between the Earth 
    and the dayside weighed interest points.
    
    Parameters
    ----------
    r0 : float
        The standoff distance obtained from the fitting.
    interest_points : np.ndarray
        Interest point array of shape (`nb_interest_points`, 4).
    nb_theta, nb_phi : int
        Number of phi and theta used for the interest points search.
    theta_used : Optional[float]
        The theta used to average the distance between the Earth and the dayside interest points 

    Returns
    -------
    np.ndarray
        r0 - sum( interest_points.radius * interest_points.weights ) / sum(interest_points.weights)
    """


class MagCUSPS_Model:
    """
    Interface to use an ML model to predict the quality of the analysed numerical simulation
    from a set of inputs. 
    """
    def define(self, model, scaler):
        """"""
    def load(self, path: str):
        """
        Load a pickled MagCUSPS_model object 
        """
    def dump(self, path: str):
        """
        Pickle an entire MagCUSPS_model object
        """
    def predict(self, X):
        """
        Scale the data with the self.scaler and predict the output with self.model
        """
    
class MagCUSPS_RandomForestModel(MagCUSPS_Model):
    """
    Implementation of the interface using a RandomForestRegressor and StandardScaler to use the provided
    pretrained models fit on the Gorgon benchmark data.
    """
    def define(self, model: RandomForestRegressor, scaler: StandardScaler):
        """"""
    def get_sample_uncertainty(self, X_sample):
        """
        Get uncertainty from Random Forest model
        """
    def get_batch_uncertainty(self, X):
        """
        Get uncertainty of entire batch from Random Forest model
        """
    
    
def load_pretrained_model(
    analytical_function: str = "Rolland25"
) -> MagCUSPS_RandomForestModel:
    """
    Load one of the pretrained models to predict the quality of the analysed numerical data
    for the analytical function used for fitting.
    """
    
def analyse(
    J_norm: np.ndarray, earth_pos: np.ndarray,
    nb_theta: int, nb_phi: int,
    interest_points: np.ndarray, 
    params: np.ndarray, fit_loss: float,
    analytical_function: str = "Rolland25",
    threshold: float = 2.0, phi_radius: float = 0.3,
    dx: float = 0.5, dy: float = 0.5, dz: float = 0.5,
    theta_used: float = 0.2
) -> np.ndarray | None:
    """
    Provide the exact parameters needed to use the MagCUSPS_Model to predict the quality
    of the analysed numerical data.
    
    Parameters
    ----------
    J_norm : np.ndarray
        Normalised current density matrix of shape (X, Y, Z).
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    nb_theta, nb_phi : int
        Number of phi and theta used for the interest points search.
    interest_points : np.ndarray
        Interest point array of shape (`nb_interest_points`, 4).
    params : np.ndarray
        Parameters for the analytical function of shape (N,).
    analytical_function : str
        Analytical function corresponding to the parameters.
    threshold : Optional[float]
        How many grid cells before the dayside is considered to have receded.
        Default value is 2.0.
    phi_radius : Optional[float]
        The angle phi to consider both sides of the (earth_pos,x,z) plane to average.
        out any possible outliers in the plane. Default value is 0.3.
    dx, dy, dz : Optional[int]
        Used to calculate the gradient. Default value is 0.5.
    theta_used : Optional[float]
        The theta used to average the distance between the Earth and the dayside interest points 

    Returns
    -------
    np.ndarray
        Array containing in order `[params..., fit_loss, grad_J_fit_over_ip, delta_r0, max_theta_in_threshold, is_concave]`.
    """


__all__ = [
    "preprocess",
    "get_bowshock_radius",
    "get_bowshock",
    "get_interest_points",
    "process_interest_points",
    "process_points",
    "Shue97",
    "Liu12",
    "Rolland25",
    "fit_to_analytical",
    "get_grad_J_fit_over_ip",
    "interest_point_flatness_checker",
    "get_delta_r0",
    "MagCUSPS_Model",
    "MagCUSPS_RandomForestModel",
    "load_pretrained_model",
    "analyse"
]
