import sys
sys.path.append('../../lib')

import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import numpy as np
import ctypes

import xglut

class Shaders:
    def __init__(self, vertex_shader, fragment_shader):
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex, vertex_shader)
        gl.glCompileShader(vertex)
        
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment, fragment_shader)
        gl.glCompileShader(fragment)
        
        self.shader = gl.glCreateProgram()
        gl.glAttachShader(self.shader, vertex)
        gl.glAttachShader(self.shader, fragment)
        gl.glLinkProgram(self.shader)
        
        gl.glDeleteShader(vertex)
        gl.glDeleteShader(fragment)
        
        # following does not work on MacOS 
        # v_shader = glshaders.compileShader(vertex_shader, gl.GL_VERTEX_SHADER)
        # f_shader = glshaders.compileShader(
        #     fragment_shader, gl.GL_FRAGMENT_SHADER)
        # self.shader = glshaders.compileProgram(
        #     v_shader, f_shader)

    @classmethod
    def load(cls, vertex_path, fragment_path):
        with open(vertex_path, 'r') as f:
            vertex_src = f.readlines()
        with open(fragment_path, 'r') as f:
            fragment_src = f.readlines()

        return cls(vertex_src, fragment_src)

    def use(self):
        gl.glUseProgram(self.shader)

    def dispose(self):
        gl.glDeleteProgram(self.shader)


# using two different VBOs to store vertex color and vertex position
class TrianglesMultiVBO:
    def __init__(self, vertices, colors):
        self.vao = None
        self.vbo_v = None
        self.vbo_c = None
        self.vertices = vertices
        self.colors = colors
        self.count = self.vertices.shape[0]
        self.upload()

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo_v = gl.glGenBuffers(1)
        self.vbo_c = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_v)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,  3 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_c)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.colors.nbytes, self.colors,
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE,  3 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def draw(self):
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.count)
        gl.glBindVertexArray(0)

    def dispose(self):
        gl.glDeleteVertexArrays(1, self.vao)
        gl.glDeleteBuffers(1, self.vbo_v)
        gl.glDeleteBuffers(1, self.vbo_c)


class Triangles:
    def __init__(self, vertices, colors):
        self.vao = None
        self.vbo = None
        self.vertex_attr = np.hstack([vertices, colors])
        self.count = self.vertex_attr.shape[0]
        self.upload()

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertex_attr.nbytes, self.vertex_attr,
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
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.count)
        gl.glBindVertexArray(0)

    def dispose(self):
        gl.glDeleteVertexArrays(1, self.vao)
        gl.glDeleteBuffers(1, self.vbo)


class App(xglut.GLFWViewer):
    def __init__(self,width,height,title="Shaders") -> None:
        super().__init__(width,height,title)

        # -------------------------------------
        # use our shaders class
        self.shader = Shaders.load('./vertex.vs', './uniform.fs')

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
        colors = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0
            ]
        colors = np.array(colors, np.float32).reshape([-1, 3])
        vertices0 = np.array(vertices0, np.float32).reshape([-1, 3])
        vertices1 = np.array(vertices1, np.float32).reshape([-1, 3])

        self.triangle0 = Triangles(vertices0, colors)
        self.triangle1 = TrianglesMultiVBO(vertices1, colors)

        self.view()


    def draw(self):
        
        # main drawing
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.shader.use()
        time_val = glfw.get_time()
        color_val = np.sin(time_val) / 2.0 + 0.5
        location = gl.glGetUniformLocation(self.shader.shader, "Color")
        gl.glUniform3f(location, 0.0, color_val, 0.0)
        self.triangle0.draw()

        gl.glUniform3f(location, color_val, 0.0,  0.0)
        self.triangle1.draw()




    def dispose(self):
        self.shader.dispose()
        self.triangle0.dispose()
        self.triangle1.dispose()


if __name__ == "__main__":
    myApp = App(640,480)
