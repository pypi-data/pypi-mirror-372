from __future__ import annotations
import ostk.core.filesystem
import ostk.core.type
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['TLE']
class TLE:
    """
    
                A Two-Line Element set (TLE).
    
                A TLE is a data format encoding a list of orbital elements of an Earth-orbiting object for a given point in time
    
                Reference:
                    https://en.wikipedia.org/wiki/Two-line_element_set
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def can_parse(first_line: ostk.core.type.String, second_line: ostk.core.type.String) -> bool:
        """
                        Check if a TLE can be parsed from two strings.
        
                        Args:
                            first_line (str): The first line of the TLE.
                            second_line (str): The second line of the TLE.
        
                        Returns:
                            bool: True if the TLE can be parsed, False otherwise.
        """
    @staticmethod
    @typing.overload
    def construct(satellite_name: ostk.core.type.String, satellite_number: ostk.core.type.Integer, classification: ostk.core.type.String, international_designator: ostk.core.type.String, epoch: ostk.physics.time.Instant, mean_motion_first_time_derivative_divided_by_two: ostk.core.type.Real, mean_motion_second_time_derivative_divided_by_six: ostk.core.type.Real, b_star_drag_term: ostk.core.type.Real, ephemeris_type: ostk.core.type.Integer, element_set_number: ostk.core.type.Integer, inclination: ostk.physics.unit.Angle, raan: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real, aop: ostk.physics.unit.Angle, mean_anomaly: ostk.physics.unit.Angle, mean_motion: ostk.physics.unit.Derived, revolution_number_at_epoch: ostk.core.type.Integer) -> TLE:
        """
                        Construct a TLE.
        
                        Args:
                            satellite_name (str): The name of the satellite.
                            satellite_number (int): The satellite number.
                            classification (str): The classification.
                            international_designator (str): The international designator.
                            epoch (Instant): The epoch.
                            mean_motion_first_time_derivative_divided_by_two (float): The mean motion first time derivative divided by two.
                            mean_motion_second_time_derivative_divided_by_six (float): The mean motion second time derivative divided by six.
                            b_star_drag_term (float): The B* drag term.
                            ephemeris_type (int): The ephemeris type.
                            element_set_number (int): The element set number.
                            inclination (Angle): The inclination.
                            raan (Angle): The right ascension of the ascending node.
                            eccentricity (float): The eccentricity.
                            aop (Angle): The argument of perigee.
                            mean_anomaly (Angle): The mean anomaly.
                            mean_motion (float): The mean motion.
                            revolution_number_at_epoch (int): The revolution number at epoch.
        
                        Returns:
                            TLE: The constructed TLE.
        """
    @staticmethod
    @typing.overload
    def construct(satellite_number: ostk.core.type.Integer, classification: ostk.core.type.String, international_designator: ostk.core.type.String, epoch: ostk.physics.time.Instant, mean_motion_first_time_derivative_divided_by_two: ostk.core.type.Real, mean_motion_second_time_derivative_divided_by_six: ostk.core.type.Real, b_star_drag_term: ostk.core.type.Real, ephemeris_type: ostk.core.type.Integer, element_set_number: ostk.core.type.Integer, inclination: ostk.physics.unit.Angle, raan: ostk.physics.unit.Angle, eccentricity: ostk.core.type.Real, aop: ostk.physics.unit.Angle, mean_anomaly: ostk.physics.unit.Angle, mean_motion: ostk.physics.unit.Derived, revolution_number_at_epoch: ostk.core.type.Integer) -> TLE:
        """
                        Construct a TLE.
        
                        Args:
                            satellite_number (int): The satellite number.
                            classification (str): The classification.
                            international_designator (str): The international designator.
                            epoch (Instant): The epoch.
                            mean_motion_first_time_derivative_divided_by_two (float): The mean motion first time derivative divided by two.
                            mean_motion_second_time_derivative_divided_by_six (float): The mean motion second time derivative divided by six.
                            b_star_drag_term (float): The B* drag term.
                            ephemeris_type (int): The ephemeris type.
                            element_set_number (int): The element set number.
                            inclination (Angle): The inclination.
                            raan (Angle): The right ascension of the ascending node.
                            eccentricity (float): The eccentricity.
                            aop (Angle): The argument of perigee.
                            mean_anomaly (Angle): The mean anomaly.
                            mean_motion (float): The mean motion.
                            revolution_number_at_epoch (int): The revolution number at epoch.
        
                        Returns:
                            TLE: The constructed TLE.
        """
    @staticmethod
    def generate_checksum(string: ostk.core.type.String) -> ostk.core.type.Integer:
        """
                        Generate the checksum of a string.
        
                        Args:
                            string (str): The string.
        
                        Returns:
                            int: The checksum.
        """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> TLE:
        """
                        Load a TLE from a file.
        
                        Args:
                            file (str): The path to the file.
        
                        Returns:
                            TLE: The loaded TLE.
        """
    @staticmethod
    def parse(string: ostk.core.type.String) -> TLE:
        """
                        Parse a TLE from a string.
        
                        Args:
                            string (str): The string to parse.
        
                        Returns:
                            TLE: The parsed TLE.
        """
    @staticmethod
    def undefined() -> TLE:
        """
                        Create an undefined `TLE` object.
        
                        Returns:
                            TLE: The undefined `TLE` object.
        """
    def __eq__(self, arg0: TLE) -> bool:
        ...
    @typing.overload
    def __init__(self, first_line: ostk.core.type.String, second_line: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            first_line (str): The first line of the TLE.
                            second_line (str): The second line of the TLE.
        """
    @typing.overload
    def __init__(self, satellite_name: ostk.core.type.String, first_line: ostk.core.type.String, second_line: ostk.core.type.String) -> None:
        """
                        Constructor.
        
                        Args:
                            satellite_name (str): The name of the satellite.
                            first_line (str): The first line of the TLE.
                            second_line (str): The second line of the TLE.
        """
    def __ne__(self, arg0: TLE) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_aop(self) -> ostk.physics.unit.Angle:
        """
                        Get the argument of perigee.
        
                        Returns:
                            Angle: The argument of perigee.
        """
    def get_b_star_drag_term(self) -> ostk.core.type.Real:
        """
                        Get the B* drag term.
        
                        Returns:
                            float: The B* drag term.
        """
    def get_classification(self) -> ostk.core.type.String:
        """
                        Get the classification.
        
                        Returns:
                            str: The classification.
        """
    def get_eccentricity(self) -> ostk.core.type.Real:
        """
                        Get the eccentricity.
        
                        Returns:
                            float: The eccentricity.
        """
    def get_element_set_number(self) -> ostk.core.type.Integer:
        """
                        Get the element set number.
        
                        Returns:
                            int: The element set number.
        """
    def get_ephemeris_type(self) -> ostk.core.type.Integer:
        """
                        Get the ephemeris type.
        
                        Returns:
                            int: The ephemeris type.
        """
    def get_epoch(self) -> ostk.physics.time.Instant:
        """
                        Get the epoch.
        
                        Returns:
                            Instant: The epoch.
        """
    def get_first_line(self) -> ostk.core.type.String:
        """
                        Get the first line of the TLE.
        
                        Returns:
                            str: The first line of the TLE.
        """
    def get_first_line_checksum(self) -> ostk.core.type.Integer:
        """
                        Get the checksum of the first line.
        
                        Returns:
                            int: The checksum of the first line.
        """
    def get_inclination(self) -> ostk.physics.unit.Angle:
        """
                        Get the inclination.
        
                        Returns:
                            Angle: The inclination.
        """
    def get_international_designator(self) -> ostk.core.type.String:
        """
                        Get the international designator.
        
                        Returns:
                            str: The international designator.
        """
    def get_mean_anomaly(self) -> ostk.physics.unit.Angle:
        """
                        Get the mean anomaly.
        
                        Returns:
                            Angle: The mean anomaly.
        """
    def get_mean_motion(self) -> ostk.physics.unit.Derived:
        """
                        Get the mean motion.
        
                        Returns:
                            float: The mean motion.
        """
    def get_mean_motion_first_time_derivative_divided_by_two(self) -> ostk.core.type.Real:
        """
                        Get the mean motion first time derivative divided by two.
        
                        Returns:
                            float: The mean motion first time derivative divided by two.
        """
    def get_mean_motion_second_time_derivative_divided_by_six(self) -> ostk.core.type.Real:
        """
                        Get the mean motion second time derivative divided by six.
        
                        Returns:
                            float: The mean motion second time derivative divided by six.
        """
    def get_raan(self) -> ostk.physics.unit.Angle:
        """
                        Get the right ascension of the ascending node.
        
                        Returns:
                            Angle: The right ascension of the ascending node.
        """
    def get_revolution_number_at_epoch(self) -> ostk.core.type.Integer:
        """
                        Get the revolution number at epoch.
        
                        Returns:
                            int: The revolution number at epoch.
        """
    def get_satellite_name(self) -> ostk.core.type.String:
        """
                        Get the name of the satellite.
        
                        Returns:
                            str: The name of the satellite.
        """
    def get_satellite_number(self) -> ostk.core.type.Integer:
        """
                        Get the satellite number.
        
                        Returns:
                            int: The satellite number.
        """
    def get_second_line(self) -> ostk.core.type.String:
        """
                        Get the second line of the TLE.
        
                        Returns:
                            str: The second line of the TLE.
        """
    def get_second_line_checksum(self) -> ostk.core.type.Integer:
        """
                        Get the checksum of the second line.
        
                        Returns:
                            int: The checksum of the second line.
        """
    def is_defined(self) -> bool:
        """
                        Check if the `TLE` object is defined.
        
                        Returns:
                            bool: True if the `TLE` object is defined, False otherwise.
        """
    def set_epoch(self, epoch: ostk.physics.time.Instant) -> None:
        """
                        Set the epoch.
        
                        Args:
                            epoch (Instant): The epoch.
        """
    def set_revolution_number_at_epoch(self, revolution_number: ostk.core.type.Integer) -> None:
        """
                        Set the revolution number at epoch.
        
                        Args:
                            revolution_number (int): The revolution number at epoch.
        """
    def set_satellite_number(self, satellite_number: ostk.core.type.Integer) -> None:
        """
                        Set the satellite number.
        
                        Args:
                            satellite_number (int): The satellite number.
        """
