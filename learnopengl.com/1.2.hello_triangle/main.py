import sys
sys.path.append('../../lib')

import xglut

import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import numpy as np
import ctypes
# orignal CPP code: https://learnopengl.com/code_viewer_gh.php?code=src/1.
# getting_started/2.2.hello_triangle_indexed/hello_triangle_indexed.cpp

class Triangles:
    def __init__(self, vertices, indices):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.vertices = vertices
        self.indices = indices
        self.upload()

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))


        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices,
            gl.GL_STATIC_DRAW)

        gl.glEnableVertexAttribArray(0)

        # note that this is allowed, the call to glVertexAttribPointer
        # registered VBO as the vertex attribute's bound vertex buffer object
        # so afterwards we can safely unbind
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        # remember: do NOT unbind the EBO while a VAO is active as the bound
        # element buffer object IS stored in the VAO; keep the EBO bound.
        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0);

        # You can unbind the VAO afterwards so other VAO calls won't
        # accidentally modify this VAO, but this rarely happens.
        # Modifying other VAOs requires a call to glBindVertexArray anyways so
        # we generally don't unbind VAOs (nor VBOs) when it's not directly
        # necessary.
        gl.glBindVertexArray(0)
        return

    def draw(self):
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES, self.indices.size, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)


    def dispose(self):
        gl.glDeleteVertexArrays(1, self.vao)
        gl.glDeleteBuffers(1, self.vbo)
        gl.glDeleteBuffers(1, self.ebo)


class App(xglut.GLFWViewer):
    def __init__(self,width,height,title):
        super().__init__(width,height,title)

        # build shaders
        with open('./vertex.vs', 'r') as f:
            src = f.readlines()
            
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex, src)
        gl.glCompileShader(vertex)
        
        with open('./green.fs', 'r') as f:
            src = f.readlines()
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment, src)
        gl.glCompileShader(fragment)
        
        self.shader = gl.glCreateProgram()
        gl.glAttachShader(self.shader, vertex)
        gl.glAttachShader(self.shader, fragment)
        gl.glLinkProgram(self.shader)
        
        gl.glDeleteShader(vertex)
        gl.glDeleteShader(fragment)
        

        # init vertex data
        vertices = [
            0.5,  0.5, 0.0,  # top right
            0.5, -0.5, 0.0,  # bottom right
            -0.5, -0.5, 0.0,  # bottom left
            -0.5,  0.5, 0.0   # top left
            ]
        vertices = np.array(vertices, np.float32)
        indices = [
            0, 1, 3,  # first Triangle
            1, 2, 3   # second Triangle
            ]
        indices = np.array(indices, np.uint32)
        self.triangle = Triangles(vertices, indices)

        self.view()


    def draw(self):
        gl.glClearColor(0.2, 0.3, 0.3, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glUseProgram(self.shader)
        self.triangle.draw()

    def dispose(self):
        gl.glDeleteProgram(self.shader)
        self.triangle.dispose()


if __name__ == "__main__":
    app = App(640,480,"Hello Triangle")
