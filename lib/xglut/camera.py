import glfw
import glfw.GLFW as GLFW

from .glm import perspective
from .glm import lookAt
from .glm import vrrot
from .glm import sph2cart
from .glm import cart2sph

import numpy as np

__all__ = [
    'PerspectiveCamera',
    'OrbitPerspectiveCamera']

class PerspectiveCamera:
    def __init__(self,fov,aspect,near,far):
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far
    
        self.projection = np.eye(4)
        self.matrix = np.eye(4)
        
        self.up = np.array([0.,1.,0.])
        self.position = np.array([0., 0., 0.])
    
    def update_projection_matrix(self):
        self.projection = perspective(self.fov,self.aspect,self.near,self.far)
        
    def lookAt(self,target):
        self.matrix = lookAt(self.position,target,self.up)  
        
class OrbitPerspectiveCamera(PerspectiveCamera):
    def __init__(self, fov, aspect, near, far):
        super().__init__(fov, aspect, near, far)
        
        self.center = np.array([0., 0., 0.])
        
        self.min_radius = 1e-3
        self.max_radius = np.inf
        
        self.min_phi = 1e-3
        self.max_phi = np.pi-1e-3
        
        self.action = None
        self.xprev = None
        self.yprev = None
    
    
    def update_matrix(self):
        self.lookAt(self.center)
        

    
    def handle_mouse_button(self, window, key, action, mods):
        if action == GLFW.GLFW_RELEASE:
            self.action = None
        elif action == GLFW.GLFW_PRESS:        
            if key== GLFW.GLFW_MOUSE_BUTTON_LEFT:
                self.action = "MOVE"
                self.xprev,self.yprev = glfw.get_cursor_pos(window)
                
                
    def handle_cursor_pos(self,window,xpos,ypos):
        if self.action is None:
            return
        
        xoffset = xpos - self.xprev
        yoffset = ypos - self.yprev
                
        
        sensitivity = 0.01
        xoffset *= sensitivity
        yoffset *= sensitivity

        if self.action == "MOVE":
            align_mat = vrrot(self.up, np.array([0., 1., 0.]))
            
            vector = self.position - self.center
            vector = align_mat @ vector
            
            spherical = cart2sph(vector)
            spherical[0] -= xoffset
            spherical[1] -= yoffset
            spherical[1] = np.clip(spherical[1],self.min_phi,self.max_phi)
            
            vector = sph2cart(spherical)
            
            vector = align_mat.T @ vector
            
            self.position = self.center + vector
            self.update_matrix()

        
        self.xprev = xpos
        self.yprev = ypos
        
        
        
    
    def handle_scroll(self,window,xoffset,yoffset):
        vector = self.position - self.center
        radius = np.linalg.norm(vector)
        unit_vector = vector / radius
        radius -= yoffset
        radius = np.clip(radius, self.min_radius, self.max_radius)
        position = unit_vector * radius
        self.position = position
        self.update_matrix()
        
            
        
        
        
        