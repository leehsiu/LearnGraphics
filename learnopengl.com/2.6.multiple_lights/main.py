import sys
sys.path.append('../../lib')

import xglut
import xglut.glm as glm

import glfw
import glfw.GLFW as GLFW
import ctypes
import numpy as np
import OpenGL.GL as gl


class Triangles:
    def __init__(self, vertices):
        self.vao = None
        self.vbo = None
        self.vertices = vertices
        self.upload()

    def upload(self):

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
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

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def draw(self):
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)

    def dispose(self):
        gl.glDeleteVertexArrays(1, self.vao)
        gl.glDeleteBuffers(1, self.vbo)



class App(xglut.GLFWViewer):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)


        self.cube_shader = xglut.Shader.load('./cube.vs','./cube.fs')
        self.light_shader = xglut.Shader.load('./light.vs', './light.fs')
        
        
        
        self.diffuse_map = xglut.Texture.load(
            '../../assets/textures/container2.png')
        self.specular_map = xglut.Texture.load(
            '../../assets/textures/container2_specular.png')
        
        vertices = np.loadtxt('./cube.txt').astype(np.float32)
        self.cube = Triangles(vertices)
        
        
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
        
        self.point_light_positions = np.array([
            0.7,  0.2,  2.0,
            2.3, -3.3, -4.0,
            -4.0,  2.0, -12.0,
            0.0,  0.0, -3.0]).reshape(-1,3)
        
        self.camera = xglut.OrbitPerspectiveCamera(
            45,self.width*1.0/self.height,1e-2,100.)
        self.camera.position = np.array([0.,0.,3.])
        self.camera.center = np.array([0.,0.,0.])
        self.camera.update_projection_matrix()
        self.camera.update_matrix()
        
        self.light_ID = 0
        
        
        gl.glEnable(gl.GL_DEPTH_TEST)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_scroll_callback(self.window,self.scroll_callback)
        glfw.set_mouse_button_callback(self.window,self.mouse_button_callback)
        glfw.set_key_callback(self.window,self.key_callback)
        
        self.view()
        
    def scroll_callback(self,window,xoffset,yoffset):
        self.camera.handle_scroll(window,xoffset,yoffset) 
    
    def cursor_pos_callback(self,window,xpos,ypos):
        self.camera.handle_cursor_pos(window,xpos,ypos)
        
    def mouse_button_callback(self,window,key,action,mods):
        self.camera.handle_mouse_button(window,key,action,mods)
    
    def key_callback(self,window,key,scancode,action,mods):
        if key== GLFW.GLFW_KEY_UP and action == GLFW.GLFW_PRESS:
            light_ID = self.light_ID + 1
            self.light_ID = min(light_ID, len(self.cube_shaders)-1)
        elif key== GLFW.GLFW_KEY_DOWN and action == GLFW.GLFW_PRESS:
            light_ID = self.light_ID - 1
            self.light_ID = max(light_ID,0)
            
        
    
    def resize(self,window,width,height):
        super().resize(window,width,height)
        self.camera.aspect = self.width * 1.0 / self.height
        self.camera.update_projection_matrix()
        
            

    def draw(self):
        # main drawing
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


        projection_mat = self.camera.projection
        view = self.camera.matrix
        
        
        
        cube_shader = self.cube_shader
        
        
        cube_shader.use()
        cube_shader.set_uniform("material.diffuse", 0)
        cube_shader.set_uniform("material.specular", 1)
        cube_shader.set_uniform("material.shininess", 32.0)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        self.diffuse_map.use()
        gl.glActiveTexture(gl.GL_TEXTURE1)
        self.specular_map.use()
        
        cube_shader.set_uniform("viewPos",self.camera.position)
        cube_shader.set_uniform("dirLight.direction",[-0.2, -1.0, -0.3])
        cube_shader.set_uniform("dirLight.ambient",[0.05,0.05,0.05])
        cube_shader.set_uniform("dirLight.diffuse", [0.4,0.4,0.4])
        cube_shader.set_uniform("dirLight.specular",[0.5,0.5,0.5])
        
        for i, position in enumerate(self.point_light_positions):
            cube_shader.set_uniform(f"pointLights[{i}].position",position)
            cube_shader.set_uniform(
                f"pointLights[{i}].ambient", [0.05, 0.05, 0.05])
            cube_shader.set_uniform(
                f"pointLights[{i}].diffuse", [0.8, 0.8, 0.8])
            cube_shader.set_uniform(
                f"pointLights[{i}].specular",[1.0, 1.0, 1.0])
            cube_shader.set_uniform(f"pointLights[{i}].constant",1.0)
            cube_shader.set_uniform(f"pointLights[{i}].linear",0.09)
            cube_shader.set_uniform(f"pointLights[{i}].quadratic",0.032)
        
            
        cube_shader.set_uniform("spotLight.position",self.camera.position)
        camera_front = - self.camera.matrix[2, :3]
        cube_shader.set_uniform("spotLight.direction",camera_front)
        cube_shader.set_uniform("spotLight.constant", 1.0)
        cube_shader.set_uniform("spotLight.linear", 0.09)
        cube_shader.set_uniform("spotLight.quadratic", 0.032)
        cube_shader.set_uniform("spotLight.cutOff", np.cos(np.deg2rad(12.5)))
        cube_shader.set_uniform(
            "spotLight.outerCutOff", np.cos(np.deg2rad(17.5)))
                                
            
        
        
        for i, position in enumerate(self.cube_positions):
            model_mat = np.eye(4)
            model_mat[:3, -1] = position
            model_mat[:3, :3] = glm.rotate(i*20, np.array([1.0, 0.3, 0.5]))
            model_mat = model_mat.astype(np.float32)
            mvp_mat = projection_mat @ view @ model_mat
            normal_mat = model_mat[:3, :3]
            
            cube_shader.set_uniform("ModelMatrix", model_mat)
            cube_shader.set_uniform("ModelViewProjectionMatrix", mvp_mat)
            cube_shader.set_uniform("NormalMatrix", normal_mat)
            self.cube.draw()
            
            
        
        
        self.light_shader.use()
        for position in self.point_light_positions:
            model_mat = np.eye(4)
            model_mat[:3,:3] *= 0.2
            model_mat[:3, -1] = position
            mvp_mat = projection_mat @ view @ model_mat
            self.light_shader.set_uniform(
                "ModelViewProjectionMatrix", mvp_mat)
            self.light_shader.set_uniform("Color", [1.0,1.0,1.0])
            self.cube.draw()

        

    def dispose(self):
        for cube_shader in self.cube_shaders:
            cube_shader.dispose()
        self.light_shader.dispose()
        self.cube.dispose()
        self.diffuse_map.dispose()
        self.specular_map.dispose()

if __name__ == "__main__":
    app = App(640 ,480, "Lighting Maps")
