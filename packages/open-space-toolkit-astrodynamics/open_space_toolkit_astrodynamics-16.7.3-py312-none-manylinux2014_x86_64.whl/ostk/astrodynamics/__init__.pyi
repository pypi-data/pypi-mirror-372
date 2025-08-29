from __future__ import annotations
import numpy
from ostk import astrodynamics as OpenSpaceToolkitAstrodynamicsPy
from ostk.astrodynamics.trajectory import State as PyState
from ostk import core as OpenSpaceToolkitCorePy
from ostk.core import container
from ostk.core import filesystem
from ostk.core import type
import ostk.core.type
from ostk import io as OpenSpaceToolkitIOPy
from ostk.io import URL
from ostk.io import ip
from ostk import mathematics as OpenSpaceToolkitMathematicsPy
from ostk.mathematics import curve_fitting
from ostk.mathematics import geometry
from ostk.mathematics import object
import ostk.physics
from ostk import physics as OpenSpaceToolkitPhysicsPy
from ostk.physics import Environment
from ostk.physics import Manager
from ostk.physics import Unit
import ostk.physics.coordinate
from ostk.physics import coordinate
import ostk.physics.coordinate.spherical
from ostk.physics import environment
import ostk.physics.environment.object
import ostk.physics.time
from ostk.physics import time
from ostk.physics import unit
import ostk.physics.unit
import typing
from . import access
from . import conjunction
from . import converters
from . import data
from . import dynamics
from . import eclipse
from . import estimator
from . import event_condition
from . import flight
from . import guidance_law
from . import pytrajectory
from . import solver
from . import trajectory
__all__ = ['Access', 'Dynamics', 'Environment', 'EventCondition', 'GuidanceLaw', 'Manager', 'OpenSpaceToolkitAstrodynamicsPy', 'OpenSpaceToolkitCorePy', 'OpenSpaceToolkitIOPy', 'OpenSpaceToolkitMathematicsPy', 'OpenSpaceToolkitPhysicsPy', 'PyState', 'RootSolver', 'Trajectory', 'URL', 'Unit', 'access', 'conjunction', 'container', 'converters', 'coordinate', 'curve_fitting', 'data', 'dynamics', 'eclipse', 'environment', 'estimator', 'event_condition', 'filesystem', 'flight', 'geometry', 'guidance_law', 'ip', 'object', 'pytrajectory', 'solver', 'time', 'trajectory', 'type', 'unit']
class Access:
    """
    
                    Object-to-object visibility
                    
                    This class encapsulates the concept of visibility access between two trajectories.
                    
                
    """
    class Type:
        """
        
                        Access type.
                    
        
        Members:
        
          Undefined : Undefined
        
          Complete : Complete
        
          Partial : Partial
        """
        Complete: typing.ClassVar[Access.Type]  # value = <Type.Complete: 1>
        Partial: typing.ClassVar[Access.Type]  # value = <Type.Partial: 2>
        Undefined: typing.ClassVar[Access.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Access.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Complete': <Type.Complete: 1>, 'Partial': <Type.Partial: 2>}
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
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def string_from_type(type: Access.Type) -> ostk.core.type.String:
        """
                            Returns a string representation of the Access type.
            
                            Args:
                                type (Access.Type): The type of the access.
                            
                            Returns:
                                str: A string representation of the type.
        """
    @staticmethod
    def undefined() -> Access:
        """
                            Creates an undefined Access object.
                            
                            Returns:
                                Access: An undefined Access object.
        """
    def __eq__(self, arg0: Access) -> bool:
        ...
    def __init__(self, type: Access.Type, acquisition_of_signal: ostk.physics.time.Instant, time_of_closest_approach: ostk.physics.time.Instant, loss_of_signal: ostk.physics.time.Instant, max_elevation: ostk.physics.unit.Angle) -> None:
        """
                            Constructs an Access object.
                            
                            Args:
                                type (Access.Type): Type of the access (Complete, Partial, Undefined)
                                acquisition_of_signal (Instant): The instant when the signal is first acquired
                                time_of_closest_approach (Instant): The time of closest approach between objects
                                loss_of_signal (Instant): The instant when the signal is lost
                                max_elevation (Angle): The maximum elevation angle during the access
        """
    def __ne__(self, arg0: Access) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_acquisition_of_signal(self) -> ostk.physics.time.Instant:
        """
                            Get the acquisition of signal of the access.
        
                            Returns:
                                Instant: The acquisition of signal of the access.
        """
    def get_duration(self) -> ostk.physics.time.Duration:
        """
                            Get the duration of the access.
        
                            Returns:
                               Duration: The duration of the access.
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                            Get the interval of the access.
        
                            Returns:
                               Interval: The interval of the access.
        """
    def get_loss_of_signal(self) -> ostk.physics.time.Instant:
        """
                            Get the loss of signal of the access.
        
                            Returns:
                               Instant: The loss of signal of the access.
        """
    def get_max_elevation(self) -> ostk.physics.unit.Angle:
        """
                            Get the maximum elevation of the access.
        
                            Returns:
                              Angle: The maximum elevation of the access.
        """
    def get_time_of_closest_approach(self) -> ostk.physics.time.Instant:
        """
                            Get the time of closest approach of the access.
        
                            Returns:
                                Instant: The time of closest approach of the access.
        """
    def get_type(self) -> Access.Type:
        """
                            Get the type of the access.
        
                            Returns:
                                Access.Type: The type of the access.
        """
    def is_complete(self) -> bool:
        """
                            Check if the access is complete.
                            
                            Returns:
                                bool: True if complete, False otherwise.
        """
    def is_defined(self) -> bool:
        """
                            Check if the Access object is defined.
                            
                            Returns:
                               bool: True if defined, False otherwise.
        """
class Dynamics:
    """
    
                Abstract interface class for dynamics.
                
                Can inherit and provide the virtual methods:
                    - is_defined
                    - get_read_coordinate_subsets
                    - get_write_coordinate_subsets
                    - compute_contribution
                to create a custom dynamics class.
    
            
    """
    @staticmethod
    def from_environment(environment: ostk.physics.Environment) -> list[Dynamics]:
        """
                        Create a list of `Dynamics` objects from an environment.
        
                        Args:
                            environment (Environment): The environment to create the dynamics from.
        
                        Returns:
                            dynamics (list[Dynamics]): The list of `Dynamics` objects created from the environment.
        """
    def __init__(self, name: ostk.core.type.String) -> None:
        """
                        Construct a new `Dynamics` object.
        
                        Args:
                            name (str): The name of the dynamics.
        
                        Returns:
                            dynamics (Dynamics): The new `Dynamics` object.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_contribution(self, instant: ostk.physics.time.Instant, state_vector: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Compute the contribution of the dynamics at a given instant.
        
                        Args:
                            instant (Instant): The instant at which to compute the contribution.
                            state_vector (numpy.ndarray): The state vector at the instant.
                            frame (Frame): The reference frame in which to compute the contribution.
        
                        Returns:
                            contribution (numpy.ndarray): The contribution of the dynamics at the instant.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the name of the dynamics.
        
                        Returns:
                            name (str): The name of the dynamics.
        """
    def get_read_coordinate_subsets(self) -> list[trajectory.state.CoordinateSubset]:
        """
                        Get the coordinate subsets that the dynamics reads.
        
                        Returns:
                            read_coordinate_subsets (Array<CoordinateSubset>): The coordinate subsets that the dynamics reads.
        """
    def get_write_coordinate_subsets(self) -> list[trajectory.state.CoordinateSubset]:
        """
                        Get the coordinate subsets that the dynamics writes.
        
                        Returns:
                            write_coordinate_subsets (Array<CoordinateSubset>): The coordinate subsets that the dynamics writes.
        """
    def is_defined(self) -> bool:
        """
                        Check if the dynamics is defined.
        
                        Returns:
                            is_defined (bool): True if the dynamics is defined, False otherwise.
        """
class EventCondition:
    """
    
                    An Event Condition defines a criterion that can be evaluated based on a current/previous state vectors and times
    
                
    """
    class Target:
        """
        
                        The Event Condition Target.
        
                    
        """
        class Type:
            """
            
                            Event Condition Target type.
                        
            
            Members:
            
              Absolute : Absolute
            
              Relative : Relative to the provided State.
            """
            Absolute: typing.ClassVar[EventCondition.Target.Type]  # value = <Type.Absolute: 0>
            Relative: typing.ClassVar[EventCondition.Target.Type]  # value = <Type.Relative: 1>
            __members__: typing.ClassVar[dict[str, EventCondition.Target.Type]]  # value = {'Absolute': <Type.Absolute: 0>, 'Relative': <Type.Relative: 1>}
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
        __hash__: typing.ClassVar[None] = None
        @staticmethod
        def StringFromType(arg0: EventCondition.Target.Type) -> ostk.core.type.String:
            """
                                Enum as a string
            
                                Args:
                                    type (EventConditionTarget.Type): The type of the target.
            
                                Returns:
                                    string (str): Name of the enum as a string.
            """
        def __eq__(self, arg0: EventCondition.Target) -> bool:
            ...
        @typing.overload
        def __init__(self, value: ostk.core.type.Real, type: EventCondition.Target.Type = ...) -> None:
            """
                                Construct a new `EventConditionTarget` object.
            
                                Args:
                                    value (float): The value of the target.
                                    type (EventConditionTarget.Type): The type of the target. Defaults to EventConditionTarget.Type.Absolute.
            
                                Returns:
                                    event_condition_target (EventConditionTarget): The new `EventConditionTarget` object.
            """
        @typing.overload
        def __init__(self, value: ostk.physics.unit.Length, type: EventCondition.Target.Type = ...) -> None:
            """
                                Construct a new `EventConditionTarget` object.
            
                                Args:
                                    length (Length): The value of the target as a `Length`.
                                    type (EventConditionTarget.Type): The type of the target. Defaults to EventConditionTarget.Type.Absolute.
            
                                Returns:
                                    event_condition_target (EventConditionTarget): The new `EventConditionTarget` object.
            """
        @typing.overload
        def __init__(self, value: ostk.physics.unit.Angle, type: EventCondition.Target.Type = ...) -> None:
            """
                                Construct a new `EventConditionTarget` object.
            
                                Args:
                                    angle (Angle): The value of the target as an `Angle`.
                                    type (EventConditionTarget.Type): The type of the target. Defaults to EventConditionTarget.Type.Absolute.
            
                                Returns:
                                    event_condition_target (EventConditionTarget): The new `EventConditionTarget` object.
            """
        def __ne__(self, arg0: EventCondition.Target) -> bool:
            ...
        @property
        def type(self) -> EventCondition.Target.Type:
            """
                                The type of the target.
            
                                :type: Type
            """
        @property
        def value(self) -> ostk.core.type.Real:
            """
                                The value of the target.
            
                                :type: float
            """
        @property
        def value_offset(self) -> ostk.core.type.Real:
            """
                                The value offset of the target. Used for Relative targets.
            
                                :type: float
            """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, evaluator: typing.Callable[[trajectory.State], ostk.core.type.Real], target: EventCondition.Target) -> None:
        """
                            Construct a new `EventCondition` object.
        
                            Args:
                                name (str): The name of the event condition.
                                evaluator (callable): The evaluator that accepts a `State` and returns a float value.
                                target (EventConditionTarget): The target of the event condition.
        
                            Returns:
                                event_condition (EventCondition): The new `EventCondition` object.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, evaluator: typing.Callable[[trajectory.State], ostk.core.type.Real], target_value: ostk.core.type.Real) -> None:
        """
                            Construct a new `EventCondition` object.
        
                            Args:
                                name (str): The name of the event condition.
                                evaluator (callable): The evaluator that accepts a `State` and returns a float value.
                                target_value (float): The target of the event condition.
        
                            Returns:
                                event_condition (EventCondition): The new `EventCondition` object.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_evaluator(self) -> typing.Callable[[trajectory.State], ostk.core.type.Real]:
        """
                            Get the evaluator of the event condition.
        
                            Returns:
                               evaluator (str): The evaluator of the event condition.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                            Get the name of the event condition.
        
                            Returns:
                               name (str): The name of the event condition.
        """
    def get_target(self) -> EventCondition.Target:
        """
                            Get the target of the event condition.
        
                            Returns:
                               target (EventConditionTarget): The target of the event condition.
        """
    def is_satisfied(self, current_state: trajectory.State, previous_state: trajectory.State) -> bool:
        """
                            Check if the event condition is satisfied.
        
                            Args:
                                current_state (State): The current state.
                                previous_state (State): The previous state.
        
                            Returns:
                               is_satisfied (bool): True if the event condition is satisfied, False otherwise.
        """
    def update_target(self, state: trajectory.State) -> None:
        """
                            Update the target value if the event condition is relative.
        
                            Args:
                                state (State): The state to calculate the relative target from.
        """
class GuidanceLaw:
    """
    
                Guidance law base class.
    
                A guidance law is a mathematical model that computes the acceleration
                based on specific guidance law logic.
    
            
    """
    def __init__(self, name: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            name (str): The name of the guidance law.
        """
    def calculate_thrust_acceleration_at(self, instant: ostk.physics.time.Instant, position_coordinates: numpy.ndarray[numpy.float64[3, 1]], velocity_coordinates: numpy.ndarray[numpy.float64[3, 1]], thrust_acceleration: ostk.core.type.Real, output_frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Compute the acceleration.
        
                        Args:
                            instant (Instant): Instant of computation.
                            position_coordinates (np.array): Position coordinates.
                            velocity_coordinates (np.array): Velocity coordinates.
                            thrust_acceleration (float): Thrust acceleration magnitude.
                            output_frame (Frame): The frame the acceleration is expressed in.
        
                        Returns:
                            np.array: The acceleration.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the name of the guidance law.
        
                        Returns:
                            str: The name of the guidance law.
        """
class RootSolver:
    """
    
                    A root solver is an algorithm for finding a zero-crossing of a function.
    
                
    """
    class Solution:
        """
        
                    A root solver solution.
        
                
        """
        @property
        def has_converged(self) -> bool:
            """
                            Whether the root solver has converged.
            
                            Type:
                                bool
            """
        @has_converged.setter
        def has_converged(self, arg0: bool) -> None:
            ...
        @property
        def iteration_count(self) -> int:
            """
                            The number of iterations required to find the root.
            
                            Type:
                                int
            """
        @iteration_count.setter
        def iteration_count(self, arg0: int) -> None:
            ...
        @property
        def root(self) -> ostk.core.type.Real:
            """
                            The root of the function.
            
                            Type:
                                float
            """
        @root.setter
        def root(self, arg0: ostk.core.type.Real) -> None:
            ...
    @staticmethod
    def default() -> RootSolver:
        """
                            Return the default root solver.
        
                            Returns:
                                RootSolver: The default root solver.
        """
    def __init__(self, maximum_iteration_count: int, tolerance: ostk.core.type.Real) -> None:
        """
                            Constructor.
        
                            Args:
                                int: The maximum number of iterations allowed.
                                float: The tolerance of the root solver.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def bisection(self, function: typing.Callable[[float], float], lower_bound: ostk.core.type.Real, upper_bound: ostk.core.type.Real) -> RootSolver.Solution:
        """
                            Solve the root of a function using the bisection method.
        
                            Args:
                                function (callable): The function to solve.
                                lower_bound (float): The lower bound of the root.
                                upper_bound (float): The upper bound of the root.
        
                            Returns:
                                RootSolverSolution: The solution to the root.
        """
    def bracket_and_solve(self, function: typing.Callable[[float], float], initial_guess: ostk.core.type.Real, is_rising: bool) -> RootSolver.Solution:
        """
                            Bracket and solve the root of a function.
        
                            Args:
                                function (callable): The function to solve.
                                initial_guess (float): The initial guess for the root.
                                is_rising (bool): Whether the function is rising.
        
                            Returns:
                                RootSolverSolution: The solution to the root.
        """
    def get_maximum_iteration_count(self) -> int:
        """
                            Get the maximum number of iterations allowed.
        
                            Returns:
                                int: The maximum number of iterations allowed.
        """
    def get_tolerance(self) -> ostk.core.type.Real:
        """
                            Get the tolerance of the root solver.
        
                            Returns:
                                float: The tolerance of the root solver.
        """
    def solve(self, function: typing.Callable[[float], float], lower_bound: ostk.core.type.Real, upper_bound: ostk.core.type.Real) -> RootSolver.Solution:
        """
                            Solve the root of a function.
        
                            Args:
                                function (callable): The function to solve.
                                lower_bound (float): The lower bound of the root.
                                upper_bound (float): The upper bound of the root.
        
                            Returns:
                                RootSolverSolution: The solution to the root.
        """
class Trajectory:
    """
    
                Path followed by an object through space as a function of time.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    @typing.overload
    def ground_strip(start_lla: ostk.physics.coordinate.spherical.LLA, end_lla: ostk.physics.coordinate.spherical.LLA, ground_speed: ostk.physics.unit.Derived, start_instant: ostk.physics.time.Instant, celestial_object: ostk.physics.environment.object.Celestial = ..., step_size: ostk.physics.time.Duration = ...) -> Trajectory:
        """
                        Create a `Trajectory` object representing a ground strip.
                        Computes the duration as the geodetic distance / ground speed.
                        Instants are generated at a 1 second interval.
        
                        Args:
                            start_lla (LLA): The start LLA.
                            end_lla (LLA): The end LLA.
                            ground_speed (Derived): The ground speed.
                            start_instant (Instant): The start instant.
                            celestial_object (Celestial): The celestial object. Defaults to Earth.WGS84().
                            step_size (Duration): The step size. Defaults to 1 second.
        
                        Returns:
                            Trajectory: The `Trajectory` object representing the ground strip.
        """
    @staticmethod
    @typing.overload
    def ground_strip(start_lla: ostk.physics.coordinate.spherical.LLA, end_lla: ostk.physics.coordinate.spherical.LLA, instants: list[ostk.physics.time.Instant], celestial_object: ostk.physics.environment.object.Celestial = ...) -> Trajectory:
        """
                        Create a `Trajectory` object representing a ground strip.
                        This method computes the duration as the geodetic distance / ground speed.
        
                        Args:
                            start_lla (LLA): The start LLA.
                            end_lla (LLA): The end LLA.
                            instants (list[Instant]): The instants.
                            celestial_object (Celestial): The celestial object. Defaults to Earth.WGS84().
        
                        Returns:
                            Trajectory: The `Trajectory` object representing the ground strip.
        """
    @staticmethod
    def ground_strip_geodetic_nadir(orbit: typing.Any, instants: list[ostk.physics.time.Instant], celestial_object: ostk.physics.environment.object.Celestial = ...) -> Trajectory:
        """
                        Create a `Trajectory` object representing a ground strip that follows the geodetic nadir of the provided orbit.
        
                        Args:
                            orbit (Orbit): The orbit.
                            instants (list[Instant]): The instants.
                            celestial_object (Celestial): The celestial object. Defaults to Earth.WGS84().
        
                        Returns:
                            Trajectory: The `Trajectory` object representing the ground strip.
        """
    @staticmethod
    def position(position: ostk.physics.coordinate.Position) -> Trajectory:
        """
                        Create a `Trajectory` object representing a position.
        
                        Args:
                            position (Position): The position. Must be in the ITRF frame.
        
                        Returns:
                            Trajectory: The `Trajectory` object representing the position.
        """
    @staticmethod
    def undefined() -> Trajectory:
        """
                        Create an undefined `Trajectory` object.
        
                        Returns:
                            Trajectory: The undefined `Trajectory` object.
        """
    def __eq__(self, arg0: Trajectory) -> bool:
        ...
    @typing.overload
    def __init__(self, model: typing.Any) -> None:
        """
                        Construct a `Trajectory` object from a model.
        
                        Args:
                            model (trajectory.Model): The model of the trajectory.
        
                        Returns:
                            Trajectory: The `Trajectory` object.
        """
    @typing.overload
    def __init__(self, states: list[...]) -> None:
        """
                        Construct a `Trajectory` object from an array of states.
        
                        Args:
                            states (list[State]): The states of the trajectory.
        
                        Returns:
                            Trajectory: The `Trajectory` object.
        """
    def __ne__(self, arg0: Trajectory) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_model(self) -> ...:
        """
                        Access the model of the trajectory.
        
                        Returns:
                            Model: The model of the trajectory.
        """
    def get_state_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get the state of the trajectory at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            State: The state of the trajectory at the given instant.
        """
    def get_states_at(self, instants: list[ostk.physics.time.Instant]) -> list[...]:
        """
                        Get the states of the trajectory at a given set of instants. It can be more performant than looping `calculate_state_at` for multiple instants.
        
                        Args:
                            instants (list[Instant]): The instants.
        
                        Returns:
                            list[State]: The states of the trajectory at the given instants.
        """
    def is_defined(self) -> bool:
        """
                        Check if the trajectory is defined.
        
                        Returns:
                            bool: True if the trajectory is defined, False otherwise.
        """
