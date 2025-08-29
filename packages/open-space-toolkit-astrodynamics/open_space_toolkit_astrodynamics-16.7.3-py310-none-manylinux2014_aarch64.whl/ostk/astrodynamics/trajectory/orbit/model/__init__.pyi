from __future__ import annotations
import numpy
import ostk.astrodynamics.trajectory
import ostk.astrodynamics.trajectory.orbit
import ostk.core.type
import ostk.mathematics.curve_fitting
import ostk.physics.coordinate
import ostk.physics.environment.object
import ostk.physics.time
import ostk.physics.unit
import typing
from . import brouwerLyddaneMean
from . import kepler
from . import sgp4
__all__ = ['BrouwerLyddaneMean', 'Kepler', 'ModifiedEquinoctial', 'Propagated', 'SGP4', 'Tabulated', 'brouwerLyddaneMean', 'kepler', 'sgp4']
class BrouwerLyddaneMean(kepler.COE):
    """
    
                    Brouwer-Lyddane mean orbit elements. This is a parent class, please use the Short or Long child classes as appropriate.
    
                
    """
    def __init__(self, semi_major_axis: ostk.physics.unit.Length, eccentricity: ostk.core.type.Real, inclination: ostk.physics.unit.Angle, raan: ostk.physics.unit.Angle, aop: ostk.physics.unit.Angle, mean_anomaly: ostk.physics.unit.Angle) -> None:
        """
                            Constructor.
        
                            Args:
                                semi_major_axis (Length): The semi-major axis.
                                eccentricity (float): The eccentricity.
                                inclination (Angle): The inclination.
                                raan (Angle): The right ascension of the ascending node.
                                aop (Angle): The argument of periapsis.
                                mean_anomaly (Angle): The mean anomaly.
        """
    def get_cartesian_state(self, gravitational_parameter: ostk.physics.unit.Derived, frame: ostk.physics.coordinate.Frame) -> tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity]:
        """
                            Get the Cartesian state of the `BrouwerLyddaneMean` model.
        
                            Args:
                                gravitational_parameter (float): The gravitational parameter of the central body.
                                frame (str): The reference frame in which the state is expressed.
        
                            Returns:
                                CartesianState: The Cartesian state.
        """
    def get_eccentric_anomaly(self) -> ostk.physics.unit.Angle:
        """
                            Get the eccentric anomaly of the `BrouwerLyddaneMean` model.
        
                            Returns:
                                Angle: The eccentric anomaly.
        """
    def get_mean_anomaly(self) -> ostk.physics.unit.Angle:
        """
                            Get the mean anomaly of the `BrouwerLyddaneMean` model.
        
                            Returns:
                                Angle: The mean anomaly.
        """
    def get_true_anomaly(self) -> ostk.physics.unit.Angle:
        """
                            Get the true anomaly of the `BrouwerLyddaneMean` model.
        
                            Returns:
                                Angle: The true anomaly.
        """
    def to_coe(self) -> kepler.COE:
        """
                            Convert the `BrouwerLyddaneMean` model to classical orbital elements.
        
                            Returns:
                                COE: The classical orbital elements.
        """
class Kepler(ostk.astrodynamics.trajectory.orbit.OrbitModel):
    """
    
                    A Kepler orbit model.
    
                    Provides the interface for orbit models.
    
                
    """
    class PerturbationType:
        """
        
                        The Perturbation Type due to Oblateness
                    
                    
        
        Members:
        
          No : No perturbation
        
          J2 : J2 perturbation
        
          J4 : J4 perturbation
        """
        J2: typing.ClassVar[Kepler.PerturbationType]  # value = <PerturbationType.J2: 1>
        J4: typing.ClassVar[Kepler.PerturbationType]  # value = <PerturbationType.J4: 2>
        No: typing.ClassVar[Kepler.PerturbationType]  # value = <PerturbationType.No: 0>
        __members__: typing.ClassVar[dict[str, Kepler.PerturbationType]]  # value = {'No': <PerturbationType.No: 0>, 'J2': <PerturbationType.J2: 1>, 'J4': <PerturbationType.J4: 2>}
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
    def string_from_perturbation_type(perturbation_type: Kepler.PerturbationType) -> ostk.core.type.String:
        """
                            Get the string representation of a `PerturbationType`.
        
                            Args:
                                perturbation_type (PerturbationType): The perturbation type.
        
                            Returns:
                                str: The string representation.
        """
    def __eq__(self, arg0: Kepler) -> bool:
        ...
    @typing.overload
    def __init__(self, coe: typing.Any, epoch: ostk.physics.time.Instant, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, j2: ostk.core.type.Real, j4: ostk.core.type.Real, perturbation_type: Kepler.PerturbationType) -> None:
        """
                            Constructor.
        
                            Args:
                                coe (COE): The classical orbital elements.
                                epoch (Instant): The epoch.
                                gravitational_parameter (Derived): The gravitational parameter.
                                equatorial_radius (Length): The equatorial radius.
                                j2 (float): The J2 coefficient.
                                j4 (float): The J4 coefficient.
                                perturbation_type (PerturbationType): The perturbation type.
        """
    @typing.overload
    def __init__(self, coe: typing.Any, epoch: ostk.physics.time.Instant, celestial_object: ostk.physics.environment.object.Celestial, perturbation_type: Kepler.PerturbationType, in_fixed_frame: bool = False) -> None:
        """
                            Constructor.
        
                            Args:
                                coe (COE): The classical orbital elements.
                                epoch (Instant): The epoch.
                                celestial_object (Celestial): The celestial object.
                                perturbation_type (PerturbationType): The perturbation type.
                                in_fixed_frame (bool): If True, the state is expressed in the fixed frame, otherwise it is expressed in the inertial frame. Default is False.
        """
    def __ne__(self, arg0: Kepler) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_revolution_number_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Integer:
        """
                            Calculate the revolution number of the `Kepler` model at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                int: The revolution number.
        """
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                            Calculate the state of the `Kepler` model at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                State: The state.
        """
    def get_classical_orbital_elements(self) -> ...:
        """
                            Get the classical orbital elements of the `Kepler` model.
        
                            Returns:
                                COE: The classical orbital elements.
        """
    def get_epoch(self) -> ostk.physics.time.Instant:
        """
                            Get the epoch of the `Kepler` model.
        
                            Returns:
                                Instant: The epoch.
        """
    def get_equatorial_radius(self) -> ostk.physics.unit.Length:
        """
                            Get the equatorial radius of the `Kepler` model.
        
                            Returns:
                                Length: The equatorial radius.
        """
    def get_gravitational_parameter(self) -> ostk.physics.unit.Derived:
        """
                            Get the gravitational parameter of the `Kepler` model.
        
                            Returns:
                                Derived: The gravitational parameter.
        """
    def get_j2(self) -> ostk.core.type.Real:
        """
                            Get the J2 coefficient of the `Kepler` model.
        
                            Returns:
                                float: The J2 coefficient.
        """
    def get_j4(self) -> ostk.core.type.Real:
        """
                            Get the J4 coefficient of the `Kepler` model.
        
                            Returns:
                                float: The J4 coefficient.
        """
    def get_perturbation_type(self) -> Kepler.PerturbationType:
        """
                            Get the perturbation type of the `Kepler` model.
        
                            Returns:
                                PerturbationType: The perturbation type.
        """
    def get_revolution_number_at_epoch(self) -> ostk.core.type.Integer:
        """
                            Get the revolution number at the epoch of the `Kepler` model.
        
                            Returns:
                                int: The revolution number.
        """
    def is_defined(self) -> bool:
        """
                            Check if the `Kepler` model is defined.
        
                            Returns:
                                bool: True if the `Kepler` model is defined, False otherwise.
        """
class ModifiedEquinoctial:
    """
    
                Modified Equinoctial Orbital Elements (ModifiedEquinoctial).
    
                The Modified Equinoctial Orbital Elements (ModifiedEquinoctial) provide a non-singular representation of an orbit,
                useful for a wide range of eccentricities and inclinations (except for i = 180 deg).
    
                Elements:
                p: semi-latus rectum (m)
                f: x-component of eccentricity vector (e * cos(RAAN + AOP))
                g: y-component of eccentricity vector (e * sin(RAAN + AOP))
                h: x-component of node vector (tan(i/2) * cos(RAAN))
                k: y-component of node vector (tan(i/2) * sin(RAAN))
                L: true longitude (RAAN + AOP + True Anomaly) (rad)
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def cartesian(cartesian_state: tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity], gravitational_parameter: ostk.physics.unit.Derived) -> ModifiedEquinoctial:
        """
                        Create ModifiedEquinoctial from Cartesian state (position, velocity).
        
                        Args:
                            cartesian_state (tuple[Position, Velocity]): Cartesian state (Position, Velocity). Must be in an inertial frame.
                            gravitational_parameter (Derived): Gravitational parameter of the central body.
        
                        Returns:
                            ModifiedEquinoctial: ModifiedEquinoctial object.
        """
    @staticmethod
    def coe(coe: kepler.COE) -> ModifiedEquinoctial:
        """
                        Create Modified Equinoctial elements from Classical Orbital Elements (COE).
        
                        Args:
                            coe (COE): Classical Orbital Elements.
        
                        Returns:
                            ModifiedEquinoctial: Modified Equinoctial Elements.
        """
    @staticmethod
    def undefined() -> ModifiedEquinoctial:
        """
                        Create an undefined ModifiedEquinoctial object.
        
                        Returns:
                            ModifiedEquinoctial: Undefined ModifiedEquinoctial object.
        """
    def __eq__(self, arg0: ModifiedEquinoctial) -> bool:
        ...
    def __init__(self, semi_latus_rectum: ostk.physics.unit.Length, eccentricity_x: ostk.core.type.Real, eccentricity_y: ostk.core.type.Real, node_x: ostk.core.type.Real, node_y: ostk.core.type.Real, true_longitude: ostk.physics.unit.Angle) -> None:
        """
                        Constructor.
        
                        Args:
                            semi_latus_rectum (Length): Semi-latus rectum.
                            eccentricity_x (float): x-component of eccentricity vector.
                            eccentricity_y (float): y-component of eccentricity vector.
                            node_x (float): x-component of node vector.
                            node_y (float): y-component of node vector.
                            true_longitude (Angle): True longitude.
        """
    def __ne__(self, arg0: ModifiedEquinoctial) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_cartesian_state(self, gravitational_parameter: ostk.physics.unit.Derived, frame: ostk.physics.coordinate.Frame) -> tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity]:
        """
                        Get Cartesian state (position, velocity) from ModifiedEquinoctial.
        
                        Args:
                            gravitational_parameter (Derived): Gravitational parameter of the central body.
                            frame (Frame): The reference frame for the output Cartesian state. Must be an inertial frame.
        
                        Returns:
                            tuple[Position, Velocity]: Position and Velocity.
        """
    def get_eccentricity_x(self) -> ostk.core.type.Real:
        """
                        Get x-component of eccentricity vector (f).
        
                        Returns:
                            float: f component.
        """
    def get_eccentricity_y(self) -> ostk.core.type.Real:
        """
                        Get y-component of eccentricity vector (g).
        
                        Returns:
                            float: g component.
        """
    def get_node_x(self) -> ostk.core.type.Real:
        """
                        Get x-component of node vector (h).
        
                        Returns:
                            float: h component.
        """
    def get_node_y(self) -> ostk.core.type.Real:
        """
                        Get y-component of node vector (k).
        
                        Returns:
                            float: k component.
        """
    def get_semi_latus_rectum(self) -> ostk.physics.unit.Length:
        """
                        Get semi-latus rectum (p).
        
                        Returns:
                            Length: Semi-latus rectum.
        """
    def get_si_vector(self) -> numpy.ndarray[numpy.float64[6, 1]]:
        """
                        Get ModifiedEquinoctial elements as a 6D vector in SI units.
                        [p (m), f, g, h, k, L (rad)]
        
                        Returns:
                            numpy.ndarray: 6D vector of elements in SI units.
        """
    def get_true_longitude(self) -> ostk.physics.unit.Angle:
        """
                        Get true longitude (L).
        
                        Returns:
                            Angle: True longitude.
        """
    def is_defined(self) -> bool:
        """
                        Check if ModifiedEquinoctial is defined.
        
                        Returns:
                            bool: True if ModifiedEquinoctial is defined.
        """
    def to_coe(self, gravitational_parameter: ostk.physics.unit.Derived) -> kepler.COE:
        """
                        Convert Modified Equinoctial to Classical Orbital Elements (COE).
        
                        Args:
                            gravitational_parameter (Derived): Gravitational parameter of the central body.
        
                        Returns:
                            COE: Classical Orbital Elements.
        """
class Propagated(ostk.astrodynamics.trajectory.orbit.OrbitModel):
    """
    
                    A Propagated orbit model.
    
                    Provides the interface for orbit models.
    
                
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Propagated) -> bool:
        ...
    @typing.overload
    def __init__(self, propagator: typing.Any, state: ostk.astrodynamics.trajectory.State, initial_revolution_number: ostk.core.type.Integer = 1) -> None:
        """
                            Constructor.
        
                            Args:
                                propagator (Propagator): The propagator.
                                state (State): The initial state.
                                initial_revolution_number (int, optional): The initial revolution number. Defaults to 1.
        """
    @typing.overload
    def __init__(self, propagator: typing.Any, state_array: list[ostk.astrodynamics.trajectory.State], initial_revolution_number: ostk.core.type.Integer = 1) -> None:
        """
                            Constructor.
        
                            Args:
                                propagator (Propagator): The propagator.
                                state_array (list[State]): The initial state array.
                                initial_revolution_number (int, optional): The initial revolution number. Defaults to 1.
        """
    def __ne__(self, arg0: Propagated) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_cached_state_array(self) -> list[ostk.astrodynamics.trajectory.State]:
        """
                            Access the cached state array of the `Propagated` model.
        
                            Returns:
                                list[State]: The cached state array.
        """
    def access_propagator(self) -> ...:
        """
                            Access the propagator of the `Propagated` model.
        
                            Returns:
                                Propagator: The propagator.
        """
    def calculate_revolution_number_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Integer:
        """
                            Calculate the revolution number of the `Propagated` model at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                int: The revolution number.
        """
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                            Calculate the state of the `Propagated` model at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                State: The state.
        """
    def calculate_states_at(self, instants: list[ostk.physics.time.Instant]) -> list[ostk.astrodynamics.trajectory.State]:
        """
                            Calculate the states of the `Propagated` model at given instants.
        
                            Args:
                                instants (list[Instant]): The instants.
        
                            Returns:
                                list[State]: The states.
        """
    def get_epoch(self) -> ostk.physics.time.Instant:
        """
                            Get the epoch of the `Propagated` model.
        
                            Returns:
                                Instant: The epoch.
        """
    def get_revolution_number_at_epoch(self) -> ostk.core.type.Integer:
        """
                            Get the revolution number at the epoch of the `Propagated` model.
        
                            Returns:
                                int: The revolution number.
        """
    def is_defined(self) -> bool:
        """
                            Check if the `Propagated` model is defined.
        
                            Returns:
                                bool: True if the `Propagated` model is defined, False otherwise.
        """
    def set_cached_state_array(self, state_array: list[ostk.astrodynamics.trajectory.State]) -> None:
        """
                            Set the cached state array of the `Propagated` model.
        
                            Args:
                                state_array (list[State]): The state array.
        """
class SGP4(ostk.astrodynamics.trajectory.orbit.OrbitModel):
    """
    
                    A SGP4 model.
    
                    Provides the interface for orbit models.
    
                
    """
    def __init__(self, tle: typing.Any) -> None:
        """
                            Constructor.
        
                            Args:
                                tle (TLE): The TLE.
        """
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                            Calculate the state of the `SGP4` model at a given instant.
        
                            Args:
                                instant (Instant): The instant.
        
                            Returns:
                                State: The state.
        """
    def get_epoch(self) -> ostk.physics.time.Instant:
        """
                            Get the epoch of the `SGP4` model.
        
                            Returns:
                                Instant: The epoch.
        """
    def get_revolution_number_at_epoch(self) -> ostk.core.type.Integer:
        """
                            Get the revolution number at the epoch of the `SGP4` model.
        
                            Returns:
                                int: The revolution number.
        """
    def get_tle(self) -> ...:
        """
                            Get the TLE of the `SGP4` model.
        
                            Returns:
                                TLE: The TLE.
        """
    def is_defined(self) -> bool:
        """
                            Check if the `SGP4` model is defined.
        
                            Returns:
                                bool: True if the `SGP4` model is defined, False otherwise.
        """
class Tabulated(ostk.astrodynamics.trajectory.orbit.OrbitModel):
    """
    
                Tabulated orbit model.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Tabulated) -> bool:
        ...
    def __init__(self, states: list[ostk.astrodynamics.trajectory.State], initial_revolution_number: ostk.core.type.Integer, interpolation_type: ostk.mathematics.curve_fitting.Interpolator.Type = ...) -> None:
        """
                        Constructor.
        
                        Args:
                            states (list[State]): The states.
                            initial_revolution_number (int): The initial revolution number.
                            interpolation_type (Interpolator.Type, optional): The interpolation type.
        """
    def __ne__(self, arg0: Tabulated) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_state_at(self, instant: ostk.physics.time.Instant) -> ostk.astrodynamics.trajectory.State:
        """
                        Calculate the state of the `Tabulated` model at a given instant.
        
                        Args:
                            instant (Instant): The instant.
        
                        Returns:
                            State: The state.
        """
    def calculate_states_at(self, instants: list[ostk.physics.time.Instant]) -> list[ostk.astrodynamics.trajectory.State]:
        """
                        Calculate the states of the `Tabulated` model at given instants.
        
                        Args:
                            instants (list[Instant]): The instants.
        
                        Returns:
                            list[State]: The states.
        """
    def get_epoch(self) -> ostk.physics.time.Instant:
        """
                        Get the epoch of the `Tabulated` model.
        
                        Returns:
                            Instant: The epoch.
        """
    def get_interpolation_type(self) -> ostk.mathematics.curve_fitting.Interpolator.Type:
        """
                        Get the interpolation type of the `Tabulated` model.
        
                        Returns:
                            Interpolator.Type: The interpolation type.
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        Get the interval of the `Tabulated` model.
        
                        Returns:
                            Interval: The interval.
        """
    def get_revolution_number_at_epoch(self) -> ostk.core.type.Integer:
        """
                        Get the revolution number at the epoch of the `Tabulated` model.
        
                        Returns:
                            int: The revolution number.
        """
    def is_defined(self) -> bool:
        """
                        Check if the `Tabulated` model is defined.
        
                        Returns:
                            bool: True if the `Tabulated` model is defined, False otherwise.
        """
