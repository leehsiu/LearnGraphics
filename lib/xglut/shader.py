import OpenGL.GL as gl
import numpy as np

__all__ = [
    'Shader',
]

class Shader:
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
            elif value.size == 9:
                gl.glUniformMatrix3fv(location, 1, gl.GL_TRUE, value)
            elif value.size == 3:
                gl.glUniform3fv(location, 1, value)
                
                
