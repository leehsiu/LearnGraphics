import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes
import PIL.Image
from scipy.spatial.transform import Rotation as R


def init_glfw(width, height, title="window"):
    glfw.init()
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE)
    
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

    return window


def framebuffer_size_callback(window, width, height):
    gl.glViewport(0, 0, width, height)


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

    def set_uniform(self, name, value):
        location = gl.glGetUniformLocation(self.shader, name)
        # TODO: support more type
        if isinstance(value, int):
            gl.glUniform1i(location, value)
        elif isinstance(value, float):
            gl.glUniform1f(location, value)
        elif isinstance(value, np.ndarray):
            if value.size == 16:
                gl.glUniformMatrix4fv(location, 1, gl.GL_TRUE, value)


class Material:
    def __init__(self, filepath):
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
        img = PIL.Image.open(filepath)
        img_data = img.convert("RGB").tobytes()

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0,
            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

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


class App:
    def __init__(self, window):
        # init opengl
        self.window = window

        # -------------------------------------
        # use our shaders class
        self.shader = Shaders.load('./vertex.vs', './fragment.fs')

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
        self.triangle.upload()

        self.texture0 = Material('../../assets/textures/container.jpg')
        self.texture1 = Material('../../assets/textures/awesomeface.png')

        self.mix_val = 0.2

        self.mainLoop()

    def process_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)
        elif glfw.get_key(self.window, GLFW.GLFW_KEY_UP) == GLFW.GLFW_PRESS:
            self.mix_val += 0.0001
            self.mix_val = min(self.mix_val, 1.0)
        elif glfw.get_key(self.window, GLFW.GLFW_KEY_DOWN) == GLFW.GLFW_PRESS:
            self.mix_val -= 0.0001
            self.mix_val = max(self.mix_val, 0.0)
        print(self.mix_val)

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
            self.shader.set_uniform("texture0", 0)
            self.shader.set_uniform("texture1", 1)
            self.shader.set_uniform("mixValue", self.mix_val)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            self.texture0.use()
            gl.glActiveTexture(gl.GL_TEXTURE1)
            self.texture1.use()

            # set transform according to time
            transform = np.eye(4)
            transform[:3, -1] = np.array([0.5, -0.5, 0.0])
            timeval = glfw.get_time()
            transform[:3, :3] = R.from_rotvec(
                timeval * np.array([0., 0., 1.0])).as_matrix()
            self.shader.set_uniform("transform", transform)
            self.triangle.draw()

            transform = np.eye(4)
            transform[:3, -1] = np.array([-0.5, 0.5, 0.0])
            timeval = glfw.get_time()
            transform[:3, :3] *= np.sin(timeval)
            self.shader.set_uniform("transform", transform)

            self.triangle.draw()

            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.quit()

    def quit(self):
        self.shader.dispose()
        self.triangle.dispose()
        self.texture0.dispose()
        self.texture1.dispose()
        glfw.terminate()


if __name__ == "__main__":
    window = init_glfw(640, 480)
    myApp = App(window)
