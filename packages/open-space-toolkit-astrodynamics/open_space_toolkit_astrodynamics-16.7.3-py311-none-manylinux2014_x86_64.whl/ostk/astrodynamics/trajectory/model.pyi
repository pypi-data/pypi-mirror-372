from __future__ import annotations
import ostk.astrodynamics.trajectory
import ostk.mathematics.curve_fitting
import ostk.physics.coordinate.spherical
import ostk.physics.environment.object
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['Nadir', 'Tabulated', 'TargetScan']
class Nadir(ostk.astrodynamics.trajectory.Model):
    """
    
                Nadir trajectory model.
    
                This model represents a trajectory that follows the nadir direction of an orbit.
            
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Nadir) -> bool:
        ...
    def __init__(self, orbit: ostk.astrodynamics.trajectory.Orbit, step_size: ostk.physics.time.Duration = ...) -> None:
        """
                        Construct a `Nadir` object from an orbit.
        
                        Args:
                            orbit (Orbit): The orbit.
                            step_size (Duration): The step size for the trajectory. Defaults to 1e-2 seconds.
        
                        Returns:
                            Nadir: The `Nadir` object.
        """
    def __ne__(self, arg0: Nadir) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Calculate the state at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            State: The state at the given instant.
        """
    def get_orbit(self) -> ostk.astrodynamics.trajectory.Orbit:
        """
                        Get the orbit of the nadir model.
        
                        Returns:
                            Orbit: The orbit of the nadir model.
        """
    def get_step_size(self) -> ostk.physics.time.Duration:
        """
                        Get the step size of the nadir model.
        
                        Returns:
                            Duration: The step size of the nadir model.
        """
    def is_defined(self) -> bool:
        """
                        Check if the model is defined.
        
                        Returns:
                            bool: True if the model is defined, False otherwise.
        """
class Tabulated(ostk.astrodynamics.trajectory.Model):
    """
    
                A trajectory model defined by a set of states.
    
            
    """
    def __init__(self, states: list[ostk.astrodynamics.trajectory.State], interpolation_type: ostk.mathematics.curve_fitting.Interpolator.Type = ...) -> None:
        """
                        Constructor.
        
                        Args:
                            states (Array[State]): The states of the model.
                            interpolation_type (Interpolator.Type): The type of interpolation to use. Defaults to Linear.
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
    def calculate_states_at(self, instants: list[ostk.physics.time.Instant]) -> list[ostk.astrodynamics.trajectory.State]:
        """
                        Calculate the states of the model at the specified instants.
        
                        Args:
                            instants (list[Instant]): The instants at which to calculate the states.
        
                        Returns:
                            list[State]: The states of the model at the specified instants.
        """
    def get_first_state(self) -> ostk.astrodynamics.trajectory.State:
        """
                        Get the first state of the model.
        
                        Returns:
                            State: The first state of the model.
        """
    def get_interpolation_type(self) -> ostk.mathematics.curve_fitting.Interpolator.Type:
        """
                        Get the interpolation type of the model.
        
                        Returns:
                            Interpolator.Type: The interpolation type of the model.
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        Get the interval of the model.
        
                        Returns:
                            Interval: The interval of the model.
        """
    def get_last_state(self) -> ostk.astrodynamics.trajectory.State:
        """
                        Get the last state of the model.
        
                        Returns:
                            State: The last state of the model.
        """
    def is_defined(self) -> bool:
        """
                        Check if the model is defined.
        
                        Returns:
                            bool: True if the model is defined, False otherwise.
        """
class TargetScan(ostk.astrodynamics.trajectory.Model):
    """
    
                TargetScan trajectory model.
    
                This model represents a trajectory that scans between two target locations on a celestial body.
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def from_ground_speed(start_lla: ostk.physics.coordinate.spherical.LLA, end_lla: ostk.physics.coordinate.spherical.LLA, ground_speed: ostk.physics.unit.Derived, start_instant: ostk.physics.time.Instant, celestial: ostk.physics.environment.object.Celestial = ..., step_size: ostk.physics.time.Duration = ...) -> TargetScan:
        """
                        Construct a `TargetScan` object from ground speed.
        
                        Args:
                            start_lla (LLA): The starting location.
                            end_lla (LLA): The ending location.
                            ground_speed (Derived): The ground speed.
                            start_instant (Instant): The starting instant.
                            celestial (Celestial): The celestial body.
                            step_size (Duration): The step size for the trajectory.
        
                        Returns:
                            TargetScan: The `TargetScan` object.
        """
    def __eq__(self, arg0: TargetScan) -> bool:
        ...
    def __init__(self, start_lla: ostk.physics.coordinate.spherical.LLA, end_lla: ostk.physics.coordinate.spherical.LLA, start_instant: ostk.physics.time.Instant, end_instant: ostk.physics.time.Instant, celestial: ostk.physics.environment.object.Celestial = ..., step_size: ostk.physics.time.Duration = ...) -> None:
        """
                        Construct a `TargetScan` object.
        
                        Args:
                            start_lla (LLA): The starting location.
                            end_lla (LLA): The ending location.
                            start_instant (Instant): The starting instant.
                            end_instant (Instant): The ending instant.
                            celestial (Celestial): The celestial body. Defaults to Earth.WGS84().
                            step_size (Duration): The step size for the trajectory. Defaults to 1e-2 seconds.
        
                        Returns:
                            TargetScan: The `TargetScan` object.
        """
    def __ne__(self, arg0: TargetScan) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Calculate the state at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            State: The state at the given instant.
        """
    def get_celestial(self) -> ostk.physics.environment.object.Celestial:
        """
                        Get the celestial object of the target scan.
        
                        Returns:
                            Celestial: The celestial object.
        """
    def get_end_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the ending instant of the target scan.
        
                        Returns:
                            Instant: The ending instant.
        """
    def get_end_lla(self) -> ostk.physics.coordinate.spherical.LLA:
        """
                        Get the ending LLA of the target scan.
        
                        Returns:
                            LLA: The ending LLA.
        """
    def get_start_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the starting instant of the target scan.
        
                        Returns:
                            Instant: The starting instant.
        """
    def get_start_lla(self) -> ostk.physics.coordinate.spherical.LLA:
        """
                        Get the starting LLA of the target scan.
        
                        Returns:
                            LLA: The starting LLA.
        """
    def get_step_size(self) -> ostk.physics.time.Duration:
        """
                        Get the step size of the target scan.
        
                        Returns:
                            Duration: The step size.
        """
    def is_defined(self) -> bool:
        """
                        Check if the model is defined.
        
                        Returns:
                            bool: True if the model is defined, False otherwise.
        """
