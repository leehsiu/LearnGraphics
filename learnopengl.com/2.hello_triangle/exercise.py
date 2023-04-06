import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes
# Draw two triangles using two VAOs and two different shaders


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
        # to only draw the first triangle
        # gl.glDrawElements(gl.GL_TRIANGLES, 1 * 3,
        #                   gl.GL_UNSIGNED_INT, None)

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

        with open('./green.frag', 'r') as f:
            src = f.readlines()
        fragment_shader0 = glshaders.compileShader(src, gl.GL_FRAGMENT_SHADER)

        with open('./yellow.frag', 'r') as f:
            src = f.readlines()
        fragment_shader1 = glshaders.compileShader(src, gl.GL_FRAGMENT_SHADER)

        self.shader0 = glshaders.compileProgram(
            vertex_shader, fragment_shader0)
        self.shader1 = glshaders.compileProgram(
            vertex_shader, fragment_shader1)

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
        indices = [
            0, 1, 2]
        indices = np.array(indices, np.uint32)
        self.triangle0 = Triangles(vertices0, indices)
        self.triangle1 = Triangles(vertices1, indices)
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
            gl.glClearColor(0.0, 0.0, 0.0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

            gl.glUseProgram(self.shader0)
            self.triangle0.draw()

            gl.glUseProgram(self.shader1)
            self.triangle1.draw()

            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.quit()

    def quit(self):
        gl.glDeleteProgram(self.shader0)
        gl.glDeleteProgram(self.shader1)
        self.triangle0.dispose()
        self.triangle1.dispose()
        glfw.terminate()


if __name__ == "__main__":
    window = init_glfw(640, 480)
    myApp = App(window)
