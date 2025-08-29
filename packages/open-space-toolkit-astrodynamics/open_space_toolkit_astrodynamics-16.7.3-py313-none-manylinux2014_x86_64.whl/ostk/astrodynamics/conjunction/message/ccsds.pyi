from __future__ import annotations
import numpy
import ostk.astrodynamics.trajectory
import ostk.core.container
import ostk.core.filesystem
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['CDM']
class CDM:
    """
    
                Conjunction Data Message.
    
                Ref: https://public.ccsds.org/Pubs/508x0b1e2s.pdf
    
            
    """
    class Data:
        """
        
                    Conjunction Data Message data.
        
                    Ref: https://public.ccsds.org/Pubs/508x0b1e2s.pdf
        
                
        """
        def __init__(self, time_last_observation_start: ostk.physics.time.Instant, time_last_observation_end: ostk.physics.time.Instant, recommended_od_span: ostk.physics.time.Duration, actual_od_span: ostk.physics.time.Duration, observations_available: ostk.core.type.Integer, observations_used: ostk.core.type.Integer, tracks_available: ostk.core.type.Integer, tracks_used: ostk.core.type.Integer, residuals_accepted: ostk.core.type.Real, weighted_rms: ostk.core.type.Real, area_pc: ostk.core.type.Real, area_drag: ostk.core.type.Real, area_srp: ostk.core.type.Real, mass: ostk.physics.unit.Mass, cd_area_over_mass: ostk.core.type.Real, cr_area_over_mass: ostk.core.type.Real, thrust_acceleration: ostk.core.type.Real, sedr: ostk.core.type.Real, state: ostk.astrodynamics.trajectory.State = ..., covariance_matrix: numpy.ndarray[numpy.float64[m, n]] = ...) -> None:
            """
                        Constructor.
            
                        Args:
                            time_last_observation_start (Instant): The time of the last observation start.
                            time_last_observation_end (Instant): The time of the last observation end.
                            recommended_od_span (Duration): The recommended OD span.
                            actual_od_span (Duration): The actual OD span.
                            observations_available (int): The number of observations available.
                            observations_used (int): The number of observations used.
                            tracks_available (int): The number of tracks available.
                            tracks_used (int): The number of tracks used.
                            residuals_accepted (float): The residuals accepted.
                            weighted_rms (float): The weighted RMS.
                            area_pc (float): The area PC.
                            area_drag (float): The area drag.
                            area_srp (float): The area SRP.
                            mass (Mass): The mass.
                            cd_area_over_mass (float): The CD area over mass.
                            cr_area_over_mass (float): The CR area over mass.
                            thrust_acceleration (float): The thrust acceleration.
                            sedr (float): The SEDR.
                            state (State): The state.
                            covariance_matrix (MatrixXd): The covariance matrix.
            """
        @property
        def actual_od_span(self) -> ostk.physics.time.Duration:
            """
                            The actual OD span.
            """
        @property
        def area_drag(self) -> ostk.core.type.Real:
            """
                            The area drag.
            """
        @property
        def area_pc(self) -> ostk.core.type.Real:
            """
                            The area PC.
            """
        @property
        def area_srp(self) -> ostk.core.type.Real:
            """
                            The area SRP.
            """
        @property
        def cd_area_over_mass(self) -> ostk.core.type.Real:
            """
                            The CD area over mass.
            """
        @property
        def covariance_matrix(self) -> numpy.ndarray[numpy.float64[m, n]]:
            """
                            The covariance matrix.
            """
        @property
        def cr_area_over_mass(self) -> ostk.core.type.Real:
            """
                            The CR area over mass.
            """
        @property
        def mass(self) -> ostk.physics.unit.Mass:
            """
                            The mass.
            """
        @property
        def observations_available(self) -> ostk.core.type.Integer:
            """
                            The number of observations available.
            """
        @property
        def observations_used(self) -> ostk.core.type.Integer:
            """
                            The number of observations used.
            """
        @property
        def recommended_od_span(self) -> ostk.physics.time.Duration:
            """
                            The recommended OD span.
            """
        @property
        def residuals_accepted(self) -> ostk.core.type.Real:
            """
                            The residuals accepted.
            """
        @property
        def sedr(self) -> ostk.core.type.Real:
            """
                            The SEDR.
            """
        @property
        def state(self) -> ostk.astrodynamics.trajectory.State:
            """
                            The state.
            """
        @property
        def thrust_acceleration(self) -> ostk.core.type.Real:
            """
                            The thrust acceleration.
            """
        @property
        def time_last_observation_end(self) -> ostk.physics.time.Instant:
            """
                            The time of the last observation end.
            """
        @property
        def time_last_observation_start(self) -> ostk.physics.time.Instant:
            """
                            The time of the last observation start.
            """
        @property
        def tracks_available(self) -> ostk.core.type.Integer:
            """
                            The number of tracks available.
            """
        @property
        def tracks_used(self) -> ostk.core.type.Integer:
            """
                            The number of tracks used.
            """
        @property
        def weighted_rms(self) -> ostk.core.type.Real:
            """
                            The weighted RMS.
            """
    class Header:
        """
        
                    Conjunction Data Message header.
        
                    Ref: https://public.ccsds.org/Pubs/508x0b1e2s.pdf
        
                
        """
        def __init__(self, *, ccsds_cdm_version: ostk.core.type.String, comment: ostk.core.type.String = ..., creation_date: ostk.physics.time.Instant, originator: ostk.core.type.String, message_for: ostk.core.type.String = ..., message_id: ostk.core.type.String) -> None:
            """
                            Constructor.
            
                            Args:
                                ccsds_cdm_version (str): The CCSDS CDM version.
                                comment (str): The comment.
                                creation_date (Instant): The creation date.
                                originator (str): The originator.
                                message_for (str): The message for.
                                message_id (str): The message ID.
            """
        @property
        def ccsds_cdm_version(self) -> ostk.core.type.String:
            """
                            The CCSDS CDM version.
            """
        @property
        def comment(self) -> ostk.core.type.String:
            """
                            The comment.
            """
        @property
        def creation_date(self) -> ostk.physics.time.Instant:
            """
                            The creation date.
            """
        @property
        def message_for(self) -> ostk.core.type.String:
            """
                            The message for.
            """
        @property
        def message_id(self) -> ostk.core.type.String:
            """
                            The message ID.
            """
        @property
        def originator(self) -> ostk.core.type.String:
            """
                            The originator.
            """
    class Metadata:
        """
        
                    Conjunction Data Message metadata.
        
                    Ref: https://public.ccsds.org/Pubs/508x0b1e2s.pdf
        
                
        """
        def __init__(self, *, comment: ostk.core.type.String = ..., object: ostk.core.type.String, object_designator: ostk.core.type.Integer, catalog_name: ostk.core.type.String = ..., object_name: ostk.core.type.String, international_designator: ostk.core.type.String, object_type: CDM.ObjectType, operator_contact_position: ostk.core.type.String = ..., operator_organization: ostk.core.type.String = ..., operator_phone: ostk.core.type.String = ..., operator_email: ostk.core.type.String = ..., ephemeris_name: ostk.core.type.String, covariance_method: ostk.core.type.String, maneuverable: ostk.core.type.String, orbit_center: ostk.core.type.String = ..., reference_frame: ostk.core.type.String, gravity_model: ostk.core.type.String = ..., atmospheric_model: ostk.core.type.String = ..., n_body_perturbations: ostk.core.type.String = ..., solar_radiation_pressure: bool = False, earth_tides: bool = False, in_track_thrust: bool = False) -> None:
            """
                            Constructor.
            
                            Args:
                                comment (str): The comment.
                                object (str): The object.
                                object_designator (int): The object designator.
                                catalog_name (str): The catalog name.
                                object_name (str): The object name.
                                international_designator (str): The international designator.
                                object_type (ObjectType): The object type.
                                operator_contact_position (str): The operator contact position.
                                operator_organization (str): The operator organization.
                                operator_phone (str): The operator phone.
                                operator_email (str): The operator email.
                                ephemeris_name (str): The ephemeris name.
                                covariance_method (str): The covariance method.
                                maneuverable (str): The maneuverable.
                                orbit_center (str): The orbit center.
                                reference_frame (str): The reference frame.
                                gravity_model (str): The gravity model.
                                atmospheric_model (str): The atmospheric model.
                                n_body_perturbations (str): The n-body perturbations.
                                solar_radiation_pressure (bool): The solar radiation pressure.
                                earth_tides (bool): The earth tides.
                                in_track_thrust (bool): The in-track thrust.
            """
        @property
        def atmospheric_model(self) -> ostk.core.type.String:
            """
                            The atmospheric model.
            """
        @property
        def catalog_name(self) -> ostk.core.type.String:
            """
                            The catalog name.
            """
        @property
        def comment(self) -> ostk.core.type.String:
            """
                            The comment.
            """
        @property
        def covariance_method(self) -> ostk.core.type.String:
            """
                            The covariance method.
            """
        @property
        def earth_tides(self) -> bool:
            """
                            The earth tides.
            """
        @property
        def ephemeris_name(self) -> ostk.core.type.String:
            """
                            The ephemeris name.
            """
        @property
        def gravity_model(self) -> ostk.core.type.String:
            """
                            The gravity model.
            """
        @property
        def in_track_thrust(self) -> bool:
            """
                            The in-track thrust.
            """
        @property
        def international_designator(self) -> ostk.core.type.String:
            """
                            The international designator.
            """
        @property
        def maneuverable(self) -> ostk.core.type.String:
            """
                            The maneuverable.
            """
        @property
        def n_body_perturbations(self) -> ostk.core.type.String:
            """
                            The n-body perturbations.
            """
        @property
        def object(self) -> ostk.core.type.String:
            """
                            The object.
            """
        @property
        def object_designator(self) -> ostk.core.type.Integer:
            """
                            The object designator.
            """
        @property
        def object_name(self) -> ostk.core.type.String:
            """
                            The object name.
            """
        @property
        def object_type(self) -> CDM.ObjectType:
            """
                            The object type.
            """
        @property
        def operator_contact_position(self) -> ostk.core.type.String:
            """
                            The operator contact position.
            """
        @property
        def operator_email(self) -> ostk.core.type.String:
            """
                            The operator email.
            """
        @property
        def operator_organization(self) -> ostk.core.type.String:
            """
                            The operator organization.
            """
        @property
        def operator_phone(self) -> ostk.core.type.String:
            """
                            The operator phone.
            """
        @property
        def orbit_center(self) -> ostk.core.type.String:
            """
                            The orbit center.
            """
        @property
        def reference_frame(self) -> ostk.core.type.String:
            """
                            The reference frame.
            """
        @property
        def solar_radiation_pressure(self) -> bool:
            """
                            The solar radiation pressure.
            """
    class ObjectType:
        """
        
                    Object type.
                
        
        Members:
        
          Payload : Payload
        
          RocketBody : Rocket Body
        
          Debris : Debris
        
          Unknown : Unknown
        
          Other : Other
        """
        Debris: typing.ClassVar[CDM.ObjectType]  # value = <ObjectType.Debris: 2>
        Other: typing.ClassVar[CDM.ObjectType]  # value = <ObjectType.Other: 4>
        Payload: typing.ClassVar[CDM.ObjectType]  # value = <ObjectType.Payload: 0>
        RocketBody: typing.ClassVar[CDM.ObjectType]  # value = <ObjectType.RocketBody: 1>
        Unknown: typing.ClassVar[CDM.ObjectType]  # value = <ObjectType.Unknown: 3>
        __members__: typing.ClassVar[dict[str, CDM.ObjectType]]  # value = {'Payload': <ObjectType.Payload: 0>, 'RocketBody': <ObjectType.RocketBody: 1>, 'Debris': <ObjectType.Debris: 2>, 'Unknown': <ObjectType.Unknown: 3>, 'Other': <ObjectType.Other: 4>}
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
    class RelativeMetadata:
        """
        
                    Relative metadata.
        
                    Ref: https://public.ccsds.org/Pubs/508x0b1e2s.pdf
        
                
        """
        def __init__(self, *, comment: ostk.core.type.String = ..., time_of_closest_approach: ostk.physics.time.Instant, miss_distance: ostk.physics.unit.Length, relative_position: ostk.physics.coordinate.Position = ..., relative_velocity: ostk.physics.coordinate.Velocity = ..., start_screen_period: ostk.physics.time.Instant, end_screen_period: ostk.physics.time.Instant, screen_volume_frame: ostk.core.type.String = ..., screen_volume_shape: ostk.core.type.String = ..., screen_volume_x: ostk.core.type.Real = ..., screen_volume_y: ostk.core.type.Real = ..., screen_volume_z: ostk.core.type.Real = ..., screen_entry_time: ostk.physics.time.Instant, screen_exit_time: ostk.physics.time.Instant, collision_probability: ostk.core.type.Real, collision_probability_method: ostk.core.type.String) -> None:
            """
                            Constructor.
            
                            Args:
                                comment (str): The comment.
                                time_of_closest_approach (Instant): The time of closest approach.
                                miss_distance (Distance): The miss distance.
                                relative_position (Position): The relative position.
                                relative_velocity (Velocity): The relative velocity.
                                start_screen_period (Instant): The start screen period.
                                end_screen_period (Instant): The end screen period.
                                screen_volume_frame (str): The screen volume frame.
                                screen_volume_shape (str): The screen volume shape.
                                screen_volume_x (float): The screen volume x.
                                screen_volume_y (float): The screen volume y.
                                screen_volume_z (float): The screen volume z.
                                screen_entry_time (Instant): The screen entry time.
                                screen_exit_time (Instant): The screen exit time.
                                collision_probability (Probability): The collision probability.
                                collision_probability_method (str): The collision probability method.
            """
        @property
        def collision_probability(self) -> ostk.core.type.Real:
            """
                            The collision probability.
            """
        @property
        def collision_probability_method(self) -> ostk.core.type.String:
            """
                            The collision probability method.
            """
        @property
        def comment(self) -> ostk.core.type.String:
            """
                            The comment.
            """
        @property
        def end_screen_period(self) -> ostk.physics.time.Instant:
            """
                            The end screen period.
            """
        @property
        def miss_distance(self) -> ostk.physics.unit.Length:
            """
                            The miss distance.
            """
        @property
        def relative_position(self) -> ostk.physics.coordinate.Position:
            """
                            The relative position.
            """
        @property
        def relative_velocity(self) -> ostk.physics.coordinate.Velocity:
            """
                            The relative velocity.
            """
        @property
        def screen_entry_time(self) -> ostk.physics.time.Instant:
            """
                            The screen entry time.
            """
        @property
        def screen_exit_time(self) -> ostk.physics.time.Instant:
            """
                            The screen exit time.
            """
        @property
        def screen_volume_frame(self) -> ostk.core.type.String:
            """
                            The screen volume frame.
            """
        @property
        def screen_volume_shape(self) -> ostk.core.type.String:
            """
                            The screen volume shape.
            """
        @property
        def screen_volume_x(self) -> ostk.core.type.Real:
            """
                            The screen volume x.
            """
        @property
        def screen_volume_y(self) -> ostk.core.type.Real:
            """
                            The screen volume y.
            """
        @property
        def screen_volume_z(self) -> ostk.core.type.Real:
            """
                            The screen volume z.
            """
        @property
        def start_screen_period(self) -> ostk.physics.time.Instant:
            """
                            The start screen period.
            """
        @property
        def time_of_closest_approach(self) -> ostk.physics.time.Instant:
            """
                            The time of closest approach.
            """
    @staticmethod
    def dictionary(dictionary: ostk.core.container.Dictionary) -> CDM:
        """
                        Get the CDM dictionary.
        
                        Returns:
                            Dictionary: The CDM dictionary.
        """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> CDM:
        """
                    Load a CDM from a file.
        
                    Args:
                        file (str): The file to load.
        
                    Returns:
                        CDM: The loaded CDM.
        """
    @staticmethod
    def object_type_from_string(string: ostk.core.type.String) -> CDM.ObjectType:
        """
                        Get the object type from a string.
        
                        Args:
                            string (str): The string to get the object type from.
        
                        Returns:
                            CDM::ObjectType: The object type.
        """
    @staticmethod
    def parse(string: ostk.core.type.String) -> CDM:
        """
                        Parse a CDM from a string.
        
                        Args:
                            string (str): The string to parse.
        
                        Returns:
                            CDM: The parsed CDM.
        """
    @staticmethod
    def undefined() -> CDM:
        """
                        Get an undefined CDM.
        
                        Returns:
                            CDM: An undefined CDM.
        """
    def __init__(self, header: typing.Any, relative_metadata: typing.Any, objects_metadata_array: list[...], objects_data_array: list[...]) -> None:
        """
                        Constructor.
        
                        Args:
                            header (CDM::Header): The CDM header.
                            relative_metadata (CDM::RelativeMetadata): The relative metadata.
                            objects_metadata_array (Array<CDM::Metadata>): The objects metadata array.
                            objects_data_array (Array<CDM::Data>): The objects data array.
        """
    def get_ccsds_cdm_version(self) -> ostk.core.type.String:
        """
                        Get the CCSDS CDM version.
        
                        Returns:
                            str: The CCSDS CDM version.
        """
    def get_collision_probability(self) -> ostk.core.type.Real:
        """
                        Get the collision probability.
        
                        Returns:
                            Probability: The collision probability.
        """
    def get_collision_probability_method(self) -> ostk.core.type.String:
        """
                        Get the collision probability method.
        
                        Returns:
                            str: The collision probability method.
        """
    def get_creation_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the creation instant.
        
                        Returns:
                            Instant: The creation instant.
        """
    def get_data_array(self) -> list[...]:
        """
                        Get the objects data array.
        
                    Returns:
                        Array<CDM::Data>: The objects data array.
        """
    def get_header(self) -> ...:
        """
                        Get the CDM header.
        
                    Returns:
                        CDM::Header: The CDM header.
        """
    def get_message_for(self) -> ostk.core.type.String:
        """
                        Get the message for.
        
                        Returns:
                            str: The message for.
        """
    def get_message_id(self) -> ostk.core.type.String:
        """
                        Get the message ID.
        
                        Returns:
                            str: The message ID.
        """
    def get_metadata_array(self) -> list[...]:
        """
                        Get the objects metadata array.
        
                    Returns:
                        Array<CDM::Metadata>: The objects metadata array.
        """
    def get_miss_distance(self) -> ostk.physics.unit.Length:
        """
                        Get the miss distance.
        
                        Returns:
                            Distance: The miss distance.
        """
    def get_object_data_at(self, index: int) -> ...:
        """
                        Get the object data at the specified index.
        
                        Args:
                            index (int): The index of the object data.
        
                        Returns:
                            Data: The object data.
        """
    def get_object_metadata_at(self, index: int) -> ...:
        """
                        Get the object metadata at the specified index.
        
                        Args:
                            index (int): The index of the object metadata.
        
                        Returns:
                            CDM::Metadata: The object metadata.
        """
    def get_originator(self) -> ostk.core.type.String:
        """
                        Get the originator.
        
                        Returns:
                            str: The originator.
        """
    def get_relative_metadata(self) -> ...:
        """
                        Get the relative metadata.
        
                    Returns:
                        CDM::RelativeMetadata: The relative metadata.
        """
    def get_relative_position(self) -> ostk.physics.coordinate.Position:
        """
                        Get the relative position.
        
                        Returns:
                            Position: The relative position.
        """
    def get_relative_velocity(self) -> ostk.physics.coordinate.Velocity:
        """
                        Get the relative velocity.
        
                        Returns:
                            Velocity: The relative velocity.
        """
    def get_time_of_closest_approach(self) -> ostk.physics.time.Instant:
        """
                        Get the time of closest approach.
        
                        Returns:
                            Instant: The time of closest approach.
        """
    def is_defined(self) -> bool:
        """
                        Check if the CDM is defined.
        
                        Returns:
                            bool: True if the CDM is defined, False otherwise.
        """
