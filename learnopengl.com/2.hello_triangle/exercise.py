import sys
import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl
import OpenGL.GL.shaders as glshaders
import numpy as np
import ctypes

# Draw two triangles using two VAOs and two shaders

def init_glfw(width, height, title="window"):
    
    glfw.init()
    # setup OpenGL context
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)
    
    if sys.platform == "darwin":
        glfw.window_hint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE)
    
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)

    return window


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
        indices = [
            0, 1, 2]
        indices = np.array(indices, np.uint32)
        self.triangle0 = Triangles(vertices0, indices)
        self.triangle1 = Triangles(vertices1, indices)
        self.triangle0.upload()
        self.triangle1.upload()
        
        
        glfw.set_framebuffer_size_callback(window,self.resize)

        self.mainloop()


    def resize(self,window, width,height):
        gl.glViewport(0,0, width, height)

    def process_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)

    def mainloop(self):
        
        while not glfw.window_should_close(self.window):
            
            self.process_input()
            # main drawing
            gl.glClearColor(0.0, 0.0, 0.0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

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
