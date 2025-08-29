from __future__ import annotations
import numpy
import ostk.astrodynamics
import ostk.core.type
import ostk.mathematics.curve_fitting
import ostk.mathematics.geometry.d3.transformation.rotation
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.environment.object
import ostk.physics.time
import ostk.physics.unit
import typing
from . import model
from . import orbit
from . import state
__all__ = ['LocalOrbitalFrameDirection', 'LocalOrbitalFrameFactory', 'LocalOrbitalFrameTransformProvider', 'Model', 'Orbit', 'Propagator', 'Segment', 'Sequence', 'State', 'StateBuilder', 'model', 'orbit', 'state']
class LocalOrbitalFrameDirection:
    """
    
                A local orbital frame direction.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> LocalOrbitalFrameDirection:
        """
                        Get an undefined local orbital frame direction.
        
                        Returns:
                            LocalOrbitalFrameDirection: The undefined local orbital frame direction.
        """
    def __eq__(self, arg0: LocalOrbitalFrameDirection) -> bool:
        ...
    def __init__(self, vector: numpy.ndarray[numpy.float64[3, 1]], local_orbital_frame_factory: LocalOrbitalFrameFactory) -> None:
        """
                        Construct a new `LocalOrbitalFrameDirection` object.
        
                        Args:
                            vector (numpy.ndarray): The vector expressed in the local orbital frame.
                            local_orbital_frame_factory (LocalOrbitalFrameFactory): The local orbital frame factory that defines the frame.
        
                        Returns:
                            LocalOrbitalFrameDirection: The new `LocalOrbitalFrameDirection` object.
        """
    def __ne__(self, arg0: LocalOrbitalFrameDirection) -> bool:
        ...
    def get_local_orbital_frame_factory(self) -> LocalOrbitalFrameFactory:
        """
                        Get the local orbital frame factory that defines the frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The local orbital frame factory that defines the frame.
        """
    def get_value(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the vector expressed in the local orbital frame.
        
                        Returns:
                            Vector3d: The vector expressed in the local orbital frame.
        """
    def is_defined(self) -> bool:
        """
                        Check if the local orbital frame direction is defined.
        
                        Returns:
                            bool: True if the local orbital frame direction is defined, False otherwise.
        """
class LocalOrbitalFrameFactory:
    """
    
                The local orbital frame factory.
    
            
    """
    @staticmethod
    def LVLH(parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Get a Local Vertical Local Horizontal (LVLH) local orbital frame factory.
        
                        Args:
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The LVLH local orbital frame factory.
        """
    @staticmethod
    def NED(parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Get a North-East-Down (NED) local orbital frame factory.
        
                        Args:
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The NED local orbital frame factory.
        """
    @staticmethod
    def QSW(parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Get a Quasi-Satellite World (QSW) local orbital frame factory.
        
                        Args:
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The QSW local orbital frame factory.
        """
    @staticmethod
    def TNW(parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Get a Tangent-Normal-Wideband (TNW) local orbital frame factory.
        
                        Args:
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The TNW local orbital frame factory.
        """
    @staticmethod
    def VNC(parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Get a Velocity-Normal-Co-normal (VNC) local orbital frame factory.
        
                        Args:
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The VNC local orbital frame factory.
        """
    @staticmethod
    def VVLH(parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Get a Velocity Local Vertical Local Horizontal (VVLH) local orbital frame factory.
        
                        Args:
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The VVLH local orbital frame factory.
        """
    @staticmethod
    @typing.overload
    def construct(type: LocalOrbitalFrameTransformProvider.Type, parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Construct a local orbital frame factory for the provided type.
        
                        Args:
                            type (LocalOrbitalFrameTransformProvider.Type): The type of local orbital frame transform provider.
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The local orbital frame factory.
        """
    @staticmethod
    @typing.overload
    def construct(transform_generator: typing.Callable[[...], ostk.physics.coordinate.Transform], parent_frame: ostk.physics.coordinate.Frame) -> LocalOrbitalFrameFactory:
        """
                        Construct a local orbital frame factory for a custom type, using the provided transform generator.
        
                        Args:
                            transform_generator (callable[[State], Transform]): The transform generator.
                            parent_frame (Frame): The parent frame.
        
                        Returns:
                            LocalOrbitalFrameFactory: The local orbital frame factory.
        """
    @staticmethod
    def undefined() -> LocalOrbitalFrameFactory:
        """
                        Get an undefined local orbital frame factory.
        
                        Returns:
                            LocalOrbitalFrameFactory: The undefined local orbital frame factory.
        """
    def access_parent_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Get the parent frame.
        
                        Returns:
                            Frame: The parent frame.
        """
    def generate_frame(self, state: typing.Any) -> ostk.physics.coordinate.Frame:
        """
                        Generate a local orbital frame.
        
                        Args:
                            state (State): The state.
        
                        Returns:
                            Frame: The local orbital frame.
        """
    def get_provider_type(self) -> LocalOrbitalFrameTransformProvider.Type:
        """
                        Get the provider type.
        
                        Returns:
                            LocalOrbitalFrameTransformProvider.Type: The provider type.
        """
    def is_defined(self) -> bool:
        """
                        Check if the local orbital frame factory is defined.
        
                        Returns:
                            Frame: True if the local orbital frame factory is defined, False otherwise.
        """
class LocalOrbitalFrameTransformProvider:
    """
    
                    Local orbital frame transform provider, frame provider.
                    Generates a specific transform based on a State (instant, position, velocity) and a LOF type.
    
                
    """
    class Type:
        """
        
                    The local orbital frame type.
                
        
        Members:
        
          Undefined : Undefined
        
          NED : North-East-Down
        
          LVLH : Local Vertical-Local Horizontal
        
          LVLHGD : Local Vertical-Local Horizontal Geodetic
        
          VVLH : Vertical-Local Horizontal
        
          QSW : Quasi-Satellite West
        
          TNW : Tangent-Normal-Wideband
        
          VNC : Velocity-Normal-Conormal
        """
        LVLH: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.LVLH: 2>
        LVLHGD: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.LVLHGD: 4>
        NED: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.NED: 1>
        QSW: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.QSW: 5>
        TNW: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.TNW: 6>
        Undefined: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.Undefined: 0>
        VNC: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.VNC: 7>
        VVLH: typing.ClassVar[LocalOrbitalFrameTransformProvider.Type]  # value = <Type.VVLH: 3>
        __members__: typing.ClassVar[dict[str, LocalOrbitalFrameTransformProvider.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'NED': <Type.NED: 1>, 'LVLH': <Type.LVLH: 2>, 'LVLHGD': <Type.LVLHGD: 4>, 'VVLH': <Type.VVLH: 3>, 'QSW': <Type.QSW: 5>, 'TNW': <Type.TNW: 6>, 'VNC': <Type.VNC: 7>}
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
    def construct(type: LocalOrbitalFrameTransformProvider.Type, state: typing.Any) -> LocalOrbitalFrameTransformProvider:
        """
                        Constructs a local orbital frame transform provider for the provided type.
        
                        Args:
                            type (LocalOrbitalFrameTransformProvider.Type): The local orbital frame provider type.
                            state (State): The state.
        
                        Returns:
                            LocalOrbitalFrameTransformProvider: The provider.
        """
    @staticmethod
    def get_transform_generator(type: LocalOrbitalFrameTransformProvider.Type) -> typing.Callable[[...], ostk.physics.coordinate.Transform]:
        """
                        Returns the transform generator function for a given type.
        
                        Args:
                            type (LocalOrbitalFrameTransformProvider.Type): The local orbital frame provider type.
        
                        Returns:
                            callable[[State], Transform]: The transform generator function.
        """
    def __init__(self, transform: ostk.physics.coordinate.Transform) -> None:
        """
                        Constructs a local orbital frame transform provider.
        
                        Args:
                            transform (Transform): The transform.
        
                        Returns:
                            LocalOrbitalFrameTransformProvider: The provider.
        """
    def get_transform_at(self, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Transform:
        """
                        Returns the transform at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            Transform: The transform at the given instant.
        """
    def is_defined(self) -> bool:
        """
                        Returns true if the provider is defined.
        
                        Returns:
                            bool: True if the provider is defined.
        """
class Model:
    """
    
                Trajectory model.
    
            
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
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> State:
        """
                        Calculate the state at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            State: The state at the given instant.
        """
    def calculate_states_at(self, instants: list[ostk.physics.time.Instant]) -> list[State]:
        """
                        Calculate the states at given instants. It can be more performant than looping `calculate_state_at` for multiple instants.
        
                        @param instants The instants.
        
                        Returns:
                            Array<State>: The states at the given instants.
        """
    def is_defined(self) -> bool:
        """
                        Check if the model is defined.
        
                        Returns:
                            bool: True if the model is defined, False otherwise.
        """
class Orbit(ostk.astrodynamics.Trajectory):
    """
    
                    Gravitationally curved trajectory of an object.
    
                
    """
    class FrameType:
        """
        
                        The local orbital frame type.
                    
        
        Members:
        
          Undefined : Undefined
        
          NED : North-East-Down
        
          LVLH : Local Vertical-Local Horizontal
        
          LVLHGD : Local Vertical-Local Horizontal GeoDetic
        
          LVLHGDGT : Local Vertical-Local Horizontal GeoDetic Ground Track
        
          VVLH : Vertical-Local Horizontal
        
          QSW : Quasi-Satellite West
        
          TNW : Tangent-Normal-Wideband
        
          VNC : Velocity-Normal-Conormal
        """
        LVLH: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.LVLH: 2>
        LVLHGD: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.LVLHGD: 4>
        LVLHGDGT: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.LVLHGDGT: 5>
        NED: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.NED: 1>
        QSW: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.QSW: 6>
        TNW: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.TNW: 7>
        Undefined: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.Undefined: 0>
        VNC: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.VNC: 8>
        VVLH: typing.ClassVar[Orbit.FrameType]  # value = <FrameType.VVLH: 3>
        __members__: typing.ClassVar[dict[str, Orbit.FrameType]]  # value = {'Undefined': <FrameType.Undefined: 0>, 'NED': <FrameType.NED: 1>, 'LVLH': <FrameType.LVLH: 2>, 'LVLHGD': <FrameType.LVLHGD: 4>, 'LVLHGDGT': <FrameType.LVLHGDGT: 5>, 'VVLH': <FrameType.VVLH: 3>, 'QSW': <FrameType.QSW: 6>, 'TNW': <FrameType.TNW: 7>, 'VNC': <FrameType.VNC: 8>}
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
    def circular(epoch: ostk.physics.time.Instant, altitude: ostk.physics.unit.Length, inclination: ostk.physics.unit.Angle, celestial_object: ostk.physics.environment.object.Celestial) -> Orbit:
        """
                            Create a circular `Orbit` object.
        
                            Args:
                                epoch (Instant): The epoch.
                                altitude (Length): The altitude (wrt. equatorial radius).
                                inclination (Angle): The inclination.
                                celestial_object (Celestial): The celestial object.
        
                            Returns:
                                Orbit: The circular `Orbit` object.
        """
    @staticmethod
    def circular_equatorial(epoch: ostk.physics.time.Instant, altitude: ostk.physics.unit.Length, celestial_object: ostk.physics.environment.object.Celestial) -> Orbit:
        """
                            Create a circular equatorial `Orbit` object.
        
                            Args:
                                epoch (Instant): The epoch.
                                altitude (Length): The altitude (wrt. equatorial radius).
                                celestial_object (Celestial): The celestial object.
        
                            Returns:
                                Orbit: The circular equatorial `Orbit` object.
        """
    @staticmethod
    def compute_passes(states: list[State], initial_revolution_number: ostk.core.type.Integer) -> list[tuple[int, ...]]:
        """
                            Compute passes from a set of states.
        
                            Args:
                                states (Array<State>): The states.
                                initial_revolution_number (Integer): The initial revolution number.
        
                            Returns:
                                list[tuple[int, Pass]]: List of index-pass pairs.
        """
    @staticmethod
    def compute_passes_with_model(model: typing.Any, start_instant: ostk.physics.time.Instant, end_instant: ostk.physics.time.Instant, initial_revolution_number: ostk.core.type.Integer) -> list[...]:
        """
                            Compute passes with the given model for the provided interval.
        
                            Args:
                                model (orbit.Model): The model.
                                start_instant (Instant): The start instant.
                                end_instant (Instant): The end instant.
                                initial_revolution_number (int): The initial revolution number.
        
                            Returns:
                                list[Pass]: List of passes.
        """
    @staticmethod
    def equatorial(epoch: ostk.physics.time.Instant, apoapsis_altitude: ostk.physics.unit.Length, periapsis_altitude: ostk.physics.unit.Length, celestial_object: ostk.physics.environment.object.Celestial) -> Orbit:
        """
                            Create an equatorial `Orbit` object.
        
                            Args:
                                epoch (Instant): The epoch.
                                apoapsis_altitude (Length): The apoapsis altitude (wrt. equatorial radius).
                                periapsis_altitude (Length): The periapsis altitude (wrt. equatorial radius).
                                celestial_object (Celestial): The celestial object.
        
                            Returns:
                                Orbit: The equatorial `Orbit` object.
        """
    @staticmethod
    def frozen(epoch: ostk.physics.time.Instant, altitude: ostk.physics.unit.Length, celestial_object: ostk.physics.environment.object.Celestial, eccentricity: ostk.core.type.Real = ..., inclination: ostk.physics.unit.Angle = ..., raan: ostk.physics.unit.Angle = ..., aop: ostk.physics.unit.Angle = ..., true_anomaly: ostk.physics.unit.Angle = ...) -> Orbit:
        """
                            Create a frozen `Orbit` object.
        
                            The critical angles for inclination are 63.4349 degrees and 116.5651 degrees.
                            The critical angles for AoP are 90.0 degrees and 270.0 degrees.
        
                            At a minimum, an epoch, altitude, and celestial body with a defined J2 and J3 must be provided. 
                            In this case, the inclination and AoP are set to critical angles, and the eccentricity is derived 
                            from inclination. RAAN and true anomaly default to zero degrees.
                                            
                            Additionally, the following combinations of inputs are supported:
                            - AoP (inclination set to critical value, eccentricity derived)
                            - AoP and eccentricity (inclination derived)
                            - AoP and inclination, but at least one of them must be a critical value (eccentricity derived)
                            - Inclination (AoP set to critical value, eccentricity derived)
                            - Eccentricity (AoP set to critical value, inclination derived)
                            
                            Note that inclination and eccentricity cannot both be provided.
                            
                            RAAN and True Anomaly may be provided alongside any of these arguments, and will be passed through
                            to the resulting Orbit as they do not impact the frozen orbit condition.
        
                            Args:
                                epoch (Instant): The epoch.
                                altitude (Length): The altitude (wrt. equatorial radius).
                                celestial_object (Celestial): The celestial object.
                                eccentricity (float): The eccentricity.
                                inclination (Angle): The inclination.
                                raan (Angle): The right ascension of the ascending node.
                                aop (Angle): The argument of periapsis.
                                true_anomaly (Angle): The true anomaly.
        
                            Returns:
                                Orbit: The frozen `Orbit` object.
        """
    @staticmethod
    def geo_synchronous(epoch: ostk.physics.time.Instant, inclination: ostk.physics.unit.Angle, longitude: ostk.physics.unit.Angle, celestial_object: ostk.physics.environment.object.Celestial) -> Orbit:
        """
                            Create a geosynchronous `Orbit` object.
        
                            Args:
                                epoch (Instant): The epoch.
                                inclination (Angle): The inclination.
                                longitude (double): The longitude.
                                celestial_object (Celestial): The celestial object.
        
                            Returns:
                                Orbit: The geosynchronous `Orbit` object.
        """
    @staticmethod
    def sun_synchronous(epoch: ostk.physics.time.Instant, altitude: ostk.physics.unit.Length, local_time_at_descending_node: ostk.physics.time.Time, celestial_object: ostk.physics.environment.object.Celestial, argument_of_latitude: ostk.physics.unit.Angle = ...) -> Orbit:
        """
                            Create a sun-synchronous `Orbit` object.
        
                            Args:
                                epoch (Instant): The epoch.
                                altitude (Length): The altitude (wrt. equatorial radius).
                                local_time_at_descending_node (Time): The local time at descending node.
                                celestial_object (Celestial): The celestial object.
                                argument_of_latitude (Angle): The argument of latitude.
        
                            Returns:
                                Orbit: The sun-synchronous `Orbit` object.
        """
    @staticmethod
    def undefined() -> Orbit:
        """
                            Get an undefined `Orbit` object.
        
                            Returns:
                                Orbit: The undefined `Orbit` object.
        """
    def __eq__(self, arg0: Orbit) -> bool:
        ...
    @typing.overload
    def __init__(self, model: typing.Any, celestial_object: ostk.physics.environment.object.Celestial) -> None:
        """
                            Constructs an `Orbit` object.
        
                            Args:
                                model (orbit.Model): The orbit model.
                                celestial_object (Celestial): The celestial object.
        """
    @typing.overload
    def __init__(self, states: list[State], initial_revolution_number: ostk.core.type.Integer, celestial_object: ostk.physics.environment.object.Celestial) -> None:
        """
                            Constructs an `Orbit` object.
        
                            Args:
                                states (Array<State>): The states.
                                initial_revolution_number (Integer): The initial revolution number.
                                celestial_object (Celestial): The celestial object.
        """
    def __ne__(self, arg0: Orbit) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_celestial_object(self) -> ostk.physics.environment.object.Celestial:
        """
                            Access the celestial object.
        
                            Returns:
                                Celestial: The celestial object.
        """
    def access_kepler_model(self) -> ...:
        """
                            Access the Kepler orbit model.
        
                            Returns:
                               Kepler: The Kepler orbit model.
        """
    def access_model(self) -> ...:
        """
                            Access the orbit model.
        
                            Returns:
                                orbit.Model: The orbit model.
        """
    def access_propagated_model(self) -> ...:
        """
                            Access the propagated orbit model.
        
                            Returns:
                                Propagated: The propagated orbit model.
        """
    def access_sgp4_model(self) -> ...:
        """
                            Access the SGP4 orbit model.
        
                            Returns:
                                SGP4: The SGP4 orbit model.
        """
    def access_tabulated_model(self) -> ...:
        """
                            Access the tabulated orbit model.
        
                            Returns:
                                Tabulated: The tabulated orbit model.
        """
    def get_orbital_frame(self, frame_type: Orbit.FrameType) -> ostk.physics.coordinate.Frame:
        """
                            Get the orbital frame.
        
                            Args:
                                frame_type (Orbit::FrameType): The frame type.
        
                            Returns:
                                Frame: The orbital frame.
        """
    def get_pass_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                            Get the pass at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                ostk::astrodynamics::trajectory::orbit::Pass: The pass.
        """
    def get_pass_with_revolution_number(self, revolution_number: ostk.core.type.Integer, step_duration: ostk.physics.time.Duration = ...) -> ...:
        """
                            Get the pass with a given revolution number.
        
                            Args:
                                revolution_number (int): The revolution number.
                                step_duration (Duration): The initial step duration used for the pass computation algorithm.
        
                            Returns:
                                Pass: The pass.
        """
    def get_passes_within_interval(self, interval: ostk.physics.time.Interval) -> list[...]:
        """
                            Get the passes within a given interval.
        
                            Args:
                                interval (Interval): The interval.
        
                            Returns:
                                list[Pass]: The passes.
        """
    def get_revolution_number_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Integer:
        """
                            Get the revolution number at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                int: The revolution number.
        """
    def is_defined(self) -> bool:
        """
                            Check if the `Orbit` object is defined.
        
                            Returns:
                                bool: True if the `Orbit` object is defined, False otherwise.
        """
class Propagator:
    """
    
                A `Propagator` that propagates the provided `State` using it's `NumericalSolver` under the set `Dynamics`.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    @typing.overload
    def default() -> Propagator:
        """
                        Get the default propagator.
        
                        Returns:
                            Propagator: The default propagator.
        """
    @staticmethod
    @typing.overload
    def default(environment: ostk.physics.Environment) -> Propagator:
        """
                        Get the default propagator for a given environment.
        
                        Args:
                            environment (Environment) The environment.
        
                        Returns:
                            Propagator: The default propagator for the given environment.
        """
    @staticmethod
    def from_environment(numerical_solver: state.NumericalSolver, environment: ostk.physics.Environment) -> Propagator:
        """
                        Create a propagator from an environment.
        
                        Args:
                            numerical_solver (NumericalSolver) The numerical solver.
                            environment (Environment) The environment.
        
                        Returns:
                            Propagator: The propagator.
        """
    def __eq__(self, arg0: Propagator) -> bool:
        ...
    @typing.overload
    def __init__(self, numerical_solver: state.NumericalSolver, dynamics: list[...] = []) -> None:
        """
                        Construct a new `Propagator` object.
        
                        Args:
                            numerical_solver (NumericalSolver) The numerical solver.
                            dynamics (list[Dynamics], optional) The dynamics.
        
                        Returns:
                            Propagator: The new `Propagator` object.
        """
    @typing.overload
    def __init__(self, numerical_solver: state.NumericalSolver, dynamics: list[...], maneuvers: list[...], interpolation_type: ostk.mathematics.curve_fitting.Interpolator.Type = ...) -> None:
        """
                        Construct a new `Propagator` object with maneuvers.
        
                        Args:
                            numerical_solver (NumericalSolver) The numerical solver.
                            dynamics (list[Dynamics]) The dynamics.
                            maneuvers (list[Maneuver]) The maneuvers.
                            interpolation_type (Interpolator.Type, optional) The interpolation type. Defaults to Barycentric Rational.
        
                        Returns:
                            Propagator: The new `Propagator` object.
        """
    def __ne__(self, arg0: Propagator) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_numerical_solver(self) -> state.NumericalSolver:
        """
                        Access the numerical solver.
        
                        Returns:
                            NumericalSolver&: The numerical solver.
        """
    def add_dynamics(self, dynamics: typing.Any) -> None:
        """
                        Add dynamics.
        
                        Args:
                            dynamics (Dynamics) The dynamics.
        """
    def add_maneuver(self, maneuver: typing.Any, interpolation_type: ostk.mathematics.curve_fitting.Interpolator.Type = ...) -> None:
        """
                        Add a maneuver.
        
                        Args:
                            maneuver (Maneuver) The maneuver.
                            interpolation_type (Interpolator.Type, optional) The interpolation type. Defaults to Barycentric Rational.
        """
    def calculate_state_at(self, state: State, instant: ostk.physics.time.Instant) -> State:
        """
                        Calculate the state at a given instant.
        
                        Args:
                            state (State) The state.
                            instant (Instant) The instant.
        
                        Returns:
                            State: The state at the given instant.
        """
    def calculate_state_to_condition(self, state: State, instant: ostk.physics.time.Instant, event_condition: typing.Any) -> state.NumericalSolver.ConditionSolution:
        """
                        Calculate the state up to a given event condition.
        
                        Args:
                            state (State) The state.
                            instant (Instant) The instant.
                            event_condition (EventCondition) The event condition.
        
                        Returns:
                            State: The state up to the given event condition.
        """
    def calculate_states_at(self, state: State, instants: list[ostk.physics.time.Instant]) -> list[State]:
        """
                        Calculate the states at given instants. It is more performant than looping `calculate_state_at` for multiple instants.
        
                        Args:
                            state (State) The state.
                            instants (list[Instant]) The instants.
        
                        Returns:
                            list[State]: The states at the given instants.
        """
    def clear_dynamics(self) -> None:
        """
                        Clear the dynamics.
        """
    def get_dynamics(self) -> list[...]:
        """
                        Get the dynamics.
        
                        Returns:
                            list[Dynamics]: The dynamics.
        """
    def get_number_of_coordinates(self) -> int:
        """
                        Get the number of coordinates.
        
                        Returns:
                            int: The number of coordinates.
        """
    def is_defined(self) -> bool:
        """
                        Check if the propagator is defined.
        
                        Returns:
                            bool: True if the propagator is defined, False otherwise.
        """
    def set_dynamics(self, dynamics: list[...]) -> None:
        """
                        Set the dynamics.
        
                        Args:
                            dynamics (list[Dynamics]) The dynamics.
        """
class Segment:
    """
    
                    A `Segment` that can be solved provided an initial `State` and termination `Event Condition`.
    
                
    """
    class Solution:
        """
        
                    The Solution object returned when a `Segment` is solved.
        
                
        """
        def __init__(self, name: ostk.core.type.String, dynamics: list[...], states: list[State], condition_is_satisfied: bool, segment_type: typing.Any) -> None:
            """
                            Construct a Segment Solution.
            
                            Args:
                                name (str): The name of the segment.
                                dynamics (list[Dynamics]): The dynamics.
                                states (list[State]): The states.
                                condition_is_satisfied (bool): Whether the event condition is satisfied.
                                segment_type (Type): The type of the segment.
            """
        def __repr__(self) -> str:
            ...
        def __str__(self) -> str:
            ...
        def access_end_instant(self) -> ostk.physics.time.Instant:
            """
                            Get the instant at which the segment ends.
            
                            Returns:
                                Instant: The instant at which the segment ends.
            """
        def access_start_instant(self) -> ostk.physics.time.Instant:
            """
                            Get the instant at which the segment starts.
            
                            Returns:
                                Instant: The instant at which the segment starts.
            """
        def calculate_states_at(self, instants: list[ostk.physics.time.Instant], numerical_solver: state.NumericalSolver) -> list[State]:
            """
                            Calculate the states in this segment's solution at the given instants.
            
                            Args:
                                instants (list[Instant]): The instants at which the states will be calculated.
                                numerical_solver (NumericalSolver): The numerical solver used to calculate the states.
            
                            Returns:
                                list[State]: The states at the provided instants.
            """
        def compute_delta_mass(self) -> ostk.physics.unit.Mass:
            """
                            Compute the delta mass.
            
                            Returns:
                                Mass: The delta mass.
            """
        def compute_delta_v(self, specific_impulse: ostk.core.type.Real) -> ostk.core.type.Real:
            """
                            Compute the delta V.
            
                            Args:
                                specific_impulse (float): The specific impulse.
            
                            Returns:
                                float: The delta V (m/s).
            """
        def extract_maneuvers(self, frame: ostk.physics.coordinate.Frame) -> list[...]:
            """
                        Extract maneuvers from the (maneuvering) segment.
            
                        Returns:
                            list[Maneuver]: The list of maneuvers.
            """
        def get_all_dynamics_contributions(self, frame: ostk.physics.coordinate.Frame) -> dict[..., numpy.ndarray[numpy.float64[m, n]]]:
            """
                            Compute the contributions of all segment's dynamics in the provided frame for all states assocated with the segment.
            
                            Args:
                                frame (Frame): The frame.
            
                            Returns:
                                dict[Dynamics, np.ndarray]: The list of matrices with individual dynamics contributions.
            """
        def get_dynamics_acceleration_contribution(self, dynamics: typing.Any, frame: ostk.physics.coordinate.Frame) -> numpy.ndarray[numpy.float64[m, n]]:
            """
                            Compute the contribution of the provided dynamics to the acceleration in the provided frame for all states associated with the segment.
            
                            Args:
                                dynamics (Dynamics): The dynamics.
                                frame (Frame): The frame.
            
                            Returns:
                                np.ndarray: The matrix of dynamics contributions to acceleration.
            """
        def get_dynamics_contribution(self, dynamics: typing.Any, frame: ostk.physics.coordinate.Frame, coordinate_subsets: list[state.CoordinateSubset] = []) -> numpy.ndarray[numpy.float64[m, n]]:
            """
                            Compute the contribution of the provided dynamics in the provided frame for all states associated with the segment.
            
                            Args:
                                dynamics (Dynamics): The dynamics.
                                frame (Frame): The frame.
                                coordinate_subsets (list[CoordinateSubset], optional): A subset of the dynamics writing coordinate subsets to consider.
            
                            Returns:
                                MatrixXd: The matrix of dynamics contributions for the selected coordinate subsets of the dynamics.
            """
        def get_final_mass(self) -> ostk.physics.unit.Mass:
            """
                            Get the final mass.
            
                            Returns:
                                Mass: The final mass.
            """
        def get_initial_mass(self) -> ostk.physics.unit.Mass:
            """
                            Get the initial mass.
            
                            Returns:
                                Mass: The initial mass.
            """
        def get_interval(self) -> ostk.physics.time.Interval:
            """
                            Get the time interval of the solution.
            
                            Returns:
                                Interval: The interval.
            """
        def get_propagation_duration(self) -> ostk.physics.time.Duration:
            """
                            Get the propagation duration.
            
                            Returns:
                                Duration: The propagation duration.
            """
        @property
        def condition_is_satisfied(self) -> bool:
            """
                            Whether the event condition is satisfied.
            
                            :type: bool
            """
        @property
        def dynamics(self) -> list[...]:
            """
                            The dynamics.
            
                            :type: Dynamics
            """
        @property
        def name(self) -> ostk.core.type.String:
            """
                            The name of the segment.
            
                            :type: str
            """
        @property
        def segment_type(self) -> ...:
            """
                            The type of the segment.
            
                            :type: Type
            """
        @property
        def states(self) -> list[State]:
            """
                            The states.
            
                            :type: list[State]
            """
    class Type:
        """
        
                    Segment type.
                
        
        Members:
        
          Coast : Coast
        
          Maneuver : Maneuver
        """
        Coast: typing.ClassVar[Segment.Type]  # value = <Type.Coast: 0>
        Maneuver: typing.ClassVar[Segment.Type]  # value = <Type.Maneuver: 1>
        __members__: typing.ClassVar[dict[str, Segment.Type]]  # value = {'Coast': <Type.Coast: 0>, 'Maneuver': <Type.Maneuver: 1>}
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
    def coast(name: ostk.core.type.String, event_condition: typing.Any, dynamics: list[...], numerical_solver: state.NumericalSolver) -> Segment:
        """
                        Create a coast segment.
        
                        Args:
                            name (str): The name of the segment.
                            event_condition (EventCondition): The event condition.
                            dynamics (Dynamics): The dynamics.
                            numerical_solver (NumericalSolver): The numerical solver.
        
                        Returns:
                            Segment: The coast segment.
        """
    @staticmethod
    def maneuver(name: ostk.core.type.String, event_condition: typing.Any, thruster_dynamics: typing.Any, dynamics: list[...], numerical_solver: state.NumericalSolver) -> Segment:
        """
                        Create a maneuver segment.
        
                        Args:
                            name (str): The name of the segment.
                            event_condition (EventCondition): The event condition.
                            thruster_dynamics (ThrusterDynamics): The thruster dynamics.
                            dynamics (Dynamics): The dynamics.
                            numerical_solver (NumericalSolver): The numerical solver.
        
                        Returns:
                            Segment: The maneuver segment.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_dynamics(self) -> list[...]:
        """
                        Get the dynamics.
        
                        Returns:
                            Dynamics: The dynamics.
        """
    def get_event_condition(self) -> ...:
        """
                        Get the event condition.
        
                        Returns:
                            EventCondition: The event condition.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the name of the segment.
        
                        Returns:
                            str: The name of the segment.
        """
    def get_numerical_solver(self) -> state.NumericalSolver:
        """
                        Get the numerical solver.
        
                        Returns:
                            NumericalSolver: The numerical solver.
        """
    def get_type(self) -> Segment.Type:
        """
                        Get the type of the segment.
        
                        Returns:
                            Type: The type of the segment.
        """
    def solve(self, state: State, maximum_propagation_duration: ostk.physics.time.Duration = ...) -> Segment.Solution:
        """
                        Solve the segment.
        
                        Args:
                            state (State): The state.
                            maximum_propagation_duration (Duration, optional): The maximum propagation duration.
        
                        Returns:
                            SegmentSolution: The segment solution.
        """
class Sequence:
    """
    
                    A mission `Sequence`. Consists of a list of `Segment` objects and various configuration parameters.
    
                
    """
    class Solution:
        """
        
                    The Solution object that is returned when a `Sequence` is solved.
        
                
        """
        def __init__(self, segment_solutions: list[Segment.Solution], execution_is_complete: bool) -> None:
            """
                            Construct a new `Sequence.Solution` object.
            
                            Args:
                            segment_solutions (list[Segment.Solution]): The segment solutions.
                            execution_is_complete (bool): Whether the execution is complete.
            
                            Returns:
                                Sequence: The new `Sequence.Solution` object.
            """
        def __repr__(self) -> str:
            ...
        def __str__(self) -> str:
            ...
        def access_end_instant(self) -> ostk.physics.time.Instant:
            """
                            Get the instant at which the access ends.
            
                            Returns:
                                Instant: The instant at which the access ends.
            """
        def access_start_instant(self) -> ostk.physics.time.Instant:
            """
                            Get the instant at which the access starts.
            
                            Returns:
                                Instant: The instant at which the access starts.
            """
        def calculate_states_at(self, instants: list[ostk.physics.time.Instant], numerical_solver: state.NumericalSolver) -> list[State]:
            """
                            Calculate states in this sequence's solution at provided instants.
            
                            Args:
                                instants (list[Instant]): The instants at which the states will be calculated.
                                numerical_solver (NumericalSolver): The numerical solver used to calculate the states.
            
                            Returns:
                                list[State]: The states at the provided instants.
            """
        def compute_delta_mass(self) -> ostk.physics.unit.Mass:
            """
                            Compute the delta mass.
            
                            Returns:
                                float: The delta mass.
            """
        def compute_delta_v(self, specific_impulse: ostk.core.type.Real) -> ostk.core.type.Real:
            """
                            Compute the delta V.
            
                            Args:
                                specific_impulse (float): The specific impulse.
            
                            Returns:
                                float: The delta V (m/s).
            """
        def get_final_mass(self) -> ostk.physics.unit.Mass:
            """
                            Get the final mass.
            
                            Returns:
                                float: The final mass.
            """
        def get_initial_mass(self) -> ostk.physics.unit.Mass:
            """
                            Get the initial mass.
            
                            Returns:
                                float: The initial mass.
            """
        def get_interval(self) -> ostk.physics.time.Interval:
            """
                            Get the interval.
            
                            Returns:
                                Interval: The interval.
            """
        def get_propagation_duration(self) -> ostk.physics.time.Duration:
            """
                            Get the propagation duration.
            
                            Returns:
                                Duration: The propagation duration.
            """
        def get_states(self) -> list[State]:
            """
                            Get the states.
            
                            Returns:
                                list[State]: The states.
            """
        @property
        def execution_is_complete(self) -> bool:
            """
                            Whether the execution is complete.
            
                            :type: bool
            """
        @property
        def segment_solutions(self) -> list[Segment.Solution]:
            """
                            The solutions for each segment.
            
                            :type: list[SegmentSolution]
            """
    def __init__(self: typing.Sequence, segments: list[Segment] = [], numerical_solver: state.NumericalSolver = ..., dynamics: list[...] = [], maximum_propagation_duration: ostk.physics.time.Duration = ..., minimum_maneuver_duration: ostk.physics.time.Duration = ..., verbosity: int = 1) -> None:
        """
                            Construct a new `Sequence` object.
        
                            Args:
                            segments (list[Segment], optional): The segments. Defaults to an empty list.
                            numerical_solver (NumericalSolver, optional): The numerical solver. Defaults to the default conditional numerical solver.
                            dynamics (list[Dynamics], optional): The dynamics. Defaults to an empty list.
                            maximum_propagation_duration (Duration, optional): The maximum propagation duration. Defaults to 30 days.
                            minimum_maneuver_duration (Duration, optional): The minimum maneuver duration. Defaults to Undefined. If defined, maneuvers less than this duration will be skipped.
                            verbosity (int, optional): The verbosity level. Defaults to 1.
        
                            Returns:
                                Sequence: The new `Sequence` object.
        """
    def __repr__(self: typing.Sequence) -> str:
        ...
    def __str__(self: typing.Sequence) -> str:
        ...
    def add_coast_segment(self: typing.Sequence, event_condition: typing.Any) -> None:
        """
                            Add a coast segment.
        
                            Args:
                                event_condition (EventCondition): The event condition.
        """
    def add_maneuver_segment(self: typing.Sequence, event_condition: typing.Any, thruster_dynamics: typing.Any) -> None:
        """
                            Add a maneuver segment.
        
                            Args:
                                event_condition (EventCondition): The event condition.
                                thruster_dynamics (Thruster): The thruster dynamics.
        """
    def add_segment(self: typing.Sequence, segment: Segment) -> None:
        """
                            Add a segment.
        
                            Args:
                                segment (Segment): The segment.
        """
    def add_segments(self: typing.Sequence, segments: list[Segment]) -> None:
        """
                            Add segments.
        
                            Args:
                                segments (list[Segment]): The segments.
        """
    def get_dynamics(self: typing.Sequence) -> list[...]:
        """
                            Get the dynamics.
        
                            Returns:
                                list[Dynamics]: The dynamics.
        """
    def get_maximum_propagation_duration(self: typing.Sequence) -> ostk.physics.time.Duration:
        """
                            Get the maximum propagation duration.
        
                            Returns:
                                Duration: The maximum propagation duration.
        """
    def get_minimum_maneuver_duration(self: typing.Sequence) -> ostk.physics.time.Duration:
        """
                            Get the minimum maneuver duration.
        
                            Returns:
                                Duration: The minimum maneuver duration.
        """
    def get_numerical_solver(self: typing.Sequence) -> state.NumericalSolver:
        """
                            Get the numerical solver.
        
                            Returns:
                                NumericalSolver: The numerical solver.
        """
    def get_segments(self: typing.Sequence) -> list[Segment]:
        """
                            Get the segments.
        
                            Returns:
                                list[Segment]: The segments.
        """
    def solve(self: typing.Sequence, state: State, repetition_count: int = 1) -> Sequence.Solution:
        """
                            Solve the sequence.
        
                            Args:
                                state (State): The state.
                                repetition_count (int, optional): The repetition count. Defaults to 1.
        
                            Returns:
                                SequenceSolution: The sequence solution.
        """
    def solve_to_condition(self: typing.Sequence, state: State, event_condition: typing.Any, maximum_propagation_duration_limit: ostk.physics.time.Duration = ...) -> Sequence.Solution:
        """
                            Solve the sequence until the event condition is met.
        
                            In the case that the event condition is not met due to maximum propagation duration limit,
                            it will return the `SequenceSolution` with `executionIsComplete` set to `False`.
        
                            Args:
                                state (State): The state.
                                event_condition (EventCondition): The event condition.
                                maximum_propagation_duration_limit (Duration, optional): The maximum propagation duration limit for the sequence. Defaults to 30 days.
        
                            Returns:
                                SequenceSolution: The sequence solution.
        """
class State:
    """
    
                This class represents the physical state of an object.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def from_dict(data: dict) -> State:
        """
        
            Create a State from a dictionary.
        
            Note: Implicit assumption that ECEF = ITRF, and ECI = GCRF.
        
            The dictionary must contain the following:
            - 'timestamp': The timestamp of the state.
            - 'r_ITRF_x'/'rx'/'rx_eci'/'rx_ecef': The x-coordinate of the position.
            - 'r_ITRF_y'/'ry'/'ry_eci'/'ry_ecef': The y-coordinate of the position.
            - 'r_ITRF_z'/'rz'/'rz_eci'/'rz_ecef': The z-coordinate of the position.
            - 'v_ITRF_x'/'vx'/'vx_eci'/'vx_ecef': The x-coordinate of the velocity.
            - 'v_ITRF_y'/'vy'/'vy_eci'/'vy_ecef': The y-coordinate of the velocity.
            - 'v_ITRF_z'/'vz'/'vz_eci'/'vz_ecef': The z-coordinate of the velocity.
            - 'frame': The frame of the state. Required if 'rx', 'ry', 'rz', 'vx', 'vy', 'vz' are provided.
            - 'q_B_ECI_x': The x-coordinate of the quaternion. Optional.
            - 'q_B_ECI_y': The y-coordinate of the quaternion. Optional.
            - 'q_B_ECI_z': The z-coordinate of the quaternion. Optional.
            - 'q_B_ECI_s': The s-coordinate of the quaternion. Optional.
            - 'w_B_ECI_in_B_x': The x-coordinate of the angular velocity. Optional.
            - 'w_B_ECI_in_B_y': The y-coordinate of the angular velocity. Optional.
            - 'w_B_ECI_in_B_z': The z-coordinate of the angular velocity. Optional.
            - 'drag_coefficient'/'cd': The drag coefficient. Optional.
            - 'cross_sectional_area'/'surface_area': The cross-sectional area. Optional.
            - 'mass': The mass. Optional.
            - 'ballistic_coefficient'/'bc': The ballistic coefficient. Optional.
        
            Args:
                data (dict): The dictionary.
        
            Returns:
                State: The State.
            
        """
    @staticmethod
    def template(frame: ostk.physics.coordinate.Frame, coordinate_subsets: list) -> type:
        """
        
            Emit a custom class type for States. This is meta-programming syntactic sugar on top of the StateBuilder class.
        
            StateType = State.template(frame, coordinate_subsets)
            state = StateType(instant, coordinates)
        
            is equivalent to
        
            state_builder = StateBuilder(frame, coordinate_subsets)
            state = state_builder.build(instant, coordinates)
            
        """
    @staticmethod
    def undefined() -> State:
        """
                        Get an undefined state.
        
                        Returns:
                            State: An undefined state.
        """
    def __add__(self, arg0: State) -> State:
        ...
    def __eq__(self, arg0: State) -> bool:
        ...
    @typing.overload
    def __init__(self, instant: ostk.physics.time.Instant, position: ostk.physics.coordinate.Position, velocity: ostk.physics.coordinate.Velocity) -> None:
        """
                         Utility constructor for Position/Velocity only.
                         
                         Args:
                             instant (Instant): An instant
                             position (Position): The cartesian position at the instant
                             velocity (Velocity): The cartesian velocity at the instant
        """
    @typing.overload
    def __init__(self, instant: ostk.physics.time.Instant, position: ostk.physics.coordinate.Position, velocity: ostk.physics.coordinate.Velocity, attitude: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion, angular_velocity: numpy.ndarray[numpy.float64[3, 1]], attitude_frame: ostk.physics.coordinate.Frame) -> None:
        """
                         Utility constructor for Position/Velocity/Attitude/Angular velocity.
                         
                         Args:
                             instant (Instant): An instant
                             position (Position): The cartesian position at the instant
                             velocity (Velocity): The cartesian velocity at the instant
                             attitude (Quaternion): The attitude at the instant, representing the rotation required to go from the attitude reference frame to the satellite body frame
                             angular_velocity (numpy.ndarray): The angular velocity at the instant, representing the angular velocity of the satellite body frame with respect ot teh attitude frame, expressed in body frame
                             attitude_frame (Frame): The attitude reference frame
        """
    @typing.overload
    def __init__(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame, coordinate_broker: typing.Any) -> None:
        """
                         Constructor with a pre-defined Coordinates Broker.
                         
                         Args:
                             instant (Instant): An instant
                             coordinates (numpy.ndarray): The coordinates at the instant in International System of Units
                             frame (Frame): The reference frame in which the coordinates are referenced to and resolved in
                             coordinate_broker (CoordinateBroker): The coordinate broker associated to the coordinates
        """
    @typing.overload
    def __init__(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]], frame: ostk.physics.coordinate.Frame, coordinate_subsets: list[...]) -> None:
        """
                         Constructor with coordinate subsets.
                         
                         Args:
                             instant (Instant): An instant
                             coordinates (numpy.ndarray): The coordinates at the instant in International System of Units
                             frame (Frame): The reference frame in which the coordinates are referenced to and resolved in
                             coordinate_subsets (CoordinateBroker): The coordinate subsets associated to the coordinates
        """
    @typing.overload
    def __init__(self, state: State) -> None:
        ...
    def __ne__(self, arg0: State) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: State) -> State:
        ...
    def extract_coordinate(self, coordinate_subset: typing.Any) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Extract the coordinates associated to a subset of the state.
        
                        Args:
                            coordinate_subset (CoordinateSubset): The coordinate subset to extract.
        
                        Returns:
                            np.array: The coordinates associated to the subset.
        """
    def extract_coordinates(self, coordinate_subsets: list[...]) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Extract the coordinates associated to a set of subsets of the state.
        
                        Args:
                            coordinate_subsets (list[CoordinateSubset]): The coordinate subsets to extract.
        
                        Returns:
                            np.array: The coordinates associated to the subsets.
        """
    def get_angular_velocity(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the angular velocity of the state.
        
                        Returns:
                            np.array: The angular velocity of the state.
        """
    def get_attitude(self) -> ostk.mathematics.geometry.d3.transformation.rotation.Quaternion:
        """
                        Get the attitude of the state.
        
                        Returns:
                            Quaternion: The attitude of the state.
        """
    def get_coordinate_subsets(self) -> list[...]:
        """
                        Get the coordinate subsets associated to the state.
        
                        Returns:
                            list[CoordinateSubset]: The coordinate subsets associated to the state.
        """
    def get_coordinates(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Get the coordinates of the state.
        
                        Returns:
                            np.array: The coordinates of the state.
        """
    def get_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Get the reference frame of the state.
        
                        Returns:
                            Frame: The reference frame of the state.
        """
    def get_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the instant of the state.
        
                        Returns:
                            Instant: The instant of the state.
        """
    def get_position(self) -> ostk.physics.coordinate.Position:
        """
                        Get the position of the state.
        
                        Returns:
                            Position: The position of the state.
        """
    def get_size(self) -> int:
        """
                        Get the size of the state.
        
                        Returns:
                            int: The size of the state.
        """
    def get_velocity(self) -> ostk.physics.coordinate.Velocity:
        """
                        Get the velocity of the state.
        
                        Returns:
                            Velocity: The velocity of the state.
        """
    def has_subset(self, subset: typing.Any) -> bool:
        """
                        Check if the state has a given subset.
        
                        Args:
                            subset (CoordinateSubset): The subset to check.
        
                        Returns:
                            bool: True if the state has the subset, False otherwise.
        """
    def in_frame(self, frame: ostk.physics.coordinate.Frame) -> State:
        """
                        Transform the state to the provided reference frame.
        
                        Args:
                            frame (Frame): The reference frame to transform to.
        
                        Returns:
                            State: The transformed state.
        """
    def is_defined(self) -> bool:
        """
                        Check if the state is defined.
        
                        Returns:
                            bool: True if the state is defined, False otherwise.
        """
class StateBuilder:
    """
    
                This class makes it convenient to build a `State` object.
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> StateBuilder:
        """
                        Get an undefined `StateBuilder`.
        
                        Returns:
                            StateBuilder: The undefined `StateBuilder`.
        """
    def __add__(self, arg0: state.CoordinateSubset) -> StateBuilder:
        """
                        Add a coordinate subset to the `StateBuilder`.
        
                        Arguments:
                            coordinate_subsets (CoordinateSubset): The coordinate subset to add.
        
                        Returns:
                            StateBuilder: The `StateBuilder` with the added coordinate subset.
        """
    def __eq__(self, arg0: StateBuilder) -> bool:
        """
                        Check if two `StateBuilder` objects are equal.
        
                        Returns:
                            bool: True if the two `StateBuilder` objects are equal, False otherwise.
        """
    @typing.overload
    def __init__(self, frame: ostk.physics.coordinate.Frame, coordinate_subsets: list[state.CoordinateSubset]) -> None:
        """
                        Construct a new `StateBuilder` object.
        
                        Arguments:
                            frame (Frame): The reference frame.
                            coordinate_subsets list[CoordinateSubset]: The coordinate subsets.
        
                        Returns:
                            StateBuilder: The new `StateBuilder` object.
        """
    @typing.overload
    def __init__(self, frame: ostk.physics.coordinate.Frame, coordinate_broker: state.CoordinateBroker) -> None:
        """
                        Construct a new `StateBuilder` object.
        
                        Arguments:
                            frame (Frame): The reference frame.
                            coordinate_broker (CoordinateBroker): The coordinate broker.
        
                        Returns:
                            StateBuilder: The new `StateBuilder` object.
        """
    @typing.overload
    def __init__(self, state: State) -> None:
        """
                        Construct a new `StateBuilder` object.
        
                        Arguments:
                            state (State): The state.
        
                        Returns:
                            StateBuilder: The new `StateBuilder` object.
        """
    def __ne__(self, arg0: StateBuilder) -> bool:
        """
                        Check if two `StateBuilder` objects are not equal.
        
                        Returns:
                            bool: True if the two `StateBuilder` objects are not equal, False otherwise.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: state.CoordinateSubset) -> StateBuilder:
        """
                        Remove a coordinate subset from the `StateBuilder`.
        
                        Arguments:
                            coordinate_subset (CoordinateSubset): The coordinate subset to remove.
        
                        Returns:
                            StateBuilder: The `StateBuilder` with the removed coordinate subset.
        """
    def access_coordinate_broker(self) -> state.CoordinateBroker:
        """
                        Access the coordinate broker of the `StateBuilder`.
        
                        Returns:
                            CoordinateBroker: The coordinate broker of the `StateBuilder`.
        """
    def build(self, instant: ostk.physics.time.Instant, coordinates: numpy.ndarray[numpy.float64[m, 1]]) -> State:
        """
                        Build a `State` object from the `StateBuilder`.
        
                        Arguments:
                            instant (Instant): The instant of the state.
                            coordinates (VectorXd): The coordinates of the state.
        
                        Returns:
                            State: A `State` object built from the `StateBuilder`.
        """
    def expand(self, state: State, default_state: State) -> State:
        """
                        Expand a `State` object to the coordinate subsets of the `StateBuilder`.
        
                        Arguments:
                            state (State): The `State` object to expand.
                            default_state (State): The `State` object used to supply any additional coordinates.
        
                        Returns:
                            State: A `State` object with the coordinate subsets of the `StateBuilder`.
        """
    def get_coordinate_subsets(self) -> list[state.CoordinateSubset]:
        """
                        Get the coordinate subsets of the `StateBuilder`.
        
                        Returns:
                            Array<Shared<const CoordinateSubset>>: The coordinate subsets of the `StateBuilder`.
        """
    def get_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Get the reference frame of the `StateBuilder`.
        
                        Returns:
                            Frame: The reference frame of the `StateBuilder`.
        """
    def get_size(self) -> int:
        """
                        Get the total size of all coordinates from all subsets.
        
                        Returns:
                            Size: The total size of all coordinates from all subsets.
        """
    def is_defined(self) -> bool:
        """
                        Check if the `StateBuilder` is defined.
        
                        Returns:
                            bool: True if the `StateBuilder` is defined, False otherwise.
        """
    def reduce(self, state: State) -> State:
        """
                        Reduce a `State` object to the coordinate subsets of the `StateBuilder`.
        
                        Arguments:
                            state (State): The `State` object to reduce.
        
                        Returns:
                            State: A `State` object with the coordinate subsets of the `StateBuilder`.
        """
