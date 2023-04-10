import sys
sys.path.append('../../lib')

import xglut
import xglut.glm as glm

import glfw
import glfw.GLFW as GLFW
import ctypes
import numpy as np
import OpenGL.GL as gl

def normalize(vec):
    return vec / np.linalg.norm(vec)


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
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,  5 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * ctypes.sizeof(ctypes.c_float),
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
        self.shader = xglut.Shader.load('./vertex.vs', './fragment.fs')

        # -----------------------------------
        vertices = np.loadtxt('./cube.txt').astype(np.float32)

        self.triangle = Triangles(vertices)
        self.triangle.upload()

        self.texture0 = xglut.Texture('../../assets/textures/container.jpg')
        self.texture1 = xglut.Texture('../../assets/textures/awesomeface.png')

        self.cube_positions = np.array([
            0.0, 0.0, 0.0,
            2.0,  5.0, -15.0,
            -1.5, -2.2, -2.5,
            -3.8, -2.0, -12.3,
            2.4, -0.4, -3.5,
            -1.7,  3.0, -7.5,
            1.3, -2.0, -2.5,
            1.5,  2.0, -2.5,
            1.5,  0.2, -1.5,
            -1.3,  1.0, -1.5], np.float32).reshape(-1, 3)

        self.view()
        

    def handle_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)

    def draw(self):
            # main drawing
        gl.glClearColor(0.2, 0.3, 0.3, 1)
        
        # clear both color buffer and z-buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.shader.use()
        self.shader.set_uniform("texture0", 0)
        self.shader.set_uniform("texture1", 1)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        self.texture0.use()
        gl.glActiveTexture(gl.GL_TEXTURE1)
        self.texture1.use()

        projection_mat = glm.perspective(45, 640./480, 0.01, 100.0)
        projection_mat = projection_mat.astype(np.float32)
        self.shader.set_uniform("projection", projection_mat)
        
        
        radius = 10.0
        camX = np.sin(glfw.get_time()) * radius
        camZ = np.cos(glfw.get_time()) * radius
        view = lookAt(
            np.array([camX, 0.0, camZ]),
            np.array([0, 0, 0]),
            np.array([0, 1., 0.0])
        )
        print(view)

        self.shader.set_uniform("view", view)
        
        for i, r in enumerate(self.cube_positions):
            model_mat = np.eye(4)
            model_mat[:3, -1] = r
            axis = np.array([1.0, 0.3, 0.5])
            angle = i * 20.0
            model_mat[:3, :3] = glm.rotate(angle, axis)
            model_mat = model_mat.astype(np.float32)
            
            self.shader.set_uniform("model", model_mat)
            self.triangle.draw()

    def dispose(self):
        self.shader.dispose()
        self.triangle.dispose()
        self.texture0.dispose()
        self.texture1.dispose()


if __name__ == "__main__":
    app = App(640 ,480, 'camera')
