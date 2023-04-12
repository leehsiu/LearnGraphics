import sys
sys.path.append('../../lib')

import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes
import PIL.Image
import xglut


class Texture:
    def __init__(self, img):
        self.texture = gl.glGenTextures(1)
        # all upcoming GL_TEXTURE_2D operations now have effect on this texture
        # object
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # set the texture wrapping parameters

        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
            gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # load image, create texture and generate mipmaps
        if isinstance(img, np.ndarray):
            img = PIL.Image.fromarray(img)
            
        img_data = img.convert("RGB").tobytes()

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0,
            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    @classmethod
    def load(cls, path):
        img = PIL.Image.open(path)
        return cls(img)

    def use(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

    def dispose(self):
        gl.glDeleteTextures(1, (self.texture,))


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
    def __init__(self, width,height,title="Textures"):
        super().__init__(width,height,title)
        
        # -------------------------------------
        # use our shaders class
        self.shader = xglut.Shader.load('./vertex.vs', './fragment.fs')

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

        self.texture = Texture.load('../../assets/textures/container.jpg')

        self.view()


    def draw(self):
            # main drawing
        gl.glClearColor(0.2, 0.3, 0.3, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.shader.use()
        self.shader.set_uniform("texture0",0)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        self.texture.use()
        
        # self.shader.set_uniform("texture0",1)
        # gl.glActiveTexture(gl.GL_TEXTURE1)
        # self.texture.use()
        self.triangle.draw()


    def dispose(self):
        self.shader.dispose()
        self.triangle.dispose()
        self.texture.dispose()


if __name__ == "__main__":
    myApp = App(640,480)
