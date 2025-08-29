from __future__ import annotations
import numpy
import ostk.astrodynamics
import ostk.astrodynamics.flight.system
import ostk.astrodynamics.trajectory.state
import ostk.core.type
import ostk.mathematics.curve_fitting
import ostk.physics.coordinate
import ostk.physics.environment.object
import ostk.physics.time
__all__ = ['AtmosphericDrag', 'CentralBodyGravity', 'PositionDerivative', 'Tabulated', 'ThirdBodyGravity', 'Thruster']
class AtmosphericDrag(ostk.astrodynamics.Dynamics):
    """
    
                    The atmospheric drag dynamics.
    
                
    """
    def __init__(self, celestial: ostk.physics.environment.object.Celestial) -> None:
        """
                            Constructor.
        
                            Args:
                                celestial (Celestial): The celestial body.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_contribution(self, instant: ostk.physics.time.Instant, x: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                            Compute the contribution of the atmospheric drag to the state vector.
        
                            Args:
                                instant (Instant): The instant of the state vector.
                                x (numpy.ndarray): The state vector.
                                frame (Frame): The reference frame.
        
                            Returns:
                                numpy.ndarray: The contribution of the atmospheric drag to the state vector.
        """
    def get_celestial(self) -> ostk.physics.environment.object.Celestial:
        """
                            Get the celestial body.
        
                            Returns:
                                Celestial: The celestial body.
        """
    def is_defined(self) -> bool:
        """
                            Check if the atmospheric drag is defined.
        
                            Returns:
                                bool: True if the atmospheric drag is defined, False otherwise.
        """
class CentralBodyGravity(ostk.astrodynamics.Dynamics):
    """
    
                    The central-body gravity model.
    
                
    """
    def __init__(self, celestial: ostk.physics.environment.object.Celestial) -> None:
        """
                            Constructor.
        
                            Args:
                                celestial (Celestial): The central body.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_contribution(self, instant: ostk.physics.time.Instant, x: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                            Compute the contribution of the central-body gravity to the state vector.
        
                            Args:
                                instant (Instant): The instant of the state vector.
                                x (numpy.ndarray): The state vector.
                                frame (Frame): The reference frame.
        
                            Returns:
                                numpy.ndarray: The contribution of the central-body gravity to the state vector.
        """
    def get_celestial(self) -> ostk.physics.environment.object.Celestial:
        """
                            Get the central body.
        
                            Returns:
                                Celestial: The central body.
        """
    def is_defined(self) -> bool:
        """
                            Check if the central-body gravity is defined.
        
                            Returns:
                                bool: True if the central-body gravity is defined, False otherwise.
        """
class PositionDerivative(ostk.astrodynamics.Dynamics):
    """
    
                    The position derivative model.
    
                
    """
    def __init__(self) -> None:
        """
                            Constructor.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_contribution(self, instant: ostk.physics.time.Instant, x: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                            Compute the contribution of the position derivative to the state vector.
        
                            Args:
                                instant (Instant): The instant of the state vector.
                                x (numpy.ndarray): The state vector.
                                frame (Frame): The reference frame.
        
                            Returns:
                                numpy.ndarray: The contribution of the position derivative to the state vector.
        """
    def is_defined(self) -> bool:
        """
                            Check if the position derivative is defined.
        
                            Returns:
                                bool: True if the position derivative is defined, False otherwise.
        """
class Tabulated(ostk.astrodynamics.Dynamics):
    """
    
                    The tabulated dynamics.
    
                
    """
    def __init__(self, instants: list[ostk.physics.time.Instant], contribution_profile: numpy.ndarray[numpy.float64[m, n]], coordinate_subsets: list[ostk.astrodynamics.trajectory.state.CoordinateSubset], frame: ostk.physics.coordinate.Frame, interpolation_type: ostk.mathematics.curve_fitting.Interpolator.Type = ...) -> None:
        """
                            Constructor.
        
                            Args:
                                instants (list[Instant]): An array of instants.
                                contribution_profile (numpy.ndarray): A contribution profile.
                                coordinate_subsets (list[CoordinateSubset]): An array of coordinate subsets related to the contribution profile.
                                frame (Frame): A frame.
                                interpolation_type (Interpolator.Type, optional): The interpolation type. Defaults to Barycentric Rational.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_contribution_profile(self) -> numpy.ndarray[numpy.float64[m, n]]:
        """
                            Access the contribution profile.
        
                            Returns:
                                np.ndarray: The contribution profile.
        """
    def access_frame(self) -> ostk.physics.coordinate.Frame:
        """
                            Access the reference frame.
        
                            Returns:
                                Frame: The reference frame.
        """
    def access_instants(self) -> list[ostk.physics.time.Instant]:
        """
                            Access the contribution instants.
        
                            Returns:
                                list[Instant]: The contribution instants.
        """
    def compute_contribution(self, instant: ostk.physics.time.Instant, x: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                            Compute the contribution from the contribution profile to the state vector.
        
                            Args:
                                instant (Instant): The instant of the state vector.
                                x (numpy.ndarray): The state vector.
                                frame (Frame): The reference frame.
        
                            Returns:
                                numpy.ndarray: The contribution from the contribution profile to the state vector.
        """
    def get_contribution_profile_from_coordinate_subsets(self, coordinate_subsets: list[ostk.astrodynamics.trajectory.state.CoordinateSubset]) -> numpy.ndarray[numpy.float64[m, n]]:
        """
                            Get the contribution profile corresponding to a subset of coordinates.
        
                            Args:
                                coordinate_subsets (list[CoordinateSubset]): The coordinate subsets.
        
                            Returns:
                                numpy.ndarray: The contribution profile.
        """
    def get_interpolation_type(self) -> ostk.mathematics.curve_fitting.Interpolator.Type:
        """
                            Get the interpolation type used for each row of the contribution profile (they are all the same).
        
                            Returns:
                                Interpolator.Type: The interpolation type.
        """
    def is_defined(self) -> bool:
        """
                            Check if the tabulated dynamics is defined.
        
                            Returns:
                                bool: True if the tabulated dynamics is defined, False otherwise.
        """
class ThirdBodyGravity(ostk.astrodynamics.Dynamics):
    """
    
                    The third body gravity model.
    
                
    """
    def __init__(self, celestial: ostk.physics.environment.object.Celestial) -> None:
        """
                            Constructor.
        
                            Args:
                                celestial (Celestial): The celestial body.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_contribution(self, instant: ostk.physics.time.Instant, x: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                            Compute the contribution of the third-body gravity to the state vector.
        
                            Args:
                                instant (Instant): The instant of the state vector.
                                x (numpy.ndarray): The state vector.
                                frame (Frame): The reference frame.
        
                            Returns:
                                numpy.ndarray: The contribution of the third-body gravity to the state vector.
        """
    def get_celestial(self) -> ostk.physics.environment.object.Celestial:
        """
                            Get the celestial body.
        
                            Returns:
                                Celestial: The celestial body.
        """
    def is_defined(self) -> bool:
        """
                            Check if the third-body gravity is defined.
        
                            Returns:
                                bool: True if the third-body gravity is defined, False otherwise.
        """
class Thruster(ostk.astrodynamics.Dynamics):
    """
    
                Abstract Thruster Class.
    
                Base class to derive other thruster classes from. Cannot be instantiated.
    
            
    """
    def __init__(self, satellite_system: ostk.astrodynamics.flight.system.SatelliteSystem, guidance_law: typing.Any, name: ostk.core.type.String = ...) -> None:
        """
                        Constructor.
        
                        Args:
                            satellite_system (SatelliteSystem): The satellite system.
                            guidance_law (GuidanceLaw): The guidance law used to compute the acceleration vector.
                            name (str): The name of the thruster.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_contribution(self, instant: ostk.physics.time.Instant, state_vector: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Compute the contribution of the thruster to the state vector.
        
                        Args:
                            instant (Instant): The instant of the state vector.
                            state_vector (numpy.ndarray): The state vector.
                            frame (Frame): The reference frame.
        
                        Returns:
                            numpy.ndarray: The contribution of the thruster to the state vector.
        """
    def get_guidance_law(self) -> ...:
        """
                        Get the guidance law of the thruster.
        
                        Returns:
                            GuidanceLaw: The guidance law.
        """
    def get_satellite_system(self) -> ostk.astrodynamics.flight.system.SatelliteSystem:
        """
                        Get the satellite system of the thruster.
        
                        Returns:
                            SatelliteSystem: The satellite system.
        """
    def is_defined(self) -> bool:
        """
                        Check if the thruster is defined.
        
                        Returns:
                            bool: True if the thruster is defined, False otherwise.
        """
