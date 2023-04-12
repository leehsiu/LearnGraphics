import sys
sys.path.append('../../lib')

import xglut
import xglut.glm as glm

import glfw
import glfw.GLFW as GLFW
import ctypes
import numpy as np
import OpenGL.GL as gl

# https://learnopengl.com/code_viewer_gh.php?code=src/2.lighting/
# 2.2.basic_lighting_specular/basic_lighting_specular.cpp


class Triangles:
    def __init__(self, vertices):
        self.vao = None
        self.vbo = None
        self.vertices = vertices

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,  6 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def draw(self):
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)

    def dispose(self):
        gl.glDeleteVertexArrays(1, self.vao)
        gl.glDeleteBuffers(1, self.vbo)



class App(xglut.GLFWViewer):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        # init opengl

        # enable z-buffering
        gl.glEnable(gl.GL_DEPTH_TEST)
        # -------------------------------------
        self.cube_shader = xglut.Shader.load('./vertex.vs', './fragment.fs')
        self.light_shader = xglut.Shader.load('./light.vs', './light.fs')

        # -----------------------------------
        vertices = np.loadtxt('./cube.txt').astype(np.float32)

        self.cube = Triangles(vertices)
        self.cube.upload()
        
        self.light_cube = Triangles(vertices)
        self.light_cube.upload()
        
        self.shininess = 20.0
        self.light_color = np.array([1.0, 1.0, 1.0])
        self.object_color = np.array([1.0, 0.5, 0.3])
        self.light_pos = np.array([1.2, 1.0, 2.0])
        

        
        

        self.camera = xglut.OrbitPerspectiveCamera(
            45,self.width*1.0/self.height,1e-2,100.)
        self.camera.position = np.array([0.,0.,3.])
        self.camera.center = np.array([0.,0.,0.])
        self.camera.update_projection_matrix()
        self.camera.update_matrix()
        
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_scroll_callback(self.window,self.scroll_callback)
        glfw.set_mouse_button_callback(self.window,self.mouse_button_callback)
        
        self.view()
        
    def scroll_callback(self,window,xoffset,yoffset):
        self.camera.handle_scroll(window,xoffset,yoffset) 
    
    def cursor_pos_callback(self,window,xpos,ypos):
        self.camera.handle_cursor_pos(window,xpos,ypos)
        
    def mouse_button_callback(self,window,key,action,mods):
        self.camera.handle_mouse_button(window,key,action,mods)
        
    
    def resize(self,window,width,height):
        super().resize(window,width,height)
        self.camera.aspect = self.width * 1.0 / self.height
        self.camera.update_projection_matrix()
        

        

    def handle_input(self):
             
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)
        
        elif glfw.get_key(self.window, GLFW.GLFW_KEY_UP) == GLFW.GLFW_PRESS:
            shininess = self.shininess + 1
            self.shininess = min(shininess, 250.0)
        elif glfw.get_key(self.window, GLFW.GLFW_KEY_DOWN) == GLFW.GLFW_PRESS:
            shininess = self.shininess - 1
            self.shininess = max(shininess, 1.0)
        
    

    def draw(self):
        # main drawing
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        
        # clear both color buffer and z-buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


        model_mat = np.eye(4)
        model_rot_mat = model_mat[:3,:3]
        model_normal_mat = model_rot_mat.T @ np.linalg.inv(model_rot_mat)
        
        self.cube_shader.use()
        self.cube_shader.set_uniform("projection", self.camera.projection)
        self.cube_shader.set_uniform("view", self.camera.matrix)
        self.cube_shader.set_uniform("model", model_mat)
        self.cube_shader.set_uniform("modelNormal", model_normal_mat)
        self.cube_shader.set_uniform("objectColor", self.object_color)
        self.cube_shader.set_uniform("lightColor", self.light_color)
        self.cube_shader.set_uniform("lightPos",self.light_pos)
        self.cube_shader.set_uniform("viewPos",self.camera.position)
        self.cube_shader.set_uniform("shininess",self.shininess)
        self.cube.draw()
        
        self.light_shader.use()
        
        model_mat = np.eye(4)
        model_mat[:3,:3] *= 0.2
        model_mat[:3, -1] = self.light_pos
        self.light_shader.set_uniform("projection", self.camera.projection)
        self.light_shader.set_uniform("view", self.camera.matrix)
        self.light_shader.set_uniform("model", model_mat)
        self.light_shader.set_uniform("lightColor", self.light_color)
        self.cube.draw()
        

    def dispose(self):
        self.cube_shader.dispose()
        self.light_shader.dispose()
        self.cube.dispose()
        self.light_cube.dispose()


if __name__ == "__main__":
    app = App(640 ,480, 'camera')
