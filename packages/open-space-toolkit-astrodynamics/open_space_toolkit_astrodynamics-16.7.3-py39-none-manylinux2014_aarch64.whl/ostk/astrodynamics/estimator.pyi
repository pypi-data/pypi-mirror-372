from __future__ import annotations
import numpy
import ostk.astrodynamics.solver
import ostk.astrodynamics.trajectory
import ostk.astrodynamics.trajectory.orbit.model.sgp4
import ostk.astrodynamics.trajectory.state
import ostk.core.type
import ostk.physics
import ostk.physics.coordinate
import typing
__all__ = ['OrbitDeterminationSolver', 'TLESolver']
class OrbitDeterminationSolver:
    """
    
                Orbit Determination solver.
            
    """
    class Analysis:
        """
        
                    Analysis results from the Orbit Determination.
                
        """
        def __init__(self, estimated_state: ostk.astrodynamics.trajectory.State, solver_analysis: ostk.astrodynamics.solver.LeastSquaresSolver.Analysis) -> None:
            """
                            Construct a new Analysis object.
            
                            Args:
                                estimated_state (State): The estimated state. Matching the frame and expanded coordinates of the provided initial guess state.
                                solver_analysis (LeastSquaresSolver.Analysis): The solver analysis.
            """
        def __repr__(self) -> str:
            ...
        def __str__(self) -> str:
            ...
        @property
        def estimated_state(self) -> ostk.astrodynamics.trajectory.State:
            """
                            The estimated state.
            
                            :type: State
            """
        @property
        def solver_analysis(self) -> ostk.astrodynamics.solver.LeastSquaresSolver.Analysis:
            """
                            The solver analysis.
            
                            :type: LeastSquaresSolver.Analysis
            """
    def __init__(self, environment: ostk.physics.Environment = ..., numerical_solver: ostk.astrodynamics.trajectory.state.NumericalSolver = ..., solver: ostk.astrodynamics.solver.LeastSquaresSolver = ..., estimation_frame: ostk.physics.coordinate.Frame = ...) -> None:
        """
                        Construct a new OrbitDeterminationSolver object.
        
                        Args:
                            environment (Environment, optional): The environment. Defaults to Environment.default().
                            numerical_solver (NumericalSolver, optional): The numerical solver. Defaults to NumericalSolver.default().
                            solver (LeastSquaresSolver, optional): The Least Squares solver. Defaults to LeastSquaresSolver.default().
                            estimation_frame (Frame, optional): The estimation frame. Defaults to Frame.GCRF().
        """
    def access_environment(self) -> ostk.physics.Environment:
        """
                        Access the environment.
        
                        Returns:
                            Environment: The environment.
        """
    def access_estimation_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Access the estimation frame.
        
                        Returns:
                            Frame: The estimation frame.
        """
    def access_propagator(self) -> ostk.astrodynamics.trajectory.Propagator:
        """
                        Access the propagator.
        
                        Returns:
                            Propagator: The propagator.
        """
    def access_solver(self) -> ostk.astrodynamics.solver.LeastSquaresSolver:
        """
                        Access the solver.
        
                        Returns:
                            LeastSquaresSolver: The Least Squares solver.
        """
    def estimate(self, initial_guess: ostk.astrodynamics.trajectory.State, observations: list[ostk.astrodynamics.trajectory.State], estimation_coordinate_subsets: list[ostk.astrodynamics.trajectory.state.CoordinateSubset] = [], initial_guess_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}, observation_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}) -> OrbitDeterminationSolver.Analysis:
        """
                        Estimate state from observations.
        
                        Args:
                            initial_guess (State): Initial guess state.
                            observations (list[State]): Observations to fit against.
                            estimation_coordinate_subsets (list[CoordinateSubset], optional): Coordinate subsets to estimate. Defaults to empty list, in which case all the coordinate subsets from the initial guess state are estimated.
                            initial_guess_sigmas (dict[CoordinateSubset, VectorXd], optional): Initial guess sigmas.
                            observation_sigmas (dict[CoordinateSubset, VectorXd], optional): Observation sigmas.
        
                        Returns:
                            OrbitDeterminationSolverAnalysis: The analysis results.
        """
    def estimate_orbit(self, initial_guess: ostk.astrodynamics.trajectory.State, observations: list[ostk.astrodynamics.trajectory.State], estimation_coordinate_subsets: list[ostk.astrodynamics.trajectory.state.CoordinateSubset] = [], initial_guess_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}, observation_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}) -> ostk.astrodynamics.trajectory.Orbit:
        """
                        Estimate Propagated Orbit from observations.
        
                        Args:
                            initial_guess (State): Initial guess state.
                            observations (list[State]): Observations to fit against.
                            estimation_coordinate_subsets (list[CoordinateSubset], optional): Coordinate subsets to estimate. Defaults to empty list, in which case all the coordinate subsets from the initial guess state are estimated.
                            initial_guess_sigmas (dict[CoordinateSubset, VectorXd], optional): Initial guess sigmas. Defaults to empty, in which case
                            observation_sigmas (dict[CoordinateSubset, VectorXd], optional): Observation sigmas.
        
                        Returns:
                            Orbit: The estimated orbit.
        """
class TLESolver:
    """
    
                Solver for estimating TLE elements.
            
    """
    class Analysis:
        """
        
                    Analysis results from the TLE estimation solver.
                
        """
        def __init__(self, estimated_tle: ostk.astrodynamics.trajectory.orbit.model.sgp4.TLE, solver_analysis: ostk.astrodynamics.solver.LeastSquaresSolver.Analysis) -> None:
            """
                            Construct a new TLESolver::Analysis object.
            
                            Args:
                                estimated_tle (TLE): The estimated TLE.
                                solver_analysis (LeastSquaresSolver.Analysis): The solver analysis.
            """
        def __repr__(self) -> str:
            ...
        def __str__(self) -> str:
            ...
        @property
        def estimated_tle(self) -> ostk.astrodynamics.trajectory.orbit.model.sgp4.TLE:
            """
                            The estimated TLE.
            
                            :type: TLE
            """
        @property
        def solver_analysis(self) -> ostk.astrodynamics.solver.LeastSquaresSolver.Analysis:
            """
                            The solver analysis.
            
                            :type: LeastSquaresSolver.Analysis
            """
    def __init__(self, solver: ostk.astrodynamics.solver.LeastSquaresSolver = ..., satellite_number: ostk.core.type.Integer = 0, international_designator: ostk.core.type.String = '00001A', revolution_number: ostk.core.type.Integer = 0, estimate_b_star: bool = True, estimation_frame: ostk.physics.coordinate.Frame = ...) -> None:
        """
                        Construct a new TLESolver object.
        
                        Args:
                            solver (LeastSquaresSolver, optional): The solver to use. Defaults to LeastSquaresSolver.default().
                            satellite_number (int, optional): Satellite number for TLE. Defaults to 0.
                            international_designator (str, optional): International designator for TLE. Defaults to "00001A".
                            revolution_number (int, optional): Revolution number. Defaults to 0.
                            estimate_b_star (bool, optional): Whether to also estimate the B* parameter. Defaults to True.
                            estimation_frame (Frame, optional): Frame for estimation. Defaults to GCRF.
        """
    def access_default_b_star(self) -> ostk.core.type.Real:
        """
                        Access the default B* value.
        
                        Returns:
                            float: The default B* value.
        """
    def access_element_set_number(self) -> ostk.core.type.Integer:
        """
                        Access the element set number.
        
                        Returns:
                            int: The element set number.
        """
    def access_ephemeris_type(self) -> ostk.core.type.Integer:
        """
                        Access the ephemeris type.
        
                        Returns:
                            int: The ephemeris type.
        """
    def access_estimate_b_star(self) -> bool:
        """
                        Access whether to estimate B*.
        
                        Returns:
                            bool: whether to estimate B*.
        """
    def access_first_derivative_mean_motion_divided_by_2(self) -> ostk.core.type.Real:
        """
                        Access the first derivative of mean motion divided by 2.
        
                        Returns:
                            float: The first derivative of mean motion divided by 2.
        """
    def access_international_designator(self) -> ostk.core.type.String:
        """
                        Access the international designator.
        
                        Returns:
                            str: The international designator.
        """
    def access_revolution_number(self) -> ostk.core.type.Integer:
        """
                        Access the revolution number.
        
                        Returns:
                            int: The revolution number.
        """
    def access_satellite_number(self) -> ostk.core.type.Integer:
        """
                        Access the satellite number.
        
                        Returns:
                            int: The satellite number.
        """
    def access_second_derivative_mean_motion_divided_by_6(self) -> ostk.core.type.Real:
        """
                        Access the second derivative of mean motion divided by 6.
        
                        Returns:
                            float: The second derivative of mean motion divided by 6.
        """
    def access_solver(self) -> ostk.astrodynamics.solver.LeastSquaresSolver:
        """
                        Access the solver.
        
                        Returns:
                            LeastSquaresSolver: The Least Squares solver.
        """
    def access_tle_state_builder(self) -> ostk.astrodynamics.trajectory.StateBuilder:
        """
                        Access the TLE state builder.
        
                        Returns:
                            StateBuilder: The TLE state builder.
        """
    def estimate(self, initial_guess: typing.Any, observations: list[ostk.astrodynamics.trajectory.State], initial_guess_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}, observation_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}) -> TLESolver.Analysis:
        """
                        Estimate TLE from observations.
        
                        Args:
                            initial_guess (TLE | tuple[State, float] | State): Initial guess - can be a TLE, (cartesian State, B*) tuple, or cartesian State.
                            observations (list[State]): State observations to fit against.
                            initial_guess_sigmas (dict[CoordinateSubset, ndarray], optional): Initial guess sigmas.
                            observation_sigmas (dict[CoordinateSubset, ndarray], optional): Observation sigmas.
        
                        Returns:
                            TLESolver.Analysis: Analysis results containing the estimated TLE and solver analysis.
        """
    def estimate_orbit(self, initial_guess: typing.Any, observations: list[ostk.astrodynamics.trajectory.State], initial_guess_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}, observation_sigmas: dict[ostk.astrodynamics.trajectory.state.CoordinateSubset, numpy.ndarray[numpy.float64[m, 1]]] = {}) -> ostk.astrodynamics.trajectory.Orbit:
        """
                        Estimate an SGP4-based orbit from observations.
        
                        Args:
                            initial_guess (TLE | tuple[State, float] | State): Initial guess - can be a TLE, (cartesian State, B*) tuple, or cartesian State.
                            observations (list[State]): State observations to fit against.
                            initial_guess_sigmas (dict[CoordinateSubset, ndarray], optional): Initial guess sigmas.
                            observation_sigmas (dict[CoordinateSubset, ndarray], optional): Observation sigmas.
        
                        Returns:
                            Orbit: The estimated SGP4 orbit.
        """
