from __future__ import annotations
import ostk.astrodynamics.trajectory
import ostk.physics.coordinate
import ostk.physics.unit
__all__ = ['compute_off_nadir_angles']
def compute_off_nadir_angles(state: ostk.astrodynamics.trajectory.State, target_position: ostk.physics.coordinate.Position) -> tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle, ostk.physics.unit.Angle]:
    """
                Compute the along-track, cross-track and total off-nadir angle between the satellite and the target.
    
                - The along-track angle is the angle between the nadir vector [Z] and the projection of the satellite->target vector 
                  onto the plane defined by the satellite local horizontal (velocity vector in circular orbits) [X] and the nadir vector [Z].
                - The cross-track angle is the angle between the nadir vector [Z] and the projection of the satellite->target vector 
                  onto the plane defined by the negative orbital momentum vector [Y] and the nadir vector [Z].
                - The total off-nadir angle is the angle between the nadir vector [Z] and the satellite->target vector.
    
                Args:
                    state (State): The state of the satellite.
                    target_position (Position): The position of the target.
    
                Returns:
                    tuple[Angle, Angle, Angle]: The along-track, cross-track and total off-nadir angle between the satellite and the target.
    """
