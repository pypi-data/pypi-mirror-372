from __future__ import annotations
import ostk.astrodynamics
import ostk.astrodynamics.flight.profile
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.mathematics.curve_fitting
import ostk.mathematics.geometry.d3.transformation.rotation
import ostk.physics.coordinate
import ostk.physics.coordinate.frame.provider
import ostk.physics.time
import typing
__all__ = ['Tabulated', 'Transform']
class Tabulated(ostk.astrodynamics.flight.profile.Model):
    """
    
                A flight profile model defined by a set of states.
    
            
    """
    @typing.overload
    def __init__(self, states: list[ostk.astrodynamics.trajectory.State]) -> None:
        """
                        Constructor.
        
                        Args:
                            states (Array[State]): The states of the model.
        """
    @typing.overload
    def __init__(self, states: list[ostk.astrodynamics.trajectory.State], interpolator_type: ostk.mathematics.curve_fitting.Interpolator.Type) -> None:
        """
                        Constructor.
        
                        Args:
                            states (Array[State]): The states of the model.
                            interpolator_type (Interpolator.Type): The type of interpolator to use for all but the AttitudeQuaternion subset. Attitude quaternions will be interpolated using spherical linear interpolation (SLERP).
        """
    def __repr__(self) -> str:
        """
                        Convert the model to a string.
        
                        Returns:
                            str: The string representation of the model.
        """
    def __str__(self) -> str:
        """
                        Convert the model to a string.
        
                        Returns:
                            str: The string representation of the model.
        """
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Calculate the state of the model at a specific instant.
        
                        Args:
                            instant (Instant): The instant at which to calculate the state.
        
                        Returns:
                            State: The state of the model at the specified instant.
        """
    def get_axes_at(self, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Axes:
        """
                        Get the axes of the model at a specific instant.
        
                        Args:
                            instant (Instant): The instant at which to get the axes.
        
                        Returns:
                            numpy.ndarray: The axes of the model at the specified instant.
        """
    def get_body_frame(self, frame_name: ostk.core.type.String) -> ostk.physics.coordinate.Frame:
        """
                        Get the body frame of the model with the specified name.
        
                        Args:
                            frame_name (str): The name of the body frame.
        
                        Returns:
                            Frame: The body frame of the model with the specified name.
        """
    def get_interpolator_type(self) -> ostk.mathematics.curve_fitting.Interpolator.Type:
        """
                        Get the type of interpolator used in the model.
        
                        Returns:
                            Interpolator.Type: The type of interpolator used in the model.
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        Get the interval of the model.
        
                        Returns:
                            Interval: The interval of the model.
        """
    def is_defined(self) -> bool:
        """
                        Check if the model is defined.
        
                        Returns:
                            bool: True if the model is defined, False otherwise.
        """
class Transform(ostk.astrodynamics.flight.profile.Model):
    """
    
                A flight profile model defined by a transform.
    
            
    """
    @staticmethod
    def inertial_pointing(trajectory: ostk.astrodynamics.Trajectory, quaternion: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion) -> Transform:
        """
                        Create a transform for inertial pointing.
        
                        Args:
                            trajectory (Trajectory): The trajectory of the satellite.
                            quaternion (Quaternion): The quaternion to rotate the axes by.
        
                        Returns:
                            Transform: The transform for inertial pointing.
        """
    @staticmethod
    def local_orbital_frame_pointing(orbit: ostk.astrodynamics.trajectory.Orbit, orbital_frame_type: ostk.astrodynamics.trajectory.Orbit.FrameType) -> Transform:
        """
                        Create a profile aligned with the provided local orbital frame type.
        
                        Args:
                            orbit (Orbit): The orbit of the satellite.
                            orbital_frame_type (OrbitalFrameType): The type of the orbital frame.
        
                        Returns:
                            Transform: The transform for the local orbital frame pointing.
        """
    @staticmethod
    def undefined() -> Transform:
        """
                        Get an undefined transform.
        
                        Returns:
                            Transform: The undefined transform.
        """
    def __init__(self, dynamic_provider: ostk.physics.coordinate.frame.provider.Dynamic, frame: ostk.physics.coordinate.Frame) -> None:
        """
                        Constructor.
        
                        Args:
                            dynamic_provider (DynamicProvider): The dynamic provider of the transform.
                            frame (Frame): The frame of the transform.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Calculate the state of the model at a specific instant.
        
                        Args:
                            instant (Instant): The instant at which to calculate the state.
        
                        Returns:
                            State: The state of the model at the specified instant.
        """
    def get_axes_at(self, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Axes:
        """
                        Get the axes of the model at a specific instant.
        
                        Args:
                            instant (Instant): The instant at which to get the axes.
        
                        Returns:
                            numpy.ndarray: The axes of the model at the specified instant.
        """
    def get_body_frame(self, frame_name: ostk.core.type.String) -> ostk.physics.coordinate.Frame:
        """
                        Get the body frame of the model with the specified name.
        
                        Args:
                            frame_name (str): The name of the body frame.
        
                        Returns:
                            Frame: The body frame of the model with the specified name.
        """
    def is_defined(self) -> bool:
        """
                        Check if the model is defined.
        
                        Returns:
                            bool: True if the model is defined, False otherwise.
        """
