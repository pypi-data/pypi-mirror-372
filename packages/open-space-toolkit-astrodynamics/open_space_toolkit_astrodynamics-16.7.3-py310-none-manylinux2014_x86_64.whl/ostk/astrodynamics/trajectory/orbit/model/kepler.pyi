from __future__ import annotations
import numpy
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.environment.object
import ostk.physics.environment.object.celestial
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['COE']
class COE:
    """
    
                Classical orbital elements.
    
                Provides the classical orbital elements used to describe the orbit of a body around another.
    
                .. math::
    
                    \\begin{aligned}
                        a & = \\text{semi-major axis} \\\\
                        e & = \\text{eccentricity} \\\\
                        i & = \\text{inclination} \\\\
                        \\Omega & = \\text{right ascension of the ascending node} \\\\
                        \\omega & = \\text{argument of periapsis} \\\\
                        \\nu & = \\text{true anomaly} \\\\
                        M & = \\text{mean anomaly} \\\\
                        E & = \\text{eccentric anomaly} \\\\
                        r_p & = \\text{periapsis radius} \\\\
                        r_a & = \\text{apoapsis radius}
                    \\end{aligned}
    
            
    """
    class AnomalyType:
        """
        
                    The type of Anomaly.
                
        
        Members:
        
          TrueAnomaly : True Anomaly
        
          MeanAnomaly : Mean Anomaly
        
          EccentricAnomaly : Eccentric Anomaly
        """
        EccentricAnomaly: typing.ClassVar[COE.AnomalyType]  # value = <AnomalyType.EccentricAnomaly: 2>
        MeanAnomaly: typing.ClassVar[COE.AnomalyType]  # value = <AnomalyType.MeanAnomaly: 1>
        TrueAnomaly: typing.ClassVar[COE.AnomalyType]  # value = <AnomalyType.TrueAnomaly: 0>
        __members__: typing.ClassVar[dict[str, COE.AnomalyType]]  # value = {'TrueAnomaly': <AnomalyType.TrueAnomaly: 0>, 'MeanAnomaly': <AnomalyType.MeanAnomaly: 1>, 'EccentricAnomaly': <AnomalyType.EccentricAnomaly: 2>}
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
    class Element:
        """
        
                    Classical Orbital Element enumeration.
        
                
        
        Members:
        
          SemiMajorAxis : Semi-Major Axis
        
          Eccentricity : Eccentricity
        
          Inclination : Inclination
        
          Aop : Argument of Perigee
        
          Raan : Right Angle of the Ascending Node
        
          TrueAnomaly : True Anomaly
        
          MeanAnomaly : Mean Anomaly
        
          EccentricAnomaly : Eccentric Anomaly
        
          ArgumentOfLatitude : Argument of Latitude
        """
        Aop: typing.ClassVar[COE.Element]  # value = <Element.Aop: 4>
        ArgumentOfLatitude: typing.ClassVar[COE.Element]  # value = <Element.ArgumentOfLatitude: 8>
        EccentricAnomaly: typing.ClassVar[COE.Element]  # value = <Element.EccentricAnomaly: 7>
        Eccentricity: typing.ClassVar[COE.Element]  # value = <Element.Eccentricity: 1>
        Inclination: typing.ClassVar[COE.Element]  # value = <Element.Inclination: 2>
        MeanAnomaly: typing.ClassVar[COE.Element]  # value = <Element.MeanAnomaly: 6>
        Raan: typing.ClassVar[COE.Element]  # value = <Element.Raan: 3>
        SemiMajorAxis: typing.ClassVar[COE.Element]  # value = <Element.SemiMajorAxis: 0>
        TrueAnomaly: typing.ClassVar[COE.Element]  # value = <Element.TrueAnomaly: 5>
        __members__: typing.ClassVar[dict[str, COE.Element]]  # value = {'SemiMajorAxis': <Element.SemiMajorAxis: 0>, 'Eccentricity': <Element.Eccentricity: 1>, 'Inclination': <Element.Inclination: 2>, 'Aop': <Element.Aop: 4>, 'Raan': <Element.Raan: 3>, 'TrueAnomaly': <Element.TrueAnomaly: 5>, 'MeanAnomaly': <Element.MeanAnomaly: 6>, 'EccentricAnomaly': <Element.EccentricAnomaly: 7>, 'ArgumentOfLatitude': <Element.ArgumentOfLatitude: 8>}
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
    def cartesian(cartesian_state: tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity], gravitational_parameter: ostk.physics.unit.Derived) -> COE:
        """
                        Create a `COE` model from Cartesian state.
        
                        Args:
                            cartesian_state (CartesianState): The Cartesian state.
                            gravitational_parameter (float): The gravitational parameter of the central body.
        
                        Returns:
                            COE: The `COE` model.
        """
    @staticmethod
    @typing.overload
    def compute_angular_momentum(semi_major_axis: ostk.core.type.Real, eccentricity: ostk.core.type.Real, gravitational_parameter: ostk.physics.unit.Derived) -> ostk.core.type.Real:
        """
                        Compute the angular momentum from the semi-major axis and the eccentricity.
        
                        Args:
                            semi_major_axis (float): The semi-major axis. In meters.
                            eccentricity (float): The eccentricity.
                            gravitational_parameter (Derived): The gravitational parameter of the central body.
        
                        Returns:
                            Derived: The angular momentum.
        """
    @staticmethod
    @typing.overload
    def compute_angular_momentum(semi_latus_rectum: ostk.core.type.Real, gravitational_parameter: ostk.physics.unit.Derived) -> ostk.core.type.Real:
        """
                        Compute the angular momentum from the semi-latus rectum.
        
                        Args:
                            semi_latus_rectum (float): The semi-latus rectum. In meters.
                            gravitational_parameter (Derived): The gravitational parameter of the central body.
        
                        Returns:
                            Derived: The angular momentum.
        """
    @staticmethod
    def compute_ltan(raan: ostk.physics.unit.Angle, instant: ostk.physics.time.Instant, sun: ostk.physics.environment.object.celestial.Sun = ...) -> ostk.physics.time.Time:
        """
                        Compute the Local Time of the Ascending Node (LTAN) from the RAAN and instant.
        
                        Args:
                            raan (Angle): The Right Ascension of the Ascending Node.
                            instant (Instant): The instant at which to compute LTAN.
                            sun (Sun): The Sun model.
        
                        Returns:
                            float: The Local Time of the Ascending Node (LTAN) in hours.
        """
    @staticmethod
    def compute_ltdn(raan: ostk.physics.unit.Angle, instant: ostk.physics.time.Instant, sun: ostk.physics.environment.object.celestial.Sun = ...) -> ostk.physics.time.Time:
        """
                        Compute the Local Time of the Descending Node (LTDN) from the RAAN and instant.
        
                        Args:
                            raan (Angle): The Right Ascension of the Descending Node.
                            instant (Instant): The instant at which to compute LTDN.
                            sun (Sun): The Sun model.
        
                        Returns:
                            float: The Local Time of the Descending Node (LTDN) in hours.
        """
    @staticmethod
    def compute_mean_ltan(raan: ostk.physics.unit.Angle, instant: ostk.physics.time.Instant, sun: ostk.physics.environment.object.celestial.Sun = ...) -> ostk.physics.time.Time:
        """
                        Compute the Mean Local Time of the Ascending Node (MLTAN) from the RAAN and instant.
        
                        Args:
                            raan (Angle): The Right Ascension of the Ascending Node.
                            instant (Instant): The instant at which to compute MLTAN.
                            sun (Sun): The Sun model.
        
                        Returns:
                            float: The Mean Local Time of the Ascending Node (MLTAN) in hours.
        """
    @staticmethod
    def compute_mean_ltdn(raan: ostk.physics.unit.Angle, instant: ostk.physics.time.Instant, sun: ostk.physics.environment.object.celestial.Sun = ...) -> ostk.physics.time.Time:
        """
                        Compute the Mean Local Time of the Descending Node (MLTDN) from the RAAN and instant.
        
                        Args:
                            raan (Angle): The Right Ascension of the Descending Node.
                            instant (Instant): The instant at which to compute MLTDN.
                            sun (Sun): The Sun model.
        
                        Returns:
                            float: The Mean Local Time of the Descending Node (MLTDN) in hours.
        """
    @staticmethod
    def compute_radial_distance(semi_latus_rectum: ostk.core.type.Real, eccentricity: ostk.core.type.Real, true_anomaly: ostk.core.type.Real) -> ostk.core.type.Real:
        """
                        Compute the radial distance from the semi-latus rectum and the eccentricity.
        
                        Args:
                            semi_latus_rectum (float): The semi-latus rectum. In meters.
                            eccentricity (float): The eccentricity.
                            true_anomaly (float): The true anomly. In degrees.
        
                        Returns:
                            Length: The radial distance.
        """
    @staticmethod
    def compute_semi_latus_rectum(semi_major_axis: ostk.core.type.Real, eccentricity: ostk.core.type.Real) -> ostk.core.type.Real:
        """
                        Compute the semi-latus rectum from the semi-major axis and the eccentricity.
        
                        Args:
                            semi_major_axis (float): The semi-major axis. In meters.
                            eccentricity (float): The eccentricity.
        
                        Returns:
                            Length: The semi-latus rectum.
        """
    @staticmethod
    def eccentric_anomaly_from_mean_anomaly(mean_anomaly: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real, tolerance: ostk.core.type.Real) -> ostk.physics.unit.Angle:
        """
                        Compute the eccentric anomaly from the mean anomaly.
        
                        Args:
                            mean_anomaly (Angle): The mean anomaly.
                            eccentricity (float): The eccentricity.
                            tolerance (float): The tolerance of the root solver.
        
                        Returns:
                            Angle: The eccentric anomaly.
        """
    @staticmethod
    def eccentric_anomaly_from_true_anomaly(true_anomaly: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real) -> ostk.physics.unit.Angle:
        """
                        Compute the eccentric anomaly from the true anomaly.
        
                        Args:
                            true_anomaly (Angle): The true anomaly.
                            eccentricity (float): The eccentricity.
        
                        Returns:
                            Angle: The eccentric anomaly.
        """
    @staticmethod
    def from_SI_vector(vector: numpy.ndarray[numpy.float64[6, 1]], anomaly_type: COE.AnomalyType) -> COE:
        """
                        Create a `COE` model from a state vector in SI units.
        
                        Args:
                            vector (Vector6d): The state vector.
                            anomaly_type (AnomalyType): The type of anomaly.
        
                        Returns:
                            COE: The `COE` model.
        """
    @staticmethod
    @typing.overload
    def frozen_orbit(semi_major_axis: ostk.physics.unit.Length, celestial_object: ostk.physics.environment.object.Celestial, eccentricity: ostk.core.type.Real = ..., inclination: ostk.physics.unit.Angle = ..., raan: ostk.physics.unit.Angle = ..., aop: ostk.physics.unit.Angle = ..., true_anomaly: ostk.physics.unit.Angle = ...) -> COE:
        """
                        Build a `COE` model of a frozen orbit.
        
                        The critical angles for inclination are 63.4349 degrees and 116.5651 degrees.
                        The critical angles for AoP are 90.0 degrees and 270.0 degrees.
        
                        At a minimum, a semi-major axis and shared pointer to a central celestial body with a defined J2 and J3
                        must be provided. In this case, the inclination and AoP are set to critical angles, and the eccentricity
                        is derived from inclination. RAAN and true anomaly default to zero degrees.
        
                        Additionally, the following combinations of inputs are supported:
                        - AoP (inclination set to critical value, eccentricity derived)
                        - AoP and eccentricity (inclination derived)
                        - AoP and inclination, but at least one of them must be a critical value (eccentricity derived)
                        - Inclination (AoP set to critical value, eccentricity derived)
                        - Eccentricity (AoP set to critical value, inclination derived)
        
                        Note that inclination and eccentricity cannot both be provided.
        
                        RAAN and True Anomaly may be provided alongside any of these arguments, and will be passed through
                        to the resulting COE as they do not impact the frozen orbit condition.
        
                        Args:
                            semi_major_axis (Length): The semi-major axis.
                            celestial_object (Celestial): The celestial object.
                            eccentricity (float): The eccentricity.
                            inclination (Angle): The inclination.
                            raan (Angle): The right ascension of the ascending node.
                            aop (Angle): The argument of periapsis.
                            true_anomaly (Angle): The true anomaly.
        
                        Returns:
                            COE: The `COE` model.
        """
    @staticmethod
    @typing.overload
    def frozen_orbit(semi_major_axis: ostk.physics.unit.Length, equatorial_radius: ostk.physics.unit.Length, j2: ostk.core.type.Real, j3: ostk.core.type.Real, eccentricity: ostk.core.type.Real = ..., inclination: ostk.physics.unit.Angle = ..., raan: ostk.physics.unit.Angle = ..., aop: ostk.physics.unit.Angle = ..., true_anomaly: ostk.physics.unit.Angle = ...) -> COE:
        """
                        Build a `COE` model of a frozen orbit.
        
                        The critical angles for inclination are 63.4349 degrees and 116.5651 degrees.
                        The critical angles for AoP are 90.0 degrees and 270.0 degrees.
        
                        At a minimum, a semi-major axis, equatorial radius, J2, and J3 must be provided. In this case,
                        the inclination and AoP are set to critical angles, and the eccentricity is derived from inclination.
                        RAAN and true anomaly default to zero degrees.
        
                        Additionally, the following combinations of inputs are supported:
                        - AoP (inclination set to critical value, eccentricity derived)
                        - AoP and eccentricity (inclination derived)
                        - AoP and inclination, but at least one of them must be a critical value (eccentricity derived)
                        - Inclination (AoP set to critical value, eccentricity derived)
                        - Eccentricity (AoP set to critical value, inclination derived)
        
                        Note that inclination and eccentricity cannot both be provided.
        
                        RAAN and True Anomaly may be provided alongside any of these arguments, and will be passed through
                        to the resulting COE as they do not impact the frozen orbit condition.
        
                        Args:
                            semi_major_axis (Length): The semi-major axis.
                            equatorial_radius (Length): The equatorial radius.
                            j2 (float): The second zonal harmonic coefficient.
                            j3 (float): The third zonal harmonic coefficient.
                            eccentricity (float): The eccentricity.
                            inclination (Angle): The inclination.
                            raan (Angle): The right ascension of the ascending node.
                            aop (Angle): The argument of periapsis.
                            true_anomaly (Angle): The true anomaly.
        
                        Returns:
                            COE: The `COE` model.
        """
    @staticmethod
    def mean_anomaly_from_eccentric_anomaly(eccentric_anomaly: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real) -> ostk.physics.unit.Angle:
        """
                        Compute the mean anomaly from the eccentric anomaly.
        
                        Args:
                            eccentric_anomaly (Angle): The eccentric anomaly.
                            eccentricity (float): The eccentricity.
        
                        Returns:
                            Angle: The mean anomaly.
        """
    @staticmethod
    def string_from_element(element: COE.Element) -> ostk.core.type.String:
        """
                        Get the string representation of an element.
        
                        Args:
                            element (Element): The element.
        
                        Returns:
                            str: The string representation.
        """
    @staticmethod
    def true_anomaly_from_eccentric_anomaly(eccentric_anomaly: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real) -> ostk.physics.unit.Angle:
        """
                        Compute the true anomaly from the eccentric anomaly.
        
                        Args:
                            eccentric_anomaly (Angle): The eccentric anomaly.
                            eccentricity (float): The eccentricity.
        
                        Returns:
                            Angle: The true anomaly.
        """
    @staticmethod
    def true_anomaly_from_mean_anomaly(mean_anomaly: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real, tolerance: ostk.core.type.Real) -> ostk.physics.unit.Angle:
        """
                        Compute the true anomaly from the mean anomaly.
        
                        Args:
                            mean_anomaly (Angle): The mean anomaly.
                            eccentricity (float): The eccentricity.
                            tolerance (float): The tolerance of the root solver.
        
                        Returns:
                            Angle: The true anomaly.
        """
    @staticmethod
    def undefined() -> COE:
        """
                        Create an undefined `COE` model.
        
                        Returns:
                            COE: The undefined `COE` model.
        """
    def __eq__(self, arg0: COE) -> bool:
        ...
    def __init__(self, semi_major_axis: ostk.physics.unit.Length, eccentricity: ostk.core.type.Real, inclination: ostk.physics.unit.Angle, raan: ostk.physics.unit.Angle, aop: ostk.physics.unit.Angle, true_anomaly: ostk.physics.unit.Angle) -> None:
        """
                        Constructor.
        
                        Args:
                            semi_major_axis (Length): The semi-major axis.
                            eccentricity (float): The eccentricity.
                            inclination (Angle): The inclination.
                            raan (Angle): The right ascension of the ascending node.
                            aop (Angle): The argument of periapsis.
                            true_anomaly (Angle): The true anomaly.
        """
    def __ne__(self, arg0: COE) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_SI_vector(self, anomaly_type: COE.AnomalyType) -> numpy.ndarray[numpy.float64[6, 1]]:
        """
                       Get the state vector of the COE in the specified anomaly type.
        
                       Args:
                          anomaly_type (AnomalyType): The type of anomaly.
        
                       Returns:
                          numpy.ndarray: The state vector of the COE in the specified anomaly type.
        """
    def get_angular_momentum(self, arg0: ostk.physics.unit.Derived) -> ostk.physics.unit.Derived:
        """
                        Get the angular momentum of the COE.
        
                        Args:
                            gravitational_parameter (Derived): The gravitational parameter of the central body.
        
                        Returns:
                            Derived: The angular momentum of the COE.
        """
    def get_aop(self) -> ostk.physics.unit.Angle:
        """
                        Get the argument of periapsis of the COE.
        
                        Returns:
                            Angle: The argument of periapsis of the COE.
        """
    def get_apoapsis_radius(self) -> ostk.physics.unit.Length:
        """
                        Get the apoapsis radius of the COE.
        
                        Returns:
                            Length: The apoapsis radius of the COE.
        """
    def get_argument_of_latitude(self) -> ostk.physics.unit.Angle:
        """
                        Get the argument of latitude of the COE.
        
                        Returns:
                            Angle: The argument of latitude (sum of argument of periapsis and true anomaly).
        """
    def get_cartesian_state(self, gravitational_parameter: ostk.physics.unit.Derived, frame: ostk.physics.coordinate.Frame) -> tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity]:
        """
                       Get the Cartesian state of the COE.
        
                       Args:
                          gravitational_parameter (double): The gravitational parameter of the central body.
                          frame (Frame): The reference frame in which to express the Cartesian state.
        
                       Returns:
                          CartesianState: The Cartesian state of the COE.
        """
    def get_eccentric_anomaly(self) -> ostk.physics.unit.Angle:
        """
                        Get the eccentric anomaly of the COE.
        
                        Returns:
                            Angle: The eccentric anomaly of the COE.
        """
    def get_eccentricity(self) -> ostk.core.type.Real:
        """
                        Get the eccentricity of the COE.
        
                        Returns:
                            float: The eccentricity of the COE.
        """
    def get_inclination(self) -> ostk.physics.unit.Angle:
        """
                        Get the inclination of the COE.
        
                        Returns:
                            Angle: The inclination of the COE.
        """
    def get_mean_anomaly(self) -> ostk.physics.unit.Angle:
        """
                        Get the mean anomaly of the COE.
        
                        Returns:
                            Angle: The mean anomaly of the COE.
        """
    def get_mean_motion(self, gravitational_parameter: ostk.physics.unit.Derived) -> ostk.physics.unit.Derived:
        """
                       Get the mean motion of the COE.
        
                       Args:
                          gravitational_parameter (Derived): The gravitational parameter of the central body.
        
                       Returns:
                          Derived: The mean motion of the COE.
        """
    def get_nodal_precession_rate(self, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, j2: ostk.core.type.Real) -> ostk.physics.unit.Derived:
        """
                       Get the nodal precession of the COE.
        
                       Args:
                          gravitational_parameter (Derived): The gravitational parameter of the central body.
                          equatorial_radius (Length): The equatorial radius of the central body.
                          j2 (float): The second zonal harmonic coefficient of the central body.
        
                       Returns:
                          Derived: The nodal precession of the COE.
        """
    def get_orbital_period(self, gravitational_parameter: ostk.physics.unit.Derived) -> ostk.physics.time.Duration:
        """
                       Get the orbital period of the COE.
        
                       Args:
                          gravitational_parameter (double): The gravitational parameter of the central body.
        
                       Returns:
                          Duration: The orbital period of the COE.
        """
    def get_periapsis_radius(self) -> ostk.physics.unit.Length:
        """
                        Get the periapsis radius of the COE.
        
                        Returns:
                            Length: The periapsis radius of the COE.
        """
    def get_raan(self) -> ostk.physics.unit.Angle:
        """
                        Get the right ascension of the ascending node of the COE.
        
                        Returns:
                            Angle: The right ascension of the ascending node of the COE.
        """
    def get_radial_distance(self) -> ostk.physics.unit.Length:
        """
                       Get the radial distance of the COE.
        
                       Returns:
                          Length: The radial distance of the COE.
        """
    def get_semi_latus_rectum(self) -> ostk.physics.unit.Length:
        """
                       Get the semi-latus rectum of the COE.
        
                       Returns:
                          Length: The semilatus rectum of the COE.
        """
    def get_semi_major_axis(self) -> ostk.physics.unit.Length:
        """
                        Get the semi-major axis of the COE.
        
                        Returns:
                            Length: The semi-major axis of the COE.
        """
    def get_true_anomaly(self) -> ostk.physics.unit.Angle:
        """
                        Get the true anomaly of the COE.
        
                        Returns:
                            Angle: The true anomaly of the COE.
        """
    def is_defined(self) -> bool:
        """
                        Check if the COE is defined.
        
                        Returns:
                            bool: True if the COE is defined, False otherwise.
        """
