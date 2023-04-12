import sys
sys.path.append('../../lib')

import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import numpy as np
import ctypes

import xglut
# Draw two triangles using two VAOs and two shaders

class Triangles:
    def __init__(self, vertices):
        self.vao = None
        self.vbo = None
        self.vertices = vertices
        self.upload()
        
    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
            gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        
        gl.glEnableVertexAttribArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def draw(self):
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        gl.glBindVertexArray(0)


    def dispose(self):
        gl.glDeleteVertexArrays(1, self.vao)
        gl.glDeleteBuffers(1, self.vbo)


class App(xglut.GLFWViewer):
    def __init__(self, width,height,title="Two Triangles"):
        super().__init__(width,height,title)
        
        # build shaders
        with open('./vertex.vs', 'r') as f:
            src = f.readlines()
            
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex, src)
        gl.glCompileShader(vertex)
        
        with open('./green.fs', 'r') as f:
            src = f.readlines()
        fragment0 = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment0, src)
        gl.glCompileShader(fragment0)
        
        with open('./yellow.fs', 'r') as f:
            src = f.readlines()
        fragment1 = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment1, src)
        gl.glCompileShader(fragment1)
        
        self.shader0 = gl.glCreateProgram()
        gl.glAttachShader(self.shader0, vertex)
        gl.glAttachShader(self.shader0, fragment0)
        gl.glLinkProgram(self.shader0)
        
        
        self.shader1 = gl.glCreateProgram()
        gl.glAttachShader(self.shader1, vertex)
        gl.glAttachShader(self.shader1, fragment1)
        gl.glLinkProgram(self.shader1)
        
        gl.glDeleteShader(vertex)
        gl.glDeleteShader(fragment0)
        gl.glDeleteShader(fragment1)
        


        # -----------------------------------
        # Init vertex data
        vertices0 = [
            0.5,  0.5, 0.0,  # top right
            0.5, -0.5, 0.0,  # bottom right
            -0.5,  0.5, 0.0   # top left
            ]

        vertices1 = [
            0.5, -0.5, 0.0,  # bottom right
            -0.5, -0.5, 0.0,  # bottom left
            -0.5,  0.5, 0.0   # top left
            ]
        vertices0 = np.array(vertices0, np.float32)
        vertices1 = np.array(vertices1, np.float32)
        self.triangle0 = Triangles(vertices0)
        self.triangle1 = Triangles(vertices1)
        
        self.view()


    def draw(self):
        
        # main drawing
        gl.glClearColor(0.0, 0.0, 0.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(self.shader0)
        self.triangle0.draw()

        gl.glUseProgram(self.shader1)
        self.triangle1.draw()


    def dispose(self):
        gl.glDeleteProgram(self.shader0)
        gl.glDeleteProgram(self.shader1)
        self.triangle0.dispose()
        self.triangle1.dispose()


if __name__ == "__main__":
    myApp = App(640,480)
