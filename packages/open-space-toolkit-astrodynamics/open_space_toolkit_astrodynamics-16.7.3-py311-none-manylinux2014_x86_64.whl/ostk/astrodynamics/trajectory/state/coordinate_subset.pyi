from __future__ import annotations
import numpy
import ostk.astrodynamics.trajectory.state
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.time
__all__ = ['AngularVelocity', 'AttitudeQuaternion', 'CartesianAcceleration', 'CartesianPosition', 'CartesianVelocity']
class AngularVelocity(ostk.astrodynamics.trajectory.state.CoordinateSubset):
    """
    
                Angular velocity coordinate subset.
    
                Defined with respect to a reference frame and a Attitude quaternion.
    
            
    """
    @staticmethod
    def default() -> AngularVelocity:
        """
                        Get the default Angular velocity subset.
        
                        Returns:
                            AngularVelocity: The default Angular velocity subset.
        """
    def __init__(self, attitude_quaternion: typing.Any, name: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            attitude_quaternion (AttitudeQuaternion): The Attitude quaternion.
                            name (str): The name of the subset.
        """
    def in_frame(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], from_frame: ostk.physics.coordinate.Frame, to_frame: ostk.physics.coordinate.Frame, coordinate_broker: ostk.astrodynamics.trajectory.state.CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Convert a Angular velocity from one reference frame to another.
        
                        Args:
                            instant (Instant): The instant of the conversion.
                            coordinates (numpy.ndarray): The Angular velocity to convert.
                            from_frame (str): The reference frame of the input Angular velocity.
                            to_frame (str): The reference frame of the output Angular velocity.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The Angular velocity in the output reference frame.
        """
class AttitudeQuaternion(ostk.astrodynamics.trajectory.state.CoordinateSubset):
    """
    
                Attitude quaternion coordinate subset.
    
                Defined with respect to a reference frame.
    
            
    """
    @staticmethod
    def default() -> AttitudeQuaternion:
        """
                        Get the default Attitude quaternion subset.
        
                        Returns:
                            AttitudeQuaternion: The default Attitude quaternion subset.
        """
    def __init__(self, name: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            name (str): The name of the subset.
        """
    def in_frame(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], from_frame: ostk.physics.coordinate.Frame, to_frame: ostk.physics.coordinate.Frame, coordinate_broker: ostk.astrodynamics.trajectory.state.CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Convert a Attitude quaternion from one reference frame to another.
        
                        Args:
                            instant (Instant): The instant of the conversion.
                            coordinates (numpy.ndarray): The Attitude quaternion to convert.
                            from_frame (str): The reference frame of the input Attitude quaternion.
                            to_frame (str): The reference frame of the output Attitude quaternion.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The Attitude quaternion in the output reference frame.
        """
class CartesianAcceleration(ostk.astrodynamics.trajectory.state.CoordinateSubset):
    """
    
                Cartesian acceleration coordinate subset.
    
                Defined with respect to a reference frame.
            
    """
    @staticmethod
    def default() -> CartesianAcceleration:
        """
                        Get the default Cartesian acceleration subset.
        
                        Returns:
                            CartesianAcceleration: The default Cartesian acceleration subset.
        """
    @staticmethod
    def thrust_acceleration() -> CartesianAcceleration:
        """
                        Get the Cartesian acceleration subset for thrust acceleration.
        
                        Returns:
                            CartesianAcceleration: The Cartesian acceleration subset for thrust acceleration.
        """
    def __init__(self, cartesian_position: CartesianPosition, cartesian_velocity: CartesianVelocity, name: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            cartesian_position (CartesianPosition): The Cartesian position.
                            cartesian_velocity (CartesianVelocity): The Cartesian velocity.
                            name (str): The name of the subset.
        """
    def in_frame(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], from_frame: ostk.physics.coordinate.Frame, to_frame: ostk.physics.coordinate.Frame, coordinate_broker: ostk.astrodynamics.trajectory.state.CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Convert a Cartesian acceleration from one reference frame to another.
        
                        Args:
                            instant (Instant): The instant of the conversion.
                            coordinates (np.ndarray): The Cartesian acceleration to convert.
                            from_frame (Frame): The reference frame of the input Cartesian acceleration.
                            to_frame (Frame): The reference frame of the output Cartesian acceleration.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The Cartesian acceleration in the output reference frame.
        """
class CartesianPosition(ostk.astrodynamics.trajectory.state.CoordinateSubset):
    """
    
                Cartesian position coordinate subset.
    
                Defined with respect to a reference frame.
    
            
    """
    @staticmethod
    def default() -> CartesianPosition:
        """
                        Get the default Cartesian position subset.
        
                        Returns:
                            CartesianPosition: The default Cartesian position subset.
        """
    def __init__(self, name: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            name (str): The name of the subset.
        """
    def in_frame(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], from_frame: ostk.physics.coordinate.Frame, to_frame: ostk.physics.coordinate.Frame, coordinate_broker: ostk.astrodynamics.trajectory.state.CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Convert a Cartesian position from one reference frame to another.
        
                        Args:
                            instant (Instant): The instant of the conversion.
                            coordinates (numpy.ndarray): The Cartesian position to convert.
                            from_frame (str): The reference frame of the input Cartesian position.
                            to_frame (str): The reference frame of the output Cartesian position.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The Cartesian position in the output reference frame.
        """
class CartesianVelocity(ostk.astrodynamics.trajectory.state.CoordinateSubset):
    """
    
                Cartesian velocity coordinate subset.
    
                Defined with respect to a reference frame and a Cartesian position.
    
            
    """
    @staticmethod
    def default() -> CartesianVelocity:
        """
                        Get the default Cartesian velocity subset.
        
                        Returns:
                            CartesianVelocity: The default Cartesian velocity subset.
        """
    def __init__(self, cartesian_position: CartesianPosition, name: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            cartesian_position (CartesianPosition): The Cartesian position.
                            name (str): The name of the subset.
        """
    def in_frame(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], from_frame: ostk.physics.coordinate.Frame, to_frame: ostk.physics.coordinate.Frame, coordinate_broker: ostk.astrodynamics.trajectory.state.CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Convert a Cartesian velocity from one reference frame to another.
        
                        Args:
                            instant (Instant): The instant of the conversion.
                            coordinates (numpy.ndarray): The Cartesian velocity to convert.
                            from_frame (str): The reference frame of the input Cartesian velocity.
                            to_frame (str): The reference frame of the output Cartesian velocity.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The Cartesian velocity in the output reference frame.
        """
