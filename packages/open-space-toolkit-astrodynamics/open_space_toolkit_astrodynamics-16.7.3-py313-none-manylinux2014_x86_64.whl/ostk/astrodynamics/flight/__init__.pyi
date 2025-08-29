from __future__ import annotations
import numpy
import ostk.astrodynamics
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.mathematics.curve_fitting
import ostk.mathematics.geometry.d3.object
import ostk.mathematics.geometry.d3.transformation.rotation
import ostk.physics.coordinate
import ostk.physics.time
import ostk.physics.unit
import typing
from . import profile
from . import system
__all__ = ['Maneuver', 'Profile', 'System', 'profile', 'system']
class Maneuver:
    """
    
                Spacecraft Maneuver class.
                Store an acceleration and mass flow rate profile of a spacecraft maneuver.
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def constant_mass_flow_rate_profile(states: list[ostk.astrodynamics.trajectory.State], mass_flow_rate: ostk.core.type.Real) -> Maneuver:
        """
                        Create a maneuver from a constant mass flow rate profile.
        
                        Args:
                            instants (list[Instant]): An array of instants, must be sorted.
                            acceleration_profile (list[numpy.ndarray]): An acceleration profile of the maneuver, one numpy.ndarray per instant.
                            frame (Frame): A frame in which the acceleration profile is defined.
                            mass_flow_rate (float): The constant mass flow rate (negative number expected).
        
                        Returns:
                            Maneuver: The created maneuver.
        """
    def __eq__(self, arg0: Maneuver) -> bool:
        ...
    def __init__(self, states: list[ostk.astrodynamics.trajectory.State]) -> None:
        """
                        Constructor.
        
                        Args:
                            states (list[State]): An list of states, must be sorted, must include the CartesianPosition, CartesianVelocity, CartesianAcceleration and MassFlowRate subsets.
        """
    def __ne__(self, arg0: Maneuver) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_average_specific_impulse(self, initial_spacecraft_mass: ostk.physics.unit.Mass) -> ostk.core.type.Real:
        """
                        Calculate the average specific impulse of the maneuver.
        
                        Args:
                            initial_spacecraft_mass (Mass): The initial mass of the spacecraft.
        
                        Returns:
                            float: The average specific impulse (s).
        """
    def calculate_average_thrust(self, initial_spacecraft_mass: ostk.physics.unit.Mass) -> ostk.core.type.Real:
        """
                        Calculate the average thrust of the maneuver.
        
                        Args:
                            initial_spacecraft_mass (Mass): The initial mass of the spacecraft.
        
                        Returns:
                            float: The average thrust (N).
        """
    def calculate_delta_mass(self) -> ostk.physics.unit.Mass:
        """
                        Calculate the delta mass of the maneuver.
        
                        Returns:
                            Mass: The delta mass (always positive) (kg).
        """
    def calculate_delta_v(self) -> ostk.core.type.Real:
        """
                        Calculate the delta-v of the maneuver.
        
                        Returns:
                            float: The delta-v value (m/s).
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        Get the interval of the maneuver.
        
                        Returns:
                            Interval: The interval.
        """
    def get_states(self) -> list[ostk.astrodynamics.trajectory.State]:
        """
                        Get the states.
        
                        Returns:
                            list[State]: The states.
        """
    def is_defined(self) -> bool:
        """
                        Check if the maneuver is defined.
        
                        Returns:
                            bool: True if the maneuver is defined, False otherwise. (Always returns true).
        """
    def to_tabulated_dynamics(self, frame: ostk.physics.coordinate.Frame = ..., interpolation_type: ostk.mathematics.curve_fitting.Interpolator.Type = ...) -> ...:
        """
                        Convert the maneuver to tabulated dynamics.
        
                        Args:
                            frame (Frame, optional): The frame in which the acceleration profile is defined. Defaults to the default acceleration frame.
                            interpolation_type (Interpolator.Type, optional): The interpolation type to use. Defaults to the default interpolation type.
        
                        Returns:
                            Tabulated: The tabulated dynamics.
        """
class Profile:
    """
    
                Spacecraft Flight Profile.
    
            
    """
    class Axis:
        """
        
                    The axis of the profile.
                
        
        Members:
        
          X : X axis
        
          Y : Y axis
        
          Z : Z axis
        """
        X: typing.ClassVar[Profile.Axis]  # value = <Axis.X: 0>
        Y: typing.ClassVar[Profile.Axis]  # value = <Axis.Y: 1>
        Z: typing.ClassVar[Profile.Axis]  # value = <Axis.Z: 2>
        __members__: typing.ClassVar[dict[str, Profile.Axis]]  # value = {'X': <Axis.X: 0>, 'Y': <Axis.Y: 1>, 'Z': <Axis.Z: 2>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class CustomTarget(Profile.Target):
        """
        
                    The custom target.
        
                
        """
        def __init__(self, orientation_generator: typing.Callable[[ostk.astrodynamics.trajectory.State], numpy.ndarray[numpy.float64[3, 1]]], axis: Profile.Axis, anti_direction: bool = False) -> None:
            """
                            Constructor.
            
                            Args:
                                orientation_generator (Callable[np.ndarray, State]]): The orientation generator, accepts a state and returns a size 3 array of directions.
                                axis (Profile.Axis): The axis.
                                anti_direction (bool): True if the direction is flipped, False otherwise. Defaults to False.
            """
        @property
        def orientation_generator(self) -> typing.Callable[[ostk.astrodynamics.trajectory.State], numpy.ndarray[numpy.float64[3, 1]]]:
            """
            The orientation generator of the target.
            """
    class OrientationProfileTarget(Profile.Target):
        """
        
                    The alignment profile target.
        
                
        """
        def __init__(self, orientation_profile: list[tuple[ostk.physics.time.Instant, numpy.ndarray[numpy.float64[3, 1]]]], axis: Profile.Axis, anti_direction: bool = False) -> None:
            """
                            Constructor.
            
                            Args:
                                orientation_profile (list[Tuple[Instant, Vector3d]]): The orientation profile.
                                axis (Profile.Axis): The axis.
                                anti_direction (bool): True if the direction is flipped, False otherwise. Defaults to False.
            """
        @property
        def orientation_profile(self) -> list[tuple[ostk.physics.time.Instant, numpy.ndarray[numpy.float64[3, 1]]]]:
            """
            The orientation profile of the target.
            """
    class Target:
        """
        
                    The target of the profile.
        
                
        """
        def __init__(self, type: Profile.TargetType, axis: Profile.Axis, anti_direction: bool = False) -> None:
            """
                            Constructor.
            
                            Args:
                                type (Profile.TargetType): The target type.
                                axis (Profile.Axis): The axis.
                                anti_direction (bool): True if the direction is flipped, False otherwise. Defaults to False.
            """
        @property
        def anti_direction(self) -> bool:
            """
            True if the direction is flipped, False otherwise.
            """
        @property
        def axis(self) -> Profile.Axis:
            """
            The axis of the target.
            """
        @property
        def type(self) -> Profile.TargetType:
            """
            The type of the target.
            """
    class TargetType:
        """
        
                    The target type of the profile.
                
        
        Members:
        
          GeocentricNadir : Geocentric nadir
        
          GeodeticNadir : Geodetic nadir
        
          Trajectory : Deprecated - Use TargetPosition instead.
        
          TargetPosition : Target position
        
          TargetVelocity : Target velocity
        
          TargetSlidingGroundVelocity : Target sliding ground velocity
        
          Sun : Sun
        
          Moon : Moon
        
          VelocityECI : Velocity in ECI
        
          VelocityECEF : Velocity in ECEF
        
          OrbitalMomentum : Orbital momentum
        
          OrientationProfile : Orientation profile
        """
        GeocentricNadir: typing.ClassVar[Profile.TargetType]  # value = <TargetType.GeocentricNadir: 0>
        GeodeticNadir: typing.ClassVar[Profile.TargetType]  # value = <TargetType.GeodeticNadir: 1>
        Moon: typing.ClassVar[Profile.TargetType]  # value = <TargetType.Moon: 7>
        OrbitalMomentum: typing.ClassVar[Profile.TargetType]  # value = <TargetType.OrbitalMomentum: 10>
        OrientationProfile: typing.ClassVar[Profile.TargetType]  # value = <TargetType.OrientationProfile: 11>
        Sun: typing.ClassVar[Profile.TargetType]  # value = <TargetType.Sun: 6>
        TargetPosition: typing.ClassVar[Profile.TargetType]  # value = <TargetType.TargetPosition: 3>
        TargetSlidingGroundVelocity: typing.ClassVar[Profile.TargetType]  # value = <TargetType.TargetSlidingGroundVelocity: 5>
        TargetVelocity: typing.ClassVar[Profile.TargetType]  # value = <TargetType.TargetVelocity: 4>
        Trajectory: typing.ClassVar[Profile.TargetType]  # value = <TargetType.Trajectory: 2>
        VelocityECEF: typing.ClassVar[Profile.TargetType]  # value = <TargetType.VelocityECEF: 9>
        VelocityECI: typing.ClassVar[Profile.TargetType]  # value = <TargetType.VelocityECI: 8>
        __members__: typing.ClassVar[dict[str, Profile.TargetType]]  # value = {'GeocentricNadir': <TargetType.GeocentricNadir: 0>, 'GeodeticNadir': <TargetType.GeodeticNadir: 1>, 'Trajectory': <TargetType.Trajectory: 2>, 'TargetPosition': <TargetType.TargetPosition: 3>, 'TargetVelocity': <TargetType.TargetVelocity: 4>, 'TargetSlidingGroundVelocity': <TargetType.TargetSlidingGroundVelocity: 5>, 'Sun': <TargetType.Sun: 6>, 'Moon': <TargetType.Moon: 7>, 'VelocityECI': <TargetType.VelocityECI: 8>, 'VelocityECEF': <TargetType.VelocityECEF: 9>, 'OrbitalMomentum': <TargetType.OrbitalMomentum: 10>, 'OrientationProfile': <TargetType.OrientationProfile: 11>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class TrajectoryTarget(Profile.Target):
        """
        
                    The trajectory target.
        
                
        """
        @staticmethod
        def target_position(trajectory: ostk.astrodynamics.Trajectory, axis: Profile.Axis, anti_direction: bool = False) -> Profile.TrajectoryTarget:
            """
                            Create a target, which produces a vector pointing from the observer to the target position.
            """
        @staticmethod
        def target_sliding_ground_velocity(trajectory: ostk.astrodynamics.Trajectory, axis: Profile.Axis, anti_direction: bool = False) -> Profile.TrajectoryTarget:
            """
                            Create a target, which produces a vector pointing along the ground velocity vector (aka the scan direction of the point sliding across the ground).
                            This will compensate for the rotation of the referenced celestial body.
            """
        @staticmethod
        def target_velocity(trajectory: ostk.astrodynamics.Trajectory, axis: Profile.Axis, anti_direction: bool = False) -> Profile.TrajectoryTarget:
            """
                            Create a target, which produces a vector pointing along the scan direction.
            """
        def __init__(self, trajectory: ostk.astrodynamics.Trajectory, axis: Profile.Axis, anti_direction: bool = False) -> None:
            """
                            Constructor.
            
                            Args:
                                trajectory (Trajectory): The trajectory, required only if the target type is `Trajectory`.
                                axis (Profile.Axis): The axis.
                                anti_direction (bool): True if the direction is flipped, False otherwise. Defaults to False.
            """
        @property
        def trajectory(self) -> ostk.astrodynamics.Trajectory:
            """
            The trajectory of the target. Used to compute the target position or velocity.
            """
    @staticmethod
    def align_and_constrain(alignment_target: Profile.Target, clocking_target: Profile.Target, angular_offset: ostk.physics.unit.Angle = ...) -> typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.mathematics.geometry.d3.transformation.rotation.Quaternion]:
        """
                        Generate a function that provides a quaternion that aligns to the `alignment_target` and constrains to the `clocking_target` for a given state.
        
                        Args:
                            alignment_target (Profile.Target | Profile.TrajectoryTarget | Profile.OrientationProfileTarget | Profile.CustomTarget): The alignment target.
                            clocking_target (Profile.Target | Profile.TrajectoryTarget | Profile.OrientationProfileTarget | Profile.CustomTarget): The clocking target.
                            angular_offset (Angle): The angular offset. Defaults to `Angle.Zero()`.
        
                        Returns:
                            callable[Quaternion, State]: The custom orientation.
        """
    @staticmethod
    @typing.overload
    def custom_pointing(orbit: ostk.astrodynamics.trajectory.Orbit, orientation_generator: typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.mathematics.geometry.d3.transformation.rotation.Quaternion]) -> Profile:
        """
                        Create a custom pointing profile.
        
                        Args:
                            orbit (Orbit): The orbit.
                            orientation_generator (callable[Quaternion, State]): The orientation generator. Typically used in conjunction with `align_and_constrain`.
        
                        Returns:
                            Profile: The custom pointing profile.
        """
    @staticmethod
    @typing.overload
    def custom_pointing(orbit: ostk.astrodynamics.trajectory.Orbit, alignment_target: Profile.Target, clocking_target: Profile.Target, angular_offset: ostk.physics.unit.Angle = ...) -> Profile:
        """
                        Create a custom pointing profile.
        
                        Args:
                            orbit (Orbit): The orbit.
                            alignment_target (Profile.Target): The alignment target.
                            clocking_target (Profile.Target): The clocking target.
                            angular_offset (Angle): The angular offset. Defaults to `Angle.Zero()`.
        
                        Returns:
                            Profile: The custom pointing profile.
        """
    @staticmethod
    def inertial_pointing(trajectory: ostk.astrodynamics.Trajectory, quaternion: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion) -> Profile:
        """
                        Create an inertial pointing profile.
        
                        Args:
                            trajectory (Trajectory): The trajectory.
                            quaternion (Quaternion): The quaternion.
        
                        Returns:
                            Profile: The inertial pointing profile.
        """
    @staticmethod
    def local_orbital_frame_pointing(orbit: ostk.astrodynamics.trajectory.Orbit, orbital_frame_type: ostk.astrodynamics.trajectory.Orbit.FrameType) -> Profile:
        """
                        Create a profile aligned with the provided local orbital frame type.
        
                        Args:
                            orbit (Orbit): The orbit.
                            orbital_frame_type (OrbitalFrameType): The type of the orbital frame.
        
                        Returns:
                            Profile: The profile aligned with the local orbital frame.
        """
    @staticmethod
    def undefined() -> Profile:
        """
                        Create an undefined profile.
        
                        Returns:
                            Profile: The undefined profile.
        """
    def __init__(self, model: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            model (Model): The profile model.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_model(self) -> ...:
        """
                        Access the profile model.
        
                        Returns:
                            Model: The profile model.
        """
    def get_axes_at(self, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Axes:
        """
                        Get the axes of the profile at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            Frame: The axes of the profile at the given instant.
        """
    def get_body_frame(self, frame_name: ostk.core.type.String) -> ostk.physics.coordinate.Frame:
        """
                        Get the body frame of the profile.
        
                        Args:
                            frame_name (str): The name of the frame.
        
                        Returns:
                            Frame: The body frame of the profile.
        """
    def get_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Get the state of the profile at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            State: The state of the profile at the given instant.
        """
    def get_states_at(self, instants: list[ostk.physics.time.Instant]) -> list[ostk.astrodynamics.trajectory.State]:
        """
                        Get the states of the profile at given instants.
        
                        Args:
                            instants (list): The instants.
        
                        Returns:
                            list: The states of the profile at the given instants.
        """
    def is_defined(self) -> bool:
        """
                        Check if the profile is defined.
        
                        Returns:
                            bool: True if the profile is defined, False otherwise.
        """
class System:
    """
    
                    A flight system.
    
                    Provides the interface for flight systems.
    
                    .. warning:: This class is an abstract class and cannot be instantiated.
    
                
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> System:
        """
                            Create an undefined system.
        
                            Returns:
                                System: The undefined system.
        """
    def __eq__(self, arg0: System) -> bool:
        ...
    def __init__(self, mass: ostk.physics.unit.Mass, geometry: ostk.mathematics.geometry.d3.object.Composite) -> None:
        """
                            Constructor.
        
                            Args:
                                mass (Mass): The mass of the system.
                                geometry (Composite): The geometry of the system.
        """
    def __ne__(self, arg0: System) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_geometry(self) -> ostk.mathematics.geometry.d3.object.Composite:
        """
                            Get the geometry of the system.
        
                            Returns:
                                Composite: The geometry of the system.
        """
    def get_mass(self) -> ostk.physics.unit.Mass:
        """
                            Get the mass of the system.
        
                            Returns:
                                Mass: The mass of the system.
        """
    def is_defined(self) -> bool:
        """
                            Check if the system is defined.
        
                            Returns:
                                bool: True if the system is defined, False otherwise.
        """
