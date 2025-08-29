from __future__ import annotations
import numpy
import ostk.astrodynamics
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.mathematics.object
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.coordinate.spherical
import ostk.physics.environment.object
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['AccessTarget', 'Generator', 'VisibilityCriterion']
class AccessTarget:
    """
    
                Represents the configuration for an Access target, including azimuth, elevation, and range intervals, as well
                as position and LLA (Latitude, Longitude, Altitude).
            
    """
    class Type:
        """
        
                Enumeration of Access Target types.
            
        
        Members:
        
          Fixed
        
          Trajectory
        """
        Fixed: typing.ClassVar[AccessTarget.Type]  # value = <Type.Fixed: 0>
        Trajectory: typing.ClassVar[AccessTarget.Type]  # value = <Type.Trajectory: 1>
        __members__: typing.ClassVar[dict[str, AccessTarget.Type]]  # value = {'Fixed': <Type.Fixed: 0>, 'Trajectory': <Type.Trajectory: 1>}
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
    Fixed: typing.ClassVar[AccessTarget.Type]  # value = <Type.Fixed: 0>
    Trajectory: typing.ClassVar[AccessTarget.Type]  # value = <Type.Trajectory: 1>
    @staticmethod
    def from_lla(visibility_criterion: typing.Any, lla: ostk.physics.coordinate.spherical.LLA, celestial: ostk.physics.environment.object.Celestial) -> AccessTarget:
        """
                        Create an AccessTarget from latitude, longitude, and altitude (LLA).
        
                        Args:
                            visibility_criterion (VisibilityCriterion): The visibility criterion.
                            lla (LLA): The latitude, longitude, and altitude.
                            celestial (Celestial): The celestial body.
        
                        Returns:
                            AccessTarget: The created AccessTarget instance.
        """
    @staticmethod
    def from_position(visibility_criterion: typing.Any, position: ostk.physics.coordinate.Position) -> AccessTarget:
        """
                        Create an AccessTarget from a fixed position.
        
                        Args:
                            visibility_criterion (VisibilityCriterion): The visibility criterion.
                            position (Position): The fixed position.
        
                        Returns:
                            AccessTarget: The created AccessTarget instance.
        """
    @staticmethod
    def from_trajectory(visibility_criterion: typing.Any, trajectory: ostk.astrodynamics.Trajectory) -> AccessTarget:
        """
                        Create an AccessTarget from a trajectory.
        
                        Args:
                            visibility_criterion (VisibilityCriterion): The visibility criterion.
                            trajectory (Trajectory): The trajectory.
        
                        Returns:
                            AccessTarget: The created AccessTarget instance.
        """
    def compute_r_sez_ecef(self, celestial: ostk.physics.environment.object.Celestial) -> numpy.ndarray[numpy.float64[3, 3]]:
        """
                        Compute the rotation matrix from ECEF to SEZ frame.
        
                        Args:
                            celestial (Celestial): The celestial body for the rotation computation.
        
                        Returns:
                            numpy.ndarray: The rotation matrix (3x3).
        """
    def get_lla(self, celestial: ostk.physics.environment.object.Celestial) -> ostk.physics.coordinate.spherical.LLA:
        """
                        Get the latitude, longitude, and altitude (LLA) of the access target.
        
                        Args:
                            celestial (Celestial): The celestial body for the LLA computation.
        
                        Returns:
                            LLA: The latitude, longitude, and altitude.
        """
    def get_position(self) -> ostk.physics.coordinate.Position:
        """
                        Get the fixed position associated with the access target.
        
                        Returns:
                            Position: The position.
        """
    def get_trajectory(self) -> ostk.astrodynamics.Trajectory:
        """
                        Get the trajectory associated with the access target.
        
                        Returns:
                            Trajectory: The trajectory.
        """
    def get_type(self) -> AccessTarget.Type:
        """
                        Get the type of the access target.
        
                        Returns:
                            AccessTarget.Type: The type of the access target.
        """
    def get_visibility_criterion(self) -> ...:
        """
                        Get the visibility criterion associated with the access target.
        
                        Returns:
                            VisibilityCriterion: The visibility criterion.
        """
class Generator:
    """
    
                An access generator.
    
            
    """
    @staticmethod
    def undefined() -> Generator:
        """
                        Get an undefined generator.
        
                        Returns:
                            Generator: An undefined generator.
        """
    def __init__(self, environment: ostk.physics.Environment, step: ostk.physics.time.Duration = ..., tolerance: ostk.physics.time.Duration = ..., access_filter: typing.Callable[[ostk.astrodynamics.Access], bool] = None, state_filter: typing.Callable[[ostk.astrodynamics.trajectory.State, ostk.astrodynamics.trajectory.State], bool] = None) -> None:
        """
                        Constructor.
        
                        Args:
                            environment (Environment): The environment.
                            step (Duration): The step. Defaults to Duration.minutes(1.0).
                            tolerance (Duration): The tolerance. Defaults to Duration.microseconds(1.0).
                            access_filter (function): The access filter. Defaults to None.
                            state_filter (function): The state filter. Defaults to None.
        """
    @typing.overload
    def compute_accesses(self, interval: ostk.physics.time.Interval, access_target: AccessTarget, to_trajectory: ostk.astrodynamics.Trajectory, coarse: bool = False) -> list[ostk.astrodynamics.Access]:
        """
                        Compute the accesses.
        
                        Args:
                            interval (Interval): The time interval over which to compute accesses.
                            access_target (AccessTarget): The access target to compute the accesses with.
                            to_trajectory (Trajectory): The trajectory to co compute the accesses with.
                            coarse (bool): True to use coarse mode. Defaults to False. Only available for fixed targets.
        
                        Returns:
                            Accesses: The accesses.
        """
    @typing.overload
    def compute_accesses(self, interval: ostk.physics.time.Interval, access_targets: list[AccessTarget], to_trajectory: ostk.astrodynamics.Trajectory, coarse: bool = False) -> list[list[ostk.astrodynamics.Access]]:
        """
                        Compute the accesses.
        
                        Args:
                            interval (Interval): The time interval over which to compute accesses.
                            access_targets (list[AccessTarget]): The access targets to compute the accesses with.
                            to_trajectory (Trajectory): The trajectory to co compute the accesses with.
                            coarse (bool): True to use coarse mode. Defaults to False. Only available for fixed targets.
        
                        Returns:
                            Accesses: The accesses.
        """
    def get_access_filter(self) -> typing.Callable[[ostk.astrodynamics.Access], bool]:
        """
                        Get the access filter.
        
                        Returns:
                            function: The access filter.
        """
    def get_condition_function(self, access_target: AccessTarget, to_trajectory: ostk.astrodynamics.Trajectory) -> typing.Callable[[ostk.physics.time.Instant], bool]:
        """
                        Get the condition function.
        
                        Args:
                            access_target (AccessTarget): The access target from which the condition function is being evaluated against.
                            to_trajectory (Trajectory): The trajectory to which the condition function is being evaluated against.
        
                        Returns:
                            function: The condition function.
        """
    def get_state_filter(self) -> typing.Callable[[ostk.astrodynamics.trajectory.State, ostk.astrodynamics.trajectory.State], bool]:
        """
                        Get the state filter.
        
                        Returns:
                            function: The state filter.
        """
    def get_step(self) -> ostk.physics.time.Duration:
        """
                        Get the step.
        
                        Returns:
                            Duration: The step.
        """
    def get_tolerance(self) -> ostk.physics.time.Duration:
        """
                        Get the tolerance.
        
                        Returns:
                            Duration: The tolerance.
        """
    def is_defined(self) -> bool:
        """
                        Check if the generator is defined.
        
                        Returns:
                            bool: True if the generator is defined, False otherwise.
        """
    def set_access_filter(self, access_filter: typing.Callable[[ostk.astrodynamics.Access], bool]) -> None:
        """
                    Set the access filter.
        
                    Args:
                        access_filter (function): The access filter.
        """
    def set_state_filter(self, state_filter: typing.Callable[[ostk.astrodynamics.trajectory.State, ostk.astrodynamics.trajectory.State], bool]) -> None:
        """
                    Set the state filter.
        
                    Args:
                        state_filter (function): The state filter.
        """
    def set_step(self, step: ostk.physics.time.Duration) -> None:
        """
                    Set the step.
        
                    Args:
                        step (Duration): The step.
        """
    def set_tolerance(self, tolerance: ostk.physics.time.Duration) -> None:
        """
                    Set the tolerance.
        
                    Args:
                        tolerance (Duration): The tolerance.
        """
class VisibilityCriterion:
    """
    
                A class representing a visibility criterion for accesses between objects.
            
    """
    class AERInterval:
        """
        
                    An AER interval visibility criterion.
                
        """
        def __init__(self, azimuth_interval: ostk.mathematics.object.RealInterval, elevation_interval: ostk.mathematics.object.RealInterval, range_interval: ostk.mathematics.object.RealInterval) -> None:
            """
                            Constructs an AER interval.
            
                            Args:
                                azimuth_interval (RealInterval): Azimuth interval in degrees.
                                elevation_interval (RealInterval): Elevation interval in degrees.
                                range_interval (RealInterval): Range interval in meters.
            """
        @typing.overload
        def is_satisfied(self, aer: ostk.physics.coordinate.spherical.AER) -> bool:
            """
                            Checks if the given AER satisfies the criterion.
            
                            Args:
                                aer (AER): The Azimuth, Elevation, and Range to check.
            
                            Returns:
                                bool: True if the criterion is satisfied, False otherwise.
            """
        @typing.overload
        def is_satisfied(self, azimuth: ostk.core.type.Real, elevation: ostk.core.type.Real, range: ostk.core.type.Real) -> bool:
            """
                            Checks if the given Azimuth, Elevation, and Range values satisfy the criterion.
            
                            Args:
                                azimuth (float): Azimuth in radians.
                                elevation (float): Elevation in radians.
                                range (float): Range in meters.
            
                            Returns:
                                bool: True if the criterion is satisfied, False otherwise.
            """
        @property
        def azimuth(self) -> ostk.mathematics.object.RealInterval:
            """
                            Azimuth interval in radians.
            
                            :type: RealInterval
            """
        @property
        def elevation(self) -> ostk.mathematics.object.RealInterval:
            """
                            Elevation interval in radians.
            
                            :type: RealInterval
            """
        @property
        def range(self) -> ostk.mathematics.object.RealInterval:
            """
                            Range interval in meters.
            
                            :type: RealInterval
            """
    class AERMask:
        """
        
                    An AER mask visibility criterion.
                
        """
        def __init__(self, azimuth_elevation_mask: dict[ostk.core.type.Real, ostk.core.type.Real], range_interval: ostk.mathematics.object.RealInterval) -> None:
            """
                            Constructs an AER mask.
            
                            Args:
                                azimuth_elevation_mask (dict): A map of azimuth angles (degrees) to elevation angles (degrees).
                                range_interval (RealInterval): Range interval in meters.
            """
        @typing.overload
        def is_satisfied(self, aer: ostk.physics.coordinate.spherical.AER) -> bool:
            """
                            Checks if the given AER satisfies the criterion.
            
                            Args:
                                aer (AER): The Azimuth, Elevation, and Range to check.
            
                            Returns:
                                bool: True if the criterion is satisfied, False otherwise.
            """
        @typing.overload
        def is_satisfied(self, azimuth: ostk.core.type.Real, elevation: ostk.core.type.Real, range: ostk.core.type.Real) -> bool:
            """
                            Checks if the given Azimuth, Elevation, and Range values satisfy the criterion.
            
                            Args:
                                azimuth (float): Azimuth in radians.
                                elevation (float): Elevation in radians.
                                range (float): Range in meters.
            
                            Returns:
                                bool: True if the criterion is satisfied, False otherwise.
            """
        @property
        def azimuth_elevation_mask(self) -> dict[ostk.core.type.Real, ostk.core.type.Real]:
            """
                            A map of azimuth angles to elevation angles in radians defining the mask.
            
                            :type: dict
            """
        @property
        def range(self) -> ostk.mathematics.object.RealInterval:
            """
                            Range interval in meters.
            
                            :type: RealInterval
            """
    class ElevationInterval:
        """
        
                    An elevation interval visibility criterion.
                
        """
        def __init__(self, elevation_interval: ostk.mathematics.object.RealInterval) -> None:
            """
                            Constructs an ElevationInterval visibility criterion.
            
                            Args:
                                elevation_interval (RealInterval): The elevation interval in degrees.
            """
        @typing.overload
        def is_satisfied(self, elevation: ostk.core.type.Real) -> bool:
            """
                            Checks if the given elevation angle satisfies the criterion.
            
                            Args:
                                elevation (float): Elevation angle in radians.
            
                            Returns:
                                bool: True if the criterion is satisfied, False otherwise.
            """
        @typing.overload
        def is_satisfied(self, elevation: ostk.physics.unit.Angle) -> bool:
            """
                            Checks if the given elevation angle satisfies the criterion.
            
                            Args:
                                elevation (Angle): Elevation angle.
            
                            Returns:
                                bool: True if the criterion is satisfied, False otherwise.
            """
        @property
        def elevation(self) -> ostk.mathematics.object.RealInterval:
            """
                            Elevation interval in radians.
            
                            :type: RealInterval
            """
    class LineOfSight:
        """
        
                    A line-of-sight visibility criterion.
                
        """
        def __init__(self, environment: ostk.physics.Environment) -> None:
            """
                            Constructs a LineOfSight visibility criterion.
            
                            Args:
                                environment (Environment): The environment to consider for line-of-sight calculations.
            """
        def is_satisfied(self, instant: ostk.physics.time.Instant, from_position_coordinates: numpy.ndarray[numpy.float64[3, 1]], to_position_coordinates: numpy.ndarray[numpy.float64[3, 1]]) -> bool:
            """
                            Checks if the line-of-sight criterion is satisfied between two positions at a given instant.
            
                            Args:
                                instant (Instant): The time at which to perform the check.
                                from_position_coordinates (np.ndarray): The position coordinates (in meters) of the observer.
                                to_position_coordinates (np.ndarray): The position coordinates (in meters) of the target.
            
                            Returns:
                                bool: True if there is a clear line of sight, False otherwise.
            """
    @staticmethod
    def from_aer_interval(azimuth_interval: ostk.mathematics.object.RealInterval, elevation_interval: ostk.mathematics.object.RealInterval, range_interval: ostk.mathematics.object.RealInterval) -> VisibilityCriterion:
        """
                        Creates a visibility criterion from azimuth, elevation, and range intervals.
        
                        Args:
                            azimuth_interval (RealInterval): Azimuth interval in degrees.
                            elevation_interval (RealInterval): Elevation interval in degrees.
                            range_interval (RealInterval): Range interval in meters.
        
                        Returns:
                            VisibilityCriterion: The visibility criterion instance.
        """
    @staticmethod
    def from_aer_mask(azimuth_elevation_mask: dict[ostk.core.type.Real, ostk.core.type.Real], range_interval: ostk.mathematics.object.RealInterval) -> VisibilityCriterion:
        """
                        Creates a visibility criterion from an azimuth-elevation mask and range interval.
        
                        Args:
                            azimuth_elevation_mask (dict): A map of azimuth angles (degrees) to elevation angles (degrees).
                            range_interval (RealInterval): Range interval in meters.
        
                        Returns:
                            VisibilityCriterion: The visibility criterion instance.
        """
    @staticmethod
    def from_elevation_interval(elevation_interval: ostk.mathematics.object.RealInterval) -> VisibilityCriterion:
        """
                        Creates a visibility criterion from an elevation interval.
        
                        Args:
                            elevation_interval (RealInterval): The elevation interval in degrees.
        
                        Returns:
                            VisibilityCriterion: The visibility criterion instance.
        """
    @staticmethod
    def from_line_of_sight(environment: ostk.physics.Environment) -> VisibilityCriterion:
        """
                        Creates a visibility criterion based on line-of-sight considerations.
        
                        Args:
                            environment (Environment): The environment to consider for line-of-sight calculations.
        
                        Returns:
                            VisibilityCriterion: The visibility criterion instance.
        """
    def as_aer_interval(self) -> VisibilityCriterion.AERInterval | None:
        """
                        Casts the visibility criterion to an AERInterval.
        
                        Returns:
                            AERInterval: The AERInterval criterion.
        
                        Raises:
                            ValueError: If the criterion is not an AERInterval.
        """
    def as_aer_mask(self) -> VisibilityCriterion.AERMask | None:
        """
                        Casts the visibility criterion to an AERMask.
        
                        Returns:
                            AERMask: The AERMask criterion.
        
                        Raises:
                            ValueError: If the criterion is not an AERMask.
        """
    def as_elevation_interval(self) -> VisibilityCriterion.ElevationInterval | None:
        """
                        Casts the visibility criterion to an ElevationInterval.
        
                        Returns:
                            ElevationInterval: The ElevationInterval criterion.
        
                        Raises:
                            ValueError: If the criterion is not an ElevationInterval.
        """
    def as_line_of_sight(self) -> VisibilityCriterion.LineOfSight | None:
        """
                        Casts the visibility criterion to a LineOfSight.
        
                        Returns:
                            LineOfSight: The LineOfSight criterion.
        
                        Raises:
                            ValueError: If the criterion is not a LineOfSight.
        """
    def is_aer_interval(self) -> bool:
        """
                        Checks if the visibility criterion is an AERInterval.
        
                        Returns:
                            bool: True if it is an AERInterval criterion, False otherwise.
        """
    def is_aer_mask(self) -> bool:
        """
                        Checks if the visibility criterion is an AERMask.
        
                        Returns:
                            bool: True if it is an AERMask criterion, False otherwise.
        """
    def is_elevation_interval(self) -> bool:
        """
                        Checks if the visibility criterion is an ElevationInterval.
        
                        Returns:
                            bool: True if it is an ElevationInterval criterion, False otherwise.
        """
    def is_line_of_sight(self) -> bool:
        """
                        Checks if the visibility criterion is a LineOfSight.
        
                        Returns:
                            bool: True if it is a LineOfSight criterion, False otherwise.
        """
