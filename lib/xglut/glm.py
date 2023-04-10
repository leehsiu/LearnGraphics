import numpy as np
from scipy.spatial.transform import Rotation as R

def deg2rad(degree):
    return degree * np.pi / 180

def perspective(fov, aspect, z_near, z_far):
    fov = deg2rad(fov)
    
    f = 1./np.tan(fov/2)
    z_dist = z_far - z_near
    mat = np.array([
        f/aspect, 0, 0, 0,
        0, f, 0, 0,
        0, 0, -(z_far + z_near) / z_dist, -2 * z_far * z_near / z_dist,
        0, 0, -1, 0], np.float32).reshape(4, 4)
    return mat

def rotate(angle, axis):
    axis_norm = np.linalg.norm(axis,2)
    axis = axis / axis_norm
    angle = deg2rad(angle)
    mat = R.from_rotvec(angle * axis).as_matrix()
    return mat

    