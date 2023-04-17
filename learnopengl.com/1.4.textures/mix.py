import sys
sys.path.append('../../lib')

import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import numpy as np
import ctypes
import PIL.Image

import xglut

class Triangles:
    def __init__(self, vertices, indices):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.vertex_attr = vertices
        self.indices = indices
        self.upload()

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertex_attr.nbytes, self.vertex_attr,
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,  8 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(
            2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(2)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices,
            gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)


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
    def __init__(self, width,height,title):
        super().__init__(width,height,title)


        # -------------------------------------
        # use our shaders class
        self.shader = xglut.Shader.load('./vertex.vs', './mix.fs')

        # -----------------------------------
        # Init vertex data
        # positions          colors           texture coords
        vertices = [
            0.5,  0.5, 0.0,   1.0, 0.0, 0.0,   1.0, 1.0,  # top right
            0.5, -0.5, 0.0,   0.0, 1.0, 0.0,   1.0, 0.0,  # bottom right
            -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0,  # bottom left
            -0.5,  0.5, 0.0,   1.0, 1.0, 0.0,   0.0, 1.0   # top left
        ]
        indices = [
            0, 1, 3,  # first triangle
            1, 2, 3  # second triangle
        ]
        vertices = np.array(vertices, np.float32)
        indices = np.array(indices, np.uint32)

        self.triangle = Triangles(vertices, indices)
        

        self.texture0 = xglut.Texture.load(
            '../../assets/textures/container.jpg')
        self.texture1 = xglut.Texture.load(
            '../../assets/textures/awesomeface.png')
        gl.glBindTexture(gl.GL_TEXTURE_2D,0)

        self.mix_val = 0.2

        self.view()

    def handle_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)
        elif glfw.get_key(self.window, GLFW.GLFW_KEY_UP) == GLFW.GLFW_PRESS:
            self.mix_val += 0.01
            self.mix_val = min(self.mix_val, 1.0)
        elif glfw.get_key(self.window, GLFW.GLFW_KEY_DOWN) == GLFW.GLFW_PRESS:
            self.mix_val -= 0.01
            self.mix_val = max(self.mix_val, 0.0)

    def draw(self):
        
        # main drawing
        gl.glClearColor(0.2, 0.3, 0.3, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.shader.use()
        
        self.shader.set_uniform("texture0", 0)
        self.shader.set_uniform("texture1", 1)
        self.shader.set_uniform("mixValue", self.mix_val)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        self.texture0.use()
        gl.glActiveTexture(gl.GL_TEXTURE1)
        self.texture1.use()
        
        self.triangle.draw()



    def dispose(self):
        self.shader.dispose()
        self.triangle.dispose()
        self.texture0.dispose()
        self.texture1.dispose()


if __name__ == "__main__":

    myApp = App(640,480,'mix')
