from __future__ import annotations
import ostk.astrodynamics
import ostk.core.type
import ostk.physics
import ostk.physics.environment.utility
import ostk.physics.time
import typing
__all__ = ['Generator']
class Generator:
    """
    
                An eclipse generator.            
            
    """
    @typing.overload
    def __init__(self, environment: ostk.physics.Environment = ..., search_step_size: ostk.physics.time.Duration = ..., search_tolerance: ostk.physics.time.Duration = ...) -> None:
        """
                        Constructor.
        
                        Args:
                            environment (Environment): The Environment to use during the search. Defaults to the Environment.default().
                            search_step_size (Duration): The step size to use during the search. Defaults to Duration.seconds(60.0).
                            search_tolerance (Duration): The tolerance to use during the search. Defaults to Duration.milliseconds(1.0).
        """
    @typing.overload
    def __init__(self) -> None:
        """
                        Default constructor with default parameters.
        """
    def generate(self, trajectory: ostk.astrodynamics.Trajectory, analysis_interval: ostk.physics.time.Interval, occulted_celestial_object_name: ostk.core.type.String = 'Sun', occulting_celestial_object_name: ostk.core.type.String = 'Earth') -> list[ostk.physics.environment.utility.Eclipse]:
        """
                        Generate eclipses for a given trajectory over the provided analysis interval.
        
                        Args:
                            trajectory (Trajectory): The trajectory to search for eclipses.
                            analysis_interval (Interval): The analysis interval.
                            occulted_celestial_object_name (str): The name of the occulted celestial object. Defaults to "Sun".
                            occulting_celestial_object_name (str): The name of the occulting celestial object. Defaults to "Earth".
        
                        Returns:
                            Array[Eclipse]: Array of eclipses found within the analysis interval.
        """
    def get_environment(self) -> ostk.physics.Environment:
        """
                        Get the environment.
        
                        Returns:
                            Environment: The environment used during the search.
        """
    def get_search_step_size(self) -> ostk.physics.time.Duration:
        """
                        Get the search step size.
        
                        Returns:
                            Duration: The step size used during the search.
        """
    def get_search_tolerance(self) -> ostk.physics.time.Duration:
        """
                        Get the search tolerance.
        
                        Returns:
                            Duration: The tolerance used during the search.
        """
    def is_defined(self) -> bool:
        """
                        Check if eclipse generator is defined.
        
                        Returns:
                            bool: True if eclipse generator is defined, False otherwise.
        """
