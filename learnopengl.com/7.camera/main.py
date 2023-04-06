import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes
import PIL.Image
from scipy.spatial.transform import Rotation as R

# https://learnopengl.com/code_viewer_gh.php?code=src/1.getting_started/
# 6.3.coordinate_systems_multiple/coordinate_systems_multiple.cpp


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

# https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
# Notice that the doc is wrong. There should be a -1. as in 
# https://github.com/g-truc/glm/blob/master/glm/ext/matrix_clip_space.inl

def perspective(fov, aspect, z_near, z_far):
    f = 1./np.tan(fov*np.pi/360)
    z_dist = z_far - z_near
    mat = np.array([
        f/aspect, 0, 0, 0,
        0, f, 0, 0,
        0, 0, -(z_far + z_near) / z_dist, -2 * z_far * z_near / z_dist,
        0, 0, -1, 0], np.float32).reshape(4, 4)
    return mat

def rotate(angle, axis):
    axis_norm = np.linalg.norm(axis,2)
    axis = axis / axis_norm
    angle = angle * np.pi / 180
    mat = R.from_rotvec(angle * axis).as_matrix()
    return mat

    
    

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
        gl.glDeleteTextures(1, self.texture)


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


class App:
    def __init__(self, window):
        # init opengl
        self.window = window

        # enable z-buffering
        gl.glEnable(gl.GL_DEPTH_TEST)
        # -------------------------------------
        self.shader = Shaders.load('./vertex.vs', './fragment.fs')

        # -----------------------------------
        vertices = np.loadtxt('./cube.txt').astype(np.float32)

        self.triangle = Triangles(vertices)
        self.triangle.upload()

        self.texture0 = Material('../../assets/textures/container.jpg')
        self.texture1 = Material('../../assets/textures/awesomeface.png')

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
        self.mix_val = 0.2
        # use our shaders class

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

    def mainLoop(self):
        running = True
        while (running):
            if glfw.window_should_close(self.window):
                running = False
            self.process_input()
            # main drawing
            gl.glClearColor(0.2, 0.3, 0.3, 1)
            
            # clear both color buffer and z-buffer
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            self.shader.use()
            self.shader.set_uniform("texture0", 0)
            self.shader.set_uniform("texture1", 1)
            self.shader.set_uniform("mixValue", self.mix_val)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            self.texture0.use()
            gl.glActiveTexture(gl.GL_TEXTURE1)
            self.texture1.use()

            projection_mat = perspective(45, 640./480, 0.01, 100.0)
            projection_mat = projection_mat.astype(np.float32)
            view_mat = np.eye(4)
            view_mat[:3, -1] = np.array([0.0, 0.0, -3.0])
            view_mat = view_mat.astype(np.float32)
            self.shader.set_uniform("projection", projection_mat)
            self.shader.set_uniform("view", view_mat)
            
            for i, r in enumerate(self.cube_positions):
                model_mat = np.eye(4)
                model_mat[:3, -1] = r
                axis = np.array([1.0, 0.3, 0.5])
                angle = i * 20.0
                model_mat[:3, :3] = rotate(angle, axis)
                model_mat = model_mat.astype(np.float32)
                
                self.shader.set_uniform("model", model_mat)
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
