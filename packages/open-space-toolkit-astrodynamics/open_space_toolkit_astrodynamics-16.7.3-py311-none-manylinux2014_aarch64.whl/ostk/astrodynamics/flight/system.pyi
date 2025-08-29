from __future__ import annotations
import numpy
import ostk.astrodynamics.flight
import ostk.core.type
import ostk.mathematics.geometry.d3.object
import ostk.physics.unit
import typing
__all__ = ['PropulsionSystem', 'SatelliteSystem', 'SatelliteSystemBuilder']
class PropulsionSystem:
    """
    
                    A propulsion system.
    
                
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def default() -> PropulsionSystem:
        """
                            Return a default propulsion system.
        
                            Returns:
                                PropulsionSystem: A default propulsion system.
        """
    @staticmethod
    def undefined() -> PropulsionSystem:
        """
                            Return an undefined propulsion system.
        
                            Returns:
                                PropulsionSystem: An undefined propulsion system.
        """
    def __eq__(self, arg0: PropulsionSystem) -> bool:
        ...
    def __init__(self, thrust_si_unit: ostk.core.type.Real, specific_impulse_si_unit: ostk.core.type.Real) -> None:
        """
                            Construct a propulsion system.
        
                            Args:
                                thrust (float): Thrust in Newton.
                                specific_impulse (float): Specific impulse in Seconds.
        """
    def __ne__(self, arg0: PropulsionSystem) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_acceleration(self, mass: ostk.physics.unit.Mass) -> ostk.core.type.Real:
        """
                            Return the acceleration.
        
                            Args:
                                mass (float): Mass in Kilograms.
        
                            Returns:
                                float: The acceleration in Meters per Second squared.
        """
    def get_mass_flow_rate(self) -> ostk.core.type.Real:
        """
                            Return the mass flow rate.
        
                            Returns:
                                float: The mass flow rate in Kilograms per Second.
        """
    def get_specific_impulse(self) -> ostk.core.type.Real:
        """
                            Return the specific impulse.
        
                            Returns:
                                float: The specific impulse in Seconds.
        """
    def get_thrust(self) -> ostk.core.type.Real:
        """
                            Return the thrust.
        
                            Returns:
                                float: The thrust in Newton.
        """
    def is_defined(self) -> bool:
        """
                            Check if the propulsion system is defined.
        
                            Returns:
                                bool: True if the propulsion system is defined, False otherwise.
        """
class SatelliteSystem(ostk.astrodynamics.flight.System):
    """
    
                    A Satellite System.
    
                
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def default() -> SatelliteSystem:
        """
                            Create a default satellite system.
        
                            Returns:
                                SatelliteSystem: The default satellite system.
        """
    @staticmethod
    def undefined() -> SatelliteSystem:
        """
                            Create an undefined satellite system.
        
                            Returns:
                                SatelliteSystem: The undefined satellite system.
        """
    def __eq__(self, arg0: SatelliteSystem) -> bool:
        ...
    def __init__(self, mass: ostk.physics.unit.Mass, satellite_geometry: ostk.mathematics.geometry.d3.object.Composite, inertia_tensor: numpy.ndarray[numpy.float64[3, 3]], cross_sectional_surface_area: ostk.core.type.Real, drag_coefficient: ostk.core.type.Real, propulsion_system: PropulsionSystem = ...) -> None:
        """
                            Constructor.
        
                            Args:
                                mass (Mass): The mass of the satellite system.
                                satellite_geometry (Composite): The geometry of the satellite system.
                                inertia_tensor (np.ndarray): The inertia tensor of the satellite system.
                                cross_sectional_surface_area (float): The cross-sectional surface area of the satellite system.
                                drag_coefficient (float): The drag coefficient of the satellite system.
                                propulsion_system (PropulsionSystem): The propulsion system of the satellite system.
        """
    def __ne__(self, arg0: SatelliteSystem) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_cross_sectional_surface_area(self) -> ostk.core.type.Real:
        """
                            Get the cross-sectional surface area of the satellite system.
        
                            Returns:
                                float: The cross-sectional surface area of the satellite system.
        """
    def get_drag_coefficient(self) -> ostk.core.type.Real:
        """
                            Get the drag coefficient of the satellite system.
        
                            Returns:
                                float: The drag coefficient of the satellite system.
        """
    def get_inertia_tensor(self) -> numpy.ndarray[numpy.float64[3, 3]]:
        """
                            Get the inertia tensor of the satellite system.
        
                            Returns:
                                Matrix3d: The inertia tensor of the satellite system.
        """
    def get_propulsion_system(self) -> PropulsionSystem:
        """
                            Get the propulsion system of the satellite system.
        
                            Returns:
                                PropulsionSystem: The propulsion system of the satellite system.
        """
    def is_defined(self) -> bool:
        """
                            Check if the satellite system is defined.
        
                            Returns:
                                bool: True if the satellite system is defined, False otherwise.
        """
class SatelliteSystemBuilder:
    """
    
                    A Satellite System Builder, meant to simplify creation of a SatelliteSystem, by allowing
                    you to only specify the parameters you want. There are two ways of doing this:
    
                    Chaining together your desired parameters like so:
    
                    .. code-block:: python
    
                        satellite_system = SatelliteSystemBuilder().with_dry_mass(X).with_area(Y).build()
    
                    Using the default SatelliteSystem and changing one parameters like so:
    
                    .. code-block:: python
    
                        satellite_system = SatelliteSystemBuilder.default().with_dry_mass(X)
    
                
    """
    @staticmethod
    def default() -> SatelliteSystemBuilder:
        """
                            Create a satellite system builder with default values.
        
                            Returns:
                                SatelliteSystem: The satellite system builder with default values.
        """
    def __init__(self) -> None:
        """
                            Constructor.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def build(self) -> SatelliteSystem:
        """
                            Build a new satellite system.
        
                            Returns:
                                SatelliteSystem: A new satellite system.
        """
    def with_cross_sectional_surface_area(self, cross_sectional_surface_area: ostk.core.type.Real) -> SatelliteSystemBuilder:
        """
                            Set the dry mass.
        
                            Args:
                                cross_sectional_surface_area (float): The cross-sectional surface area.
        
                            Returns:
                                SatelliteSystemBuilder: The builder.
        """
    def with_drag_coefficient(self, drag_coefficient: ostk.core.type.Real) -> SatelliteSystemBuilder:
        """
                            Set the drag coefficient.
        
                            Args:
                                drag_coefficient (float): The drag coefficient.
        
                            Returns:
                                SatelliteSystemBuilder: The builder.
        """
    def with_dry_mass(self, dry_mass: ostk.physics.unit.Mass) -> SatelliteSystemBuilder:
        """
                            Set the dry mass.
        
                            Args:
                                dry_mass (Mass): The dry mass.
        
                            Returns:
                                SatelliteSystemBuilder: The builder.
        """
    def with_geometry(self, geometry: ostk.mathematics.geometry.d3.object.Composite) -> SatelliteSystemBuilder:
        """
                            Set the geometry.
        
                            Args:
                                geometry (Composite): The geometry.
        
                            Returns:
                                SatelliteSystemBuilder: The builder.
        """
    def with_inertia_tensor(self, inertia_tensor: numpy.ndarray[numpy.float64[3, 3]]) -> SatelliteSystemBuilder:
        """
                            Set the inertia tensor.
        
                            Args:
                                inertia_tensor (Matrix3d): The inertia tensor.
        
                            Returns:
                                SatelliteSystemBuilder: The builder.
        """
    def with_propulsion_system(self, propulsion_system: PropulsionSystem) -> SatelliteSystemBuilder:
        """
                            Set the propulsion system.
        
                            Args:
                                propulsion_system (PropulsionSystem): The propulsion system.
        
                            Returns:
                                SatelliteSystemBuilder: The builder.
        """
