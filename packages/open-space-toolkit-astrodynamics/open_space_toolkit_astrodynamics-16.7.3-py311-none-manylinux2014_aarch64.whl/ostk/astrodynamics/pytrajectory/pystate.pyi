from __future__ import annotations
import numpy as np
from ostk.astrodynamics.converters import coerce_to_instant
import ostk.astrodynamics.trajectory
from ostk.astrodynamics.trajectory import State
from ostk.astrodynamics.trajectory import StateBuilder
from ostk.astrodynamics.trajectory.state import CoordinateSubset
from ostk.astrodynamics.trajectory.state.coordinate_subset import AngularVelocity
from ostk.astrodynamics.trajectory.state.coordinate_subset import AttitudeQuaternion
from ostk.astrodynamics.trajectory.state.coordinate_subset import CartesianPosition
from ostk.astrodynamics.trajectory.state.coordinate_subset import CartesianVelocity
import ostk.physics.coordinate
from ostk.physics.coordinate import Frame
from ostk.physics.time import Instant
import re as re
__all__ = ['AngularVelocity', 'AttitudeQuaternion', 'CartesianPosition', 'CartesianVelocity', 'CoordinateSubset', 'Frame', 'Instant', 'POS_VEL_CANONICAL_FORMAT', 'State', 'StateBuilder', 'coerce_to_instant', 'custom_class_generator', 'from_dict', 'np', 're']
def custom_class_generator(frame: ostk.physics.coordinate.Frame, coordinate_subsets: list) -> type:
    """
    
        Emit a custom class type for States. This is meta-programming syntactic sugar on top of the StateBuilder class.
    
        StateType = State.template(frame, coordinate_subsets)
        state = StateType(instant, coordinates)
    
        is equivalent to
    
        state_builder = StateBuilder(frame, coordinate_subsets)
        state = state_builder.build(instant, coordinates)
        
    """
def from_dict(data: dict) -> ostk.astrodynamics.trajectory.State:
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
POS_VEL_CANONICAL_FORMAT: str = '(r|v)_(.*?)_(x|y|z)'
