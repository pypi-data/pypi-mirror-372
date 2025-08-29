from __future__ import annotations
import ostk.astrodynamics.trajectory
import ostk.core.container
import ostk.core.filesystem
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.time
import ostk.physics.unit
__all__ = ['OPM']
class OPM:
    """
    
                The SpaceX OPM message.
    
                See Also:
                    `SpaceX OPM <https://public.ccsds.org/Pubs/502x0b3e1.pdf>`_.
    
            
    """
    class Deployment:
        """
        
                    The deployment of the SpaceX OPM message.
        
                
        """
        def __init__(self, name: ostk.core.type.String, sequence_number: ostk.core.type.Integer, mission_time: ostk.physics.time.Duration, date: ostk.physics.time.Instant, position: ostk.physics.coordinate.Position, velocity: ostk.physics.coordinate.Velocity, mean_perigee_altitude: ostk.physics.unit.Length, mean_apogee_altitude: ostk.physics.unit.Length, mean_inclination: ostk.physics.unit.Angle, mean_argument_of_perigee: ostk.physics.unit.Angle, mean_longitude_ascending_node: ostk.physics.unit.Angle, mean_mean_anomaly: ostk.physics.unit.Angle, ballistic_coefficient: ostk.core.type.Real) -> None:
            """
                            Constructor.
            
                            Args:
                                name (str): The name of the deployment.
                                sequence_number (int): The sequence number of the deployment.
                                mission_time (Duration): The mission time of the deployment.
                                date (Instant): The date of the deployment.
                                position (Position): The position of the deployment.
                                velocity (Velocity): The velocity of the deployment.
                                mean_perigee_altitude (Length): The mean perigee altitude of the deployment.
                                mean_apogee_altitude (Length): The mean apogee altitude of the deployment.
                                mean_inclination (Angle): The mean inclination of the deployment.
                                mean_argument_of_perigee (Angle): The mean argument of perigee of the deployment.
                                mean_longitude_ascending_node (Angle): The mean longitude of the ascending node of the deployment.
                                mean_mean_anomaly (Angle): The mean mean anomaly of the deployment.
                                ballistic_coefficient (float): The ballistic coefficient of the deployment.
            """
        def to_state(self) -> ostk.astrodynamics.trajectory.State:
            """
                            Convert the deployment to a state.
            
                            Returns:
                                state (State): The state of the deployment.
            """
        @property
        def ballistic_coefficient(self) -> ostk.core.type.Real:
            """
                            Get the ballistic coefficient of the deployment.
            
                            :type: float
            """
        @property
        def date(self) -> ostk.physics.time.Instant:
            """
                            Get the date of the deployment.
            
                            :type: Instant
            """
        @property
        def mean_apogee_altitude(self) -> ostk.physics.unit.Length:
            """
                            Get the mean apogee altitude of the deployment.
            
                            :type: Length
            """
        @property
        def mean_argument_of_perigee(self) -> ostk.physics.unit.Angle:
            """
                            Get the mean argument of perigee of the deployment.
            
                            :type: Angle
            """
        @property
        def mean_inclination(self) -> ostk.physics.unit.Angle:
            """
                            Get the mean inclination of the deployment.
            
                            :type: Angle
            """
        @property
        def mean_longitude_ascending_node(self) -> ostk.physics.unit.Angle:
            """
                            Get the mean longitude of the ascending node of the deployment.
            
                            :type: Angle
            """
        @property
        def mean_mean_anomaly(self) -> ostk.physics.unit.Angle:
            """
                            Get the mean mean anomaly of the deployment.
            
                            :type: Angle
            """
        @property
        def mean_perigee_altitude(self) -> ostk.physics.unit.Length:
            """
                            Get the mean perigee altitude of the deployment.
            
                            :type: Length
            """
        @property
        def mission_time(self) -> ostk.physics.time.Duration:
            """
                            Get the mission time of the deployment.
            
                            :type: Duration
            """
        @property
        def name(self) -> ostk.core.type.String:
            """
                            Get the name of the deployment.
            
                            :type: str
            """
        @property
        def position(self) -> ostk.physics.coordinate.Position:
            """
                            Get the position of the deployment.
            
                            :type: Position
            """
        @property
        def sequence_number(self) -> ostk.core.type.Integer:
            """
                            Get the sequence number of the deployment.
            
                            :type: int
            """
        @property
        def velocity(self) -> ostk.physics.coordinate.Velocity:
            """
                            Get the velocity of the deployment.
            
                            :type: Velocity
            """
    class Header:
        """
        
                    The header of the SpaceX OPM message.
        
                
        """
        def __init__(self, generation_date: ostk.physics.time.Instant, launch_date: ostk.physics.time.Instant) -> None:
            """
                            Constructor.
            
                            Args:
                                generation_date (Instant): The date at which the OPM message was generated.
                                launch_date (Instant): The date at which the spacecraft was launched.
            """
        @property
        def generation_date(self) -> ostk.physics.time.Instant:
            """
                            Get the date at which the OPM message was generated.
            
                            Returns:
                                instant (Instant): The date at which the OPM message was generated.
            """
        @property
        def launch_date(self) -> ostk.physics.time.Instant:
            """
                            Get the date at which the spacecraft was launched.
            
                            Returns:
                                instant (Instant): The date at which the spacecraft was launched.
            """
    @staticmethod
    def dictionary(dictionary: ostk.core.container.Dictionary) -> OPM:
        """
                        Build an OPM message from a dictionary.
        
                        Args:
                            dictionary (dict): The dictionary containing the OPM message information.
        
                        Returns:
                            opm (OPM): The OPM message.
        """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> OPM:
        """
                        Load an OPM message from a file.
        
                        Args:
                            file (str): The path to the file containing the OPM message.
        
                        Returns:
                            opm (OPM): The OPM message.
        """
    @staticmethod
    def parse(string: ostk.core.type.String) -> OPM:
        """
                        Parse an OPM message from a string.
        
                        Args:
                            string (str): The string containing the OPM message.
        
                        Returns:
                            opm (OPM): The OPM message.
        """
    @staticmethod
    def undefined() -> OPM:
        """
                        Return an undefined OPM message.
        
                        Returns:
                            opm (OPM): An undefined OPM message.
        """
    def __init__(self, header: typing.Any, deployments: list[...]) -> None:
        """
                        Constructor.
        
                        Args:
                            header (Header): The header of the OPM message.
                            deployments (list[Deployment]): The deployments of the OPM message.
        """
    def get_deployment_at(self, index: int) -> ...:
        """
                        Get the deployment at a given index.
        
                        Args:
                            index (int): The index of the deployment.
        
                        Returns:
                            deployment (Deployment): The deployment at the given index.
        """
    def get_deployment_with_name(self, name: ostk.core.type.String) -> ...:
        """
                        Get the deployment with a given name.
        
                        Args:
                            name (str): The name of the deployment.
        
                        Returns:
                            deployment (Deployment): The deployment with the given name.
        """
    def get_deployments(self) -> list[...]:
        """
                        Get the deployments of the OPM message.
        
                        Returns:
                            deployments (list[Deployment]): The deployments of the OPM message.
        """
    def get_header(self) -> ...:
        """
                        Get the header of the OPM message.
        
                        Returns:
                            header (Header): The header of the OPM message.
        """
    def is_defined(self) -> bool:
        """
                        Check if the OPM message is defined.
        
                        Returns:
                            is_defined (bool): True if the OPM message is defined, False otherwise.
        """
