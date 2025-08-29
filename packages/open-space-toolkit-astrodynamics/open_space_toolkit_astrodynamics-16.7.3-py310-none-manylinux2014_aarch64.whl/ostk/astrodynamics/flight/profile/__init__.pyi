from __future__ import annotations
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.time
import typing
from . import model
__all__ = ['Model', 'model']
class Model:
    """
    
                A flight profile model.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Model) -> bool:
        ...
    def __ne__(self, arg0: Model) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def as_tabulated(self) -> ...:
        """
                        Cast the model to a tabulated model.
        
                        Returns:
                            Tabulated: The tabulated model.
        """
    def as_transform(self) -> ...:
        """
                        Cast the model to a transform model.
        
                        Returns:
                            Transform: The transform model.
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
                        Calculate the states of the model at specific instants. It can be more performant than looping `calculate_state_at` for multiple instants.
        
                        Args:
                            instants (list[Instant]): The instants at which to calculate the states.
        
                        Returns:
                            list[State]: The states of the model at the specified instants.
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
    def is_tabulated(self) -> bool:
        """
                        Check if the model is a tabulated model.
        
                        Returns:
                            bool: True if the model is a tabulated model, False otherwise.
        """
    def is_transform(self) -> bool:
        """
                        Check if the model is a transform model.
        
                        Returns:
                            bool: True if the model is a transform model, False otherwise.
        """
