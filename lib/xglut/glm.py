import numpy as np
from scipy.spatial.transform import Rotation as R

__all__ = [
    'perspective',
    'lookAt',
]

def deg2rad(degree):
    return degree * np.pi / 180

def skew_symmetric(v):
    """skew symmetric form of cross-product matrix
    """
    mat =  np.array(
        [[0, -v[2], v[1]],
         [v[2], 0, -v[0]],
         [-v[1],v[0],0]])
    
    return mat

# those two implementations are identical

# def vrrot(vfrom,vto,eps=1e-9):
#     """calculate the rotation matrix that rotates vector a to b.
#     """
#     vfrom = normalize(vfrom)
#     vto = normalize(vto)
    
#     v = np.cross(vfrom,vto)
#     r = 1 + np.dot(vfrom,vto)
#     v_x = skew_symmetric(v)

#     if r < eps:
#         rot = -np.eye(3)
#     else:
#         rot = v_x + v_x @ v_x / r + np.eye(3)
    
#     return rot

def vrrot(vfrom,vto,eps=1e-9):
    """calculate the rotation matrix that rotates vector a to b.
    """
    vfrom = normalize(vfrom)
    vto = normalize(vto)
    
    r = 1 + np.dot(vfrom,vto)
    
    if r < eps:
        r = 0
        if np.abs(vfrom[0]) > np.abs(vfrom[2]):
            x = -vfrom[1]
            y = vfrom[0]
            z = 0
        else:
            x = 0
            y = -vfrom[2]
            z = vfrom[1]
    else:
        xyz = np.cross(vfrom,vto)
        x,y,z = xyz[0],xyz[1],xyz[2]
    
    w = r
    
    rot = R.from_quat([x,y,z,w]).as_matrix()
    
    return rot

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
    mat = R.from_rotvec(angle * normalize(axis)).as_matrix()
    return mat


def cart2sph(xyz,eps = 1e-9):
    radius = np.linalg.norm(xyz)
    if radius < eps:
        theta = 0
        phi = 0
    else:
        theta = np.arctan2(xyz[0],xyz[2])
        phi = np.arccos(np.clip(xyz[1]/radius,-1.0,1.0))
    
    return np.array([theta,phi,radius])

def sph2cart(input):
    theta, phi, radius = input[0],input[1],input[2]
    sin_phi_radius = np.sin( phi ) * radius
    
    x = sin_phi_radius * np.sin( theta )
    y = np.cos( phi ) * radius
    z = sin_phi_radius * np.cos( theta )
    return np.array([x,y,z])

    
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
