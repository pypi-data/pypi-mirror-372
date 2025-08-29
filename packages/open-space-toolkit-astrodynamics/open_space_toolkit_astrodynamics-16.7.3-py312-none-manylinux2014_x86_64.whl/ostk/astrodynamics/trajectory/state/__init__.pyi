from __future__ import annotations
import numpy
import ostk.astrodynamics
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.mathematics.solver
import ostk.physics.coordinate
import ostk.physics.time
import typing
from . import coordinate_subset
__all__ = ['CoordinateBroker', 'CoordinateSubset', 'NumericalSolver', 'coordinate_subset']
class CoordinateBroker:
    """
    
                Class to manage the coordinate subsets of a state.
            
            
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: CoordinateBroker) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        """
                        Default constructor.
        """
    @typing.overload
    def __init__(self, coordinate_subsets: list[...]) -> None:
        """
                        Create a broker for ther provided coordinate subsets.
        
                        Args:
                            list[CoordinateSubset]: The list of coordinate subsets.
        """
    def __ne__(self, arg0: CoordinateBroker) -> bool:
        ...
    def access_subsets(self) -> list[...]:
        """
                        Access the list of coordinate subsets.
        
                        Returns:
                            list[CoordinateSubset]: The list of coordinate subsets.
        """
    def add_subset(self, coordinate_subset: typing.Any) -> int:
        """
                        Add a coordinate subset.
        
                        Args:
                            coordinate_subset (CoordinateSubset): The coordinate subset to add.
        """
    def extract_coordinate(self, coordinates: numpy.ndarray[numpy.float64[m, 1]], coordinate_subset: typing.Any) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Extract the coordinates of a subset from a full coordinates vector.
        
                        Args:
                            coordinates (numpy.ndarray): The full coordinates vector.
                            coordinate_subset (CoordinateSubset): The coordinate subset.
        
                        Returns:
                            numpy.ndarray: The coordinates of the subset.
        """
    def extract_coordinates(self, coordinates: numpy.ndarray[numpy.float64[m, 1]], coordinate_subsets: list[...]) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Extract the coordinates of multiple subsets from a full coordinates vector.
        
                        Args:
                            coordinates (numpy.ndarray): The full coordinates vector.
                            coordinate_subsets (list[CoordinateSubset]): The coordinate subsets.
        
                        Returns:
                            numpy.ndarray: The coordinates of the subsets.
        """
    def get_number_of_coordinates(self) -> int:
        """
                        Get the total number of coordinates.
        
                        Returns:
                            int: The total number of coordinates.
        """
    def get_number_of_subsets(self) -> int:
        """
                        Get the number of coordinate subsets.
        
                        Returns:
                            int: The number of coordinate subsets.
        """
    def get_subsets(self) -> list[...]:
        """
                        Get the list of coordinate subsets.
        
                        Returns:
                            list[CoordinateSubset]: The list of coordinate subsets.
        """
    def has_subset(self, coordinate_subset: typing.Any) -> bool:
        """
                        Check if the coordinate broker has a given coordinate subset.
        
                        Args:
                            coordinate_subset (CoordinateSubset): The coordinate subset to check.
        
                        Returns:
                            bool: True if the coordinate broker has the coordinate subset, False otherwise.
        """
class CoordinateSubset:
    """
    
                State coordinate subset. It contains information related to a particular group of coordinates. It does not
                contain the coordinate values.
    
            
    """
    @staticmethod
    def ballistic_coefficient() -> CoordinateSubset:
        """
                        Get the ballistic coefficient coordinate subset.
        
                        Returns:
                            CoordinateSubset: The ballistic coefficient coordinate subset.
        """
    @staticmethod
    def drag_coefficient() -> CoordinateSubset:
        """
                        Get the drag coefficient coordinate subset.
        
                        Returns:
                            CoordinateSubset: The drag coefficient coordinate subset.
        """
    @staticmethod
    def mass() -> CoordinateSubset:
        """
                        Get the mass coordinate subset.
        
                        Returns:
                            CoordinateSubset: The mass coordinate subset.
        """
    @staticmethod
    def mass_flow_rate() -> CoordinateSubset:
        """
                        Get the mass flow rate coordinate subset.
        
                        Returns:
                            CoordinateSubset: The mass flow rate coordinate subset.
        """
    @staticmethod
    def surface_area() -> CoordinateSubset:
        """
                        Get the surface area coordinate subset.
        
                        Returns:
                            CoordinateSubset: The surface area coordinate subset.
        """
    def __eq__(self, arg0: CoordinateSubset) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, name: ostk.core.type.String, size: int) -> None:
        """
                        Constructor.
        
                        Args:
                            name (str): The name of the coordinate subset.
                            size (int): The size of the coordinate subset.
        """
    def __ne__(self, arg0: CoordinateSubset) -> bool:
        ...
    def add(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], another_coordinates: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame, coordinate_broker: CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Add the coordinates of another state to the coordinates of this state.
        
                        Args:
                            instant (Instant): The instant of the state.
                            coordinates (numpy.ndarray): The coordinates of this state.
                            another_coordinates (numpy.ndarray): The coordinates of the other state.
                            frame (Frame): The reference frame of the coordinates.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The sum of the coordinates.
        """
    def get_id(self) -> ostk.core.type.String:
        """
                        Get the identifier of the coordinate subset.
        
                        Returns:
                            str: The identifier of the coordinate subset.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the name of the coordinate subset.
        
                        Returns:
                            str: The name of the coordinate subset.
        """
    def get_size(self) -> int:
        """
                        Get the size of the coordinate subset.
        
                        Returns:
                            int: The size of the coordinate subset.
        """
    def in_frame(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], from_frame: ostk.physics.coordinate.Frame, to_frame: ostk.physics.coordinate.Frame, coordinate_broker: CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Convert the coordinates of this state from one frame to another.
        
                        Args:
                            instant (Instant): The instant of the state.
                            coordinates (numpy.ndarray): The coordinates of this state.
                            from_frame (Frame): The reference frame of the input coordinates.
                            to_frame (Frame): The reference frame of the output coordinates.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The coordinates in the output frame.
        """
    def subtract(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], another_coordinates: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame, coordinate_broker: CoordinateBroker) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Subtract the coordinates of another state from the coordinates of this state.
        
                        Args:
                            instant (Instant): The instant of the state.
                            coordinates (numpy.ndarray): The coordinates of this state.
                            another_coordinates (numpy.ndarray): The coordinates of the other state.
                            frame (Frame): The reference frame of the coordinates.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            numpy.ndarray: The difference of the coordinates.
        """
class NumericalSolver(ostk.mathematics.solver.NumericalSolver):
    """
    
                    A numerical solver is used to integrate the trajectory of a dynamical system.
    
                    The numerical solver can be used to integrate the trajectory of a dynamical system to a given instant,
                    or to a set of instants, or until an `Event Condition` is met.
    
                
    """
    class ConditionSolution:
        """
        
                    The solution to an event condition.
        
                
        """
        @property
        def condition_is_satisfied(self) -> bool:
            """
                            Whether the event condition is satisfied.
            
                            Type:
                                bool
            """
        @property
        def iteration_count(self) -> int:
            """
                            The number of iterations required to find the solution.
            
                            Type:
                                int
            """
        @property
        def root_solver_has_converged(self) -> bool:
            """
                            Whether the root solver has converged.
            
                            Type:
                                bool
            """
        @property
        def state(self) -> ostk.astrodynamics.trajectory.State:
            """
                            The state of the trajectory.
            
                            Type:
                                State
            """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def conditional(arg0: ostk.core.type.Real, arg1: ostk.core.type.Real, arg2: ostk.core.type.Real, arg3: typing.Callable[[ostk.astrodynamics.trajectory.State], None]) -> NumericalSolver:
        """
                            Return a conditional numerical solver.
        
                            Returns:
                                NumericalSolver: The conditional numerical solver.
        """
    @staticmethod
    def default() -> NumericalSolver:
        """
                            Return the default numerical solver.
        
                            Returns:
                                NumericalSolver: The default numerical solver.
        """
    @staticmethod
    def default_conditional(state_logger: typing.Callable[[ostk.astrodynamics.trajectory.State], None] = None) -> NumericalSolver:
        """
                            Return the default conditional numerical solver.
        
                            Args:
                                state_logger (StateLogger, optional): The state logger. Defaults to None.
        
                            Returns:
                                NumericalSolver: The default conditional numerical solver.
        """
    @staticmethod
    def fixed_step_size(stepper_type: ostk.mathematics.solver.NumericalSolver.StepperType, time_step: ostk.core.type.Real) -> NumericalSolver:
        """
                            Return a Numerical Solver using a fixed stepper.
        
                            Returns:
                                NumericalSolver: The numerical solver.
        """
    @staticmethod
    def undefined() -> NumericalSolver:
        """
                            Return an undefined numerical solver.
        
                            Returns:
                                NumericalSolver: The undefined numerical solver.
        """
    def __eq__(self, arg0: NumericalSolver) -> bool:
        ...
    def __init__(self, log_type: ostk.mathematics.solver.NumericalSolver.LogType, stepper_type: ostk.mathematics.solver.NumericalSolver.StepperType, time_step: ostk.core.type.Real, relative_tolerance: ostk.core.type.Real, absolute_tolerance: ostk.core.type.Real, root_solver: ostk.astrodynamics.RootSolver = ...) -> None:
        """
                            Constructor.
        
                            Args:
                                log_type (NumericalSolver.LogType): The type of logging.
                                stepper_type (NumericalSolver.StepperType): The type of stepper.
                                time_step (float): The time step.
                                relative_tolerance (float): The relative tolerance.
                                absolute_tolerance (float): The absolute tolerance.
                                root_solver (RootSolver, optional): The root solver. Defaults to RootSolver.Default().
        """
    def __ne__(self, arg0: NumericalSolver) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_observed_states(self) -> list[ostk.astrodynamics.trajectory.State]:
        """
                            Get the observed states.
        
                            Returns:
                                list[State]: The observed states.
        """
    def get_root_solver(self) -> ostk.astrodynamics.RootSolver:
        """
                            Get the root solver.
        
                            Returns:
                                RootSolver: The root solver.
        """
    @typing.overload
    def integrate_time(self, state: ostk.astrodynamics.trajectory.State, instant: ostk.physics.time.Instant, system_of_equations: typing.Any) -> ostk.astrodynamics.trajectory.State:
        """
                            Integrate the trajectory to a given instant.
        
                            Args:
                                state (State): The initial state of the trajectory.
                                instant (Instant): The instant to integrate to.
                                system_of_equations (callable): The system of equations.
        
                            Returns:
                               State: The state at the requested time.
        """
    @typing.overload
    def integrate_time(self, state: ostk.astrodynamics.trajectory.State, instants: list[ostk.physics.time.Instant], system_of_equations: typing.Any) -> list[ostk.astrodynamics.trajectory.State]:
        """
                            Integrate the trajectory to a set of instants.
        
                            Args:
                                state (State): The initial state of the trajectory.
                                instants (list[Instant]): The instants to integrate to.
                                system_of_equations (callable): The system of equations.
        
                            Returns:
                                list[State]: The states at the requested times.
        """
    @typing.overload
    def integrate_time(self, state: ostk.astrodynamics.trajectory.State, instant: ostk.physics.time.Instant, system_of_equations: typing.Any, event_condition: typing.Any) -> NumericalSolver.ConditionSolution:
        """
                            Integrate the trajectory to a given instant, with an event condition.
        
                            Args:
                                state (State): The initial state of the trajectory.
                                instant (Instant): The instant to integrate to.
                                system_of_equations (callable): The system of equations.
                                event_condition (EventCondition): The event condition.
        
                            Returns:
                                ConditionSolution: The solution to the event condition.
        """
    def is_defined(self) -> bool:
        """
                            Check if the numerical solver is defined.
        
                            Returns:
                                bool: True if the numerical solver is defined, False otherwise.
        """
