from __future__ import annotations
import ostk.astrodynamics.trajectory.orbit.model
import ostk.astrodynamics.trajectory.orbit.model.kepler
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.unit
__all__ = ['BrouwerLyddaneMeanLong', 'BrouwerLyddaneMeanShort']
class BrouwerLyddaneMeanLong(ostk.astrodynamics.trajectory.orbit.model.BrouwerLyddaneMean):
    """
    
                Brouwer-Lyddane Mean (Long) orbit elements. Short periodic variations and secular variations are averaged.
    
            
    """
    @staticmethod
    def COE(coe: ostk.astrodynamics.trajectory.orbit.model.kepler.COE) -> BrouwerLyddaneMeanLong:
        """
                        Create a `BrouwerLyddaneMeanLong` model from classical orbital elements.
        
                        Args:
                            coe (COE): The classical orbital elements.
        
                        Returns:
                            BrouwerLyddaneMeanLong: The `BrouwerLyddaneMeanLong` model.
        """
    @staticmethod
    def cartesian(cartesian_state: tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity], gravitational_parameter: ostk.physics.unit.Derived) -> BrouwerLyddaneMeanLong:
        """
                        Create a `BrouwerLyddaneMeanLong` model from Cartesian state.
        
                        Args:
                            cartesian_state (CartesianState): The Cartesian state.
                            gravitational_parameter (float): The gravitational parameter of the central body.
        
                        Returns:
                            BrouwerLyddaneMeanLong: The `BrouwerLyddaneMeanLong` model.
        """
    @staticmethod
    def undefined() -> BrouwerLyddaneMeanLong:
        """
                        Create an undefined `BrouwerLyddaneMeanLong` model.
        
                        Returns:
                            BrouwerLyddaneMeanLong: The undefined `BrouwerLyddaneMeanLong` model.
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
    def to_coe(self) -> ostk.astrodynamics.trajectory.orbit.model.kepler.COE:
        """
                        Convert the `BrouwerLyddaneMeanLong` model to classical orbital elements.
        
                        Returns:
                            COE: The classical orbital elements.
        """
class BrouwerLyddaneMeanShort(ostk.astrodynamics.trajectory.orbit.model.BrouwerLyddaneMean):
    """
    
                Brouwer-Lyddane Mean (Short) orbit elements. Short periodic variations are averaged.
    
            
    """
    @staticmethod
    def COE(coe: ostk.astrodynamics.trajectory.orbit.model.kepler.COE) -> BrouwerLyddaneMeanShort:
        """
                        Create a `BrouwerLyddaneMeanShort` model from classical orbital elements.
        
                        Args:
                            coe (COE): The classical orbital elements.
        
                        Returns:
                            BrouwerLyddaneMeanShort: The `BrouwerLyddaneMeanShort` model.
        """
    @staticmethod
    def cartesian(cartesian_state: tuple[ostk.physics.coordinate.Position, ostk.physics.coordinate.Velocity], gravitational_parameter: ostk.physics.unit.Derived) -> BrouwerLyddaneMeanShort:
        """
                        Create a `BrouwerLyddaneMeanShort` model from Cartesian state.
        
                        Args:
                            cartesian_state (CartesianState): The Cartesian state.
                            gravitational_parameter (float): The gravitational parameter of the central body.
        
                        Returns:
                            BrouwerLyddaneMeanShort: The `BrouwerLyddaneMeanShort` model.
        """
    @staticmethod
    def undefined() -> BrouwerLyddaneMeanShort:
        """
                        Create an undefined `BrouwerLyddaneMeanShort` model.
        
                        Returns:
                            BrouwerLyddaneMeanShort: The undefined `BrouwerLyddaneMeanShort` model.
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
    def to_coe(self) -> ostk.astrodynamics.trajectory.orbit.model.kepler.COE:
        """
                        Convert the `BrouwerLyddaneMeanShort` model to classical orbital elements.
        
                        Returns:
                            COE: The classical orbital elements.
        """
