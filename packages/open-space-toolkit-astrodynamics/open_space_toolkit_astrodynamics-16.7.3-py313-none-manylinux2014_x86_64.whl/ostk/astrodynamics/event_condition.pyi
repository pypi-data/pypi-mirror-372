from __future__ import annotations
import ostk.astrodynamics
import ostk.astrodynamics.trajectory
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['AngularCondition', 'BooleanCondition', 'BrouwerLyddaneMeanLongCondition', 'COECondition', 'InstantCondition', 'LogicalCondition', 'RealCondition']
class AngularCondition(ostk.astrodynamics.EventCondition):
    """
    
                    An Angular Event Condition.
    
                
    """
    class Criterion:
        """
        
                        Angular condition criterion.
        
                    
        
        Members:
        
          PositiveCrossing
        
          NegativeCrossing
        
          AnyCrossing
        
          WithinRange
        """
        AnyCrossing: typing.ClassVar[AngularCondition.Criterion]  # value = <Criterion.AnyCrossing: 0>
        NegativeCrossing: typing.ClassVar[AngularCondition.Criterion]  # value = <Criterion.NegativeCrossing: 2>
        PositiveCrossing: typing.ClassVar[AngularCondition.Criterion]  # value = <Criterion.PositiveCrossing: 1>
        WithinRange: typing.ClassVar[AngularCondition.Criterion]  # value = <Criterion.WithinRange: 3>
        __members__: typing.ClassVar[dict[str, AngularCondition.Criterion]]  # value = {'PositiveCrossing': <Criterion.PositiveCrossing: 1>, 'NegativeCrossing': <Criterion.NegativeCrossing: 2>, 'AnyCrossing': <Criterion.AnyCrossing: 0>, 'WithinRange': <Criterion.WithinRange: 3>}
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
    @staticmethod
    def string_from_criterion(criterion: AngularCondition.Criterion) -> ostk.core.type.String:
        """
                            Get the string representation of a criterion.
        
                            Args:
                                criterion (ostk.astrodynamics.event_condition.AngularCondition.Criterion): The criterion.
        
                            Returns:
                                str: The string representation of the criterion.
        """
    @staticmethod
    def within_range(name: ostk.core.type.String, evaluator: typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.core.type.Real], target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle]) -> AngularCondition:
        """
                            Create an angular condition that is satisfied when the angle is within a range.
        
                            Args:
                                name (str): The name of the condition.
                                evaluator (function): The evaluator of the condition.
                                target_range (tuple): The target range of the condition.
        
                            Returns:
                                AngularCondition: The angular condition.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, criterion: AngularCondition.Criterion, evaluator: typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.core.type.Real], target_angle: ostk.physics.unit.Angle) -> None:
        """
                            Constructor.
        
                            Args:
                                name (str): The name of the condition.
                                criterion (ostk.astrodynamics.event_condition.AngularCondition.Criterion): The criterion of the condition.
                                evaluator (function): The evaluator of the condition.
                                target_angle (Angle): The target angle of the condition.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, criterion: AngularCondition.Criterion, evaluator: typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.core.type.Real], target: ostk.astrodynamics.EventCondition.Target) -> None:
        """
                            Constructor.
        
                            Args:
                                name (str): The name of the condition.
                                criterion (ostk.astrodynamics.event_condition.AngularCondition.Criterion): The criterion of the condition.
                                evaluator (function): The evaluator of the condition.
                                target (EventConditionTarget): The target of the condition.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_criterion(self) -> AngularCondition.Criterion:
        """
                            Get the criterion of the condition.
        
                            Returns:
                                ostk.astrodynamics.event_condition.AngularCondition.Criterion: The criterion of the condition.
        """
    def get_target_angle(self) -> ostk.physics.unit.Angle:
        """
                            Get the target angle of the condition.
        
                            Returns:
                                Angle: The target angle of the condition.
        """
    def get_target_range(self) -> tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle]:
        """
                            Get the target range of the condition.
        
                            Returns:
                                tuple: The target range of the condition.
        """
    def is_satisfied(self, current_state: ostk.astrodynamics.trajectory.State, previous_state: ostk.astrodynamics.trajectory.State) -> bool:
        """
                            Check if the condition is satisfied.
        
                            Args:
                                current_state (State): The current state.
                                previous_state (State): The previous state.
        
                            Returns:
                                bool: True if the condition is satisfied, False otherwise.
        """
class BooleanCondition(RealCondition):
    """
    
                A Boolean Event Condition.
    
            
    """
    def __init__(self, name: ostk.core.type.String, criterion: RealCondition.Criterion, evaluator: typing.Callable[[ostk.astrodynamics.trajectory.State], bool], is_inverse: bool) -> None:
        """
                        Constructor.
        
                        Args:
                            name (str): The name of the condition.
                            criterion (Criterion): The criterion of the condition.
                            evaluator (function): The evaluator of the condition.
                            is_inverse (bool): Whether the condition is inverse.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def evaluate(self, state: ostk.astrodynamics.trajectory.State) -> ostk.core.type.Real:
        """
                        Evaluate the condition.
        
                        Args:
                            state (State): The state.
        
                        Returns:
                            bool: True if the condition is satisfied, False otherwise.
        """
    def is_inversed(self) -> bool:
        """
                        Check if the condition is inverse.
        
                        Returns:
                            bool: True if the condition is inverse, False otherwise.
        """
    def is_satisfied(self, current_state: ostk.astrodynamics.trajectory.State, previous_state: ostk.astrodynamics.trajectory.State) -> bool:
        """
                        Check if the condition is satisfied.
        
                        Args:
                            current_state (State): The current state.
                            previous_state (State): The previous state.
        
                        Returns:
                            bool: True if the condition is satisfied, False otherwise.
        """
class BrouwerLyddaneMeanLongCondition:
    """
    
                    A Brouwer-Lyddane Mean Long Event Condition.
    
                
    """
    @staticmethod
    @typing.overload
    def aop(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, aop: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the argument of perigee.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                aop (EventConditionTarget): The argument of perigee.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def aop(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the argument of perigee being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def argument_of_latitude(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, argument_of_latitude: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the argument of latitude.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                argument_of_latitude (EventConditionTarget): The argument of latitude.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def argument_of_latitude(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the argument of latitude being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def eccentric_anomaly(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, eccentric_anomaly: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the eccentric anomaly.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                eccentric_anomaly (EventConditionTarget): The eccentric anomaly.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def eccentric_anomaly(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the eccentric anomaly being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    def eccentricity(criterion: RealCondition.Criterion, frame: ostk.physics.coordinate.Frame, eccentricity: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> RealCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the eccentricity.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                eccentricity (EventConditionTarget): The eccentricity.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def inclination(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, inclination: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the inclination.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                inclination (EventConditionTarget): The inclination.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def inclination(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the inclination being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def mean_anomaly(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, mean_anomaly: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the mean anomaly.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                mean_anomaly (EventConditionTarget): The mean anomaly.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def mean_anomaly(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the mean anomaly being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def raan(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, raan: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the right ascension of the ascending node.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                raan (EventConditionTarget): The right ascension of the ascending node.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def raan(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the right ascension of the ascending node being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    def semi_major_axis(criterion: RealCondition.Criterion, frame: ostk.physics.coordinate.Frame, semi_major_axis: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> RealCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the semi-major axis.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                semi_major_axis (EventConditionTarget): The semi-major axis.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def true_anomaly(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, true_anomaly: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the true anomaly.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                true_anomaly (EventConditionTarget): The true anomaly.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
    @staticmethod
    @typing.overload
    def true_anomaly(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a Brouwer-Lyddane Mean Long condition based on the true anomaly being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                BrouwerLyddaneMeanLongCondition: The Brouwer-Lyddane Mean Long condition.
        """
class COECondition:
    """
    
                    A COE Event Condition.
    
                
    """
    @staticmethod
    @typing.overload
    def aop(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, aop: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the argument of perigee.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                aop (EventConditionTarget): The argument of perigee.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def aop(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the argument of perigee being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def argument_of_latitude(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, argument_of_latitude: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the argument of latitude.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                argument_of_latitude (EventConditionTarget): The argument of latitude.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def argument_of_latitude(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the argument of latitude being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def eccentric_anomaly(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, eccentric_anomaly: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the eccentric anomaly.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                eccentric_anomaly (EventConditionTarget): The eccentric anomaly.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def eccentric_anomaly(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the eccentric anomaly being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    def eccentricity(criterion: RealCondition.Criterion, frame: ostk.physics.coordinate.Frame, eccentricity: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> RealCondition:
        """
                            Create a COE condition based on the eccentricity.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                eccentricity (EventConditionTarget): The eccentricity.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def inclination(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, inclination: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the inclination.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                inclination (EventConditionTarget): The inclination.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def inclination(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the inclination being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def mean_anomaly(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, mean_anomaly: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the mean anomaly.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                mean_anomaly (EventConditionTarget): The mean anomaly.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def mean_anomaly(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the mean anomaly being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def raan(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, raan: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the right ascension of the ascending node.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                raan (EventConditionTarget): The right ascension of the ascending node.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def raan(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the right ascension of the ascending node being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    def semi_major_axis(criterion: RealCondition.Criterion, frame: ostk.physics.coordinate.Frame, semi_major_axis: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> RealCondition:
        """
                            Create a COE condition based on the semi-major axis.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                semi_major_axis (EventConditionTarget): The semi-major axis.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def true_anomaly(criterion: AngularCondition.Criterion, frame: ostk.physics.coordinate.Frame, true_anomaly: ostk.astrodynamics.EventCondition.Target, gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the true anomaly.
        
                            Args:
                                criterion (Criterion): The criterion.
                                frame (Frame): The reference frame.
                                true_anomaly (EventConditionTarget): The true anomaly.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
    @staticmethod
    @typing.overload
    def true_anomaly(frame: ostk.physics.coordinate.Frame, target_range: tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle], gravitational_parameter: ostk.physics.unit.Derived) -> AngularCondition:
        """
                            Create a COE condition based on the true anomaly being within a range.
        
                            Args:
                                frame (Frame): The reference frame.
                                target_range (tuple[Angle, Angle]): A tuple of two angles defining the range.
                                gravitational_parameter (Derived): The gravitational parameter.
        
                            Returns:
                                COECondition: The COE condition.
        """
class InstantCondition(RealCondition):
    """
    
                    An Instant Event Condition.
    
                
    """
    def __init__(self, criterion: RealCondition.Criterion, instant: ostk.physics.time.Instant) -> None:
        """
                            Constructor.
        
                            Args:
                                criterion (Criterion): The criterion.
                                instant (Instant): The instant.
        """
    def get_instant(self) -> ostk.physics.time.Instant:
        """
                            Get the instant.
        
                            Returns:
                                Instant: The instant.
        """
class LogicalCondition(ostk.astrodynamics.EventCondition):
    """
    
                    A Logical Event Condition. This class is used to combine multiple event conditions into a single set.
    
                
    """
    class Type:
        """
        
                        Logical Condition Type.
                            - Disjunctive (Or)
                            - Conjucntive (And)
                    
        
        Members:
        
          And : And
        
          Or : Or
        """
        And: typing.ClassVar[LogicalCondition.Type]  # value = <Type.And: 0>
        Or: typing.ClassVar[LogicalCondition.Type]  # value = <Type.Or: 1>
        __members__: typing.ClassVar[dict[str, LogicalCondition.Type]]  # value = {'And': <Type.And: 0>, 'Or': <Type.Or: 1>}
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
    def __init__(self, name: ostk.core.type.String, type: LogicalCondition.Type, event_conditions: list[ostk.astrodynamics.EventCondition]) -> None:
        """
                            Constructor.
        
                            Args:
                                name (str): The name of the condition.
                                type (Type): The type of the logical condition.
                                event_conditions (list[EventCondition]): The list of event conditions.
        """
    def get_event_conditions(self) -> list[ostk.astrodynamics.EventCondition]:
        """
                            Get the list of event conditions.
        
                            Returns:
                                list[EventCondition]: The list of event conditions.
        """
    def get_type(self) -> LogicalCondition.Type:
        """
                            Get the type of the logical condition.
        
                            Returns:
                                Type: The type of the logical condition.
        """
class RealCondition(ostk.astrodynamics.EventCondition):
    """
    
                    A Real Event Condition.
    
                
    """
    class Criterion:
        """
        
                        The Criterion that defines how the condition is satisfied.
                    
        
        Members:
        
          PositiveCrossing : The positive crossing criterion
        
          NegativeCrossing : The negative crossing criterion
        
          AnyCrossing : The any crossing criterion
        
          StrictlyPositive : The strictly positive criterion
        
          StrictlyNegative : The strictly negative criterion
        """
        AnyCrossing: typing.ClassVar[RealCondition.Criterion]  # value = <Criterion.AnyCrossing: 2>
        NegativeCrossing: typing.ClassVar[RealCondition.Criterion]  # value = <Criterion.NegativeCrossing: 1>
        PositiveCrossing: typing.ClassVar[RealCondition.Criterion]  # value = <Criterion.PositiveCrossing: 0>
        StrictlyNegative: typing.ClassVar[RealCondition.Criterion]  # value = <Criterion.StrictlyNegative: 4>
        StrictlyPositive: typing.ClassVar[RealCondition.Criterion]  # value = <Criterion.StrictlyPositive: 3>
        __members__: typing.ClassVar[dict[str, RealCondition.Criterion]]  # value = {'PositiveCrossing': <Criterion.PositiveCrossing: 0>, 'NegativeCrossing': <Criterion.NegativeCrossing: 1>, 'AnyCrossing': <Criterion.AnyCrossing: 2>, 'StrictlyPositive': <Criterion.StrictlyPositive: 3>, 'StrictlyNegative': <Criterion.StrictlyNegative: 4>}
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
    @staticmethod
    def duration_condition(criterion: RealCondition.Criterion, duration: ostk.physics.time.Duration) -> RealCondition:
        """
                            Generate a duration condition.
        
                            Args:
                                criterion (Criterion): The criterion of the condition.
                                duration (Duration): Duration target.
        
                            Returns:
                                RealCondition: The duration condition.
        """
    @staticmethod
    def string_from_criterion(criterion: RealCondition.Criterion) -> ostk.core.type.String:
        """
                            Get the string representation of a criterion.
        
                            Args:
                                criterion (Criterion): The criterion.
        
                            Returns:
                                str: The string representation.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, criterion: RealCondition.Criterion, evaluator: typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.core.type.Real], target_value: ostk.core.type.Real = 0.0) -> None:
        """
                            Constructor.
        
                            Args:
                                name (str): The name of the condition.
                                criterion (Criterion): The criterion of the condition.
                                evaluator (function): The evaluator of the condition.
                                target_value (float): The target value of the condition.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, criterion: RealCondition.Criterion, evaluator: typing.Callable[[ostk.astrodynamics.trajectory.State], ostk.core.type.Real], target: ostk.astrodynamics.EventCondition.Target) -> None:
        """
                            Constructor.
        
                            Args:
                                name (str): The name of the condition.
                                criterion (Criterion): The criterion of the condition.
                                evaluator (function): The evaluator of the condition.
                                target (EventConditionTarget): The target of the condition.
        """
    def __repr__(self) -> str:
        """
                            Return a string representation of the real condition.
        
                            Returns:
                                str: The string representation.
        """
    def __str__(self) -> str:
        """
                            Return a string representation of the real condition.
        
                            Returns:
                                str: The string representation.
        """
    def evaluate(self, state: ostk.astrodynamics.trajectory.State) -> ostk.core.type.Real:
        """
                            Evaluate the condition.
        
                            Args:
                                state (State): The state.
        
                            Returns:
                                bool: True if the condition is satisfied, False otherwise.
        """
    def get_criterion(self) -> RealCondition.Criterion:
        """
                            Get the criterion of the condition.
        
                            Returns:
                                Criterion: The criterion.
        """
    def is_satisfied(self, current_state: ostk.astrodynamics.trajectory.State, previous_state: ostk.astrodynamics.trajectory.State) -> bool:
        """
                            Check if the condition is satisfied.
        
                            Args:
                                current_state (State): The current state.
                                previous_state (State): The previous state.
        
                            Returns:
                                bool: True if the condition is satisfied, False otherwise.
        """
