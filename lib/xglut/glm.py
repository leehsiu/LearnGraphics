import numpy as np
from scipy.spatial.transform import Rotation as R

__all__ = [
    'perspective',
    'lookAt',
]

def deg2rad(degree):
    return degree * np.pi / 180


def normalize(vec):
    return vec / np.linalg.norm(vec)

# https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml

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



# https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
def lookAt(position, center, up):
    z = normalize(position - center)
    x = normalize(np.cross(up, z))
    y = np.cross(z, x)
    
    rot = np.vstack([x,y,z])
    trans = - rot @ position
    mat = np.eye(4)
    mat[:3,:3] = rot
    mat[:3, -1] = trans
    return mat
