import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes
# orignal CPP code: https://learnopengl.com/code_viewer_gh.php?code=src/1.
# getting_started/2.2.hello_triangle_indexed/hello_triangle_indexed.cpp


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
    def __init__(self) -> None:
        return


class Triangles:
    def __init__(self, vertices, indices):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.vertices = vertices
        self.indices = indices

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
            gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices,
            gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))

        gl.glEnableVertexAttribArray(0)
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
        # pyopengl provides convenient way to build shaders
        with open('./vertex.vert', 'r') as f:
            src = f.readlines()
        vertex_shader = glshaders.compileShader(src, gl.GL_VERTEX_SHADER)

        with open('./uniform.frag', 'r') as f:
            src = f.readlines()
        fragment_shader = glshaders.compileShader(src, gl.GL_FRAGMENT_SHADER)
        self.shader = glshaders.compileProgram(
            vertex_shader, fragment_shader)

        # -----------------------------------
        # Init vertex data
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
        self.triangle.upload()

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

            gl.glUseProgram(self.shader)
            timeValue = glfw.get_time()
            greenValue = np.sin(timeValue) / 2.0 + 0.5
            vertexColorLocation = gl.glGetUniformLocation(
                self.shader, "ourColor")
            gl.glUniform3f(vertexColorLocation, 0.0, greenValue, 0.0)

            self.triangle.draw()

            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.quit()

    def quit(self):
        gl.glDeleteProgram(self.shader)
        self.triangle.dispose()
        glfw.terminate()


if __name__ == "__main__":
    window = init_glfw(640, 480)
    myApp = App(window)
