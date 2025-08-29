from __future__ import annotations
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.physics.time
import typing
from . import message
from . import model
__all__ = ['OrbitModel', 'Pass', 'message', 'model']
class OrbitModel:
    """
    
                Base class for orbit models.
    
                Provides the interface for orbit models.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: OrbitModel) -> bool:
        ...
    def __ne__(self, arg0: OrbitModel) -> bool:
        ...
    def __str__(self) -> str:
        ...
    def as_kepler(self) -> ...:
        """
                        Cast the orbit model to a Kepler model.
        
                        Returns:
                            Kepler: The Kepler model.
        """
    def as_propagated(self) -> ...:
        """
                        Cast the orbit model to a propagated model.
        
                        Returns:
                            Propagated: The propagated model.
        """
    def as_sgp4(self) -> ...:
        """
                        Cast the orbit model to an SGP4 model.
        
                        Returns:
                            SGP4: The SGP4 model.
        """
    def calculate_revolution_number_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Integer:
        """
                        Calculate the revolution number of the orbit model at a given instant.
        
                        Args:
                            instant (Instant): The instant at which to calculate the revolution number.
        
                        Returns:
                            int: The revolution number of the orbit model at the given instant.
        """
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Calculate the state of the orbit model at a given instant.
        
                        Args:
                            instant (Instant): The instant at which to calculate the state.
        
                        Returns:
                            State: The state of the orbit model at the given instant.
        """
    def get_epoch(self) -> ostk.physics.time.Instant:
        """
                        Get the epoch of the orbit model.
        
                        Returns:
                            Instant: The epoch of the orbit model.
        """
    def get_revolution_number_at_epoch(self) -> ostk.core.type.Integer:
        """
                        Get the revolution number at the epoch of the orbit model.
        
                        Returns:
                            int: The revolution number at the epoch of the orbit model.
        """
    def is_defined(self) -> bool:
        """
                        Check if the orbit model is defined.
        
                        Returns:
                            bool: True if the orbit model is defined, False otherwise.
        """
    def is_kepler(self) -> bool:
        """
                        Check if the orbit model is a Kepler model.
        
                        Returns:
                            bool: True if the orbit model is a Kepler model, False otherwise.
        """
    def is_propagated(self) -> bool:
        """
                        Check if the orbit model is a propagated model.
        
                        Returns:
                            bool: True if the orbit model is a propagated model, False otherwise.
        """
    def is_sgp4(self) -> bool:
        """
                        Check if the orbit model is an SGP4 model.
        
                        Returns:
                            bool: True if the orbit model is an SGP4 model, False otherwise.
        """
class Pass:
    """
    
                A revolution of an orbiting object.
    
            
    """
    class Phase:
        """
        
                    The phase of the `Pass`.
                
        
        Members:
        
          Undefined : Undefined
        
          Ascending : Ascending
        
          Descending : Descending
        """
        Ascending: typing.ClassVar[Pass.Phase]  # value = <Phase.Ascending: 1>
        Descending: typing.ClassVar[Pass.Phase]  # value = <Phase.Descending: 2>
        Undefined: typing.ClassVar[Pass.Phase]  # value = <Phase.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Pass.Phase]]  # value = {'Undefined': <Phase.Undefined: 0>, 'Ascending': <Phase.Ascending: 1>, 'Descending': <Phase.Descending: 2>}
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
    class Type:
        """
        
                    The type of `Pass`.
                
        
        Members:
        
          Undefined : Undefined
        
          Complete : Complete
        
          Partial : Partial
        """
        Complete: typing.ClassVar[Pass.Type]  # value = <Type.Complete: 1>
        Partial: typing.ClassVar[Pass.Type]  # value = <Type.Partial: 2>
        Undefined: typing.ClassVar[Pass.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Pass.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Complete': <Type.Complete: 1>, 'Partial': <Type.Partial: 2>}
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
    def string_from_phase(phase: Pass.Phase) -> ostk.core.type.String:
        """
                        Get the string representation of a pass phase.
        
                        Args:
                            phase (Pass.Phase): The pass phase.
        
                        Returns:
                            str: The string representation of the pass phase.
        """
    @staticmethod
    def string_from_type(type: Pass.Type) -> ostk.core.type.String:
        """
                        Get the string representation of a pass type.
        
                        Args:
                            type (Pass.Type): The pass type.
        
                        Returns:
                            str: The string representation of the pass type.
        """
    @staticmethod
    def undefined() -> Pass:
        """
                        Get an undefined pass.
        
                        Returns:
                            Pass: The undefined pass.
        """
    def __eq__(self, arg0: Pass) -> bool:
        ...
    def __init__(self, revolution_number: ostk.core.type.Integer, instant_at_ascending_node: ostk.physics.time.Instant, instant_at_north_point: ostk.physics.time.Instant, instant_at_descending_node: ostk.physics.time.Instant, instant_at_south_point: ostk.physics.time.Instant, instant_at_pass_break: ostk.physics.time.Instant) -> None:
        """
                        Constructor.
        
                        Args:
                            revolution_number (int): The revolution number of the pass.
                            instant_at_ascending_node (Instant): The instant at the ascending node of the pass.
                            instant_at_north_point (Instant): The instant at the north point of the pass.
                            instant_at_descending_node (Instant): The instant at the descending node of the pass.
                            instant_at_south_point (Instant): The instant at the south point of the pass.
                            instant_at_pass_break (Instant): The instant at break of the pass.
        """
    def __ne__(self, arg0: Pass) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_duration(self) -> ostk.physics.time.Duration:
        """
                        Get the duration of the pass. Undefined if the pass is not complete.
        
                        Returns:
                            Duration: The duration of the pass.
        """
    def get_end_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the end instant of the pass. For partial passes, this is the maximum defined instant.
        
                        Returns:
                            Instant: The end instant of the pass.
        """
    def get_instant_at_ascending_node(self) -> ostk.physics.time.Instant:
        """
                        Get the instant at the ascending node of the pass.
                        i.e. z = 0 & vz > 0 in an ECI frame.
        
                        Returns:
                            Instant: The instant at the ascending node of the pass.
        """
    def get_instant_at_descending_node(self) -> ostk.physics.time.Instant:
        """
                        Get the instant at the descending node of the pass.
                        i.e. z = 0 and vz < 0 in an ECI frame.
        
                        Returns:
                            Instant: The instant at the descending node of the pass.
        """
    def get_instant_at_north_point(self) -> ostk.physics.time.Instant:
        """
                        Get the instant at the north point of the pass.
                        i.e. z = maximum and vz = 0 in an ECI frame.
        
                        Returns:
                            Instant: The instant at the north point of the pass.
        """
    def get_instant_at_pass_break(self) -> ostk.physics.time.Instant:
        """
                        Get the instant at the break of the pass,
                        i.e. the ascending node of the next pass.
        
                        Returns:
                            Instant: The instant at the break of the pass.
        """
    def get_instant_at_south_point(self) -> ostk.physics.time.Instant:
        """
                        Get the instant at the south point of the pass.
                        i.e. z = minimum and vz = 0 in an ECI frame.
        
                        Returns:
                            Instant: The instant at the south point of the pass.
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        Get the interval of the pass. Undefined if the pass is not complete.
        
                        Returns:
                            Interval: The interval of the pass.
        """
    def get_revolution_number(self) -> ostk.core.type.Integer:
        """
                        Get the revolution number of the pass.
        
                        Returns:
                            int: The revolution number of the pass.
        """
    def get_start_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the start instant of the pass. For partial passes, this is the minimum defined instant.
        
                        Returns:
                            Instant: The start instant of the pass.
        """
    def get_type(self) -> Pass.Type:
        """
                        Get the type of the pass.
        
                        Returns:
                            Pass.Type: The type of the pass.
        """
    def is_complete(self) -> bool:
        """
                        Check if the pass is complete.
        
                        Returns:
                            bool: True if the pass is complete, False otherwise.
        """
    def is_defined(self) -> bool:
        """
                        Check if the pass is defined.
        
                        Returns:
                            bool: True if the pass is defined, False otherwise.
        """
