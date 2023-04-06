import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes


def init_glfw(width, height, title="window"):
    glfw.init()
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE)
    glfw.window_hint(GLFW.GLFW_DOUBLEBUFFER, gl.GL_FALSE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

    return window


def framebuffer_size_callback(window, width, height):
    gl.glViewport(0, 0, width, height)


class Shaders:
    def __init__(self, vertex_shader, fragment_shader):
        v_shader = glshaders.compileShader(vertex_shader, gl.GL_VERTEX_SHADER)
        f_shader = glshaders.compileShader(
            fragment_shader, gl.GL_FRAGMENT_SHADER)
        self.shader = glshaders.compileProgram(
            v_shader, f_shader)

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
class TrianglesNonStride:
    def __init__(self, vertices, colors, indices):
        self.vao = None
        self.vbo_v = None
        self.vbo_c = None
        self.ebo = None
        self.vertices = vertices
        self.colors = colors
        self.indices = indices

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo_v = gl.glGenBuffers(1)
        self.vbo_c = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

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
        gl.glDeleteBuffers(1, self.vbo_v)
        gl.glDeleteBuffers(1, self.vbo_c)
        gl.glDeleteBuffers(1, self.ebo)


class Triangles:
    def __init__(self, vertices, colors, indices):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.vertex_attr = np.hstack([vertices, colors])
        self.indices = indices

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
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,  6 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(1)

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


class App:
    def __init__(self, window):
        # init opengl
        self.window = window

        # -------------------------------------
        # use our shaders class
        self.shader = Shaders.load('./vertex.vert', './fragment.frag')

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
        indices = [0, 1, 2]
        indices = np.array(indices, np.uint32)
        colors = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0
            ]
        colors = np.array(colors, np.float32).reshape([-1, 3])
        vertices0 = np.array(vertices0, np.float32).reshape([-1, 3])
        vertices1 = np.array(vertices1, np.float32).reshape([-1, 3])
        indices = np.array(indices, np.uint32)

        self.triangle0 = Triangles(vertices0, colors, indices)
        self.triangle1 = TrianglesNonStride(vertices1, colors, indices)
        self.triangle0.upload()
        self.triangle1.upload()

        self.mainLoop()

    def process_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)

    def mainLoop(self):
        running = True
        while (running):
            if glfw.window_should_close(self.window):
                running = False
            self.process_input()
            # main drawing
            gl.glClearColor(0.2, 0.3, 0.3, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self.shader.use()
            self.triangle0.draw()
            self.triangle1.draw()

            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.quit()

    def quit(self):
        self.shader.dispose()
        self.triangle0.dispose()
        self.triangle1.dispose()
        glfw.terminate()


if __name__ == "__main__":
    window = init_glfw(640, 480)
    myApp = App(window)
